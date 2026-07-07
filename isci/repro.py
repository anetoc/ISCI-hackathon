"""R — reproducibility weight from cross-donor and cross-guide QC fields."""

from __future__ import annotations

import pandas as pd


def compute_reproducibility(obs: pd.DataFrame) -> pd.Series:
    """
    Compute R(g,c) from DE_stats.obs columns:
    donor_correlation_hits_mean, guide_correlation_signif, ontarget_significant,
    single_guide_estimate, low_target_gex.

    Returns Series indexed by (perturbation, condition) with values in [0, 1].
    """
    raise NotImplementedError("Implement in Claude Science build (D0)")
