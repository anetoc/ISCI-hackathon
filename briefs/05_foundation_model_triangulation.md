# Brief 05 (Phase 11) — Foundation-model triangulation of the controllers (GPU)

**Goal:** ask whether an **independent** foundation model — one that never saw the Marson screen's
regulator labels — agrees that the ISCI top controllers are distinguished. This is an *external
concordance* test (the "A" idea done honestly), NOT a new controllership score and NOT a way to
rescue anything. A positive result is corroboration; a null is a real, reportable result.

Read `reports/result_lock.md` and `reports/conditional_controllability_invariant.md` first. The
locked ranking (`results/final/isci_final_ranking.csv`, `ISCI_orthogonal`) is the input; do not
recompute or modify it.

## Environment
GPU machine (RTX 6000, 48 GB). scGPT needs ≥24 GB VRAM + the released human checkpoint
(`args.json`, `best_model.pt`, `vocab.json`). Install into the `tsc`/`venv-tsc` env:
`pip install scgpt` (pass `use_fast_transformer=False` if flash-attn does not import — expected).
Confirm `torch.cuda.is_available()` and `GeneVocab.from_file(vocab.json)` loads (~60,697 genes).

## The test — gene-embedding concordance (primary)
scGPT carries a learned **gene embedding** (the token embedding over its 60k-gene vocab). The
prediction: if ISCI controllership captures something real about gene *regulatory role*, the top
controllers should occupy a **non-random region** of scGPT's gene-embedding space relative to
magnitude-matched non-controllers.

1. **Extract gene embeddings** for all genes in the locked ranking that are in scGPT's vocab
   (map by symbol; report the mapped fraction). Use the token/gene embedding matrix from the
   checkpoint, not cell embeddings.
2. **Positives / matched negatives:** positives = detectable-set genes in the ISCI top decile
   (or known_regulator==True, run BOTH as pre-registered variants). Negatives = **expression/
   power-matched** non-controllers via the locked helper `expression_matched_negatives`
   (`outputs/marson_obs_matching.parquet`, match on n_cells_target). This is the whole point —
   an unmatched comparison just re-finds magnitude.
3. **Concordance metric (pre-registered, pick ONE primary before running):**
   - *Neighborhood coherence:* mean pairwise cosine similarity among positives' scGPT embeddings
     vs the matched-negative null distribution (permutation p over 1,000 matched draws).
   - *Linear separability (secondary):* logistic regression positives-vs-matched-neg on scGPT
     embedding, honest CV AUROC; report vs a magnitude-only baseline on the SAME split.
4. **Verdict:** CONCORDANT if positives are significantly more coherent / separable than the
   matched-negative null (perm-p<0.05); NULL otherwise. Either way it's descriptive external
   evidence, never a change to the locked result.

## Guards (mandatory — CLAUDE.md)
- **Matched negatives, always.** An unmatched positive-vs-rest comparison is invalid here; state
  the matching covariate and n_matched.
- **scGPT never saw the labels** — that's the point; do not fine-tune on Marson regulators (that
  would manufacture the concordance you're testing for). Zero-shot embeddings only.
- Report the **vocab mapping fraction**; if <60% of ranking genes map, say so — it bounds the test.
- If the concordance is null, that is the result. A foundation model disagreeing is informative
  about the limits of the controllership signal, not a failure to fix.

## Deliverables (commit)
- `outputs/fm_triangulation/fm_concordance_report.md` — mapped fraction, primary metric, matched
  null, perm-p, verdict (CONCORDANT / NULL), and the honest caveats.
- `outputs/fm_triangulation/fm_gene_scores.csv` — per-gene scGPT neighborhood/separability score
  joined to `ISCI_orthogonal`, positive/negative label, matched flag.
- `outputs/fm_triangulation/fm_embedding_umap.png` — scGPT gene-embedding UMAP, positives vs
  matched negatives highlighted.
- Commit: `Phase 11: scGPT gene-embedding concordance with ISCI controllers (matched-negative, zero-shot) — <verdict>`.

## Optional stretch (only if primary is clean and time remains)
- **evo2 sequence-level** view: for the top controllers, score whether their promoter/regulatory
  windows carry higher variant-effect density than matched negatives (evo2 skill). Fully separate,
  fully optional — do not start it until the scGPT arm is committed.
