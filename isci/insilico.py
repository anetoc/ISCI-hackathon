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


def run_pert2state_baseline(de_stats, axis_vectors: dict) -> pd.DataFrame:
    """Reproduce Marson Fig. 4 linear model as mandatory baseline."""
    raise NotImplementedError("Implement in Claude Science build (D1-D2)")


def compute_in_silico_concordance(
    observed: pd.DataFrame,
    predicted: pd.DataFrame,
) -> pd.DataFrame:
    """Compute A(g,a,c) as agreement between predicted and observed axis projections."""
    raise NotImplementedError("Implement in Claude Science build (D2)")
