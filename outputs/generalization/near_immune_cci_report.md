# Near-Transfer Test of the Conditional Controllability Invariant (CCI)
## Independent immune Perturb-seq — Schmidt et al. 2022

**Verdict: FAIL** (by the pre-registered falsification criterion), with a **directionally
consistent, underpowered near-miss**. See §5 for the honest interpretation.

---

## 1. Dataset & feasibility gate

**Target:** Schmidt et al. 2022, *"CRISPR activation and interference screens decode
stimulation responses in primary human T cells"* — CRISPRa Perturb-seq subset,
**GEO GSE190604**. Pooled CRISPR**a** (gain-of-function) screen coupled to scRNA-seq in
primary human T cells, with and without anti-CD3/CD28 stimulation, designed around IL2/IFNG
cytokine production.

**Hard gate (metadata-only, passed before heavy download):**

| Requirement | Status | Evidence |
|---|---|---|
| Perturbation x gene effect form | PASS (cell-level -> pseudobulk) | 10x matrix 996 MB gz; 103,805 cells x 36,601 genes; pseudobulks well under 20 GB |
| >=2 replicates per perturbation | PASS | 4 wells x two conditions (stim / nostim); barcode suffix 1-4 = nostim wells 1-4, 5-8 = stim wells 1-4 |
| Credible state axis | PASS (data-derived) | T-cell activation axis = stim minus nostim in NO-TARGET control cells; IL2 +3.0, IFNG +3.6, IL2RA +3.2, GZMB +3.3, TNF +1.9 (log-CPM) — canonical and correctly signed |
| Regulator label set | PASS (external, curated) | canonical TCR-proximal signaling + master effector/helper TFs + core cytokine-receptor signaling; intersected with measured targets (see §3) |
| CPU-local <=20 GB | PASS | peak RSS 5.2 GB |

**Perturbation set:** 73 gene targets (2 guides each) + NO-TARGET control (8 guides, 4,000
cells). Cells assigned to a single guide (singlets): 61,041. Analysis condition = **stim**
(cytokine biology is stimulation-dependent), NO-TARGET as within-well baseline.

## 2. Protocol (as specified; skill `isci-controllership`)

1. **Pseudobulk** per (target x well x condition), >=25 cells each -> 560 profiles; CPM+log1p.
2. **State axis** (leave-marker-out): activation direction from NO-TARGET stim-minus-nostim,
   restricted to the top/bottom 200 axis genes (NES-style, avoids cosine dilution over 36k genes).
   When scoring a target that is itself an axis gene, that gene is removed from the axis.
3. **M** = L2 norm of the mean well effect vector (target minus well-matched NO-TARGET).
4. **S** = |cos(effect, signed axis)| on axis genes; **R** = mean pairwise Pearson of
   per-well effect vectors (top-2000 moved genes).
5. **Residualize** S, R on M (rank regression) -> S_resid, R_resid; **C** = mean of their
   residual percentiles.
6. **Gate** to detectable subset (M >= median): 35/69 targets.
7. **Magnitude-matched negatives** (match on magnitude, base expression, cells/target;
   3 per positive) from detectable non-positives.
8. **Test:** conditional LR (C over M) + bootstrap dAUPRC(M -> M+C), 1000 resamples.

## 3. Label provenance (honest)

Positives are an **external, curated** high-confidence set of canonical T-cell activation
controllers — TCR-proximal signaling (LAT, LCP2, VAV1, PLCG2, CD28, CD247, GRAP, PRKD2,
MAP4K1, RAC2, PIK3AP1, DEF6, LAT2), master state TFs (TBX21, GATA3, EOMES, TCF7, PRDM1,
IKZF3), cytokine-receptor signaling (IL2RB, IL2RG), and costim/NF-kB (CD27, TNFRSF9, RELA,
TRAF3IP2). This is the same philosophy used to anchor Marson (curated known regulators),
**not** derived from this dataset's own hits. IL2 and IFNG are the screen **readout** and
were excluded from both classes. Of 23 measured positives, **10 fell in the detectable
subset**; matched to **15 negatives**. This N is small — the primary limitation (§5).

## 4. Result

| Quantity | Value |
|---|---|
| Targets scored | 69 |
| Detectable subset | 35 |
| Positives (detectable) / matched negatives | **10 / 15** |
| Magnitude balance pos vs matched-neg (MW p, want NS) | 0.846 (balanced) |
| **Spearman(C, magnitude)** | **0.054** (all) / 0.169 (detectable) — orthogonal |
| Conditional LR: C over M | p = **0.131** (NS) |
| Conditional LR: S_resid over M | p = 0.099 (trend) |
| Conditional LR: R_resid over M | p = 0.693 (NS) |
| AUPRC magnitude-only -> +C | 0.538 -> 0.676 |
| **Bootstrap dAUPRC(M -> M+C)** | **0.138**, 95% CI **[-0.029, 0.434]**, P(>0)=0.904 |
| Bootstrap dAUPRC(M -> M+S_resid) | 0.169, 95% CI [-0.02, 0.498], P(>0)=0.931 |

## 5. Interpretation — FAIL, honestly

By the **pre-registered falsification criterion** (invariant doc §3: falsified if the
bootstrap dAUPRC 95% CI includes 0 **OR** the conditional LR test is non-significant), the
CCI is **not confirmed** in Schmidt 2022:

- The conditional LR test for C is **non-significant** (p=0.131), and
- The bootstrap dAUPRC 95% CI **includes 0** ([-0.029, 0.434]).

**But the failure is a directional near-miss, not a contradiction.** Every quantity points
the *same way* as the anchoring Marson result, only with insufficient power to clear the bar:

- dAUPRC point estimate is **positive** (+0.138; Marson +0.229), lifting AUPRC
  0.538 -> 0.676, with **P(gain>0)=0.904**.
- C is **orthogonal to magnitude** (Spearman 0.054), exactly as required and as
  seen in Marson (+0.02) — the signal is not a magnitude proxy.
- Axis-specificity (S_resid) is the stronger component (LR p=0.099, P(gain>0)=0.931),
  consistent with Marson where specificity was the leading conditional feature.

**Why underpowered:** Schmidt is a **targeted** ~73-gene CRISPRa screen, not genome-scale.
After the mandatory detectable-effect gate, only **10 labeled positives** remain (out of
35 detectable) — vs 19 in Marson from a **1,260-gene detectable pool** (of 2,520 scored;
both screens pass ~half at the magnitude-median gate, 35/69 here vs 1260/2520 there). With 10 positives / 15 matched
negatives, a true dAUPRC of ~0.14 is not separable from 0 at 95%. The result is consistent
with H0 *and* with a real effect of the Marson magnitude; the data cannot distinguish them.

**Scope statement (invariant doc §6).** This near-transfer test does **not** upgrade CCI to
a confirmed immune-scoped property: it is a **PASS in direction, FAIL in significance**,
power-limited. It neither confirms nor refutes; it defines the N a targeted screen needs.
A larger immune screen (Frangieh Perturb-CITE-seq, or the LOF/CRISPRi Schmidt companion) is
the correct next near-transfer target. The one unambiguous positive: the orthogonality of C
to magnitude **replicates** — the central claim that the conditional signal is not an
effect-size artifact holds in an independent lab, platform, and perturbation modality.

## 6. Files
- `near_immune_scores.csv` — all 69 scored targets: M, n_de, cells, base_expr, R, S,
  S_resid, R_resid, C, detectable flag, positive/matched-negative flags.
- This report.

*Data: GSE190604 (Schmidt et al., Science 2022). Analysis: isci-controllership skill,
leave-marker-out axis, magnitude-matched negatives, conditional LR + bootstrap. CPU-local.*
