#!/usr/bin/env python
"""Build the outcome-blind prospective donor-panel manifest and resource plan."""

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

from isci.prospective_panel import plan_panel_resources, select_prospective_panel  # noqa: E402

DEFAULT_LABELS = ROOT / "outputs/generalization/near_immune_scores.csv"
DEFAULT_GUIDES = ROOT / "data/external/gse190604/guidecalls.txt.gz"
DEFAULT_AXES = ROOT / "config/axes.yaml"
DEFAULT_MANIFEST = ROOT / "outputs/decomposition_v2/prospective_donor_panel.csv"
DEFAULT_SUMMARY = ROOT / "outputs/decomposition_v2/prospective_donor_panel.json"


def sha256(path: Path) -> str:
    """Hash an input in chunks so even a large guide-call table stays memory-safe."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_targets(panel: pd.DataFrame, role: str) -> list[str]:
    """Preserve the deterministic selection order while collapsing guide rows."""

    return panel.loc[panel["role"] == role, "target"].drop_duplicates().tolist()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--guidecalls", type=Path, default=DEFAULT_GUIDES)
    parser.add_argument("--axes", type=Path, default=DEFAULT_AXES)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--positive-count", type=int, default=8)
    parser.add_argument("--non-target-count", type=int, default=4)
    parser.add_argument("--donor-counts", default="8,10,12")
    parser.add_argument("--usable-cells-per-guide", type=int, default=50)
    parser.add_argument("--usable-fraction", type=float, default=0.60)
    parser.add_argument("--recovered-cells-per-channel", type=int, default=20_000)
    args = parser.parse_args()

    required = [args.labels, args.guidecalls, args.axes]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"missing panel inputs: {missing}")
    donor_counts = tuple(
        int(value.strip()) for value in args.donor_counts.split(",") if value.strip()
    )

    # Only frozen labels and raw assignment coverage enter selection. In particular, the script
    # never opens the GSE feature, replication, or context-interaction result artifacts.
    labels = pd.read_csv(args.labels)
    guidecalls = pd.read_csv(args.guidecalls, sep="\t")
    panel = select_prospective_panel(
        labels,
        guidecalls,
        positive_count=args.positive_count,
        non_target_count=args.non_target_count,
    )
    scenarios = plan_panel_resources(
        int(panel["guide_id"].nunique()),
        donor_counts=donor_counts,
        usable_cells_per_guide=args.usable_cells_per_guide,
        usable_fraction=args.usable_fraction,
        recovered_cells_per_channel=args.recovered_cells_per_channel,
    )

    git_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    timestamp = datetime.now().astimezone().isoformat()
    command = shlex.join(["python", *sys.argv])
    input_hashes = {
        str(args.labels.resolve().relative_to(ROOT)): sha256(args.labels),
        str(args.guidecalls.resolve().relative_to(ROOT)): sha256(args.guidecalls),
    }
    provenance = {
        "git_sha": git_sha,
        "data_sha256": json.dumps(input_hashes, sort_keys=True),
        "axes_sha256": sha256(args.axes),
        "timestamp": timestamp,
        "command": command,
        "method_version": "prospective_donor_panel_v1",
    }
    for key, value in provenance.items():
        panel[key] = value

    role_counts = (
        panel.groupby("role", sort=False)
        .agg(targets=("target", "nunique"), guides=("guide_id", "nunique"))
        .astype(int)
        .to_dict(orient="index")
    )
    payload = {
        "status": "DESIGN_READY_SEQUENCE_VALIDATION_REQUIRED",
        "selection": {
            "primary_positives": unique_targets(panel, "PRIMARY_POSITIVE"),
            "matched_negatives": unique_targets(panel, "MATCHED_NEGATIVE"),
            "mechanistic_sentinels": unique_targets(panel, "MECHANISTIC_SENTINEL"),
            "non_target_controls": panel.loc[
                panel["role"] == "NON_TARGET_CONTROL", "guide_id"
            ].tolist(),
            "role_counts": role_counts,
            "n_target_genes": int(panel.loc[panel["target"] != "NO-TARGET", "target"].nunique()),
            "n_guide_constructs": int(panel["guide_id"].nunique()),
        },
        "selection_boundary": {
            "used": [
                "frozen is_positive and is_matched_negative labels",
                "singleton guide-assignment coverage by public guide ID and context",
            ],
            "not_used": [
                "effect reach",
                "signed axis projections or precision",
                "repeatability",
                "GSE190604 replication or context-interaction outcomes",
            ],
            "sentinels_counted_in_primary_metric": False,
        },
        "resource_assumptions": {
            "paired_contexts_per_donor": 2,
            "usable_cells_per_guide_donor_context": args.usable_cells_per_guide,
            "usable_fraction": args.usable_fraction,
            "recovered_cells_per_channel": args.recovered_cells_per_channel,
            "channel_capacity_boundary": "configurable planning unit, not a vendor guarantee",
        },
        "resource_scenarios": scenarios,
        "ordering_gate": {
            "status": "BLOCKED_PENDING_GUIDE_SEQUENCE_VALIDATION",
            "reason": (
                "the public local artifact contains guide IDs and assignments but no validated "
                "protospacer sequences"
            ),
            "required_before_order": [
                "map each guide ID to an authoritative sequence source",
                "confirm CRISPR modality and vector compatibility",
                "score on-target activity and sequence-specific off-target risk",
                "approve substitutions and regenerate this manifest with an audit trail",
            ],
        },
        "analysis_boundary": (
            "Design and costing artifact only. Donor is the biological replicate; guides, wells, "
            "channels, and libraries do not increase the donor count."
        ),
        "provenance": provenance,
    }

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(args.manifest, index=False)
    args.summary.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
