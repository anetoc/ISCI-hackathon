"""S — target-state stability / geometric coherence of post-perturbation state."""

from __future__ import annotations

import pandas as pd


def compute_stability(
    pseudobulk,
    by_guide_path: str | None = None,
    by_donors_path: str | None = None,
    magnitude_vectors: pd.Series | None = None,
) -> pd.DataFrame:
    """
    Compute S(g,a,c) via shesha-geometry with magnitude residualization (C3).

    Pseudobulk by_guide/by_donor dispersion is a proxy — validate on one
  single-cell subsample. Residualize C_raw against ||z|| before percentile rank.
    """
    raise NotImplementedError("Implement in Claude Science build (D2)")
