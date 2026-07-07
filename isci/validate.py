"""Validation: AUROC/AUPRC, ablation, external transfer, clinical bridge."""

from __future__ import annotations

from typing import Sequence

import pandas as pd


def ground_truth_recovery(
    scores: pd.Series,
    positives: Sequence[str],
    negatives: Sequence[str] | None = None,
) -> dict[str, float]:
    """Return AUROC, AUPRC, precision@20, precision@50."""
    raise NotImplementedError("Implement in Claude Science build (D0)")


def ablation_curve(
    full_scores: pd.DataFrame,
    variants: dict[str, pd.DataFrame],
    positives: Sequence[str],
) -> pd.DataFrame:
    """Compare recovery metrics across ISCI full and ablated variants."""
    raise NotImplementedError("Implement in Claude Science build (D2)")


def project_clinical_signature(
    isci_signature: pd.Series,
    cohort_path: str,
    outcome_column: str,
) -> dict[str, float]:
    """D4: test responder vs non-responder separation (AUROC)."""
    raise NotImplementedError("Implement in Claude Science build (D4)")
