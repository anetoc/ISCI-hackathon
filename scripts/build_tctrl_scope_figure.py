#!/usr/bin/env python3
"""Build the judge-facing four-system controllability boundary figure.

The historical evidence archive uses the CCI and TSC labels. This public figure keeps the
same frozen estimates and verdicts while describing the result in plain scientific language.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "figures" / "tctrl_scope_4systems.png"

# Values are the frozen matched C-vs-M comparator used only for cross-system scope mapping.
# They are not the primary full-sample M -> M+C estimand reported on slide 4.
SYSTEMS = [
    {
        "label": "Marson CD4+\nimmune · KD/KO",
        "gain": 0.229,
        "ci": (0.072, 0.405),
        "verdict": "PASS",
        "color": "#1C7C43",
    },
    {
        "label": "Schmidt CD4+\nimmune · CRISPRa",
        "gain": 0.138,
        "ci": (-0.029, 0.434),
        "verdict": "NEAR-MISS",
        "color": "#62BE64",
    },
    {
        "label": "Norman K562\nnon-immune · differentiation",
        "gain": 0.138,
        "ci": (-0.033, 0.370),
        "verdict": "FAIL (near)",
        "color": "#F39C72",
    },
    {
        "label": "Replogle RPE1\nnon-immune · proliferation",
        "gain": 0.060,
        "ci": (-0.013, 0.204),
        "verdict": "FAIL",
        "color": "#B7192E",
    },
]


def build() -> Path:
    """Render the frozen scope comparison without historical public-facing acronyms."""

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, ax = plt.subplots(figsize=(10.43, 7.0), dpi=180)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Soft bands make the immune versus non-immune boundary readable before the labels.
    ax.axhspan(1.5, 3.5, color="#F1F7F3", zorder=0)
    ax.axhspan(-0.5, 1.5, color="#FCF4F4", zorder=0)
    ax.axvline(0, color="#666666", linestyle=(0, (4, 3)), linewidth=1.4, zorder=1)

    y_positions = np.arange(len(SYSTEMS) - 1, -1, -1)
    for y, system in zip(y_positions, SYSTEMS, strict=True):
        gain = system["gain"]
        low, high = system["ci"]
        color = system["color"]
        ax.errorbar(
            gain,
            y,
            xerr=np.array([[gain - low], [high - gain]]),
            fmt="o",
            markersize=13,
            markeredgecolor="white",
            markeredgewidth=1.2,
            color=color,
            ecolor=color,
            elinewidth=3.2,
            capsize=8,
            capthick=3.2,
            zorder=3,
        )
        ax.text(
            high + 0.018,
            y,
            f"{gain:+.3f} · {system['verdict']}",
            va="center",
            ha="left",
            color=color,
            fontsize=12,
            fontweight="bold",
        )

    ax.set_yticks(y_positions, [system["label"] for system in SYSTEMS])
    ax.set_xlim(-0.08, 0.62)
    ax.set_ylim(-0.65, 3.65)
    ax.set_xlabel(
        "Conditional gain in regulator recovery\n"
        "ΔAUPRC after magnitude control (M → M+C)",
        fontsize=13,
        labelpad=12,
    )
    ax.text(
        0.605,
        2.5,
        "IMMUNE",
        color="#7CAE8A",
        rotation=90,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
    )
    ax.text(
        0.605,
        0.5,
        "NON-IMMUNE",
        color="#D77A86",
        rotation=90,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=11)
    ax.tick_params(axis="x", labelsize=10)
    ax.grid(False)

    fig.text(
        0.06,
        0.02,
        "PASS requires a bootstrap interval excluding zero and the pre-specified conditional gate. "
        "A near-miss remains non-PASS.",
        fontsize=8.5,
        color="#666666",
    )
    # The slide already carries the explanatory headline, so the chart uses the space for data.
    fig.subplots_adjust(left=0.24, right=0.91, top=0.94, bottom=0.19)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, facecolor="white")
    plt.close(fig)
    return OUTPUT


if __name__ == "__main__":
    output = build()
    print(f"Wrote {output}")
