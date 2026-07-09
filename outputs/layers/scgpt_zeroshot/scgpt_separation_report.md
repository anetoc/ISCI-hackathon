# Brief 07 (Gap 13) — scGPT zero-shot embedding separation: **NOT-EVALUABLE**

> **Verdict: NOT-EVALUABLE on the current machine state.** This is a *deferrable* stop, not a
> scientific null. The test did not run, so it neither corroborates nor refutes the locked
> RNA-CCI result (Marson `ISCI_orthogonal` PASS +0.229). Stretch deliverable — does not block
> submission.

## Why (two concurrent blockers, both honest stops)

### 1. Step 0 GATE (data) — FAILED — *primary reason*
scGPT embeds **expression profiles**, not gene names. The correct zero-shot input is one
**pseudobulk expression vector per perturbation** (`GWCD4i.pseudobulk_merged.h5ad`). That matrix
is **not on the machine.** What *is* local is **summary statistics only**:

- `outputs/iec_latent/iec_axis_scores_pseudobulk_stim48.csv` — 11,281 perturbations × {`A_persist`,
  `A_kill`, `A_resist`, `magnitude`} (IEC axis z-scores, i.e. 3–4 numbers per perturbation).
- `results/final/isci_final_ranking.csv` — 2,520 genes (1,260 detectable) with magnitude /
  specificity / ranks.

The brief's Step-0 gate is explicit: *if only summary stats are available, STOP and report
NOT-EVALUABLE — do not embed gene tokens as a substitute.* No gene-token embedding was attempted.

### 2. Negatives — BLOCKED
The locked `expression_matched_negatives` helper matches on `target_baseMean` + `n_cells_target`
per perturbation (the SAME matching as every other CCI test). **Neither column exists in any local
table** — they live in the un-downloaded `GWCD4i` `.obs`. So even the pre-registered matched-negative
set cannot be built locally.

### 3. Compute (VRAM) — BLOCKED (concurrent)
The RTX 6000 Ada was saturated by other users' jobs at run time — **1,246 MiB free** vs the
**≥24 GB** the released scGPT human checkpoint needs (`llama-server` ~24.5 GB + `MedRax` ~22.7 GB).
A subsample cannot fit the free VRAM either. Per the brief's compute posture this is a legitimate
stop; **no foreign job was touched.** (Secondary: scGPT is not installed in any venv, and
`venv-scvi`'s torch cannot initialise CUDA against the current driver — driver 12.6 vs a cu130 torch
build.)

## What the test *would* have been (pre-registered, not run)
- **Positives:** top-30 controllers by `ISCI_primary_rank` among detectable (feasible from the local
  ranking — e.g. IRF1, IKBKB, BCLAF1, TFAP4, …).
- **Negatives:** expression/power-matched, 8 per positive, via the locked helper.
- **Metrics:** silhouette (pos vs neg); logistic-regression **LOO-AUROC + CI** on the 512-dim
  `X_scGPT`; permutation null (1000×) p-value; **direction concordance** Spearman(observed IEC
  loading, embedding-projected direction) + permutation null.
- **PASS iff** silhouette > 0 AND LOO-AUROC CI excludes 0.5 AND perm p < 0.05.

All metrics in `scgpt_separation_result.json` are `null` — nothing was computed and nothing fabricated.

## How to make it evaluable (obtainable path — offered, not executed)
1. Download `GWCD4i.pseudobulk_merged.h5ad` (44.6 GB) [+ `GWCD4i.DE_stats.h5ad` 16.8 GB for
   `target_baseMean`] server-side from the public S3 bucket `genome-scale-tcell-perturb-seq`
   (both keys verified present via HTTP HEAD; ~4.4 TB free on `/mnt/dados2`).
2. Install scGPT into a venv with a torch matching the CUDA 12.6 driver; `use_fast_transformer=False`
   if `flash_attn` does not import cleanly.
3. Run `embed_data` **on CPU** (zero GPU footprint — most considerate while the card is full) *or*
   on GPU once ≥24 GB frees, then run the pre-registered separation + direction-concordance tests.

I did **not** start the 44 GB download / scGPT install / CPU embedding unprompted: the brief flags
this as low-priority stretch, and its compute decision-tree for a full card resolves to
"stop and report." Happy to green-light path (3) on request.

## Triangulation framing (unchanged)
This layer is external corroboration, never proof. Because it did not run it is silent on the CCI
result. A future scGPT **null** would still not refute the RNA-CCI PASS (different representation);
a future **PASS** would be independent-foundation-model corroboration. Discordances become
hypotheses, not errors.

## Artifacts
- `outputs/layers/scgpt_zeroshot/scgpt_separation_result.json` — verdict + null metrics + provenance.
- `figures/scgpt_zeroshot_separation.png` — status/provenance card (no embedding to plot).
- `outputs/layers/scgpt_zeroshot/make_deliverables.py` — the script that captured GPU state and wrote these (no science, no compute).
