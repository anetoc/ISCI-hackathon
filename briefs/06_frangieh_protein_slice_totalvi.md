# Brief 06 (Layer 1) — Protein-level controllership slice on Frangieh (totalVI, CPU)

> **Compute posture (read first): this runs on CPU. Do NOT wait for the GPU.** totalVI trains in
> minibatches, so it runs fine on CPU — the GPU only makes training *faster per epoch*, it is not
> required. Everything else in this brief (feature construction, the CCI test) is CPU-only already.
> The RTX 6000 is usually saturated by other users' jobs (llama-server, MedRax) — do not kill them
> and do not block on them. Force `accelerator="cpu"` and subsample to ~80–100k cells (Step 1). At
> ~10 positives the power is set by the positive count, not the cell count, so the subsample costs
> almost nothing. Expected wall time on the 48-core machine: ~15–30 min end to end. If a GPU window
> opens and someone wants full fidelity later, the same script runs unchanged with
> `accelerator="gpu"` — but the submission does not depend on that.

**Goal.** Fill the **first non-RNA slice** of the controllability tensor:
`T[gene, immune_evasion_axis, Frangieh, PROTEIN_coherence]`. Ask one falsifiable question with the
locked operator: **does protein-level axis-specificity/coherence add controller information beyond
RNA-level (and beyond magnitude)?** This tests whether our RNA controllership signal is a
transcriptional shadow of a protein-level control event, or independent protein information.

This is Layer 1 of `reports/INTEGRATION_ARCHITECTURE.md`. Read that §2.1 + §3.2 first. The operator
is the SAME `isci-controllership` skill used for RNA — do **not** invent a new test.

## Environment
vuno-idor, `/mnt/dados2/abel-tsc/venv-tsc` (or the dedicated scvi-tools venv already installing).
totalVI ships in scvi-tools (the same library used in Phase 5, which trained the RNA-only **scVI**
model — totalVI is its joint RNA+protein sibling, used here for the first time). **Run on CPU — do not check for or require
CUDA.** 48 cores / 125 GB RAM is more than enough for a subsampled totalVI. Just confirm
`import scvi, anndata` imports cleanly; ignore `torch.cuda.is_available()`.

## Step 0 — GET THE PROTEIN MATRIX (the RNA run did not use it)
The Phase-6 run used `data_public/external_perturb/FrangiehIzar2021_RNA.h5ad` — **RNA only**.
Perturb-CITE-seq has a companion **protein/ADT** matrix. Obtain it:
- scPerturb hosts Frangieh (Zenodo). Look for the protein/ADT export
  (`FrangiehIzar2021_protein.h5ad` or an `.obsm['protein']` / ADT layer in a combined object).
- Use `aria2c -x16 -s16` (Zenodo throttles single-stream ~525 KB/s).
- **GATE:** if no protein/ADT matrix with per-cell antibody counts and matching cell barcodes to the
  RNA object exists, **STOP and report NOT-EVALUABLE for the protein slice** — do not fabricate a
  protein layer from RNA. Report which files you found.

## Step 1 — totalVI joint latent (protein readout), CPU + subsample
1. Build a paired AnnData: RNA counts in `.X`/`layers['counts']`, protein counts in
   `.obsm['protein_expression']`, cell barcodes intersected with the RNA object used in Phase 6.
   Batch key = `perturbation_2` (the 3 conditions Control/IFNγ/Co-culture) or sample, matching the
   RNA run's `sample_col`.
2. **Subsample to ~80–100k cells before training** — stratify by perturbation so every positive/
   negative target keeps enough cells for a stable per-perturbation protein effect (e.g. keep all
   cells for perturbations with < 400 cells, cap the rest at 400). Record the exact n_cells kept and
   the per-perturbation counts. This is a power-neutral speedup: the test has ~10 positives, so cell
   count is not the binding constraint.
3. `scvi.model.TOTALVI.setup_anndata(...)`; **train on CPU**:
   `model.train(accelerator="cpu", max_epochs=200, early_stopping=True)` (early stopping usually
   halts well before 200; ~10–20 min on 48 cores at this size). Do **not** pass a GPU device. Save
   the model + the **denoised protein expression**
   (`get_normalized_expression(..., protein_list=..., n_samples=25)`) per cell.
4. Sanity: confirm protein panel identity and that denoised protein tracks known markers (e.g. HLA/
   B2M surface loss under the positives). Report the panel size, mapped antibodies, and the n_cells
   used after subsampling.

## Step 2 — protein feature X, then the SAME operator
For each perturbation, compute the protein analogues of the RNA features, then run the locked test:
- **Protein axis-specificity S_prot(g):** concentration of the perturbation's *protein-level* effect
  on the immune-evasion axis (IFNγ-response surface proteins: HLA-A/B/C/E, B2M, PD-L1/CD274, etc.),
  relative to total protein effect. Mirror the RNA `S` definition on the protein readout.
- **Protein coherence R_prot(g):** reproducibility of the protein effect direction across the
  condition/replicate structure (`perturbation_2`).
- **Residualize both against protein-effect magnitude** (protein n-DE or total protein shift) with the
  locked `residualize`/percentile helpers.
- **Matched negatives:** reuse the **exact** Phase-6 positive set from `frangieh_config.py`
  `CONFIG['positives']` — all 13 genes: B2M, CD274, HLA-A, HLA-B, HLA-C, HLA-E, IFNGR1, IFNGR2,
  IRF3, JAK1, JAK2, STAT1, TAPBP. Read the config, do not retype from this list. Then draw
  **expression/power-matched negatives** with the locked `expression_matched_negatives` (match on
  n_cells / base expression — protein-appropriate covariate).
- **Verdict:** run `bootstrap_auprc_gain` + `conditional_lr_test` (the locked CondInfo). Report
  ΔAUPRC, CI, perm/LR p, PASS/FAIL, exactly as the RNA slice.

## Step 3 — the incremental question (the actual point)
The headline is not "does protein pass" alone; it is **does protein add over RNA**:
1. Join protein `C_prot` to the RNA `C` from `frangieh_perturbcite_scores.csv` per gene.
2. Report Spearman(C_prot, C_rna) — are they redundant or complementary?
3. Conditional LR: does `C_prot` add to controller status **given `C_rna` and magnitude**? This is
   the tensor's reason to exist. If protein is redundant with RNA, say so (a clean negative). If it
   adds, that is a genuinely new evidence layer.

## Guards (CLAUDE.md — non-negotiable)
- Protein feature from **denoised protein counts**, never re-derived from RNA (that would fabricate
  the independence you are testing).
- Expression/power-matched negatives, always; state covariate and n_matched.
- Underpowered is expected (~10 positives, like RNA). Report the honest verdict; a near-miss is fine.
- Do NOT touch the locked RNA result or the clinical null. This writes a NEW tensor slice only.

## Deliverables (commit to repo)
- `outputs/layers/frangieh_protein/protein_cci_result.json` — canonical contract (gain, ci, lr_p,
  verdict) matching `cci_result.json` schema, plus `spearman_protein_vs_rna` and
  `lr_protein_given_rna_and_magnitude`.
- `outputs/layers/frangieh_protein/protein_scores.csv` — per-gene S_prot, R_prot, resid, C_prot,
  joined to RNA C.
- `outputs/layers/frangieh_protein/protein_slice_report.md` — verdict + the incremental-over-RNA
  finding + honest caveats + panel description + **compute provenance line** (CPU, n_cells after
  subsample, per-perturbation counts, epochs to early-stop).
- `outputs/layers/frangieh_protein/totalvi_model/` — saved model (provenance).
- Commit: `Layer 1: Frangieh protein controllership slice (totalVI) — <verdict>, adds/redundant over RNA`.

## What comes back to the local operator
The `protein_cci_result.json` is the interface. Once committed and synced, the local side ingests it
as a tensor slice `T[·, immune_evasion, Frangieh, PROTEIN]` and adds a per-modality panel to the
dashboard — no GPU needed for that half. The scaffold for the local side is in
`isci/run_layer.py` (being built alongside this brief).