"""A — in-silico concordance (pert2state, CellOracle, GEARS)."""

from __future__ import annotations

import pandas as pd


def run_pert2state_baseline(de_stats, axis_vectors: dict) -> pd.DataFrame:
    """Reproduce Marson Fig. 4 linear model as mandatory baseline."""
    raise NotImplementedError("Implement in Claude Science build (D1-D2)")


def compute_in_silico_concordance(
    observed: pd.DataFrame,
    predicted: pd.DataFrame,
) -> pd.DataFrame:
    """Compute A(g,a,c) as agreement between predicted and observed axis projections."""
    raise NotImplementedError("Implement in Claude Science build (D2)")
