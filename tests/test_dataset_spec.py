import json
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from isci.dataset_spec import (
    DatasetCapability,
    DatasetSpecError,
    load_dataset_spec,
    validate_dataset_spec,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.yaml"


def example_raw():
    return yaml.safe_load(EXAMPLE.read_text())


def test_machine_readable_schema_is_valid_json_and_frozen_to_v1():
    schema = json.loads((ROOT / "contracts" / "dataset_spec.schema.json").read_text())
    assert schema["$schema"].endswith("2020-12/schema")
    assert schema["properties"]["schema_version"]["const"] == 1
    assert schema["additionalProperties"] is False


def test_example_loads_with_paths_and_declares_confirmatory_inputs():
    raw = example_raw()
    report = validate_dataset_spec(raw, repo_root=ROOT, check_paths=True)
    spec = load_dataset_spec(EXAMPLE, repo_root=ROOT, check_paths=True)

    assert report.valid
    assert report.capability == DatasetCapability.CONFIRMATORY_DECLARED
    assert spec.dataset.id == "mini_cd4_screen"
    assert spec.input.layout == "long_effects"
    assert spec.benchmark is not None
    assert spec.benchmark.negatives["match_on"] == (
        "target_expression",
        "n_guides",
        "n_cells",
        "condition",
    )


def test_valid_spec_without_benchmark_is_diagnostic_only():
    raw = example_raw()
    raw.pop("benchmark")
    report = validate_dataset_spec(raw)

    assert report.valid
    assert report.capability == DatasetCapability.DIAGNOSTIC_ONLY
    assert "No independent positive-set benchmark" in report.capability_notes[0]


def test_benchmark_cannot_drop_expression_matching_covariates():
    raw = example_raw()
    raw["benchmark"]["negatives"]["match_on"].remove("target_expression")
    report = validate_dataset_spec(raw)

    assert not report.valid
    assert report.capability == DatasetCapability.NOT_EVALUABLE
    assert {issue.code for issue in report.issues} == {"BENCHMARK_CONTRACT"}


def test_marker_leakage_control_cannot_be_disabled():
    raw = example_raw()
    raw["analysis"]["leave_one_marker_out"] = False
    report = validate_dataset_spec(raw)

    assert not report.valid
    assert any(issue.code == "LOO_REQUIRED" for issue in report.issues)


@pytest.mark.parametrize(
    ("path", "expected_code"),
    [
        ("/tmp/private.h5ad", "NON_PORTABLE_PATH"),
        ("C:\\private\\screen.h5ad", "NON_PORTABLE_PATH"),
        ("../outside/screen.h5ad", "PATH_TRAVERSAL"),
    ],
)
def test_unsafe_input_paths_are_rejected(path, expected_code):
    raw = example_raw()
    raw["input"]["path"] = path
    report = validate_dataset_spec(raw)

    assert not report.valid
    assert any(issue.code == expected_code for issue in report.issues)


def test_unknown_fields_are_rejected_instead_of_becoming_accidental_api():
    raw = example_raw()
    raw["dataset"]["magic_score"] = 0.99
    report = validate_dataset_spec(raw)

    assert not report.valid
    issue = next(issue for issue in report.issues if issue.code == "UNKNOWN_FIELD")
    assert issue.path == "dataset.magic_score"


def test_layout_specific_columns_are_required():
    raw = deepcopy(example_raw())
    raw["mapping"].pop("standardized_effect")
    report = validate_dataset_spec(raw)

    assert not report.valid
    assert any(issue.path == "mapping.standardized_effect" for issue in report.issues)


def test_loader_raises_structured_error_for_invalid_contract(tmp_path):
    raw = example_raw()
    raw["schema_version"] = 2
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text(yaml.safe_dump(raw))

    with pytest.raises(DatasetSpecError) as exc:
        load_dataset_spec(invalid)

    assert exc.value.report.capability == DatasetCapability.NOT_EVALUABLE
    assert exc.value.report.issues[0].code == "UNSUPPORTED_VERSION"
