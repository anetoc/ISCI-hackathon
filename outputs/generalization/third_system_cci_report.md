# CCI Third System — Non-immune Differentiation (Norman K562 CRISPRa)

**Purpose.** Add a third point to the Conditional Controllability Invariant (CCI) scope
test to sharpen the Tissue-Synapse-Capacity **P1** prediction. Prior points:
immune Marson CD4+ = **PASS**; non-immune *proliferation* Replogle RPE1 = **FAIL**.
This system is the wanted third case: **non-immune and NOT proliferation-dominated** —
a *differentiation / lineage* program. TSC P1 predicts CCI should **FAIL** here
(differentiation is a cell-autonomous state, not a synaptic/relational one).

**Verdict: FAIL (primary), directional near-miss — matches the TSC P1 prediction.**

---

## 1. Dataset and admissibility (feasibility gate — passed)

| Gate requirement | Status | Detail |
|---|---|---|
| Effect matrix (pert × gene) | ✅ | 105 single-gene CRISPRa perturbations, pseudobulk LFC vs 11,855 control cells |
| ≥2 replicates | ✅ | 8 gemgroups (10x lanes) → split-half reproducibility computable |
| Credible **state axis** | ✅ | Erythroid (25 genes) + megakaryocyte (15) **structural effector markers** — hemoglobins, glycophorins, platelet GPs. **Zero TFs** → disjoint from the label set by construction |
| Credible **regulator labels** | ✅ | 27 hematopoietic-lineage master regulators among the 105 singles (KLF1, CEBPA/B/E, SPI1, PRDM1, FEV, IKZF3, IRF1…), curated from literature independent of this screen; 13 pass the detectable gate |
| CPU-local ≤~20 GB | ✅ | 699 MB harmonized h5ad (scPerturb, Zenodo 13350497); loads and pseudobulks on 24 GB |

**System.** K562 (CML erythroleukemia line) — CRISPRa activation of transcription factors
drives hematopoietic-lineage differentiation (erythroid / megakaryocyte), the central
finding of Norman et al. 2019 (*Science*). This is a **cell-autonomous differentiation
program**, the decisive non-proliferation far-transfer case for TSC P1.

**Admissibility.** The axis (structural markers) and the positives (lineage TFs) are
disjoint sets, so leave-marker-out is trivially clean and the label set is non-circular.
This is *not* the "no clean axis+label pair" NOT-EVALUABLE failure mode the feasibility
doc anticipated for Norman — resolved by defining the axis from effector markers, not TFs.

## 2. Protocol (identical to Marson anchor and RPE1)

Effects built in per-gene-standardized LFC space (dropout-safe for near-zero hemoglobin
baselines in undifferentiated K562). Per perturbation:
- **M** = transcriptional effect norm over 10,217 expressed genes (the confound).
- **S** = coherent signed shift on the best-matching differentiation axis, **leave-marker-out**.
- **R** = split-half (interleaved gemgroups) reproducibility of the effect over top-effect genes.
- Gate to detectable effect (M ≥ median); residualize S, R on M (rank-regression → residual
  percentile); **C = mean(S_resid, R_resid)**.
- Magnitude-matched negatives (matched on M + baseline expression + cells/target, all
  27 candidate positives excluded from the negative pool).
- **Conditional LR** (C over M) **AND** **bootstrap ΔAUPRC** (M → M+C), 2000 resamples.

Pre-registered dual criterion: **PASS ⇔ bootstrap ΔAUPRC 95% CI excludes 0 AND LR p<0.05.**

## 3. Result

**Orthogonality (sanity):** Spearman(C, M) = **+0.052** — C is magnitude-orthogonal, as in
Marson (+0.02) and RPE1 (~0). The conditional design is intact.

| Test | Value | Reads |
|---|---|---|
| Conditional LR for C | χ²=6.20, **p = 0.013** | significant (C adds over M) |
| — component R_resid | χ²=10.98, p = 0.0009 | reproducibility carries the signal |
| — component S_resid | χ²=1.85, p = 0.174 | axis-specificity does **not** add |
| Bootstrap ΔAUPRC (M → M+C) | **+0.138**, 95% CI **[−0.033, +0.370]** | **CI includes 0** |
| P(gain > 0) | 0.926 | high but sub-threshold |
| n_pos / n_neg | 13 / 32 | comparable to Marson (19) |

**The dual criterion is not met** (LR significant, but ΔAUPRC CI includes 0) →
**FAIL** on the primary (median-gate) variant.

### Robustness (4 variants)

| Variant | n_pos | n_neg | Spearman(C,M) | LR p (C) | ΔAUPRC | 95% CI | Verdict |
|---|---|---|---|---|---|---|---|
| **gate50 (PRIMARY)** | 13 | 32 | +0.052 | 0.013 | **+0.138** | [−0.033, 0.370] | **FAIL** |
| gate25 (looser) | 19 | 54 | +0.006 | 0.010 | +0.125 | [−0.006, 0.306] | FAIL |
| gate67 (stricter) | 12 | 21 | −0.015 | 0.005 | +0.237 | [+0.004, 0.469] | PASS (marginal) |
| gate50 npp6 seed7 | 13 | 28 | +0.052 | 0.024 | +0.146 | [−0.016, 0.364] | FAIL |

3 of 4 FAIL; only the stricter gate marginally clears (CI_lo +0.004, n_pos 12). The
verdict is **FAIL** but **not clean-FAIL**: the CI hugs zero from above and P(gain>0)≈0.93.

## 4. Cross-system synthesis

| System | Type | Perturbation | ΔAUPRC | 95% CI | LR p | Spearman(C,M) | Verdict |
|---|---|---|---|---|---|---|---|
| Marson CD4+ | **immune** | KD/KO | **+0.229** | [0.072, 0.405] | <1e-4 | +0.02 | **PASS** |
| Norman K562 | non-immune **differentiation** | CRISPRa | +0.138 | [−0.033, 0.370] | 0.013 | +0.05 | **FAIL** (near-miss) |
| Replogle RPE1 | non-immune **proliferation** | CRISPRi | +0.060 | [−0.013, 0.204] | 0.195 | 0.00 | **FAIL** (clean) |

The three systems order exactly as TSC predicts, with a **graded** effect:
**immune PASS (+0.229) > differentiation near-miss (+0.138) > proliferation clean-FAIL (+0.060).**

## 5. Interpretation — matches TSC P1

- **Matches the prediction.** Norman is non-immune and cell-autonomous (differentiation);
  TSC P1 predicts FAIL, and the primary verdict is FAIL. The immune-scoped boundary from
  the two-point test survives a third, independent, non-proliferation system.
- **Mechanistic refinement.** The residual conditional signal that *is* present here is
  carried by **reproducibility (R), not axis-specificity (S)** — S_resid adds nothing
  (p=0.17). Differentiation TFs produce highly reproducible effects but not the
  *axis-selective, magnitude-independent directionality* that defines controllers in the
  immune system. This is the signature TSC expects: relational/synaptic state has a
  directional control axis (immune PASS on S); cell-autonomous state does not (S fails
  here and in RPE1), and any residual is just clean reproducibility.
- **Graded, not binary.** Differentiation sits between immune and proliferation — a partial
  program with a real (LR-significant) but underpowered conditional signal. This sharpens
  P1 from a binary PASS/FAIL into a **gradient of relational content**, and is the honest
  reading: it is a near-miss, not a clean orthogonal null like proliferation.

**Bottom line:** CCI remains **immune-scoped**. A non-immune differentiation program does
not clear the pre-registered bar (primary FAIL), consistent with TSC P1, while showing more
residual signal than pure proliferation — a graded boundary, not a hard wall.

---

### Provenance
- Data: `NormanWeissman2019_filtered.h5ad`, scPerturb v1.4 (Zenodo 10.5281/zenodo.13350497),
  111,445 cells × 33,694 genes, K562 CRISPRa, 105 single-gene perturbations, 8 gemgroups.
- Protocol: `isci-controllership` skill helpers (`expression_matched_negatives`,
  `conditional_lr_test`, `bootstrap_auprc_gain`); invariant + spec as referenced.
- Axis: erythroid/megakaryocyte structural effector markers (no TFs). Labels: literature
  hematopoietic-lineage master regulators (disjoint from axis).
- Scores: `third_system_norman_scores.csv`; summary: `third_system_cci_summary.csv`.
