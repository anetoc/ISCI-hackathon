# Far-transfer test of the Conditional Controllability Invariant (CCI) — non-immune genome-scale Perturb-seq

**Verdict: FAIL (robust) — the CCI does not transfer to a non-immune proliferation screen.**
This defines the property as **immune-scoped**, not a universal invariant of perturbation biology.

---

## 1. What was tested

The Conditional Controllability Invariant (CCI) states: *after conditioning on effect
magnitude `M`, a reproducible, axis-specific residual signal `C` distinguishes genes that
CONTROL a cell-state transition from genes merely associated with it.* It holds strongly in
the anchoring immune system (Marson CD4+ Perturb-seq: bootstrap ΔAUPRC +0.229,
95% CI [0.072, 0.405], conditional LR p<1e-4).

The decisive far-transfer question (invariant §6): *does the same magnitude-conditional signal
recover known regulators in a completely different, non-immune cell system?* If yes → CCI is a
property of perturbation biology. If no → it is domain-scoped.

## 2. Dataset (hard gate passed)

| Property | Value |
|---|---|
| Dataset | **Replogle & Weissman 2022**, RPE1 essential-scale Perturb-seq (scPerturb, Zenodo 13350497, `ReplogleWeissman2022_rpe1.h5ad`) |
| System | Retinal pigment epithelial cells (RPE1) — **non-cancerous, non-immune** |
| Size | 1.24 GB on disk / ~8.7 GB densified — CPU-local feasible (no institutional gate) |
| Cells × genes | 247,914 × 8,749 |
| Perturbations | 2,394 CRISPRi gene knockdowns + 11,485 non-targeting control cells |
| Replicate structure | 56 gemgroup batches; split-half of cells per perturbation used for reproducibility `R` |
| Cells / perturbation | median 72 (IQR 41–117) |

Intake-gate requirements (generalization spec §"Minimum viable dataset"): perturbation×gene
effect matrix ✅ (computed as pseudobulk log-FC vs non-targeting, then z-scored); ≥2 replicates ✅
(split-half); credible **state axis** ✅ (below); credible **regulator label set** ✅ (below);
CPU-local ✅. **All requirements met — dataset is ADMISSIBLE.**

## 3. Axis and labels (non-immune, orthogonal sources — no invented labels)

- **State axis (the ruler):** canonical **cell-cycle / proliferation** expression program —
  Tirosh S-phase + G2/M marker genes (scanpy standard), 93/97 measured. This is an *expression
  readout* of proliferative state, appropriate for a dividing epithelial line.
- **Regulator label set (the positives):** **cell-cycle control machinery from an independent
  source** (not the expression ruler) — CDKs/cyclins, checkpoint kinases (CHEK1, WEE1, ATR),
  spindle-assembly checkpoint (BUB1/BUB1B/BUB3, MAD2L1, TTK, AURKA/B), APC/C subunits
  (ANAPC*, CDC16/20/23/27), replication licensing/origin (MCM2-7, ORC*, CDC6, CDT1, CDC45),
  cohesin (SMC1A/SMC3/RAD21/STAG2), PLK1, ESPL1. **49 of these are perturbed** in the screen;
  **33 survive the detectable-effect gate** and form the positive set.

These are genuinely distinct sources: the axis measures the *transcriptional state of
proliferation*; the labels are the *machinery that controls the cell cycle*. Overlap between
the two (MCM2-7, CDK1, CDC20, AURKA/B, BUB1) is exactly what the mandatory **leave-marker-out**
guard neutralizes.

## 4. Protocol (as implemented by the `isci-controllership` skill)

1. Pseudobulk each perturbation: CP10k + log1p, mean over its cells minus non-targeting mean → per-gene log-FC; z-scored across perturbations.
2. **Magnitude** `M` = number of strongly-DE genes (|z|>2) per perturbation. (Regulators have larger effects — median 583 vs 275 nDE genes — the confound the test must condition through.)
3. **Axis-specificity** `S` = NES-style concentration of |z| on axis genes vs transcriptome, **with leave-marker-out** (a perturbation whose target is itself an axis marker is scored on an axis rebuilt without it).
4. **Reproducibility** `R` = Pearson correlation of the effect direction across two random half-splits of the perturbation's cells (non-targeting `R`≈0.00, correct null).
5. Gate to detectable subset (`M` ≥ median); residualize `S`, `R` on `M` by rank-regression; form `C` = mean residual percentile of `S` and `R`.
6. **Magnitude-matched negatives** (8 per positive, matched on `M` + cells/perturbation): positive vs negative magnitude balanced (median 746 vs 749, MWU p=0.87) — the confound is removed.
7. **Conditional LR test** (`C`, `S`, `R` over `M`) and **bootstrap ΔAUPRC** (`M` → `M`+`C`, 2000 resamples).

## 5. Result

Primary run (nDE magnitude, median gate): **33 positives, 219 matched negatives**.

| Quantity | Value | Requirement for PASS |
|---|---|---|
| Spearman(`C`, `M`) | **−0.005** (orthogonal ✅) | small |
| Conditional LR test, `C` over `M` | **p = 0.195** (n.s.) | p < 0.05 ❌ |
| Conditional LR, `S` over `M` | p = 0.062 (marginal) | — |
| Conditional LR, `R` over `M` | p = 0.589 (n.s.) | — |
| AUPRC magnitude-only → +`C` | 0.162 → 0.220 | — |
| **Bootstrap ΔAUPRC** | **+0.060, 95% CI [−0.013, +0.204]** | CI excludes 0 ❌ |
| P(ΔAUPRC > 0) | 0.894 | — |

**Both PASS conditions fail:** the bootstrap ΔAUPRC 95% CI includes 0 **and** the conditional
LR test is non-significant. By the pre-registered criterion (invariant §3), **CCI is FAIL /
falsified in this system.**

### Robustness (the FAIL is not an artifact of one choice)

| Variant | n_pos | n_neg | Spearman(C,M) | LR p (C) | ΔAUPRC | 95% CI | verdict |
|---|---|---|---|---|---|---|---|
| nDE magnitude, gate=median (primary) | 33 | 219 | −0.005 | 0.195 | +0.060 | [−0.013, 0.204] | **FAIL** |
| effect-norm magnitude, gate=median | 33 | 216 | −0.013 | 0.283 | +0.059 | [−0.019, 0.218] | **FAIL** |
| nDE, looser gate (25th pct) | 42 | 280 | +0.038 | 0.018 | +0.074 | [−0.012, 0.213] | **FAIL** |
| nDE, stricter gate (67th pct) | 16 | 105 | −0.041 | 0.691 | +0.044 | [−0.041, 0.198] | **FAIL** |

Every variant FAILs. The ΔAUPRC point estimate is consistently small-positive (+0.04 to +0.07,
vs +0.23 in Marson) but its CI never clears 0. At the looser gate the conditional LR reaches
p=0.018, but the ΔAUPRC CI still spans 0 — the two-condition PASS bar is never met. `C` remains
orthogonal to magnitude throughout (|Spearman| ≤ 0.04), so this is not a failure of the
residualization; it is a genuine absence of conditional signal.

## 6. Interpretation — the property is immune-scoped

Combining the anchor and the far test (see figure):

- **Marson CD4+ (immune): PASS** — ΔAUPRC +0.229 [0.072, 0.405].
- **Replogle RPE1 (non-immune): FAIL** — ΔAUPRC +0.060 [−0.013, 0.204].

Per the invariant's own decision rule (§6, "PASS in immune only → immune-scoped property"), the
honest reading is **(b): a domain-scoped property**. The magnitude-conditional axis-specificity /
reproducibility signal that separates controllers from associates is a real feature of the
immune (T-cell) system tested, but it does **not** generalize to a non-immune proliferation
screen. This is a genuine, publishable boundary on the property — not a null result to be spun.

### Why this is plausible (mechanistic, not post-hoc excuse)

In a proliferation screen the "controllers" (CDKs, APC/C, replication licensing) act largely by
**dosage on a single dominant axis** — knock them down and the cell-cycle program collapses more
or less uniformly. There is little *axis-specific-beyond-magnitude* structure to detect:
magnitude and controllership are nearly collinear once you're on the cell-cycle axis, so
conditioning on `M` removes essentially all of the discriminative signal. In the immune system,
by contrast, state transitions (memory/effector/exhaustion/Treg) are governed by regulators
whose effects are *directional and axis-selective* independent of their raw size — which is what
`C` captures. The far-transfer FAIL is consistent with the biology, not merely with a lack of
statistical power (n_pos=33 is comparable to Marson's 19).

## 7. Files

- `far_nonimmune_cci_report.md` — this report.
- `far_nonimmune_cci_scores.csv` — Marson anchor + 4 robustness variants (n_pos, n_neg, Spearman(C,M), LR p, ΔAUPRC, CI, verdict).
- `cci_invariance_far_transfer.png` — the invariance figure (ΔAUPRC ± 95% CI, immune PASS vs non-immune FAIL).

## 8. Reproducibility

- Data: scPerturb Zenodo record 13350497, file `ReplogleWeissman2022_rpe1.h5ad` (SHA verified by size 1,236,886,900 bytes).
- Effect matrix: pseudobulk CP10k+log1p, log-FC vs 11,485 non-targeting cells, z-scored across 2,394 perturbations.
- Method: `isci-controllership` skill (`conditional_lr_test`, `expression_matched_negatives`, `bootstrap_auprc_gain`); leave-marker-out axis; seeds fixed (split-half rng=0, bootstrap seed=0, 2000 resamples).
- Axis: Tirosh S+G2M markers (scanpy standard). Labels: curated cell-cycle control machinery (CORUM/GO-consistent), intersected with perturbed + detectable genes.
