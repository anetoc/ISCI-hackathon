# Claim ledger — what this project claims, at what status, on what evidence

One row per claim. `status` ∈ {PASS, NULL, FAIL, NOT-EVALUABLE, SUPPORT}. Every "claimed" row has a
matching "not claimed" boundary. This is the single source of truth; README/PAPER/DOSSIER must agree
with it.

## Core claims (submission)

| # | Claim | Status | Evidence | NOT claimed |
|---|-------|--------|----------|-------------|
| 1 | Among detectable-effect perturbations, axis-specificity + cross-donor coherence identify known T-cell-state regulators **beyond effect magnitude** | **PASS** | Marson CD4+ Perturb-seq: detectable set AUPRC 0.415→0.722; bootstrap gain +0.229 [0.072,0.405] P>0=99.6%; orthogonal to magnitude ρ=+0.02; replicated across 3 conditions (Rest/Stim8/Stim48) | Not a claim about every gene — restricted to detectable-effect set |
| 2 | The property is **immune-scoped** with a falsifiable boundary | **PASS/FAIL boundary** | Marson PASS +0.229; Schmidt near-miss +0.138 (CI incl. 0); Norman K562 FAIL; Replogle RPE1 FAIL | Not universal controllability across all cell systems |
| 3 | Controllership is **specific to canonical, axis-defining regulators** | **FAIL boundary (completed)** | Ablation: gain +0.25→+0.03 removing 4 axis TFs (n=9, underpowered). Independent external positive set (20 non-marker functional-screen regulators, Shifrut/Schmidt/Belk, matched negatives): ΔAUPRC −0.281 [−0.476,−0.073], CI excludes 0 negative — clean FAIL. External regulators are magnitude-visible (base AUPRC 0.58) | Does NOT generalize to the broad functional-regulator class; specific to axis-defining regulators |
| 4 | The gate is **not tuned** | **PASS** | Gate-sensitivity: gain stable +0.26→+0.33 across top-40%→100% | — |
| 5 | Controllership ≠ therapeutic desirability | **SUPPORT** | IRF1 (#1 controller) has negative therapeutic convergence and is a dangerous-rheostat on the safety board | Ranking does not recommend targets |

## Extension claims (tested, honest verdicts)

| # | Claim | Status | Evidence | NOT claimed |
|---|-------|--------|----------|-------------|
| 6 | IEC is a measurable multi-axis capacity (2.5 axes) | **confirmed** | Pseudobulk + CAR-T atlas single-cell (455,370 cells): persistence orthogonal; killing↔resistance entangled ρ=−0.53, survives CD8 control (−0.44) | Not a clinical predictor |
| 7 | An IEC axis predicts CAR-T clinical response | **NULL (well-powered)** | Functional CAR-T atlas, n=87 labeled, 9 studies: A_persist LPO 0.643 → LSO 0.533 [0.408,0.650] perm-p 0.14; CD8-frac baseline 0.585 beats all | No transportable transcriptional response biomarker in the current public multi-study atlas |
| 8 | Magnitude-conditional controllership holds at the **protein layer** | **FAIL** | Frangieh totalVI protein CCI: raw +0.584 was a direction-agnostic inverted-feature artifact (positives lower residual coherence 0.059 vs 0.565); direction-aware verdict FAIL, adds_over_rna=False | Magnitude-independence is an RNA/cross-donor property, not universal across layers |
| 9 | Cross-layer RNA→protein concordance | **SUPPORT** | RNA-called controllers produce expected surface phenotype; cross-layer surface-shift AUROC 0.90; Papalexi PD-L1 rescue AUROC 0.77 | Concordance, not a magnitude-conditional protein PASS (see #8) |
| 10 | Mechanism enrichment (NF-κB, Treg-brake) is causal | **prioritization only** | Curated sets enrich in controllership not magnitude (NFkB q=0.017, Treg q=0.008); broad GO/Reactome negative | Computational prioritization, not causal — needs wet-lab |

## Prior-art positioning

| Claim | Status | Evidence |
|-------|--------|----------|
| Shesha/Raju is the nearest prior art; our coordinate is distinct | **SUPPORT** | Frangieh three-coherence: Shesha Sₚ~magnitude ρ=0.97 (replicates their coupling); our R~magnitude 0.008, S~magnitude 0.19; partials Sₚ~R\|M=−0.71, Sₚ~S\|M=+0.67 — Shesha collapses onto magnitude, our signal is orthogonal |

## Methodology honesty

- "Pre-specified" = criteria fixed in code before the adjudicated result was computed. For the
  **completed** tests this is a pre-specification, honestly **not** a formal pre-registration.
  Tests **not yet run** (B1 non-T immune, CD8/CAR-T replication, functional P3) ARE genuinely
  pre-registered in `reports/PREREGISTRATION.md` — criteria + directional predictions locked, with
  the git commit SHA as the timestamp (Zenodo DOI mintable via a GitHub release; maintainer step).
