#!/usr/bin/env python3
"""Build the self-contained, deterministic T-CTRL hackathon stage demo."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "docs" / "hackathon_judge_demo.template.html"
DEFAULT_MANIFEST = ROOT / "outputs" / "hackathon" / "claim_manifest.json"
DEFAULT_TIMING = ROOT / "config" / "hackathon_timing.json"
DEFAULT_HERO = ROOT / "figures" / "hackathon_hero.png"
DEFAULT_OUTPUT = ROOT / "docs" / "hackathon_judge_demo.html"
DEFAULT_PRETEXT = Path.home() / ".claude" / "skills" / "gstack" / "design-html" / "vendor" / "pretext.js"


def data_uri(path: Path, media_type: str) -> str:
    """Embed a binary asset so the stage demo has no network dependency."""

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def build(
    template_path: Path,
    manifest_path: Path,
    timing_path: Path,
    hero_path: Path,
    pretext_path: Path,
    output_path: Path,
) -> str:
    """Inject frozen claims, hero art and Pretext into one offline HTML file."""

    manifest = json.loads(manifest_path.read_text())
    timing = json.loads(timing_path.read_text())
    manifest_json = json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
    timing_json = json.dumps(timing, ensure_ascii=False).replace("</", "<\\/")
    pretext_b64 = base64.b64encode(pretext_path.read_bytes()).decode("ascii")
    html = template_path.read_text()
    replacements = {
        "__CLAIM_MANIFEST__": manifest_json,
        "__TIMING_PLAN__": timing_json,
        "__PRETEXT_BASE64__": pretext_b64,
        "__HERO_DATA_URI__": data_uri(hero_path, "image/png"),
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
    parser.add_argument("--hero", type=Path, default=DEFAULT_HERO)
    parser.add_argument("--pretext", type=Path, default=DEFAULT_PRETEXT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.template, args.manifest, args.timing, args.hero, args.pretext, args.output)
    print(f"Wrote {args.output} (self-contained, offline)")


if __name__ == "__main__":
    main()
