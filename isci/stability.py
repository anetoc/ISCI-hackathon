"""S — target-state stability / geometric coherence of post-perturbation state."""

from __future__ import annotations

import pandas as pd


def compute_stability(
    pseudobulk,
    by_guide_path: str | None = None,
    by_donors_path: str | None = None,
) -> pd.DataFrame:
    """
    Compute S(g,a,c) from geometric coherence across guide and donor replicates.

    High S = tight attractor; low S = scattered / unstable intermediate state.
    """
    raise NotImplementedError("Implement in Claude Science build (D2)")
