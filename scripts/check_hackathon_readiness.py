#!/usr/bin/env python3
"""Audit the reproducible hackathon package and separate human-only gates."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

try:  # Package import in tests; direct import when run as `python scripts/...`.
    from .release_provenance import source_paths_dirty, source_snapshot
except ImportError:  # pragma: no cover - exercised by the release CLI.
    from release_provenance import source_paths_dirty, source_snapshot


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.dataset_spec import (  # noqa: E402
    DatasetCapability,
    load_dataset_spec,
    validate_dataset_spec,
)
from isci.adapters import RuntimeCapability, load_tabular_dataset  # noqa: E402

OUTPUT = ROOT / "outputs" / "hackathon" / "readiness_report.json"
AXES = ROOT / "config" / "axes.yaml"
CLAIMS = ROOT / "outputs" / "hackathon" / "claim_manifest.json"
TIMING = ROOT / "config" / "hackathon_timing.json"
VIDEO = ROOT / "demo_assets" / "hackathon" / "hackathon_fallback_2m30.mp4"
VIDEO_MANIFEST = ROOT / "outputs" / "hackathon" / "video_manifest.json"
SCREENSHOT_MANIFEST = ROOT / "outputs" / "hackathon" / "screenshot_manifest.json"
DEMO = ROOT / "docs" / "hackathon_judge_demo.html"
DECK = ROOT / "outputs" / "isci_hackathon_medical_deck.pptx"
DATASET_SPEC_CODE = ROOT / "isci" / "dataset_spec.py"
DATASET_ADAPTER_CODE = ROOT / "isci" / "adapters" / "tabular.py"
DATASET_ADAPTER_EXPORTS = ROOT / "isci" / "adapters" / "__init__.py"
ANNDATA_ADAPTER_CODE = ROOT / "isci" / "adapters" / "anndata_effects.py"
CELL_PREFLIGHT_CODE = ROOT / "isci" / "adapters" / "anndata_cells.py"
DATASET_CLI_CODE = ROOT / "isci" / "cli.py"
DATASET_RUNNER_CODE = ROOT / "isci" / "analysis_runner.py"
FEATURE_EXTRACTION_CODE = ROOT / "isci" / "feature_extraction.py"
EFFECT_BUILDER_CODE = ROOT / "isci" / "effect_builder.py"
LOCKED_KERNEL = ROOT / "skills" / "isci-controllership" / "kernel.py"
LOCKED_METHOD = ROOT / "skills" / "isci-controllership" / "SKILL.md"
RESEARCHER_NOTEBOOK = ROOT / "notebooks" / "ISCI_Researcher_Track_Walkthrough.ipynb"
PYPROJECT = ROOT / "pyproject.toml"
DATASET_SPEC_SCHEMA = ROOT / "contracts" / "dataset_spec.schema.json"
DATASET_SPEC_DOC = ROOT / "docs" / "dataset_spec.md"
DATASET_SPEC_EXAMPLE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.yaml"
CELL_SPEC_EXAMPLE = ROOT / "examples" / "dataset_spec" / "scperturb_cell_h5ad.yaml"
CELL_PREFLIGHT_SMOKE = ROOT / "outputs" / "hackathon" / "cell_preflight_smoke.json"
DATASET_SPEC_FIXTURE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.csv"
DATASET_SPEC_POSITIVES = ROOT / "examples" / "dataset_spec" / "mini_positives.txt"
PROVENANCE_HELPER = ROOT / "scripts" / "release_provenance.py"


def sha256(path: Path) -> str:
    """Hash release artifacts for a local audit trail."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_output(*args: str) -> str:
    """Run a read-only Git query in the project root."""

    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def word_count(text: str) -> int:
    """Use the same compact word definition as the copy-contract tests."""

    return len(re.findall(r"\b[\w+→-]+\b", text))


def main() -> None:
    """Write PASS only for machine-verifiable gates; leave human gates explicit."""

    claims = json.loads(CLAIMS.read_text())
    timing = json.loads(TIMING.read_text())
    video_manifest = json.loads(VIDEO_MANIFEST.read_text())
    screenshot_manifest = json.loads(SCREENSHOT_MANIFEST.read_text())
    dataset_spec = load_dataset_spec(DATASET_SPEC_EXAMPLE, repo_root=ROOT, check_paths=True)
    dataset_spec_report = validate_dataset_spec(
        yaml.safe_load(DATASET_SPEC_EXAMPLE.read_text()), repo_root=ROOT, check_paths=True
    )
    cell_spec_report = validate_dataset_spec(yaml.safe_load(CELL_SPEC_EXAMPLE.read_text()))
    cell_preflight_smoke = json.loads(CELL_PREFLIGHT_SMOKE.read_text())["preflight"]
    dataset_adapter = load_tabular_dataset(dataset_spec, repo_root=ROOT)
    demo_html = DEMO.read_text()
    readme = (ROOT / "README.md").read_text()
    pyproject = PYPROJECT.read_text()
    anndata_adapter_source = ANNDATA_ADAPTER_CODE.read_text()
    cell_preflight_source = CELL_PREFLIGHT_CODE.read_text()
    dataset_runner_source = DATASET_RUNNER_CODE.read_text()
    feature_extraction_source = FEATURE_EXTRACTION_CODE.read_text()
    effect_builder_source = EFFECT_BUILDER_CODE.read_text()
    dataset_cli_source = DATASET_CLI_CODE.read_text()
    notebook = json.loads(RESEARCHER_NOTEBOOK.read_text())
    notebook_code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    notebook_errors = [
        output
        for cell in notebook_code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    submission = (ROOT / "SUBMISSION.md").read_text()
    summary = submission.split("## 150-word summary", 1)[1].split("---", 1)[0]
    stage_script = (ROOT / "DEMO_SCRIPT.md").read_text()
    spoken = " ".join(line[2:] for line in stage_script.splitlines() if line.startswith("> "))
    screenshots = sorted((ROOT / "demo_assets" / "hackathon").glob("[0-9][0-9]_*.png"))
    public_surfaces = [
        ROOT / "README.md",
        ROOT / "SUBMISSION.md",
        ROOT / "DEMO_SCRIPT.md",
        ROOT / "JUDGE_QA.md",
        ROOT / "DELIVERABLE.md",
        DATASET_SPEC_DOC,
        RESEARCHER_NOTEBOOK,
        DEMO,
    ]
    local_paths = [
        str(path.relative_to(ROOT)) for path in public_surfaces if "/Users/" in path.read_text()
    ]
    forbidden_tracked = [
        path
        for path in git_output("ls-files").splitlines()
        if path.endswith((".h5ad", ".h5mu", ".pem", ".key"))
        or Path(path).name in {".env", ".env.secure"}
    ]

    checks = {
        "four_verdicts_frozen": [claim["verdict"] for claim in claims["claims"]]
        == ["PASS", "FAIL", "NULL", "NOT-EVALUABLE"],
        "timing_is_150_seconds": sum(scene["duration_seconds"] for scene in timing["scenes"])
        == 150,
        "six_full_hd_fallbacks_present": len(screenshots) == 6,
        "screenshots_match_current_demo": screenshot_manifest["demo_sha256"] == sha256(DEMO)
        and all(
            sha256(ROOT / path) == expected
            for path, expected in screenshot_manifest["screenshots_sha256"].items()
        ),
        "video_matches_manifest": VIDEO.exists()
        and sha256(VIDEO) == video_manifest["output_sha256"],
        "video_is_150_seconds": video_manifest["duration_seconds"] == 150.0,
        "medical_deck_present": DECK.exists() and DECK.stat().st_size > 100_000,
        "dataset_spec_v1_valid": dataset_spec.schema_version == 1
        and dataset_spec.dataset.id == "mini_cd4_screen"
        and dataset_spec.benchmark is not None
        and dataset_spec_report.capability == DatasetCapability.CONFIRMATORY_DECLARED
        and dataset_adapter.inspection.runtime_capability == RuntimeCapability.DIAGNOSTIC_ONLY
        and dataset_adapter.inspection.canonical_rows == 8,
        "dataset_cli_registered": 'isci = "isci.cli:main"' in pyproject,
        "anndata_streaming_adapter_present": 'backed="r"' in anndata_adapter_source
        and "iter_anndata_effect_blocks" in anndata_adapter_source
        and "iter_anndata_group_effect_blocks" in anndata_adapter_source
        and "extract_controller_features_from_group_blocks" in feature_extraction_source
        and '"anndata>=0.10"' in pyproject,
        "cell_level_preflight_present": 'backed="r"' in cell_preflight_source
        and "CellPreflightStatus" in cell_preflight_source
        and "SIGNAL_VALUES_NOT_SCANNED" in cell_preflight_source
        and '"preflight-cells"' in dataset_cli_source
        and cell_spec_report.capability == DatasetCapability.PREPROCESSING_DECLARED
        and cell_preflight_smoke["status"] == "DIAGNOSTIC_ONLY"
        and cell_preflight_smoke["can_construct_effects"] is True
        and cell_preflight_smoke["biological_verdict"] == "NOT_ISSUED",
        "dataset_runner_bounded": "run_controller_features" in dataset_runner_source
        and '"biological_verdict": "NOT_ISSUED"' in dataset_runner_source
        and '"run"' in dataset_cli_source,
        "long_effect_feature_extraction_present": "extract_controller_features"
        in feature_extraction_source
        and "leave_one_marker_out" in feature_extraction_source
        and "run_dataset" in dataset_runner_source,
        "cell_effect_builder_present": "build_anndata_effects" in effect_builder_source
        and "SOURCE_NOT_RAW_COUNTS" in effect_builder_source
        and "def _standardize" in effect_builder_source
        and '"biological_verdict": "NOT_ISSUED"' in effect_builder_source,
        "researcher_notebook_executed": len(notebook_code_cells) >= 8
        and all(cell.get("execution_count") is not None for cell in notebook_code_cells)
        and not notebook_errors,
        "demo_is_offline": "https://" not in demo_html and "http://" not in demo_html,
        "submission_summary_within_limit": 140 <= word_count(summary) <= 150,
        "spoken_script_within_budget": 300 <= word_count(spoken) <= 380,
        "readme_scope_boundary_locked": "It does **not** survive" in readme
        and "ΔAUPRC −0.281 [−0.476, −0.073]" in readme
        and "cross-condition replication is within the same dataset" in readme
        and "survives removing regulators that are also axis markers" not in readme,
        "no_absolute_local_paths_on_public_surfaces": not local_paths,
        "no_forbidden_raw_or_secret_files_tracked": not forbidden_tracked,
    }
    automated_pass = all(checks.values())
    source_paths = [
        Path(__file__),
        PROVENANCE_HELPER,
        AXES,
        CLAIMS,
        TIMING,
        VIDEO,
        VIDEO_MANIFEST,
        SCREENSHOT_MANIFEST,
        DEMO,
        DECK,
        DATASET_SPEC_CODE,
        DATASET_ADAPTER_CODE,
        DATASET_ADAPTER_EXPORTS,
        ANNDATA_ADAPTER_CODE,
        CELL_PREFLIGHT_CODE,
        DATASET_CLI_CODE,
        DATASET_RUNNER_CODE,
        FEATURE_EXTRACTION_CODE,
        EFFECT_BUILDER_CODE,
        LOCKED_KERNEL,
        LOCKED_METHOD,
        RESEARCHER_NOTEBOOK,
        PYPROJECT,
        DATASET_SPEC_SCHEMA,
        DATASET_SPEC_EXAMPLE,
        CELL_SPEC_EXAMPLE,
        CELL_PREFLIGHT_SMOKE,
        DATASET_SPEC_FIXTURE,
        DATASET_SPEC_POSITIVES,
        *public_surfaces,
    ]
    report = {
        "schema_version": "hackathon_readiness_v1",
        "status": "AUTOMATED_GATES_PASS_HUMAN_GATES_PENDING"
        if automated_pass
        else "AUTOMATED_GATE_FAIL",
        "checks": checks,
        "details": {
            "submission_summary_words": word_count(summary),
            "spoken_script_words": word_count(spoken),
            "medical_deck_sha256": sha256(DECK) if DECK.exists() else None,
            "dataset_spec_schema_sha256": sha256(DATASET_SPEC_SCHEMA),
            "dataset_spec_example_capability": dataset_spec_report.capability.value,
            "dataset_spec_example_runtime": dataset_adapter.inspection.runtime_capability.value,
            "cell_spec_example_capability": cell_spec_report.capability.value,
            "cell_preflight_smoke_status": cell_preflight_smoke["status"],
            "cell_preflight_smoke_ready_units": cell_preflight_smoke[
                "perturbation_conditions_ready"
            ],
            "locked_kernel_sha256": sha256(LOCKED_KERNEL),
            "researcher_notebook_sha256": sha256(RESEARCHER_NOTEBOOK),
            "researcher_notebook_code_cells": len(notebook_code_cells),
            "local_path_violations": local_paths,
            "forbidden_tracked_files": forbidden_tracked,
        },
        "human_gates_pending": [
            "PI approves final bounded scientific wording",
            "three consecutive narrated rehearsals finish at or below 2:30",
            "microphone and screen recording are reviewed end-to-end",
            "public repository and uploaded video URLs are opened in a logged-out browser",
            "submission form is previewed before final irreversible submit",
        ],
        "git_sha": git_output("rev-parse", "HEAD"),
        "git_sha_semantics": "Base revision at generation time; source_snapshot binds exact working-tree inputs.",
        "source_paths_dirty": source_paths_dirty(source_paths, ROOT),
        "source_snapshot": source_snapshot(source_paths, ROOT),
        "branch": git_output("branch", "--show-current"),
        "data_sha256": sha256(CLAIMS),
        "axes_sha256": sha256(AXES),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": "python scripts/check_hackathon_readiness.py",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{report['status']}: {sum(checks.values())}/{len(checks)} automated gates passed")
    if not automated_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
