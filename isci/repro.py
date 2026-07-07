"""R — reproducibility across donors and guides (biological/technical replication).

R is now PURE reproducibility. The QC/on-target validity questions (off-target flags,
low expression, single-guide) live in qc.py as Q — a different question (revised
architecture). This keeps ISCI-core components non-overlapping and interpretable.

Fields used (DE_stats.obs): donor_correlation_hits_mean, guide_correlation_signif.
"""

from __future__ import annotations

import pandas as pd


def compute_reproducibility(
    obs: pd.DataFrame,
    w_donor: float = 0.5,
    w_guide: float = 0.5,
) -> pd.Series:
    """Compute R(g,c) in [0,1]: percentile rank of a donor/guide agreement blend.

    R = rank( w_donor * donor_correlation_hits_mean + w_guide * guide_correlation_signif ).
    NaN correlations -> 0 before ranking. Weights are hand-set priors (documented in
    method.md); the benchmark reports a sensitivity check. No QC gating here (see qc.py).
    """
    donor = pd.to_numeric(obs.get("donor_correlation_hits_mean"), errors="coerce").fillna(0.0)
    guide = pd.to_numeric(obs.get("guide_correlation_signif"), errors="coerce").fillna(0.0)
    combined = w_donor * donor.to_numpy() + w_guide * guide.to_numpy()
    return pd.Series(combined, index=obs.index).rank(pct=True).rename("R_score")
