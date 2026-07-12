#!/usr/bin/env python
"""Execute frozen T2 component-support transport tests from committed artifacts only."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.decomposition import (  # noqa: E402
    benjamini_hochberg,
    block_bootstrap_delta,
    blocked_oof_predictions,
    component_verdict,
    delta_auprc,
    match_unique_blocks,
    permute_positive_within_blocks,
)

SEED = 20260712


@dataclass
class Dataset:
    dataset: str
    system: str
    frame: pd.DataFrame | None
    positives: list[str]
    candidates: list[str]
    effect_col: str
    components: dict[str, str]
    match_cols: list[str]
    inputs: list[Path]
    replicate_count: int | None
    blocker: str | None = None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_datasets() -> list[Dataset]:
    rank_path = ROOT / "results/final/isci_final_ranking.csv"
    match_path = ROOT / "outputs/marson_obs_matching.parquet"
    marson = pd.read_csv(rank_path).set_index("gene")
    matching = pd.read_parquet(match_path).groupby("gene", observed=True)[
        ["target_baseMean", "n_cells_target"]
    ].mean()
    marson = marson.join(matching)
    marson = marson[marson["detectable_effect"].astype(bool)].copy()
    marson_pos = marson.index[marson["known_regulator"].astype(bool)].tolist()
    marson_candidates = marson.index[~marson["known_regulator"].astype(bool)].tolist()

    schmidt_path = ROOT / "outputs/generalization/near_immune_scores.csv"
    schmidt = pd.read_csv(schmidt_path).set_index("gene")
    schmidt_pos = schmidt.index[schmidt["is_positive"].astype(bool)].tolist()
    schmidt_neg = schmidt.index[schmidt["is_matched_negative"].astype(bool)].tolist()

    norman_path = ROOT / "outputs/generalization/third_system_norman_scores.csv"
    norman = pd.read_csv(norman_path).set_index("gene")
    norman_pos = norman.index[norman["is_positive"].astype(bool)].tolist()
    norman_neg = norman.index[norman["is_negative"].astype(bool)].tolist()

    thp_path = ROOT / "outputs/generalization/b1_myeloid_gse221321/b1_myeloid_features.csv"
    thp_result_path = ROOT / "outputs/generalization/b1_myeloid_gse221321/cci_result.json"
    thp = pd.read_csv(thp_path).set_index("gene")
    thp = thp[thp["detectable"].astype(bool)].copy()
    thp_result = json.loads(thp_result_path.read_text())

    rpe_path = ROOT / "outputs/generalization/far_nonimmune_cci_scores.csv"
    return [
        Dataset(
            "marson_cd4",
            "CD4 T cell CRISPRi",
            marson,
            marson_pos,
            marson_candidates,
            "magnitude",
            {"precision": "specificity", "repeatability": "coh_donor"},
            ["target_baseMean", "n_cells_target"],
            [rank_path, match_path],
            3,
        ),
        Dataset(
            "schmidt_cd4_crispra",
            "CD4 T cell CRISPRa",
            schmidt,
            schmidt_pos,
            schmidt_neg,
            "magnitude",
            {"precision": "specificity", "repeatability": "reproducibility"},
            ["magnitude", "base_expr", "n_cells"],
            [schmidt_path],
            4,
        ),
        Dataset(
            "thp1_myeloid",
            "THP-1 myeloid CRISPRi",
            thp,
            list(thp_result["positives"]),
            list(thp_result["negatives"]),
            "magnitude",
            {"precision": "S", "repeatability": "R"},
            ["target_baseMean", "n_cells_target"],
            [thp_path, thp_result_path],
            len(thp_result.get("provenance", {}).get("reps", [])),
        ),
        Dataset(
            "norman_k562",
            "K562 CRISPRa",
            norman,
            norman_pos,
            norman_neg,
            "magnitude",
            {"precision": "S_axis", "repeatability": "R"},
            ["magnitude", "base_expr", "ncells"],
            [norman_path],
            2,
        ),
        Dataset(
            "replogle_rpe1",
            "RPE1 CRISPRi",
            None,
            [],
            [],
            "magnitude",
            {"precision": "S", "repeatability": "R"},
            [],
            [rpe_path],
            None,
            "committed artifact contains summary rows only, not gene-level E/S/R and labels",
        ),
    ]


def not_evaluable_rows(dataset: Dataset, reason: str) -> list[dict[str, object]]:
    return [
        {
            "dataset": dataset.dataset,
            "system": dataset.system,
            "component": component,
            "n_positives": len(dataset.positives),
            "n_negatives": len(dataset.candidates),
            "coverage": np.nan,
            "delta_auprc_oof": np.nan,
            "ci_low": np.nan,
            "ci_high": np.nan,
            "coefficient": np.nan,
            "p_perm": 1.0,
            "q_perm_bh": np.nan,
            "verdict": "NOT_EVALUABLE",
            "reason": reason,
        }
        for component in dataset.components
    ]


def evaluate_dataset(dataset: Dataset, n_resamples: int) -> list[dict[str, object]]:
    if dataset.blocker or dataset.frame is None:
        return not_evaluable_rows(dataset, dataset.blocker or "gene-level artifact absent")
    frame = dataset.frame
    if len(dataset.positives) < 8:
        return not_evaluable_rows(dataset, "fewer than eight positive genes")
    if len(dataset.candidates) < len(dataset.positives) * 5:
        return not_evaluable_rows(
            dataset,
            f"only {len(dataset.candidates)} unique candidates for {len(dataset.positives)} "
            "positives; fewer than five negatives per block",
        )
    if dataset.replicate_count is None or dataset.replicate_count < 2:
        return not_evaluable_rows(dataset, "fewer than two documented independent replicates")
    try:
        blocks = match_unique_blocks(
            frame,
            dataset.positives,
            dataset.candidates,
            match_cols=dataset.match_cols,
            n_negatives=5,
        )
    except ValueError as error:
        return not_evaluable_rows(dataset, str(error))

    rows: list[dict[str, object]] = []
    block_genes = [gene for block in blocks for gene in block.genes]
    for component_index, (component, component_col) in enumerate(dataset.components.items()):
        coverage = float(frame.loc[block_genes, component_col].notna().mean())
        if coverage < 0.8:
            rows.extend(not_evaluable_rows(dataset, f"{component} coverage {coverage:.1%} below 80%")[:1])
            rows[-1]["component"] = component
            rows[-1]["coverage"] = coverage
            continue
        analysis = frame.copy()
        observed = blocked_oof_predictions(
            analysis,
            blocks,
            effect_col=dataset.effect_col,
            component_col=component_col,
            seed=SEED,
        )
        gain = delta_auprc(observed)
        bootstrap = block_bootstrap_delta(observed, n_resamples=n_resamples, seed=SEED)
        null = np.empty(n_resamples, dtype=float)
        for iteration in range(n_resamples):
            permuted = permute_positive_within_blocks(
                blocks, seed=SEED + 10_000 * (component_index + 1) + iteration
            )
            prediction = blocked_oof_predictions(
                analysis,
                permuted,
                effect_col=dataset.effect_col,
                component_col=component_col,
                seed=SEED,
            )
            null[iteration] = delta_auprc(prediction)
        coefficient = float(observed.attrs["mean_component_coefficient"])
        ci_low, ci_high = np.quantile(bootstrap, [0.025, 0.975])
        p_perm = float((1 + np.sum(null >= gain)) / (n_resamples + 1))
        rows.append(
            {
                "dataset": dataset.dataset,
                "system": dataset.system,
                "component": component,
                "n_positives": len(blocks),
                "n_negatives": sum(len(block.negatives) for block in blocks),
                "coverage": coverage,
                "delta_auprc_oof": gain,
                "ci_low": float(ci_low),
                "ci_high": float(ci_high),
                "coefficient": coefficient,
                "p_perm": p_perm,
                "q_perm_bh": np.nan,
                "verdict": "PENDING_MULTIPLICITY",
                "reason": "",
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-resamples", type=int, default=1_000)
    args = parser.parse_args()
    if args.n_resamples < 1:
        raise SystemExit("--n-resamples must be positive")

    datasets = load_datasets()
    rows = []
    for dataset in datasets:
        print(f"[T2] {dataset.dataset}", flush=True)
        rows.extend(evaluate_dataset(dataset, args.n_resamples))
    q_values = benjamini_hochberg([float(row["p_perm"]) for row in rows])
    for row, q_value in zip(rows, q_values, strict=True):
        row["q_perm_bh"] = float(q_value)
        if row["verdict"] != "NOT_EVALUABLE":
            row["verdict"] = component_verdict(
                gain=float(row["delta_auprc_oof"]),
                coefficient=float(row["coefficient"]),
                ci_low=float(row["ci_low"]),
                q_value=float(q_value),
            )

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    timestamp = datetime.now().astimezone().isoformat()
    command = f"python scripts/run_t2_decomposition.py --n-resamples {args.n_resamples}"
    input_hashes = {
        str(path.relative_to(ROOT)): sha256(path)
        for dataset in datasets
        for path in dataset.inputs
        if path.exists()
    }
    axes_path = ROOT / "config/axes.yaml"
    for row in rows:
        row.update(
            {
                "git_sha": git_sha,
                "data_sha256": json.dumps(input_hashes, sort_keys=True),
                "axes_sha256": sha256(axes_path),
                "timestamp": timestamp,
                "command": command,
                "post_hoc_stress_test": True,
                "seed": SEED,
                "n_resamples": args.n_resamples,
            }
        )

    output_dir = ROOT / "outputs/decomposition"
    output_dir.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame(rows)
    table.to_csv(output_dir / "t2_component_support.csv", index=False)
    payload = {
        "test": "T2 component-support transport map",
        "status": "POST_HOC_STRESS_TEST",
        "results": rows,
        "provenance": {
            "git_sha": git_sha,
            "data_sha256": input_hashes,
            "axes_sha256": sha256(axes_path),
            "timestamp": timestamp,
            "command": command,
            "seed": SEED,
            "n_resamples": args.n_resamples,
        },
    }
    (output_dir / "t2_component_support.json").write_text(json.dumps(payload, indent=2))
    print(table[["dataset", "component", "delta_auprc_oof", "q_perm_bh", "verdict", "reason"]].to_string(index=False))


if __name__ == "__main__":
    main()
