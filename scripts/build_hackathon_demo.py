#!/usr/bin/env python3
"""Build the self-contained T-CTRL judge demo from the approved ten-slide deck."""

from __future__ import annotations

import argparse
import base64
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "docs" / "hackathon_judge_demo.template.html"
DEFAULT_MANIFEST = ROOT / "outputs" / "hackathon" / "claim_manifest.json"
DEFAULT_TIMING = ROOT / "config" / "hackathon_timing.json"
DEFAULT_ASSETS = ROOT / "demo_assets" / "hackathon"
DEFAULT_OUTPUT = ROOT / "docs" / "hackathon_judge_demo.html"


def data_uri(path: Path, media_type: str) -> str:
    """Embed a binary asset so the stage demo has no network dependency."""

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def build(
    template_path: Path,
    manifest_path: Path,
    timing_path: Path,
    assets_path: Path,
    output_path: Path,
) -> str:
    """Embed the exact approved deck renders and frozen claims in one offline HTML file."""

    manifest = json.loads(manifest_path.read_text())
    timing = json.loads(timing_path.read_text())
    scenes = timing["scenes"]
    slide_paths = [
        assets_path / f"{scene['scene']:02d}_{scene['id']}.png" for scene in scenes
    ]
    missing = [path for path in slide_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing rendered judge slides: {missing}")

    manifest_json = json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
    timing_json = json.dumps(timing, ensure_ascii=False).replace("</", "<\\/")
    slides_html = []
    for scene, slide_path in zip(scenes, slide_paths, strict=True):
        active = " active" if scene["scene"] == 1 else ""
        title = escape(scene["title"], quote=True)
        slides_html.append(
            f'<section class="slide{active}" data-label="{title}" '
            f'aria-label="Slide {scene["scene"]}: {title}">'
            f'<img src="{data_uri(slide_path, "image/png")}" alt="{title}">'
            "</section>"
        )
    html = template_path.read_text()
    replacements = {
        "__CLAIM_MANIFEST__": manifest_json,
        "__TIMING_PLAN__": timing_json,
        "__SLIDES_HTML__": "\n      ".join(slides_html),
    }
    for marker, value in replacements.items():
        if marker not in html:
            raise ValueError(f"Template marker missing: {marker}")
        html = html.replace(marker, value)

    if "https://" in html or "http://" in html:
        raise ValueError("Stage demo must not contain external network dependencies")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    return html


def main() -> None:
    """Expose all inputs so the committed build is reproducible."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--timing", type=Path, default=DEFAULT_TIMING)
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.template, args.manifest, args.timing, args.assets, args.output)
    print(f"Wrote {args.output} (self-contained, offline)")


if __name__ == "__main__":
    main()
