# Claim ledger — what this project claims, at what status, on what evidence

One row per claim. `status` ∈ {PASS, NULL, FAIL, NOT-EVALUABLE, SUPPORT,
SUPPORTED-EXPLORATORY, REPLICATED-EXPLORATORY, DIRECTIONAL-UNCERTAIN, UNSUPPORTED}. Every "claimed" row has a
matching "not claimed" boundary. This is the single source of truth; README/PAPER/DOSSIER must agree
with it.

## Core claims (submission)

| # | Claim | Status | Evidence | NOT claimed |
|---|-------|--------|----------|-------------|
| 1 | Among detectable-effect perturbations, axis-specificity + cross-donor coherence identify known T-cell-state regulators **beyond effect magnitude** | **PASS** | Marson CD4+ Perturb-seq: detectable set AUPRC 0.415→0.722; bootstrap gain +0.229 [0.072,0.405] P>0=99.6%; orthogonal to magnitude ρ=+0.02; replicated across 3 conditions (Rest/Stim8/Stim48) | Not a claim about every gene — restricted to detectable-effect set |
| 2 | The property is **immune-scoped** (T-cell → immune-lineage) with a falsifiable boundary | **PASS/FAIL boundary** | Marson PASS +0.229; Schmidt near-miss +0.138 (CI incl. 0); THP-1 myeloid (non-T immune, pre-registered) near-miss +0.166 [−0.006,0.374], axis-specificity transfers (LR p=6.7e-5), R does not — mirror of K562; Norman K562 FAIL; Replogle RPE1 FAIL | Not universal controllability across all cell systems; myeloid near-miss is power-limited (2 reps), not a PASS |
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
| 11 | Real functional rulers outperform structurally matched pseudo-axes uniformly | **MIXED v2** | Th1 +0.181 (p=0.0199) and Th2 +0.253 (p=0.0050) SUPPORT; TCR, memory and Treg UNSUPPORTED. Conditional topology sampler resolved prior gaps: exhaustion +0.029 (p=0.209) and CD4-CTL +0.035 (p=0.522) are UNSUPPORTED | Not a universal property of every axis; ontology overlap remains |
| 12 | Precision and repeatability independently transport after family-wise control | **DIRECTIONAL-UNCERTAIN post-hoc** | T2 Marson precision +0.215 [0.094,0.498], permutation p=0.0070, BH q=0.070; THP-1 precision +0.083 [−0.030,0.259], q=0.185; repeatability weaker; 6/10 planned tests NOT-EVALUABLE | No component is declared confirmed across systems; non-evaluable is not biological absence |
| 13 | Component support transports across Marson conditions | **SUPPORTED-EXPLORATORY v2 (Th2 only)** | Raw reconstruction authorized by PI: leakage-safe leave-one-condition-out Th2 precision ΔAUPRC +0.174 [+0.091,+0.364], permutation p=0.0020, BH q=0.016; positive in Rest/Stim8/Stim48. Th1 +0.101, q=0.112 remains directional-uncertain | Within-screen context transport, not independent replication; no universal claim for other axes |
| 14 | One scalar is the best scientific representation of controllability | **UNSUPPORTED v2** | 1,236-gene component profile yields 7 interpretable archetypes and 66 Pareto-front genes; known regulators occupy distinct reach/precision/repeatability regimes | v1 scalar remains a useful ranking baseline, but v2 does not average trade-offs into a new score |
| 15 | A topologically coherent functional ruler necessarily discriminates controllers | **FAIL v2** | Exhaustion-like and CD4-CTL are both more correlated than all 10,000 expression-matched random sets (p<10⁻⁴), yet neither beats a converged topology-conditional null for controller recovery (p=0.209/0.522) | Axis coherence is a ruler property, not evidence of controller-label validity |
| 16 | Th2 precision externally replicates independently of stimulation context | **FAIL boundary / REPLICATED-EXPLORATORY no-stim only** | Frozen GSE190604 targeted CRISPRa analysis: stimulated primary Δ weighted AUPRC +0.003 [−0.096,+0.099], permutation p=0.396, q=0.396; no-stim secondary +0.193 [+0.057,+0.361], p=0.0070, q=0.028 | No context-invariant replication; the secondary does not rescue the failed primary; external to Marson but not an untouched prospective dataset; no therapeutic direction |
| 17 | The GSE190604 no-stim versus stimulated Th2 difference establishes a context interaction | **DIRECTIONAL-UNCERTAIN post-result** | Target-paired contrast +0.190, paired bootstrap [+0.046,+0.370] with 99.8% positive, but within-gene context-swap p=0.091 (1,000 swaps) | Stable to target resampling is not significance under context exchange; not donor-paired and not a stimulation mechanism |

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
