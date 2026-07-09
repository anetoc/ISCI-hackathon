"""DEPRECATED — legacy multi-component ISCI (M/R/D/A/S).

This module belonged to the ORIGINAL ISCI-core index (movement/reproducibility/network/
in-silico/stability), which LOST to the trivial effect-magnitude baseline under
expression-matched negatives and was abandoned. The validated method is the
magnitude-conditional CCI test, implemented in the `isci-controllership` skill helpers
(conditional_lr_test, expression_matched_negatives, bootstrap_auprc_gain) and driven by
`isci/run_cci.py`. See reports/result_lock.md and reports/conditional_controllability_invariant.md.

Kept for provenance only. The NotImplementedError stubs below were never completed BY DESIGN —
this code path is not part of the locked result. Do not implement them; use run_cci.py.
"""

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
