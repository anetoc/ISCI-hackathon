"""Load AnnData DE_stats / pseudobulk with hashing and provenance manifest.

The reproducibility manifest is the SaMD-grade audit trail: every input file is
SHA-256 hashed, and the environment (package versions, seeds, git-SHA) is captured
so any artifact can be traced back to exact inputs + code.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anndata as ad


def load_de_stats(path: Path | str, backed: str | None = None) -> ad.AnnData:
    """Load GWCD4i.DE_stats.h5ad (33,983 perturbation x condition, 10,282 genes).

    .layers: log_fc, zscore (=logFC/lfcSE), p_value, adj_p_value, lfcSE, baseMean
    .obs: target_contrast_gene_name, culture_condition, ontarget_* , donor/guide
          correlation QC fields, off-target flags (see data_sharing_readme.md).
    .varm: measured_genes_stats_{Rest,Stim8hr,Stim48hr}

    Parameters
    ----------
    backed : optional "r" to memory-map (the file is ~16.8 GB). For M/R we only
             need .obs + one layer at a time, so backed="r" keeps RSS low.
    """
    return ad.read_h5ad(str(path), backed=backed)


def load_pseudobulk(path: Path | str, backed: str | None = "r") -> ad.AnnData:
    """Load GWCD4i.pseudobulk_merged.h5ad (~44.6 GB; default backed to spare RAM)."""
    return ad.read_h5ad(str(path), backed=backed)


def file_sha256(path: Path | str, chunk: int = 1 << 20) -> str:
    """Return SHA-256 hex digest for the reproducibility manifest."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _git_sha(repo_dir: Path | str | None = None) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_dir) if repo_dir else None,
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def _pkg_versions(pkgs: tuple[str, ...] = (
    "anndata", "scanpy", "numpy", "pandas", "scipy", "sklearn",
    "statsmodels", "pertpy", "decoupler", "networkx",
)) -> dict[str, str]:
    vers: dict[str, str] = {}
    for name in pkgs:
        try:
            mod = __import__(name)
            vers[name] = getattr(mod, "__version__", "unknown")
        except Exception:
            vers[name] = "not-installed"
    return vers


def build_manifest(
    inputs: dict[str, Path | str],
    seeds: dict[str, int] | None = None,
    params: dict[str, Any] | None = None,
    repo_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Assemble a provenance manifest: input hashes + env + seeds + git-SHA."""
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "git_sha": _git_sha(repo_dir),
        "package_versions": _pkg_versions(),
        "seeds": seeds or {},
        "params": params or {},
        "inputs": {
            k: {"path": str(v), "sha256": file_sha256(v) if Path(v).exists() else None,
                "size_bytes": Path(v).stat().st_size if Path(v).exists() else None}
            for k, v in inputs.items()
        },
    }


def write_manifest(path: Path | str, entries: dict[str, Any]) -> None:
    """Write execution manifest (versions, hashes, seeds) for audit trail."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2, default=str)
