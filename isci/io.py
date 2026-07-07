"""Load AnnData DE_stats / pseudobulk with hashing and provenance manifest."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import anndata as ad


def load_de_stats(path: Path | str) -> ad.AnnData:
    """Load GWCD4i.DE_stats.h5ad (perturbation x condition x gene DE matrix)."""
    raise NotImplementedError("Implement in Claude Science build (D0)")


def load_pseudobulk(path: Path | str) -> ad.AnnData:
    """Load GWCD4i.pseudobulk_merged.h5ad."""
    raise NotImplementedError("Implement in Claude Science build (D0)")


def file_sha256(path: Path) -> str:
    """Return SHA-256 hex digest for reproducibility manifest."""
    raise NotImplementedError("Implement in Claude Science build (D0)")


def write_manifest(path: Path, entries: dict[str, Any]) -> None:
    """Write execution manifest (versions, hashes, seeds) for audit trail."""
    raise NotImplementedError("Implement in Claude Science build (D0)")
