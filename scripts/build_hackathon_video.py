#!/usr/bin/env python3
"""Build and validate a silent 2:30 Full-HD fallback video with FFmpeg."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:  # Package import in tests; direct import when run as `python scripts/...`.
    from .release_provenance import source_paths_dirty, source_snapshot
except ImportError:  # pragma: no cover - exercised by the release CLI.
    from release_provenance import source_paths_dirty, source_snapshot


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMING = ROOT / "config" / "hackathon_timing.json"
DEFAULT_ASSETS = ROOT / "demo_assets" / "hackathon"
DEFAULT_OUTPUT = DEFAULT_ASSETS / "hackathon_fallback_2m30.mp4"
DEFAULT_MANIFEST = ROOT / "outputs" / "hackathon" / "video_manifest.json"
PROVENANCE_HELPER = ROOT / "scripts" / "release_provenance.py"


def sha256(path: Path) -> str:
    """Hash media without loading the complete file into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_sha() -> str:
    """Record the exact code state that assembled the fallback."""

    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def probe(video_path: Path, ffprobe: str) -> dict:
    """Return normalized container properties used by validation and tests."""

    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
        "-of",
        "json",
        str(video_path),
    ]
    return json.loads(subprocess.check_output(command, text=True))


def build_video(timing_path: Path, assets_dir: Path, output_path: Path) -> tuple[list[Path], dict]:
    """Encode hard-cut scenes from the shared timing contract."""

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("ffmpeg and ffprobe are required to build the fallback video")

    timing = json.loads(timing_path.read_text())
    scenes = timing["scenes"]
    screenshots = [assets_dir / f"{scene['scene']:02d}_{scene['id']}.png" for scene in scenes]
    missing = [path for path in screenshots if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing scene screenshots: {missing}")
    total_seconds = sum(int(scene["duration_seconds"]) for scene in scenes)
    if total_seconds != int(timing["target_seconds"]):
        raise ValueError("Scene durations do not match target_seconds")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="isci-video-") as tmp:
        concat_path = Path(tmp) / "scenes.txt"
        lines = []
        for screenshot, scene in zip(screenshots, scenes, strict=True):
            lines.extend([f"file '{screenshot}'", f"duration {scene['duration_seconds']}"])
        # FFmpeg concat needs the final still repeated to honor its duration.
        lines.append(f"file '{screenshots[-1]}'")
        concat_path.write_text("\n".join(lines) + "\n")

        command = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-vf",
            "fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-t",
            str(total_seconds),
            "-movflags",
            "+faststart",
            str(output_path),
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    properties = probe(output_path, ffprobe)
    duration = float(properties["format"]["duration"])
    video_stream = next(stream for stream in properties["streams"] if stream["codec_type"] == "video")
    audio_stream = next(stream for stream in properties["streams"] if stream["codec_type"] == "audio")
    if abs(duration - total_seconds) > 0.1:
        raise ValueError(f"Unexpected video duration: {duration}")
    if (video_stream["width"], video_stream["height"]) != (1920, 1080):
        raise ValueError(f"Unexpected video size: {video_stream['width']}x{video_stream['height']}")
    if video_stream["codec_name"] != "h264" or audio_stream["codec_name"] != "aac":
        raise ValueError("Fallback must use H.264 video and AAC audio")
    return screenshots, properties


def main() -> None:
    """Build the MP4 and emit a content-addressed media manifest."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--timing", type=Path, default=DEFAULT_TIMING)
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    screenshots, properties = build_video(args.timing, args.assets, args.output)
    command = "python scripts/build_hackathon_video.py"
    source_paths = [Path(__file__), PROVENANCE_HELPER, args.timing, *screenshots]
    manifest = {
        "schema_version": "hackathon_video_manifest_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha(),
        "git_sha_semantics": "Base revision at generation time; source_snapshot binds exact working-tree inputs.",
        "source_paths_dirty": source_paths_dirty(source_paths, ROOT),
        "source_snapshot": source_snapshot(source_paths, ROOT),
        "command": command,
        "timing_path": str(args.timing.relative_to(ROOT)),
        "timing_sha256": sha256(args.timing),
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in screenshots},
        "output_path": str(args.output.relative_to(ROOT)),
        "output_sha256": sha256(args.output),
        "duration_seconds": float(properties["format"]["duration"]),
        "width": 1920,
        "height": 1080,
        "video_codec": "h264",
        "audio_codec": "aac",
        "audio_content": "silence",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {args.output} ({manifest['duration_seconds']:.1f}s, Full HD)")


if __name__ == "__main__":
    main()
