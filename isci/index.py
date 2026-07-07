"""ISCI aggregation, null permutation, FDR, and graceful degradation by ambition tier."""

from __future__ import annotations

import pandas as pd


def geometric_mean_components(
    m: pd.Series,
    d: pd.Series | None,
    a: pd.Series | None,
    s: pd.Series | None,
    r: pd.Series,
    epsilon: float = 1e-3,
) -> pd.Series:
    """
    ISCI(g,a,c) = R * S * geomean_eps(M, D, A) with epsilon floor (C4).

    D0 degradation: R * geomean_eps(M) when D/A/S absent.
    """
    raise NotImplementedError("Implement in Claude Science build (D0)")


def null_permutation_test(
    scores: pd.DataFrame,
    n_perm: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """Empirical p-values by shuffling perturbation labels; BH-FDR q-values."""
    raise NotImplementedError("Implement in Claude Science build (D0)")
