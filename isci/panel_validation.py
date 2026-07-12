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
    data = frame[required].apply(pd.to_numeric, errors="coerce")
    if data.isna().any().any() or not np.isfinite(data.to_numpy()).all():
        raise ValueError("panel validation features must be finite and complete")
    y = data[label_col].to_numpy(dtype=int)
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
