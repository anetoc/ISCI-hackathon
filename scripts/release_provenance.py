"""Content-address the exact source files used by public release builders."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Iterable


SNAPSHOT_SCHEMA = "isci_source_snapshot_v1"


def file_sha256(path: Path) -> str:
    """Hash one file without loading large evidence artifacts into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_snapshot(paths: Iterable[Path], root: Path) -> dict[str, object]:
    """Bind named source files with unambiguous length-prefixed SHA-256 framing.

    The Git commit is necessarily the revision *before* a newly generated artifact
    is committed. This snapshot closes that gap by hashing the actual working-tree
    sources consumed by the builder, including the builder and this helper.
    """

    root = root.resolve()
    normalized: dict[str, Path] = {}
    for path in paths:
        resolved = path.resolve()
        relative = resolved.relative_to(root).as_posix()
        normalized[relative] = resolved

    digest = hashlib.sha256()
    files_sha256: dict[str, str] = {}
    for relative, path in sorted(normalized.items()):
        file_hash = file_sha256(path)
        files_sha256[relative] = file_hash
        for value in (relative.encode(), bytes.fromhex(file_hash)):
            digest.update(len(value).to_bytes(8, "big"))
            digest.update(value)

    return {
        "schema_version": SNAPSHOT_SCHEMA,
        "sha256": digest.hexdigest(),
        "files_sha256": files_sha256,
    }


def source_paths_dirty(paths: Iterable[Path], root: Path) -> bool:
    """Report whether the recorded source paths differ from the base Git revision."""

    relative = sorted({path.resolve().relative_to(root.resolve()).as_posix() for path in paths})
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all", "--", *relative],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return bool(result.stdout.strip())
