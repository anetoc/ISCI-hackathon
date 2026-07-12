"""Outcome-blind selection and resource planning for a prospective donor panel."""

from __future__ import annotations

import math

import pandas as pd


REQUIRED_LABEL_COLUMNS = {"gene", "is_positive", "is_matched_negative"}
REQUIRED_GUIDE_COLUMNS = {"cell_barcode", "feature_call"}
SEQUENCE_STATUS = "REQUIRES_DESIGN_AND_VALIDATION"


def _as_bool(series: pd.Series, *, column: str) -> pd.Series:
    """Normalize common serialized booleans without treating non-empty strings as true."""

    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)
    normalized = series.astype(str).str.strip().str.lower()
    allowed = {"true", "false", "1", "0"}
    unknown = sorted(set(normalized) - allowed)
    if unknown:
        raise ValueError(f"{column} contains invalid boolean values: {unknown}")
    return normalized.isin({"true", "1"})


def guide_coverage(guidecalls: pd.DataFrame) -> pd.DataFrame:
    """Count singleton guide assignments by guide and paired experimental context."""

    missing = REQUIRED_GUIDE_COLUMNS - set(guidecalls.columns)
    if missing:
        raise ValueError(f"guide calls missing columns: {sorted(missing)}")

    # Multi-guide cells do not provide an unambiguous guide-level coverage estimate.
    singleton = guidecalls[
        ~guidecalls["feature_call"].astype(str).str.contains("|", regex=False)
    ].copy()
    if singleton.empty:
        raise ValueError("guide calls contain no singleton assignments")
    singleton["guide_id"] = singleton["feature_call"].astype(str)
    singleton["target"] = singleton["guide_id"].str.replace(r"-\d+$", "", regex=True)
    well_text = singleton["cell_barcode"].astype(str).str.rsplit("-", n=1).str[-1]
    if not well_text.str.fullmatch(r"\d+").all():
        raise ValueError("cell barcodes must end in a numeric well suffix")
    singleton["well"] = well_text.astype(int)
    if not singleton["well"].between(1, 8).all():
        raise ValueError("well suffix must be between 1 and 8")
    singleton["context"] = singleton["well"].map(
        lambda well: "nostim" if well <= 4 else "stim"
    )

    counts = (
        singleton.groupby(["target", "guide_id", "context"], observed=True)
        .size()
        .unstack("context", fill_value=0)
        .reindex(columns=["nostim", "stim"], fill_value=0)
        .reset_index()
    )
    counts = counts.rename(
        columns={"nostim": "nostim_cells", "stim": "stim_cells"}
    )
    counts["min_context_cells"] = counts[["nostim_cells", "stim_cells"]].min(axis=1)
    counts["total_cells"] = counts[["nostim_cells", "stim_cells"]].sum(axis=1)
    return counts.sort_values(["target", "guide_id"], kind="mergesort").reset_index(
        drop=True
    )


def _best_guides(coverage: pd.DataFrame, target: str, *, count: int = 2) -> pd.DataFrame:
    """Choose technically strongest guides using only assignment coverage."""

    candidates = coverage[coverage["target"] == target].sort_values(
        ["min_context_cells", "total_cells", "guide_id"],
        ascending=[False, False, True],
        kind="mergesort",
    )
    if len(candidates) < count:
        raise ValueError(f"target {target} has fewer than {count} singleton guides")
    return candidates.head(count).copy()


def select_prospective_panel(
    labels: pd.DataFrame,
    guidecalls: pd.DataFrame,
    *,
    positive_count: int = 8,
    sentinels: tuple[str, ...] = ("GATA3", "TBX21"),
    non_target_count: int = 4,
) -> pd.DataFrame:
    """Build the frozen panel using labels and guide coverage, never outcome features."""

    missing = REQUIRED_LABEL_COLUMNS - set(labels.columns)
    if missing:
        raise ValueError(f"labels missing columns: {sorted(missing)}")
    if labels["gene"].duplicated().any():
        raise ValueError("labels must contain one row per gene")
    if positive_count < 1 or non_target_count < 1:
        raise ValueError("panel counts must be positive")

    label_table = labels[["gene", "is_positive", "is_matched_negative"]].copy()
    label_table["is_positive"] = _as_bool(
        label_table["is_positive"], column="is_positive"
    )
    label_table["is_matched_negative"] = _as_bool(
        label_table["is_matched_negative"], column="is_matched_negative"
    )
    overlap = label_table["is_positive"] & label_table["is_matched_negative"]
    if overlap.any():
        raise ValueError("positive and matched-negative labels must be disjoint")

    coverage = guide_coverage(guidecalls)
    positive_genes = label_table.loc[label_table["is_positive"], "gene"].astype(str)
    if len(positive_genes) < positive_count:
        raise ValueError("not enough frozen positives for requested panel")

    # A target's score is its weaker selected guide-context cell count. This prevents one
    # high-coverage guide from hiding a second guide that cannot support reproducibility checks.
    positive_candidates: list[tuple[str, int]] = []
    for gene in positive_genes:
        selected_guides = _best_guides(coverage, gene)
        positive_candidates.append(
            (gene, int(selected_guides["min_context_cells"].min()))
        )
    selected_positives = [
        gene
        for gene, _ in sorted(positive_candidates, key=lambda item: (-item[1], item[0]))[
            :positive_count
        ]
    ]
    matched_negatives = sorted(
        label_table.loc[label_table["is_matched_negative"], "gene"].astype(str)
    )

    rows: list[dict[str, object]] = []

    def append_target(target: str, role: str, counted_in_primary: bool) -> None:
        guides = _best_guides(coverage, target)
        target_score = int(guides["min_context_cells"].min())
        for guide_rank, guide in enumerate(guides.itertuples(index=False), start=1):
            rows.append(
                {
                    "target": target,
                    "role": role,
                    "guide_id": guide.guide_id,
                    "guide_rank": guide_rank,
                    "nostim_cells": int(guide.nostim_cells),
                    "stim_cells": int(guide.stim_cells),
                    "min_context_cells": int(guide.min_context_cells),
                    "total_cells": int(guide.total_cells),
                    "technical_target_score": target_score,
                    "counted_in_primary": counted_in_primary,
                    "sequence_status": SEQUENCE_STATUS,
                }
            )

    for gene in selected_positives:
        append_target(gene, "PRIMARY_POSITIVE", True)
    for gene in matched_negatives:
        append_target(gene, "MATCHED_NEGATIVE", True)
    primary_targets = set(selected_positives) | set(matched_negatives)
    for gene in sentinels:
        if gene not in primary_targets:
            append_target(gene, "MECHANISTIC_SENTINEL", False)

    controls = _best_guides(coverage, "NO-TARGET", count=non_target_count)
    for guide_rank, guide in enumerate(controls.itertuples(index=False), start=1):
        rows.append(
            {
                "target": "NO-TARGET",
                "role": "NON_TARGET_CONTROL",
                "guide_id": guide.guide_id,
                "guide_rank": guide_rank,
                "nostim_cells": int(guide.nostim_cells),
                "stim_cells": int(guide.stim_cells),
                "min_context_cells": int(guide.min_context_cells),
                "total_cells": int(guide.total_cells),
                "technical_target_score": int(controls["min_context_cells"].min()),
                "counted_in_primary": False,
                "sequence_status": SEQUENCE_STATUS,
            }
        )

    panel = pd.DataFrame(rows)
    if panel["guide_id"].duplicated().any():
        raise RuntimeError("guide IDs must be unique in the prospective panel")
    return panel.reset_index(drop=True)


def plan_panel_resources(
    n_guides: int,
    *,
    donor_counts: tuple[int, ...] = (8, 10, 12),
    contexts: int = 2,
    usable_cells_per_guide: int = 50,
    usable_fraction: float = 0.60,
    recovered_cells_per_channel: int = 20_000,
) -> list[dict[str, int | float]]:
    """Calculate transparent capture and channel scenarios for a fixed guide panel."""

    if n_guides < 1 or contexts < 1 or usable_cells_per_guide < 1:
        raise ValueError("guide, context, and usable-cell counts must be positive")
    if not donor_counts or any(count < 1 for count in donor_counts):
        raise ValueError("donor counts must be positive")
    if not 0 < usable_fraction <= 1:
        raise ValueError("usable fraction must be in (0, 1]")
    if recovered_cells_per_channel < 1:
        raise ValueError("recovered cells per channel must be positive")

    scenarios: list[dict[str, int | float]] = []
    for donors in donor_counts:
        usable_cells = n_guides * donors * contexts * usable_cells_per_guide
        captured_cells = math.ceil(usable_cells / usable_fraction)
        scenarios.append(
            {
                "donors": donors,
                "contexts": contexts,
                "n_guides": n_guides,
                "usable_cells_per_guide_donor_context": usable_cells_per_guide,
                "usable_fraction": usable_fraction,
                "usable_cells": usable_cells,
                "captured_cells": captured_cells,
                "recovered_cells_per_channel": recovered_cells_per_channel,
                "planning_channels": math.ceil(
                    captured_cells / recovered_cells_per_channel
                ),
            }
        )
    return scenarios
