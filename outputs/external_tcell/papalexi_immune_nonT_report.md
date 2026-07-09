# EXEC-3 / MASTER_ROADMAP Phase 7 — immune non-T boundary far-test

**VERDICT: NOT-EVALUABLE** (data boundary, not a null). The one readily-available immune-non-T
Perturb-seq — **Papalexi 2021 ECCITE-seq (THP-1 myeloid)** — cannot support a *non-circular* CCI
test: it has **no baseline (unstimulated) condition** (4 untreated vs 20,725 IFN-γ-treated cells),
so the only definable state axis is the IFN-γ response program itself, which is **circular** with
the IFN-γ-regulator positive set. Per the CCI's mandatory anti-circularity guard (leave-marker-out
axis + an axis independent of the label set), the far-test cannot be run here without fabricating an
axis. The question "is CCI T-cell-scoped or immune-state-scoped?" therefore stays **open,
data-limited** — pre-registered for a future myeloid/DC/NK screen that has a baseline condition.

---

## Gate log

- **Papalexi 2021 ECCITE-seq** (`PapalexiSatija2021_eccite_RNA.h5ad`, scPerturb Zenodo 13350497),
  THP-1 (myeloid leukemia line), 20,729 cells × 18,649 genes, raw counts.
- **Contrast exists** (unlike Shifrut): 25 targets → **15 canonical IFN-γ/PD-L1 regulators**
  (IFNGR1/2, JAK2, STAT1/2/3/5A, IRF1/7, NFKBIA, CMTM6, MARCH8, UBE2L6, PDCD1LG2, SPI1) vs **10
  non-canonical** candidate negatives (ATF2, BRD4, CAV1, CD86, CUL3, ETV7, MYC, POU2F2, SMAD4,
  TNFRSF14). So a positive/negative split is available.
- **The blocker is the axis, not the labels:**
  1. **No baseline condition.** `hto` shows 20,725 IFN-γ-treated cells and **4** untreated — a
     leave-marker-out state axis (treatment − baseline in control cells, the Schmidt recipe) cannot
     be built.
  2. **The only available axis is circular.** The system's sole state program is the IFN-γ response;
     but the positives ARE IFN-γ-pathway regulators, so they move that axis by construction. Testing
     axis-specificity (S) against an axis defined by the same pathway as the labels violates the
     anti-circularity guard (`conditional_controllability_invariant.md`: axis must be independent of
     the label set; magnitude-matched negatives + leave-marker-out are mandatory).
- A reproducibility-only (R, no S) variant is possible but is **not the CCI** — every prior result
  shows axis-specificity S is the immune-specific carrier (Marson S-led; Schmidt S_resid p=0.099;
  Frangieh S_resid p=0.083). Reporting an R-only number as "the CCI far-test" would misrepresent it,
  so we do not.

## What a valid immune-non-T far-test needs (pre-registered)

A myeloid / DC / NK perturbation screen with: (a) a **baseline/unstimulated condition** (to derive a
state axis by leave-marker-out), (b) a state axis **independent** of the regulator label set
(e.g. a differentiation or activation axis, not the same pathway as the positives), (c) ≥2
replicates, (d) a known-regulator positive set with enough non-regulator targets for
magnitude-matched negatives. Candidates to scout later: an NK-cell CRISPR Perturb-seq, or a
monocyte→macrophage/DC differentiation Perturb-seq with an activation axis.

## Bottom line

The immune-non-T boundary is **not yet decidable with in-window public data** — reported honestly as
NOT-EVALUABLE rather than forced. This does not weaken the three-system immune replication (Marson
PASS; Schmidt + Frangieh directional near-miss with C⊥magnitude replicating): it marks the next data
gap. The scoping claim stays exactly where the evidence puts it — **immune-scoped, demonstrated in
T cells; myeloid/NK generalization untested for lack of an evaluable dataset.**

### Deliverables
- `papalexi_immune_nonT_report.md` (this file). No scores CSV / verdict JSON: the test was not run
  (NOT-EVALUABLE at the axis gate) — no fabricated axis or numbers.
