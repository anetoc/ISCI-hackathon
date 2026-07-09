# EXEC-2 / MASTER_ROADMAP Phase 6 — external immune CCI validation

**VERDICT: FAIL (directional near-miss, underpowered)** on Frangieh Perturb-CITE-seq — and it is
the **third independent immune system** to show the same signature: **C is orthogonal to
magnitude (ρ=0.03)** and the ΔAUPRC point estimate is **positive (+0.118)**, specificity-led, but
with only 10 positives the bootstrap CI includes 0 and the conditional LR is n.s. The central
claim — the conditional signal is **not** an effect-size artifact — **replicates a third time**;
only the genome-scale anchor (Marson, 19 positives) clears the significance bar.

---

## Gate log (gate-first, per plan)

- **Shifrut–Marson 2018 (CD8+ T-cell KO) → NOT-EVALUABLE.** Inspected before any heavy run:
  20 targets, of which **19 are canonical immune regulators** (only STAT6 non-canonical). The CCI
  benchmark needs known-regulator *positives* vs non-regulator *magnitude-matched negatives*; a
  screen deliberately built of curated regulators cannot furnish a negative set. Reported and
  pivoted — no fabricated contrast.
- **Frangieh 2021 Perturb-CITE-seq → EVALUABLE** and run here: 248 targets give a genuine
  regulator/non-regulator contrast; least-circular labels available (see §2).

## 1. Dataset & method

- **Frangieh et al. 2021** (*Nat Genet*), Perturb-CITE-seq: patient melanoma + autologous TIL
  co-culture, CRISPR-KO of 248 genes, 3 conditions (Control / IFNγ / Co-culture). scPerturb
  harmonized h5ad (Zenodo 13350497), 218,331 cells × 23,712 genes, raw counts.
- **Protocol = the locked Schmidt recipe** (`outputs/generalization/near_immune_cci_report.md` §2),
  reusing the kernel helpers: pseudobulk per (target × condition) → leave-marker-out immune-evasion
  axis (IFNγ − Control in control cells) → M (effect norm), S (|cos| with axis), R (cross-condition
  reproducibility) → residualize S,R on M → C = mean residual percentile → detectable gate
  (M ≥ median) → **magnitude-matched negatives** (locked helper) → conditional LR + bootstrap ΔAUPRC.

## 2. Labels (least-circular)

- **Positives = canonical IFN-γ-signaling + antigen-presentation regulators** — external pathway
  knowledge, **not** Frangieh's own discovery hits (avoids circularity). Of 13 present, **10 fell in
  the detectable subset**: B2M, HLA-B, HLA-E, IFNGR1, IFNGR2, IRF3, JAK1, JAK2, STAT1, TAPBP.
- **Negatives = 22 magnitude/expression-matched** non-canonical targets (MW p=0.28, balanced).

## 3. Result

| quantity | value |
|---|---|
| targets scored / detectable | 238 / 119 |
| positives (detectable) / matched negatives | **10 / 22** |
| magnitude balance (MW p, want NS) | 0.281 (balanced) |
| **Spearman(C, magnitude)** | **0.031** (orthogonal) |
| conditional LR: C over M | p = 0.150 (n.s.) |
| conditional LR: S_resid over M | p = 0.083 (trend) |
| conditional LR: R_resid over M | p = 0.358 (n.s.) |
| AUPRC magnitude-only → +C | 0.609 → 0.727 |
| **bootstrap ΔAUPRC(M → M+C)** | **+0.118, 95% CI [−0.018, 0.336], P(>0)=0.862** |

## 4. Interpretation — FAIL, honestly, but a consistent near-miss

By the pre-registered criterion (ΔAUPRC CI excludes 0 AND conditional LR p<0.05 AND |Spearman(C,M)|
small), CCI is **not confirmed** in Frangieh: the LR for C is n.s. (0.150) and the ΔAUPRC CI
includes 0 ([−0.018, 0.336]). **But every quantity points the same way as Marson/Schmidt:**

| system | modality | n_pos | ΔAUPRC | 95% CI | Spearman(C,M) | verdict |
|---|---|---|---|---|---|---|
| Marson CD4+ | KD/KO (genome-scale) | 19 | **+0.229** | [0.072, 0.405] | +0.02 | **PASS** |
| Schmidt CD4+ | CRISPRa (targeted) | 10 | +0.138 | [−0.029, 0.434] | +0.05 | near-miss |
| **Frangieh (this)** | KO (tumor+TIL) | 10 | **+0.118** | [−0.018, 0.336] | **+0.03** | **near-miss** |

- The **orthogonality of C to magnitude now replicates in three independent immune systems**
  (0.02 / 0.05 / 0.03) — across lab, platform, perturbation modality, and even cell compartment.
  The conditional signal is **not** a magnitude proxy anywhere.
- **Axis-specificity (S_resid) is again the leading component** (p=0.083; Schmidt 0.099; Marson: S
  led) — the immune-specific part of the signal is consistent.
- The bar is missed for the **same reason each time**: after the detectable gate, targeted screens
  leave ~10 positives, and a true ΔAUPRC ≈0.12–0.14 is not separable from 0 at 95% with n≈10.

## 5. Scope statement

This does **not** upgrade CCI beyond its locked scope; it is a **PASS in direction, FAIL in
significance**, power-limited — as pre-registered. It **strengthens** the immune-scoped reading:
the magnitude-independence of the controllership signal is now a three-system replication, and
axis-specificity is repeatedly the carrier. The honest boundary remains that **only a genome-scale
immune screen (Marson) has the positive count to clear significance**; independent genome-scale
immune Perturb-seq with a non-regulator contrast is scarce (Shifrut/Schmidt/Papalexi are targeted
regulator panels). Caveats: Frangieh perturbs **tumor** cells under T-cell pressure (immune-evasion
axis, not a T-cell-intrinsic state); labels are canonical-pathway (not the screen's own hits) to
minimize circularity.

### Deliverables
- `frangieh_cci_report.md` (this file) · `frangieh_perturbcite_scores.csv` (all 238 targets: M, S,
  R, S_resid, R_resid, C, detectable, base_expr, n_cells) · `frangieh_perturbcite_cci_result.json`
  (all numbers) · `cci_external.py`, `frangieh_config.py` (reusable, CPU).
