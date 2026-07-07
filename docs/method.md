# Method Specification — Immune-State Controllability Index (ISCI)

> Technical spec, ready to implement. Companion to `related_work.md` and `benchmark.md`.
> **Revision:** incorporates peer-review fixes C1–C8 from Claude for Life Sciences critique (Jul 7, 2026).
> Data substrate: Marson CD4+ genome-scale Perturb-seq (`GWCD4i.DE_stats.h5ad`, `GWCD4i.pseudobulk_merged.h5ad`).

---

## 1. Objects & notation

- Perturbations (genes knocked down) `g ∈ G` (~10k targets that pass QC).
- Measured genes `j ∈ J` (10,282 genes in `DE_stats`).
- Conditions `c ∈ {Rest, Stim8hr, Stim48hr}`.
- Functional axes `a ∈ A` (activation, Th1, Th2, exhaustion-like, memory-like, CD4-CTL/cytotox, Treg).
- From `DE_stats.h5ad` per (g,c): effect vector **z**_{g,c} ∈ ℝ^J (layer `zscore` = logFC/lfcSE),
  plus `log_fc`, `adj_p_value`, and QC/reproducibility fields in `.obs`.
- Axis signature vector **u**_a(g) ∈ ℝ^J : signed loadings for axis `a`, built **with gene g left out** when scoring g (§3, C1).

Everything is computed per condition `c`, then aggregated across conditions (report per-condition profiles; default aggregate: max-abs with sign kept).

---

## 2. Design principles

1. **Direction matters, not just magnitude.** A controller pushes state *along a clinically meaningful axis*.
2. **Reproducible or it doesn't count.** Weight by cross-donor/cross-guide agreement in the data.
3. **Control = graded network influence**, not binary membership in one driver set (C5).
4. **Generalizable = linear model agrees.** Primary in-silico layer is `pert2state_model` (C7).
5. **Stability orthogonal to magnitude.** S is magnitude-residualized geometric coherence (C3).
6. **Beat baselines under leave-one-out axes** (C1). DE magnitude and pert2state are strong; ISCI must add signal in ablation.
7. **Headline differentiator:** auditable causal index + clinical bridge — not raw S alone.

---

## 3. Functional axes (signatures **u**_a) — with leave-one-out (C1)

Two complementary sources, combined:
- **Data-native:** Th1/Th2 polarization DE (`Th2_Th1_polarization_signature_DE_results_full.suppl_table.csv`) and activation/polarization regulator coefficients.
- **Curated markers** in `config/axes.yaml` (decoupler ULM or `scanpy.tl.score_genes`).
- **CELLxGENE cross-check** via `mcp-cellguide` (Claude Science) to validate marker choice.

Normalize **u**_a to unit L2 norm.

### Leave-one-out (mandatory for scoring and benchmark)

When computing ISCI(g, ·), rebuild every axis signature **u**_a^{(-g)} with gene `g` removed from:
- all curated marker sets in `axes.yaml`, and
- data-native loading tables (zero out or drop row/column for `g`).

**All benchmark AUROC/AUPRC reports use LOO axes.** Non-LOO scores may be shown for exploration only.

---

## 4. The five components (each mapped to [0,1] via rank/percentile)

### M — Directional movement (empirical)

```
m_raw(g,a,c) = < z_{g,c} , u_a^{(-g)} > / ||z_{g,c}||     # cosine; sign = direction along axis
M(g,a,c)     = percentile_rank( |m_raw(g,a,c)| over g )
sign_M(g,a,c) = sign(m_raw)
```

### R — Reproducibility (empirical weight)

From `DE_stats.obs`: `donor_correlation_hits_mean`, `guide_correlation_signif`, `ontarget_significant`,
`single_guide_estimate`, `low_target_gex`.

```
R(g,c) = percentile_rank( w1*donor_corr_hits_mean + w2*guide_corr_signif ), gated by ontarget_significant
```

Default w1=w2=0.5 (stated as **priors**; report sensitivity w1 ∈ {0.3, 0.5, 0.7}). R multiplies the final score.

### D — Structural network control (continuous influence, C5)

**GRN construction (connector-grounded, CPU-local):**
1. **CollecTRI** TF→target priors (`decoupler`), intersected with
2. **STRING** PPI (`mcp-protein-annotation`) and
3. **JASPAR/UniBind** TFBS (`mcp-regulation`),
restricted to measured genes. Avoid fragile de-novo GRNBoost2 in the critical path.

**Score (never binary MFVS/MDS membership):**
```
D(g) = percentile_rank( influence(g) )
```
where `influence(g)` is a **continuous** controllability contribution — e.g. CEFCON-style influence score, or fraction of sampled minimal driver sets containing `g`. MFVS/MDS enumerate candidate sets; membership is aggregated, not a single yes/no.

### A — In-silico concordance (pert2state-first, C7)

**Primary (mandatory):** run Marson's `pert2state_model` linear regression (Fig. 4 baseline + A layer):
```
a_pred(g,a) = < predicted_shift(g) , u_a^{(-g)} > / ||predicted_shift(g)||
A(g,a) = percentile_rank( agreement(a_pred, m_raw) )
```

**Optional stretch:** `scgpt` skill for embedding-based concordance if time permits.

**Descoped (CPU-local, no remote compute):** CellOracle, GEARS, State/Tahoe-x1.

### S — Target-state stability (magnitude-residualized, C3)

Raw geometric coherence correlates ρ≈0.75–0.97 with effect magnitude (Shesha et al., arXiv 2604.16642) — redundant with M if used raw.

**Definition:**
1. Compute geometric coherence `C_raw(g,c)` using **`shesha-geometry`** where single-cell vectors exist; on pseudobulk use **by_guide / by_donor replicate dispersion** as a documented proxy.
2. Residualize: `C_resid(g,c) = C_raw - f(||z_{g,c}||)` (linear or rank regression on magnitude).
3. `S(g,a,c) = percentile_rank( C_resid(g,c) )`.

Validate proxy vs true Shesha on **one subsampled perturbation set** (report correlation). Call pseudobulk metric a **proxy**, not Shesha itself.

---

## 5. Aggregation & significance (C4, C6)

Per condition:
```
core(g,a,c)  = geomean_eps( M(g,a,c), D(g), A(g,a) ; ε=1e-3 )   # ε floor prevents zeroing (C4)
ISCI(g,a,c)  = R(g,c) * S(g,a,c) * core(g,a,c)
ISCI(g,a)    = aggregate_c( ISCI(g,a,c) )                        # report all conditions
ISCI(g)      = aggregate_a( ISCI(g,a) )
```

**Degradation:** D0 = `R * geomean_eps(M)`; add D, A, S as implemented.

### Component-appropriate null models (C6)

| Component | Null |
|-----------|------|
| M, A | Permute perturbation labels (shuffle **z** across g) |
| D | Degree-preserving edge rewiring of GRN |
| S | Shuffle guide labels within perturbation |

Report FDR (BH) per component where valid; do not claim global ISCI q-values from M-only permutation.

**Ablations:** ISCI full vs −D / −A / −S vs M+R only vs each baseline.

---

## 6. Baselines (must-beat, under LOO axes)

1. **DE magnitude** — `n_total_de_genes` or ||z_{g,c}||.
2. **Effect size** — `n_downstream`, `ontarget_effect_size`.
3. **Centrality-only** — PageRank on connector GRN.
4. **pert2state_model** — linear regression (Marson Fig. 4); **honest strong baseline**.

Hypothesis: ISCI full > pert2state > DE magnitude on **clinical-curated** positives (§7); ablation shows D and residualized S add measurable AUPRC.

---

## 7. Validation plan

### Ground truth (C2)

| Tier | Set | Role |
|------|-----|------|
| **Primary (headline)** | Clinically/mechanistically curated from independent literature: FOXO1, TCF7, TOX/TOX2, NR4A, BATF3, IKZF1, ETS1, ARID1A, INO80, BACH2, ID3, PRDM1, IRF4 | Main AUROC claim |
| **Secondary** | `known_regulators=True` in Marson `polarization_prediction_…_coefficients.csv` | Confirmation (same dataset — state explicitly) |

**Negatives:** expression-matched non-controllers via **GTEx** (`mcp-expression`); high-DE non-controllers; housekeeping.

**Metrics:** AUROC, AUPRC, precision@20/@50 — **all under LOO axis construction**.

### External transfer (D3)

Frangieh via `pertpy` first → Belk → Schmidt (`mcp-omics-archives`).

### Clinical bridge (D4)

1. **Phenotype floor (minimum acceptable D4):** ISCI signature separates exhaustion vs memory/stem in Functional CAR-T atlas latent (scVI-hub precomputed).
2. **Outcome test (stretch):** responder vs non-responder AUROC with study/batch correction; benchmark TCF7/FOXO1-regulon; report honestly if underpowered.

---

## 8. Code architecture

```
isci/
  io.py              # load DE_stats / pseudobulk, SHA-256 manifest, provenance
  axes.py            # u_a build + leave-one-out mode + cellguide cross-check
  movement.py        # M
  repro.py           # R
  network.py         # D: connector GRN + continuous influence
  insilico.py        # A: pert2state concordance (+ optional scgpt)
  stability.py       # S: shesha-geometry + magnitude residualization
  index.py           # geomean_eps, component nulls, FDR
  baselines.py       # DE, effect-size, centrality, pert2state
  validate.py        # LOO benchmark, ablation, transfer, clinical projection
  evidence.py        # PubMed + Open Targets + literature-review (NOT Consensus)
```

**Claude Science connectors (live environment):** `mcp-pubmed`, `mcp-open-targets`, `mcp-biorxiv`, `mcp-omics-archives`, `mcp-regulation`, `mcp-protein-annotation`, `mcp-cellguide`, `mcp-expression`, `literature-review`, `scvi-tools`, sub-agents for parallel evidence cards.

**Cursor-only MCPs (NOT in Claude Science):** Consensus, Wiley Scholar Gateway, Cortellis, Medidata — do not depend on these in the build path.

**Compute:** **CPU-local on Mac 24GB** over DE_stats/pseudobulk. No HPC/Modal unless configured later. CAR-T atlas uses **precomputed scVI latent** (no re-integration).

---

## 9. Determinism & reproducibility

- Fixed seeds; `uv` lockfile; data hashes in manifest per artifact.
- **New work only:** design docs predate event; all analysis code, figures, and results timestamped during the event.
- Clean commit history from hackathon start; stubs contain signatures only.

---

## 10. Phased execution (aligned with `docs/execution_plan.json`)

| Phase | Deliverable |
|-------|-------------|
| **D0** | io, axes (LOO), M, R, baselines, LOO benchmark, `R × M` ranked table |
| **D1–D2** | D (connector GRN), S (residualized), A (pert2state), full ISCI, **central ablation figure** |
| **D3** | External transfer (Frangieh → Belk → Schmidt) |
| **D4** | CAR-T atlas phenotype floor → outcome test if powered |
| **D5 (cut-first)** | Gladstone chromatin hook (borzoi/evo2) only if D2+D4 close early |
| **Continuous** | Evidence cards, clinician report, demo, skill packaging |

**Minimum competitive submission:** D0–D2 + ablation figure. **Impact stretch:** D4 phenotype floor on Functional CAR-T atlas.

**Cut order:** chromatin D5 → scGPT → raw GSE151511 → external transfer. Never cut LOO benchmark or central figure.
