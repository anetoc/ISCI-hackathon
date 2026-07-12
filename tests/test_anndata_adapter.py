from dataclasses import replace
from pathlib import Path
import json

import numpy as np
import pandas as pd
import pytest
import yaml

from isci.adapters import (
    CellPreflightStatus,
    RuntimeCapability,
    inspect_anndata_dataset,
    iter_anndata_effect_blocks,
    iter_anndata_group_effect_blocks,
    preflight_anndata_cells,
)
from isci.dataset_spec import (
    BenchmarkSettings,
    CellPreprocessingSettings,
    DatasetInput,
    load_dataset_spec,
)
from isci.cli import EXIT_INVALID_SPEC, EXIT_SUCCESS, main
from isci.analysis_runner import run_dataset
from isci.effect_builder import build_anndata_effects

ad = pytest.importorskip("anndata")

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.yaml"
BASE_SPEC = load_dataset_spec(EXAMPLE, repo_root=ROOT)


def _write_h5ad(
    tmp_path,
    obs,
    *,
    effect=None,
    standardized=None,
    positives=("IRF1", "STAT6"),
    var_names=("STATE_A", "STATE_B", "STATE_C"),
    x=None,
):
    obs = obs.copy()
    obs.index = [f"obs_{index}" for index in range(len(obs))]
    n_obs = len(obs)
    var = pd.DataFrame(index=list(var_names))
    n_vars = len(var_names)
    effect = (
        np.asarray(effect)
        if effect is not None
        else np.arange(n_obs * n_vars).reshape(n_obs, n_vars) / 10
    )
    standardized = np.asarray(standardized) if standardized is not None else effect / 0.25
    x = np.asarray(x) if x is not None else np.zeros((n_obs, n_vars))
    adata = ad.AnnData(X=x, obs=obs, var=var)
    adata.layers["log_fc"] = effect
    adata.layers["zscore"] = standardized
    adata.write_h5ad(tmp_path / "effects.h5ad")
    (tmp_path / "positives.txt").write_text("\n".join(positives) + "\n")

    input_spec = DatasetInput(
        path="effects.h5ad",
        format="h5ad",
        layout="anndata_effects",
        sha256=None,
        layers={"effect": "log_fc", "standardized_effect": "zscore"},
    )
    mapping = {
        "perturbation": "target",
        "condition": "condition",
        "donor": "donor_id",
        "guide": "guide_id",
        "target_expression": "target_baseMean",
        "n_guides": "n_guides",
        "n_cells": "n_cells_target",
    }
    benchmark = BenchmarkSettings(
        positives={"source": "file", "path": "positives.txt"},
        negatives={
            "strategy": "expression_matched",
            "match_on": ("target_expression", "n_guides", "n_cells", "condition"),
        },
        expected_verdict=None,
    )
    return replace(BASE_SPEC, input=input_spec, mapping=mapping, benchmark=benchmark)


def _small_obs():
    return pd.DataFrame(
        {
            "target": ["IRF1", "IRF1", "STAT6", "GENE_X"],
            "condition": ["rest", "stim", "rest", "stim"],
            "donor_id": ["D1", "D2", "D1", "D2"],
            "guide_id": ["g1", "g2", "g3", "g4"],
            "target_baseMean": [5.0, 5.0, 4.5, 4.8],
            "n_guides": [2, 2, 1, 1],
            "n_cells_target": [200, 210, 190, 205],
        },
        index=["obs1", "obs2", "obs3", "obs4"],
    )


def _cell_obs(*, cells_per_stratum=10, include_donor=True):
    rows = []
    for donor_index, donor in enumerate(("D0", "D1")):
        for perturbation in ("NT", "CTRL_A", "CTRL_B"):
            for _ in range(cells_per_stratum):
                row = {
                    "target": perturbation,
                    "condition": "stim",
                    "replicate_id": f"R{donor_index}",
                    "guide_id": f"{perturbation}_g1",
                    "nperts": 0 if perturbation == "NT" else 1,
                    "target_baseMean": 5.0,
                    "n_guides": 1,
                    "n_cells_target": cells_per_stratum,
                }
                if include_donor:
                    row["donor_id"] = donor
                rows.append(row)
    return pd.DataFrame(rows)


def _cell_preflight_spec(tmp_path, observations, *, include_donor=True, x=None):
    spec = _write_h5ad(tmp_path, observations, positives=(), x=x)
    config = tmp_path / "config"
    config.mkdir(exist_ok=True)
    (config / "axes.yaml").write_text((ROOT / "config" / "axes.yaml").read_text())
    mapping = {
        "perturbation": "target",
        "condition": "condition",
        "replicate": "replicate_id",
        "guide": "guide_id",
        "guide_count": "nperts",
    }
    if include_donor:
        mapping["donor"] = "donor_id"
    preprocessing = CellPreprocessingSettings(
        source={"location": "X", "kind": "raw_counts"},
        control={"column": "target", "labels": ("NT",)},
        normalization="log1p_cpm",
        contrast="pseudobulk_difference",
        standardization="gene_wise_zscore_within_condition",
        min_cells_per_stratum=10,
        min_replicates=2,
        multi_guide_policy="exclude",
    )
    return replace(
        spec,
        input=replace(spec.input, layout="anndata_cells", layers={}),
        mapping=mapping,
        preprocessing=preprocessing,
        benchmark=None,
    )


def test_backed_inspection_validates_structure_without_loading_effect_values(tmp_path):
    spec = _write_h5ad(tmp_path, _small_obs())
    result = inspect_anndata_dataset(spec, repo_root=tmp_path)

    assert result.inspection.evaluable
    assert result.matrix_shape == (4, 3)
    assert result.values_scanned is False
    assert result.invalid_effect_values is None
    assert result.inspection.runtime_capability == RuntimeCapability.DIAGNOSTIC_ONLY
    assert result.inspection.n_perturbations == 3
    assert result.inspection.n_features == 3
    assert any(issue.code == "EFFECT_VALUES_NOT_SCANNED" for issue in result.inspection.issues)


def test_cell_preflight_finds_donor_resolved_effect_construction_coverage(tmp_path):
    spec = _cell_preflight_spec(tmp_path, _cell_obs())

    result = preflight_anndata_cells(spec, repo_root=tmp_path)

    assert result.status == CellPreflightStatus.READY_FOR_EFFECT_CONSTRUCTION
    assert result.can_construct_effects
    assert result.matrix_shape == (60, 3)
    assert result.eligible_effect_strata == 4
    assert result.underpowered_effect_strata == 0
    assert result.perturbation_conditions_ready == 2
    assert result.donor_resolved_conditions_ready == 2
    assert result.n_controls == 20
    assert any(issue.code == "SIGNAL_VALUES_NOT_SCANNED" for issue in result.issues)


def test_cell_preflight_is_diagnostic_without_donor_identity(tmp_path):
    observations = _cell_obs(include_donor=False)
    spec = _cell_preflight_spec(tmp_path, observations, include_donor=False)

    result = preflight_anndata_cells(spec, repo_root=tmp_path)

    assert result.status == CellPreflightStatus.DIAGNOSTIC_ONLY
    assert result.can_construct_effects
    assert any(issue.code == "DONOR_COVERAGE_INSUFFICIENT" for issue in result.issues)


def test_cell_preflight_audits_multi_guide_exclusion(tmp_path):
    observations = _cell_obs(cells_per_stratum=11)
    observations.loc[0, "nperts"] = 2
    spec = _cell_preflight_spec(tmp_path, observations)

    result = preflight_anndata_cells(spec, repo_root=tmp_path)

    assert result.status == CellPreflightStatus.READY_FOR_EFFECT_CONSTRUCTION
    assert result.multi_guide_cells == 1
    assert result.excluded_cells == 1


def test_cell_preflight_rejects_absent_controls_or_source_layer(tmp_path):
    observations = _cell_obs()
    no_controls = observations.assign(target="CTRL_A")
    control_spec = _cell_preflight_spec(tmp_path, no_controls)
    control_result = preflight_anndata_cells(control_spec, repo_root=tmp_path)

    layer_spec = _cell_preflight_spec(tmp_path, observations)
    layer_spec = replace(
        layer_spec,
        preprocessing=replace(
            layer_spec.preprocessing,
            source={"location": "layer", "layer": "counts", "kind": "raw_counts"},
        ),
    )
    layer_result = preflight_anndata_cells(layer_spec, repo_root=tmp_path)

    assert control_result.status == CellPreflightStatus.NOT_EVALUABLE
    assert any(issue.code == "CONTROLS_NOT_OBSERVED" for issue in control_result.issues)
    assert layer_result.status == CellPreflightStatus.NOT_EVALUABLE
    assert any(issue.code == "SOURCE_LAYER_MISSING" for issue in layer_result.issues)


def test_effect_builder_writes_a_valid_generated_effect_spec(tmp_path):
    observations = _cell_obs()
    profiles = {
        "NT": [10.0, 10.0, 10.0],
        "CTRL_A": [30.0, 10.0, 10.0],
        "CTRL_B": [10.0, 30.0, 10.0],
    }
    x = np.asarray([profiles[target] for target in observations["target"]])
    spec = _cell_preflight_spec(tmp_path, observations, x=x)
    output = tmp_path / "outputs" / "effects"

    result = build_anndata_effects(
        spec,
        repo_root=tmp_path,
        output_dir=output,
        block_rows=3,
    )

    assert result.completed
    assert result.status == "EFFECTS_BUILT"
    assert result.n_effect_rows == 4
    assert result.n_features == 3
    generated = load_dataset_spec(result.generated_spec_path, repo_root=tmp_path, check_paths=True)
    inspected = inspect_anndata_dataset(
        generated, repo_root=tmp_path, scan_values=True, block_rows=2
    )
    assert inspected.inspection.evaluable
    assert inspected.invalid_effect_values == 0
    built = ad.read_h5ad(result.effects_path)
    assert set(built.layers) == {"effect", "standardized_effect"}
    assert np.allclose(np.asarray(built.layers["standardized_effect"]).mean(axis=0), 0.0)


def test_effect_builder_stops_when_preflight_has_no_controls(tmp_path):
    observations = _cell_obs().assign(target="CTRL_A")
    spec = _cell_preflight_spec(tmp_path, observations)
    output = tmp_path / "outputs"

    result = build_anndata_effects(spec, repo_root=tmp_path, output_dir=output)

    assert result.status == "PREFLIGHT_FAILED"
    assert not output.exists()


def test_effect_builder_rejects_values_that_are_not_raw_counts(tmp_path):
    observations = _cell_obs()
    x = np.ones((len(observations), 3))
    x[0, 0] = -1.0
    spec = _cell_preflight_spec(tmp_path, observations, x=x)
    output = tmp_path / "outputs"

    result = build_anndata_effects(spec, repo_root=tmp_path, output_dir=output, block_rows=4)

    assert result.status == "SOURCE_VALUES_INVALID"
    assert result.report["reason"] == "SOURCE_NOT_RAW_COUNTS"
    assert not output.exists()


def test_full_value_scan_detects_nonfinite_effects(tmp_path):
    effect = np.arange(12, dtype=float).reshape(4, 3)
    effect[0, 0] = np.nan
    spec = _write_h5ad(tmp_path, _small_obs(), effect=effect)
    result = inspect_anndata_dataset(spec, repo_root=tmp_path, scan_values=True, block_rows=2)

    assert result.inspection.evaluable
    assert result.values_scanned is True
    assert result.invalid_effect_values == 2
    assert any(issue.code == "NONFINITE_EFFECT_VALUES" for issue in result.inspection.issues)


def test_missing_effect_layer_is_not_evaluable(tmp_path):
    spec = _write_h5ad(tmp_path, _small_obs())
    spec = replace(
        spec,
        input=replace(
            spec.input,
            layers={"effect": "missing", "standardized_effect": "zscore"},
        ),
    )
    result = inspect_anndata_dataset(spec, repo_root=tmp_path)

    assert result.inspection.runtime_capability == RuntimeCapability.NOT_EVALUABLE
    assert any(issue.code == "MISSING_LAYERS" for issue in result.inspection.issues)


def test_effect_matrix_is_streamed_in_bounded_long_form_blocks(tmp_path):
    spec = _write_h5ad(tmp_path, _small_obs())
    blocks = list(iter_anndata_effect_blocks(spec, repo_root=tmp_path, block_rows=2))

    assert [len(block) for block in blocks] == [6, 6]
    combined = pd.concat(blocks, ignore_index=True)
    assert len(combined) == 12
    assert combined.columns.tolist() == [
        "perturbation",
        "condition",
        "donor",
        "guide",
        "target_expression",
        "n_guides",
        "n_cells",
        "benchmark_positive",
        "feature",
        "effect",
        "standardized_effect",
    ]
    assert combined.loc[0, "feature"] == "STATE_A"
    assert combined.loc[0, "effect"] == 0.0


def test_group_stream_is_contiguous_even_when_h5ad_rows_are_interleaved(tmp_path):
    observations = _small_obs().iloc[[0, 3, 1, 2]].copy()
    observations["condition"] = "stim"
    spec = _write_h5ad(tmp_path, observations)

    grouped_blocks = list(iter_anndata_group_effect_blocks(spec, repo_root=tmp_path, block_rows=1))

    keys = [key for key, _ in grouped_blocks]
    assert keys == [
        ("stim", "GENE_X"),
        ("stim", "IRF1"),
        ("stim", "IRF1"),
        ("stim", "STAT6"),
    ]
    assert all(len(block) == 3 for _, block in grouped_blocks)
    assert all(block["perturbation"].nunique() == 1 for _, block in grouped_blocks)


def test_h5ad_can_reach_confirmatory_ready_only_after_value_scan(tmp_path):
    positives = [f"POS_{index}" for index in range(8)]
    negatives = [f"NEG_{index}" for index in range(15)]
    rows = []
    for perturbation in positives + negatives:
        for condition in ("rest", "stim"):
            for donor in range(6):
                for guide in range(2):
                    rows.append(
                        {
                            "target": perturbation,
                            "condition": condition,
                            "donor_id": f"D{donor}",
                            "guide_id": f"{perturbation}_g{guide}",
                            "target_baseMean": 5.0,
                            "n_guides": 2,
                            "n_cells_target": 250,
                        }
                    )
    spec = _write_h5ad(tmp_path, pd.DataFrame(rows), positives=positives)

    structural = inspect_anndata_dataset(spec, repo_root=tmp_path, scan_values=False)
    scanned = inspect_anndata_dataset(spec, repo_root=tmp_path, scan_values=True, block_rows=32)

    assert structural.inspection.runtime_capability == RuntimeCapability.BENCHMARK_READY
    assert scanned.inspection.runtime_capability == RuntimeCapability.CONFIRMATORY_READY
    assert scanned.invalid_effect_values == 0


def test_cli_dispatches_h5ad_to_low_memory_adapter(tmp_path, capsys):
    _write_h5ad(tmp_path, _small_obs())
    (tmp_path / "axes.yaml").write_text((ROOT / "config" / "axes.yaml").read_text())
    raw = yaml.safe_load(EXAMPLE.read_text())
    raw["input"] = {
        "path": "effects.h5ad",
        "format": "h5ad",
        "layout": "anndata_effects",
        "layers": {"effect": "log_fc", "standardized_effect": "zscore"},
    }
    raw["mapping"] = {
        "perturbation": "target",
        "condition": "condition",
        "donor": "donor_id",
        "guide": "guide_id",
        "target_expression": "target_baseMean",
        "n_guides": "n_guides",
        "n_cells": "n_cells_target",
    }
    raw["analysis"]["axes_path"] = "axes.yaml"
    raw["benchmark"]["positives"]["path"] = "positives.txt"
    spec_path = tmp_path / "dataset.yaml"
    spec_path.write_text(yaml.safe_dump(raw, sort_keys=False))

    exit_code = main(
        [
            "inspect",
            str(spec_path),
            "--repo-root",
            str(tmp_path),
            "--scan-values",
            "--block-rows",
            "2",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == EXIT_SUCCESS
    assert payload["adapter"] == "anndata_effects"
    assert payload["adapter_details"]["matrix_shape"] == [4, 3]
    assert payload["adapter_details"]["values_scanned"] is True


def test_h5ad_run_streams_features_into_the_same_auditable_ranking(tmp_path):
    observations = pd.DataFrame(
        {
            "target": ["CTRL_A", "CTRL_A", "CTRL_B", "CTRL_B", "CTRL_C", "CTRL_C"],
            "condition": ["stim"] * 6,
            "donor_id": ["D0", "D1"] * 3,
            "guide_id": [f"g{index}" for index in range(6)],
            "target_baseMean": [5.0] * 6,
            "n_guides": [2] * 6,
            "n_cells_target": [200] * 6,
        }
    )
    vectors = np.array(
        [
            [1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
            [1.0, 2.0, 1.0, 2.0],
            [1.0, 2.0, 1.0, 2.0],
            [-1.0, -1.0, -1.0, -1.0],
            [-1.0, -1.0, -1.0, -1.0],
        ]
    )
    spec = _write_h5ad(
        tmp_path,
        observations,
        effect=vectors / 2,
        standardized=vectors,
        var_names=("IL2", "IL2RA", "CD69", "TNF"),
    )
    spec = replace(spec, benchmark=None)
    config = tmp_path / "config"
    config.mkdir()
    (config / "axes.yaml").write_text((ROOT / "config" / "axes.yaml").read_text())
    kernel = tmp_path / "skills" / "isci-controllership"
    kernel.mkdir(parents=True)
    (kernel / "kernel.py").write_text(
        (ROOT / "skills" / "isci-controllership" / "kernel.py").read_text()
    )
    output = tmp_path / "outputs"

    result = run_dataset(spec, repo_root=tmp_path, output_dir=output, block_rows=1)

    assert result.completed
    assert len(result.ranking) == 3
    assert result.report["feature_extraction"]["methods"]["streaming_grouped"] is True
    assert result.report["feature_extraction"]["methods"]["peak_summary_buffer_rows"] == 8
    assert (output / "controller_features.csv").is_file()
    assert (output / "analysis_report.json").is_file()


def test_cli_preflight_cells_writes_structured_metadata_report(tmp_path, capsys):
    observations = _cell_obs()
    _write_h5ad(tmp_path, observations, positives=())
    (tmp_path / "axes.yaml").write_text((ROOT / "config" / "axes.yaml").read_text())
    raw = yaml.safe_load(EXAMPLE.read_text())
    raw["input"] = {
        "path": "effects.h5ad",
        "format": "h5ad",
        "layout": "anndata_cells",
    }
    raw["mapping"] = {
        "perturbation": "target",
        "condition": "condition",
        "donor": "donor_id",
        "replicate": "replicate_id",
        "guide": "guide_id",
        "guide_count": "nperts",
    }
    raw["preprocessing"] = {
        "source": {"location": "X", "kind": "raw_counts"},
        "control": {"column": "target", "labels": ["NT"]},
        "normalization": "log1p_cpm",
        "contrast": "pseudobulk_difference",
        "standardization": "gene_wise_zscore_within_condition",
        "min_cells_per_stratum": 10,
        "min_replicates": 2,
        "multi_guide_policy": "exclude",
    }
    raw["analysis"]["axes_path"] = "axes.yaml"
    raw.pop("benchmark")
    spec_path = tmp_path / "cells.yaml"
    spec_path.write_text(yaml.safe_dump(raw, sort_keys=False))
    report_path = tmp_path / "preflight.json"

    exit_code = main(
        [
            "preflight-cells",
            str(spec_path),
            "--repo-root",
            str(tmp_path),
            "--report",
            str(report_path),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == EXIT_SUCCESS
    assert payload["preflight"]["status"] == "READY_FOR_EFFECT_CONSTRUCTION"
    assert payload["preflight"]["biological_verdict"] == "NOT_ISSUED"
    assert payload["preflight"]["provenance"]["spec_sha256"]
    assert payload["preflight"]["provenance"]["axes_sha256"]
    assert "/Users/" not in json.dumps(payload)
    assert json.loads(report_path.read_text()) == payload

    inspect_exit = main(["inspect", str(spec_path), "--repo-root", str(tmp_path)])
    inspect_payload = json.loads(capsys.readouterr().out)
    assert inspect_exit == EXIT_INVALID_SPEC
    assert inspect_payload["error"]["code"] == "USE_PREFLIGHT_CELLS"
