"""Build functional axis signature vectors u_a from config and dataset-native tables.

Leave-one-out (LOO) construction is the key benchmark-leakage fix (gap C1): when a
gene is itself a ground-truth controller AND a marker of the axis it is scored on,
its Movement score is inflated because the gene is a coordinate of the ruler. LOO
rebuilds each axis with the scored gene removed from all marker/loading sources.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


def load_axes_config(path: Path | str) -> dict[str, Any]:
    """Load config/axes.yaml."""
    with open(path) as f:
        return yaml.safe_load(f)


def _data_native_loadings(
    axis_name: str, axis_cfg: dict[str, Any], gene_index: pd.Index,
    suppl_dir: Path | None,
) -> pd.Series | None:
    """Signed z-score loadings from the Marson Th2/Th1 polarization signature table.

    Column `zscore`, contrast "Th2_vs_Th1": positive z = Th2-high, negative = Th1-high.
    """
    if suppl_dir is None:
        return None
    src = str(axis_cfg.get("source", ""))
    th_path = Path(suppl_dir) / "Th2_Th1_polarization_signature_DE_results_full.suppl_table.csv"
    if "Th2_Th1_polarization" in src and th_path.exists():
        df = pd.read_csv(th_path)
        df = df[df["contrast"].str.contains("Th2_vs_Th1", na=False)]
        z = df.groupby("variable", observed=True)["zscore"].mean()
        if axis_name.startswith("th1"):
            z = -z  # Th1 axis is the negative pole of Th2_vs_Th1
        return z.reindex(gene_index).fillna(0.0)
    return None


def build_axis_vectors(
    config: dict[str, Any],
    gene_names: list[str],
    suppl_dir: Path | str | None = None,
    leave_one_out: str | None = None,
    blend_data_native: bool = True,
) -> dict[str, np.ndarray]:
    """Return unit-L2-normalized signature vector u_a per axis, aligned to gene_names.

    Combines curated markers from axes.yaml with data-native loadings (Th1/Th2) when
    suppl_dir is given. If ``leave_one_out`` is a gene symbol, its weight is zeroed in
    every axis before normalization (fixes C1).
    """
    gene_index = pd.Index(gene_names)
    suppl = Path(suppl_dir) if suppl_dir else None
    out: dict[str, np.ndarray] = {}

    for axis_name, axis_cfg in config["axes"].items():
        vec = pd.Series(0.0, index=gene_index)

        for gene, weight in (axis_cfg.get("curated_markers") or {}).items():
            if gene in gene_index:
                vec[gene] += float(weight)

        if blend_data_native:
            native = _data_native_loadings(axis_name, axis_cfg, gene_index, suppl)
            if native is not None and native.abs().sum() > 0:
                native = native / (np.linalg.norm(native.values) + 1e-12)
                if np.linalg.norm(vec.values) > 0:
                    vec = vec / np.linalg.norm(vec.values)
                vec = vec + native

        if leave_one_out is not None and leave_one_out in gene_index:
            vec[leave_one_out] = 0.0

        norm = np.linalg.norm(vec.values)
        out[axis_name] = (vec.values / norm) if norm > 0 else vec.values
    return out
