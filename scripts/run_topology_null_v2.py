#!/usr/bin/env python
"""Run topology rarity and conditional controller-recovery nulls for small axes."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.axes import build_axis_vectors, load_axes_config  # noqa: E402
from isci.decomposition import (  # noqa: E402
    blocked_oof_predictions,
    delta_auprc,
    match_unique_blocks,
)
from isci.topology_null import conditional_topology_samples, topology_rarity  # noqa: E402
from scripts.run_t1_axis_null import (  # noqa: E402
    aggregate_gene_precision,
    load_matrix_and_metadata,
)

SEED = 20260712
PLANNED_AXES = ["exhaustion_like", "cd4_ctl_cytotoxic"]
RAW = ROOT / "data/GWCD4i.DE_stats.h5ad"
RANKING = ROOT / "results/final/isci_final_ranking.csv"
MATCHING = ROOT / "outputs/marson_obs_matching.parquet"
AXES = ROOT / "config/axes.yaml"
OUTPUT_DIR = ROOT / "outputs/decomposition_v2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sampler_is_evaluable(diagnostics: dict[str, float | int], n_samples: int) -> tuple[bool, list[str]]:
    failures = []
    if int(diagnostics["collected_samples"]) < int(np.ceil(0.90 * n_samples)):
        failures.append("fewer than 90% unique conditional sets")
    if int(diagnostics["initialized_chains"]) < 3:
        failures.append("fewer than three initialized chains")
    if float(diagnostics["proposal_acceptance_rate"]) < 0.001:
        failures.append("proposal acceptance below 0.001")
    if float(diagnostics["effective_sample_size"]) < min(50, 0.25 * n_samples):
        failures.append("effective sample size below gate")
    r_hat = float(diagnostics["r_hat"])
    if not np.isfinite(r_hat) or r_hat > 1.10:
        failures.append("R-hat is non-finite or above 1.10")
    return not failures, failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-samples", type=int, default=200)
    parser.add_argument("--n-random", type=int, default=10_000)
    args = parser.parse_args()

    zscore, z_mean, z_std, expression, targets, genes = load_matrix_and_metadata()
    print("[topology v2] computing exact gene-gene correlation", flush=True)
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        correlation = (zscore.T @ zscore) / max(1, zscore.shape[0] - 1)
    if not np.isfinite(correlation).all():
        raise RuntimeError("correlation matrix contains non-finite values")
    np.fill_diagonal(correlation, 1.0)
    expression_deciles = pd.qcut(
        pd.Series(expression).rank(method="first"), 10, labels=False
    ).to_numpy(dtype=int)
    config = load_axes_config(AXES)
    axes = build_axis_vectors(config, genes, suppl_dir=ROOT / "data/emdann")

    ranking = pd.read_csv(RANKING).set_index("gene")
    ranking = ranking[ranking["detectable_effect"].astype(bool)].copy()
    matching = pd.read_parquet(MATCHING).groupby("gene", observed=True)[
        ["target_baseMean", "n_cells_target"]
    ].mean()
    ranking = ranking.join(matching)
    positives = ranking.index[ranking["known_regulator"].astype(bool)].tolist()
    candidates = ranking.index[~ranking["known_regulator"].astype(bool)].tolist()
    blocks = match_unique_blocks(
        ranking,
        positives,
        candidates,
        match_cols=["target_baseMean", "n_cells_target"],
        n_negatives=8,
    )
    gene_to_column = {gene: index for index, gene in enumerate(genes)}
    ranking_to_code = {gene: index for index, gene in enumerate(ranking.index)}
    target_columns = np.asarray([gene_to_column.get(gene, -1) for gene in targets], dtype=int)
    target_gene_codes = np.asarray([ranking_to_code.get(gene, -1) for gene in targets], dtype=int)

    rng = np.random.default_rng(SEED)
    results: list[dict[str, object]] = []
    score_rows: list[dict[str, object]] = []
    for axis_index, axis_name in enumerate(PLANNED_AXES):
        real_vector = axes[axis_name].astype(np.float64)
        real_indices = np.flatnonzero(real_vector)
        rarity, rarity_null = topology_rarity(
            real_indices,
            expression_deciles,
            correlation,
            n_random=args.n_random,
            seed=SEED + axis_index,
        )
        samples, diagnostics_object = conditional_topology_samples(
            real_indices,
            expression_deciles,
            correlation,
            n_samples=args.n_samples,
            tolerance=0.20,
            n_chains=4,
            burn_in=2_000,
            thinning=100,
            max_initialization_steps=50_000,
            seed=SEED + axis_index,
        )
        diagnostics = asdict(diagnostics_object)
        evaluable, failures = sampler_is_evaluable(diagnostics, args.n_samples)
        print(
            f"[topology v2] {axis_name}: rarity percentile={rarity.percentile:.4f}; "
            f"samples={len(samples)}/{args.n_samples}; ESS={diagnostics['effective_sample_size']:.1f}",
            flush=True,
        )
        base_result = {
            "axis": axis_name,
            "n_axis_genes": len(real_indices),
            "topology_rarity": asdict(rarity),
            "random_topology_q025": float(np.quantile(rarity_null, 0.025)),
            "random_topology_q975": float(np.quantile(rarity_null, 0.975)),
            "sampler": diagnostics,
        }
        if not evaluable:
            results.append(
                {
                    **base_result,
                    "verdict": "TOPOLOGY_SINGULAR",
                    "reason": "; ".join(failures),
                }
            )
            continue

        pseudo_vectors = []
        absolute_weights = np.abs(real_vector[real_indices])
        signs = np.sign(real_vector[real_indices])
        for sample in samples:
            vector = np.zeros_like(real_vector)
            vector[sample] = rng.permutation(absolute_weights) * rng.permutation(signs)
            vector /= np.linalg.norm(vector) + 1e-12
            pseudo_vectors.append(vector)
        weights = np.column_stack([real_vector, *pseudo_vectors])
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            projections = zscore @ (z_std[:, None] * weights)
            projections += (z_mean @ weights)[None, :]
        if not np.isfinite(projections).all():
            raise RuntimeError(f"non-finite projections for {axis_name}")
        precision = aggregate_gene_precision(
            projections,
            weights,
            zscore,
            z_mean,
            z_std,
            target_columns,
            target_gene_codes,
            len(ranking),
        )
        gains = []
        coefficients = []
        for candidate_index in range(weights.shape[1]):
            analysis = ranking[["magnitude"]].copy()
            analysis["axis_precision"] = precision[:, candidate_index]
            predictions = blocked_oof_predictions(
                analysis,
                blocks,
                effect_col="magnitude",
                component_col="axis_precision",
                seed=SEED + axis_index,
                min_negatives=8,
            )
            gain = delta_auprc(predictions)
            coefficient = float(predictions.attrs["mean_component_coefficient"])
            gains.append(gain)
            coefficients.append(coefficient)
            score_rows.append(
                {
                    "axis": axis_name,
                    "candidate_index": candidate_index,
                    "is_real_axis": candidate_index == 0,
                    "delta_auprc_oof": gain,
                    "mean_component_coefficient": coefficient,
                }
            )
        real_gain = gains[0]
        null = np.asarray(gains[1:])
        empirical_p = float((1 + np.sum(null >= real_gain)) / (1 + len(null)))
        support = (
            real_gain > float(np.quantile(null, 0.95))
            and empirical_p < 0.05
            and coefficients[0] > 0
        )
        results.append(
            {
                **base_result,
                "real_gain": real_gain,
                "median_conditional_null_gain": float(np.median(null)),
                "conditional_null_95th": float(np.quantile(null, 0.95)),
                "empirical_p": empirical_p,
                "real_component_coefficient": coefficients[0],
                "verdict": "SUPPORT_TOPOLOGY_CONDITIONAL" if support else "UNSUPPORTED",
            }
        )

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    timestamp = datetime.now().astimezone().isoformat()
    command = (
        f"python scripts/run_topology_null_v2.py --n-samples {args.n_samples} "
        f"--n-random {args.n_random}"
    )
    provenance = {
        "git_sha": git_sha,
        "data_sha256": {
            str(RAW.relative_to(ROOT)): sha256(RAW),
            str(RANKING.relative_to(ROOT)): sha256(RANKING),
            str(MATCHING.relative_to(ROOT)): sha256(MATCHING),
        },
        "axes_sha256": sha256(AXES),
        "timestamp": timestamp,
        "command": command,
        "seed": SEED,
        "method_version": "topology_conditional_null_v2",
    }
    payload = {
        "test": "Topology-conditional axis null v2",
        "status": "EXPLORATORY_EVOLUTIONARY",
        "results": results,
        "provenance": provenance,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "topology_null_v2.json").write_text(json.dumps(payload, indent=2))
    scores = pd.DataFrame(score_rows)
    if not scores.empty:
        for key, value in provenance.items():
            scores[key] = json.dumps(value, sort_keys=True) if isinstance(value, dict) else value
        scores.to_parquet(OUTPUT_DIR / "topology_null_v2_scores.parquet", index=False)
    print(json.dumps(results, indent=2), flush=True)


if __name__ == "__main__":
    main()
