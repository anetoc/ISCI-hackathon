"""Deterministic acquisition gates for donor-resolved external validation datasets."""

from __future__ import annotations

from typing import Any


def evaluate_dataset_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Return a conservative decision and explicit failed/unknown gates."""

    gates = {
        "external_independent": candidate.get("external_independent") is True,
        "primary_human_t_cells": candidate.get("primary_human_t_cells") is True,
        "single_cell_perturbation": candidate.get("single_cell_perturbation") is True,
        "donor_resolved": candidate.get("donor_resolved") is True,
        "at_least_six_donors": (
            candidate.get("donor_count") is not None and candidate["donor_count"] >= 6
        ),
        "paired_contexts": candidate.get("paired_contexts") is True,
        "same_perturbations_across_contexts": (
            candidate.get("same_perturbations_across_contexts") is True
        ),
        "matched_controls": candidate.get("matched_controls") is True,
        "positive_coverage": (
            candidate.get("eligible_positive_count") is not None
            and candidate["eligible_positive_count"] >= 8
        ),
        "negative_coverage": (
            candidate.get("eligible_negative_count") is not None
            and candidate["eligible_negative_count"] >= 15
        ),
        "public_processed_data": candidate.get("public_processed_data") is True,
    }
    unknown = [
        name
        for name, passed in gates.items()
        if not passed
        and candidate.get(
            {
                "at_least_six_donors": "donor_count",
                "positive_coverage": "eligible_positive_count",
                "negative_coverage": "eligible_negative_count",
            }.get(name, name)
        )
        is None
    ]
    failed = [name for name, passed in gates.items() if not passed and name not in unknown]
    if all(gates.values()):
        decision = "GO_CONFIRMATORY"
    elif not failed and unknown:
        decision = "NEEDS_METADATA"
    elif (
        candidate.get("primary_human_t_cells") is True
        and candidate.get("single_cell_perturbation") is True
        and candidate.get("matched_controls") is True
    ):
        decision = "DIAGNOSTIC_ONLY"
    else:
        decision = "NO_GO_CURRENT_CLAIM"
    return {
        "decision": decision,
        "gates": gates,
        "failed_gates": failed,
        "unknown_gates": unknown,
    }
