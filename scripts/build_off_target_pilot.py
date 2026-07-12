#!/usr/bin/env python
"""Build the version-pinned CRISPRitz pilot inputs without running the search engine."""

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
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.guide_sequence_validation import build_off_target_pilot_manifest  # noqa: E402

DEFAULT_CONFIG = ROOT / "config/off_target_pilot.yaml"
DEFAULT_SCREENING = ROOT / "outputs/decomposition_v2/off_target_screening_input.csv"
DEFAULT_SHORTLIST = ROOT / "outputs/decomposition_v2/guide_replacement_shortlist.csv"
DEFAULT_AXES = ROOT / "config/axes.yaml"
DEFAULT_MANIFEST = ROOT / "outputs/decomposition_v2/off_target_pilot_manifest.csv"
DEFAULT_GUIDES = ROOT / "outputs/decomposition_v2/off_target_pilot_guides.txt"
DEFAULT_CONTROL = ROOT / "outputs/decomposition_v2/off_target_pilot_control_emx1.txt"
DEFAULT_PAM = ROOT / "outputs/decomposition_v2/off_target_pilot_spcas9_ngg.txt"
DEFAULT_CONTRACT = ROOT / "outputs/decomposition_v2/off_target_pilot_contract.json"


def sha256(path: Path) -> str:
    """Hash a pilot input in bounded chunks for the audit record."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--screening", type=Path, default=DEFAULT_SCREENING)
    parser.add_argument("--shortlist", type=Path, default=DEFAULT_SHORTLIST)
    parser.add_argument("--axes", type=Path, default=DEFAULT_AXES)
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--guides-output", type=Path, default=DEFAULT_GUIDES)
    parser.add_argument("--control-output", type=Path, default=DEFAULT_CONTROL)
    parser.add_argument("--pam-output", type=Path, default=DEFAULT_PAM)
    parser.add_argument("--contract-output", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()

    required = [args.config, args.screening, args.shortlist, args.axes]
    if missing := [str(path) for path in required if not path.exists()]:
        raise SystemExit(f"missing pilot inputs: {missing}")

    config = yaml.safe_load(args.config.read_text())
    if config.get("status") != "FROZEN_NOT_EXECUTED":
        raise SystemExit("pilot config must be FROZEN_NOT_EXECUTED")
    if config["engine"]["version"] != "2.7.0":
        raise SystemExit("unexpected CRISPRitz version")

    screening = pd.read_csv(args.screening)
    shortlist = pd.read_csv(args.shortlist)
    manifest = build_off_target_pilot_manifest(screening, shortlist)
    stage = next(
        stage
        for stage in config["pilot_stages"]
        if stage["id"] == "S1_PRIORITY_REFERENCE_SEARCH"
    )
    manifest["search_engine"] = f"{config['engine']['name']}_{config['engine']['version']}"
    manifest["search_mode"] = stage["search_mode"]
    manifest["mismatch_ceiling"] = stage["mismatch_ceiling"]
    manifest["dna_bulge_ceiling"] = stage["dna_bulge_ceiling"]
    manifest["rna_bulge_ceiling"] = stage["rna_bulge_ceiling"]

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
        "method_version": config["contract_version"],
    }
    for key, value in provenance.items():
        manifest[key] = value

    outputs = [
        args.manifest_output,
        args.guides_output,
        args.control_output,
        args.pam_output,
        args.contract_output,
    ]
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(args.manifest_output, index=False)
    args.guides_output.write_text("\n".join(manifest["crispritz_guide"]) + "\n")
    args.control_output.write_text(
        config["official_installation_control"]["guide_with_pam_placeholder"] + "\n"
    )
    args.pam_output.write_text(config["crispr_contract"]["pam_file_line"] + "\n")

    payload = {
        "status": "PILOT_INPUTS_READY_EXECUTION_NOT_RUN",
        "execution_status": "NOT_EXECUTED",
        "engine": config["engine"],
        "scientific_reference": config["scientific_reference"],
        "pilot_stage": stage,
        "n_project_candidates": len(manifest),
        "targets": sorted(manifest["target"].unique()),
        "candidate_kinds": manifest["candidate_kind"].value_counts().to_dict(),
        "official_installation_control": config["official_installation_control"],
        "acceptance": config["acceptance"],
        "promotion_boundary": config["promotion_boundary"],
        "input_sha256": input_hashes,
        "output_sha256": {
            str(path.resolve().relative_to(ROOT)): sha256(path)
            for path in outputs[:-1]
        },
        "provenance": provenance,
    }
    args.contract_output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
