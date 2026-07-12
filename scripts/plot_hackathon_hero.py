#!/usr/bin/env python3
"""Render the single 16:9 scientific thesis figure used in the stage demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "outputs" / "hackathon" / "claim_manifest.json"
DEFAULT_OUTPUT = ROOT / "figures" / "hackathon_hero.png"

BG = "#07131F"
INK = "#F4F7FA"
MUTED = "#A9B7C5"
LINE = "#294054"
REACH = "#F1A340"
PRECISION = "#45B7D1"
REPEAT = "#67C587"
PASS = "#49A267"
FAIL = "#D95A4E"
NULL = "#718096"
NE = "#98A6B3"


def _component_reach(ax: plt.Axes, x: float, y: float) -> None:
    """Draw distance moved without implying that distance determines direction."""

    ax.add_patch(Circle((x - 0.055, y), 0.013, color=MUTED, alpha=0.85))
    ax.add_patch(
        FancyArrowPatch(
            (x - 0.035, y),
            (x + 0.075, y),
            arrowstyle="-|>",
            mutation_scale=22,
            linewidth=3,
            color=REACH,
        )
    )


def _component_precision(ax: plt.Axes, x: float, y: float) -> None:
    """Draw directional alignment onto a pre-defined functional axis."""

    for radius, alpha in ((0.075, 0.18), (0.050, 0.28), (0.026, 0.95)):
        ax.add_patch(Circle((x, y), radius, color=PRECISION, alpha=alpha))
    ax.plot([x - 0.10, x + 0.10], [y, y], color=MUTED, linewidth=1.4, alpha=0.55)
    ax.plot([x, x], [y - 0.10, y + 0.10], color=MUTED, linewidth=1.4, alpha=0.55)


def _component_repeatability(ax: plt.Axes, x: float, y: float) -> None:
    """Draw donor/guide effects converging on the same state displacement."""

    starts = [(x - 0.09, y + 0.07), (x - 0.09, y), (x - 0.09, y - 0.07)]
    targets = [(x + 0.055, y + 0.012), (x + 0.065, y), (x + 0.055, y - 0.012)]
    for start, target in zip(starts, targets, strict=True):
        ax.add_patch(Circle(start, 0.010, color=MUTED))
        ax.add_patch(
            FancyArrowPatch(
                start,
                target,
                arrowstyle="-|>",
                mutation_scale=15,
                linewidth=2.2,
                color=REPEAT,
                alpha=0.92,
            )
        )


def build_figure(manifest: dict) -> Figure:
    """Build a projector-readable figure from the frozen claim manifest."""

    primary = manifest["claims"][0]["metrics"]
    discovery = primary["authoritative_full_sample"]
    oof = primary["leakage_free_oof"]

    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.055,
        0.925,
        "MAGNITUDE IS NECESSARY. IT IS NOT SUFFICIENT.",
        color=INK,
        fontsize=25,
        fontweight="bold",
        va="top",
    )
    ax.text(
        0.055,
        0.862,
        "Controllability asks where the cell moved — and whether the movement repeats.",
        color=MUTED,
        fontsize=17,
        va="top",
    )
    ax.text(
        0.055,
        0.817,
        "Scope: canonical axis-defining CD4+ T-cell regulators · detectable-effect perturbations",
        color=PRECISION,
        fontsize=11.5,
        va="top",
    )

    components = [
        (0.19, "1  REACH", "How far did the cell move?", REACH, _component_reach),
        (0.50, "2  PRECISION", "Did it move along the intended state axis?", PRECISION, _component_precision),
        (0.81, "3  REPEATABILITY", "Did guides and donors agree?", REPEAT, _component_repeatability),
    ]
    for index, (x, label, question, color, draw) in enumerate(components):
        if index:
            ax.plot([x - 0.155, x - 0.155], [0.46, 0.78], color=LINE, linewidth=1.2)
        ax.text(x, 0.745, label, color=color, fontsize=18, fontweight="bold", ha="center")
        draw(ax, x, 0.625)
        ax.text(x, 0.495, question, color=INK, fontsize=13.5, ha="center", va="center")

    ax.add_patch(Rectangle((0.055, 0.245), 0.89, 0.145, color="#0D2233", ec=LINE, linewidth=1.2))
    ax.text(0.080, 0.350, "EVIDENCE", color=MUTED, fontsize=12, fontweight="bold")
    ax.text(
        0.080,
        0.315,
        f"Full-sample M→M+C  +{discovery['discovery_gain']:.3f}",
        color=INK,
        fontsize=20,
        fontweight="bold",
    )
    ax.text(
        0.080,
        0.270,
        f"95% CI  [{discovery['discovery_ci95'][0]:+.3f}, {discovery['discovery_ci95'][1]:+.3f}]",
        color=MUTED,
        fontsize=13,
    )
    ax.plot([0.535, 0.535], [0.270, 0.360], color=LINE, linewidth=1.2)
    ax.text(
        0.565,
        0.320,
        f"Leakage-free OOF  +{oof['gain']:.3f}",
        color=PRECISION,
        fontsize=20,
        fontweight="bold",
    )
    ax.text(
        0.565,
        0.275,
        f"95% CI [{oof['ci95'][0]:+.3f}, {oof['ci95'][1]:+.3f}]  ·  permutation p={oof['permutation_p']:.3f}",
        color=MUTED,
        fontsize=13,
    )

    verdicts = [("PASS", PASS), ("FAIL", FAIL), ("NULL", NULL), ("NOT-EVALUABLE", NE)]
    widths = [0.15, 0.15, 0.15, 0.23]
    x = 0.055
    for (label, color), width in zip(verdicts, widths, strict=True):
        ax.add_patch(Rectangle((x, 0.115), width, 0.072, color=color, alpha=0.95))
        ax.text(
            x + width / 2,
            0.151,
            label,
            color="#FFFFFF",
            fontsize=12.5,
            fontweight="bold",
            ha="center",
            va="center",
        )
        x += width + 0.012
    ax.text(0.055, 0.075, "A good scientific agent knows when not to call PASS.", color=INK, fontsize=15)
    ax.text(
        0.945,
        0.040,
        f"git {manifest['git_sha'][:8]} · axes {manifest['axes_sha256'][:10]} · public-data evidence",
        color="#708497",
        fontsize=8.5,
        ha="right",
    )
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig


def main() -> None:
    """Read the manifest and emit the stage-ready PNG."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    figure = build_figure(manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, facecolor=BG, dpi=120)
    plt.close(figure)
    print(f"Wrote {args.output} (16:9)")


if __name__ == "__main__":
    main()
