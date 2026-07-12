"""Label-blind topology diagnostics for functional-axis conditional nulls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class TopologyRarity:
    observed: float
    null_mean: float
    null_std: float
    percentile: float
    upper_p: float
    n_random: int


def mean_absolute_correlation(indices: Sequence[int], correlation: np.ndarray) -> float:
    """Mean absolute off-diagonal correlation for a set of gene columns."""

    selected = np.asarray(indices, dtype=int)
    if len(selected) < 2:
        return 0.0
    matrix = np.abs(np.asarray(correlation)[np.ix_(selected, selected)])
    return float((matrix.sum(dtype=np.float64) - np.trace(matrix)) / (len(selected) * (len(selected) - 1)))


def expression_matched_random_sets(
    real_indices: Sequence[int],
    expression_deciles: Sequence[int],
    *,
    n_random: int,
    seed: int,
    exclude_real: bool = True,
) -> np.ndarray:
    """Draw gene sets preserving the exact expression-decile counts of an axis."""

    real = np.asarray(real_indices, dtype=int)
    deciles = np.asarray(expression_deciles, dtype=int)
    if deciles.ndim != 1:
        raise ValueError("expression deciles must be one-dimensional")
    if len(np.unique(real)) != len(real):
        raise ValueError("real axis indices must be unique")
    counts = np.bincount(deciles[real], minlength=int(deciles.max()) + 1)
    forbidden = set(real.tolist()) if exclude_real else set()
    pools = {
        decile: np.asarray(
            [index for index in np.flatnonzero(deciles == decile) if index not in forbidden],
            dtype=int,
        )
        for decile in np.flatnonzero(counts)
    }
    for decile, count in enumerate(counts):
        if count and len(pools[decile]) < count:
            raise ValueError(f"expression decile {decile} lacks enough alternative genes")
    rng = np.random.default_rng(seed)
    samples = np.empty((n_random, len(real)), dtype=int)
    for row in range(n_random):
        cursor = 0
        for decile, count in enumerate(counts):
            if not count:
                continue
            selected = rng.choice(pools[decile], size=count, replace=False)
            samples[row, cursor : cursor + count] = selected
            cursor += count
    return samples


def topology_rarity(
    real_indices: Sequence[int],
    expression_deciles: Sequence[int],
    correlation: np.ndarray,
    *,
    n_random: int = 10_000,
    seed: int = 20260712,
) -> tuple[TopologyRarity, np.ndarray]:
    """Compare observed within-axis topology with expression-matched random sets."""

    observed = mean_absolute_correlation(real_indices, correlation)
    sets = expression_matched_random_sets(
        real_indices,
        expression_deciles,
        n_random=n_random,
        seed=seed,
        exclude_real=True,
    )
    null = np.asarray([mean_absolute_correlation(row, correlation) for row in sets])
    percentile = float((np.sum(null < observed) + 0.5 * np.sum(null == observed)) / len(null))
    upper_p = float((1 + np.sum(null >= observed)) / (1 + len(null)))
    return (
        TopologyRarity(
            observed=observed,
            null_mean=float(null.mean()),
            null_std=float(null.std(ddof=1)),
            percentile=percentile,
            upper_p=upper_p,
            n_random=n_random,
        ),
        null,
    )
