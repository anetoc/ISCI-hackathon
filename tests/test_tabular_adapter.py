from dataclasses import replace
from pathlib import Path

import pandas as pd

from isci.adapters import IssueSeverity, RuntimeCapability, load_tabular_dataset
from isci.dataset_spec import BenchmarkSettings, DatasetInput, load_dataset_spec

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.yaml"
BASE_SPEC = load_dataset_spec(EXAMPLE, repo_root=ROOT)


def _write_spec_inputs(
    tmp_path,
    frame,
    *,
    input_format="csv",
    positives=("IRF1", "STAT6"),
    sha256=None,
    mapping=None,
    layout="long_effects",
    benchmark=True,
):
    filename = f"input.{input_format}"
    if input_format == "csv":
        frame.to_csv(tmp_path / filename, index=False)
    else:
        frame.to_parquet(tmp_path / filename, index=False)
    (tmp_path / "positives.txt").write_text("\n".join(positives) + "\n")

    input_spec = DatasetInput(
        path=filename,
        format=input_format,
        layout=layout,
        sha256=sha256,
        layers={},
    )
    benchmark_spec = None
    if benchmark:
        benchmark_spec = BenchmarkSettings(
            positives={"source": "file", "path": "positives.txt"},
            negatives={
                "strategy": "expression_matched",
                "match_on": ("target_expression", "n_guides", "n_cells", "condition"),
            },
            expected_verdict=None,
        )
    return replace(
        BASE_SPEC,
        input=input_spec,
        mapping=mapping or BASE_SPEC.mapping,
        benchmark=benchmark_spec,
    )


def _example_frame():
    return pd.read_csv(ROOT / "examples" / "dataset_spec" / "mini_long_effects.csv")


def test_example_is_canonicalized_and_conservatively_downgraded():
    result = load_tabular_dataset(BASE_SPEC, repo_root=ROOT)
    inspection = result.inspection

    assert inspection.evaluable
    assert inspection.declared_capability == "CONFIRMATORY_DECLARED"
    assert inspection.runtime_capability == RuntimeCapability.DIAGNOSTIC_ONLY
    assert inspection.source_rows == inspection.canonical_rows == 8
    assert inspection.n_perturbations == 4
    assert inspection.n_positives == 2
    assert inspection.min_donors_per_positive == 2
    assert inspection.min_conditions_per_positive == 1
    assert (
        inspection.data_sha256 == "620b54d4ee9834d78bd66123d50cf18522ff392bc2fc5b1200a7730c039e994d"
    )
    assert {
        "perturbation",
        "feature",
        "effect",
        "standardized_effect",
        "benchmark_positive",
    }.issubset(result.table.columns)


def test_parquet_uses_the_same_canonical_contract(tmp_path):
    spec = _write_spec_inputs(tmp_path, _example_frame(), input_format="parquet")
    result = load_tabular_dataset(spec, repo_root=tmp_path)

    assert result.inspection.evaluable
    assert result.inspection.canonical_rows == 8
    assert result.table["effect"].dtype.kind == "f"


def test_missing_declared_column_is_not_evaluable(tmp_path):
    frame = _example_frame().drop(columns="zscore")
    spec = _write_spec_inputs(tmp_path, frame)
    result = load_tabular_dataset(spec, repo_root=tmp_path)

    assert result.inspection.runtime_capability == RuntimeCapability.NOT_EVALUABLE
    assert result.table.empty
    assert any(issue.code == "MISSING_COLUMNS" for issue in result.inspection.issues)


def test_hash_mismatch_stops_before_data_interpretation(tmp_path):
    spec = _write_spec_inputs(tmp_path, _example_frame(), sha256="0" * 64)
    result = load_tabular_dataset(spec, repo_root=tmp_path)

    assert result.inspection.runtime_capability == RuntimeCapability.NOT_EVALUABLE
    assert [issue.code for issue in result.inspection.issues] == ["HASH_MISMATCH"]


def test_invalid_rows_are_excluded_with_an_explicit_warning(tmp_path):
    frame = _example_frame()
    frame.loc[0, "zscore"] = float("nan")
    spec = _write_spec_inputs(tmp_path, frame)
    result = load_tabular_dataset(spec, repo_root=tmp_path)

    assert result.inspection.evaluable
    assert result.inspection.source_rows == 8
    assert result.inspection.canonical_rows == 7
    assert result.inspection.excluded_rows == 1
    warning = next(issue for issue in result.inspection.issues if issue.code == "ROWS_EXCLUDED")
    assert warning.severity == IssueSeverity.WARNING


def test_duplicate_canonical_keys_are_rejected(tmp_path):
    frame = _example_frame()
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    spec = _write_spec_inputs(tmp_path, frame)
    result = load_tabular_dataset(spec, repo_root=tmp_path)

    assert result.inspection.runtime_capability == RuntimeCapability.NOT_EVALUABLE
    assert any(issue.code == "DUPLICATE_KEYS" for issue in result.inspection.issues)


def test_symlink_cannot_escape_repository_root(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.csv"
    _example_frame().to_csv(outside, index=False)
    (root / "link.csv").symlink_to(outside)
    spec = replace(BASE_SPEC, input=replace(BASE_SPEC.input, path="link.csv"))
    result = load_tabular_dataset(spec, repo_root=root)

    assert result.inspection.runtime_capability == RuntimeCapability.NOT_EVALUABLE
    assert any(issue.code == "PATH_ESCAPE" for issue in result.inspection.issues)


def test_observed_coverage_can_reach_confirmatory_ready(tmp_path):
    positives = [f"POS_{index}" for index in range(8)]
    negatives = [f"NEG_{index}" for index in range(15)]
    rows = []
    for perturbation in positives + negatives:
        for condition in ("rest", "stim"):
            for donor in range(6):
                for guide in range(2):
                    rows.append(
                        {
                            "perturbation_gene": perturbation,
                            "measured_gene": "STATE_GENE",
                            "condition": condition,
                            "donor_id": f"D{donor}",
                            "guide_id": f"{perturbation}_g{guide}",
                            "log_fc": 0.2,
                            "zscore": 1.5,
                            "target_baseMean": 5.0,
                            "n_guides": 2,
                            "n_cells_target": 250,
                        }
                    )
    spec = _write_spec_inputs(tmp_path, pd.DataFrame(rows), positives=positives)
    result = load_tabular_dataset(spec, repo_root=tmp_path)

    assert result.inspection.runtime_capability == RuntimeCapability.CONFIRMATORY_READY
    assert result.inspection.n_positives == 8
    assert result.inspection.n_negative_pool == 15
    assert result.inspection.min_donors_per_positive == 6
    assert result.inspection.min_guides_per_positive == 2
    assert result.inspection.min_conditions_per_positive == 2


def test_controller_feature_layout_is_supported_without_a_benchmark(tmp_path):
    frame = pd.DataFrame(
        {
            "gene": ["A", "B", "C"],
            "mag": [0.2, 0.5, 0.8],
            "spec": [-0.1, 0.0, 0.4],
            "repro": [0.3, 0.4, 0.7],
        }
    )
    mapping = {
        "perturbation": "gene",
        "magnitude": "mag",
        "specificity": "spec",
        "reproducibility": "repro",
    }
    spec = _write_spec_inputs(
        tmp_path,
        frame,
        mapping=mapping,
        layout="controller_features",
        benchmark=False,
    )
    result = load_tabular_dataset(spec, repo_root=tmp_path)

    assert result.inspection.runtime_capability == RuntimeCapability.DIAGNOSTIC_ONLY
    assert result.inspection.n_perturbations == 3
    assert result.table.columns.tolist() == [
        "perturbation",
        "magnitude",
        "specificity",
        "reproducibility",
    ]
