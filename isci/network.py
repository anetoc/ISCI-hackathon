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


def infer_grn(de_stats, method: str = "collectri") -> object:
    """Infer directed GRN from perturbation structure and/or CollecTRI priors."""
    raise NotImplementedError("Implement in Claude Science build (D1)")


def compute_structural_control(grn: object, gene_names: list[str]) -> pd.Series:
    """
    Compute D(g) as continuous influence/controllability score (C5).

    Never use binary MFVS/MDS membership alone. Percentile-rank to [0, 1].
    """
    raise NotImplementedError("Implement in Claude Science build (D1)")
