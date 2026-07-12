"""Label-blind utilities for topology-conditional functional-axis nulls."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

import numpy as np


def mean_absolute_correlation(correlation: np.ndarray, indices: Sequence[int]) -> float:
    """Mean absolute off-diagonal correlation for one gene set."""

    matrix = np.asarray(correlation, dtype=float)
    selected = np.asarray(indices, dtype=int)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("correlation must be a square matrix")
    if len(selected) < 2 or len(np.unique(selected)) != len(selected):
        raise ValueError("topology requires at least two unique gene indices")
    submatrix = np.abs(matrix[np.ix_(selected, selected)])
    return float((submatrix.sum() - np.trace(submatrix)) / (len(selected) * (len(selected) - 1)))


def decile_counts(deciles: Sequence[int], indices: Sequence[int]) -> Counter[int]:
    """Exact expression-decile composition of a gene set."""

    values = np.asarray(deciles, dtype=int)
    return Counter(int(value) for value in values[np.asarray(indices, dtype=int)])


def gelman_rubin(chains: np.ndarray) -> float:
    """Classic split-chain R-hat for equal-length scalar traces."""

    traces = np.asarray(chains, dtype=float)
    if traces.ndim != 2 or traces.shape[0] < 2 or traces.shape[1] < 2:
        return float("nan")
    within = float(np.mean(np.var(traces, axis=1, ddof=1)))
    between = float(traces.shape[1] * np.var(np.mean(traces, axis=1), ddof=1))
    if within == 0:
        return 1.0 if between == 0 else float("inf")
    variance = ((traces.shape[1] - 1) / traces.shape[1]) * within + between / traces.shape[1]
    return float(np.sqrt(variance / within))


def effective_sample_size(chains: np.ndarray) -> float:
    """Conservative scalar ESS using positive pooled lag autocorrelations."""

    traces = np.asarray(chains, dtype=float)
    if traces.ndim != 2 or traces.shape[0] < 1 or traces.shape[1] < 3:
        return 0.0
    centered = traces - traces.mean(axis=1, keepdims=True)
    variance = np.mean(np.sum(centered * centered, axis=1) / traces.shape[1])
    if variance <= 0:
        return float(traces.size)
    autocorrelation_sum = 0.0
    for lag in range(1, traces.shape[1]):
        covariance = np.mean(
            np.sum(centered[:, :-lag] * centered[:, lag:], axis=1) / (traces.shape[1] - lag)
        )
        rho = float(covariance / variance)
        if rho <= 0:
            break
        autocorrelation_sum += rho
    return float(traces.size / (1.0 + 2.0 * autocorrelation_sum))


def convergence_diagnostics(
    samples_by_chain: Sequence[Sequence[Sequence[int]]],
    topology_by_chain: Sequence[Sequence[float]],
    *,
    proposal_acceptance: float,
) -> dict[str, float | int | bool]:
    """Summarize the predeclared exchangeability/convergence gates."""

    initialized = sum(bool(chain) for chain in samples_by_chain)
    samples = [tuple(sorted(sample)) for chain in samples_by_chain for sample in chain]
    unique = len(set(samples))
    traces = [list(trace) for trace in topology_by_chain if len(trace) > 0]
    equal_length = min((len(trace) for trace in traces), default=0)
    trace_array = np.asarray([trace[:equal_length] for trace in traces], dtype=float)
    rhat = gelman_rubin(trace_array)
    ess = effective_sample_size(trace_array)
    evaluable = bool(
        unique >= 180
        and initialized >= 3
        and proposal_acceptance >= 0.001
        and ess >= 50
        and np.isfinite(rhat)
        and rhat <= 1.10
    )
    return {
        "n_samples": len(samples),
        "n_unique": unique,
        "n_initialized_chains": initialized,
        "proposal_acceptance": float(proposal_acceptance),
        "effective_sample_size": ess,
        "rhat": rhat,
        "evaluable": evaluable,
    }
