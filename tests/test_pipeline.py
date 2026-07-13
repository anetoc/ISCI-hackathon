from pathlib import Path

import pandas as pd
import yaml

from isci.dataset_spec import load_dataset_spec
from isci.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.yaml"


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
