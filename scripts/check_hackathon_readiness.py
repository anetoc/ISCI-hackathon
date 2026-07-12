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
DATASET_SPEC_SCHEMA = ROOT / "contracts" / "dataset_spec.schema.json"
DATASET_SPEC_DOC = ROOT / "docs" / "dataset_spec.md"
DATASET_SPEC_EXAMPLE = ROOT / "examples" / "dataset_spec" / "mini_long_effects.yaml"
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
    demo_html = DEMO.read_text()
    readme = (ROOT / "README.md").read_text()
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
        and dataset_spec_report.capability == DatasetCapability.CONFIRMATORY_DECLARED,
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
        DATASET_SPEC_SCHEMA,
        DATASET_SPEC_EXAMPLE,
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
