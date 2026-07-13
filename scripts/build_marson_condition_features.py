#!/usr/bin/env python
"""Build the v2 gene-by-condition controllability feature table from Marson DE statistics."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.axes import build_axis_vectors, load_axes_config  # noqa: E402

RAW = ROOT / "data/GWCD4i.DE_stats.h5ad"
RANKING = ROOT / "results/final/isci_final_ranking.csv"
MATCHING = ROOT / "outputs/marson_obs_matching.parquet"
AXES = ROOT / "config/axes.yaml"
OUTPUT = ROOT / "outputs/decomposition_v2/marson_condition_features.parquet"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def categorical(group: h5py.Group) -> np.ndarray:
    categories = group["categories"].asstr()[:]
    return categories[group["codes"][:]].astype(str)


def main() -> None:
    ranking = pd.read_csv(RANKING).set_index("gene")
    population = ranking.index[ranking["detectable_effect"].astype(bool)]
    config = load_axes_config(AXES)

    with h5py.File(RAW, "r") as handle:
        genes = [str(value) for value in handle["var/gene_name"].asstr()[:]]
        targets = categorical(handle["obs/target_contrast_gene_name"])
        conditions = categorical(handle["obs/culture_condition"])
        axes = build_axis_vectors(config, genes, suppl_dir=ROOT / "data/emdann")
        axis_names = list(axes)
        weights = np.column_stack([axes[name] for name in axis_names]).astype(np.float64)
        gene_to_column = {gene: index for index, gene in enumerate(genes)}
        target_columns = np.asarray([gene_to_column.get(gene, -1) for gene in targets], dtype=int)
        keep = np.isin(targets, population)
        kept_rows = np.flatnonzero(keep)
        projections = np.empty((len(kept_rows), len(axis_names)), dtype=np.float64)
        source_rows = np.empty(len(kept_rows), dtype=int)
        cursor = 0
        zscore = handle["layers/zscore"]
        for start in range(0, len(targets), 512):
            stop = min(start + 512, len(targets))
            local_keep = keep[start:stop]
            if not local_keep.any():
                continue
            matrix = np.asarray(zscore[start:stop], dtype=np.float64)
            with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
                chunk_projection = matrix @ weights
            local_rows = np.flatnonzero(local_keep)
            local_targets = target_columns[start:stop][local_keep]
            valid = local_targets >= 0
            chunk_projection = chunk_projection[local_keep]
            if valid.any():
                chunk_projection[valid] -= (
                    matrix[local_rows[valid], local_targets[valid], None]
                    * weights[local_targets[valid]]
                )
            count = len(local_rows)
            projections[cursor : cursor + count] = np.abs(chunk_projection)
            source_rows[cursor : cursor + count] = start + local_rows
            cursor += count
        if not np.isfinite(projections).all():
            raise RuntimeError("condition-level axis projections contain non-finite values")

        table = pd.DataFrame(
            {
                "gene": targets[source_rows],
                "condition": conditions[source_rows],
                "effect_reach": handle["obs/n_total_de_genes"][:][source_rows],
                "repeatability": handle["obs/donor_correlation_hits_mean"][:][source_rows],
                "target_baseMean": handle["obs/target_baseMean"][:][source_rows],
                "n_cells_target": handle["obs/n_cells_target"][:][source_rows],
            }
        )
    for column, axis_name in enumerate(axis_names):
        table[f"precision__{axis_name}"] = projections[:, column]

    table = table.join(
        ranking[["known_regulator"]], on="gene", validate="many_to_one"
    ).sort_values(["gene", "condition"], kind="mergesort")
    if table.duplicated(["gene", "condition"]).any():
        raise RuntimeError("gene-condition rows are not unique")
    if set(table["condition"]) != {"Rest", "Stim8hr", "Stim48hr"}:
        raise RuntimeError("unexpected condition set")
    counts = table.groupby("gene", observed=True)["condition"].nunique()
    complete_genes = counts.index[counts.eq(3)]
    complete_coverage = len(complete_genes) / len(population)
    table = table[table["gene"].isin(complete_genes)].copy()
    if complete_coverage < 0.80:
        raise RuntimeError(f"complete-condition coverage {complete_coverage:.1%} below 80%")
    known = set(ranking.index[ranking["known_regulator"].astype(bool)]) & set(population)
    if not known.issubset(set(complete_genes)):
        raise RuntimeError("at least one positive regulator lacks a condition")

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    provenance = {
        "git_sha": git_sha,
        "data_sha256": json.dumps(
            {
                str(RAW.relative_to(ROOT)): sha256(RAW),
                str(RANKING.relative_to(ROOT)): sha256(RANKING),
                str(MATCHING.relative_to(ROOT)): sha256(MATCHING),
            },
            sort_keys=True,
        ),
        "axes_sha256": sha256(AXES),
        "timestamp": datetime.now().astimezone().isoformat(),
        "command": "python scripts/build_marson_condition_features.py",
        "seed": 20260712,
        "method_version": "controllability_profile_v2",
        "population_n": len(population),
        "complete_condition_n": len(complete_genes),
        "complete_condition_coverage": complete_coverage,
    }
    for key, value in provenance.items():
        table[key] = value
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(OUTPUT, index=False)
    print(
        table.groupby("condition", observed=True)[["effect_reach", "repeatability"]]
        .agg(["count", "median"])
        .to_string()
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
