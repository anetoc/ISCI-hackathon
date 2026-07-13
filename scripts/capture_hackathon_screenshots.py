#!/usr/bin/env python3
"""Render the approved ten-slide judge deck to deterministic Full-HD PNG assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:  # Package import in tests; direct import when run as `python scripts/...`.
    from .release_provenance import source_paths_dirty, source_snapshot
except ImportError:  # pragma: no cover - exercised by the release CLI.
    from release_provenance import source_paths_dirty, source_snapshot


ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "outputs" / "tctrl_hackathon_deck.pptx"
TIMING = ROOT / "config" / "hackathon_timing.json"
ASSETS = ROOT / "demo_assets" / "hackathon"
MANIFEST = ROOT / "outputs" / "hackathon" / "screenshot_manifest.json"
AXES = ROOT / "config" / "axes.yaml"
PROVENANCE_HELPER = ROOT / "scripts" / "release_provenance.py"


def sha256(path: Path) -> str:
    """Return a content address for HTML and screenshots."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_binary(name: str) -> str:
    """Resolve a local rendering dependency or fail with an actionable error."""

    binary = shutil.which(name)
    if not binary:
        raise RuntimeError(f"Required binary not found on PATH: {name}")
    return binary


def render_slides(deck: Path, render_dir: Path, soffice: str, pdftoppm: str) -> list[Path]:
    """Render the public deck to exact Full-HD PNGs for the offline HTML."""

    if not deck.is_file():
        raise FileNotFoundError(deck)
    render_dir.mkdir(parents=True, exist_ok=True)
    pdf = render_dir / f"{deck.stem}.pdf"
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(render_dir), str(deck)],
        check=True,
    )
    if not pdf.is_file():
        raise RuntimeError(f"LibreOffice did not produce the expected PDF: {pdf}")
    subprocess.run(
        [
            pdftoppm,
            "-png",
            "-scale-to-x",
            "1920",
            "-scale-to-y",
            "1080",
            str(pdf),
            str(render_dir / "slide"),
        ],
        check=True,
    )
    return sorted(
        render_dir.glob("slide-*.png"),
        key=lambda path: int(path.stem.rsplit("-", 1)[1]),
    )


def png_size(path: Path) -> tuple[int, int]:
    """Read PNG dimensions from the fixed IHDR header without image dependencies."""

    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def expected_screenshots(timing: dict[str, object]) -> list[Path]:
    """Map the frozen timing plan to the approved deck screenshot paths."""

    return [
        ASSETS / f"{scene['scene']:02d}_{scene['id']}.png"
        for scene in timing["scenes"]
    ]


def validate_screenshots(screenshots: list[Path], expected_count: int = 10) -> None:
    """Reject partial or incorrectly sized deck renders before provenance is written."""

    if len(screenshots) != expected_count:
        raise ValueError(f"Expected {expected_count} screenshots, found {len(screenshots)}")
    for output in screenshots:
        if not output.is_file():
            raise FileNotFoundError(f"Missing screenshot: {output}")
        if png_size(output) != (1920, 1080):
            raise ValueError(f"Unexpected screenshot size: {output} {png_size(output)}")


def main() -> None:
    """Render each approved slide and write provenance only after all assets validate."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reuse-existing",
        action="store_true",
        help=(
            "Validate existing Full-HD deck renders and rebuild only the manifest."
        ),
    )
    args = parser.parse_args()
    timing = json.loads(TIMING.read_text())
    ASSETS.mkdir(parents=True, exist_ok=True)
    screenshots = expected_screenshots(timing)
    if args.reuse_existing:
        manifest_command = "python scripts/capture_hackathon_screenshots.py --reuse-existing"
    else:
        manifest_command = "python scripts/capture_hackathon_screenshots.py"
        soffice = require_binary("soffice")
        pdftoppm = require_binary("pdftoppm")
        with tempfile.TemporaryDirectory(prefix="tctrl-judge-slides-") as temporary:
            rendered = render_slides(DECK, Path(temporary), soffice, pdftoppm)
            if len(rendered) != len(screenshots):
                raise ValueError(
                    f"Timing expects {len(screenshots)} slides, deck rendered {len(rendered)}"
                )
            for source, output in zip(rendered, screenshots, strict=True):
                shutil.copyfile(source, output)

    validate_screenshots(screenshots, expected_count=len(timing["scenes"]))

    source_paths = [Path(__file__), PROVENANCE_HELPER, DECK, TIMING, AXES]
    manifest = {
        "schema_version": "hackathon_screenshot_manifest_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_sha_semantics": "Base revision at generation time; source_snapshot binds exact working-tree inputs.",
        "source_paths_dirty": source_paths_dirty(source_paths, ROOT),
        "source_snapshot": source_snapshot(source_paths, ROOT),
        "command": manifest_command,
        "renderer": "LibreOffice PDF export + pdftoppm 1920x1080",
        "deck_path": str(DECK.relative_to(ROOT)),
        "deck_sha256": sha256(DECK),
        "data_sha256": sha256(ROOT / "outputs" / "hackathon" / "claim_manifest.json"),
        "axes_sha256": sha256(AXES),
        "width": 1920,
        "height": 1080,
        "screenshots_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in screenshots},
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(screenshots)} Full-HD screenshots from {DECK.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
