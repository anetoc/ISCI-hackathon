#!/usr/bin/env python
"""Plot the frozen post-hoc controllability decomposition stress tests."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    t1 = json.loads((ROOT / "outputs/decomposition/t1_axis_null.json").read_text())
    t1_scores = pd.read_parquet(ROOT / "outputs/decomposition/t1_axis_null_scores.parquet")
    t2 = pd.read_csv(ROOT / "outputs/decomposition/t2_component_support.csv")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.8), constrained_layout=True)
    colors = {"SUPPORT": "#167D64", "UNSUPPORTED": "#B2483B", "NOT_EVALUABLE": "#8A8F98"}

    axis_labels = {
        "activation_tcr": "TCR activation",
        "th1_effector": "Th1 effector",
        "th2": "Th2",
        "exhaustion_like": "Exhaustion-like",
        "memory_stem_like": "Memory stem-like",
        "cd4_ctl_cytotoxic": "CD4-CTL",
        "treg": "Treg",
    }
    results = t1["results"]
    y = np.arange(len(results))[::-1]
    for position, result in zip(y, results, strict=True):
        name = result["axis"]
        verdict = result["verdict"]
        if verdict == "NOT_EVALUABLE":
            axes[0].scatter(0, position, marker="x", s=65, color=colors[verdict], linewidth=2)
            axes[0].text(0.015, position, f"NE ({result['n_admissible']}/200)", va="center", color=colors[verdict])
            continue
        scores = t1_scores[(t1_scores.axis == name) & ~t1_scores.is_real_axis]
        low, median, high = scores.delta_auprc_oof.quantile([0.05, 0.5, 0.95])
        axes[0].plot([low, high], [position, position], color="#B9BEC6", linewidth=5, solid_capstyle="round")
        axes[0].scatter(median, position, color="#69717C", s=22, zorder=3, label="pseudo-axis median" if position == y[0] else None)
        axes[0].scatter(
            result["real_gain"], position, color=colors[verdict], s=58, edgecolor="white", linewidth=0.7, zorder=4
        )
    axes[0].axvline(0, color="#333333", linestyle="--", linewidth=0.8)
    axes[0].set_yticks(y, [axis_labels[result["axis"]] for result in results])
    axes[0].set_xlabel("OOF ΔAUPRC: effect reach → + axis precision")
    axes[0].set_title("A. Adversarial axis null (T1)", loc="left", fontweight="bold")
    axes[0].text(
        0.01,
        -0.16,
        "Gray interval = pseudo-axis 5th–95th percentile; colored point = frozen real axis.\nNE = <90% structurally admissible pseudo-axes.",
        transform=axes[0].transAxes,
        color="#59616B",
    )

    evaluated = t2[t2.verdict != "NOT_EVALUABLE"].copy()
    evaluated["label"] = evaluated["dataset"].map(
        {"marson_cd4": "Marson CD4", "thp1_myeloid": "THP-1 myeloid"}
    ) + " · " + evaluated["component"].map({"precision": "precision", "repeatability": "repeatability"})
    y2 = np.arange(len(evaluated))[::-1]
    component_colors = {"precision": "#276FBF", "repeatability": "#9B5DE5"}
    for position, (_, row) in zip(y2, evaluated.iterrows(), strict=True):
        axes[1].plot([row.ci_low, row.ci_high], [position, position], color=component_colors[row.component], linewidth=2)
        axes[1].scatter(row.delta_auprc_oof, position, color=component_colors[row.component], s=55, zorder=3)
        axes[1].text(row.ci_high + 0.012, position, f"q={row.q_perm_bh:.3f}", va="center", fontsize=8)
    axes[1].axvline(0, color="#333333", linestyle="--", linewidth=0.8)
    axes[1].set_yticks(y2, evaluated.label)
    axes[1].set_xlabel("OOF ΔAUPRC over effect reach (95% block-bootstrap CI)")
    axes[1].set_title("B. Component-support transport (T2)", loc="left", fontweight="bold")
    axes[1].text(
        0.01,
        -0.16,
        "BH-FDR includes all 10 planned tests; Schmidt, Norman and RPE1 are NOT_EVALUABLE.\nPositive direction is retained as uncertainty unless CI > 0 and q < 0.05.",
        transform=axes[1].transAxes,
        color="#59616B",
    )
    fig.suptitle(
        "Perturbational controllability is axis- and evidence-dependent\n"
        "Post-hoc stress tests · frozen ISCI ranking unchanged",
        fontsize=15,
        fontweight="bold",
    )
    output = ROOT / "figures/controllability_decomposition.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    print(output)


if __name__ == "__main__":
    main()
