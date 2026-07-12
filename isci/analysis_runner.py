"""Auditable DatasetSpec runner for precomputed controllership features.

This module reuses the frozen ``isci-controllership`` kernel. It produces rankings and
condition-level diagnostics, but deliberately does not issue a biological PASS/FAIL verdict for a
new dataset. Verdict adjudication remains a separate, pre-registered scientific decision.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

import pandas as pd

from isci.adapters import RuntimeCapability, load_tabular_dataset
from isci.dataset_spec import DatasetSpec


@dataclass(frozen=True)
class DatasetRunResult:
    dataset_id: str
    status: str
    biological_verdict: str
    ranking: pd.DataFrame
    condition_metrics: pd.DataFrame
    report: dict[str, Any]

    @property
    def completed(self) -> bool:
        return self.status == "ANALYSIS_COMPLETE"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_sha(repo_root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _load_locked_kernel(repo_root: Path) -> tuple[ModuleType, Path]:
    path = repo_root / "skills" / "isci-controllership" / "kernel.py"
    if not path.is_file():
        raise FileNotFoundError("frozen isci-controllership kernel is missing")
    module_spec = importlib.util.spec_from_file_location("isci_locked_controllership", path)
    if module_spec is None or module_spec.loader is None:
        raise ImportError("could not load frozen isci-controllership kernel")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module, path


def _base_report(spec: DatasetSpec, inspection: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    axes_path = repo_root / spec.analysis.axes_path
    return {
        "schema_version": "isci_dataset_run_v1",
        "dataset_id": spec.dataset.id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": _git_sha(repo_root),
        "input_sha256": inspection.get("data_sha256"),
        "axes_sha256": _sha256(axes_path) if axes_path.is_file() else None,
        "declared_capability": inspection.get("declared_capability"),
        "runtime_capability": inspection.get("runtime_capability"),
        "inspection": inspection,
        "method": {
            "name": "magnitude-conditional controllership",
            "primary_features": ["specificity", "reproducibility"],
            "negative_strategy": "screen-native expression matched within condition",
            "leave_one_marker_out": spec.analysis.leave_one_marker_out,
            "n_bootstrap": spec.analysis.n_bootstrap,
            "seed": spec.analysis.seed,
        },
        "biological_verdict": "NOT_ISSUED",
        "verdict_reason": (
            "The framework reports evidence; a biological PASS/FAIL requires a pre-registered "
            "dataset-specific adjudication outside this runner."
        ),
    }


def _aggregate_features(table: pd.DataFrame) -> pd.DataFrame:
    data = table.copy()
    if "condition" not in data:
        data["condition"] = "__all__"
    numeric = [
        column
        for column in (
            "magnitude",
            "specificity",
            "reproducibility",
            "coherence",
            "target_expression",
            "n_guides",
            "n_cells",
        )
        if column in data
    ]
    aggregations: dict[str, str] = {column: "mean" for column in numeric}
    if "benchmark_positive" in data:
        aggregations["benchmark_positive"] = "max"
    return (
        data.groupby(["condition", "perturbation"], as_index=False, observed=True)
        .agg(aggregations)
        .sort_values(["condition", "perturbation"])
        .reset_index(drop=True)
    )


def _rank_condition(kernel: ModuleType, condition_frame: pd.DataFrame) -> pd.DataFrame:
    feat = condition_frame.drop(columns="condition").set_index("perturbation").copy()
    components = ["magnitude", "specificity", "reproducibility"]
    feat["balanced_score"] = kernel.controllership_score(
        feat,
        components=components,
        method="balanced",
        magnitude_col="magnitude",
    )
    feat["orthogonal_score"] = kernel.controllership_score(
        feat,
        components=components,
        method="orthogonal",
        magnitude_col="magnitude",
        detectable_floor=False,
    )
    detectable = feat["magnitude"] >= feat["magnitude"].median()
    feat["detectable_effect"] = detectable
    feat["orthogonal_score_gated"] = feat["orthogonal_score"].where(detectable)
    feat["orthogonal_rank"] = feat["orthogonal_score_gated"].rank(ascending=False, method="min")
    return feat.reset_index().sort_values(
        ["orthogonal_score_gated", "balanced_score"], ascending=[False, False], na_position="last"
    )


def _condition_metrics(
    kernel: ModuleType,
    condition: str,
    ranked: pd.DataFrame,
    n_bootstrap: int,
    seed: int,
) -> dict[str, Any]:
    positives = ranked.loc[ranked["benchmark_positive"], "perturbation"].tolist()
    all_negatives = ranked.loc[~ranked["benchmark_positive"], "perturbation"].tolist()
    if len(positives) < 8 or len(all_negatives) < 15:
        return {
            "condition": condition,
            "status": "UNDERPOWERED",
            "n_positives": len(positives),
            "n_matched_negatives": 0,
            "reason": "requires at least 8 observed positives and 15 negative candidates",
        }

    match_columns = ["target_expression", "n_guides", "n_cells"]
    matching = ranked.rename(columns={"perturbation": "gene"})
    negatives: list[str] = []
    for n_per_positive in range(8, len(all_negatives) + 1):
        negatives = kernel.expression_matched_negatives(
            positives=positives,
            obs=matching,
            gene_col="gene",
            match_cols=match_columns,
            n_per_positive=n_per_positive,
        )
        if len(negatives) >= 15:
            break
    if len(negatives) < 15:
        return {
            "condition": condition,
            "status": "UNDERPOWERED_AFTER_MATCHING",
            "n_positives": len(positives),
            "n_matched_negatives": len(negatives),
            "reason": "expression matching produced fewer than 15 unique negatives",
        }

    feat = ranked.set_index("perturbation")
    try:
        lr = kernel.conditional_lr_test(
            feat,
            positives=positives,
            negatives=negatives,
            base_col="magnitude",
            feature_cols=["specificity", "reproducibility"],
        )
        gain = kernel.bootstrap_auprc_gain(
            feat,
            positives=positives,
            negatives=negatives,
            base_col="magnitude",
            score_col="orthogonal_score",
            n_boot=n_bootstrap,
            seed=seed,
        )
    except Exception as exc:
        return {
            "condition": condition,
            "status": "MODEL_ERROR",
            "n_positives": len(positives),
            "n_matched_negatives": len(negatives),
            "reason": type(exc).__name__,
        }

    lr_by_feature = {
        row["feature"]: {
            "lr_stat": float(row["lr_stat"]),
            "p_value": float(row["p_value"]),
            "coefficient": float(row["coef"]),
            "adds_at_0_05": bool(row["adds"]),
        }
        for _, row in lr.iterrows()
    }
    return {
        "condition": condition,
        "status": "EVALUATED",
        "n_positives": len(positives),
        "n_matched_negatives": len(negatives),
        "base_auprc": float(gain["base_auprc"]),
        "orthogonal_auprc": float(gain["full_auprc"]),
        "descriptive_auprc_gain": float(gain["gain"]),
        "gain_ci_low": float(gain["ci95"][0]),
        "gain_ci_high": float(gain["ci95"][1]),
        "bootstrap_p_gain_gt_zero": float(gain["p_gain_gt0"]),
        "conditional_lr": lr_by_feature,
        "interpretation": (
            "Descriptive fixed-score bootstrap; not the leakage-free OOF estimand and not a verdict."
        ),
    }


def run_controller_features(
    spec: DatasetSpec,
    *,
    repo_root: Path | str,
    output_dir: Path | str | None = None,
) -> DatasetRunResult:
    """Rank a controller-feature table and conditionally benchmark it against magnitude."""

    root = Path(repo_root).resolve()
    adapter = load_tabular_dataset(spec, repo_root=root)
    inspection = adapter.inspection.to_dict()
    report = _base_report(spec, inspection, root)

    if spec.input.layout != "controller_features":
        report.update(
            {
                "status": "FEATURE_EXTRACTION_REQUIRED",
                "reason": "run_controller_features requires input.layout=controller_features",
            }
        )
        return DatasetRunResult(
            spec.dataset.id,
            "FEATURE_EXTRACTION_REQUIRED",
            "NOT_ISSUED",
            pd.DataFrame(),
            pd.DataFrame(),
            report,
        )
    if adapter.inspection.runtime_capability == RuntimeCapability.NOT_EVALUABLE:
        report.update({"status": "NOT_EVALUABLE", "reason": "physical adapter rejected input"})
        return DatasetRunResult(
            spec.dataset.id,
            "NOT_EVALUABLE",
            "NOT_ISSUED",
            pd.DataFrame(),
            pd.DataFrame(),
            report,
        )

    kernel, kernel_path = _load_locked_kernel(root)
    features = _aggregate_features(adapter.table)
    rankings = []
    metrics = []
    for condition, frame in features.groupby("condition", observed=True, sort=True):
        ranked = _rank_condition(kernel, frame)
        ranked.insert(0, "condition", str(condition))
        ranked.insert(0, "dataset_id", spec.dataset.id)
        rankings.append(ranked)
        if "benchmark_positive" in ranked:
            metrics.append(
                _condition_metrics(
                    kernel,
                    str(condition),
                    ranked,
                    n_bootstrap=spec.analysis.n_bootstrap,
                    seed=spec.analysis.seed,
                )
            )

    ranking = pd.concat(rankings, ignore_index=True)
    condition_metrics = pd.DataFrame(metrics)
    spec_label = "<dataset.yaml>"
    if spec.source_path is not None:
        try:
            spec_label = str(spec.source_path.resolve().relative_to(root))
        except ValueError:
            spec_label = spec.source_path.name
    report.update(
        {
            "status": "ANALYSIS_COMPLETE",
            "kernel_sha256": _sha256(kernel_path),
            "conditions": metrics,
            "ranking_rows": len(ranking),
            "command": f"isci run {spec_label}",
        }
    )
    result = DatasetRunResult(
        spec.dataset.id,
        "ANALYSIS_COMPLETE",
        "NOT_ISSUED",
        ranking,
        condition_metrics,
        report,
    )
    if output_dir is not None:
        save_dataset_run(result, output_dir)
    return result


def save_dataset_run(result: DatasetRunResult, output_dir: Path | str) -> None:
    """Write deterministic tables and a report that binds their SHA-256 hashes."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    ranking_path = destination / "controller_ranking.csv"
    metrics_path = destination / "condition_metrics.json"
    report_path = destination / "analysis_report.json"
    result.ranking.to_csv(ranking_path, index=False)
    metrics_path.write_text(
        json.dumps(result.condition_metrics.to_dict(orient="records"), indent=2) + "\n"
    )
    report = dict(result.report)
    report["outputs_sha256"] = {
        "controller_ranking.csv": _sha256(ranking_path),
        "condition_metrics.json": _sha256(metrics_path),
    }
    report_path.write_text(json.dumps(report, indent=2, default=str) + "\n")
