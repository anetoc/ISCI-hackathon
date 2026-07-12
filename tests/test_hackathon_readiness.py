import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs" / "hackathon" / "readiness_report.json"


def test_readiness_report_passes_automated_gates_without_faking_human_approval():
    """Machine checks may pass, but narration and PI approval remain explicit gates."""

    report = json.loads(REPORT.read_text())
    assert report["status"] == "AUTOMATED_GATES_PASS_HUMAN_GATES_PENDING"
    assert all(report["checks"].values())
    assert len(report["checks"]) == 14
    assert len(report["human_gates_pending"]) == 5
    assert report["details"]["local_path_violations"] == []
    assert report["details"]["forbidden_tracked_files"] == []
    assert len(report["details"]["medical_deck_sha256"]) == 64
    assert len(report["details"]["dataset_spec_schema_sha256"]) == 64
    assert report["details"]["dataset_spec_example_capability"] == "CONFIRMATORY_DECLARED"
    assert report["details"]["dataset_spec_example_runtime"] == "DIAGNOSTIC_ONLY"
