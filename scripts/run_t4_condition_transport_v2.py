#!/usr/bin/env python
"""Run v2 leave-one-condition-out component transport on Marson CD4 perturbations."""

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

from isci.decomposition import (  # noqa: E402
    benjamini_hochberg,
    block_bootstrap_transport_delta,
    condition_transport_delta,
    leave_one_condition_out_predictions,
    match_unique_blocks,
    permute_positive_within_blocks,
)

SEED = 20260712
CONDITIONS = ["Rest", "Stim8hr", "Stim48hr"]
FEATURES = ROOT / "outputs/decomposition_v2/marson_condition_features.parquet"
AXES = ROOT / "config/axes.yaml"
OUTPUT_DIR = ROOT / "outputs/decomposition_v2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verdict(
    *, gain: float, coefficient: float, ci_low: float, q_value: float, condition_gains: dict[str, float]
) -> str:
    if gain <= 0 or coefficient <= 0:
        return "UNSUPPORTED"
    if any(value <= 0 for value in condition_gains.values()):
        return "CONTEXT_DEPENDENT"
    if ci_low > 0 and q_value < 0.05:
        return "SUPPORTED_EXPLORATORY"
    return "DIRECTIONAL_UNCERTAIN"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-resamples", type=int, default=1_000)
    args = parser.parse_args()
    if args.n_resamples < 1:
        raise SystemExit("--n-resamples must be positive")

    frame = pd.read_parquet(FEATURES)
    gene_table = frame.groupby("gene", observed=True).agg(
        target_baseMean=("target_baseMean", "mean"),
        n_cells_target=("n_cells_target", "mean"),
        known_regulator=("known_regulator", "first"),
    )
    positives = gene_table.index[gene_table["known_regulator"].astype(bool)].tolist()
    candidates = gene_table.index[~gene_table["known_regulator"].astype(bool)].tolist()
    blocks = match_unique_blocks(
        gene_table,
        positives,
        candidates,
        match_cols=["target_baseMean", "n_cells_target"],
        n_negatives=8,
    )
    block_genes = [gene for block in blocks for gene in block.genes]
    components = {
        column.removeprefix("precision__"): column
        for column in frame.columns
        if column.startswith("precision__")
    }
    components["repeatability"] = "repeatability"

    result_rows: list[dict[str, object]] = []
    prediction_tables: list[pd.DataFrame] = []
    for component_index, (component, column) in enumerate(components.items()):
        analysis = frame[["gene", "condition", "effect_reach", column]].copy()
        coverage = float(
            analysis[analysis["gene"].isin(block_genes)][column].notna().mean()
        )
        print(f"[T4 v2] {component} coverage={coverage:.1%}", flush=True)
        if coverage < 0.80:
            result_rows.append(
                {
                    "component": component,
                    "coverage": coverage,
                    "mean_delta_auprc": np.nan,
                    "ci_low": np.nan,
                    "ci_high": np.nan,
                    "mean_coefficient": np.nan,
                    "p_perm": 1.0,
                    "q_perm_bh": np.nan,
                    "condition_gains": "{}",
                    "condition_coefficients": "{}",
                    "verdict": "NOT_EVALUABLE",
                    "reason": "component coverage below 80% in fixed evaluation blocks",
                }
            )
            continue
        observed = leave_one_condition_out_predictions(
            analysis,
            blocks,
            conditions=CONDITIONS,
            effect_col="effect_reach",
            component_col=column,
            seed=SEED,
        )
        gain, condition_gains = condition_transport_delta(observed)
        bootstrap = block_bootstrap_transport_delta(
            observed, n_resamples=args.n_resamples, seed=SEED
        )
        null = np.empty(args.n_resamples, dtype=float)
        for iteration in range(args.n_resamples):
            permuted = permute_positive_within_blocks(
                blocks, seed=SEED + (component_index + 1) * 100_000 + iteration
            )
            prediction = leave_one_condition_out_predictions(
                analysis,
                permuted,
                conditions=CONDITIONS,
                effect_col="effect_reach",
                component_col=column,
                seed=SEED,
            )
            null[iteration] = condition_transport_delta(prediction)[0]
        ci_low, ci_high = np.quantile(bootstrap, [0.025, 0.975])
        p_perm = float((1 + np.sum(null >= gain)) / (args.n_resamples + 1))
        coefficients = observed.attrs["condition_component_coefficients"]
        result_rows.append(
            {
                "component": component,
                "coverage": coverage,
                "mean_delta_auprc": gain,
                "ci_low": float(ci_low),
                "ci_high": float(ci_high),
                "mean_coefficient": float(observed.attrs["mean_component_coefficient"]),
                "p_perm": p_perm,
                "q_perm_bh": np.nan,
                "condition_gains": json.dumps(condition_gains, sort_keys=True),
                "condition_coefficients": json.dumps(coefficients, sort_keys=True),
                "verdict": "PENDING_MULTIPLICITY",
                "reason": "",
            }
        )
        observed.insert(0, "component", component)
        prediction_tables.append(observed)

    q_values = benjamini_hochberg([float(row["p_perm"]) for row in result_rows])
    for row, q_value in zip(result_rows, q_values, strict=True):
        row["q_perm_bh"] = float(q_value)
        if row["verdict"] == "NOT_EVALUABLE":
            continue
        row["verdict"] = verdict(
            gain=float(row["mean_delta_auprc"]),
            coefficient=float(row["mean_coefficient"]),
            ci_low=float(row["ci_low"]),
            q_value=float(q_value),
            condition_gains=json.loads(str(row["condition_gains"])),
        )

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    timestamp = datetime.now().astimezone().isoformat()
    command = f"python scripts/run_t4_condition_transport_v2.py --n-resamples {args.n_resamples}"
    provenance = {
        "git_sha": git_sha,
        "data_sha256": sha256(FEATURES),
        "axes_sha256": sha256(AXES),
        "timestamp": timestamp,
        "command": command,
        "seed": SEED,
        "n_resamples": args.n_resamples,
        "method_version": "controllability_profile_v2",
        "n_positive_blocks": len(blocks),
        "n_negatives_per_block": 8,
    }
    results = pd.DataFrame(result_rows)
    for key, value in provenance.items():
        results[key] = value
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_DIR / "t4_condition_transport_v2.csv", index=False)
    predictions = pd.concat(prediction_tables, ignore_index=True)
    for key, value in provenance.items():
        predictions[key] = value
    predictions.to_parquet(OUTPUT_DIR / "t4_condition_transport_v2_predictions.parquet", index=False)
    payload = {
        "test": "T4 v2 leave-one-condition-out transport",
        "status": "EXPLORATORY_EVOLUTIONARY",
        "results": result_rows,
        "provenance": provenance,
        "interpretation_boundary": (
            "Within-screen context transport using the same genes across conditions; "
            "not independent biological replication."
        ),
    }
    (OUTPUT_DIR / "t4_condition_transport_v2.json").write_text(json.dumps(payload, indent=2))
    print(
        results[
            ["component", "mean_delta_auprc", "ci_low", "ci_high", "p_perm", "q_perm_bh", "verdict"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
