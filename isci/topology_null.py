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


@dataclass(frozen=True)
class ConditionalSamplerDiagnostics:
    target_correlation: float
    lower_bound: float
    upper_bound: float
    requested_samples: int
    collected_samples: int
    initialized_chains: int
    proposal_acceptance_rate: float
    unique_sample_fraction: float
    effective_sample_size: float
    r_hat: float


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


def _propose_state(
    state: np.ndarray,
    slot_deciles: np.ndarray,
    pools: dict[int, np.ndarray],
    rng: np.random.Generator,
) -> np.ndarray:
    proposal = state.copy()
    move_size = int(rng.integers(1, len(state) + 1))
    slots = rng.choice(len(state), size=move_size, replace=False)
    occupied = set(state.tolist()) - set(state[slots].tolist())
    for slot in slots:
        candidates = [gene for gene in pools[int(slot_deciles[slot])] if gene not in occupied]
        if not candidates:
            return state.copy()
        proposal[slot] = int(rng.choice(candidates))
        occupied.add(int(proposal[slot]))
    return proposal


def _random_state(
    slot_deciles: np.ndarray,
    pools: dict[int, np.ndarray],
    rng: np.random.Generator,
) -> np.ndarray:
    state = np.empty(len(slot_deciles), dtype=int)
    occupied: set[int] = set()
    for slot, decile in enumerate(slot_deciles):
        candidates = [gene for gene in pools[int(decile)] if gene not in occupied]
        if not candidates:
            raise ValueError(f"expression decile {decile} lacks a unique alternative")
        state[slot] = int(rng.choice(candidates))
        occupied.add(int(state[slot]))
    return state


def _find_feasible_state(
    slot_deciles: np.ndarray,
    pools: dict[int, np.ndarray],
    correlation: np.ndarray,
    target: float,
    lower: float,
    upper: float,
    rng: np.random.Generator,
    max_steps: int,
) -> np.ndarray | None:
    state = _random_state(slot_deciles, pools, rng)
    statistic = mean_absolute_correlation(state, correlation)
    for step in range(max_steps):
        if lower <= statistic <= upper:
            return state
        proposal = _propose_state(state, slot_deciles, pools, rng)
        proposal_statistic = mean_absolute_correlation(proposal, correlation)
        current_distance = abs(statistic - target)
        proposal_distance = abs(proposal_statistic - target)
        temperature = max(target * 0.5, 0.01) * (1.0 - step / max_steps) + 1e-5
        if proposal_distance <= current_distance or rng.random() < np.exp(
            -(proposal_distance - current_distance) / temperature
        ):
            state = proposal
            statistic = proposal_statistic
    return state if lower <= statistic <= upper else None


def _effective_sample_size(values: np.ndarray) -> float:
    if len(values) < 3 or np.var(values) == 0:
        return 1.0
    centered = values - values.mean()
    variance = float(np.dot(centered, centered))
    autocorrelation_sum = 0.0
    for lag in range(1, min(len(values) // 2, 100)):
        autocorrelation = float(np.dot(centered[:-lag], centered[lag:]) / variance)
        if autocorrelation <= 0:
            break
        autocorrelation_sum += autocorrelation
    return float(len(values) / (1.0 + 2.0 * autocorrelation_sum))


def _r_hat(chains: list[np.ndarray]) -> float:
    usable = [chain for chain in chains if len(chain) >= 2]
    if len(usable) < 2:
        return float("nan")
    length = min(len(chain) for chain in usable)
    matrix = np.vstack([chain[:length] for chain in usable])
    within = float(np.mean(np.var(matrix, axis=1, ddof=1)))
    between = float(length * np.var(matrix.mean(axis=1), ddof=1))
    if within == 0:
        return 1.0 if between == 0 else float("inf")
    variance = ((length - 1) / length) * within + between / length
    return float(np.sqrt(variance / within))


def conditional_topology_samples(
    real_indices: Sequence[int],
    expression_deciles: Sequence[int],
    correlation: np.ndarray,
    *,
    n_samples: int = 200,
    tolerance: float = 0.20,
    n_chains: int = 4,
    burn_in: int = 2_000,
    thinning: int = 100,
    max_initialization_steps: int = 50_000,
    seed: int = 20260712,
) -> tuple[np.ndarray, ConditionalSamplerDiagnostics]:
    """Sample the expression/topology-conditional axis-set state space.

    Initialization uses label-blind annealing. Sampling then uses a symmetric
    constrained proposal; states outside the frozen topology band are rejected.
    Diagnostics expose whether the conditional state space is sufficiently mobile.
    """

    real = np.asarray(real_indices, dtype=int)
    deciles = np.asarray(expression_deciles, dtype=int)
    slot_deciles = deciles[real]
    forbidden = set(real.tolist())
    pools = {
        int(decile): np.asarray(
            [gene for gene in np.flatnonzero(deciles == decile) if gene not in forbidden],
            dtype=int,
        )
        for decile in np.unique(slot_deciles)
    }
    target = mean_absolute_correlation(real, correlation)
    lower = max(0.0, target * (1.0 - tolerance))
    upper = min(1.0, target * (1.0 + tolerance))
    rng = np.random.default_rng(seed)
    per_chain = int(np.ceil(n_samples / n_chains))
    samples: list[np.ndarray] = []
    seen: set[tuple[int, ...]] = set()
    chain_statistics: list[np.ndarray] = []
    accepted = 0
    proposals = 0
    initialized = 0

    for _ in range(n_chains):
        state = _find_feasible_state(
            slot_deciles,
            pools,
            correlation,
            target,
            lower,
            upper,
            rng,
            max_initialization_steps,
        )
        if state is None:
            continue
        initialized += 1
        chain_values: list[float] = []
        collected = 0
        max_steps = burn_in + per_chain * thinning * 50
        for step in range(max_steps):
            proposal = _propose_state(state, slot_deciles, pools, rng)
            statistic = mean_absolute_correlation(proposal, correlation)
            proposals += 1
            if lower <= statistic <= upper:
                state = proposal
                accepted += 1
            if step < burn_in or (step - burn_in) % thinning:
                continue
            state_statistic = mean_absolute_correlation(state, correlation)
            chain_values.append(state_statistic)
            key = tuple(sorted(state.tolist()))
            if key in seen:
                continue
            seen.add(key)
            samples.append(state.copy())
            collected += 1
            if collected >= per_chain or len(samples) >= n_samples:
                break
        chain_statistics.append(np.asarray(chain_values, dtype=float))
        if len(samples) >= n_samples:
            break

    result = np.asarray(samples[:n_samples], dtype=int)
    effective_sample_size = float(sum(_effective_sample_size(chain) for chain in chain_statistics))
    diagnostics = ConditionalSamplerDiagnostics(
        target_correlation=target,
        lower_bound=lower,
        upper_bound=upper,
        requested_samples=n_samples,
        collected_samples=len(result),
        initialized_chains=initialized,
        proposal_acceptance_rate=float(accepted / proposals) if proposals else 0.0,
        unique_sample_fraction=float(len(result) / n_samples),
        effective_sample_size=effective_sample_size,
        r_hat=_r_hat(chain_statistics),
    )
    return result, diagnostics
