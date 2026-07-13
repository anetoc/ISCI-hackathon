#!/usr/bin/env python
"""Run the frozen overlap-weighted GSE190604 targeted-panel replication tests."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.decomposition import benjamini_hochberg  # noqa: E402
from isci.panel_validation import (  # noqa: E402
    overlap_weighted_delta,
    repeated_overlap_oof,
    stratified_gene_bootstrap,
)

SEED = 20260712
FEATURES = ROOT / "outputs/decomposition_v2/gse190604_features.parquet"
AXES = ROOT / "config/axes.yaml"
OUTPUT_DIR = ROOT / "outputs/decomposition_v2"
TESTS = [
    ("stim_th2_precision", "stim", "precision__th2", "signed__th2", True),
    ("nostim_th2_precision", "nostim", "precision__th2", "signed__th2", False),
    ("stim_th1_precision", "stim", "precision__th1_effector", "signed__th1_effector", False),
    ("stim_repeatability", "stim", "repeatability", None, False),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-resamples", type=int, default=1_000)
    parser.add_argument("--n-repeats", type=int, default=10)
    args = parser.parse_args()
    if args.n_resamples < 1 or args.n_repeats < 1:
        raise SystemExit("resamples and repeats must be positive")
    features = pd.read_parquet(FEATURES)
    rows: list[dict[str, object]] = []
    predictions_out: list[pd.DataFrame] = []
    for test_index, (test_name, context, component, signed, primary) in enumerate(TESTS):
        frame = features[features["context"] == context].copy().set_index("gene")
        required = ["is_positive", "effect_reach", component, "target_base_expr", "n_cells_target"]
        frame = frame.dropna(subset=required)
        n_positive = int(frame["is_positive"].sum())
        n_negative = int(len(frame) - n_positive)
        print(f"[GSE190604] {test_name}: pos={n_positive} neg={n_negative}", flush=True)
        if n_positive < 8 or n_negative < 15:
            rows.append(
                {
                    "test": test_name,
                    "context": context,
                    "component": component,
                    "primary": primary,
                    "n_positive": n_positive,
                    "n_negative": n_negative,
                    "gain": np.nan,
                    "ci_low": np.nan,
                    "ci_high": np.nan,
                    "coefficient": np.nan,
                    "p_perm": 1.0,
                    "q_bh": np.nan,
                    "verdict": "NOT_EVALUABLE",
                    "reason": "label-count gate failed",
                }
            )
            continue
        frame["log_base_expr"] = np.log1p(frame["target_base_expr"].clip(lower=0))
        frame["log_cells"] = np.log1p(frame["n_cells_target"])
        predictions = repeated_overlap_oof(
            frame,
            label_col="is_positive",
            effect_col="effect_reach",
            component_col=component,
            overlap_cols=["log_base_expr", "log_cells"],
            n_splits=5,
            n_repeats=args.n_repeats,
            seed=SEED,
        )
        gain = overlap_weighted_delta(predictions)
        bootstrap = stratified_gene_bootstrap(
            predictions, n_resamples=args.n_resamples, seed=SEED + test_index
        )
        null = np.empty(args.n_resamples, dtype=float)
        labels = frame["is_positive"].to_numpy(dtype=int)
        for iteration in range(args.n_resamples):
            permuted = frame.copy()
            rng = np.random.default_rng(SEED + (test_index + 1) * 100_000 + iteration)
            permuted["is_positive"] = rng.permutation(labels)
            permuted_predictions = repeated_overlap_oof(
                permuted,
                label_col="is_positive",
                effect_col="effect_reach",
                component_col=component,
                overlap_cols=["log_base_expr", "log_cells"],
                n_splits=5,
                n_repeats=args.n_repeats,
                seed=SEED,
            )
            null[iteration] = overlap_weighted_delta(permuted_predictions)
            if (iteration + 1) % max(1, args.n_resamples // 10) == 0:
                print(
                    f"[GSE190604] {test_name}: permutations {iteration + 1}/{args.n_resamples}",
                    flush=True,
                )
        ci_low, ci_high = np.quantile(bootstrap, [0.025, 0.975])
        p_perm = float((1 + np.sum(null >= gain)) / (args.n_resamples + 1))
        signed_diagnostic = {}
        if signed is not None:
            signed_diagnostic = {
                "median_signed_positive": float(frame.loc[frame["is_positive"], signed].median()),
                "median_signed_negative": float(frame.loc[~frame["is_positive"], signed].median()),
            }
        rows.append(
            {
                "test": test_name,
                "context": context,
                "component": component,
                "primary": primary,
                "n_positive": n_positive,
                "n_negative": n_negative,
                "gain": gain,
                "ci_low": float(ci_low),
                "ci_high": float(ci_high),
                "coefficient": float(predictions.attrs["mean_component_coefficient"]),
                "p_perm": p_perm,
                "q_bh": np.nan,
                "verdict": "PENDING_MULTIPLICITY",
                "reason": "",
                "signed_diagnostic": json.dumps(signed_diagnostic, sort_keys=True),
            }
        )
        prediction_table = predictions.reset_index(names="gene")
        prediction_table.insert(0, "test", test_name)
        predictions_out.append(prediction_table)

    q_values = benjamini_hochberg([float(row["p_perm"]) for row in rows])
    for row, q_value in zip(rows, q_values, strict=True):
        row["q_bh"] = float(q_value)
        if row["verdict"] == "NOT_EVALUABLE":
            continue
        if float(row["gain"]) <= 0 or float(row["coefficient"]) <= 0:
            row["verdict"] = "UNSUPPORTED"
        elif float(row["ci_low"]) > 0 and float(row["p_perm"]) < 0.05 and q_value < 0.05:
            row["verdict"] = "REPLICATED_EXPLORATORY"
        else:
            row["verdict"] = "DIRECTIONAL_UNCERTAIN"

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    timestamp = datetime.now().astimezone().isoformat()
    command = (
        f"python scripts/run_gse190604_replication.py --n-resamples {args.n_resamples} "
        f"--n-repeats {args.n_repeats}"
    )
    provenance = {
        "git_sha": git_sha,
        "data_sha256": sha256(FEATURES),
        "axes_sha256": sha256(AXES),
        "timestamp": timestamp,
        "command": command,
        "seed": SEED,
        "method_version": "gse190604_overlap_oof_v1",
    }
    results = pd.DataFrame(rows)
    for key, value in provenance.items():
        results[key] = value
    results.to_csv(OUTPUT_DIR / "gse190604_replication.csv", index=False)
    if predictions_out:
        prediction_table = pd.concat(predictions_out, ignore_index=True)
        for key, value in provenance.items():
            prediction_table[key] = value
        prediction_table.to_parquet(OUTPUT_DIR / "gse190604_replication_predictions.parquet", index=False)
    payload = {
        "test": "GSE190604 targeted-panel replication",
        "status": "EXTERNAL_TARGETED_PANEL",
        "results": rows,
        "provenance": provenance,
        "boundary": "External to Marson but reanalysis of a previously inspected targeted panel.",
    }
    (OUTPUT_DIR / "gse190604_replication.json").write_text(json.dumps(payload, indent=2))
    print(results[["test", "gain", "ci_low", "ci_high", "p_perm", "q_bh", "verdict"]].to_string(index=False))


if __name__ == "__main__":
    main()
