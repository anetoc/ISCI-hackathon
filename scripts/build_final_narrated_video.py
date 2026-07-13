#!/usr/bin/env python3
"""Render the corrected judge deck and synchronize it to the approved narration."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECK = ROOT / "outputs" / "tctrl_hackathon_deck.pptx"

# Transition centers were measured from the approved 2:41 narrated cut. Keeping them frozen means
# a visual-only correction does not silently change the spoken pacing or scientific emphasis.
TRANSITION_CENTERS = [15.55, 34.67, 48.91, 78.70, 97.00, 109.20, 123.03, 137.24, 144.05]
TRANSITION_SECONDS = 0.60


def require_binary(name: str) -> str:
    """Resolve a local media dependency or fail with an actionable error."""

    binary = shutil.which(name)
    if not binary:
        raise RuntimeError(f"Required binary not found on PATH: {name}")
    return binary


def audio_duration(audio: Path, ffprobe: str) -> float:
    """Read the authoritative duration from the exact narration file."""

    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(audio),
    ]
    payload = json.loads(subprocess.check_output(command, text=True))
    return float(payload["format"]["duration"])


def render_slides(deck: Path, render_dir: Path, soffice: str, pdftoppm: str) -> list[Path]:
    """Render the PPTX through LibreOffice at exact Full-HD slide dimensions."""

    if not deck.is_file():
        raise FileNotFoundError(deck)
    render_dir.mkdir(parents=True, exist_ok=True)
    # Remove stale renders so a previous 10-slide run cannot mask a failed conversion.
    for stale in render_dir.glob("slide-*.png"):
        stale.unlink()
    pdf = render_dir / f"{deck.stem}.pdf"
    pdf.unlink(missing_ok=True)
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
    slides = sorted(
        render_dir.glob("slide-*.png"),
        key=lambda path: int(path.stem.rsplit("-", 1)[1]),
    )
    if len(slides) != 10:
        raise RuntimeError(f"Expected 10 rendered slides, found {len(slides)}")
    return slides


def build_video(slides: list[Path], audio: Path, output: Path, duration: float, ffmpeg: str) -> None:
    """Cross-dissolve the ten stills at the frozen narration transition centers."""

    if len(slides) != 10:
        raise ValueError(f"Expected 10 rendered slides, found {len(slides)}")
    if not audio.is_file():
        raise FileNotFoundError(audio)
    if TRANSITION_CENTERS[-1] >= duration:
        raise ValueError("The final slide transition must occur before the narration ends")
    half = TRANSITION_SECONDS / 2
    boundaries = [0.0, *TRANSITION_CENTERS, duration]
    clip_durations: list[float] = []
    for index in range(10):
        logical = boundaries[index + 1] - boundaries[index]
        padding = half if index in (0, 9) else TRANSITION_SECONDS
        clip_durations.append(logical + padding)

    command = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
    for slide, clip_duration in zip(slides, clip_durations, strict=True):
        command.extend(["-loop", "1", "-t", f"{clip_duration:.6f}", "-i", str(slide)])
    command.extend(["-i", str(audio)])

    filters = [
        f"[{index}:v]fps=30,format=yuv420p,setsar=1[v{index}]" for index in range(10)
    ]
    previous = "v0"
    for index, center in enumerate(TRANSITION_CENTERS, start=1):
        output_label = f"x{index}"
        offset = center - half
        filters.append(
            f"[{previous}][v{index}]xfade=transition=fade:duration={TRANSITION_SECONDS}:"
            f"offset={offset:.6f}[{output_label}]"
        )
        previous = output_label

    output.parent.mkdir(parents=True, exist_ok=True)
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            f"[{previous}]",
            "-map",
            "10:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "30",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "1",
            "-movflags",
            "+faststart",
            "-shortest",
            str(output),
        ]
    )
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deck", type=Path, default=DEFAULT_DECK)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--render-dir",
        type=Path,
        help="Keep rendered slides here for visual QA; otherwise a temporary directory is used.",
    )
    args = parser.parse_args()

    soffice = require_binary("soffice")
    pdftoppm = require_binary("pdftoppm")
    ffmpeg = require_binary("ffmpeg")
    ffprobe = require_binary("ffprobe")
    deck = args.deck.resolve()
    audio = args.audio.resolve()
    output = args.output.resolve()
    duration = audio_duration(audio, ffprobe)

    if args.render_dir:
        slides = render_slides(deck, args.render_dir.resolve(), soffice, pdftoppm)
        build_video(slides, audio, output, duration, ffmpeg)
    else:
        with tempfile.TemporaryDirectory(prefix="tctrl-final-video-") as temporary:
            slides = render_slides(deck, Path(temporary), soffice, pdftoppm)
            build_video(slides, audio, output, duration, ffmpeg)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
