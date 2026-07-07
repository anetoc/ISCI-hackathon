"""Baselines: DE magnitude, effect size, centrality-only — must-beat comparators."""

from __future__ import annotations

import pandas as pd


def de_magnitude_baseline(obs: pd.DataFrame) -> pd.Series:
    """Baseline from n_total_de_genes or mean |zscore|."""
    raise NotImplementedError("Implement in Claude Science build (D0)")


def effect_size_baseline(obs: pd.DataFrame) -> pd.Series:
    """Baseline from n_downstream / ontarget_effect_size."""
    raise NotImplementedError("Implement in Claude Science build (D0)")
