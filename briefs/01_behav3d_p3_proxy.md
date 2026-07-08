# Brief 01 — BEHAV3D (GSE172325) as a correlational proxy for the TSC P3 test

**Goal:** test whether a transcriptional "serial-killing / synapse" signature co-varies with
a *functional* killing-behavior readout — a REACHABLE, correlational surrogate for the
decisive TSC prediction P3. This is NOT the definitive per-cell perturbation→killing test.

## Scope caveats — state these in the report, do not oversell

- BEHAV3D is **solid-tumor organoids + engineered T cells (TEGs)**, NOT hematologic CAR-T.
- The link is at the **signature level**: GSE172325 holds the scRNA-seq; the live-imaging
  behavioral reference is separate (BioImage Archive S-BIAD448). We are testing whether the
  transcriptome carries a *behavioral-cluster / killing* signature, not re-running imaging.
- Frame the result explicitly as a **generalization / association** check.

## Step 0 — verify the dataset before downloading

1. Confirm GSE172325 on GEO is BEHAV3D (Nat Biotechnol 2022, PMID 35879361,
   DOI 10.1038/s41587-022-01397-w). Record the exact supplementary file names + sizes.
2. Confirm it has: (a) a scRNA-seq count matrix of the engineered T cells, and (b) metadata
   assigning cells to **behavioral clusters** (killing/engagement behavior) or a killing/
   effector signature. If (b) is absent -> **STOP, report NOT-EVALUABLE** (no functional label).

## Step 1 — feasibility gate (before heavy download)

- Total supplementary size must be tractable (it is small, <2 GB expected). If a single file
  is huge, prefer the processed/pseudobulk form. Log sizes first (HTTP HEAD / GEO listing).

## Step 2 — build the two quantities

- **Functional axis (label):** the behavioral/killing classification or effector-killing
  score provided in the metadata. Define which cells are "killer/effector" (positive) vs
  "non-killer" using the AUTHORS' labels — do not invent a threshold if a label exists.
- **TSC transcriptional score per cell:** score the same L1–L4 loadings used in Marson
  (durable state, tissue access, synapse/cytoskeleton, killing gene-set) with
  `scanpy.tl.score_genes`. Reuse the gene sets from `reports/tissue_synapse_capacity.md`
  sections 3/4. Combine into a single TSC score (mean of z-scored loadings, or 1-factor FA).

## Step 3 — the test (pre-registered)

- **Primary:** does the TSC score separate killer vs non-killer cells better than a
  magnitude/activation baseline? Report AUROC and AUPRC for TSC vs the baseline, with a
  bootstrap 95% CI on the difference. Baseline = total activation score (e.g. IFNG/effector
  module) or per-cell total counts.
- **Orthogonality:** Spearman(TSC, activation-magnitude) — expect it to add signal beyond
  magnitude, mirroring the CCI logic.
- **Honest verdict:** PASS (TSC beats baseline, CI excludes 0), NULL (no separation), or
  NOT-EVALUABLE (no functional label). Any outcome is fine — report it straight.

## Step 4 — deliverables (commit these)

- `outputs/behav3d_p3/behav3d_p3_report.md` — dataset provenance, what the label is, the
  numbers (AUROC/AUPRC TSC vs baseline + CI), the verdict, and the scope caveats above.
- `outputs/behav3d_p3/behav3d_tsc_scores.csv` — per-cell TSC score + label + baseline.
- `outputs/behav3d_p3/behav3d_p3.png` — TSC score distribution by killer/non-killer +
  ROC or PR curve (TSC vs baseline).
- Commit message: `BEHAV3D P3 proxy: <verdict> (TSC vs activation baseline, GSE172325)`.

## What to hand back to Claude Science

Paste the report's verdict paragraph + the AUROC/AUPRC numbers, or just push and tell Abel
the commit is up. Claude Science reviews, checks the honesty of the framing, and writes the
next brief.
