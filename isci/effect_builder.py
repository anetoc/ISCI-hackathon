"""Construct perturbation-level effect matrices from validated cell-level AnnData inputs."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

try:
    import anndata as ad
except ImportError:  # Keep non-H5AD workflows importable.
    ad = None

try:
    from scipy import sparse
except ImportError:
    sparse = None

from isci.adapters import preflight_anndata_cells
from isci.dataset_spec import DatasetSpec


@dataclass(frozen=True)
class EffectBuildResult:
    dataset_id: str
    status: str
    effects_path: Path | None
    generated_spec_path: Path | None
    n_effect_rows: int
    n_features: int
    report: dict[str, Any]

    @property
    def completed(self) -> bool:
        return self.status in {"EFFECTS_BUILT", "DIAGNOSTIC_EFFECTS_BUILT"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_sha(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _canonical_cells(adata: Any, spec: DatasetSpec) -> tuple[pd.DataFrame, pd.Series]:
    control_column = str(spec.preprocessing.control["column"])
    source_columns = list(dict.fromkeys([*spec.mapping.values(), control_column]))
    raw = adata.obs.loc[:, source_columns].copy()
    control = raw[control_column].astype(str).isin(spec.preprocessing.control["labels"])
    cells = raw.loc[:, list(spec.mapping.values())].rename(
        columns={source: logical for logical, source in spec.mapping.items()}
    )
    cells["_row_position"] = np.arange(len(cells))
    identity = ["perturbation", "replicate"]
    identity.extend(column for column in ("condition", "donor") if column in cells)
    metadata_valid = pd.Series(True, index=cells.index)
    for column in identity:
        metadata_valid &= cells[column].notna() & cells[column].astype(str).str.strip().ne("")
    guide_count = pd.to_numeric(cells["guide_count"], errors="coerce")
    guide_present = cells["guide"].notna() & cells["guide"].astype(str).str.strip().ne("")
    valid_control = control & guide_count.isin([0, 1])
    valid_effect = ~control & guide_present & guide_count.eq(1)
    valid = metadata_valid & (valid_control | valid_effect)
    return cells.loc[valid].reset_index(drop=True), control.loc[valid].reset_index(drop=True)


def _eligible_groups(
    cells: pd.DataFrame,
    control: pd.Series,
    *,
    min_cells: int,
    min_replicates: int,
) -> tuple[pd.DataFrame, list[str]]:
    background = [column for column in ("condition", "donor", "replicate") if column in cells]
    effect_keys = [*background, "perturbation", "guide"]
    effect_counts = (
        cells.loc[~control]
        .groupby(effect_keys, observed=True, dropna=False)
        .size()
        .rename("n_cells")
        .reset_index()
    )
    control_counts = (
        cells.loc[control]
        .groupby(background, observed=True, dropna=False)
        .size()
        .rename("n_control")
        .reset_index()
    )
    groups = effect_counts.merge(control_counts, on=background, how="left")
    groups["n_control"] = groups["n_control"].fillna(0)
    groups = groups[(groups["n_cells"] >= min_cells) & (groups["n_control"] >= min_cells)]
    condition_keys = ["perturbation"] + (["condition"] if "condition" in groups else [])
    ready = (
        groups.groupby(condition_keys, observed=True, dropna=False)["replicate"].nunique()
        >= min_replicates
    )
    ready_index = ready[ready].index
    if len(condition_keys) == 1:
        groups = groups[groups["perturbation"].isin(ready_index)]
    else:
        ready_pairs = pd.MultiIndex.from_tuples(list(ready_index), names=condition_keys)
        observed_pairs = pd.MultiIndex.from_frame(groups[condition_keys])
        groups = groups.loc[observed_pairs.isin(ready_pairs)]
    return groups.reset_index(drop=True), background


def _profile(matrix: Any, positions: np.ndarray, kind: str, block_rows: int) -> np.ndarray:
    total = np.zeros(matrix.shape[1], dtype=np.float64)
    observed = 0
    for start in range(0, len(positions), block_rows):
        selected = positions[start : start + block_rows]
        block = matrix[selected, :]
        values = (
            block.toarray() if sparse is not None and sparse.issparse(block) else np.asarray(block)
        )
        values = np.asarray(values, dtype=np.float64)
        if not np.isfinite(values).all():
            raise ValueError("SOURCE_NONFINITE")
        if kind == "raw_counts" and (
            (values < 0).any() or not np.allclose(values, np.round(values))
        ):
            raise ValueError("SOURCE_NOT_RAW_COUNTS")
        total += values.sum(axis=0)
        observed += len(selected)
    if kind == "normalized":
        return total / max(observed, 1)
    library_size = total.sum()
    return np.log1p(total / library_size * 1_000_000) if library_size > 0 else total


def _standardize(effects: np.ndarray, conditions: pd.Series) -> np.ndarray:
    standardized = np.zeros_like(effects, dtype=np.float64)
    for condition in conditions.drop_duplicates():
        rows = conditions.eq(condition).to_numpy()
        subset = effects[rows]
        mean = subset.mean(axis=0)
        scale = subset.std(axis=0, ddof=0)
        standardized[rows] = np.divide(
            subset - mean,
            scale,
            out=np.zeros_like(subset),
            where=scale > 0,
        )
    return standardized


def _generated_spec(
    spec: DatasetSpec, root: Path, effects_path: Path, output_sha256: str
) -> dict[str, Any]:
    mapping = {
        field: field
        for field in ("perturbation", "condition", "donor", "replicate", "guide", "n_cells")
        if field in {"perturbation", "condition", "replicate", "guide", "n_cells"}
        or field in spec.mapping
    }
    return {
        "schema_version": 1,
        "dataset": {
            "id": f"{spec.dataset.id[:55]}_effects",
            "label": f"{spec.dataset.label} — constructed effects",
            "description": "Generated locally from a validated cell-level preprocessing contract.",
            "organism": spec.dataset.organism,
            "cell_system": spec.dataset.cell_system,
            "perturbation_modality": spec.dataset.perturbation_modality,
        },
        "input": {
            "path": str(effects_path.relative_to(root)),
            "format": "h5ad",
            "layout": "anndata_effects",
            "sha256": output_sha256,
            "layers": {"effect": "effect", "standardized_effect": "standardized_effect"},
        },
        "mapping": mapping,
        "analysis": {
            "axes_path": spec.analysis.axes_path,
            "primary_signal": spec.analysis.primary_signal,
            "sensitivity_signal": spec.analysis.sensitivity_signal,
            "leave_one_marker_out": spec.analysis.leave_one_marker_out,
            "n_bootstrap": spec.analysis.n_bootstrap,
            "seed": spec.analysis.seed,
        },
        "provenance": {
            "source_url": spec.provenance.source_url,
            "citation": spec.provenance.citation,
            "license": spec.provenance.license,
            "data_classification": spec.provenance.data_classification,
            "redistributable": spec.provenance.redistributable,
        },
    }


def build_anndata_effects(
    spec: DatasetSpec,
    *,
    repo_root: Path | str,
    output_dir: Path | str,
    block_rows: int = 64,
) -> EffectBuildResult:
    """Build matched-control pseudobulk effects after a successful metadata preflight."""

    root = Path(repo_root).resolve()
    destination = Path(output_dir).resolve()
    preflight = preflight_anndata_cells(spec, repo_root=root)
    base_report = {
        "schema_version": "isci_effect_build_v1",
        "dataset_id": spec.dataset.id,
        "preflight": preflight.to_dict(),
        "biological_verdict": "NOT_ISSUED",
    }
    if ad is None or sparse is None:
        return EffectBuildResult(
            spec.dataset.id, "DEPENDENCY_MISSING", None, None, 0, 0, base_report
        )
    if block_rows < 1 or not destination.is_relative_to(root):
        base_report["reason"] = "output must be inside repo root and block_rows must be >= 1"
        return EffectBuildResult(spec.dataset.id, "INVALID_OUTPUT", None, None, 0, 0, base_report)
    if not preflight.can_construct_effects:
        return EffectBuildResult(spec.dataset.id, "PREFLIGHT_FAILED", None, None, 0, 0, base_report)

    input_path = (root / spec.input.path).resolve()
    adata = ad.read_h5ad(input_path, backed="r")
    try:
        cells, control = _canonical_cells(adata, spec)
        groups, background = _eligible_groups(
            cells,
            control,
            min_cells=spec.preprocessing.min_cells_per_stratum,
            min_replicates=spec.preprocessing.min_replicates,
        )
        matrix = (
            adata.X
            if spec.preprocessing.source["location"] == "X"
            else adata.layers[spec.preprocessing.source["layer"]]
        )
        control_cells = cells.loc[control]
        control_profiles: dict[tuple[Any, ...], np.ndarray] = {}
        for key, frame in control_cells.groupby(background, observed=True, sort=True, dropna=False):
            normalized_key = key if isinstance(key, tuple) else (key,)
            control_profiles[normalized_key] = _profile(
                matrix,
                frame["_row_position"].to_numpy(dtype=int),
                spec.preprocessing.source["kind"],
                block_rows,
            )

        effects = []
        output_rows = []
        effect_keys = [*background, "perturbation", "guide"]
        effect_cells = cells.loc[~control]
        eligible_keys = set(map(tuple, groups[effect_keys].itertuples(index=False, name=None)))
        for key, frame in effect_cells.groupby(effect_keys, observed=True, sort=True, dropna=False):
            normalized_key = key if isinstance(key, tuple) else (key,)
            if normalized_key not in eligible_keys:
                continue
            metadata = dict(zip(effect_keys, normalized_key, strict=True))
            background_key = tuple(metadata[column] for column in background)
            target_profile = _profile(
                matrix,
                frame["_row_position"].to_numpy(dtype=int),
                spec.preprocessing.source["kind"],
                block_rows,
            )
            effects.append(target_profile - control_profiles[background_key])
            metadata["condition"] = str(metadata.get("condition", "__all__"))
            metadata["n_cells"] = len(frame)
            output_rows.append(metadata)

        effect_matrix = np.asarray(effects, dtype=np.float64)
        output_obs = pd.DataFrame(output_rows)
        standardized = _standardize(effect_matrix, output_obs["condition"])
        output_obs.index = [f"effect_{index}" for index in range(len(output_obs))]
        output_var = adata.var.copy()
    except ValueError as exc:
        base_report["reason"] = str(exc)
        return EffectBuildResult(
            spec.dataset.id,
            "SOURCE_VALUES_INVALID",
            None,
            None,
            0,
            int(adata.n_vars),
            base_report,
        )
    finally:
        if adata.file is not None:
            adata.file.close()

    destination.mkdir(parents=True, exist_ok=True)
    effects_path = destination / "effects.h5ad"
    generated_spec_path = destination / "dataset.effects.yaml"
    report_path = destination / "preprocessing_report.json"
    output = ad.AnnData(X=None, obs=output_obs, var=output_var, shape=effect_matrix.shape)
    output.layers["effect"] = effect_matrix.astype(np.float32)
    output.layers["standardized_effect"] = standardized.astype(np.float32)
    output.write_h5ad(effects_path, compression="gzip")
    output_sha256 = _sha256(effects_path)
    generated = _generated_spec(spec, root, effects_path, output_sha256)
    generated_spec_path.write_text(yaml.safe_dump(generated, sort_keys=False))

    status = (
        "DIAGNOSTIC_EFFECTS_BUILT"
        if preflight.status.value == "DIAGNOSTIC_ONLY"
        else "EFFECTS_BUILT"
    )
    report = {
        **base_report,
        "status": status,
        "n_effect_rows": len(output_obs),
        "n_features": len(output_var),
        "normalization": spec.preprocessing.normalization,
        "contrast": spec.preprocessing.contrast,
        "standardization": spec.preprocessing.standardization,
        "input_sha256": preflight.data_sha256,
        "output_sha256": output_sha256,
        "generated_spec_sha256": _sha256(generated_spec_path),
        "git_sha": _git_sha(root),
        "axes_sha256": _sha256(root / spec.analysis.axes_path),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": f"isci build-effects {spec.source_path.name if spec.source_path else '<dataset.yaml>'}",
    }
    report_path.write_text(json.dumps(report, indent=2, default=str) + "\n")
    return EffectBuildResult(
        spec.dataset.id,
        status,
        effects_path,
        generated_spec_path,
        len(output_obs),
        len(output_var),
        report,
    )
