import json
from datetime import datetime
from pathlib import Path

from isci import build_dashboard, run_cci
from scripts.release_provenance import file_sha256, source_snapshot


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_RESULTS = {
    "marson_cd4": ROOT / "outputs" / "marson_cd4" / "cci_method_check.json",
    "norman_k562": ROOT / "outputs" / "norman_k562" / "cci_result.json",
    "replogle_rpe1": ROOT / "outputs" / "replogle_rpe1" / "cci_result.json",
}


def test_canonical_legacy_results_carry_content_addressed_provenance():
    """Every result emitted by run_cci must bind its real inputs and execution context."""

    for dataset_id, path in CANONICAL_RESULTS.items():
        payload = json.loads(path.read_text())
        for key in run_cci.PROVENANCE_KEYS:
            assert payload.get(key), f"{path} missing {key}"

        expected_snapshot = source_snapshot(run_cci.result_input_paths(dataset_id), ROOT)
        assert payload["provenance_schema"] == run_cci.PROVENANCE_SCHEMA
        assert payload["data_sha256"] == expected_snapshot["sha256"]
        assert payload["data_files_sha256"] == expected_snapshot["files_sha256"]
        assert payload["axes_sha256"] == file_sha256(run_cci.AXES_PATH)
        assert payload["config_sha256"] == file_sha256(run_cci.REGISTRY_PATH)
        assert payload["command"] == "python isci/run_cci.py"
        assert len(payload["git_sha"]) == 40
        datetime.fromisoformat(payload["timestamp"])


def test_provenance_backfill_does_not_change_locked_legacy_metrics():
    """Closing ENG-02 may add metadata, but it must not re-adjudicate scientific results."""

    expected = {
        "marson_cd4": (0.248, -0.043, 0.467, "DIAGNOSTIC (verdict fixed in result_lock.md)"),
        "norman_k562": (0.138, -0.033, 0.370, "FAIL"),
        "replogle_rpe1": (0.060, -0.013, 0.204, "FAIL"),
    }
    for dataset_id, path in CANONICAL_RESULTS.items():
        payload = json.loads(path.read_text())
        observed = (
            payload["delta_auprc"],
            payload["ci_lo"],
            payload["ci_hi"],
            payload["verdict"],
        )
        assert observed == expected[dataset_id]


def test_dashboard_accepts_provenance_without_changing_verdicts():
    """Canonical files should override legacy seed rows and retain their audit stamps."""

    runs = {run["id"]: run for run in build_dashboard.load_runs()}
    assert runs["norman_k562"]["verdict"] == "FAIL"
    assert runs["replogle_rpe1"]["verdict"] == "FAIL"
    assert runs["norman_k562"]["provenance_schema"] == run_cci.PROVENANCE_SCHEMA
    assert runs["replogle_rpe1"]["provenance_schema"] == run_cci.PROVENANCE_SCHEMA
