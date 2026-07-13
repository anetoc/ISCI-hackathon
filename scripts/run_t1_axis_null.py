#!/usr/bin/env python
"""Execute the frozen T1 adversarial pseudo-axis null on the Marson screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import h5py
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

SEED = 20260712
N_PSEUDO = 200
MAX_ATTEMPTS = 1_000
MIN_ADMISSIBILITY = 0.90
RUNTIME_SECONDS = 3 * 60 * 60
RAW = ROOT / "data/GWCD4i.DE_stats.h5ad"
RANKING = ROOT / "results/final/isci_final_ranking.csv"
MATCHING = ROOT / "outputs/marson_obs_matching.parquet"
AXES = ROOT / "config/axes.yaml"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_categorical(group: h5py.Group) -> np.ndarray:
    categories = group["categories"].asstr()[:]
    codes = group["codes"][:]
    return categories[codes].astype(str)


def mean_abs_correlation(
    indices: np.ndarray,
    absolute_correlation: np.ndarray,
    row_sums: np.ndarray,
    total_sum: float,
) -> float:
    """Exact off-diagonal mean, using the complement when the set is dense."""

    size = len(indices)
    if size < 2:
        return 0.0
    n_genes = absolute_correlation.shape[0]
    if size <= n_genes // 2:
        subtotal = float(absolute_correlation[np.ix_(indices, indices)].sum(dtype=np.float64))
    else:
        excluded = np.setdiff1d(np.arange(n_genes), indices, assume_unique=False)
        excluded_subtotal = float(
            absolute_correlation[np.ix_(excluded, excluded)].sum(dtype=np.float64)
        )
        subtotal = total_sum - 2.0 * float(row_sums[excluded].sum()) + excluded_subtotal
    return subtotal / (size * (size - 1))


def generate_pseudo_axes(
    real: np.ndarray,
    expression_deciles: np.ndarray,
    absolute_correlation: np.ndarray,
    *,
    rng: np.random.Generator,
) -> tuple[list[np.ndarray], list[dict[str, object]]]:
    real_indices = np.flatnonzero(real)
    real_weights = real[real_indices]
    row_sums = absolute_correlation.sum(axis=1, dtype=np.float64)
    total_sum = float(row_sums.sum())
    real_correlation = mean_abs_correlation(
        real_indices, absolute_correlation, row_sums, total_sum
    )
    counts = {
        decile: int(np.sum(expression_deciles[real_indices] == decile)) for decile in range(10)
    }
    pools = {decile: np.flatnonzero(expression_deciles == decile) for decile in range(10)}
    if any(counts[d] > len(pools[d]) for d in range(10)):
        return [], [{"reason": "expression-decile pool smaller than frozen axis"}]

    absolute_weights = np.abs(real_weights)
    signs = np.sign(real_weights)
    pseudo: list[np.ndarray] = []
    audit: list[dict[str, object]] = []
    for pseudo_index in range(N_PSEUDO):
        accepted = False
        for attempt in range(1, MAX_ATTEMPTS + 1):
            selected = np.concatenate(
                [
                    rng.choice(pools[decile], size=counts[decile], replace=False)
                    for decile in range(10)
                    if counts[decile]
                ]
            )
            candidate_correlation = mean_abs_correlation(
                selected, absolute_correlation, row_sums, total_sum
            )
            tolerance = 0.20 * abs(real_correlation)
            if abs(candidate_correlation - real_correlation) <= tolerance:
                weights = rng.permutation(absolute_weights) * rng.permutation(signs)
                vector = np.zeros_like(real, dtype=np.float64)
                vector[selected] = weights.astype(np.float64)
                vector /= np.linalg.norm(vector) + 1e-12
                pseudo.append(vector)
                audit.append(
                    {
                        "pseudo_index": pseudo_index,
                        "attempts": attempt,
                        "mean_abs_correlation": candidate_correlation,
                        "real_mean_abs_correlation": real_correlation,
                    }
                )
                accepted = True
                break
        if not accepted:
            audit.append(
                {
                    "pseudo_index": pseudo_index,
                    "attempts": MAX_ATTEMPTS,
                    "reason": "correlation tolerance not met",
                    "real_mean_abs_correlation": real_correlation,
                }
            )
    return pseudo, audit


def load_matrix_and_metadata() -> tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[str]
]:
    """Load only zscore/baseMean and standardize zscore in-place to bound memory."""

    with h5py.File(RAW, "r") as handle:
        z_dataset = handle["layers/zscore"]
        base_dataset = handle["layers/baseMean"]
        n_rows, n_genes = z_dataset.shape
        zscore = np.empty((n_rows, n_genes), dtype=np.float64)
        z_sum = np.zeros(n_genes, dtype=np.float64)
        z_square_sum = np.zeros(n_genes, dtype=np.float64)
        base_sum = np.zeros(n_genes, dtype=np.float64)
        base_count = np.zeros(n_genes, dtype=np.int64)
        for start in range(0, n_rows, 256):
            stop = min(start + 256, n_rows)
            z_chunk = np.asarray(z_dataset[start:stop], dtype=np.float64)
            z_chunk = np.nan_to_num(z_chunk, nan=0.0, posinf=0.0, neginf=0.0)
            zscore[start:stop] = z_chunk
            z_sum += z_chunk.sum(axis=0)
            z_square_sum += np.square(z_chunk).sum(axis=0)
            base_chunk = np.asarray(base_dataset[start:stop], dtype=np.float64)
            finite = np.isfinite(base_chunk)
            base_sum += np.where(finite, base_chunk, 0.0).sum(axis=0)
            base_count += finite.sum(axis=0)
            if start % 4096 == 0:
                print(f"[T1] loaded rows {stop}/{n_rows}", flush=True)
        targets = decode_categorical(handle["obs/target_contrast_gene_name"])
        genes = [str(value) for value in handle["var/gene_name"].asstr()[:]]
    expression = np.divide(
        base_sum, base_count, out=np.zeros_like(base_sum), where=base_count > 0
    )
    mean = z_sum / n_rows
    variance = np.maximum(z_square_sum / n_rows - np.square(mean), 0.0)
    std = np.sqrt(variance)
    std[std == 0] = 1.0
    zscore -= mean
    zscore /= std
    if not np.isfinite(zscore).all():
        raise RuntimeError("standardized zscore matrix contains non-finite values")
    print(f"[T1] standardized max_abs={np.max(np.abs(zscore)):.3f}", flush=True)
    return zscore, mean, std, expression, targets, genes


def aggregate_gene_precision(
    projections: np.ndarray,
    weights: np.ndarray,
    standardized_zscore: np.ndarray,
    mean: np.ndarray,
    std: np.ndarray,
    target_columns: np.ndarray,
    target_gene_codes: np.ndarray,
    n_ranking_genes: int,
) -> np.ndarray:
    """Apply target LOO and aggregate max absolute projection over conditions."""

    valid_target = target_columns >= 0
    raw_target = np.zeros(len(target_columns), dtype=np.float64)
    rows = np.flatnonzero(valid_target)
    columns = target_columns[valid_target]
    raw_target[valid_target] = (
        standardized_zscore[rows, columns] * std[columns] + mean[columns]
    )
    projections[valid_target] -= (
        raw_target[valid_target, None] * weights[target_columns[valid_target], :]
    )
    precision = np.full((n_ranking_genes, projections.shape[1]), np.nan, dtype=np.float64)
    valid_gene = target_gene_codes >= 0
    for column in range(projections.shape[1]):
        values = np.full(n_ranking_genes, -np.inf, dtype=np.float64)
        np.maximum.at(
            values,
            target_gene_codes[valid_gene],
            np.abs(projections[valid_gene, column]),
        )
        values[~np.isfinite(values)] = np.nan
        precision[:, column] = values
    return precision


def not_evaluable_payload(reason: str, started: float, details: dict[str, object]) -> dict:
    return {
        "test": "T1 adversarial axis null",
        "status": "POST_HOC_STRESS_TEST",
        "verdict": "NOT_EVALUABLE",
        "reason": reason,
        "runtime_seconds": time.monotonic() - started,
        "details": details,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    config = load_axes_config(AXES)
    with h5py.File(RAW, "r") as handle:
        genes = [str(value) for value in handle["var/gene_name"].asstr()[:]]
        shape = list(handle["layers/zscore"].shape)
    real_axes = build_axis_vectors(config, genes, suppl_dir=ROOT / "data/emdann")
    nonzero = {name: int(np.count_nonzero(vector)) for name, vector in real_axes.items()}
    print(f"[T1 preflight] shape={shape}; nonzero={nonzero}", flush=True)
    if args.preflight_only:
        return

    zscore, z_mean, z_std, expression, targets, genes = load_matrix_and_metadata()
    print("[T1] computing exact gene-gene correlation matrix", flush=True)
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        correlation = (zscore.T @ zscore) / max(1, zscore.shape[0] - 1)
    if not np.isfinite(correlation).all():
        raise RuntimeError("gene-gene correlation matrix contains non-finite values")
    np.abs(correlation, out=correlation)
    np.fill_diagonal(correlation, 0.0)
    expression_deciles = pd.qcut(
        pd.Series(expression).rank(method="first"), 10, labels=False
    ).to_numpy(dtype=int)

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
    score_rows: list[dict[str, object]] = []
    axis_results: list[dict[str, object]] = []
    for axis_index, (axis_name, real_vector) in enumerate(real_axes.items()):
        if time.monotonic() - started > RUNTIME_SECONDS:
            axis_results.append(
                not_evaluable_payload("three-hour runtime stop reached", started, {"axis": axis_name})
            )
            break
        print(f"[T1] generating pseudo axes for {axis_name}", flush=True)
        pseudo, audit = generate_pseudo_axes(
            real_vector.astype(np.float64), expression_deciles, correlation, rng=rng
        )
        admissibility = len(pseudo) / N_PSEUDO
        if admissibility < MIN_ADMISSIBILITY:
            axis_results.append(
                {
                    "axis": axis_name,
                    "verdict": "NOT_EVALUABLE",
                    "reason": f"pseudo-axis admissibility {admissibility:.1%} below 90%",
                    "n_admissible": len(pseudo),
                    "n_planned": N_PSEUDO,
                    "audit": audit,
                }
            )
            continue
        weights = np.column_stack([real_vector, *pseudo]).astype(np.float64)
        raw_weights = z_std[:, None] * weights
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            projections = zscore @ raw_weights
            projections += (z_mean @ weights)[None, :]
        if not np.isfinite(projections).all():
            raise RuntimeError(f"non-finite axis projections for {axis_name}")
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
        gains: list[float] = []
        coefficients: list[float] = []
        accepted_audit = [row for row in audit if "mean_abs_correlation" in row]
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
                    "mean_abs_correlation": (
                        accepted_audit[candidate_index - 1]["mean_abs_correlation"]
                        if candidate_index > 0
                        else accepted_audit[0]["real_mean_abs_correlation"]
                    ),
                }
            )
        real_gain = gains[0]
        null = np.asarray(gains[1:])
        empirical_p = float((1 + np.sum(null >= real_gain)) / (1 + len(null)))
        theta = float(real_gain - np.median(null))
        support = (
            theta > 0
            and real_gain > float(np.quantile(null, 0.95))
            and empirical_p < 0.05
            and coefficients[0] > 0
        )
        axis_results.append(
            {
                "axis": axis_name,
                "verdict": "SUPPORT" if support else "UNSUPPORTED",
                "real_gain": real_gain,
                "median_pseudo_gain": float(np.median(null)),
                "pseudo_95th": float(np.quantile(null, 0.95)),
                "theta_axis": theta,
                "empirical_p": empirical_p,
                "real_component_coefficient": coefficients[0],
                "n_admissible": len(pseudo),
                "n_planned": N_PSEUDO,
            }
        )
        print(f"[T1] {axis_name}: gain={real_gain:+.3f}, p={empirical_p:.4f}", flush=True)

    output_dir = ROOT / "outputs/decomposition"
    output_dir.mkdir(parents=True, exist_ok=True)
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    timestamp = datetime.now().astimezone().isoformat()
    command = "python scripts/run_t1_axis_null.py"
    provenance = {
        "git_sha": git_sha,
        "data_sha256": {
            str(RANKING.relative_to(ROOT)): sha256(RANKING),
            str(MATCHING.relative_to(ROOT)): sha256(MATCHING),
            str(RAW.relative_to(ROOT)): sha256(RAW),
        },
        "axes_sha256": sha256(AXES),
        "timestamp": timestamp,
        "command": command,
        "seed": SEED,
        "n_pseudo_per_axis": N_PSEUDO,
    }
    scores = pd.DataFrame(score_rows)
    for key, value in provenance.items():
        scores[key] = json.dumps(value, sort_keys=True) if isinstance(value, dict) else value
    scores.to_parquet(output_dir / "t1_axis_null_scores.parquet", index=False)
    payload = {
        "test": "T1 adversarial axis null",
        "status": "POST_HOC_STRESS_TEST",
        "results": axis_results,
        "runtime_seconds": time.monotonic() - started,
        "provenance": provenance,
    }
    (output_dir / "t1_axis_null.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(axis_results, indent=2), flush=True)


if __name__ == "__main__":
    main()
