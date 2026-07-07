"""R — reproducibility weight from cross-donor and cross-guide QC fields."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_reproducibility(
    obs: pd.DataFrame,
    w_donor: float = 0.5,
    w_guide: float = 0.5,
    gate_penalty: float = 0.5,
) -> pd.Series:
    """Compute R(g,c) in [0,1] from DE_stats.obs QC fields.

    R = percentile_rank( w_donor * donor_correlation_hits_mean
                        + w_guide * guide_correlation_signif ),
    then multiplicatively gated: perturbations that fail on-target KD, are
    single-guide estimates, or have low target expression are down-weighted by
    ``gate_penalty`` (not dropped — flagged). NaN correlations -> 0 before ranking.

    Weights are hand-set priors (documented in method.md); index.py exposes a
    sensitivity check. Returns a Series aligned to ``obs`` row order.
    """
    donor = pd.to_numeric(obs.get("donor_correlation_hits_mean"), errors="coerce").fillna(0.0)
    guide = pd.to_numeric(obs.get("guide_correlation_signif"), errors="coerce").fillna(0.0)
    combined = w_donor * donor.to_numpy() + w_guide * guide.to_numpy()
    r = pd.Series(combined, index=obs.index).rank(pct=True)

    # multiplicative QC gates
    def _flag(col: str) -> np.ndarray:
        if col not in obs:
            return np.zeros(len(obs), dtype=bool)
        return obs[col].fillna(False).astype(bool).to_numpy()

    ontarget_ok = _flag("ontarget_significant")
    single_guide = _flag("single_guide_estimate")
    low_gex = _flag("low_target_gex")

    gate = np.ones(len(obs))
    gate[~ontarget_ok] *= gate_penalty
    gate[single_guide] *= gate_penalty
    gate[low_gex] *= gate_penalty

    return pd.Series(r.to_numpy() * gate, index=obs.index)
