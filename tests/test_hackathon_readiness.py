import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs" / "hackathon" / "readiness_report.json"


def test_readiness_report_records_the_submitted_public_package():
    """Machine checks and author-confirmed submission state must remain distinguishable."""

    report = json.loads(REPORT.read_text())
    assert report["schema_version"] == "hackathon_readiness_v2"
    assert report["status"] == "SUBMITTED_AUTOMATED_GATES_PASS"
    assert all(report["checks"].values())
    assert len(report["checks"]) == 21
    assert "human_gates_pending" not in report
    assert report["submission"] == {
        "status": "SUBMITTED",
        "confirmation_basis": "Author-confirmed; private platform receipt is not committed.",
        "repository_url": "https://github.com/anetoc/ISCI-hackathon",
        "interactive_demo_url": "https://anetoc.github.io/ISCI-hackathon/",
        "narrated_video_url": "https://youtu.be/7Rz4PpmQZuI",
    }
    assert report["details"]["local_path_violations"] == []
    assert report["details"]["forbidden_tracked_files"] == []
    assert len(report["details"]["medical_deck_sha256"]) == 64
    assert len(report["details"]["dataset_spec_schema_sha256"]) == 64
    assert report["details"]["dataset_spec_example_capability"] == "CONFIRMATORY_DECLARED"
    assert report["details"]["dataset_spec_example_runtime"] == "DIAGNOSTIC_ONLY"
    assert len(report["details"]["locked_kernel_sha256"]) == 64
    assert len(report["details"]["researcher_notebook_sha256"]) == 64
    assert report["details"]["researcher_notebook_code_cells"] >= 8
