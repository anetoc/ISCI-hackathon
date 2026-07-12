from isci.dataset_gates import evaluate_dataset_candidate


def complete_candidate():
    return {
        "external_independent": True,
        "primary_human_t_cells": True,
        "single_cell_perturbation": True,
        "donor_resolved": True,
        "donor_count": 8,
        "paired_contexts": True,
        "same_perturbations_across_contexts": True,
        "matched_controls": True,
        "eligible_positive_count": 12,
        "eligible_negative_count": 30,
        "public_processed_data": True,
    }


def test_complete_candidate_passes_confirmatory_gate():
    result = evaluate_dataset_candidate(complete_candidate())
    assert result["decision"] == "GO_CONFIRMATORY"
    assert not result["failed_gates"]
    assert not result["unknown_gates"]


def test_primary_screen_with_too_few_unresolved_donors_is_diagnostic_only():
    candidate = complete_candidate()
    candidate.update({"donor_count": 2, "donor_resolved": False})
    result = evaluate_dataset_candidate(candidate)
    assert result["decision"] == "DIAGNOSTIC_ONLY"
    assert set(result["failed_gates"]) == {"donor_resolved", "at_least_six_donors"}


def test_missing_metadata_is_not_silently_treated_as_failure():
    candidate = complete_candidate()
    candidate["donor_count"] = None
    candidate["eligible_positive_count"] = None
    result = evaluate_dataset_candidate(candidate)
    assert result["decision"] == "NEEDS_METADATA"
    assert set(result["unknown_gates"]) == {
        "at_least_six_donors",
        "positive_coverage",
    }
