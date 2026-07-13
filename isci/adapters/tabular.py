"""CSV/Parquet adapter for DatasetSpec v1.

The adapter opens only perturbation-level tables. It canonicalizes declared column names, records
all row exclusions, verifies provenance hashes, and computes the strongest capability supported by
the data that are actually present. It may downgrade the DatasetSpec declaration; it never upgrades
it silently.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from isci.dataset_spec import DatasetCapability, DatasetSpec


class RuntimeCapability(StrEnum):
    """Strongest analysis tier supported by the inspected physical data."""

    CONFIRMATORY_READY = "CONFIRMATORY_READY"
    BENCHMARK_READY = "BENCHMARK_READY"
    DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
    NOT_EVALUABLE = "NOT_EVALUABLE"


class IssueSeverity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True)
class AdapterIssue:
    """Structured adapter issue that never includes raw biological text."""

    code: str
    severity: IssueSeverity
    field: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "field": self.field,
            "message": self.message,
        }


@dataclass(frozen=True)
class DatasetInspection:
    """Data-level capability and provenance report returned by the adapter."""

    dataset_id: str
    declared_capability: DatasetCapability
    runtime_capability: RuntimeCapability
    data_sha256: str | None
    source_rows: int
    canonical_rows: int
    excluded_rows: int
    n_perturbations: int
    n_features: int | None
    n_conditions: int | None
    n_donors: int | None
    n_guides: int | None
    n_positives: int | None
    n_negative_pool: int | None
    min_donors_per_positive: int | None
    min_guides_per_positive: int | None
    min_conditions_per_positive: int | None
    issues: tuple[AdapterIssue, ...]
    capability_notes: tuple[str, ...]

    @property
    def evaluable(self) -> bool:
        return self.runtime_capability != RuntimeCapability.NOT_EVALUABLE

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "declared_capability": self.declared_capability.value,
            "runtime_capability": self.runtime_capability.value,
            "data_sha256": self.data_sha256,
            "source_rows": self.source_rows,
            "canonical_rows": self.canonical_rows,
            "excluded_rows": self.excluded_rows,
            "n_perturbations": self.n_perturbations,
            "n_features": self.n_features,
            "n_conditions": self.n_conditions,
            "n_donors": self.n_donors,
            "n_guides": self.n_guides,
            "n_positives": self.n_positives,
            "n_negative_pool": self.n_negative_pool,
            "min_donors_per_positive": self.min_donors_per_positive,
            "min_guides_per_positive": self.min_guides_per_positive,
            "min_conditions_per_positive": self.min_conditions_per_positive,
            "issues": [issue.to_dict() for issue in self.issues],
            "capability_notes": list(self.capability_notes),
        }


@dataclass(frozen=True)
class AdapterResult:
    """Canonical perturbation table plus its inseparable inspection report."""

    table: pd.DataFrame
    inspection: DatasetInspection


def _sha256(path: Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def _declared_capability(spec: DatasetSpec) -> DatasetCapability:
    if spec.benchmark is None:
        return DatasetCapability.DIAGNOSTIC_ONLY
    if {"condition", "donor", "guide"}.issubset(spec.mapping):
        return DatasetCapability.CONFIRMATORY_DECLARED
    return DatasetCapability.BENCHMARK_DECLARED


def _error(code: str, field: str, message: str) -> AdapterIssue:
    return AdapterIssue(code, IssueSeverity.ERROR, field, message)


def _warning(code: str, field: str, message: str) -> AdapterIssue:
    return AdapterIssue(code, IssueSeverity.WARNING, field, message)


def _empty_result(
    spec: DatasetSpec,
    issues: list[AdapterIssue],
    *,
    data_sha256: str | None = None,
    source_rows: int = 0,
) -> AdapterResult:
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
    return AdapterResult(table=pd.DataFrame(), inspection=inspection)


def _resolve_inside_root(
    spec: DatasetSpec, repo_root: Path, issues: list[AdapterIssue]
) -> Path | None:
    root = repo_root.resolve()
    resolved = (root / spec.input.path).resolve()
    if not resolved.is_relative_to(root):
        issues.append(
            _error("PATH_ESCAPE", "input.path", "resolved input path escapes the repository root")
        )
        return None
    if not resolved.is_file():
        issues.append(_error("INPUT_NOT_FOUND", "input.path", "declared input file does not exist"))
        return None
    return resolved


def _source_columns(spec: DatasetSpec) -> tuple[list[str], str | None]:
    columns = list(dict.fromkeys(spec.mapping.values()))
    positive_column = None
    if spec.benchmark and spec.benchmark.positives["source"] == "column":
        positive_column = str(spec.benchmark.positives["column"])
        if positive_column not in columns:
            columns.append(positive_column)
    return columns, positive_column


def _read_table(
    path: Path,
    input_format: str,
    source_columns: list[str],
    issues: list[AdapterIssue],
) -> pd.DataFrame | None:
    try:
        if input_format == "csv":
            header = pd.read_csv(path, nrows=0)
            missing = sorted(set(source_columns) - set(header.columns))
            if missing:
                issues.append(
                    _error(
                        "MISSING_COLUMNS",
                        "mapping",
                        f"input is missing declared columns: {', '.join(missing)}",
                    )
                )
                return None
            return pd.read_csv(path, usecols=source_columns)
        if input_format == "parquet":
            return pd.read_parquet(path, columns=source_columns)
    except Exception as exc:
        issues.append(
            _error(
                "INPUT_READ_ERROR",
                "input.path",
                f"could not read {input_format}: {type(exc).__name__}",
            )
        )
        return None
    issues.append(
        _error("UNSUPPORTED_FORMAT", "input.format", "tabular adapter requires csv or parquet")
    )
    return None


def _canonicalize_columns(
    raw: pd.DataFrame,
    spec: DatasetSpec,
    positive_column: str | None,
    issues: list[AdapterIssue],
) -> pd.DataFrame | None:
    sources = list(spec.mapping.values())
    collisions = sorted({source for source in sources if sources.count(source) > 1})
    if collisions:
        issues.append(
            _error(
                "MAPPING_COLLISION",
                "mapping",
                f"one source column maps to multiple logical fields: {', '.join(collisions)}",
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
                    "positive-set column cannot also map to a canonical signal",
                )
            )
            return None
        rename[positive_column] = "benchmark_positive"
    return raw.rename(columns=rename).copy()


def _filter_invalid_rows(
    table: pd.DataFrame, spec: DatasetSpec, issues: list[AdapterIssue]
) -> tuple[pd.DataFrame, int]:
    identity = ["perturbation"]
    numeric = []
    if spec.input.layout == "long_effects":
        identity.append("feature")
        numeric.extend(["effect", "standardized_effect"])
    else:
        numeric.extend(["magnitude", "specificity", "reproducibility"])
    identity.extend(field for field in ("condition", "donor", "guide") if field in table)
    numeric.extend(
        field
        for field in ("coherence", "target_expression", "n_guides", "n_cells")
        if field in table
    )

    valid = pd.Series(True, index=table.index)
    for field in identity:
        values = table[field]
        invalid = values.isna() | values.astype(str).str.strip().eq("")
        valid &= ~invalid
    for field in numeric:
        converted = pd.to_numeric(table[field], errors="coerce")
        invalid = converted.isna() | ~np.isfinite(converted)
        table[field] = converted
        valid &= ~invalid

    excluded = int((~valid).sum())
    if excluded:
        issues.append(
            _warning(
                "ROWS_EXCLUDED",
                "input",
                f"excluded {excluded} rows with missing or non-finite required values",
            )
        )
    return table.loc[valid].reset_index(drop=True), excluded


def _duplicate_key(spec: DatasetSpec, table: pd.DataFrame) -> list[str]:
    key = ["perturbation"]
    if spec.input.layout == "long_effects":
        key.append("feature")
    key.extend(field for field in ("condition", "donor", "guide") if field in table)
    return key


def _load_positive_set(
    spec: DatasetSpec,
    table: pd.DataFrame,
    repo_root: Path,
    issues: list[AdapterIssue],
) -> pd.Series | None:
    if spec.benchmark is None:
        return None
    positives = spec.benchmark.positives
    if positives["source"] == "column":
        positive_value = positives.get("positive_value", True)
        return table["benchmark_positive"].eq(positive_value)

    positive_path = (repo_root.resolve() / str(positives["path"])).resolve()
    if not positive_path.is_relative_to(repo_root.resolve()) or not positive_path.is_file():
        issues.append(
            _error(
                "POSITIVE_SET_NOT_FOUND",
                "benchmark.positives.path",
                "positive-set file is missing or escapes the repository root",
            )
        )
        return None
    genes = {
        line.strip()
        for line in positive_path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if not genes:
        issues.append(_error("EMPTY_POSITIVE_SET", "benchmark.positives.path", "file has no IDs"))
        return None
    observed = set(table["perturbation"].astype(str))
    missing_count = len(genes - observed)
    if missing_count:
        issues.append(
            _warning(
                "POSITIVES_NOT_OBSERVED",
                "benchmark.positives.path",
                f"{missing_count} positive IDs are absent from the canonical table",
            )
        )
    return table["perturbation"].astype(str).isin(genes)


def _minimum_unique_per_positive(
    table: pd.DataFrame, field: str, positive_mask: pd.Series | None
) -> int | None:
    if positive_mask is None or field not in table or not positive_mask.any():
        return None
    counts = table.loc[positive_mask].groupby("perturbation", observed=True)[field].nunique()
    return int(counts.min()) if not counts.empty else None


def _runtime_capability(
    *,
    has_benchmark: bool,
    n_positives: int | None,
    n_negative_pool: int | None,
    min_donors: int | None,
    min_guides: int | None,
    min_conditions: int | None,
) -> tuple[RuntimeCapability, tuple[str, ...]]:
    if not has_benchmark:
        return (
            RuntimeCapability.DIAGNOSTIC_ONLY,
            ("No independent positive benchmark is available for a confirmatory verdict.",),
        )

    benchmark_ready = (n_positives or 0) >= 8 and (n_negative_pool or 0) >= 15
    confirmatory_ready = (
        benchmark_ready
        and (min_donors or 0) >= 6
        and (min_guides or 0) >= 2
        and (min_conditions or 0) >= 2
    )
    if confirmatory_ready:
        return (
            RuntimeCapability.CONFIRMATORY_READY,
            (
                "Observed coverage passes the v1 positive, negative, donor, guide and condition gates.",
            ),
        )
    if benchmark_ready:
        missing = []
        if (min_donors or 0) < 6:
            missing.append("at least 6 donors per positive")
        if (min_guides or 0) < 2:
            missing.append("at least 2 guides per positive")
        if (min_conditions or 0) < 2:
            missing.append("at least 2 conditions per positive")
        return (
            RuntimeCapability.BENCHMARK_READY,
            (f"Benchmark coverage passes; confirmatory design still needs {', '.join(missing)}.",),
        )
    return (
        RuntimeCapability.DIAGNOSTIC_ONLY,
        (
            "Benchmark is underpowered for v1 gates: at least 8 observed positives and 15 negatives are required.",
        ),
    )


def load_tabular_dataset(spec: DatasetSpec, *, repo_root: Path | str) -> AdapterResult:
    """Load and inspect a CSV/Parquet DatasetSpec into canonical logical columns.

    Expected data limitations are returned as structured issues instead of exceptions. The adapter
    does not compute ISCI scores; its only job is to establish a trustworthy canonical boundary.
    """

    issues: list[AdapterIssue] = []
    if spec.input.layout == "anndata_effects":
        issues.append(
            _error(
                "UNSUPPORTED_LAYOUT",
                "input.layout",
                "anndata_effects requires the separate AnnData adapter",
            )
        )
        return _empty_result(spec, issues)

    root = Path(repo_root)
    input_path = _resolve_inside_root(spec, root, issues)
    if input_path is None:
        return _empty_result(spec, issues)

    data_sha256 = _sha256(input_path)
    if spec.input.sha256 is not None and data_sha256.lower() != spec.input.sha256.lower():
        issues.append(_error("HASH_MISMATCH", "input.sha256", "input SHA-256 does not match spec"))
        return _empty_result(spec, issues, data_sha256=data_sha256)

    source_columns, positive_column = _source_columns(spec)
    raw = _read_table(input_path, spec.input.format, source_columns, issues)
    if raw is None:
        return _empty_result(spec, issues, data_sha256=data_sha256)
    source_rows = len(raw)
    if source_rows == 0:
        issues.append(_error("EMPTY_INPUT", "input.path", "input table contains zero rows"))
        return _empty_result(spec, issues, data_sha256=data_sha256)

    canonical = _canonicalize_columns(raw, spec, positive_column, issues)
    if canonical is None:
        return _empty_result(spec, issues, data_sha256=data_sha256, source_rows=source_rows)
    canonical, excluded_rows = _filter_invalid_rows(canonical, spec, issues)
    if canonical.empty:
        issues.append(
            _error("NO_VALID_ROWS", "input", "no rows remain after required-value checks")
        )
        return _empty_result(spec, issues, data_sha256=data_sha256, source_rows=source_rows)

    duplicate_key = _duplicate_key(spec, canonical)
    duplicate_rows = int(canonical.duplicated(duplicate_key, keep=False).sum())
    if duplicate_rows:
        issues.append(
            _error(
                "DUPLICATE_KEYS",
                "input",
                f"{duplicate_rows} rows duplicate the canonical key {duplicate_key}",
            )
        )
        return _empty_result(spec, issues, data_sha256=data_sha256, source_rows=source_rows)

    positive_mask = _load_positive_set(spec, canonical, root, issues)
    if any(issue.severity == IssueSeverity.ERROR for issue in issues):
        return _empty_result(spec, issues, data_sha256=data_sha256, source_rows=source_rows)
    if positive_mask is not None:
        canonical["benchmark_positive"] = positive_mask.astype(bool)

    n_perturbations = int(canonical["perturbation"].nunique())
    n_features = int(canonical["feature"].nunique()) if "feature" in canonical else None
    n_conditions = int(canonical["condition"].nunique()) if "condition" in canonical else None
    n_donors = int(canonical["donor"].nunique()) if "donor" in canonical else None
    n_guides = int(canonical["guide"].nunique()) if "guide" in canonical else None
    n_positives = (
        int(canonical.loc[positive_mask, "perturbation"].nunique())
        if positive_mask is not None
        else None
    )
    n_negative_pool = n_perturbations - n_positives if n_positives is not None else None
    min_donors = _minimum_unique_per_positive(canonical, "donor", positive_mask)
    min_guides = _minimum_unique_per_positive(canonical, "guide", positive_mask)
    min_conditions = _minimum_unique_per_positive(canonical, "condition", positive_mask)
    runtime_capability, capability_notes = _runtime_capability(
        has_benchmark=positive_mask is not None,
        n_positives=n_positives,
        n_negative_pool=n_negative_pool,
        min_donors=min_donors,
        min_guides=min_guides,
        min_conditions=min_conditions,
    )

    inspection = DatasetInspection(
        dataset_id=spec.dataset.id,
        declared_capability=_declared_capability(spec),
        runtime_capability=runtime_capability,
        data_sha256=data_sha256,
        source_rows=source_rows,
        canonical_rows=len(canonical),
        excluded_rows=excluded_rows,
        n_perturbations=n_perturbations,
        n_features=n_features,
        n_conditions=n_conditions,
        n_donors=n_donors,
        n_guides=n_guides,
        n_positives=n_positives,
        n_negative_pool=n_negative_pool,
        min_donors_per_positive=min_donors,
        min_guides_per_positive=min_guides,
        min_conditions_per_positive=min_conditions,
        issues=tuple(issues),
        capability_notes=capability_notes,
    )
    return AdapterResult(table=canonical, inspection=inspection)
