#!/usr/bin/env python
"""Estimate partial donor-gate power from a real pilot contrast table."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.power_planning import simulate_partial_donor_gate_power  # noqa: E402

DEFAULT_OUTPUT = ROOT / "outputs/decomposition_v2/donor_context_power_plan.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def comma_values(raw: str, cast: type[int] | type[float]) -> list[int] | list[float]:
    return [cast(value.strip()) for value in raw.split(",") if value.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--donor-counts", default="6,8,10,12,16")
    parser.add_argument("--effect-scales", default="0.5,0.75,1.0")
    parser.add_argument("--n-trials", type=int, default=2_000)
    parser.add_argument("--n-bootstrap", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260712)
    args = parser.parse_args()

    with args.input.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or set(rows[0]) != {"donor", "contrast"}:
        raise SystemExit("input must contain exactly donor,contrast columns")
    donors = [row["donor"] for row in rows]
    if len(donors) != len(set(donors)):
        raise SystemExit("pilot donor identifiers must be unique")
    contrasts = np.asarray([float(row["contrast"]) for row in rows], dtype=float)
    donor_counts = comma_values(args.donor_counts, int)
    effect_scales = comma_values(args.effect_scales, float)
    results = simulate_partial_donor_gate_power(
        contrasts,
        donor_counts=donor_counts,
        effect_scales=effect_scales,
        n_trials=args.n_trials,
        n_bootstrap=args.n_bootstrap,
        seed=args.seed,
    )
    git_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    payload = {
        "status": "PLANNING_ONLY_PARTIAL_GATE",
        "pilot": {
            "n_donors": len(contrasts),
            "mean_contrast": float(np.mean(contrasts)),
            "sd_contrast": float(np.std(contrasts, ddof=1)),
        },
        "scenarios": results,
        "gate_coverage": {
            "included": [
                "donor-bootstrap interval above zero",
                "at least 70 percent donor contrasts positive",
                "positive leave-one-donor-out mean for every donor",
            ],
            "missing": [
                "gene-label permutation",
                "within-gene-donor context-exchange permutation",
            ],
        },
        "boundary": (
            "Planning sensitivity based on empirical pilot residuals; not confirmatory power, "
            "not a result, and not valid with fewer than four pilot donors."
        ),
        "provenance": {
            "git_sha": git_sha,
            "input_sha256": sha256(args.input),
            "timestamp": datetime.now().astimezone().isoformat(),
            "command": " ".join(sys.argv),
            "seed": args.seed,
            "method_version": "donor_partial_gate_power_v1",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
