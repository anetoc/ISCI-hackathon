"""ISCI aggregation, null permutation, FDR, and graceful degradation by ambition tier."""

from __future__ import annotations

import pandas as pd


def geometric_mean_components(
    m: pd.Series,
    d: pd.Series | None,
    a: pd.Series | None,
    s: pd.Series | None,
    r: pd.Series,
) -> pd.Series:
    """
    ISCI(g,a,c) = R * S * geomean(M, D, A) with missing components omitted (D0 = R * M).
    """
    raise NotImplementedError("Implement in Claude Science build (D0)")


def null_permutation_test(
    scores: pd.DataFrame,
    n_perm: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """Empirical p-values by shuffling perturbation labels; BH-FDR q-values."""
    raise NotImplementedError("Implement in Claude Science build (D0)")
