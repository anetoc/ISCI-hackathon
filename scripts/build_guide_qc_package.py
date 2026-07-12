#!/usr/bin/env python
"""Build guide replacement backups and a deliberately blocked off-target input package."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.guide_sequence_validation import (  # noqa: E402
    build_off_target_screening_input,
    build_replacement_shortlist,
)

DEFAULT_PANEL = ROOT / "outputs/decomposition_v2/prospective_donor_panel_sequences.csv"
DEFAULT_CANDIDATES = ROOT / "outputs/decomposition_v2/gse190604_calabrese_panel_candidates.csv"
DEFAULT_AXES = ROOT / "config/axes.yaml"
DEFAULT_SHORTLIST = ROOT / "outputs/decomposition_v2/guide_replacement_shortlist.csv"
DEFAULT_SCREENING = ROOT / "outputs/decomposition_v2/off_target_screening_input.csv"
DEFAULT_SUMMARY = ROOT / "outputs/decomposition_v2/guide_qc_triage.json"
REFERENCE_BUILD = "GCF_000001405.40_GRCh38.p14"
TRANSCRIPT_TSS_ANNOTATION = "GCF_000001405.40-RS_2025_08"


def sha256(path: Path) -> str:
    """Hash source artifacts in bounded chunks."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_provenance(table: pd.DataFrame, provenance: dict[str, str]) -> pd.DataFrame:
    """Attach the required artifact contract to a generated result table."""

    result = table.copy()
    for key, value in provenance.items():
        result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--axes", type=Path, default=DEFAULT_AXES)
    parser.add_argument("--candidates-per-target", type=int, default=3)
    parser.add_argument("--shortlist-output", type=Path, default=DEFAULT_SHORTLIST)
    parser.add_argument("--screening-output", type=Path, default=DEFAULT_SCREENING)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    required = [args.panel, args.candidates, args.axes]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"missing guide-QC inputs: {missing}")

    panel = pd.read_csv(args.panel)
    candidates = pd.read_csv(args.candidates)
    shortlist = build_replacement_shortlist(
        panel,
        candidates,
        candidates_per_target=args.candidates_per_target,
    )
    screening = build_off_target_screening_input(
        panel,
        shortlist,
        reference_build=REFERENCE_BUILD,
        transcript_tss_annotation=TRANSCRIPT_TSS_ANNOTATION,
    )

    git_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    input_hashes = {
        str(path.resolve().relative_to(ROOT)): sha256(path) for path in required
    }
    input_manifest = json.dumps(input_hashes, sort_keys=True)
    provenance = {
        "git_sha": git_sha,
        "data_sha256": hashlib.sha256(input_manifest.encode()).hexdigest(),
        "axes_sha256": sha256(args.axes),
        "timestamp": datetime.now().astimezone().isoformat(),
        "command": shlex.join(["python", *sys.argv]),
        "method_version": "guide_qc_replacement_shortlist_v1",
    }
    shortlist = add_provenance(shortlist, provenance)
    screening = add_provenance(screening, provenance)

    review_mask = panel["source_identity_status"].ne(
        "SOURCE_IDENTITY_CONFIRMED"
    ) | panel["basic_sequence_flags"].ne("NONE")
    review_guides = panel.loc[review_mask, "guide_id"].astype(str).tolist()
    high_priority_targets = (
        shortlist.loc[
            shortlist["replacement_priority"] == "HIGH_ALL_CURRENT_GUIDES_REVIEW",
            "target",
        ]
        .drop_duplicates()
        .tolist()
    )
    payload = {
        "status": "OFF_TARGET_PACKAGE_READY_ENGINE_NOT_FROZEN",
        "current_panel": {
            "n_guides": int(panel["guide_id"].nunique()),
            "n_guides_in_basic_or_source_review": len(review_guides),
            "guides_in_review": review_guides,
        },
        "fallbacks": {
            "n_targets": int(shortlist["target"].nunique()),
            "n_candidates": len(shortlist),
            "candidates_per_target": args.candidates_per_target,
            "high_priority_targets": high_priority_targets,
            "automatic_substitutions": 0,
        },
        "off_target_package": {
            "n_current_guides": int(
                (screening["candidate_kind"] == "CURRENT_GUIDE").sum()
            ),
            "n_fallback_candidates": int(
                (screening["candidate_kind"] == "FALLBACK_CANDIDATE").sum()
            ),
            "reference_build": REFERENCE_BUILD,
            "transcript_tss_annotation": TRANSCRIPT_TSS_ANNOTATION,
            "search_engine": "UNSELECTED",
            "status": "BLOCKED_ENGINE_AND_PARAMETERS_NOT_FROZEN",
        },
        "boundary": (
            "Technical backup ordering only. No current guide is replaced, no controller label "
            "changes, and no guide is ready for synthesis."
        ),
        "input_sha256": input_hashes,
        "provenance": provenance,
    }

    for path in [args.shortlist_output, args.screening_output, args.summary_output]:
        path.parent.mkdir(parents=True, exist_ok=True)
    shortlist.to_csv(args.shortlist_output, index=False)
    screening.to_csv(args.screening_output, index=False)
    args.summary_output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
