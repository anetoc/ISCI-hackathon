"""Q — causal / on-target QC confidence, separated from reproducibility (R).

Q answers: "is this knockdown a valid causal perturbation, or contaminated by
off-target / low expression / single-guide artifact?" — a different question from
R ("does the effect repeat across donors and guides?"). Splitting them keeps the
ISCI-core components interpretable (revised architecture, PI-approved).

Fields used (DE_stats.obs): ontarget_effect_size, ontarget_significant, low_target_gex,
neighboring_gene_KD, distal_offtarget_flag, n_guides, single_guide_estimate.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_qc(
    obs: pd.DataFrame,
    penalty_low_gex: float = 0.5,
    penalty_neighbor: float = 0.6,
    penalty_distal: float = 0.7,
    penalty_single_guide: float = 0.6,
) -> pd.Series:
    """Compute Q(g,c) in [0,1]: on-target knockdown validity, gated by artifact flags.

    Base = percentile rank of |ontarget_effect_size| among on-target-significant
    perturbations (0 for non-significant on-target). Then multiplicative penalties for
    low target expression, cis-neighbor knockdown, distal off-target, and single-guide
    estimates. Missing columns are treated as "no penalty" (robust to schema variation).
    """
    n = len(obs)

    eff = pd.to_numeric(obs.get("ontarget_effect_size", pd.Series(np.nan, index=obs.index)),
                        errors="coerce").abs()
    ontarget_ok = (obs["ontarget_significant"].fillna(False).astype(bool).to_numpy()
                   if "ontarget_significant" in obs else np.ones(n, dtype=bool))

    base = eff.where(pd.Series(ontarget_ok, index=obs.index), other=0.0)
    q = base.rank(pct=True).to_numpy()
    q = np.where(ontarget_ok, q, 0.0)  # non-significant on-target -> Q=0

    def _flag(col: str) -> np.ndarray:
        if col not in obs:
            return np.zeros(n, dtype=bool)
        return obs[col].fillna(False).astype(bool).to_numpy()

    q = q * np.where(_flag("low_target_gex"), penalty_low_gex, 1.0)
    q = q * np.where(_flag("neighboring_gene_KD"), penalty_neighbor, 1.0)
    q = q * np.where(_flag("distal_offtarget_flag"), penalty_distal, 1.0)
    q = q * np.where(_flag("single_guide_estimate"), penalty_single_guide, 1.0)

    return pd.Series(q, index=obs.index, name="Q_score")
