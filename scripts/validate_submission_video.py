#!/usr/bin/env python3
"""Validate the human-narrated hackathon submission video.

The deterministic repository fallback intentionally proves timing and visual consistency. The
actual submission also needs audible speech, so this validator checks the exported file without
trying to infer whether the scientific narration is correct.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


def assess_video(
    probe: dict[str, Any], mean_volume_db: float | None, max_volume_db: float | None
) -> list[str]:
    """Return contract failures for parsed ffprobe and volumedetect evidence."""
    failures: list[str] = []
    streams = probe.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    duration = float(probe.get("format", {}).get("duration", 0.0))

    if not 60.0 <= duration <= 180.0:
        failures.append(f"duration must be between 60 and 180 seconds; observed {duration:.3f}")

    if video is None:
        failures.append("video stream is missing")
    else:
        if video.get("codec_name") != "h264":
            failures.append(f"video codec must be h264; observed {video.get('codec_name')}")
        if int(video.get("width", 0)) < 1920 or int(video.get("height", 0)) < 1080:
            failures.append(
                "video resolution must be at least 1920x1080; "
                f"observed {video.get('width')}x{video.get('height')}"
            )

    if audio is None:
        failures.append("audio stream is missing")
    else:
        if audio.get("codec_name") != "aac":
            failures.append(f"audio codec must be aac; observed {audio.get('codec_name')}")
        # Silence beds can satisfy a superficial "audio stream exists" check. These conservative
        # thresholds reject silence while leaving final loudness judgment to headphone review.
        if mean_volume_db is None or mean_volume_db <= -45.0:
            failures.append(
                "mean audio level is silent or too quiet; "
                f"observed {mean_volume_db if mean_volume_db is not None else 'unavailable'} dB"
            )
        if max_volume_db is None or max_volume_db <= -20.0:
            failures.append(
                "peak audio level is silent or too quiet; "
                f"observed {max_volume_db if max_volume_db is not None else 'unavailable'} dB"
            )

    return failures


def inspect_video(path: Path) -> dict[str, Any]:
    """Collect machine-readable stream metadata and simple volume evidence."""
    for binary in ("ffprobe", "ffmpeg"):
        if shutil.which(binary) is None:
            raise RuntimeError(f"required binary not found: {binary}")

    probe_process = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels:format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    probe = json.loads(probe_process.stdout)

    volume_process = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    stderr = volume_process.stderr
    mean_match = re.search(r"mean_volume:\s*(-?[0-9.]+) dB", stderr)
    max_match = re.search(r"max_volume:\s*(-?[0-9.]+) dB", stderr)
    mean_volume = float(mean_match.group(1)) if mean_match else None
    max_volume = float(max_match.group(1)) if max_match else None

    failures = assess_video(probe, mean_volume, max_volume)
    return {
        "schema_version": "tctrl_submission_video_check_v1",
        "path": str(path.resolve()),
        "status": "PASS" if not failures else "FAIL",
        "duration_seconds": float(probe.get("format", {}).get("duration", 0.0)),
        "mean_volume_db": mean_volume,
        "max_volume_db": max_volume,
        "streams": probe.get("streams", []),
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="human-narrated MP4 exported for submission")
    parser.add_argument("--json-out", type=Path, help="optional path for the validation report")
    args = parser.parse_args()

    if not args.video.is_file():
        raise SystemExit(f"video not found: {args.video}")

    report = inspect_video(args.video)
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered + "\n")
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
