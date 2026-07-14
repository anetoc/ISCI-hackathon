#!/usr/bin/env python3
"""Run the frozen CRISPRitz S0 installation smoke twice on disposable Linux."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_OUTPUTS = {
    "targets": "emx1.hg38.targets.txt",
    "profile": "emx1.hg38.profile.xls",
    "extended_profile": "emx1.hg38.extended_profile.xls",
}


def sha256(path: Path) -> str:
    """Hash inputs and outputs in bounded chunks for the execution record."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_target_rows(path: Path) -> list[str]:
    """Sort non-empty target rows so CRISPRitz output order cannot fake a mismatch."""

    return sorted(line for line in path.read_text(errors="replace").splitlines() if line.strip())


def parse_peak_rss_kib(resource_log: Path) -> int | None:
    """Extract GNU time's child-process peak RSS while preserving its raw report."""

    prefix = "Maximum resident set size (kbytes):"
    for line in resource_log.read_text(errors="replace").splitlines():
        if line.strip().startswith(prefix):
            return int(line.rsplit(":", 1)[1].strip())
    return None


def git_sha(root: Path) -> str:
    """Prefer the Actions revision and fall back to the checked-out Git commit."""

    if value := os.environ.get("GITHUB_SHA"):
        return value
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def run_once(
    *,
    run_number: int,
    engine: str,
    reference_dir: Path,
    pam_file: Path,
    guide_file: Path,
    output_root: Path,
) -> dict[str, object]:
    """Execute one isolated mismatch-only search and retain every audit artifact."""

    run_dir = output_root / f"run_{run_number}"
    run_dir.mkdir(parents=True, exist_ok=False)
    resource_log = run_dir / "resource_usage.txt"
    stdout_path = run_dir / "stdout.txt"
    stderr_path = run_dir / "stderr.txt"
    time_binary = shutil.which("time") or "/usr/bin/time"
    engine_binary = shutil.which(engine) or engine
    command = [
        time_binary,
        "-v",
        "-o",
        str(resource_log),
        engine_binary,
        "search",
        f"{reference_dir}/",
        str(pam_file),
        str(guide_file),
        "emx1.hg38",
        "-mm",
        "4",
        "-t",
        "-scores",
        f"{reference_dir}/",
    ]
    completed = subprocess.run(
        command,
        cwd=run_dir,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "LC_ALL": "C", "LANG": "C"},
    )
    stdout_path.write_text(completed.stdout)
    stderr_path.write_text(completed.stderr)

    errors: list[str] = []
    if completed.returncode != 0:
        errors.append(f"engine exited with code {completed.returncode}")
    if completed.stderr.strip():
        errors.append("unexpected stderr is non-empty")

    outputs: dict[str, dict[str, object]] = {}
    for label, filename in EXPECTED_OUTPUTS.items():
        path = run_dir / filename
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty {filename}")
            continue
        outputs[label] = {
            "path": str(path.relative_to(output_root)),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }

    targets = run_dir / EXPECTED_OUTPUTS["targets"]
    canonical_rows = canonical_target_rows(targets) if targets.is_file() else []
    canonical_path = run_dir / "targets.canonical.txt"
    canonical_path.write_text("\n".join(canonical_rows) + ("\n" if canonical_rows else ""))
    if not canonical_rows:
        errors.append("canonical target rows are empty")

    disk_bytes = sum(path.stat().st_size for path in run_dir.rglob("*") if path.is_file())
    return {
        "run": run_number,
        "status": "PASS" if not errors else "FAIL",
        "return_code": completed.returncode,
        "command": shlex.join(command),
        "unexpected_stderr": bool(completed.stderr.strip()),
        "peak_rss_kib": parse_peak_rss_kib(resource_log),
        "disk_bytes": disk_bytes,
        "canonical_target_rows": len(canonical_rows),
        "canonical_targets_sha256": sha256(canonical_path),
        "outputs": outputs,
        "errors": errors,
    }


def main() -> None:
    """Validate the frozen inputs, run S0 twice and issue no biological verdict."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", default="crispritz.py")
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--reference-fasta", type=Path, required=True)
    parser.add_argument("--pam-file", type=Path, required=True)
    parser.add_argument("--guide-file", type=Path, required=True)
    parser.add_argument("--package-file", type=Path, required=True)
    parser.add_argument("--expected-package-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    required = [
        args.reference_fasta,
        args.pam_file,
        args.guide_file,
        args.package_file,
    ]
    if missing := [str(path) for path in required if not path.is_file()]:
        raise SystemExit(f"missing S0 inputs: {missing}")
    if not args.reference_dir.is_dir():
        raise SystemExit(f"missing reference directory: {args.reference_dir}")

    package_sha = sha256(args.package_file)
    if package_sha != args.expected_package_sha256:
        raise SystemExit(
            f"CRISPRitz package hash mismatch: {package_sha} != {args.expected_package_sha256}"
        )

    args.output_dir.mkdir(parents=True, exist_ok=False)
    runs = [
        run_once(
            run_number=run_number,
            engine=args.engine,
            reference_dir=args.reference_dir.resolve(),
            pam_file=args.pam_file.resolve(),
            guide_file=args.guide_file.resolve(),
            output_root=args.output_dir.resolve(),
        )
        for run_number in (1, 2)
    ]
    deterministic = (
        runs[0]["canonical_targets_sha256"] == runs[1]["canonical_targets_sha256"]
        and runs[0]["canonical_target_rows"] == runs[1]["canonical_target_rows"]
        and runs[0]["canonical_target_rows"] > 0
    )
    passed = all(run["status"] == "PASS" for run in runs) and deterministic
    report = {
        "schema_version": "crispritz_s0_execution_v1",
        "stage": "S0_INSTALLATION_SMOKE",
        "status": "S0_INSTALLATION_SMOKE_PASS" if passed else "S0_INSTALLATION_SMOKE_FAIL",
        "biological_verdict": "NOT_ISSUED",
        "promotion_boundary": {
            "automatic_replacements": 0,
            "synthesis_approval": False,
            "reason": "S0 validates the pinned command surface on chr22; it does not assess project guides.",
        },
        "engine": {
            "name": "CRISPRitz",
            "version": "2.7.0",
            "package_build": "py39h2de1943_0",
            "package_sha256": package_sha,
        },
        "inputs_sha256": {
            "reference_fasta": sha256(args.reference_fasta),
            "pam_file": sha256(args.pam_file),
            "guide_file": sha256(args.guide_file),
        },
        "repeated_runs": 2,
        "identical_target_rows_after_canonical_sort": deterministic,
        "runs": runs,
        "git_sha": git_sha(root),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": shlex.join(["python", *os.sys.argv]),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
