import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_ROOT = ROOT / "outputs/decomposition_v2/off_target_s0"


def test_committed_s0_result_satisfies_the_frozen_installation_gate() -> None:
    """The public result must preserve PASS evidence without issuing a biological verdict."""

    report = json.loads((RESULT_ROOT / "s0_execution_report.json").read_text())

    assert report["status"] == "S0_INSTALLATION_SMOKE_PASS"
    assert report["biological_verdict"] == "NOT_ISSUED"
    assert report["repeated_runs"] == 2
    assert report["identical_target_rows_after_canonical_sort"] is True
    assert len(report["git_sha"]) == 40
    assert report["engine"]["package_sha256"] == (
        "88aa3073a76f8b74b2a869ecf921c59241cf19267df877bafc285b8620cfc215"
    )
    assert all(run["status"] == "PASS" for run in report["runs"])
    assert all(run["unexpected_stderr"] is False for run in report["runs"])
    assert all(not run["errors"] for run in report["runs"])
    assert all(set(run["outputs"]) == {"targets", "profile", "extended_profile"} for run in report["runs"])


def test_committed_raw_target_rows_match_after_canonical_sort() -> None:
    """Both raw runs stay visible while order-only variation is normalized explicitly."""

    targets = [
        (RESULT_ROOT / f"runs/run_{run}/emx1.hg38.targets.txt").read_text().splitlines()
        for run in (1, 2)
    ]

    assert targets[0] != targets[1]
    assert sorted(targets[0]) == sorted(targets[1])
