"""Extract magnitude-conditional controllership features from canonical long effects.

The implementation follows the frozen CCI measurement protocol: effect magnitude is a confound,
axis specificity is evaluated on axis genes with leave-one-marker-out, and reproducibility measures
directional agreement across independent donor/guide vectors. Missing replication remains missing.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeatureExtractionIssue:
    code: str
    severity: str
    perturbation: str | None
    condition: str | None
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "perturbation": self.perturbation,
            "condition": self.condition,
            "message": self.message,
        }


@dataclass(frozen=True)
class FeatureExtractionResult:
    status: str
    features: pd.DataFrame
    axis_scores: pd.DataFrame
    issues: tuple[FeatureExtractionIssue, ...]
    methods: dict[str, Any]

    def report(self) -> dict[str, Any]:
        return {
            "schema_version": "isci_feature_extraction_v1",
            "status": self.status,
            "feature_rows": len(self.features),
            "axis_score_rows": len(self.axis_scores),
            "missing_specificity": int(self.features["specificity"].isna().sum())
            if "specificity" in self.features
            else 0,
            "missing_reproducibility": int(self.features["reproducibility"].isna().sum())
            if "reproducibility" in self.features
            else 0,
            "issues": [issue.to_dict() for issue in self.issues],
            "methods": self.methods,
            "biological_verdict": "NOT_ISSUED",
        }


_REQUIRED_COLUMNS = {
    "perturbation",
    "feature",
    "effect",
    "standardized_effect",
}


def _rms(values: pd.Series) -> float:
    numeric = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    finite = numeric[np.isfinite(numeric)]
    return float(np.sqrt(np.mean(finite**2))) if finite.size else float("nan")


def _weighted_feature_mean(frame: pd.DataFrame, column: str) -> pd.Series:
    values = pd.to_numeric(frame[column], errors="coerce")
    weights = (
        pd.to_numeric(frame["_weight"], errors="coerce")
        if "_weight" in frame
        else pd.Series(1.0, index=frame.index)
    )
    valid = values.notna() & np.isfinite(values) & weights.notna() & (weights > 0)
    working = frame.loc[valid, ["feature"]].copy()
    working["_weighted_value"] = values.loc[valid] * weights.loc[valid]
    working["_weight"] = weights.loc[valid]
    grouped = working.groupby("feature", observed=True, sort=True).sum()
    return grouped["_weighted_value"] / grouped["_weight"]


def _axis_specificity(
    mean_effect: pd.Series,
    perturbation: str,
    axes_config: dict[str, Any],
    min_axis_genes: int,
) -> tuple[float, str | None, float, list[dict[str, Any]]]:
    scores = []
    for axis_name, axis in axes_config.get("axes", {}).items():
        markers = dict(axis.get("curated_markers") or {})
        markers.pop(perturbation, None)
        measured = [
            gene for gene in markers if gene in mean_effect.index and pd.notna(mean_effect[gene])
        ]
        if len(measured) < min_axis_genes:
            scores.append(
                {
                    "axis": axis_name,
                    "axis_score": float("nan"),
                    "n_measured_markers": len(measured),
                    "evaluable": False,
                }
            )
            continue
        z = mean_effect.loc[measured].to_numpy(dtype=float)
        weights = np.array([float(markers[gene]) for gene in measured], dtype=float)
        denom = np.linalg.norm(z) * np.linalg.norm(weights)
        score = float(np.clip(np.dot(z, weights) / denom, -1.0, 1.0)) if denom > 0 else float("nan")
        scores.append(
            {
                "axis": axis_name,
                "axis_score": score,
                "n_measured_markers": len(measured),
                "evaluable": bool(np.isfinite(score)),
            }
        )
    finite = [row for row in scores if np.isfinite(row["axis_score"])]
    if not finite:
        return float("nan"), None, float("nan"), scores
    best = max(finite, key=lambda row: abs(row["axis_score"]))
    return abs(float(best["axis_score"])), str(best["axis"]), float(best["axis_score"]), scores


def _replicate_labels(frame: pd.DataFrame) -> pd.Series | None:
    if "donor" in frame and "guide" in frame:
        return frame["donor"].astype(str) + "::" + frame["guide"].astype(str)
    if "replicate" in frame and "guide" in frame:
        return frame["replicate"].astype(str) + "::" + frame["guide"].astype(str)
    if "donor" in frame:
        return frame["donor"].astype(str)
    if "replicate" in frame:
        return frame["replicate"].astype(str)
    if "guide" in frame:
        return frame["guide"].astype(str)
    return None


def _reproducibility(frame: pd.DataFrame, min_overlap_genes: int) -> tuple[float, int, int]:
    labels = _replicate_labels(frame)
    if labels is None:
        return float("nan"), 0, 0
    working = frame.assign(_replicate=labels).copy()
    working["_weight"] = (
        pd.to_numeric(working["_weight"], errors="coerce") if "_weight" in working else 1.0
    )
    working["standardized_effect"] = pd.to_numeric(working["standardized_effect"], errors="coerce")
    valid = (
        np.isfinite(working["standardized_effect"])
        & np.isfinite(working["_weight"])
        & (working["_weight"] > 0)
    )
    working = working.loc[valid]
    working["_weighted_value"] = working["standardized_effect"] * working["_weight"]
    grouped = working.groupby(["_replicate", "feature"], observed=True, sort=True)[
        ["_weighted_value", "_weight"]
    ].sum()
    matrix = (grouped["_weighted_value"] / grouped["_weight"]).unstack("feature")
    if len(matrix) < 2:
        return float("nan"), len(matrix), 0
    similarities = []
    for left, right in combinations(matrix.index, 2):
        pair = matrix.loc[[left, right]].T.dropna()
        if len(pair) < min_overlap_genes:
            continue
        left_values = pair[left].to_numpy(dtype=float)
        right_values = pair[right].to_numpy(dtype=float)
        denom = np.linalg.norm(left_values) * np.linalg.norm(right_values)
        if denom > 0:
            similarities.append(float(np.dot(left_values, right_values) / denom))
    if not similarities:
        return float("nan"), len(matrix), 0
    coherence = (float(np.mean(similarities)) + 1.0) / 2.0
    return float(np.clip(coherence, 0.0, 1.0)), len(matrix), len(similarities)


def _aggregate_optional(frame: pd.DataFrame, column: str) -> Any:
    if column not in frame:
        return None
    if column == "benchmark_positive":
        return bool(frame[column].fillna(False).astype(bool).any())
    numeric = pd.to_numeric(frame[column], errors="coerce")
    weights = (
        pd.to_numeric(frame["_weight"], errors="coerce")
        if "_weight" in frame
        else pd.Series(1.0, index=frame.index)
    )
    valid = numeric.notna() & np.isfinite(numeric) & weights.notna() & (weights > 0)
    return (
        float(np.average(numeric.loc[valid], weights=weights.loc[valid])) if valid.any() else None
    )


def extract_controller_features(
    long_effects: pd.DataFrame,
    axes_config: dict[str, Any],
    *,
    min_axis_genes: int = 3,
    min_overlap_genes: int = 3,
) -> FeatureExtractionResult:
    """Convert canonical long effects into one controller-feature row per gene/condition."""

    missing = sorted(_REQUIRED_COLUMNS - set(long_effects.columns))
    if missing:
        issue = FeatureExtractionIssue(
            "MISSING_COLUMNS",
            "ERROR",
            None,
            None,
            f"canonical long table is missing: {', '.join(missing)}",
        )
        return FeatureExtractionResult(
            "NOT_EVALUABLE",
            pd.DataFrame(),
            pd.DataFrame(),
            (issue,),
            {},
        )
    if min_axis_genes < 2 or min_overlap_genes < 2:
        issue = FeatureExtractionIssue(
            "INVALID_THRESHOLD",
            "ERROR",
            None,
            None,
            "minimum axis and overlap thresholds must be at least 2",
        )
        return FeatureExtractionResult(
            "NOT_EVALUABLE",
            pd.DataFrame(),
            pd.DataFrame(),
            (issue,),
            {},
        )
    if long_effects.empty:
        issue = FeatureExtractionIssue(
            "EMPTY_INPUT",
            "ERROR",
            None,
            None,
            "canonical long table contains no effect rows",
        )
        return FeatureExtractionResult(
            "NOT_EVALUABLE",
            pd.DataFrame(),
            pd.DataFrame(),
            (issue,),
            {},
        )
    if "_weight" in long_effects:
        weights = pd.to_numeric(long_effects["_weight"], errors="coerce")
        if weights.isna().any() or (~np.isfinite(weights)).any() or (weights <= 0).any():
            issue = FeatureExtractionIssue(
                "INVALID_WEIGHTS",
                "ERROR",
                None,
                None,
                "internal row weights must be finite and greater than zero",
            )
            return FeatureExtractionResult(
                "NOT_EVALUABLE", pd.DataFrame(), pd.DataFrame(), (issue,), {}
            )

    data = long_effects.copy()
    if "condition" not in data:
        data["condition"] = "__all__"
    issues: list[FeatureExtractionIssue] = []
    feature_rows = []
    axis_rows = []
    for (condition, perturbation), frame in data.groupby(
        ["condition", "perturbation"], observed=True, sort=True
    ):
        mean_standardized = _weighted_feature_mean(frame, "standardized_effect")
        specificity, best_axis, signed_axis_score, scores = _axis_specificity(
            mean_standardized,
            str(perturbation),
            axes_config,
            min_axis_genes,
        )
        reproducibility, n_replicates, n_pairs = _reproducibility(frame, min_overlap_genes)
        if not np.isfinite(specificity):
            issues.append(
                FeatureExtractionIssue(
                    "AXIS_NOT_EVALUABLE",
                    "WARNING",
                    str(perturbation),
                    str(condition),
                    f"no axis retained at least {min_axis_genes} measured markers after LOO",
                )
            )
        if not np.isfinite(reproducibility):
            issues.append(
                FeatureExtractionIssue(
                    "REPRODUCIBILITY_NOT_EVALUABLE",
                    "WARNING",
                    str(perturbation),
                    str(condition),
                    f"requires two replicate vectors sharing at least {min_overlap_genes} genes",
                )
            )
        row: dict[str, Any] = {
            "perturbation": str(perturbation),
            "condition": str(condition),
            "magnitude": _rms(mean_standardized),
            "magnitude_sensitivity": _rms(_weighted_feature_mean(frame, "effect")),
            "specificity": specificity,
            "reproducibility": reproducibility,
            "best_axis": best_axis,
            "best_axis_signed_score": signed_axis_score,
            "n_replicates": n_replicates,
            "n_replicate_pairs": n_pairs,
        }
        for optional in ("target_expression", "n_guides", "n_cells", "benchmark_positive"):
            if optional in frame:
                row[optional] = _aggregate_optional(frame, optional)
        feature_rows.append(row)
        for score in scores:
            axis_rows.append(
                {
                    "perturbation": str(perturbation),
                    "condition": str(condition),
                    **score,
                }
            )

    features = pd.DataFrame(feature_rows)
    axis_scores = pd.DataFrame(axis_rows)
    complete = features[["magnitude", "specificity", "reproducibility"]].notna().all(axis=1)
    if complete.all():
        status = "COMPLETE"
    elif complete.any():
        status = "PARTIAL"
    else:
        status = "NOT_EVALUABLE"
    methods = {
        "magnitude": "RMS of mean standardized-effect vector",
        "magnitude_sensitivity": "RMS of mean raw-effect vector",
        "specificity": "maximum absolute marker-restricted cosine across LOO axes",
        "reproducibility": "mean pairwise replicate-vector cosine mapped from [-1,1] to [0,1]",
        "min_axis_genes": min_axis_genes,
        "min_overlap_genes": min_overlap_genes,
        "leave_one_marker_out": True,
        "biological_verdict": "NOT_ISSUED",
    }
    return FeatureExtractionResult(status, features, axis_scores, tuple(issues), methods)


def _summarize_effect_block(block: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    working = block.copy()
    working["effect"] = pd.to_numeric(working["effect"], errors="coerce")
    working["standardized_effect"] = pd.to_numeric(working["standardized_effect"], errors="coerce")
    valid = np.isfinite(working["effect"]) & np.isfinite(working["standardized_effect"])
    excluded = int((~valid).sum())
    working = working.loc[valid]
    if working.empty:
        return pd.DataFrame(), excluded

    keys = ["condition", "perturbation", "feature"]
    keys.extend(column for column in ("donor", "guide") if column in working)
    aggregations: dict[str, str] = {
        "effect": "mean",
        "standardized_effect": "mean",
    }
    for optional in ("target_expression", "n_guides", "n_cells"):
        if optional in working:
            working[optional] = pd.to_numeric(working[optional], errors="coerce")
            aggregations[optional] = "mean"
    if "benchmark_positive" in working:
        aggregations["benchmark_positive"] = "max"
    summary = (
        working.groupby(keys, as_index=False, observed=True, sort=True, dropna=False)
        .agg(aggregations)
        .reset_index(drop=True)
    )
    weights = working.groupby(keys, observed=True, sort=True, dropna=False).size().to_numpy()
    summary["_weight"] = weights
    return summary, excluded


def extract_controller_features_from_group_blocks(
    group_blocks: Iterable[tuple[tuple[str, str], pd.DataFrame]],
    axes_config: dict[str, Any],
    *,
    min_axis_genes: int = 3,
    min_overlap_genes: int = 3,
) -> FeatureExtractionResult:
    """Extract features from contiguous H5AD group blocks with bounded screen-level memory."""

    feature_frames = []
    axis_frames = []
    issues: list[FeatureExtractionIssue] = []
    seen: set[tuple[str, str]] = set()
    current_key: tuple[str, str] | None = None
    summaries: list[pd.DataFrame] = []
    source_rows = 0
    excluded_rows = 0
    peak_buffer_rows = 0
    base_methods: dict[str, Any] = {}

    def finalize_group() -> None:
        nonlocal summaries, base_methods, peak_buffer_rows
        if current_key is None:
            return
        if not summaries:
            issues.append(
                FeatureExtractionIssue(
                    "GROUP_NO_FINITE_EFFECTS",
                    "WARNING",
                    current_key[1],
                    current_key[0],
                    "all effect rows in this group were non-finite",
                )
            )
            return
        peak_buffer_rows = max(peak_buffer_rows, sum(len(frame) for frame in summaries))
        result = extract_controller_features(
            pd.concat(summaries, ignore_index=True),
            axes_config,
            min_axis_genes=min_axis_genes,
            min_overlap_genes=min_overlap_genes,
        )
        feature_frames.append(result.features)
        axis_frames.append(result.axis_scores)
        issues.extend(result.issues)
        base_methods = result.methods
        summaries = []

    for key, block in group_blocks:
        key = (str(key[0]), str(key[1]))
        if current_key is not None and key != current_key:
            finalize_group()
            seen.add(current_key)
            if key in seen:
                issue = FeatureExtractionIssue(
                    "NONCONTIGUOUS_GROUP",
                    "ERROR",
                    key[1],
                    key[0],
                    "streamed groups must be contiguous to preserve bounded memory",
                )
                return FeatureExtractionResult(
                    "NOT_EVALUABLE", pd.DataFrame(), pd.DataFrame(), (issue,), {}
                )
        current_key = key
        source_rows += len(block)
        summary, excluded = _summarize_effect_block(block)
        excluded_rows += excluded
        if not summary.empty:
            summaries.append(summary)
    finalize_group()

    if not feature_frames:
        issue = FeatureExtractionIssue(
            "EMPTY_INPUT", "ERROR", None, None, "stream contained no finite effect groups"
        )
        return FeatureExtractionResult(
            "NOT_EVALUABLE", pd.DataFrame(), pd.DataFrame(), tuple([*issues, issue]), {}
        )
    if excluded_rows:
        issues.append(
            FeatureExtractionIssue(
                "NONFINITE_ROWS_EXCLUDED",
                "WARNING",
                None,
                None,
                f"excluded {excluded_rows} of {source_rows} streamed effect rows",
            )
        )
    features = pd.concat(feature_frames, ignore_index=True)
    axis_scores = pd.concat(axis_frames, ignore_index=True)
    complete = features[["magnitude", "specificity", "reproducibility"]].notna().all(axis=1)
    status = "COMPLETE" if complete.all() else "PARTIAL" if complete.any() else "NOT_EVALUABLE"
    methods = {
        **base_methods,
        "streaming_grouped": True,
        "streamed_effect_rows": source_rows,
        "excluded_nonfinite_rows": excluded_rows,
        "peak_summary_buffer_rows": peak_buffer_rows,
    }
    return FeatureExtractionResult(status, features, axis_scores, tuple(issues), methods)
