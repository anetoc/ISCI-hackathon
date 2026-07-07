# Method Specification — Immune-State Controllability Index (ISCI)

> Technical spec, ready to implement. Companion to `related_work.md`.
> Scope: define ISCI precisely, its 5 components, aggregation, null model, benchmarks, and code architecture.
> Data substrate: Marson CD4+ genome-scale Perturb-seq (`GWCD4i.DE_stats.h5ad`, `GWCD4i.pseudobulk_merged.h5ad`).

---

## 1. Objects & notation

- Perturbations (genes knocked down) `g ∈ G` (~10k targets that pass QC).
- Measured genes `j ∈ J` (10,282 genes in `DE_stats`).
- Conditions `c ∈ {Rest, Stim8hr, Stim48hr}`.
- Functional axes `a ∈ A` (activation, Th1, Th2, exhaustion-like, memory-like, CD4-CTL/cytotox, Treg, Tfh).
- From `DE_stats.h5ad` per (g,c): effect vector **z**_{g,c} ∈ ℝ^J (layer `zscore` = logFC/lfcSE),
  plus `log_fc`, `adj_p_value`, and QC/reproducibility fields in `.obs`.
- Axis signature vector **u**_a ∈ ℝ^J : signed gene loadings for axis `a` (see §3).

Everything is computed per condition `c`, then aggregated across conditions (default: max-abs with sign kept,
plus we report per-condition profiles).

---

## 2. Design principles

1. **Direction matters, not just magnitude.** A controller pushes the state *along a clinically meaningful
   axis*, not just "perturbs a lot of genes".
2. **Reproducible or it doesn't count.** Weight by cross-donor/cross-guide agreement already in the data.
3. **Control = network position, independent of effect size.** Driver-node in the GRN.
4. **Generalizable = models agree.** In-silico prediction concordance.
5. **Real controllers land in a stable attractor.** Penalize "hallucinatory intermediates".
6. **Beat simple baselines explicitly.** DE magnitude and effect-size are strong; ISCI must add signal (ablation).

---

## 3. Functional axes (signatures **u**_a)

Two complementary sources, combined:
- **Data-native signatures** already shipped with the dataset: Th1/Th2 polarization DE
  (`Th2_Th1_polarization_signature_DE_results_full.suppl_table.csv`) and activation/polarization
  regulator coefficients. Use their z-scores as loadings.
- **Curated marker sets** projected via a scoring method (decoupler `run_ulm`/`run_wsum` or `scanpy.tl.score_genes`):
  - activation: CD69, IL2RA, CD25, MKI67, HLA-DRA, TNFRSF9
  - Th1: TBX21, IFNG, CXCR3, STAT1; Th2: GATA3, IL4, IL5, IL13
  - exhaustion-like: TOX, PDCD1, LAG3, HAVCR2, TIGIT, ENTPD1, NR4A1/2/3
  - memory/stem-like: TCF7, LEF1, IL7R, CCR7, SELL, BACH2, ID3, FOXO1 targets
  - CD4-CTL/cytotoxicity: GZMA, GZMB, PRF1, GNLY, NKG7, KLRG1
  - Treg: FOXP3, IL2RA, IKZF2; Tfh: CXCL13, PDCD1, BCL6
- Normalize **u**_a to unit L2 norm. Axis validity checked with IDOR immunologists (see related_work §7).

---

## 4. The five components (each mapped to [0,1] via rank/percentile)

### M — Directional movement (empirical)
Projection of the perturbation effect onto the axis:
```
m_raw(g,a,c) = < z_{g,c} , u_a >  /  ||z_{g,c}||        # cosine-like; sign = direction along axis
M(g,a,c)     = percentile_rank( |m_raw(g,a,c)| over g )  # magnitude of movement
sign_M(g,a,c) = sign(m_raw)                              # keep direction for interpretation
```
Rationale: high when KD moves the transcriptome coherently along axis `a`.

### R — Reproducibility (empirical weight)
From `DE_stats.obs`: `donor_correlation_hits_mean`, `guide_correlation_signif`, `n_guides`,
`ontarget_significant`. Combine into a stability weight:
```
R(g,c) = percentile_rank( w1*donor_corr_hits_mean + w2*guide_corr_signif ) , gated by ontarget_significant
```
Default w1=w2=0.5. Perturbations failing on-target KD or with NaN correlations get down-weighted (not dropped;
flagged). R multiplies the final score (a controller must be reproducible).

### D — Structural network control (topology)
1. Infer a GRN on measured genes (options, in order of preference/robustness):
   - `decoupler` + **CollecTRI** priors (TF→target) intersected with data-supported edges; OR
   - GRNBoost2 / BetterBoost using the perturbation structure; OR
   - CEFCON's GRN constructor (if time permits).
2. Apply **network control theory** to the directed GRN:
   - **MFVS** (minimum feedback vertex set) and **MDS** (minimum dominating set) → candidate driver nodes.
   - Influence/centrality score (out-degree in regulon, PageRank, or CEFCON-style attention).
```
D(g) = percentile_rank( α*1[g ∈ driver_set] * influence(g) + (1-α)*centrality(g) )
```
Rationale: captures *control position* independent of effect magnitude. **This is what separates
"controller" from "associate".**

### A — In-silico concordance (generalization)
Predict KD effect with an independent model and check agreement with observed direction on axis `a`:
- **CellOracle** (GRN-based in-silico KO) and/or **GEARS**; optionally **State/scGPT** embeddings.
```
a_pred(g,a) = < predicted_shift(g) , u_a > / ||predicted_shift(g)||
A(g,a) = percentile_rank( positive_agreement( a_pred , m_raw ) )   # rewards concordant direction & magnitude
```
Discordance is reported honestly (a candidate strong empirically but not predicted may be novel or noisy).

### S — Target-state stability (novel component)
After the (observed or simulated) shift, is the resulting state a *deep attractor* or an unstable intermediate?
Operationalize via **geometric coherence** (arXiv 2604.16642) in a foundation-model / PCA embedding:
```
# Embed pseudobulk (perturbed vs NTC) in latent space (scVI / scGPT / PCA)
S(g,a,c) = percentile_rank( coherence(neighborhood of perturbed state) )
         # high = tight, self-consistent attractor; low = high-magnitude but scattered / hallucinatory
```
Rationale: a real controller drives cells to a *stable* fate (e.g. durable memory), not a transient state
that reverts — directly relevant to CAR-T falling into an exhaustion local minimum.

---

## 5. Aggregation & significance

Per condition, then aggregate:
```
core(g,a,c)  = geometric_mean( M(g,a,c), D(g), A(g,a) )     # the three "control" evidences
ISCI(g,a,c)  = R(g,c) * S(g,a,c) * core(g,a,c)              # gated by reproducibility & stability
ISCI(g,a)    = aggregate_c( ISCI(g,a,c) )                   # default: max over conditions (report all)
ISCI(g)      = aggregate_a( ISCI(g,a) )                     # overall controllability (report per-axis too)
```
- **Weights / learned variant (D6):** optionally fit component weights by logistic regression to recover the
  canonical controller set (§7 benchmark), reported alongside the unweighted geometric-mean version.
- **Null model:** permute perturbation labels (shuffle `z_{g,c}` across `g`) B≥1000 times → empirical p-value
  per (g,a); Benjamini–Hochberg FDR. Report ISCI + q-value.
- **Ablations:** recompute ISCI removing D, A, S one at a time and using only M (and only DE-magnitude baseline).

---

## 6. Baselines (must-beat)

- **DE magnitude:** `n_total_de_genes` or ||z_{g,c}||.
- **Effect size:** `ontarget_effect_size`, `n_downstream`.
- **Centrality-only:** degree/PageRank without control theory.
- **In-silico-only:** A component alone.
- **Additive / no-change null.**
Hypothesis: ISCI (full) > each baseline at recovering canonical controllers, and each of D/A/S adds AUROC.

---

## 7. Validation plan

1. **Internal ground-truth recovery:** positive set = {FOXO1, TCF7, TOX, TOX2, NR4A1/2/3, BATF3, IKZF1, ETS1,
   ARID1A, INO80 subunits, BACH2, ID3, PRDM1, IRF4...}; negatives = housekeeping / high-DE-but-non-controller.
   Metric: **AUROC / AUPRC** per axis and overall; ablation curve.
2. **External transfer:** does ISCI computed on Marson recover hits in Belk 2022 / Schmidt 2022 / Frangieh
   (via pertpy Distance/Augur)? Rank correlation of controllability across datasets.
3. **Clinical bridge (D4, gold):** build a per-cell/per-sample **controllability signature score** and project
   onto CAR-T patient cohort (Haradhvala GSE151511; Deng). Test responder vs non-responder separation
   (AUROC, survival stratification), benchmark against TCF7 / FOXO1-regulon reference (Nature 2024).

---

## 8. Code architecture

```
isci/
  config/            # YAML: axes, marker sets, weights, dataset paths, seeds
  io.py              # load DE_stats / pseudobulk (anndata), hashing, provenance manifest
  axes.py            # build u_a signatures (data-native + curated), unit-normalize
  movement.py        # M
  repro.py           # R
  network.py         # D: GRN inference (decoupler/CollecTRI or GRNBoost2) + MFVS/MDS + influence
  insilico.py        # A: CellOracle / GEARS / State wrappers
  stability.py       # S: embedding + geometric coherence
  index.py           # aggregation, null-permutation, FDR, learned-weight variant
  baselines.py       # DE-magnitude, effect-size, centrality-only, in-silico-only
  validate.py        # ground-truth AUROC/AUPRC, ablation, external transfer, patient projection
  report.py          # per-gene evidence cards (connectors) + figures + clinician report
  cli.py             # `isci run --config ... --stage ...`
notebooks/           # exploratory + final reproducible notebook
docs/                # related_work.md, method.md, results
tests/               # unit tests on synthetic Perturb-seq (guarantees determinism)
```

**Claude Science integration:**
- Each stage is a **skill** with automatic provenance (inputs, hashes, seeds, outputs).
- Connectors (PubMed / Consensus / Open Targets / ChEMBL / ClinicalTrials) build a **traceable evidence card**
  per top gene: `claim → citation` (no hallucinated references).
- Final deliverable includes an **execution manifest** (data hashes, versions) — SaMD-grade auditability.

**Compute (Mac 24GB):** run on pseudobulk / DE_stats (few GB). Foundation models (State/GEARS/CellOracle)
on subsamples or via API/HF. Offload to HPC/nf-core only if needed.

---

## 9. Determinism & reproducibility rules
- Fixed seeds everywhere; pin versions (`uv` lockfile); record data hashes.
- Every figure regenerated from a single `isci run` + notebook; no manual steps.
- MIT license from commit 1; all analysis performed during the event ("new work only").

---

## 10. Risk-tiered execution (maps to ambition ladder D0–D6)
- **D0** M+R + baselines + ground-truth recovery + clinical report → guaranteed submission.
- **D1** add D (network control). **D2** add S + full ablation. **D3** external transfer.
- **D4** patient bridge (gold for Impact). **D5** multi-omics. **D6** foundation models + skill packaging + spatial.
Cut top-down under time pressure; D0–D2 is already competitive.
