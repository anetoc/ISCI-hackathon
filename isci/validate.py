"""Validation: AUROC/AUPRC, ablation, external transfer, clinical bridge."""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd


def ground_truth_recovery(
    scores: pd.Series,
    positives: Sequence[str],
    negatives: Sequence[str] | None = None,
    leave_one_out_axes: bool = True,
) -> dict[str, float]:
    """Return AUROC, AUPRC, precision@20, precision@50.

    ``scores`` is a gene-level ranking (index = gene symbol, value = ISCI or baseline).
    Positives are ground-truth controllers; negatives default to all non-positive genes
    in ``scores`` (or an explicit expression-matched set). ``leave_one_out_axes`` is a
    provenance flag recorded verbatim in the output for audit; the LOO reconstruction
    itself happens upstream in axes.build_axis_vectors. This function does not verify
    how ``scores`` were produced — the caller is responsible for passing LOO scores.
    """
    from sklearn.metrics import average_precision_score, roc_auc_score

    scores = scores.dropna()
    pos = set(g for g in positives if g in scores.index)
    if negatives is not None:
        neg = set(g for g in negatives if g in scores.index) - pos
    else:
        neg = set(scores.index) - pos

    idx = list(pos | neg)
    y = np.array([1 if g in pos else 0 for g in idx])
    s = scores.reindex(idx).to_numpy()

    ranked = scores.sort_values(ascending=False)
    def _precision_at_k(k: int) -> float:
        topk = set(ranked.head(k).index)
        return len(topk & pos) / float(k)

    return {
        "auroc": float(roc_auc_score(y, s)) if y.sum() and (len(y) - y.sum()) else float("nan"),
        "auprc": float(average_precision_score(y, s)) if y.sum() else float("nan"),
        "precision_at_20": _precision_at_k(20),
        "precision_at_50": _precision_at_k(50),
        "n_positives": int(y.sum()),
        "n_negatives": int(len(y) - y.sum()),
        "leave_one_out_axes": bool(leave_one_out_axes),
    }


def expression_matched_negatives(
    positives: Sequence[str],
    obs: pd.DataFrame,
    gene_col: str = "target_contrast_gene_name",
    match_cols: Sequence[str] = ("target_baseMean", "n_cells_target"),
    n_per_positive: int = 5,
    exclude: Sequence[str] | None = None,
    seed: int = 42,
) -> list[str]:
    """Marson-native negatives matched to positives on expression/power covariates.

    For each positive, pick the ``n_per_positive`` nearest perturbations (by standardized
    Euclidean distance over ``match_cols``, computed on the per-gene means from ``obs``)
    that are NOT positives and NOT in ``exclude``. This removes the confound where the
    positives are simply higher-expressed or better-powered than a random background —
    the red-team's requirement (NOT GTEx bulk, NOT the full 11k background).

    Returns a de-duplicated list of matched negative gene symbols.
    """
    rng = np.random.default_rng(seed)
    per_gene = obs.groupby(gene_col, observed=True)[list(match_cols)].apply(
        lambda d: d.apply(lambda s: np.nanmean(pd.to_numeric(s, errors="coerce")))
    )
    per_gene = per_gene.dropna()
    # standardize covariates
    Z = (per_gene - per_gene.mean()) / (per_gene.std(ddof=0) + 1e-12)
    pos = set(positives)
    excl = set(exclude or []) | pos
    cand = Z.index[~Z.index.isin(excl)]
    chosen: list[str] = []
    used: set[str] = set()
    for g in positives:
        if g not in Z.index:
            continue
        d = np.sqrt(((Z.loc[cand] - Z.loc[g]) ** 2).sum(axis=1))
        order = d.sort_values().index
        picked = [x for x in order if x not in used][:n_per_positive]
        chosen.extend(picked)
        used.update(picked)
    return sorted(set(chosen))


def ablation_curve(
    full_scores: pd.DataFrame,
    variants: dict[str, pd.DataFrame],
    positives: Sequence[str],
) -> pd.DataFrame:
    """Compare recovery metrics across ISCI full and ablated variants."""
    raise NotImplementedError("Implement in Claude Science build (D2)")


def project_clinical_signature(
    isci_signature: pd.Series,
    cohort_path: str,
    outcome_column: str,
) -> dict[str, float]:
    """D4: test responder vs non-responder separation (AUROC)."""
    raise NotImplementedError("Implement in Claude Science build (D4)")
