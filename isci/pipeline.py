"""One-call orchestration for validated external DatasetSpec inputs."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from isci.analysis_runner import run_dataset
from isci.dataset_spec import DatasetSpec, load_dataset_spec
from isci.effect_builder import build_anndata_effects


@dataclass(frozen=True)
class PipelineResult:
    """Outcome and audit report for one end-to-end dataset attempt."""

    dataset_id: str
    status: str
    report_path: Path | None
    report: dict[str, Any]

    @property
    def completed(self) -> bool:
        return self.status == "ANALYSIS_COMPLETE"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_sha(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _relative(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root))


def run_pipeline(
    spec: DatasetSpec,
    *,
    repo_root: Path | str,
    output_dir: Path | str,
    block_rows: int = 64,
) -> PipelineResult:
    """Run an already effect-level dataset and bind the stages into one report."""

    root = Path(repo_root).resolve()
    destination = Path(output_dir).resolve()
    base = {
        "schema_version": "isci_pipeline_v1",
        "dataset_id": spec.dataset.id,
        "input_layout": spec.input.layout,
        "biological_verdict": "NOT_ISSUED",
    }
    if block_rows < 1 or not destination.is_relative_to(root):
        report = {**base, "status": "INVALID_OUTPUT", "stages": []}
        return PipelineResult(spec.dataset.id, "INVALID_OUTPUT", None, report)
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / "pipeline_report.json"
    stages: list[dict[str, Any]] = [
        {"name": "contract", "status": "VALIDATED", "layout": spec.input.layout}
    ]
    source_data_sha256: str | None = None
    effective_spec = spec
    if spec.input.layout == "anndata_cells":
        effects_dir = destination / "effects"
        build = build_anndata_effects(
            spec,
            repo_root=root,
            output_dir=effects_dir,
            block_rows=block_rows,
        )
        preflight = build.report.get("preflight", {})
        stages.extend(
            [
                {
                    "name": "cell_preflight",
                    "status": preflight.get("status", "NOT_EVALUABLE"),
                    "can_construct_effects": preflight.get("can_construct_effects", False),
                },
                {
                    "name": "effect_construction",
                    "status": build.status,
                    "output_dir": _relative(effects_dir, root),
                },
            ]
        )
        source_data_sha256 = build.report.get("input_sha256") or preflight.get("data_sha256")
        if not build.completed or build.generated_spec_path is None:
            report = {
                **base,
                "status": build.status,
                "stages": stages,
                "git_sha": _git_sha(root),
                "data_sha256": source_data_sha256,
                "axes_sha256": build.report.get("axes_sha256"),
                "spec_sha256": _sha256(spec.source_path) if spec.source_path else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "command": (
                    f"isci pipeline {spec.source_path.name if spec.source_path else '<dataset.yaml>'}"
                ),
            }
            report_path.write_text(json.dumps(report, indent=2) + "\n")
            return PipelineResult(spec.dataset.id, build.status, report_path, report)
        effective_spec = load_dataset_spec(
            build.generated_spec_path,
            repo_root=root,
            check_paths=True,
        )

    run_dir = destination / "run"
    analysis = run_dataset(
        effective_spec,
        repo_root=root,
        output_dir=run_dir,
        block_rows=block_rows,
    )
    stages.append(
        {
            "name": "analysis",
            "status": analysis.status,
            "output_dir": _relative(run_dir, root),
        }
    )
    analysis_data_sha256 = analysis.report.get("input_sha256")
    report = {
        **base,
        "status": analysis.status,
        "stages": stages,
        "git_sha": _git_sha(root),
        "data_sha256": source_data_sha256 or analysis_data_sha256,
        "analysis_data_sha256": analysis_data_sha256,
        "axes_sha256": analysis.report.get("axes_sha256"),
        "spec_sha256": _sha256(spec.source_path) if spec.source_path else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": f"isci pipeline {spec.source_path.name if spec.source_path else '<dataset.yaml>'}",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return PipelineResult(spec.dataset.id, analysis.status, report_path, report)
