"""Baselines: DE magnitude, effect size, centrality-only — must-beat comparators.

These are the honest strong baselines ISCI must beat (method.md §6, benchmark.md).
Each returns a per-perturbation score in [0,1] (percentile-ranked), aggregated to the
gene level by max over conditions so it is comparable to a gene-level ISCI ranking.
"""

from __future__ import annotations

import pandas as pd


def _gene_level(obs: pd.DataFrame, values: pd.Series, gene_col: str) -> pd.Series:
    """Percentile-rank a per-row score, then take the max over conditions per gene."""
    ranked = values.rank(pct=True)
    return ranked.groupby(obs[gene_col].to_numpy()).max()


def de_magnitude_baseline(
    obs: pd.DataFrame, gene_col: str = "target_contrast_gene_name",
) -> pd.Series:
    """Baseline from n_total_de_genes (the DE-magnitude straw-man)."""
    v = pd.to_numeric(obs["n_total_de_genes"], errors="coerce").fillna(0.0)
    return _gene_level(obs, v, gene_col)


def effect_size_baseline(
    obs: pd.DataFrame, gene_col: str = "target_contrast_gene_name",
) -> pd.Series:
    """Baseline from n_downstream (incoming trans-effects; raw association)."""
    v = pd.to_numeric(obs["n_downstream"], errors="coerce").fillna(0.0)
    return _gene_level(obs, v, gene_col)


def ontarget_effect_baseline(
    obs: pd.DataFrame, gene_col: str = "target_contrast_gene_name",
) -> pd.Series:
    """Baseline from |ontarget_effect_size| (knockdown strength)."""
    v = pd.to_numeric(obs["ontarget_effect_size"], errors="coerce").abs().fillna(0.0)
    return _gene_level(obs, v, gene_col)


def centrality_baseline(
    grn_centrality: pd.Series, gene_names: list[str] | None = None,
) -> pd.Series:
    """Centrality-only baseline: PageRank/out-degree on the GRN without FVS/MDS.

    Provided by network.py once the GRN is built (D1). Percentile-ranked.
    """
    s = grn_centrality.copy()
    if gene_names is not None:
        s = s.reindex(gene_names).fillna(0.0)
    return s.rank(pct=True)
