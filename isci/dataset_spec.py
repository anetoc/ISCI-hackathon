"""Versioned, portable input contract for bringing Perturb-seq datasets to ISCI.

The spec validator is deliberately separate from dataset loading. It validates the public
configuration boundary without opening a potentially large or restricted data file. Adapters can
therefore trust a parsed :class:`DatasetSpec` and focus on translating data into canonical ISCI
tables.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import re
from typing import Any

import yaml


class DatasetCapability(StrEnum):
    """Strongest analysis tier declared by a syntactically valid spec."""

    CONFIRMATORY_DECLARED = "CONFIRMATORY_DECLARED"
    BENCHMARK_DECLARED = "BENCHMARK_DECLARED"
    PREPROCESSING_DECLARED = "PREPROCESSING_DECLARED"
    DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class ValidationIssue:
    """Stable machine-readable validation error returned at the config boundary."""

    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class SpecValidationReport:
    """Validation result that never silently upgrades scientific capability."""

    valid: bool
    capability: DatasetCapability
    issues: tuple[ValidationIssue, ...]
    capability_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "capability": self.capability.value,
            "issues": [issue.to_dict() for issue in self.issues],
            "capability_notes": list(self.capability_notes),
        }


class DatasetSpecError(ValueError):
    """Raised by ``load_dataset_spec`` when the public contract is invalid."""

    def __init__(self, report: SpecValidationReport):
        self.report = report
        summary = "; ".join(f"{issue.path}: {issue.message}" for issue in report.issues)
        super().__init__(summary or "Invalid DatasetSpec")


@dataclass(frozen=True)
class DatasetMetadata:
    id: str
    label: str
    organism: str
    cell_system: str
    perturbation_modality: str
    description: str | None = None


@dataclass(frozen=True)
class DatasetInput:
    path: str
    format: str
    layout: str
    sha256: str | None
    layers: dict[str, str]


@dataclass(frozen=True)
class AnalysisSettings:
    axes_path: str
    primary_signal: str
    sensitivity_signal: str
    leave_one_marker_out: bool
    n_bootstrap: int
    seed: int


@dataclass(frozen=True)
class BenchmarkSettings:
    positives: dict[str, Any]
    negatives: dict[str, Any]
    expected_verdict: str | None


@dataclass(frozen=True)
class ProvenanceSettings:
    source_url: str
    citation: str
    license: str
    data_classification: str
    redistributable: bool


@dataclass(frozen=True)
class CellPreprocessingSettings:
    source: dict[str, Any]
    control: dict[str, Any]
    normalization: str
    contrast: str
    standardization: str
    min_cells_per_stratum: int
    min_replicates: int
    multi_guide_policy: str
    perturbation_transform: str


@dataclass(frozen=True)
class DatasetSpec:
    """Typed DatasetSpec v1 consumed by future adapters and notebook interfaces."""

    schema_version: int
    dataset: DatasetMetadata
    input: DatasetInput
    mapping: dict[str, str]
    analysis: AnalysisSettings
    benchmark: BenchmarkSettings | None
    provenance: ProvenanceSettings
    preprocessing: CellPreprocessingSettings | None = None
    source_path: Path | None = None

    def resolve_path(self, relative_path: str, repo_root: Path | str) -> Path:
        """Resolve a contract path against the repository root, never the current shell state."""

        return Path(repo_root).resolve() / relative_path


_TOP_LEVEL_FIELDS = {
    "schema_version",
    "dataset",
    "input",
    "mapping",
    "analysis",
    "preprocessing",
    "benchmark",
    "provenance",
}
_DATASET_FIELDS = {
    "id",
    "label",
    "description",
    "organism",
    "cell_system",
    "perturbation_modality",
}
_INPUT_FIELDS = {"path", "format", "layout", "sha256", "layers"}
_LAYER_FIELDS = {"effect", "standardized_effect"}
_MAPPING_FIELDS = {
    "perturbation",
    "feature",
    "effect",
    "standardized_effect",
    "condition",
    "donor",
    "guide",
    "guide_count",
    "replicate",
    "control",
    "magnitude",
    "specificity",
    "reproducibility",
    "coherence",
    "target_expression",
    "n_guides",
    "n_cells",
}
_ANALYSIS_FIELDS = {
    "axes_path",
    "primary_signal",
    "sensitivity_signal",
    "leave_one_marker_out",
    "n_bootstrap",
    "seed",
}
_PROVENANCE_FIELDS = {
    "source_url",
    "citation",
    "license",
    "data_classification",
    "redistributable",
}
_PERTURBATION_MODALITIES = {"CRISPR_KO", "CRISPRI", "CRISPRA", "RNAI", "OTHER"}
_INPUT_FORMATS = {"h5ad", "csv", "parquet"}
_LAYOUTS = {"anndata_cells", "anndata_effects", "long_effects", "controller_features"}
_CLASSIFICATIONS = {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"}
_VERDICTS = {"PASS", "FAIL", "NULL", "NOT_EVALUABLE"}
_MATCH_FIELDS = {"target_expression", "n_guides", "n_cells", "condition"}
_PREPROCESSING_FIELDS = {
    "source",
    "control",
    "normalization",
    "contrast",
    "standardization",
    "min_cells_per_stratum",
    "min_replicates",
    "multi_guide_policy",
    "perturbation_transform",
}


def _add(issues: list[ValidationIssue], code: str, path: str, message: str) -> None:
    issues.append(ValidationIssue(code=code, path=path, message=message))


def _mapping(value: Any, path: str, issues: list[ValidationIssue]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _add(issues, "INVALID_TYPE", path, "must be an object")
        return {}
    return value


def _unknown_fields(
    value: dict[str, Any], allowed: set[str], path: str, issues: list[ValidationIssue]
) -> None:
    for key in sorted(set(value) - allowed):
        _add(issues, "UNKNOWN_FIELD", f"{path}.{key}", "field is not part of DatasetSpec v1")


def _required_string(
    value: dict[str, Any], key: str, path: str, issues: list[ValidationIssue]
) -> str | None:
    field_path = f"{path}.{key}"
    if key not in value:
        _add(issues, "REQUIRED_FIELD", field_path, "field is required")
        return None
    candidate = value[key]
    if not isinstance(candidate, str) or not candidate.strip():
        _add(issues, "INVALID_TYPE", field_path, "must be a non-empty string")
        return None
    return candidate


def _portable_path(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    if not isinstance(value, str) or not value.strip():
        _add(issues, "INVALID_TYPE", path, "must be a non-empty relative path")
        return False
    is_windows_absolute = len(value) >= 3 and value[1] == ":" and value[2] in {"/", "\\"}
    if Path(value).is_absolute() or is_windows_absolute:
        _add(issues, "NON_PORTABLE_PATH", path, "absolute paths are not allowed")
        return False
    if ".." in value.replace("\\", "/").split("/"):
        _add(issues, "PATH_TRAVERSAL", path, "repository-relative paths cannot contain '..'")
        return False
    return True


def _infer_repo_root(spec_path: Path) -> Path:
    for candidate in (spec_path.parent, *spec_path.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    return spec_path.parent


def _validate_required_paths(
    raw: dict[str, Any], repo_root: Path, issues: list[ValidationIssue]
) -> None:
    input_block = raw.get("input") if isinstance(raw.get("input"), dict) else {}
    analysis = raw.get("analysis") if isinstance(raw.get("analysis"), dict) else {}
    benchmark = raw.get("benchmark") if isinstance(raw.get("benchmark"), dict) else {}
    paths: list[tuple[str, Any]] = [
        ("input.path", input_block.get("path")),
        ("analysis.axes_path", analysis.get("axes_path")),
    ]
    positives = benchmark.get("positives", {})
    positives = positives if isinstance(positives, dict) else {}
    if positives.get("source") == "file":
        paths.append(("benchmark.positives.path", positives.get("path")))
    for field_path, value in paths:
        if isinstance(value, str) and not (repo_root / value).exists():
            _add(issues, "PATH_NOT_FOUND", field_path, f"does not exist under {repo_root}")


def _validate_benchmark(
    benchmark: Any, mapping: dict[str, Any], issues: list[ValidationIssue]
) -> bool:
    if benchmark is None:
        return False
    block = _mapping(benchmark, "benchmark", issues)
    _unknown_fields(block, {"positives", "negatives", "expected_verdict"}, "benchmark", issues)

    positives = _mapping(block.get("positives"), "benchmark.positives", issues)
    source = _required_string(positives, "source", "benchmark.positives", issues)
    if source == "file":
        _unknown_fields(positives, {"source", "path"}, "benchmark.positives", issues)
        positive_path = _required_string(positives, "path", "benchmark.positives", issues)
        if positive_path is not None:
            _portable_path(positive_path, "benchmark.positives.path", issues)
    elif source == "column":
        _unknown_fields(
            positives,
            {"source", "column", "positive_value"},
            "benchmark.positives",
            issues,
        )
        _required_string(positives, "column", "benchmark.positives", issues)
    elif source is not None:
        _add(
            issues,
            "INVALID_VALUE",
            "benchmark.positives.source",
            "must be 'file' or 'column'",
        )

    negatives = _mapping(block.get("negatives"), "benchmark.negatives", issues)
    _unknown_fields(negatives, {"strategy", "match_on"}, "benchmark.negatives", issues)
    strategy = _required_string(negatives, "strategy", "benchmark.negatives", issues)
    if strategy is not None and strategy != "expression_matched":
        _add(
            issues,
            "BENCHMARK_CONTRACT",
            "benchmark.negatives.strategy",
            "ISCI v1 requires expression_matched negatives",
        )
    match_on = negatives.get("match_on")
    if not isinstance(match_on, list) or not all(isinstance(item, str) for item in match_on):
        _add(
            issues,
            "INVALID_TYPE",
            "benchmark.negatives.match_on",
            "must be a list of logical mapping fields",
        )
    else:
        missing_match = _MATCH_FIELDS - set(match_on)
        if missing_match:
            _add(
                issues,
                "BENCHMARK_CONTRACT",
                "benchmark.negatives.match_on",
                "must include target_expression, n_guides, n_cells and condition",
            )
        if len(match_on) != len(set(match_on)):
            _add(
                issues,
                "BENCHMARK_CONTRACT",
                "benchmark.negatives.match_on",
                "must not contain duplicate fields",
            )
        undeclared = set(match_on) - set(mapping)
        if undeclared:
            _add(
                issues,
                "BENCHMARK_CONTRACT",
                "mapping",
                f"missing columns declared in match_on: {', '.join(sorted(undeclared))}",
            )

    verdict = block.get("expected_verdict")
    if verdict is not None and verdict not in _VERDICTS:
        _add(
            issues,
            "INVALID_VALUE",
            "benchmark.expected_verdict",
            "must be PASS, FAIL, NULL, NOT_EVALUABLE or null",
        )
    return True


def _validate_cell_preprocessing(
    value: Any, layout: str | None, issues: list[ValidationIssue]
) -> None:
    if layout != "anndata_cells":
        if value is not None:
            _add(
                issues,
                "INCOMPATIBLE_PREPROCESSING",
                "preprocessing",
                "is only valid for input.layout=anndata_cells",
            )
        return
    if value is None:
        _add(issues, "REQUIRED_FIELD", "preprocessing", "required by anndata_cells")
        return

    block = _mapping(value, "preprocessing", issues)
    _unknown_fields(block, _PREPROCESSING_FIELDS, "preprocessing", issues)
    source = _mapping(block.get("source"), "preprocessing.source", issues)
    _unknown_fields(source, {"location", "layer", "kind"}, "preprocessing.source", issues)
    location = _required_string(source, "location", "preprocessing.source", issues)
    kind = _required_string(source, "kind", "preprocessing.source", issues)
    if location not in {None, "X", "layer"}:
        _add(issues, "INVALID_VALUE", "preprocessing.source.location", "must be X or layer")
    if location == "layer":
        _required_string(source, "layer", "preprocessing.source", issues)
    elif "layer" in source:
        _add(
            issues,
            "INVALID_VALUE",
            "preprocessing.source.layer",
            "must be omitted when location is X",
        )
    if kind not in {None, "raw_counts", "normalized"}:
        _add(
            issues,
            "INVALID_VALUE",
            "preprocessing.source.kind",
            "must be raw_counts or normalized",
        )

    control = _mapping(block.get("control"), "preprocessing.control", issues)
    _unknown_fields(control, {"column", "labels", "match_on"}, "preprocessing.control", issues)
    _required_string(control, "column", "preprocessing.control", issues)
    labels = control.get("labels")
    if (
        not isinstance(labels, list)
        or not labels
        or not all(isinstance(label, str) and label.strip() for label in labels)
        or len(labels) != len(set(labels))
    ):
        _add(
            issues,
            "INVALID_VALUE",
            "preprocessing.control.labels",
            "must be a non-empty list of unique control labels",
        )
    match_on = control.get("match_on")
    allowed_match_fields = {"condition", "donor", "replicate"}
    if (
        not isinstance(match_on, list)
        or not all(isinstance(field, str) for field in match_on)
        or len(match_on) != len(set(match_on))
    ):
        _add(
            issues,
            "INVALID_VALUE",
            "preprocessing.control.match_on",
            "must be a list of unique logical stratum fields",
        )
    else:
        unsupported = set(match_on) - allowed_match_fields
        if unsupported:
            _add(
                issues,
                "INVALID_VALUE",
                "preprocessing.control.match_on",
                f"unsupported fields: {', '.join(sorted(unsupported))}",
            )

    expected_strings = {
        "normalization": {"log1p_cpm", "already_normalized"},
        "contrast": {"pseudobulk_difference"},
        "standardization": {"gene_wise_zscore_within_condition"},
        "multi_guide_policy": {"exclude", "not_applicable_arrayed"},
        "perturbation_transform": {"identity", "strip_trailing_guide_number"},
    }
    for field, allowed in expected_strings.items():
        observed = _required_string(block, field, "preprocessing", issues)
        if observed is not None and observed not in allowed:
            _add(
                issues,
                "INVALID_VALUE",
                f"preprocessing.{field}",
                f"must be one of {sorted(allowed)}",
            )
    normalization = block.get("normalization")
    if kind == "raw_counts" and normalization != "log1p_cpm":
        _add(
            issues,
            "INCOMPATIBLE_NORMALIZATION",
            "preprocessing.normalization",
            "raw_counts requires log1p_cpm",
        )
    if kind == "normalized" and normalization != "already_normalized":
        _add(
            issues,
            "INCOMPATIBLE_NORMALIZATION",
            "preprocessing.normalization",
            "normalized input requires already_normalized",
        )
    for field, minimum in (("min_cells_per_stratum", 10), ("min_replicates", 2)):
        observed = block.get(field)
        if isinstance(observed, bool) or not isinstance(observed, int) or observed < minimum:
            _add(
                issues,
                "INVALID_VALUE",
                f"preprocessing.{field}",
                f"must be an integer >= {minimum}",
            )


def validate_dataset_spec(
    raw: Any,
    *,
    repo_root: Path | str | None = None,
    check_paths: bool = False,
) -> SpecValidationReport:
    """Validate a DatasetSpec mapping and infer its strongest declared capability.

    This function does not open the dataset. Structural validation of H5AD/table columns belongs
    to the adapter boundary and may downgrade a valid declaration to ``NOT_EVALUABLE``.
    """

    issues: list[ValidationIssue] = []
    root = _mapping(raw, "$", issues)
    _unknown_fields(root, _TOP_LEVEL_FIELDS, "$", issues)

    if root.get("schema_version") != 1:
        _add(issues, "UNSUPPORTED_VERSION", "schema_version", "DatasetSpec v1 is required")

    dataset = _mapping(root.get("dataset"), "dataset", issues)
    _unknown_fields(dataset, _DATASET_FIELDS, "dataset", issues)
    dataset_id = _required_string(dataset, "id", "dataset", issues)
    for field in ("label", "organism", "cell_system", "perturbation_modality"):
        _required_string(dataset, field, "dataset", issues)
    if dataset_id is not None:
        if re.fullmatch(r"[a-z][a-z0-9_]{2,63}", dataset_id) is None:
            _add(
                issues,
                "INVALID_VALUE",
                "dataset.id",
                "must match ^[a-z][a-z0-9_]{2,63}$",
            )
    modality = dataset.get("perturbation_modality")
    if modality is not None and modality not in _PERTURBATION_MODALITIES:
        _add(
            issues,
            "INVALID_VALUE",
            "dataset.perturbation_modality",
            f"must be one of {sorted(_PERTURBATION_MODALITIES)}",
        )

    input_block = _mapping(root.get("input"), "input", issues)
    _unknown_fields(input_block, _INPUT_FIELDS, "input", issues)
    input_path = _required_string(input_block, "path", "input", issues)
    if input_path is not None:
        _portable_path(input_path, "input.path", issues)
    input_format = _required_string(input_block, "format", "input", issues)
    layout = _required_string(input_block, "layout", "input", issues)
    if input_format is not None and input_format not in _INPUT_FORMATS:
        _add(issues, "INVALID_VALUE", "input.format", f"must be one of {sorted(_INPUT_FORMATS)}")
    if layout is not None and layout not in _LAYOUTS:
        _add(issues, "INVALID_VALUE", "input.layout", f"must be one of {sorted(_LAYOUTS)}")
    if layout in {"anndata_cells", "anndata_effects"} and input_format != "h5ad":
        _add(
            issues,
            "INCOMPATIBLE_LAYOUT",
            "input.format",
            f"{layout} requires h5ad",
        )
    if layout in {"long_effects", "controller_features"} and input_format not in {
        "csv",
        "parquet",
    }:
        _add(
            issues,
            "INCOMPATIBLE_LAYOUT",
            "input.format",
            f"{layout} requires csv or parquet",
        )
    sha256 = input_block.get("sha256")
    if sha256 is not None and (
        not isinstance(sha256, str)
        or len(sha256) != 64
        or any(char not in "0123456789abcdefABCDEF" for char in sha256)
    ):
        _add(issues, "INVALID_VALUE", "input.sha256", "must be a 64-character SHA-256")
    layers = _mapping(input_block.get("layers", {}), "input.layers", issues)
    _unknown_fields(layers, _LAYER_FIELDS, "input.layers", issues)
    if layout == "anndata_effects":
        for field in ("effect", "standardized_effect"):
            _required_string(layers, field, "input.layers", issues)

    mapping = _mapping(root.get("mapping"), "mapping", issues)
    _unknown_fields(mapping, _MAPPING_FIELDS, "mapping", issues)
    for key, value in mapping.items():
        if not isinstance(value, str) or not value.strip():
            _add(issues, "INVALID_TYPE", f"mapping.{key}", "must be a non-empty column name")
    layout_requirements = {
        "anndata_cells": {"perturbation", "guide", "replicate"},
        "anndata_effects": {"perturbation"},
        "long_effects": {"perturbation", "feature", "effect", "standardized_effect"},
        "controller_features": {
            "perturbation",
            "magnitude",
            "specificity",
            "reproducibility",
        },
    }
    for field in sorted(layout_requirements.get(layout, set()) - set(mapping)):
        _add(issues, "REQUIRED_FIELD", f"mapping.{field}", f"required by {layout}")

    _validate_cell_preprocessing(root.get("preprocessing"), layout, issues)
    if layout == "anndata_cells" and isinstance(root.get("preprocessing"), dict):
        preprocessing = root["preprocessing"]
        policy = preprocessing.get("multi_guide_policy")
        if policy == "exclude" and "guide_count" not in mapping:
            _add(
                issues,
                "REQUIRED_FIELD",
                "mapping.guide_count",
                "required when multi_guide_policy=exclude",
            )
        if policy == "not_applicable_arrayed" and "guide_count" in mapping:
            _add(
                issues,
                "INCOMPATIBLE_MAPPING",
                "mapping.guide_count",
                "must be omitted for an explicitly arrayed single-guide design",
            )
        control = preprocessing.get("control")
        if isinstance(control, dict) and isinstance(control.get("match_on"), list):
            undeclared = set(control["match_on"]) - set(mapping)
            if undeclared:
                _add(
                    issues,
                    "CONTROL_MATCH_CONTRACT",
                    "preprocessing.control.match_on",
                    f"fields are not mapped: {', '.join(sorted(undeclared))}",
                )

    analysis = _mapping(root.get("analysis"), "analysis", issues)
    _unknown_fields(analysis, _ANALYSIS_FIELDS, "analysis", issues)
    axes_path = _required_string(analysis, "axes_path", "analysis", issues)
    if axes_path is not None:
        _portable_path(axes_path, "analysis.axes_path", issues)
    if analysis.get("primary_signal") != "standardized_effect":
        _add(
            issues,
            "INVALID_VALUE",
            "analysis.primary_signal",
            "DatasetSpec v1 freezes standardized_effect as primary",
        )
    if analysis.get("sensitivity_signal") != "effect":
        _add(
            issues,
            "INVALID_VALUE",
            "analysis.sensitivity_signal",
            "DatasetSpec v1 freezes effect as sensitivity",
        )
    if analysis.get("leave_one_marker_out") is not True:
        _add(
            issues,
            "LOO_REQUIRED",
            "analysis.leave_one_marker_out",
            "must be true to prevent axis-marker leakage",
        )
    n_bootstrap = analysis.get("n_bootstrap")
    if isinstance(n_bootstrap, bool) or not isinstance(n_bootstrap, int) or n_bootstrap < 100:
        _add(issues, "INVALID_VALUE", "analysis.n_bootstrap", "must be an integer >= 100")
    seed = analysis.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        _add(issues, "INVALID_VALUE", "analysis.seed", "must be an integer >= 0")

    has_benchmark = _validate_benchmark(root.get("benchmark"), mapping, issues)
    if layout == "anndata_cells" and root.get("benchmark") is not None:
        _add(
            issues,
            "PREPROCESSING_BOUNDARY",
            "benchmark",
            "benchmark belongs to the generated effect DatasetSpec, not cell-level preprocessing",
        )

    provenance = _mapping(root.get("provenance"), "provenance", issues)
    _unknown_fields(provenance, _PROVENANCE_FIELDS, "provenance", issues)
    for field in ("source_url", "citation", "license", "data_classification"):
        _required_string(provenance, field, "provenance", issues)
    source_url = provenance.get("source_url")
    if isinstance(source_url, str) and not source_url.startswith(("https://", "http://")):
        _add(issues, "INVALID_VALUE", "provenance.source_url", "must be an HTTP(S) URL")
    classification = provenance.get("data_classification")
    if classification is not None and classification not in _CLASSIFICATIONS:
        _add(
            issues,
            "INVALID_VALUE",
            "provenance.data_classification",
            f"must be one of {sorted(_CLASSIFICATIONS)}",
        )
    if not isinstance(provenance.get("redistributable"), bool):
        _add(issues, "INVALID_TYPE", "provenance.redistributable", "must be a boolean")

    if check_paths and repo_root is not None:
        _validate_required_paths(root, Path(repo_root).resolve(), issues)

    if issues:
        capability = DatasetCapability.NOT_EVALUABLE
        notes = ("Fix the contract errors before any data are opened.",)
    elif layout == "anndata_cells":
        capability = DatasetCapability.PREPROCESSING_DECLARED
        notes = (
            "Cell-level preprocessing is declared but no effect matrix or biological verdict exists.",
        )
    elif has_benchmark and {"condition", "donor", "guide"}.issubset(mapping):
        capability = DatasetCapability.CONFIRMATORY_DECLARED
        notes = (
            "Guide- and donor-resolved reproducibility is declared.",
            "The benchmark uses expression-matched negatives and LOO axes.",
        )
    elif has_benchmark:
        capability = DatasetCapability.BENCHMARK_DECLARED
        missing = sorted({"condition", "donor", "guide"} - set(mapping))
        notes = (f"Benchmark is declared, but full reproducibility lacks: {', '.join(missing)}.",)
    else:
        capability = DatasetCapability.DIAGNOSTIC_ONLY
        notes = (
            "No independent positive-set benchmark is declared; do not issue a confirmatory PASS.",
        )

    return SpecValidationReport(
        valid=not issues,
        capability=capability,
        issues=tuple(issues),
        capability_notes=notes,
    )


def load_dataset_spec(
    path: Path | str,
    *,
    repo_root: Path | str | None = None,
    check_paths: bool = False,
) -> DatasetSpec:
    """Load YAML into a typed DatasetSpec or raise ``DatasetSpecError``."""

    source_path = Path(path).resolve()
    raw = yaml.safe_load(source_path.read_text())
    effective_root = Path(repo_root).resolve() if repo_root else _infer_repo_root(source_path)
    report = validate_dataset_spec(raw, repo_root=effective_root, check_paths=check_paths)
    if not report.valid:
        raise DatasetSpecError(report)

    dataset = raw["dataset"]
    input_block = raw["input"]
    analysis = raw["analysis"]
    benchmark = raw.get("benchmark")
    preprocessing = raw.get("preprocessing")
    provenance = raw["provenance"]
    return DatasetSpec(
        schema_version=raw["schema_version"],
        dataset=DatasetMetadata(
            id=dataset["id"],
            label=dataset["label"],
            organism=dataset["organism"],
            cell_system=dataset["cell_system"],
            perturbation_modality=dataset["perturbation_modality"],
            description=dataset.get("description"),
        ),
        input=DatasetInput(
            path=input_block["path"],
            format=input_block["format"],
            layout=input_block["layout"],
            sha256=input_block.get("sha256"),
            layers=dict(input_block.get("layers", {})),
        ),
        mapping=dict(raw["mapping"]),
        analysis=AnalysisSettings(
            axes_path=analysis["axes_path"],
            primary_signal=analysis["primary_signal"],
            sensitivity_signal=analysis["sensitivity_signal"],
            leave_one_marker_out=analysis["leave_one_marker_out"],
            n_bootstrap=analysis["n_bootstrap"],
            seed=analysis["seed"],
        ),
        benchmark=(
            BenchmarkSettings(
                positives=dict(benchmark["positives"]),
                negatives={
                    **benchmark["negatives"],
                    "match_on": tuple(benchmark["negatives"]["match_on"]),
                },
                expected_verdict=benchmark.get("expected_verdict"),
            )
            if benchmark is not None
            else None
        ),
        provenance=ProvenanceSettings(
            source_url=provenance["source_url"],
            citation=provenance["citation"],
            license=provenance["license"],
            data_classification=provenance["data_classification"],
            redistributable=provenance["redistributable"],
        ),
        preprocessing=(
            CellPreprocessingSettings(
                source=dict(preprocessing["source"]),
                control={
                    **preprocessing["control"],
                    "labels": tuple(preprocessing["control"]["labels"]),
                    "match_on": tuple(preprocessing["control"]["match_on"]),
                },
                normalization=preprocessing["normalization"],
                contrast=preprocessing["contrast"],
                standardization=preprocessing["standardization"],
                min_cells_per_stratum=preprocessing["min_cells_per_stratum"],
                min_replicates=preprocessing["min_replicates"],
                multi_guide_policy=preprocessing["multi_guide_policy"],
                perturbation_transform=preprocessing["perturbation_transform"],
            )
            if preprocessing is not None
            else None
        ),
        source_path=source_path,
    )
