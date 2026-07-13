from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from isci.dataset_spec import load_dataset_spec
from isci.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.yaml"
ad = pytest.importorskip("anndata")


def test_pipeline_runs_a_controller_feature_dataset_and_writes_audit_report(tmp_path):
    table = pd.DataFrame(
        {
            "target": ["A", "B", "C"],
            "magnitude": [1.0, 2.0, 3.0],
            "specificity": [0.9, 0.5, 0.2],
            "reproducibility": [0.8, 0.6, 0.4],
        }
    )
    table.to_csv(tmp_path / "features.csv", index=False)
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "axes.yaml").write_text((ROOT / "config" / "axes.yaml").read_text())
    kernel_dir = tmp_path / "skills" / "isci-controllership"
    kernel_dir.mkdir(parents=True)
    (kernel_dir / "kernel.py").write_text(
        (ROOT / "skills" / "isci-controllership" / "kernel.py").read_text()
    )
    raw = yaml.safe_load(EXAMPLE.read_text())
    raw["input"] = {
        "path": "features.csv",
        "format": "csv",
        "layout": "controller_features",
    }
    raw["mapping"] = {
        "perturbation": "target",
        "magnitude": "magnitude",
        "specificity": "specificity",
        "reproducibility": "reproducibility",
    }
    raw["analysis"]["axes_path"] = "config/axes.yaml"
    raw.pop("benchmark")
    spec_path = tmp_path / "dataset.yaml"
    spec_path.write_text(yaml.safe_dump(raw, sort_keys=False))
    spec = load_dataset_spec(spec_path, repo_root=tmp_path, check_paths=True)

    result = run_pipeline(
        spec,
        repo_root=tmp_path,
        output_dir=tmp_path / "outputs" / "pipeline",
    )

    assert result.completed
    assert result.report["biological_verdict"] == "NOT_ISSUED"
    assert [stage["status"] for stage in result.report["stages"]] == [
        "VALIDATED",
        "ANALYSIS_COMPLETE",
    ]
    assert result.report_path.is_file()
    assert (tmp_path / "outputs" / "pipeline" / "run" / "analysis_report.json").is_file()


def test_pipeline_builds_cell_effects_before_running_the_frozen_analysis(tmp_path):
    rows = []
    vectors = []
    profiles = {
        "NT": [2, 2, 2, 2],
        "CTRL_A": [8, 6, 4, 2],
        "CTRL_B": [2, 4, 6, 8],
        "CTRL_C": [4, 8, 2, 6],
    }
    for replicate in ("R0", "R1"):
        for perturbation in ("NT", "CTRL_A", "CTRL_B", "CTRL_C"):
            for _ in range(10):
                rows.append(
                    {
                        "target": perturbation,
                        "condition": "stim",
                        "replicate": replicate,
                        "guide": f"{perturbation}_g1",
                        "guide_count": 0 if perturbation == "NT" else 1,
                    }
                )
                vectors.append(profiles[perturbation])
    cells = ad.AnnData(
        X=np.asarray(vectors, dtype=np.float32),
        obs=pd.DataFrame(rows, index=[f"cell_{index}" for index in range(len(rows))]),
        var=pd.DataFrame(index=["IL2", "IL2RA", "CD69", "TNF"]),
    )
    cells.write_h5ad(tmp_path / "cells.h5ad")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "axes.yaml").write_text((ROOT / "config" / "axes.yaml").read_text())
    kernel_dir = tmp_path / "skills" / "isci-controllership"
    kernel_dir.mkdir(parents=True)
    (kernel_dir / "kernel.py").write_text(
        (ROOT / "skills" / "isci-controllership" / "kernel.py").read_text()
    )
    raw = yaml.safe_load(EXAMPLE.read_text())
    raw["input"] = {"path": "cells.h5ad", "format": "h5ad", "layout": "anndata_cells"}
    raw["mapping"] = {
        "perturbation": "target",
        "condition": "condition",
        "replicate": "replicate",
        "guide": "guide",
        "guide_count": "guide_count",
    }
    raw["preprocessing"] = {
        "source": {"location": "X", "kind": "raw_counts"},
        "control": {
            "column": "target",
            "labels": ["NT"],
            "match_on": ["condition", "replicate"],
        },
        "normalization": "log1p_cpm",
        "contrast": "pseudobulk_difference",
        "standardization": "gene_wise_zscore_within_condition",
        "min_cells_per_stratum": 10,
        "min_replicates": 2,
        "multi_guide_policy": "exclude",
        "perturbation_transform": "identity",
    }
    raw["analysis"]["axes_path"] = "config/axes.yaml"
    raw.pop("benchmark")
    spec_path = tmp_path / "cells.yaml"
    spec_path.write_text(yaml.safe_dump(raw, sort_keys=False))
    spec = load_dataset_spec(spec_path, repo_root=tmp_path, check_paths=True)

    result = run_pipeline(
        spec,
        repo_root=tmp_path,
        output_dir=tmp_path / "outputs" / "pipeline",
        block_rows=4,
    )

    assert result.completed
    assert [stage["status"] for stage in result.report["stages"]] == [
        "VALIDATED",
        "DIAGNOSTIC_ONLY",
        "DIAGNOSTIC_EFFECTS_BUILT",
        "ANALYSIS_COMPLETE",
    ]
    assert result.report["data_sha256"] != result.report["analysis_data_sha256"]
    assert (tmp_path / "outputs" / "pipeline" / "effects" / "effects.h5ad").is_file()
