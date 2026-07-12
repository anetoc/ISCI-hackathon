#!/usr/bin/env python
"""Visualize the non-scalar Controllability Profile v2 and condition transport."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    profile = pd.read_csv(ROOT / "outputs/decomposition_v2/controllability_profile_v2.csv")
    transport = pd.read_csv(ROOT / "outputs/decomposition_v2/t4_condition_transport_v2.csv")
    summary = json.loads((ROOT / "outputs/decomposition_v2/controllability_profile_v2.json").read_text())

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.7), constrained_layout=True)

    non_front = profile[~profile["pareto_front"]]
    front = profile[profile["pareto_front"]]
    axes[0].scatter(
        non_front["reach_pct"],
        non_front["precision_th2_conditional_pct"],
        c=non_front["repeatability_conditional_pct"],
        cmap="viridis",
        vmin=0,
        vmax=1,
        s=12,
        alpha=0.28,
        linewidth=0,
    )
    scatter = axes[0].scatter(
        front["reach_pct"],
        front["precision_th2_conditional_pct"],
        c=front["repeatability_conditional_pct"],
        cmap="viridis",
        vmin=0,
        vmax=1,
        s=36,
        edgecolor="#111111",
        linewidth=0.55,
    )
    known = front[front["known_regulator"]]
    for _, row in known.iterrows():
        axes[0].annotate(
            row.gene,
            (row.reach_pct, row.precision_th2_conditional_pct),
            xytext=(3, 3),
            textcoords="offset points",
            fontsize=7,
            fontweight="bold",
        )
    axes[0].axhline(0.75, color="#777777", linestyle="--", linewidth=0.7)
    axes[0].axvline(0.75, color="#777777", linestyle="--", linewidth=0.7)
    axes[0].set_xlabel("Effect reach percentile")
    axes[0].set_ylabel("Th2 precision conditional percentile")
    axes[0].set_title("A. Pareto controller landscape", loc="left", fontweight="bold")
    colorbar = fig.colorbar(scatter, ax=axes[0], shrink=0.72)
    colorbar.set_label("Repeatability conditional percentile")

    display = transport.sort_values("mean_delta_auprc")
    labels = {
        "activation_tcr": "TCR activation",
        "th1_effector": "Th1",
        "th2": "Th2",
        "exhaustion_like": "Exhaustion-like",
        "memory_stem_like": "Memory stem-like",
        "cd4_ctl_cytotoxic": "CD4-CTL",
        "treg": "Treg",
        "repeatability": "Repeatability",
    }
    y = np.arange(len(display))
    colors = ["#16856B" if value == "SUPPORTED_EXPLORATORY" else "#53789D" for value in display.verdict]
    for position, (_, row), color in zip(y, display.iterrows(), colors, strict=True):
        axes[1].plot([row.ci_low, row.ci_high], [position, position], color=color, linewidth=2)
        axes[1].scatter(row.mean_delta_auprc, position, color=color, s=42, zorder=3)
        axes[1].text(row.ci_high + 0.01, position, f"q={row.q_perm_bh:.3f}", va="center", fontsize=7)
    axes[1].axvline(0, color="#333333", linestyle="--", linewidth=0.8)
    axes[1].set_yticks(y, [labels[value] for value in display.component])
    axes[1].set_xlabel("Mean held-condition ΔAUPRC (95% block CI)")
    axes[1].set_title("B. Context transport", loc="left", fontweight="bold")

    counts = pd.Series(summary["archetype_counts"]).sort_values()
    archetype_labels = {
        "robust_axis_controller": "Robust axis controller",
        "precise_repeatable_low_reach": "Precise + repeatable, lower reach",
        "precise_context_controller": "Precise context controller",
        "repeatable_broad_mover": "Repeatable broad mover",
        "high_reach_mover": "High-reach mover",
        "repeatable_low_precision": "Repeatable, low Th2 precision",
        "unresolved": "Unresolved",
    }
    axes[2].barh(
        np.arange(len(counts)),
        counts.values,
        color=["#16856B" if "robust" in name else "#9AA5B1" for name in counts.index],
    )
    axes[2].set_yticks(np.arange(len(counts)), [archetype_labels[name] for name in counts.index])
    axes[2].set_xlabel("Genes")
    axes[2].set_title("C. Profile archetypes", loc="left", fontweight="bold")
    for position, value in enumerate(counts.values):
        axes[2].text(value + 5, position, str(value), va="center", fontsize=8)

    fig.suptitle(
        "Controllability Profile v2: expose the trade-offs, do not hide them in one score\n"
        "Exploratory evolution · Marson CD4 screen · no clinical desirability claim",
        fontsize=14,
        fontweight="bold",
    )
    output = ROOT / "figures/controllability_profile_v2.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    print(output)


if __name__ == "__main__":
    main()
