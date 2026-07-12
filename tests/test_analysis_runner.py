import hashlib
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from isci.analysis_runner import run_controller_features
from isci.dataset_spec import (
    AnalysisSettings,
    BenchmarkSettings,
    DatasetInput,
    load_dataset_spec,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.yaml"
BASE_SPEC = load_dataset_spec(EXAMPLE, repo_root=ROOT)


def _prepare_root(tmp_path):
    kernel_dir = tmp_path / "skills" / "isci-controllership"
    kernel_dir.mkdir(parents=True)
    kernel_dir.joinpath("kernel.py").write_text(
        (ROOT / "skills" / "isci-controllership" / "kernel.py").read_text()
    )
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_dir.joinpath("axes.yaml").write_text((ROOT / "config" / "axes.yaml").read_text())


def _controller_spec(tmp_path, *, n_positives=8, n_negatives=15):
    _prepare_root(tmp_path)
    positives = [f"POS_{index}" for index in range(n_positives)]
    negatives = [f"NEG_{index}" for index in range(n_negatives)]
    genes = positives + negatives
    rows = []
    rng = np.random.default_rng(7)
    for condition_index, condition in enumerate(("rest", "stim")):
        for gene_index, gene in enumerate(genes):
            is_positive = gene in positives
            magnitude = rng.normal(0.0, 1.0) + 0.25 * is_positive + 0.05 * condition_index
            specificity = rng.normal(0.0, 1.0) + 0.20 * is_positive
            reproducibility = rng.normal(0.0, 1.0) + 0.15 * is_positive
            match_position = gene_index % max(n_negatives, 1)
            for donor in range(6):
                for guide in range(2):
                    rows.append(
                        {
                            "gene": gene,
                            "condition": condition,
                            "donor": f"D{donor}",
                            "guide": f"{gene}_g{guide}",
                            "magnitude": magnitude,
                            "specificity": specificity,
                            "reproducibility": reproducibility,
                            "target_expression": float(match_position),
                            "n_guides": 2,
                            "n_cells": 200 + match_position,
                        }
                    )
    pd.DataFrame(rows).to_csv(tmp_path / "features.csv", index=False)
    (tmp_path / "positives.txt").write_text("\n".join(positives) + "\n")

    input_spec = DatasetInput(
        path="features.csv",
        format="csv",
        layout="controller_features",
        sha256=None,
        layers={},
    )
    mapping = {
        "perturbation": "gene",
        "condition": "condition",
        "donor": "donor",
        "guide": "guide",
        "magnitude": "magnitude",
        "specificity": "specificity",
        "reproducibility": "reproducibility",
        "target_expression": "target_expression",
        "n_guides": "n_guides",
        "n_cells": "n_cells",
    }
    benchmark = BenchmarkSettings(
        positives={"source": "file", "path": "positives.txt"},
        negatives={
            "strategy": "expression_matched",
            "match_on": ("target_expression", "n_guides", "n_cells", "condition"),
        },
        expected_verdict=None,
    )
    analysis = AnalysisSettings(
        axes_path="config/axes.yaml",
        primary_signal="standardized_effect",
        sensitivity_signal="effect",
        leave_one_marker_out=True,
        n_bootstrap=100,
        seed=11,
    )
    return replace(
        BASE_SPEC,
        input=input_spec,
        mapping=mapping,
        benchmark=benchmark,
        analysis=analysis,
        source_path=tmp_path / "dataset.yaml",
    )


def test_non_feature_layout_requests_extraction_without_fake_results():
    result = run_controller_features(BASE_SPEC, repo_root=ROOT)

    assert result.status == "FEATURE_EXTRACTION_REQUIRED"
    assert result.biological_verdict == "NOT_ISSUED"
    assert result.ranking.empty
    assert result.condition_metrics.empty


def test_underpowered_feature_table_produces_ranking_but_no_benchmark_claim(tmp_path):
    spec = _controller_spec(tmp_path, n_positives=2, n_negatives=4)
    result = run_controller_features(spec, repo_root=tmp_path)

    assert result.completed
    assert result.biological_verdict == "NOT_ISSUED"
    assert len(result.ranking) == 12
    assert set(result.condition_metrics["status"]) == {"UNDERPOWERED"}
    assert set(result.ranking["benchmark_positive"]) == {True, False}


def test_powered_feature_table_runs_locked_conditional_method_and_writes_hashes(tmp_path):
    try:
        import statsmodels.api  # noqa: F401
    except ImportError:
        pytest.skip("global statsmodels/scipy pair is incompatible; covered in isolated env")
    spec = _controller_spec(tmp_path)
    output = tmp_path / "outputs"
    result = run_controller_features(spec, repo_root=tmp_path, output_dir=output)

    assert result.completed
    assert result.biological_verdict == "NOT_ISSUED"
    assert len(result.ranking) == 46
    assert set(result.condition_metrics["status"]) == {"EVALUATED"}
    assert (
        result.report["kernel_sha256"]
        == hashlib.sha256(
            (tmp_path / "skills" / "isci-controllership" / "kernel.py").read_bytes()
        ).hexdigest()
    )
    report = json.loads((output / "analysis_report.json").read_text())
    assert report["biological_verdict"] == "NOT_ISSUED"
    assert "/Users/" not in json.dumps(report)
    for filename, expected in report["outputs_sha256"].items():
        assert hashlib.sha256((output / filename).read_bytes()).hexdigest() == expected


def test_ranking_and_metrics_are_deterministic_for_same_seed(tmp_path):
    spec = _controller_spec(tmp_path)
    first = run_controller_features(spec, repo_root=tmp_path)
    second = run_controller_features(spec, repo_root=tmp_path)

    pd.testing.assert_frame_equal(first.ranking, second.ranking)
    pd.testing.assert_frame_equal(first.condition_metrics, second.condition_metrics)
