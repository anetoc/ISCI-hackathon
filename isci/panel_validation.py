"""Cross-fitted overlap-weighted validation for targeted perturbation panels."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.preprocessing import StandardScaler

from isci.decomposition import RankResidualizer


def weighted_average_precision(y: np.ndarray, score: np.ndarray, weight: np.ndarray) -> float:
    return float(average_precision_score(y, score, sample_weight=weight))


def repeated_overlap_oof(
    frame: pd.DataFrame,
    *,
    label_col: str,
    effect_col: str,
    component_col: str,
    overlap_cols: list[str],
    n_splits: int = 5,
    n_repeats: int = 10,
    seed: int = 20260712,
) -> pd.DataFrame:
    """Cross-fit overlap weights, residualization and outcome models inside every fold."""

    required = [label_col, effect_col, component_col, *overlap_cols]
    # A boolean outcome plus floating-point covariates otherwise yields an object
    # NumPy array, on which np.isfinite is undefined. Normalize the complete
    # validation surface to float before enforcing its numerical contract.
    data = frame[required].apply(pd.to_numeric, errors="coerce").astype(float)
    if data.isna().any().any() or not np.isfinite(data.to_numpy()).all():
        raise ValueError("panel validation features must be finite and complete")
    y = data[label_col].to_numpy(dtype=int)
    if not set(np.unique(y)).issubset({0, 1}) or len(np.unique(y)) != 2:
        raise ValueError("panel validation label must contain both binary classes")
    if min(np.bincount(y)) < n_splits:
        raise ValueError("each class must contain at least n_splits genes")
    splitter = RepeatedStratifiedKFold(
        n_splits=n_splits, n_repeats=n_repeats, random_state=seed
    )
    base_predictions = np.zeros((len(data), n_repeats), dtype=float)
    full_predictions = np.zeros((len(data), n_repeats), dtype=float)
    overlap_weights = np.zeros((len(data), n_repeats), dtype=float)
    coefficients: list[float] = []
    for fold_index, (train, test) in enumerate(splitter.split(data, y)):
        repeat = fold_index // n_splits
        overlap_scaler = StandardScaler().fit(data.iloc[train][overlap_cols])
        propensity = LogisticRegression(max_iter=2_000, random_state=seed + fold_index).fit(
            overlap_scaler.transform(data.iloc[train][overlap_cols]), y[train]
        )
        train_propensity = np.clip(
            propensity.predict_proba(overlap_scaler.transform(data.iloc[train][overlap_cols]))[:, 1],
            0.05,
            0.95,
        )
        test_propensity = np.clip(
            propensity.predict_proba(overlap_scaler.transform(data.iloc[test][overlap_cols]))[:, 1],
            0.05,
            0.95,
        )
        train_weight = np.where(y[train] == 1, 1.0 - train_propensity, train_propensity)
        test_weight = np.where(y[test] == 1, 1.0 - test_propensity, test_propensity)

        residualizer = RankResidualizer().fit(
            data.iloc[train][effect_col], data.iloc[train][component_col]
        )
        train_residual = residualizer.transform(
            data.iloc[train][effect_col], data.iloc[train][component_col]
        )
        test_residual = residualizer.transform(
            data.iloc[test][effect_col], data.iloc[test][component_col]
        )
        base_scaler = StandardScaler().fit(data.iloc[train][[effect_col]])
        base_train = base_scaler.transform(data.iloc[train][[effect_col]])
        base_test = base_scaler.transform(data.iloc[test][[effect_col]])
        full_scaler = StandardScaler().fit(
            np.column_stack([data.iloc[train][effect_col], train_residual])
        )
        full_train = full_scaler.transform(
            np.column_stack([data.iloc[train][effect_col], train_residual])
        )
        full_test = full_scaler.transform(
            np.column_stack([data.iloc[test][effect_col], test_residual])
        )
        base_model = LogisticRegression(max_iter=2_000, random_state=seed + fold_index).fit(
            base_train, y[train], sample_weight=train_weight
        )
        full_model = LogisticRegression(max_iter=2_000, random_state=seed + fold_index).fit(
            full_train, y[train], sample_weight=train_weight
        )
        base_predictions[test, repeat] = base_model.predict_proba(base_test)[:, 1]
        full_predictions[test, repeat] = full_model.predict_proba(full_test)[:, 1]
        overlap_weights[test, repeat] = test_weight
        coefficients.append(float(full_model.coef_[0, 1]))
    result = pd.DataFrame(
        {
            "label": y,
            "base_prediction": base_predictions.mean(axis=1),
            "full_prediction": full_predictions.mean(axis=1),
            "overlap_weight": overlap_weights.mean(axis=1),
        },
        index=frame.index,
    )
    result.attrs["mean_component_coefficient"] = float(np.mean(coefficients))
    return result


def overlap_weighted_delta(predictions: pd.DataFrame) -> float:
    y = predictions["label"].to_numpy(dtype=int)
    weight = predictions["overlap_weight"].to_numpy(dtype=float)
    return weighted_average_precision(y, predictions["full_prediction"], weight) - weighted_average_precision(
        y, predictions["base_prediction"], weight
    )


def stratified_gene_bootstrap(
    predictions: pd.DataFrame, *, n_resamples: int = 1_000, seed: int = 20260712
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    positive = np.flatnonzero(predictions["label"].to_numpy() == 1)
    negative = np.flatnonzero(predictions["label"].to_numpy() == 0)
    values = np.empty(n_resamples, dtype=float)
    for iteration in range(n_resamples):
        indices = np.concatenate(
            [rng.choice(positive, len(positive), replace=True), rng.choice(negative, len(negative), replace=True)]
        )
        values[iteration] = overlap_weighted_delta(predictions.iloc[indices])
    return values


def paired_context_oof(
    frame: pd.DataFrame,
    *,
    gene_col: str,
    context_col: str,
    contexts: tuple[str, str],
    label_col: str,
    effect_col: str,
    component_col: str,
    overlap_cols: list[str],
    n_splits: int = 5,
    n_repeats: int = 10,
    seed: int = 20260712,
) -> dict[str, pd.DataFrame]:
    """Fit identical gene-ordered OOF pipelines for two complete contexts."""

    first, second = contexts
    subset = frame[frame[context_col].isin(contexts)].copy()
    counts = subset.groupby(gene_col, observed=True)[context_col].nunique()
    genes = sorted(counts[counts == 2].index.astype(str))
    if not genes:
        raise ValueError("paired context validation requires complete gene pairs")
    outputs: dict[str, pd.DataFrame] = {}
    reference_labels: np.ndarray | None = None
    for context in (first, second):
        context_frame = subset[subset[context_col] == context].copy()
        if context_frame[gene_col].duplicated().any():
            raise ValueError("each gene must have one row per context")
        context_frame[gene_col] = context_frame[gene_col].astype(str)
        context_frame = context_frame.set_index(gene_col).loc[genes]
        labels = context_frame[label_col].to_numpy(dtype=int)
        if reference_labels is not None and not np.array_equal(labels, reference_labels):
            raise ValueError("paired gene labels differ between contexts")
        reference_labels = labels
        outputs[context] = repeated_overlap_oof(
            context_frame,
            label_col=label_col,
            effect_col=effect_col,
            component_col=component_col,
            overlap_cols=overlap_cols,
            n_splits=n_splits,
            n_repeats=n_repeats,
            seed=seed,
        )
    return outputs


def paired_context_delta(
    predictions: dict[str, pd.DataFrame], *, contexts: tuple[str, str]
) -> float:
    """Return the first-minus-second incremental weighted-AUPRC contrast."""

    first, second = (predictions[context] for context in contexts)
    if not first.index.equals(second.index) or not np.array_equal(
        first["label"].to_numpy(), second["label"].to_numpy()
    ):
        raise ValueError("context predictions must contain aligned gene labels")
    return overlap_weighted_delta(first) - overlap_weighted_delta(second)


def stratified_paired_gene_bootstrap(
    predictions: dict[str, pd.DataFrame],
    *,
    contexts: tuple[str, str],
    n_resamples: int = 1_000,
    seed: int = 20260712,
) -> np.ndarray:
    """Bootstrap the context contrast with identical gene draws in both contexts."""

    first, second = (predictions[context] for context in contexts)
    if not first.index.equals(second.index) or not np.array_equal(
        first["label"].to_numpy(), second["label"].to_numpy()
    ):
        raise ValueError("context predictions must contain aligned gene labels")
    rng = np.random.default_rng(seed)
    labels = first["label"].to_numpy(dtype=int)
    positive = np.flatnonzero(labels == 1)
    negative = np.flatnonzero(labels == 0)
    values = np.empty(n_resamples, dtype=float)
    for iteration in range(n_resamples):
        indices = np.concatenate(
            [rng.choice(positive, len(positive), replace=True), rng.choice(negative, len(negative), replace=True)]
        )
        sampled = {
            contexts[0]: first.iloc[indices],
            contexts[1]: second.iloc[indices],
        }
        values[iteration] = paired_context_delta(sampled, contexts=contexts)
    return values


def swap_paired_context_features(
    frame: pd.DataFrame,
    *,
    gene_col: str,
    context_col: str,
    contexts: tuple[str, str],
    feature_cols: list[str],
    swap_mask: np.ndarray,
) -> pd.DataFrame:
    """Swap complete feature bundles between contexts for selected paired genes."""

    wide = frame.set_index([gene_col, context_col]).sort_index()
    genes = sorted(frame[gene_col].astype(str).unique())
    if len(swap_mask) != len(genes):
        raise ValueError("swap mask length must equal the number of genes")
    first, second = contexts
    for gene, should_swap in zip(genes, swap_mask, strict=True):
        if not should_swap:
            continue
        try:
            first_values = wide.loc[(gene, first), feature_cols].copy()
            second_values = wide.loc[(gene, second), feature_cols].copy()
        except KeyError as error:
            raise ValueError("context swap requires complete gene pairs") from error
        wide.loc[(gene, first), feature_cols] = second_values.to_numpy()
        wide.loc[(gene, second), feature_cols] = first_values.to_numpy()
    return wide.reset_index()
