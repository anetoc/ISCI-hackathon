"""Leakage-safe utilities for post-hoc controllability decomposition tests.

The independent evaluation unit is a *matched block*: one known positive and its
prespecified matched negatives.  Transformations are fitted only on training
blocks.  This module deliberately does not infer blocks from an aggregate list of
negatives because that would make the resampling unit scientifically ambiguous.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class MatchedBlock:
    """One positive gene and at least one matched negative gene."""

    positive: str
    negatives: tuple[str, ...]

    @property
    def genes(self) -> tuple[str, ...]:
        return (self.positive, *self.negatives)


class EmpiricalRanker:
    """Training-only empirical CDF transform, including out-of-fold values."""

    def fit(self, values: Sequence[float]) -> "EmpiricalRanker":
        array = np.asarray(values, dtype=float)
        if array.ndim != 1 or not np.isfinite(array).all() or len(array) < 2:
            raise ValueError("ranker requires at least two finite training values")
        self._sorted = np.sort(array)
        return self

    def transform(self, values: Sequence[float]) -> np.ndarray:
        if not hasattr(self, "_sorted"):
            raise RuntimeError("ranker must be fitted before transform")
        array = np.asarray(values, dtype=float)
        left = np.searchsorted(self._sorted, array, side="left")
        right = np.searchsorted(self._sorted, array, side="right")
        # Midrank expressed on (0, 1); values outside the training range remain bounded.
        return (left + right + 1.0) / (2.0 * (len(self._sorted) + 1.0))


class RankResidualizer:
    """Fit rank(component) ~ rank(effect reach) on training observations only."""

    def fit(self, effect: Sequence[float], component: Sequence[float]) -> "RankResidualizer":
        self.effect_ranker = EmpiricalRanker().fit(effect)
        self.component_ranker = EmpiricalRanker().fit(component)
        x = self.effect_ranker.transform(effect)
        y = self.component_ranker.transform(component)
        design = np.column_stack([np.ones(len(x)), x])
        self.intercept_, self.slope_ = np.linalg.lstsq(design, y, rcond=None)[0]
        return self

    def transform(self, effect: Sequence[float], component: Sequence[float]) -> np.ndarray:
        x = self.effect_ranker.transform(effect)
        y = self.component_ranker.transform(component)
        return y - (self.intercept_ + self.slope_ * x)


def validate_blocks(
    frame: pd.DataFrame,
    blocks: Sequence[MatchedBlock],
    *,
    min_negatives: int = 5,
) -> None:
    """Reject overlapping or incomplete blocks before any model is fitted."""

    if len(blocks) < 2:
        raise ValueError("at least two matched blocks are required for OOF evaluation")
    seen: set[str] = set()
    for block in blocks:
        if len(block.negatives) < min_negatives:
            raise ValueError(
                f"block {block.positive!r} has {len(block.negatives)} negatives; "
                f"requires at least {min_negatives}"
            )
        if block.positive in block.negatives:
            raise ValueError(f"positive {block.positive!r} also occurs as its own negative")
        for gene in block.genes:
            if gene not in frame.index:
                raise ValueError(f"gene {gene!r} is absent from the feature table")
            if gene in seen:
                raise ValueError(f"gene {gene!r} occurs in more than one evaluation block")
            seen.add(gene)


def match_unique_blocks(
    frame: pd.DataFrame,
    positives: Sequence[str],
    candidates: Sequence[str],
    *,
    match_cols: Sequence[str],
    n_negatives: int = 5,
) -> list[MatchedBlock]:
    """Create deterministic, non-overlapping blocks from frozen matching covariates.

    Covariates are standardized once solely to freeze the evaluation blocks; none of
    the predictive features, component values, or outcomes beyond positive membership
    enter the distance. Positives with the sparsest nearby candidate pool are assigned
    first to reduce greedy matching failures.
    """

    positive_genes = [gene for gene in positives if gene in frame.index]
    candidate_genes = [
        gene for gene in candidates if gene in frame.index and gene not in set(positive_genes)
    ]
    genes = list(dict.fromkeys([*positive_genes, *candidate_genes]))
    values = frame.loc[genes, list(match_cols)].apply(pd.to_numeric, errors="coerce")
    complete = values.notna().all(axis=1) & np.isfinite(values.to_numpy(dtype=float)).all(axis=1)
    values = values.loc[complete]
    positive_genes = [gene for gene in positive_genes if gene in values.index]
    candidate_genes = [gene for gene in candidate_genes if gene in values.index]
    if len(candidate_genes) < len(positive_genes) * n_negatives:
        raise ValueError(
            f"need {len(positive_genes) * n_negatives} unique negatives, "
            f"but only {len(candidate_genes)} complete candidates are available"
        )
    scale = values.std(ddof=0).replace(0.0, 1.0)
    standardized = (values - values.mean()) / scale

    distances = {
        positive: np.sqrt(
            ((standardized.loc[candidate_genes] - standardized.loc[positive]) ** 2).sum(axis=1)
        ).sort_values(kind="mergesort")
        for positive in positive_genes
    }
    # Hardest-to-match positives first; gene name is a deterministic tie-breaker.
    order = sorted(
        positive_genes,
        key=lambda gene: (-float(distances[gene].iloc[n_negatives - 1]), gene),
    )
    used: set[str] = set()
    assigned: dict[str, tuple[str, ...]] = {}
    for positive in order:
        available = [gene for gene in distances[positive].index if gene not in used]
        selected = tuple(available[:n_negatives])
        if len(selected) < n_negatives:
            raise ValueError(f"unique matching failed for {positive!r}")
        assigned[positive] = selected
        used.update(selected)
    return [MatchedBlock(positive, assigned[positive]) for positive in positive_genes]


def _fit_predict(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    effect_col: str,
    component_col: str,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    train = train.copy()
    test = test.copy()
    component_median = float(train[component_col].median())
    if not np.isfinite(component_median):
        raise ValueError("training fold has no finite component values")
    # Missing component values are imputed without consulting the held-out block.
    train[component_col] = train[component_col].fillna(component_median)
    test[component_col] = test[component_col].fillna(component_median)
    residualizer = RankResidualizer().fit(train[effect_col], train[component_col])
    train_resid = residualizer.transform(train[effect_col], train[component_col])
    test_resid = residualizer.transform(test[effect_col], test[component_col])

    base_scaler = StandardScaler().fit(train[[effect_col]])
    base_x_train = base_scaler.transform(train[[effect_col]])
    base_x_test = base_scaler.transform(test[[effect_col]])

    full_scaler = StandardScaler().fit(
        np.column_stack([train[effect_col].to_numpy(), train_resid])
    )
    full_x_train = full_scaler.transform(
        np.column_stack([train[effect_col].to_numpy(), train_resid])
    )
    full_x_test = full_scaler.transform(
        np.column_stack([test[effect_col].to_numpy(), test_resid])
    )

    y_train = train["_label"].to_numpy(dtype=int)
    base = LogisticRegression(max_iter=2_000, random_state=seed).fit(base_x_train, y_train)
    full = LogisticRegression(max_iter=2_000, random_state=seed).fit(full_x_train, y_train)
    return (
        base.predict_proba(base_x_test)[:, 1],
        full.predict_proba(full_x_test)[:, 1],
        float(full.coef_[0, 1]),
    )


def blocked_oof_predictions(
    frame: pd.DataFrame,
    blocks: Sequence[MatchedBlock],
    *,
    effect_col: str,
    component_col: str,
    seed: int = 20260712,
    min_negatives: int = 5,
) -> pd.DataFrame:
    """Leave one complete matched block out and return gene-level OOF predictions."""

    validate_blocks(frame, blocks, min_negatives=min_negatives)
    required = [effect_col, component_col]
    effect = pd.to_numeric(frame[effect_col], errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(effect).all():
        raise ValueError("effect reach must be finite and complete")
    component = pd.to_numeric(frame[component_col], errors="coerce").to_numpy(dtype=float)
    if np.isinf(component).any():
        raise ValueError("component values cannot be infinite")

    rows: list[dict[str, object]] = []
    coefficients: list[float] = []
    for fold, held in enumerate(blocks):
        train_blocks = [block for block in blocks if block is not held]
        train_genes = [gene for block in train_blocks for gene in block.genes]
        test_genes = list(held.genes)
        train = frame.loc[train_genes, required].copy()
        test = frame.loc[test_genes, required].copy()
        train["_label"] = [int(gene == block.positive) for block in train_blocks for gene in block.genes]
        test["_label"] = [int(gene == held.positive) for gene in test_genes]
        base_pred, full_pred, coefficient = _fit_predict(
            train,
            test,
            effect_col=effect_col,
            component_col=component_col,
            seed=seed + fold,
        )
        coefficients.append(coefficient)
        for gene, label, base_p, full_p in zip(
            test_genes, test["_label"], base_pred, full_pred, strict=True
        ):
            rows.append(
                {
                    "gene": gene,
                    "block": held.positive,
                    "label": int(label),
                    "base_prediction": float(base_p),
                    "full_prediction": float(full_p),
                    "fold_component_coefficient": coefficient,
                }
            )
    result = pd.DataFrame(rows)
    result.attrs["mean_component_coefficient"] = float(np.mean(coefficients))
    return result


def delta_auprc(predictions: pd.DataFrame) -> float:
    """Full-model minus effect-only AUPRC on pooled OOF predictions."""

    y = predictions["label"].to_numpy(dtype=int)
    return float(
        average_precision_score(y, predictions["full_prediction"])
        - average_precision_score(y, predictions["base_prediction"])
    )


def block_bootstrap_delta(
    predictions: pd.DataFrame,
    *,
    n_resamples: int = 1_000,
    seed: int = 20260712,
) -> np.ndarray:
    """Resample complete blocks; duplicated draws receive unique temporary block IDs."""

    groups = {name: group for name, group in predictions.groupby("block", sort=False)}
    names = np.asarray(list(groups), dtype=object)
    if len(names) < 2:
        raise ValueError("block bootstrap requires at least two blocks")
    rng = np.random.default_rng(seed)
    values = np.empty(n_resamples, dtype=float)
    for iteration in range(n_resamples):
        sampled = rng.choice(names, size=len(names), replace=True)
        replicate = pd.concat([groups[name] for name in sampled], ignore_index=True)
        values[iteration] = delta_auprc(replicate)
    return values


def permute_positive_within_blocks(
    blocks: Sequence[MatchedBlock], *, seed: int
) -> list[MatchedBlock]:
    """Uniformly reassign the positive identity within every fixed matched block."""

    rng = np.random.default_rng(seed)
    permuted: list[MatchedBlock] = []
    for block in blocks:
        genes = list(block.genes)
        positive = str(rng.choice(genes))
        permuted.append(MatchedBlock(positive, tuple(gene for gene in genes if gene != positive)))
    return permuted


def benjamini_hochberg(p_values: Iterable[float]) -> np.ndarray:
    """Return monotone BH-adjusted p-values in the original order."""

    p = np.asarray(list(p_values), dtype=float)
    if p.ndim != 1 or ((p < 0) | (p > 1) | ~np.isfinite(p)).any():
        raise ValueError("p-values must be finite values in [0, 1]")
    order = np.argsort(p)
    ranked = p[order] * len(p) / np.arange(1, len(p) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty_like(ranked)
    adjusted[order] = np.clip(ranked, 0.0, 1.0)
    return adjusted


def component_verdict(
    *, gain: float, coefficient: float, ci_low: float, q_value: float, evaluable: bool = True
) -> str:
    """Apply the frozen T2 verdict without converting uncertainty into absence."""

    if not evaluable:
        return "NOT_EVALUABLE"
    if gain <= 0 or coefficient <= 0:
        return "UNSUPPORTED"
    if ci_low > 0 and q_value < 0.05:
        return "SUPPORTED"
    return "DIRECTIONAL_UNCERTAIN"
