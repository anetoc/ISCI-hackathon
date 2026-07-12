"""Low-memory AnnData effect-matrix adapter for DatasetSpec v1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import pandas as pd
from scipy import sparse

try:
    import anndata as ad
except ImportError:  # The tabular adapter and CLI must remain usable before optional sync.
    ad = None

from isci.adapters.tabular import (
    AdapterIssue,
    DatasetInspection,
    IssueSeverity,
    RuntimeCapability,
    _declared_capability,
    _error,
    _minimum_unique_per_positive,
    _resolve_inside_root,
    _runtime_capability,
    _sha256,
    _warning,
)
from isci.dataset_spec import DatasetSpec


@dataclass(frozen=True)
class AnnDataInspectionResult:
    """Canonical observation metadata plus the physical H5AD inspection report."""

    observations: pd.DataFrame
    inspection: DatasetInspection
    matrix_shape: tuple[int, int] | None
    effect_layer: str | None
    standardized_effect_layer: str | None
    values_scanned: bool
    invalid_effect_values: int | None

    @property
    def table(self) -> pd.DataFrame:
        """Compatibility view used by the CLI; effect values remain block-streamed."""

        return self.observations


class AnnDataAdapterError(ValueError):
    """Raised when block streaming is requested for a non-evaluable H5AD."""

    def __init__(self, inspection: DatasetInspection):
        self.inspection = inspection
        super().__init__("AnnData dataset is not evaluable; inspect issues before streaming")


def _empty_result(
    spec: DatasetSpec,
    issues: list[AdapterIssue],
    *,
    data_sha256: str | None = None,
    source_rows: int = 0,
) -> AnnDataInspectionResult:
    inspection = DatasetInspection(
        dataset_id=spec.dataset.id,
        declared_capability=_declared_capability(spec),
        runtime_capability=RuntimeCapability.NOT_EVALUABLE,
        data_sha256=data_sha256,
        source_rows=source_rows,
        canonical_rows=0,
        excluded_rows=source_rows,
        n_perturbations=0,
        n_features=None,
        n_conditions=None,
        n_donors=None,
        n_guides=None,
        n_positives=None,
        n_negative_pool=None,
        min_donors_per_positive=None,
        min_guides_per_positive=None,
        min_conditions_per_positive=None,
        issues=tuple(issues),
        capability_notes=("No biological verdict may be issued until adapter errors are fixed.",),
    )
    return AnnDataInspectionResult(
        observations=pd.DataFrame(),
        inspection=inspection,
        matrix_shape=None,
        effect_layer=spec.input.layers.get("effect"),
        standardized_effect_layer=spec.input.layers.get("standardized_effect"),
        values_scanned=False,
        invalid_effect_values=None,
    )


def _canonical_observations(
    adata: Any, spec: DatasetSpec, issues: list[AdapterIssue]
) -> pd.DataFrame | None:
    sources = list(spec.mapping.values())
    positive_column = None
    if spec.benchmark and spec.benchmark.positives["source"] == "column":
        positive_column = str(spec.benchmark.positives["column"])
        sources.append(positive_column)

    missing = sorted(set(sources) - set(adata.obs.columns))
    if missing:
        issues.append(
            _error(
                "MISSING_OBS_COLUMNS",
                "mapping",
                f"AnnData.obs is missing declared columns: {', '.join(missing)}",
            )
        )
        return None
    mapping_sources = list(spec.mapping.values())
    collisions = sorted({source for source in mapping_sources if mapping_sources.count(source) > 1})
    if collisions:
        issues.append(
            _error(
                "MAPPING_COLLISION",
                "mapping",
                f"one obs column maps to multiple logical fields: {', '.join(collisions)}",
            )
        )
        return None

    rename = {source: logical for logical, source in spec.mapping.items()}
    if positive_column is not None:
        if positive_column in rename:
            issues.append(
                _error(
                    "MAPPING_COLLISION",
                    "benchmark.positives.column",
                    "positive-set column cannot also map to observation metadata",
                )
            )
            return None
        rename[positive_column] = "benchmark_positive"
    observations = adata.obs.loc[:, list(dict.fromkeys(sources))].rename(columns=rename).copy()
    perturbation = observations["perturbation"]
    if perturbation.isna().any() or perturbation.astype(str).str.strip().eq("").any():
        issues.append(
            _error(
                "INVALID_PERTURBATION_IDS",
                "mapping.perturbation",
                "perturbation IDs must be non-empty for every observation",
            )
        )
        return None
    for field in ("condition", "donor", "guide"):
        if field in observations and observations[field].isna().any():
            issues.append(
                _warning(
                    "MISSING_DESIGN_METADATA",
                    f"mapping.{field}",
                    f"{int(observations[field].isna().sum())} observations have missing {field}",
                )
            )
    return observations.reset_index(drop=True)


def _positive_mask(
    spec: DatasetSpec,
    observations: pd.DataFrame,
    repo_root: Path,
    issues: list[AdapterIssue],
) -> pd.Series | None:
    if spec.benchmark is None:
        return None
    positives = spec.benchmark.positives
    if positives["source"] == "column":
        return observations["benchmark_positive"].eq(positives.get("positive_value", True))

    root = repo_root.resolve()
    positive_path = (root / str(positives["path"])).resolve()
    if not positive_path.is_relative_to(root) or not positive_path.is_file():
        issues.append(
            _error(
                "POSITIVE_SET_NOT_FOUND",
                "benchmark.positives.path",
                "positive-set file is missing or escapes the repository root",
            )
        )
        return None
    positive_ids = {
        line.strip()
        for line in positive_path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if not positive_ids:
        issues.append(_error("EMPTY_POSITIVE_SET", "benchmark.positives.path", "file has no IDs"))
        return None
    observed = set(observations["perturbation"].astype(str))
    missing_count = len(positive_ids - observed)
    if missing_count:
        issues.append(
            _warning(
                "POSITIVES_NOT_OBSERVED",
                "benchmark.positives.path",
                f"{missing_count} positive IDs are absent from AnnData.obs",
            )
        )
    return observations["perturbation"].astype(str).isin(positive_ids)


def _dense(block) -> np.ndarray:
    return block.toarray() if sparse.issparse(block) else np.asarray(block)


def _scan_layers(
    adata: Any, effect_layer: str, standardized_layer: str, block_rows: int
) -> tuple[int, int]:
    total = 0
    invalid = 0
    for start in range(0, adata.n_obs, block_rows):
        stop = min(start + block_rows, adata.n_obs)
        for layer in (effect_layer, standardized_layer):
            values = _dense(adata.layers[layer][start:stop, :])
            total += values.size
            invalid += int((~np.isfinite(values)).sum())
    return total, invalid


def inspect_anndata_dataset(
    spec: DatasetSpec,
    *,
    repo_root: Path | str,
    scan_values: bool = False,
    block_rows: int = 64,
) -> AnnDataInspectionResult:
    """Inspect an H5AD in backed mode and optionally scan effect layers blockwise."""

    issues: list[AdapterIssue] = []
    if ad is None:
        issues.append(
            _error(
                "DEPENDENCY_MISSING",
                "anndata",
                "install project dependencies with 'uv sync' before inspecting H5AD",
            )
        )
        return _empty_result(spec, issues)
    if spec.input.layout != "anndata_effects":
        issues.append(
            _error("UNSUPPORTED_LAYOUT", "input.layout", "AnnData adapter requires anndata_effects")
        )
        return _empty_result(spec, issues)
    if block_rows < 1:
        issues.append(_error("INVALID_BLOCK_SIZE", "block_rows", "must be an integer >= 1"))
        return _empty_result(spec, issues)

    root = Path(repo_root)
    input_path = _resolve_inside_root(spec, root, issues)
    if input_path is None:
        return _empty_result(spec, issues)
    data_sha256 = _sha256(input_path)
    if spec.input.sha256 is not None and data_sha256.lower() != spec.input.sha256.lower():
        issues.append(_error("HASH_MISMATCH", "input.sha256", "input SHA-256 does not match spec"))
        return _empty_result(spec, issues, data_sha256=data_sha256)

    effect_layer = spec.input.layers["effect"]
    standardized_layer = spec.input.layers["standardized_effect"]
    try:
        adata = ad.read_h5ad(input_path, backed="r")
    except Exception as exc:
        issues.append(
            _error("H5AD_READ_ERROR", "input.path", f"could not open H5AD: {type(exc).__name__}")
        )
        return _empty_result(spec, issues, data_sha256=data_sha256)

    try:
        missing_layers = [
            layer for layer in (effect_layer, standardized_layer) if layer not in adata.layers
        ]
        if missing_layers:
            issues.append(
                _error(
                    "MISSING_LAYERS",
                    "input.layers",
                    f"H5AD is missing declared layers: {', '.join(missing_layers)}",
                )
            )
            return _empty_result(
                spec, issues, data_sha256=data_sha256, source_rows=int(adata.n_obs)
            )
        if adata.n_obs == 0 or adata.n_vars == 0:
            issues.append(_error("EMPTY_INPUT", "input.path", "H5AD has an empty matrix dimension"))
            return _empty_result(
                spec, issues, data_sha256=data_sha256, source_rows=int(adata.n_obs)
            )
        if not adata.var_names.is_unique or (adata.var_names.astype(str).str.strip() == "").any():
            issues.append(
                _error(
                    "INVALID_FEATURE_IDS", "var_names", "feature IDs must be unique and non-empty"
                )
            )
            return _empty_result(
                spec, issues, data_sha256=data_sha256, source_rows=int(adata.n_obs)
            )

        observations = _canonical_observations(adata, spec, issues)
        if observations is None:
            return _empty_result(
                spec, issues, data_sha256=data_sha256, source_rows=int(adata.n_obs)
            )
        positive_mask = _positive_mask(spec, observations, root, issues)
        if any(issue.severity == IssueSeverity.ERROR for issue in issues):
            return _empty_result(
                spec, issues, data_sha256=data_sha256, source_rows=int(adata.n_obs)
            )
        if positive_mask is not None:
            observations["benchmark_positive"] = positive_mask.astype(bool)

        n_perturbations = int(observations["perturbation"].nunique())
        n_positives = (
            int(observations.loc[positive_mask, "perturbation"].nunique())
            if positive_mask is not None
            else None
        )
        n_negative_pool = n_perturbations - n_positives if n_positives is not None else None
        min_donors = _minimum_unique_per_positive(observations, "donor", positive_mask)
        min_guides = _minimum_unique_per_positive(observations, "guide", positive_mask)
        min_conditions = _minimum_unique_per_positive(observations, "condition", positive_mask)
        runtime_capability, capability_notes = _runtime_capability(
            has_benchmark=positive_mask is not None,
            n_positives=n_positives,
            n_negative_pool=n_negative_pool,
            min_donors=min_donors,
            min_guides=min_guides,
            min_conditions=min_conditions,
        )

        invalid_effect_values = None
        if scan_values:
            _, invalid_effect_values = _scan_layers(
                adata, effect_layer, standardized_layer, block_rows
            )
            if invalid_effect_values:
                issues.append(
                    _warning(
                        "NONFINITE_EFFECT_VALUES",
                        "input.layers",
                        f"found {invalid_effect_values} non-finite values across both effect layers",
                    )
                )
                if runtime_capability == RuntimeCapability.CONFIRMATORY_READY:
                    runtime_capability = RuntimeCapability.BENCHMARK_READY
                    capability_notes = (
                        "Design coverage passes, but non-finite effect values require downstream exclusion.",
                    )
        else:
            issues.append(
                _warning(
                    "EFFECT_VALUES_NOT_SCANNED",
                    "input.layers",
                    "layer values were not scanned; use scan_values=True for a full finite-value pass",
                )
            )
            if runtime_capability == RuntimeCapability.CONFIRMATORY_READY:
                runtime_capability = RuntimeCapability.BENCHMARK_READY
                capability_notes = (
                    "Design coverage passes, but effect values were not fully scanned.",
                )

        inspection = DatasetInspection(
            dataset_id=spec.dataset.id,
            declared_capability=_declared_capability(spec),
            runtime_capability=runtime_capability,
            data_sha256=data_sha256,
            source_rows=int(adata.n_obs),
            canonical_rows=len(observations),
            excluded_rows=0,
            n_perturbations=n_perturbations,
            n_features=int(adata.n_vars),
            n_conditions=(
                int(observations["condition"].nunique()) if "condition" in observations else None
            ),
            n_donors=int(observations["donor"].nunique()) if "donor" in observations else None,
            n_guides=int(observations["guide"].nunique()) if "guide" in observations else None,
            n_positives=n_positives,
            n_negative_pool=n_negative_pool,
            min_donors_per_positive=min_donors,
            min_guides_per_positive=min_guides,
            min_conditions_per_positive=min_conditions,
            issues=tuple(issues),
            capability_notes=capability_notes,
        )
        return AnnDataInspectionResult(
            observations=observations,
            inspection=inspection,
            matrix_shape=(int(adata.n_obs), int(adata.n_vars)),
            effect_layer=effect_layer,
            standardized_effect_layer=standardized_layer,
            values_scanned=scan_values,
            invalid_effect_values=invalid_effect_values,
        )
    finally:
        if adata.file is not None:
            adata.file.close()


def iter_anndata_effect_blocks(
    spec: DatasetSpec,
    *,
    repo_root: Path | str,
    block_rows: int = 64,
) -> Iterator[pd.DataFrame]:
    """Yield canonical long-form effect blocks without materializing the full H5AD.

    Each yielded frame contains logical observation metadata, ``feature``, ``effect`` and
    ``standardized_effect``. Non-finite values are preserved so downstream analysis must record any
    exclusions explicitly.
    """

    inspection = inspect_anndata_dataset(
        spec, repo_root=repo_root, scan_values=False, block_rows=block_rows
    )
    if not inspection.inspection.evaluable:
        raise AnnDataAdapterError(inspection.inspection)

    path = (Path(repo_root).resolve() / spec.input.path).resolve()
    adata = ad.read_h5ad(path, backed="r")
    try:
        effect_layer = spec.input.layers["effect"]
        standardized_layer = spec.input.layers["standardized_effect"]
        feature_ids = adata.var_names.astype(str).to_numpy()
        for start in range(0, adata.n_obs, block_rows):
            stop = min(start + block_rows, adata.n_obs)
            obs = adata.obs.iloc[start:stop].loc[:, list(spec.mapping.values())]
            obs = obs.rename(columns={source: logical for logical, source in spec.mapping.items()})
            effect = _dense(adata.layers[effect_layer][start:stop, :])
            standardized = _dense(adata.layers[standardized_layer][start:stop, :])
            n_observations = stop - start
            block = {
                logical: np.repeat(obs[logical].to_numpy(), adata.n_vars)
                for logical in spec.mapping
            }
            if "benchmark_positive" in inspection.observations:
                block["benchmark_positive"] = np.repeat(
                    inspection.observations.iloc[start:stop]["benchmark_positive"].to_numpy(),
                    adata.n_vars,
                )
            block.update(
                {
                    "feature": np.tile(feature_ids, n_observations),
                    "effect": effect.reshape(-1),
                    "standardized_effect": standardized.reshape(-1),
                }
            )
            yield pd.DataFrame(block)
    finally:
        if adata.file is not None:
            adata.file.close()
