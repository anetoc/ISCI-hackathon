#!/usr/bin/env python
"""Build the source-backed donor-resolved dataset acquisition inventory."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.dataset_gates import evaluate_dataset_candidate  # noqa: E402

CONFIG = ROOT / "config/donor_dataset_candidates.yaml"
OUTPUT = ROOT / "outputs/decomposition_v2/donor_dataset_inventory.json"


def main() -> None:
    config = yaml.safe_load(CONFIG.read_text())
    candidates = []
    for candidate in config["candidates"]:
        evaluated = {**candidate, **evaluate_dataset_candidate(candidate)}
        candidates.append(evaluated)
    git_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    counts: dict[str, int] = {}
    for candidate in candidates:
        decision = candidate["decision"]
        counts[decision] = counts.get(decision, 0) + 1
    payload = {
        "criteria_version": config["criteria_version"],
        "searched_at": str(config["searched_at"]),
        "result": "NO_PUBLIC_GO_IDENTIFIED",
        "decision_counts": counts,
        "candidates": candidates,
        "provenance": {
            "git_sha": git_sha,
            "timestamp": datetime.now().astimezone().isoformat(),
            "command": "python scripts/build_donor_dataset_inventory.py",
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
