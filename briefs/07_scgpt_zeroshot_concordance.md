# Brief 07 (Gap 13) — Foundation-model triangulation: scGPT zero-shot embedding separation

> **Purpose (triangulation, not proof).** Ask whether an INDEPENDENT foundation model, with NO
> access to our labels or our ISCI score, places our top magnitude-conditional controllers in a
> distinguishable region of its embedding space relative to expression/power-matched negatives. A
> positive result is external corroboration; a null is reported honestly. This is **zero-shot only** —
> no fine-tuning on our labels — precisely to avoid the circularity that would inflate the result.

## Compute posture
GPU machine (vuno-idor, RTX 6000). scGPT needs ≥24 GB VRAM for the released human checkpoint; the
48 GB card is fine, but the other users' jobs saturate it — **check `nvidia-smi` first and, if the
card is full, either wait for a window or run the embedding on a subsample that fits the free VRAM.**
Do NOT kill llama-server/MedRax. This is a stretch deliverable; it does not block submission.

## Environment
Add scGPT to the `tsc` venv (or a sibling): `pip install scgpt` plus its checkpoint directory
(`args.json`, `best_model.pt`, `vocab.json` — released human model, ~200 MB). If `flash_attn` is
absent, pass `use_fast_transformer=False` (see gotchas below).

## Inputs (already in the repo / on the machine)
- `results/final/isci_final_ranking.csv` — locked ranking (`ISCI_orthogonal`, `ISCI_primary_rank`,
  `known_regulator`, `detectable_effect`).
- The Marson pseudobulk perturbation matrix already used for the IEC axes
  (`outputs/iec_latent/…pseudobulk…` or `pseudobulk_merged.h5ad`) — one profile per perturbation.

## Step 0 — GATE (stop if it fails)
scGPT embeds **cells/expression profiles**, not gene names. The correct zero-shot test is on
**perturbation pseudobulk profiles**: each perturbation = one pseudobulk expression vector; embed
those, then ask whether the embeddings of top-controller perturbations separate from matched-negative
perturbations. If no per-perturbation expression profile is available (only summary stats), STOP and
report NOT-EVALUABLE — do not embed gene tokens as a substitute.

## Step 1 — Zero-shot embedding
```python
from scgpt.tasks import embed_data
emb = embed_data(adata_pseudobulk, model_dir="<checkpoint dir>",
                 gene_col="<var symbol col>", use_fast_transformer=False)
# emb.obsm["X_scGPT"] : n_perturbations x 512
```

## Step 2 — Separation test (pre-specified, label-blind to scGPT)
- Positives = top-N controllers by `ISCI_primary_rank` among detectable (e.g. N=30).
- Negatives = expression/power-matched via the locked `expression_matched_negatives` helper (SAME
  matching as every other CCI test — `target_baseMean` + `n_cells_target`), 8 per positive.
- Metric: in scGPT embedding space, is the positive/negative label linearly separable beyond chance?
  Report **silhouette** of pos-vs-neg, and a logistic-regression **AUROC with leave-one-out CV** on
  the 512-dim embedding (LOO to be honest at small N). Permutation null (shuffle labels 1000×) for a
  p-value.
- **Direction concordance (Test 2):** for the top controllers, does the scGPT-predicted shift
  direction agree with the observed IEC-axis loading sign? Report Spearman(observed loading,
  embedding-projected direction) with a permutation null.

## Step 3 — Honest verdict
- PASS: silhouette > 0 AND LOO-AUROC CI excludes 0.5 AND permutation p < 0.05.
- NEAR/NULL: report the point estimates and CIs; discordant genes become hypotheses, not errors.
- Explicitly state this is triangulation: scGPT never saw our labels or ISCI score, so separation is
  external corroboration; non-separation does not refute the RNA CCI result (different representation).

## Deliverables
- `outputs/layers/scgpt_zeroshot/scgpt_separation_result.json` — silhouette, LOO-AUROC + CI, perm-p,
  direction-concordance Spearman + perm-p, N pos/neg, checkpoint id, compute provenance (GPU/subsample).
- `outputs/layers/scgpt_zeroshot/scgpt_separation_report.md` — verdict + honest framing.
- `figures/scgpt_zeroshot_separation.png` — embedding UMAP colored by pos/neg + the AUROC/silhouette.
- Commit + push; ping the main session with the verdict.

## Gotchas (from the scGPT skill)
- `use_fast_transformer=True` is the default and needs flash-attn; set `False` unless flash_attn
  imports cleanly.
- Unmatched gene symbols are dropped — set `gene_col` to the real symbol column in `.var`.
- Checkpoint is a raw directory, not an HF repo id.
