import json
from pathlib import Path

import yaml

from isci.cli import EXIT_INVALID_SPEC, EXIT_SUCCESS, main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.yaml"


def _stdout_json(capsys):
    return json.loads(capsys.readouterr().out)


def test_validate_command_checks_contract_and_paths(capsys):
    exit_code = main(["validate", str(EXAMPLE), "--repo-root", str(ROOT)])
    payload = _stdout_json(capsys)

    assert exit_code == EXIT_SUCCESS
    assert payload["ok"] is True
    assert payload["report"]["capability"] == "CONFIRMATORY_DECLARED"
    assert payload["report"]["issues"] == []


def test_structure_only_can_validate_before_large_data_are_downloaded(tmp_path, capsys):
    raw = yaml.safe_load(EXAMPLE.read_text())
    raw["input"]["path"] = "data/not_downloaded_yet.csv"
    raw["analysis"]["axes_path"] = "config/not_downloaded_yet.yaml"
    raw["benchmark"]["positives"]["path"] = "config/positives_not_downloaded_yet.txt"
    spec_path = tmp_path / "queued.yaml"
    spec_path.write_text(yaml.safe_dump(raw, sort_keys=False))

    exit_code = main(["validate", str(spec_path), "--structure-only"])
    payload = _stdout_json(capsys)

    assert exit_code == EXIT_SUCCESS
    assert payload["report"]["valid"] is True


def test_invalid_yaml_has_one_structured_error_shape(tmp_path, capsys):
    spec_path = tmp_path / "invalid.yaml"
    spec_path.write_text("dataset: [unterminated")

    exit_code = main(["validate", str(spec_path)])
    payload = _stdout_json(capsys)

    assert exit_code == EXIT_INVALID_SPEC
    assert payload == {
        "command": "validate",
        "error": {"code": "INVALID_YAML", "message": "ParserError"},
        "ok": False,
    }


def test_inspect_command_reports_observed_downgrade_without_raw_values(capsys):
    exit_code = main(["inspect", str(EXAMPLE), "--repo-root", str(ROOT)])
    payload = _stdout_json(capsys)

    assert exit_code == EXIT_SUCCESS
    assert payload["ok"] is True
    assert payload["inspection"]["declared_capability"] == "CONFIRMATORY_DECLARED"
    assert payload["inspection"]["runtime_capability"] == "DIAGNOSTIC_ONLY"
    assert payload["inspection"]["canonical_rows"] == 8
    assert "IRF1" not in json.dumps(payload)


def test_inspect_can_write_a_report_and_canonical_table(tmp_path, capsys):
    report = tmp_path / "inspection.json"
    canonical = tmp_path / "canonical.csv"

    exit_code = main(
        [
            "inspect",
            str(EXAMPLE),
            "--repo-root",
            str(ROOT),
            "--report",
            str(report),
            "--canonical-output",
            str(canonical),
        ]
    )
    stdout_payload = _stdout_json(capsys)
    report_payload = json.loads(report.read_text())

    assert exit_code == EXIT_SUCCESS
    assert report_payload == stdout_payload
    assert report_payload["inspection"]["data_sha256"]
    assert canonical.read_text().splitlines()[0].startswith("perturbation,feature")


def test_invalid_canonical_extension_does_not_write_data(tmp_path, capsys):
    destination = tmp_path / "canonical.xlsx"
    exit_code = main(
        [
            "inspect",
            str(EXAMPLE),
            "--repo-root",
            str(ROOT),
            "--canonical-output",
            str(destination),
        ]
    )
    payload = _stdout_json(capsys)

    assert exit_code == EXIT_INVALID_SPEC
    assert payload["error"]["code"] == "INVALID_OUTPUT_FORMAT"
    assert not destination.exists()


def test_missing_spec_is_reported_without_traceback(capsys):
    exit_code = main(["inspect", "does-not-exist.yaml"])
    payload = _stdout_json(capsys)

    assert exit_code == EXIT_INVALID_SPEC
    assert payload["error"]["code"] == "SPEC_NOT_FOUND"
