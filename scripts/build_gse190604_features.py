#!/usr/bin/env python
"""Build target-by-context GSE190604 CRISPRa features without unpacking the MTX."""

from __future__ import annotations

import gzip
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

from isci.axes import build_axis_vectors, load_axes_config  # noqa: E402
from isci.targeted_panel import (  # noqa: E402
    aggregate_matrix_market_groups,
    log_cpm_profiles,
    matrix_market_header,
)

DATA = ROOT / "data/external/gse190604"
MATRIX = DATA / "matrix.mtx.gz"
BARCODES = DATA / "barcodes.tsv.gz"
FEATURES = DATA / "features.tsv.gz"
GUIDES = DATA / "guidecalls.txt.gz"
LABELS = ROOT / "outputs/generalization/near_immune_scores.csv"
AXES = ROOT / "config/axes.yaml"
OUTPUT = ROOT / "outputs/decomposition_v2/gse190604_features.parquet"
QC_OUTPUT = ROOT / "outputs/decomposition_v2/gse190604_feature_qc.json"
MIN_CELLS = 25
TOP_MOVED = 2_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    with gzip.open(path, "rt") as handle:
        return [line.rstrip("\n") for line in handle]


def mean_pairwise_correlation(effects: np.ndarray, moved: np.ndarray) -> float:
    correlation = np.corrcoef(effects[:, moved])
    upper = correlation[np.triu_indices(len(effects), 1)]
    return float(np.nanmean(upper))


def main() -> None:
    required = [MATRIX, BARCODES, FEATURES, GUIDES]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"missing GSE190604 files: {missing}")
    barcodes = read_lines(BARCODES)
    feature_table = pd.read_csv(
        FEATURES,
        compression="gzip",
        sep="\t",
        header=None,
        names=["gene_id", "gene", "feature_type"],
    )
    matrix_shape = matrix_market_header(MATRIX)
    if matrix_shape[:2] != (len(feature_table), len(barcodes)):
        raise RuntimeError("matrix dimensions do not match features and barcodes")

    guides = pd.read_csv(GUIDES, sep="\t")
    singleton = guides[~guides["feature_call"].str.contains("|", regex=False)].copy()
    singleton["target"] = singleton["feature_call"].str.replace(r"-\d+$", "", regex=True)
    barcode_to_column = {barcode: index for index, barcode in enumerate(barcodes)}
    singleton = singleton[singleton["cell_barcode"].isin(barcode_to_column)].copy()
    singleton["well"] = singleton["cell_barcode"].str.rsplit("-", n=1).str[-1].astype(int)
    group_keys = sorted(set(zip(singleton["target"], singleton["well"], strict=True)))
    group_to_index = {key: index for index, key in enumerate(group_keys)}
    cell_to_group = np.full(len(barcodes), -1, dtype=int)
    for row in singleton.itertuples(index=False):
        cell_to_group[barcode_to_column[row.cell_barcode]] = group_to_index[(row.target, row.well)]
    group_cells = singleton.groupby(["target", "well"], observed=True).size()

    last_percent = -1

    def progress(observed: int, expected: int) -> None:
        nonlocal last_percent
        percent = int(100 * observed / expected)
        if percent >= last_percent + 5:
            last_percent = percent
            print(f"[GSE190604] parsed {percent}% of {expected:,} nonzeros", flush=True)

    counts = aggregate_matrix_market_groups(
        MATRIX,
        cell_to_group,
        n_groups=len(group_keys),
        chunksize=2_000_000,
        progress=progress,
    )
    profiles = log_cpm_profiles(counts)
    del counts

    genes = feature_table["gene"].astype(str).tolist()
    config = load_axes_config(AXES)
    axis_vectors = build_axis_vectors(config, genes, suppl_dir=ROOT / "data/emdann")
    gene_positions: dict[str, np.ndarray] = {
        gene: np.flatnonzero(feature_table["gene"].astype(str).to_numpy() == gene)
        for gene in singleton["target"].unique()
    }
    positives = set(
        pd.read_csv(LABELS).loc[lambda data: data["is_positive"].astype(bool), "gene"]
    )
    contexts = {"nostim": range(1, 5), "stim": range(5, 9)}
    rows: list[dict[str, object]] = []
    targets = sorted(set(singleton["target"]) - {"NO-TARGET"})
    for target in targets:
        for context, wells in contexts.items():
            effects = []
            cell_counts = []
            control_profiles = []
            for well in wells:
                target_key = (target, well)
                control_key = ("NO-TARGET", well)
                if target_key not in group_to_index or control_key not in group_to_index:
                    continue
                n_cells = int(group_cells.get(target_key, 0))
                if n_cells < MIN_CELLS:
                    continue
                target_profile = profiles[group_to_index[target_key]]
                control_profile = profiles[group_to_index[control_key]]
                effects.append(target_profile - control_profile)
                control_profiles.append(control_profile)
                cell_counts.append(n_cells)
            if len(effects) < 3:
                continue
            effect_matrix = np.asarray(effects, dtype=np.float64)
            mean_effect = effect_matrix.mean(axis=0)
            target_indices = gene_positions.get(target, np.asarray([], dtype=int))
            mean_effect[target_indices] = 0.0
            effect_matrix[:, target_indices] = 0.0
            moved = np.argsort(np.abs(mean_effect))[-min(TOP_MOVED, len(mean_effect)) :]
            row = {
                "gene": target,
                "context": context,
                "effect_reach": float(np.linalg.norm(mean_effect)),
                "repeatability": mean_pairwise_correlation(effect_matrix, moved),
                "target_base_expr": (
                    float(np.mean(np.asarray(control_profiles)[:, target_indices]))
                    if len(target_indices)
                    else np.nan
                ),
                "n_cells_target": float(np.mean(cell_counts)),
                "n_wells": len(effects),
                "is_positive": target in positives,
            }
            for axis_name, axis_vector in axis_vectors.items():
                vector = np.asarray(axis_vector, dtype=np.float64).copy()
                vector[target_indices] = 0.0
                vector /= np.linalg.norm(vector) + 1e-12
                row[f"precision__{axis_name}"] = float(abs(mean_effect @ vector))
            rows.append(row)
    result = pd.DataFrame(rows).sort_values(["gene", "context"], kind="mergesort")
    if result.empty or result.duplicated(["gene", "context"]).any():
        raise RuntimeError("invalid target-context feature table")

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    provenance = {
        "git_sha": git_sha,
        "data_sha256": json.dumps(
            {str(path.relative_to(ROOT)): sha256(path) for path in required}, sort_keys=True
        ),
        "axes_sha256": sha256(AXES),
        "timestamp": datetime.now().astimezone().isoformat(),
        "command": "python scripts/build_gse190604_features.py",
        "method_version": "gse190604_targeted_panel_v1",
    }
    for key, value in provenance.items():
        result[key] = value
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(OUTPUT, index=False)
    qc = {
        "n_target_context_rows": len(result),
        "n_targets": int(result["gene"].nunique()),
        "contexts": result.groupby("context", observed=True)["gene"].nunique().to_dict(),
        "positives": result.groupby("context", observed=True)["is_positive"].sum().to_dict(),
        "matrix_shape": matrix_shape[:3],
        "n_singleton_cells": len(singleton),
        "n_groups": len(group_keys),
        "normalization": "raw-count pseudobulk per target-well, log1p CPM",
        "provenance": provenance,
    }
    QC_OUTPUT.write_text(json.dumps(qc, indent=2))
    print(json.dumps(qc, indent=2), flush=True)


if __name__ == "__main__":
    main()
