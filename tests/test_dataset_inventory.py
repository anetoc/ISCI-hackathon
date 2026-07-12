from pathlib import Path

import yaml

from isci.dataset_gates import evaluate_dataset_candidate

ROOT = Path(__file__).resolve().parents[1]


def test_candidate_inventory_has_sources_unique_ids_and_no_unproven_go():
    config = yaml.safe_load((ROOT / "config/donor_dataset_candidates.yaml").read_text())
    candidates = config["candidates"]
    ids = [candidate["id"] for candidate in candidates]
    assert len(ids) == len(set(ids))
    assert all(candidate["sources"] for candidate in candidates)
    decisions = [evaluate_dataset_candidate(candidate)["decision"] for candidate in candidates]
    assert "GO_CONFIRMATORY" not in decisions
    assert decisions.count("DIAGNOSTIC_ONLY") >= 1
