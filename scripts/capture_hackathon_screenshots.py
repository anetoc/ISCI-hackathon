#!/usr/bin/env python3
"""Capture six deterministic Full-HD stage scenes from the current offline HTML."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:  # Package import in tests; direct import when run as `python scripts/...`.
    from .release_provenance import source_paths_dirty, source_snapshot
except ImportError:  # pragma: no cover - exercised by the release CLI.
    from release_provenance import source_paths_dirty, source_snapshot


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "docs" / "hackathon_judge_demo.html"
TIMING = ROOT / "config" / "hackathon_timing.json"
ASSETS = ROOT / "demo_assets" / "hackathon"
MANIFEST = ROOT / "outputs" / "hackathon" / "screenshot_manifest.json"
AXES = ROOT / "config" / "axes.yaml"
PROVENANCE_HELPER = ROOT / "scripts" / "release_provenance.py"


def sha256(path: Path) -> str:
    """Return a content address for HTML and screenshots."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_chrome() -> str:
    """Locate a local Chromium-family browser without downloading anything."""

    candidates = [
        os.environ.get("CHROME_BIN"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("Local Chrome/Chromium not found; set CHROME_BIN explicitly")


def png_size(path: Path) -> tuple[int, int]:
    """Read PNG dimensions from the fixed IHDR header without image dependencies."""

    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def main() -> None:
    """Capture each static scene and write provenance only after all six validate."""

    chrome = find_chrome()
    timing = json.loads(TIMING.read_text())
    ASSETS.mkdir(parents=True, exist_ok=True)
    screenshots = []
    for scene in timing["scenes"]:
        output = ASSETS / f"{scene['scene']:02d}_{scene['id']}.png"
        url = f"{DEMO.as_uri()}?static=1&scene={scene['scene']}"
        command = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--allow-file-access-from-files",
            "--force-device-scale-factor=1",
            "--window-size=1920,1080",
            "--virtual-time-budget=1000",
            f"--screenshot={output}",
            url,
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if png_size(output) != (1920, 1080):
            raise ValueError(f"Unexpected screenshot size: {output} {png_size(output)}")
        screenshots.append(output)

    source_paths = [Path(__file__), PROVENANCE_HELPER, DEMO, TIMING, AXES]
    manifest = {
        "schema_version": "hackathon_screenshot_manifest_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_sha_semantics": "Base revision at generation time; source_snapshot binds exact working-tree inputs.",
        "source_paths_dirty": source_paths_dirty(source_paths, ROOT),
        "source_snapshot": source_snapshot(source_paths, ROOT),
        "command": "python scripts/capture_hackathon_screenshots.py",
        "browser": Path(chrome).name,
        "demo_path": str(DEMO.relative_to(ROOT)),
        "demo_sha256": sha256(DEMO),
        "data_sha256": sha256(ROOT / "outputs" / "hackathon" / "claim_manifest.json"),
        "axes_sha256": sha256(AXES),
        "width": 1920,
        "height": 1080,
        "screenshots_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in screenshots},
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(screenshots)} Full-HD screenshots from {DEMO.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
