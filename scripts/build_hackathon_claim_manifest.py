#!/usr/bin/env python3
"""Build the stage-demo claim manifest from frozen public-data evidence.

The script does not recompute scientific results. It validates the already
adjudicated artifacts, applies the presentation verdict contract, and records
the provenance needed to audit every claim shown to the hackathon jury.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:  # Package import in tests; direct import when run as `python scripts/...`.
    from .release_provenance import source_paths_dirty, source_snapshot
except ImportError:  # pragma: no cover - exercised by the release CLI.
    from release_provenance import source_paths_dirty, source_snapshot


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "hackathon_claims.yaml"
DEFAULT_OUTPUT = ROOT / "outputs" / "hackathon" / "claim_manifest.json"
AXES_PATH = ROOT / "config" / "axes.yaml"
PROVENANCE_HELPER = ROOT / "scripts" / "release_provenance.py"


def sha256(path: Path) -> str:
    """Return a stable content hash without exposing the underlying data."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_sha() -> str:
    """Capture the exact repository state used to assemble the manifest."""

    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def selected_payload(claim: dict[str, Any]) -> dict[str, Any]:
    """Load the evidence object and optionally select one named result block."""

    evidence_path = ROOT / claim["evidence_path"]
    payload = json.loads(evidence_path.read_text())
    selector = claim.get("json_selector")
    if selector:
        payload = payload[selector]
    return payload


def adjudicate(claim: dict[str, Any], payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Apply frozen, explicit verdict semantics to one evidence payload."""

    claim_id = claim["claim_id"]
    if claim_id == "C1-CONTROLLABILITY":
        oof_gain = float(payload["oof_gain"])
        ci_low, ci_high = map(float, payload["hierarchical_bootstrap"]["ci95"])
        permutation_p = float(payload["within_block_permutation"]["perm_p"])
        verdict = "PASS" if oof_gain > 0 and ci_low > 0 and permutation_p < 0.05 else "FAIL"
        metrics = {
            "authoritative_full_sample": claim["presentation"],
            "leakage_free_oof": {
                "gain": oof_gain,
                "ci95": [ci_low, ci_high],
                "permutation_p": permutation_p,
                "n_positive": int(payload["n_pos"]),
                "n_negative_per_positive": int(payload["n_neg_per_positive"]),
            },
        }
    elif claim_id == "C2-EXTERNAL-FUNCTIONAL":
        gain = float(payload["gain"])
        ci_low, ci_high = map(float, payload["ci"])
        verdict = "FAIL" if ci_high < 0 else "NULL"
        metrics = {
            "gain": gain,
            "ci95": [ci_low, ci_high],
            "n_positive": int(payload["n_pos"]),
            "n_negative": int(payload["n_neg"]),
        }
    elif claim_id == "C3-CART-CLINICAL":
        primary = payload["primary"]
        permutation_p = float(primary["perm_p"])
        best_baseline = float(payload["best_baseline_lso"])
        verdict = "NULL" if permutation_p >= 0.05 and float(primary["auroc"]) <= best_baseline else "PASS"
        metrics = {
            "study_out_auroc": float(primary["auroc"]),
            "ci95": [float(value) for value in primary["ci"]],
            "permutation_p": permutation_p,
            "best_baseline_auroc": best_baseline,
        }
    elif claim_id == "C4-SCGPT":
        metrics_payload = payload["metrics"]
        missing_metrics = all(value is None for value in metrics_payload.values())
        verdict = "NOT-EVALUABLE" if missing_metrics else "PASS"
        metrics = {
            "primary_gate": payload["why_not_evaluable"]["primary_gate"],
            "all_metrics_missing": missing_metrics,
        }
    else:  # Defensive: a new stage claim must add an explicit gate here.
        raise ValueError(f"No adjudication rule for {claim_id}")

    expected = claim["expected_verdict"]
    if verdict != expected:
        raise ValueError(f"{claim_id}: expected {expected}, computed {verdict}")
    return verdict, metrics


def build(config_path: Path, output_path: Path) -> dict[str, Any]:
    """Validate all claims and write a deterministic, auditable demo bundle."""

    config = yaml.safe_load(config_path.read_text())
    command = "python scripts/build_hackathon_claim_manifest.py"
    claims = []
    evidence_paths = []
    for claim in config["claims"]:
        evidence_path = ROOT / claim["evidence_path"]
        evidence_paths.append(evidence_path)
        payload = selected_payload(claim)
        verdict, metrics = adjudicate(claim, payload)
        claims.append(
            {
                "claim_id": claim["claim_id"],
                "short_label": claim["short_label"],
                "claim": claim["claim"],
                "verdict": verdict,
                "metrics": metrics,
                "scope": claim["scope"],
                "prohibited_overclaim": claim["prohibited_overclaim"],
                "evidence_path": claim["evidence_path"],
                "data_sha256": sha256(evidence_path),
            }
        )

    source_paths = [Path(__file__), PROVENANCE_HELPER, config_path, AXES_PATH, *evidence_paths]
    manifest = {
        "schema_version": config["schema_version"],
        "title": config["title"],
        "thesis": config["thesis"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha(),
        "git_sha_semantics": "Base revision at generation time; source_snapshot binds exact working-tree inputs.",
        "source_paths_dirty": source_paths_dirty(source_paths, ROOT),
        "source_snapshot": source_snapshot(source_paths, ROOT),
        "axes_sha256": sha256(AXES_PATH),
        "config_sha256": sha256(config_path),
        "command": command,
        "verdict_contract": {
            "PASS": "Prespecified direction and required gates are met.",
            "FAIL": "The claim is evaluable but a directional or required gate is violated.",
            "NULL": "The claim is evaluable but no supported incremental signal is present.",
            "NOT-EVALUABLE": "A required input or structural gate is absent; no biological conclusion is forced.",
        },
        "claims": claims,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def main() -> None:
    """Parse paths explicitly so the same builder works locally and in CI."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = build(args.config, args.output)
    verdicts = ", ".join(f"{item['claim_id']}={item['verdict']}" for item in manifest["claims"])
    print(f"Wrote {args.output}: {verdicts}")


if __name__ == "__main__":
    main()
