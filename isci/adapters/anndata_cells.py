"""Metadata-only preflight for cell-by-feature perturbation AnnData inputs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import anndata as ad
except ImportError:  # Keep tabular workflows importable without the H5AD stack.
    ad = None

from isci.adapters.tabular import (
    AdapterIssue,
    IssueSeverity,
    _error,
    _resolve_inside_root,
    _sha256,
    _warning,
)
from isci.dataset_spec import DatasetSpec


class CellPreflightStatus(StrEnum):
    READY_FOR_EFFECT_CONSTRUCTION = "READY_FOR_EFFECT_CONSTRUCTION"
    DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class CellPreflightResult:
    dataset_id: str
    status: CellPreflightStatus
    data_sha256: str | None
    matrix_shape: tuple[int, int] | None
    source_rows: int
    eligible_cells: int
    excluded_cells: int
    multi_guide_cells: int
    n_perturbations: int
    n_controls: int
    n_replicates: int
    n_donors: int | None
    eligible_effect_strata: int
    underpowered_effect_strata: int
    perturbation_conditions_ready: int
    donor_resolved_conditions_ready: int
    issues: tuple[AdapterIssue, ...]
    preprocessing: dict[str, Any]

    @property
    def can_construct_effects(self) -> bool:
        return self.perturbation_conditions_ready > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "isci_cell_preflight_v1",
            "dataset_id": self.dataset_id,
            "status": self.status.value,
            "can_construct_effects": self.can_construct_effects,
            "data_sha256": self.data_sha256,
            "matrix_shape": list(self.matrix_shape) if self.matrix_shape else None,
            "source_rows": self.source_rows,
            "eligible_cells": self.eligible_cells,
            "excluded_cells": self.excluded_cells,
            "multi_guide_cells": self.multi_guide_cells,
            "n_perturbations": self.n_perturbations,
            "n_controls": self.n_controls,
            "n_replicates": self.n_replicates,
            "n_donors": self.n_donors,
            "eligible_effect_strata": self.eligible_effect_strata,
            "underpowered_effect_strata": self.underpowered_effect_strata,
            "perturbation_conditions_ready": self.perturbation_conditions_ready,
            "donor_resolved_conditions_ready": self.donor_resolved_conditions_ready,
            "issues": [issue.to_dict() for issue in self.issues],
            "preprocessing": self.preprocessing,
            "biological_verdict": "NOT_ISSUED",
        }


def _empty_result(
    spec: DatasetSpec,
    issues: list[AdapterIssue],
    *,
    data_sha256: str | None = None,
    source_rows: int = 0,
) -> CellPreflightResult:
    return CellPreflightResult(
        spec.dataset.id,
        CellPreflightStatus.NOT_EVALUABLE,
        data_sha256,
        None,
        source_rows,
        0,
        source_rows,
        0,
        0,
        0,
        0,
        None,
        0,
        0,
        0,
        0,
        tuple(issues),
        {},
    )


def _coverage(
    cells: pd.DataFrame,
    control_mask: pd.Series,
    *,
    min_cells: int,
    min_replicates: int,
) -> tuple[int, int, int, int]:
    background = [column for column in ("condition", "donor", "replicate") if column in cells]
    effect_keys = [*background, "perturbation", "guide"]
    effect_counts = (
        cells.loc[~control_mask]
        .groupby(effect_keys, observed=True, dropna=False)
        .size()
        .rename("n_effect")
    )
    control_counts = (
        cells.loc[control_mask]
        .groupby(background, observed=True, dropna=False)
        .size()
        .rename("n_control")
    )
    groups = effect_counts.reset_index().merge(
        control_counts.reset_index(), on=background, how="left"
    )
    groups["n_control"] = groups["n_control"].fillna(0)
    eligible = groups[(groups["n_effect"] >= min_cells) & (groups["n_control"] >= min_cells)].copy()
    condition_keys = ["perturbation"]
    if "condition" in eligible:
        condition_keys.append("condition")
    grouped = eligible.groupby(condition_keys, observed=True, dropna=False)
    replicate_ready = grouped["replicate"].nunique() >= min_replicates
    donor_ready = (
        replicate_ready & (grouped["donor"].nunique() >= min_replicates)
        if "donor" in eligible
        else pd.Series(False, index=replicate_ready.index)
    )
    return (
        len(eligible),
        len(groups) - len(eligible),
        int(replicate_ready.sum()),
        int(donor_ready.sum()),
    )


def preflight_anndata_cells(
    spec: DatasetSpec,
    *,
    repo_root: Path | str,
) -> CellPreflightResult:
    """Inspect cell-level H5AD metadata without reading expression values."""

    issues: list[AdapterIssue] = []
    if ad is None:
        issues.append(_error("DEPENDENCY_MISSING", "anndata", "install anndata before preflight"))
        return _empty_result(spec, issues)
    if spec.input.layout != "anndata_cells" or spec.preprocessing is None:
        issues.append(
            _error(
                "UNSUPPORTED_LAYOUT",
                "input.layout",
                "cell preflight requires a validated anndata_cells DatasetSpec",
            )
        )
        return _empty_result(spec, issues)

    root = Path(repo_root).resolve()
    input_path = _resolve_inside_root(spec, root, issues)
    if input_path is None:
        return _empty_result(spec, issues)
    data_sha256 = _sha256(input_path)
    if spec.input.sha256 and data_sha256.lower() != spec.input.sha256.lower():
        issues.append(_error("HASH_MISMATCH", "input.sha256", "input SHA-256 does not match spec"))
        return _empty_result(spec, issues, data_sha256=data_sha256)

    try:
        adata = ad.read_h5ad(input_path, backed="r")
    except Exception as exc:
        issues.append(_error("H5AD_READ_ERROR", "input.path", type(exc).__name__))
        return _empty_result(spec, issues, data_sha256=data_sha256)

    try:
        source = spec.preprocessing.source
        if source["location"] == "layer" and source["layer"] not in adata.layers:
            issues.append(
                _error(
                    "SOURCE_LAYER_MISSING", "preprocessing.source.layer", "declared layer is absent"
                )
            )
        if adata.n_obs == 0 or adata.n_vars == 0:
            issues.append(_error("EMPTY_INPUT", "input.path", "H5AD has an empty matrix dimension"))
        if not adata.var_names.is_unique or (adata.var_names.astype(str).str.strip() == "").any():
            issues.append(
                _error(
                    "INVALID_FEATURE_IDS", "var_names", "feature IDs must be unique and non-empty"
                )
            )

        control_column = str(spec.preprocessing.control["column"])
        source_columns = list(dict.fromkeys([*spec.mapping.values(), control_column]))
        missing = sorted(set(source_columns) - set(adata.obs.columns))
        if missing:
            issues.append(
                _error(
                    "MISSING_OBS_COLUMNS", "mapping", f"missing {len(missing)} declared obs columns"
                )
            )
        collisions = sorted(
            source
            for source in spec.mapping.values()
            if list(spec.mapping.values()).count(source) > 1
        )
        if collisions:
            issues.append(
                _error(
                    "MAPPING_COLLISION",
                    "mapping",
                    "logical fields must map to distinct obs columns",
                )
            )
        if any(issue.severity == IssueSeverity.ERROR for issue in issues):
            return _empty_result(
                spec, issues, data_sha256=data_sha256, source_rows=int(adata.n_obs)
            )

        raw = adata.obs.loc[:, source_columns].copy()
        control_values = raw[control_column].astype(str)
        cells = raw.loc[:, list(spec.mapping.values())].rename(
            columns={source_name: logical for logical, source_name in spec.mapping.items()}
        )
        identity = ["perturbation", "guide", "guide_count", "replicate"]
        identity.extend(column for column in ("condition", "donor") if column in cells)
        metadata_valid = pd.Series(True, index=cells.index)
        for column in identity:
            metadata_valid &= cells[column].notna() & cells[column].astype(str).str.strip().ne("")
        guide_count = pd.to_numeric(cells["guide_count"], errors="coerce")
        multi_guide = guide_count.notna() & guide_count.ne(1)
        valid = metadata_valid & guide_count.eq(1)
        excluded = int((~valid).sum())
        if excluded:
            issues.append(
                _warning(
                    "CELLS_EXCLUDED",
                    "obs",
                    f"excluded {excluded} cells by declared metadata and guide policy",
                )
            )
        cells = cells.loc[valid].copy()
        control_mask = control_values.loc[valid].isin(spec.preprocessing.control["labels"])
        if not control_mask.any():
            issues.append(
                _error(
                    "CONTROLS_NOT_OBSERVED",
                    "preprocessing.control.labels",
                    "no declared controls were observed",
                )
            )
            return _empty_result(
                spec, issues, data_sha256=data_sha256, source_rows=int(adata.n_obs)
            )

        eligible, underpowered, ready, donor_ready = _coverage(
            cells,
            control_mask,
            min_cells=spec.preprocessing.min_cells_per_stratum,
            min_replicates=spec.preprocessing.min_replicates,
        )
        issues.append(
            _warning(
                "SIGNAL_VALUES_NOT_SCANNED",
                "preprocessing.source",
                "metadata-only preflight did not read matrix values",
            )
        )
        n_donors = int(cells["donor"].nunique()) if "donor" in cells else None
        if ready == 0:
            issues.append(
                _error(
                    "INSUFFICIENT_COVERAGE",
                    "preprocessing",
                    "no perturbation-condition meets cell and replicate thresholds",
                )
            )
            status = CellPreflightStatus.NOT_EVALUABLE
        elif donor_ready == 0:
            issues.append(
                _warning(
                    "DONOR_COVERAGE_INSUFFICIENT",
                    "mapping.donor",
                    "effect construction is diagnostic without sufficient donors",
                )
            )
            status = CellPreflightStatus.DIAGNOSTIC_ONLY
        else:
            status = CellPreflightStatus.READY_FOR_EFFECT_CONSTRUCTION

        return CellPreflightResult(
            spec.dataset.id,
            status,
            data_sha256,
            (int(adata.n_obs), int(adata.n_vars)),
            int(adata.n_obs),
            len(cells),
            excluded,
            int(multi_guide.sum()),
            int(cells.loc[~control_mask, "perturbation"].nunique()),
            int(control_mask.sum()),
            int(cells["replicate"].nunique()),
            n_donors,
            eligible,
            underpowered,
            ready,
            donor_ready,
            tuple(issues),
            {
                "source_location": source["location"],
                "source_kind": source["kind"],
                "normalization": spec.preprocessing.normalization,
                "contrast": spec.preprocessing.contrast,
                "standardization": spec.preprocessing.standardization,
                "min_cells_per_stratum": spec.preprocessing.min_cells_per_stratum,
                "min_replicates": spec.preprocessing.min_replicates,
                "multi_guide_policy": spec.preprocessing.multi_guide_policy,
            },
        )
    finally:
        if adata.file is not None:
            adata.file.close()
