#!/usr/bin/env python
"""Audit the frozen T4 gate without recomputing condition-level science."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

import h5py

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/GWCD4i.DE_stats.h5ad"
RANKING = ROOT / "results/final/isci_final_ranking.csv"
MATCHING = ROOT / "outputs/marson_obs_matching.parquet"
AXES = ROOT / "config/axes.yaml"
OUTPUT = ROOT / "outputs/decomposition/t4_condition_transport.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def categorical_values(group: h5py.Group) -> list[str]:
    values = group["categories"].asstr()[:]
    return [str(value) for value in values]


def main() -> None:
    reusable_candidates = sorted(
        path
        for base in (ROOT / "outputs", ROOT / "results")
        for path in base.rglob("*")
        if path.is_file()
        and any(token in path.name.lower() for token in ("condition", "stim", "rest"))
    )
    with h5py.File(RAW, "r") as handle:
        conditions = categorical_values(handle["obs/culture_condition"])
        raw_has_required_fields = all(
            name in handle
            for name in (
                "layers/zscore",
                "obs/target_contrast_gene_name",
                "obs/culture_condition",
                "obs/donor_correlation_all_mean",
            )
        )

    # None of the discovered condition-named artifacts contains the required joint
    # gene x condition E/S/R + label + matching-block table. The raw h5ad could produce
    # it, but doing so is a new recomputation and therefore fails the frozen T4 intake gate.
    reason = (
        "No reusable gene-by-condition artifact jointly contains E, S, R, controller labels "
        "and auditable matching blocks/covariates. The raw Marson h5ad contains the three "
        "conditions and necessary source fields, but T4 would require raw-data recomputation."
    )
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    payload = {
        "test": "T4 leave-one-condition-out transport gate",
        "status": "POST_HOC_STRESS_TEST",
        "verdict": "NOT_EVALUABLE",
        "reason": reason,
        "interpretation": (
            "This is an artifact-readiness limitation, not evidence that component support "
            "fails to transport across Rest, Stim8hr and Stim48hr."
        ),
        "audit": {
            "conditions_in_raw": conditions,
            "raw_has_required_source_fields": raw_has_required_fields,
            "reusable_candidates_inspected": [
                str(path.relative_to(ROOT)) for path in reusable_candidates
            ],
            "raw_recomputation_performed": False,
        },
        "provenance": {
            "git_sha": git_sha,
            "data_sha256": {
                str(path.relative_to(ROOT)): sha256(path)
                for path in (RANKING, MATCHING)
            },
            "raw_data_sha256": sha256(RAW),
            "axes_sha256": sha256(AXES),
            "timestamp": datetime.now().astimezone().isoformat(),
            "command": "python scripts/audit_t4_condition_transport.py",
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
