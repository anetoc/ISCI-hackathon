"""Command-line boundary for validating and inspecting external ISCI datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

import yaml

from isci.adapters import RuntimeCapability, inspect_anndata_dataset, load_tabular_dataset
from isci.analysis_runner import run_dataset
from isci.dataset_spec import DatasetSpecError, load_dataset_spec, validate_dataset_spec


EXIT_SUCCESS = 0
EXIT_INVALID_SPEC = 2
EXIT_NOT_EVALUABLE = 3


def _repo_root(spec_path: Path, explicit_root: str | None) -> Path:
    """Find a stable repository root instead of depending on the caller's shell directory."""

    if explicit_root:
        return Path(explicit_root).resolve()
    resolved = spec_path.resolve()
    for candidate in (resolved.parent, *resolved.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    return resolved.parent


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _write_json(path: str, payload: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _config_error(command: str, code: str, message: str) -> dict[str, Any]:
    """Return one predictable error shape for file, YAML and contract failures."""

    return {
        "command": command,
        "ok": False,
        "error": {"code": code, "message": message},
    }


def _load_raw_yaml(path: Path, command: str) -> tuple[Any | None, dict[str, Any] | None]:
    try:
        return yaml.safe_load(path.read_text()), None
    except FileNotFoundError:
        return None, _config_error(command, "SPEC_NOT_FOUND", "DatasetSpec file does not exist")
    except yaml.YAMLError as exc:
        return None, _config_error(command, "INVALID_YAML", type(exc).__name__)
    except OSError as exc:
        return None, _config_error(command, "SPEC_READ_ERROR", type(exc).__name__)


def _validate(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec)
    raw, error = _load_raw_yaml(spec_path, "validate")
    if error is not None:
        _print_json(error)
        return EXIT_INVALID_SPEC

    root = _repo_root(spec_path, args.repo_root)
    report = validate_dataset_spec(raw, repo_root=root, check_paths=not args.structure_only)
    payload = {
        "command": "validate",
        "ok": report.valid,
        "report": report.to_dict(),
    }
    _print_json(payload)
    return EXIT_SUCCESS if report.valid else EXIT_INVALID_SPEC


def _save_canonical(path: str, table) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.suffix.lower() == ".csv":
        table.to_csv(destination, index=False)
        return
    if destination.suffix.lower() == ".parquet":
        table.to_parquet(destination, index=False)
        return
    raise ValueError("canonical output must end in .csv or .parquet")


def _inspect(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec)
    root = _repo_root(spec_path, args.repo_root)
    try:
        spec = load_dataset_spec(spec_path, repo_root=root, check_paths=True)
    except FileNotFoundError:
        _print_json(_config_error("inspect", "SPEC_NOT_FOUND", "DatasetSpec file does not exist"))
        return EXIT_INVALID_SPEC
    except yaml.YAMLError as exc:
        _print_json(_config_error("inspect", "INVALID_YAML", type(exc).__name__))
        return EXIT_INVALID_SPEC
    except DatasetSpecError as exc:
        payload = {
            "command": "inspect",
            "ok": False,
            "error": {"code": "INVALID_SPEC", "message": "DatasetSpec validation failed"},
            "report": exc.report.to_dict(),
        }
        _print_json(payload)
        return EXIT_INVALID_SPEC

    if spec.input.layout == "anndata_effects":
        result = inspect_anndata_dataset(
            spec,
            repo_root=root,
            scan_values=args.scan_values,
            block_rows=args.block_rows,
        )
        adapter_name = "anndata_effects"
        adapter_details = {
            "matrix_shape": list(result.matrix_shape) if result.matrix_shape else None,
            "effect_layer": result.effect_layer,
            "standardized_effect_layer": result.standardized_effect_layer,
            "values_scanned": result.values_scanned,
            "invalid_effect_values": result.invalid_effect_values,
        }
    else:
        result = load_tabular_dataset(spec, repo_root=root)
        adapter_name = "tabular"
        adapter_details = None
    inspection = result.inspection.to_dict()
    payload = {
        "command": "inspect",
        "ok": result.inspection.evaluable,
        "adapter": adapter_name,
        "inspection": inspection,
        "canonical_columns": list(result.table.columns),
    }
    if adapter_details is not None:
        payload["adapter_details"] = adapter_details
    if spec.input.layout == "anndata_effects" and args.canonical_output:
        payload = _config_error(
            "inspect",
            "STREAM_REQUIRED",
            "H5AD effects must be consumed with iter_anndata_effect_blocks; inspect does not materialize them",
        )
        _print_json(payload)
        return EXIT_INVALID_SPEC
    if args.canonical_output and Path(args.canonical_output).suffix.lower() not in {
        ".csv",
        ".parquet",
    }:
        payload = _config_error(
            "inspect", "INVALID_OUTPUT_FORMAT", "canonical output must end in .csv or .parquet"
        )
        _print_json(payload)
        return EXIT_INVALID_SPEC
    try:
        if args.report:
            _write_json(args.report, payload)
        if args.canonical_output and result.inspection.evaluable:
            _save_canonical(args.canonical_output, result.table)
    except OSError as exc:
        payload = _config_error("inspect", "OUTPUT_WRITE_ERROR", type(exc).__name__)
        _print_json(payload)
        return EXIT_INVALID_SPEC
    _print_json(payload)
    if result.inspection.runtime_capability == RuntimeCapability.NOT_EVALUABLE:
        return EXIT_NOT_EVALUABLE
    return EXIT_SUCCESS


def _run(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec)
    root = _repo_root(spec_path, args.repo_root)
    try:
        spec = load_dataset_spec(spec_path, repo_root=root, check_paths=True)
    except FileNotFoundError:
        _print_json(_config_error("run", "SPEC_NOT_FOUND", "DatasetSpec file does not exist"))
        return EXIT_INVALID_SPEC
    except yaml.YAMLError as exc:
        _print_json(_config_error("run", "INVALID_YAML", type(exc).__name__))
        return EXIT_INVALID_SPEC
    except DatasetSpecError as exc:
        payload = {
            "command": "run",
            "ok": False,
            "error": {"code": "INVALID_SPEC", "message": "DatasetSpec validation failed"},
            "report": exc.report.to_dict(),
        }
        _print_json(payload)
        return EXIT_INVALID_SPEC

    output_dir = Path(args.output_dir) if args.output_dir else root / "outputs" / spec.dataset.id
    result = run_dataset(spec, repo_root=root, output_dir=output_dir)
    report_path = output_dir / "analysis_report.json"
    report = json.loads(report_path.read_text()) if report_path.is_file() else result.report
    payload = {
        "command": "run",
        "ok": result.completed,
        "status": result.status,
        "biological_verdict": result.biological_verdict,
        "report": report,
    }
    _print_json(payload)
    return EXIT_SUCCESS if result.completed else EXIT_NOT_EVALUABLE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="isci",
        description="Validate and inspect Perturb-seq datasets against DatasetSpec v1.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="validate the DatasetSpec contract and declared paths"
    )
    validate_parser.add_argument("spec", help="path to DatasetSpec YAML")
    validate_parser.add_argument(
        "--repo-root", help="repository root for resolving contract-relative paths"
    )
    validate_parser.add_argument(
        "--structure-only",
        action="store_true",
        help="validate structure without requiring data files to exist",
    )
    validate_parser.set_defaults(handler=_validate)

    inspect_parser = subparsers.add_parser(
        "inspect", help="open a tabular dataset and infer its observed capability"
    )
    inspect_parser.add_argument("spec", help="path to DatasetSpec YAML")
    inspect_parser.add_argument(
        "--repo-root", help="repository root for resolving contract-relative paths"
    )
    inspect_parser.add_argument("--report", help="optional JSON inspection report output")
    inspect_parser.add_argument(
        "--canonical-output", help="optional canonical .csv or .parquet output"
    )
    inspect_parser.add_argument(
        "--scan-values",
        action="store_true",
        help="scan both H5AD effect layers blockwise for non-finite values",
    )
    inspect_parser.add_argument(
        "--block-rows",
        type=int,
        default=64,
        help="H5AD observation rows per scan block (default: 64)",
    )
    inspect_parser.set_defaults(handler=_inspect)

    run_parser = subparsers.add_parser(
        "run", help="extract and rank a tabular dataset with the frozen conditional method"
    )
    run_parser.add_argument("spec", help="path to DatasetSpec YAML")
    run_parser.add_argument(
        "--repo-root", help="repository root for resolving contract-relative paths"
    )
    run_parser.add_argument(
        "--output-dir",
        help="output directory (default: outputs/<dataset_id> under the repository root)",
    )
    run_parser.set_defaults(handler=_run)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a stable process exit code for notebooks and automation."""

    args = build_parser().parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":  # pragma: no cover - exercised through the installed command.
    raise SystemExit(main())
