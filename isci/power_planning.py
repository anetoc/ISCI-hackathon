"""Pilot-based planning for donor-resolved context validation."""

from __future__ import annotations

import numpy as np


def simulate_partial_donor_gate_power(
    contrasts: np.ndarray,
    *,
    donor_counts: list[int],
    effect_scales: list[float] | None = None,
    n_trials: int = 2_000,
    n_bootstrap: int = 500,
    seed: int = 20260712,
) -> list[dict[str, float | int]]:
    """Estimate partial promotion-gate pass rates from pilot donor contrasts.

    The simulation preserves empirical residuals and scales the pilot mean to
    expose winner's-curse sensitivity. Gene-label and context-exchange
    permutation gates are intentionally outside this donor-summary model.
    """

    values = np.asarray(contrasts, dtype=float)
    if len(values) < 4:
        raise ValueError("power planning requires at least four pilot donors")
    if not np.isfinite(values).all() or np.std(values, ddof=1) <= 0:
        raise ValueError("pilot donor contrasts must be finite and variable")
    if min(donor_counts) < 4 or n_trials < 1 or n_bootstrap < 20:
        raise ValueError("invalid simulation size")
    scales = effect_scales or [0.5, 0.75, 1.0]
    if any(scale <= 0 for scale in scales):
        raise ValueError("effect scales must be positive")

    rng = np.random.default_rng(seed)
    pilot_mean = float(np.mean(values))
    residuals = values - pilot_mean
    results: list[dict[str, float | int]] = []
    for scale in scales:
        population = residuals + pilot_mean * scale
        for donor_count in donor_counts:
            passes = 0
            for _ in range(n_trials):
                trial = rng.choice(population, donor_count, replace=True)
                boot_indices = rng.integers(
                    0, donor_count, size=(n_bootstrap, donor_count)
                )
                ci_low = float(np.quantile(trial[boot_indices].mean(axis=1), 0.025))
                positive_fraction = float(np.mean(trial > 0))
                leave_one_out = (trial.sum() - trial) / (donor_count - 1)
                if (
                    ci_low > 0
                    and positive_fraction >= 0.70
                    and np.all(leave_one_out > 0)
                ):
                    passes += 1
            results.append(
                {
                    "donor_count": donor_count,
                    "effect_scale": float(scale),
                    "partial_gate_power": passes / n_trials,
                    "n_trials": n_trials,
                    "n_bootstrap": n_bootstrap,
                }
            )
    return results
