# Brief 02 — IEC latent structure at cell level (scVI on the GPU)

**Goal:** confirm that Immune Engagement Capacity (IEC) is a genuine **multi-axis** structure
at single-cell resolution — that A_persist, A_kill, A_resist are orthogonal to each other and
to effect magnitude — using the GPU (RTX 6000). Read `reports/immune_engagement_capacity.md`
for the definition before starting.

## Environment
Use the pip venv from `envs/requirements_machine.txt`. Add scVI: `pip install scvi-tools`
(CUDA build; it will use the RTX 6000). Confirm `import scvi; scvi.settings.dl_pin_memory_gpu_training`
and that torch sees the GPU (`torch.cuda.is_available()`).

## Data
1. **Marson cell-level** — one condition file is enough for this test (start with the SMALLEST:
   D4_Rest.assigned_guide.h5ad ≈ 118 GB is too big to load whole; instead **subsample**).
   Actually: prefer the already-summarized route if cell-level is impractical — but the POINT
   of this brief is cell-level, so: stream/subsample to ~200k cells (scanpy `sc.pp.subsample`
   after backed read, or read a single lane). If even one file is intractable in RAM (125 GB),
   report the practical limit and fall back to the largest tractable subsample — do NOT fabricate.
2. **Functional CAR-T atlas** (ML4BM-Lab / Univ Navarra, Zenodo record 19066393, DOI
   10.5281/zenodo.17213452) — the CD3+CAR+ subset (~414k cells). Cache under
   /mnt/dados2/abel-tsc/data_public/cart/ (already downloaded in Brief 03/04).
   **CRITICAL — scVI source:** the *integrated* atlas object does **NOT** contain `X_scVI` in
   `.obsm`. Do not try to read a pretrained latent from it. Use the dataset's dedicated scVI
   file (the `Python_scVI_*` / `scVI_hub` artifact from the Zenodo record) if present; otherwise
   **train scVI yourself** on the CD3+CAR+ subset (batch key = patient/`orig_ident`). Verify
   `X_scVI` exists and has the expected shape before scoring — if neither route yields a latent,
   report NOT-EVALUABLE for the atlas arm rather than substituting `X_pca`.

## Protocol
1. **scVI latent space per dataset** (batch key = donor/patient): train scVI (default 10–30
   latent dims, ~400 epochs or early-stop), get the batch-corrected latent `X_scVI`.
2. **Score the three IEC axes per cell** with `sc.tl.score_genes` on the log-normalized counts
   (NOT the scVI latent — the axes are gene-set scores): A_persist = mean-z(L1,L2,L3),
   A_kill = L4 killing set, A_resist = −exhaustion set. Gene sets in
   `reports/immune_engagement_capacity.md` §2 and `outputs/movability_gate.json`.
3. **Orthogonality test (the core result):** pairwise Spearman among {A_persist, A_kill,
   A_resist} and each vs a magnitude proxy (total counts / n_genes). Report the 3×3 + magnitude
   correlation matrix, per dataset. Pre-registered: axes are "distinct" if pairwise |ρ|<0.5 and
   vs-magnitude |ρ|<0.3.
4. **Does the multi-axis structure REPLICATE cross-system?** Compare the correlation structure
   between Marson (CD4+ primary) and the CAR-T atlas (clinical products). The prediction: killing
   stays orthogonal to persistence in BOTH (that is the generalizable claim).
   **The "2.5-axis" test (pre-registered from pseudobulk):** at pseudobulk we found A_persist is a
   clean axis (|ρ|<0.08 vs both others) but A_kill and A_resist are **entangled** (ρ≈−0.45). The
   cell-level prediction is therefore *2.5* separable axes, not 3. Confirm or refute at single-cell
   resolution: report whether kill↔resist stays ~−0.45 (entangled → 2.5 axes) or separates
   (|ρ|<0.5 → genuine 3 axes). Either outcome is a real result — state which.
5. **Confounder guard:** compute a CD8-identity score; report each axis's correlation with it,
   and whether A_kill is separable from CD8-identity (partial correlation controlling CD8).

## Deliverables (commit)
- `outputs/iec_latent/iec_latent_report.md` — the correlation matrices (both datasets), the
  orthogonality verdict per axis pair, cross-system replication statement, CD8 guard, and any
  RAM/compute limits hit (honest).
- `outputs/iec_latent/iec_axis_scores.csv` — per-cell axis scores + CD8 + dataset + donor.
- `outputs/iec_latent/iec_axis_decomposition.png` — correlation heatmap(s) + axis-vs-magnitude
  scatter, both systems.
- Commit: `IEC latent: multi-axis orthogonality at cell level (Marson + CAR-T atlas), scVI`.

## Honesty rules (CLAUDE.md)
- If a dataset is too big for 125 GB RAM, subsample honestly and STATE the subsample — never
  claim full-data when you ran a subset.
- Report the orthogonality matrix as-is. If an axis pair is NOT orthogonal (|ρ|>0.5), say so —
  that collapses two axes and is a real finding, not a failure.
- This is a STRUCTURE test, not a clinical test. **No response labels here.** The clinical
  prediction question was already answered in Brief 04 (`outputs/iec_clinical/`): VERDICT = NULL,
  well-powered — no IEC axis predicts CAR-T response under honest leave-one-study-out CV (A_persist
  collapses from AUROC 0.643 patient-out to 0.533 study-out; CD8-fraction baseline beats every
  axis). Do NOT re-run a response predictor or re-open that verdict. This brief only asks whether
  the capacity has multi-axis STRUCTURE at cell level — a descriptive claim, orthogonal to (and not
  rescuing) the null clinical result.
