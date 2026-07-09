#!/usr/bin/env python
"""Brief 07 (Gap 13) — scGPT zero-shot embedding-separation triangulation.

This run terminated at the pre-registered Step 0 GATE (data) with a concurrent
compute blocker (VRAM). It performs NO embedding and fabricates NO metrics: it
records exactly why the test is NOT-EVALUABLE on the current machine state and
what would make it evaluable. Honest-stop per CLAUDE.md hard rule #1 and the
brief's Step 0 gate.
"""
import json, subprocess, datetime, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR = "outputs/layers/scgpt_zeroshot"
FIG = "figures/scgpt_zeroshot_separation.png"


def gpu_snapshot():
    try:
        q = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=30).stdout.strip()
        name, total, used, free = [x.strip() for x in q.split(",")]
        procs = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=30).stdout.strip()
        return {"gpu": name, "memory_total_MiB": int(total),
                "memory_used_MiB": int(used), "memory_free_MiB": int(free),
                "compute_apps": [l.strip() for l in procs.splitlines() if l.strip()]}
    except Exception as e:
        return {"error": repr(e)}


def git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return None


gpu = gpu_snapshot()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

result = {
    "task": "Brief 07 / Gap 13 — scGPT zero-shot embedding-separation triangulation",
    "verdict": "NOT-EVALUABLE",
    "verdict_scope": "on current machine state (not a scientific null); test is deferrable, not refuted",
    "generated_utc": now,
    "git_sha": git_sha(),

    "why_not_evaluable": {
        "primary_gate": "STEP-0 (data) FAILED",
        "step0_reason": (
            "scGPT embeds per-cell/per-perturbation EXPRESSION PROFILES, not gene names. "
            "The required input — one pseudobulk expression vector per perturbation "
            "(GWCD4i.pseudobulk_merged.h5ad) — is NOT present on the machine. Only SUMMARY "
            "STATISTICS are local: per-perturbation IEC axis z-scores "
            "(outputs/iec_latent/iec_axis_scores_pseudobulk_stim48.csv: perturbation, "
            "A_persist, A_kill, A_resist, magnitude) and the ISCI ranking "
            "(results/final/isci_final_ranking.csv: magnitude/specificity/ranks). "
            "The brief's Step-0 gate explicitly forbids substituting gene tokens for "
            "expression profiles, so with only summary stats available the honest call is "
            "NOT-EVALUABLE. No gene-token embedding was attempted."
        ),
        "negatives_blocker": (
            "The locked expression_matched_negatives helper matches on "
            "['target_baseMean','n_cells_target'] per perturbation. Neither column exists in "
            "any local table (they live in the un-downloaded GWCD4i .obs), so the "
            "pre-registered matched-negative set cannot be constructed locally either."
        ),
        "concurrent_compute_blocker": (
            "RTX 6000 Ada is saturated by other users' jobs — only "
            f"{gpu.get('memory_free_MiB','?')} MiB free vs the >=24 GB the released scGPT human "
            "checkpoint needs. A subsample cannot fit the free VRAM either. Per the brief's "
            "compute posture this is a legitimate stop; no foreign job was touched. "
            "(Secondary: scGPT is not installed in any venv, and venv-scvi's torch cannot "
            "initialise CUDA against the current driver — driver 12.6 vs torch cu130 build.)"
        ),
    },

    "data_availability": {
        "expression_matrix_on_machine": False,
        "obtainable_public": True,
        "s3_bucket": "genome-scale-tcell-perturb-seq",
        "s3_keys_verified_via_HEAD": {
            "marson2025_data/GWCD4i.pseudobulk_merged.h5ad": "44.6 GB (one profile per perturbation — the scGPT input)",
            "marson2025_data/GWCD4i.DE_stats.h5ad": "16.8 GB (per-perturbation x gene logFC/zscore/baseMean; provides target_baseMean for negatives)",
        },
        "local_summary_stats_only": [
            "outputs/iec_latent/iec_axis_scores_pseudobulk_stim48.csv (11281 perts x {A_persist,A_kill,A_resist,magnitude})",
            "results/final/isci_final_ranking.csv (2520 genes; 1260 detectable)",
        ],
    },

    "pre_registered_design_not_run": {
        "positives": "top-30 controllers by ISCI_primary_rank among detectable (feasible from local ranking; e.g. IRF1, IKBKB, BCLAF1, TFAP4, ...)",
        "negatives": "expression/power-matched via locked expression_matched_negatives (target_baseMean + n_cells_target), 8 per positive",
        "metrics": "silhouette(pos vs neg); logistic-regression LOO-AUROC + CI on 512-dim X_scGPT; permutation null (1000x) p-value; direction concordance Spearman(observed IEC loading, embedding-projected direction) + perm null",
        "pass_criterion": "silhouette>0 AND LOO-AUROC CI excludes 0.5 AND perm p<0.05",
    },

    "metrics": {  # explicitly null — nothing computed, nothing fabricated
        "silhouette": None,
        "loo_auroc": None, "loo_auroc_ci": None,
        "permutation_p": None,
        "direction_concordance_spearman": None, "direction_concordance_perm_p": None,
        "n_positive": None, "n_negative": None,
    },

    "compute_provenance": {
        "checkpoint_id": "scGPT released human checkpoint — NOT obtained (no embedding run)",
        "gpu_snapshot": gpu,
        "subsample": "n/a — no embedding attempted",
        "no_foreign_job_touched": True,
    },

    "how_to_make_evaluable": [
        "Download GWCD4i.pseudobulk_merged.h5ad (44.6 GB) [+ DE_stats.h5ad 16.8 GB for target_baseMean] server-side from the public S3 bucket.",
        "Install scGPT into a venv with a torch matching the CUDA 12.6 driver; use_fast_transformer=False if flash_attn does not import.",
        "Run embed_data on CPU (zero GPU footprint — most considerate while the card is full) OR on GPU once >=24 GB frees, then run the pre-registered separation + direction-concordance tests above.",
    ],

    "triangulation_framing": (
        "This is external corroboration, not proof. Because it did not run, it neither "
        "corroborates nor refutes the locked RNA-CCI result (Marson ISCI_orthogonal "
        "PASS +0.229). A future scGPT null would still not refute the CCI result "
        "(different representation); a PASS would be independent-model corroboration."
    ),
}

import os
os.makedirs(OUTDIR, exist_ok=True)
with open(f"{OUTDIR}/scgpt_separation_result.json", "w") as f:
    json.dump(result, f, indent=2)

# ---- Provenance / status figure (no embedding exists to plot) ----
fig, ax = plt.subplots(figsize=(10, 7.2))
ax.axis("off")
ax.text(0.5, 0.965, "scGPT zero-shot embedding separation — Brief 07 / Gap 13",
        ha="center", va="top", fontsize=14, fontweight="bold")
ax.text(0.5, 0.915, "VERDICT: NOT-EVALUABLE  (deferrable, not a scientific null)",
        ha="center", va="top", fontsize=13, color="#b00020", fontweight="bold")

free = gpu.get("memory_free_MiB", 0)
lines = [
    ("STEP-0 GATE (data)  —  FAILED",  "#b00020"),
    ("  scGPT embeds expression profiles, not gene names.", "#222"),
    ("  Required per-perturbation pseudobulk matrix (GWCD4i.pseudobulk_merged.h5ad)", "#222"),
    ("  is NOT on the machine — only SUMMARY STATS are local (axis z-scores, ISCI ranks).", "#222"),
    ("  Gate forbids gene-token substitution -> stop. No embedding attempted.", "#222"),
    ("", "#222"),
    ("NEGATIVES  —  BLOCKED", "#b00020"),
    ("  expression_matched_negatives needs target_baseMean + n_cells_target;", "#222"),
    ("  absent locally (live in the un-downloaded GWCD4i .obs).", "#222"),
    ("", "#222"),
    (f"COMPUTE (VRAM)  —  BLOCKED  ({free} MiB free vs >=24 GB needed)", "#b00020"),
    ("  RTX 6000 Ada saturated by other users (llama-server + MedRax).", "#222"),
    ("  Subsample cannot fit free VRAM. No foreign job touched.", "#222"),
    ("", "#222"),
    ("OBTAINABLE PATH (offer, not run):", "#1a6e1a"),
    ("  download pseudobulk_merged (44.6 GB, public S3) -> install scGPT", "#1a6e1a"),
    ("  -> embed on CPU or when >=24 GB frees -> pre-registered separation test.", "#1a6e1a"),
]
y = 0.85
for txt, col in lines:
    ax.text(0.06, y, txt, ha="left", va="top", fontsize=10.3, color=col,
            family="monospace" if txt.startswith("  ") else "sans-serif",
            fontweight="bold" if (txt and not txt.startswith("  ")) else "normal")
    y -= 0.045

prov = f"git {git_sha()[:10] if git_sha() else 'n/a'}  |  {now}  |  GPU: {gpu.get('gpu','?')}  |  checkpoint: not obtained"
ax.text(0.5, 0.02, prov, ha="center", va="bottom", fontsize=8, color="#666")
fig.savefig(FIG, dpi=140, bbox_inches="tight")
print("wrote", f"{OUTDIR}/scgpt_separation_result.json")
print("wrote", FIG)
print("free VRAM MiB:", free)
