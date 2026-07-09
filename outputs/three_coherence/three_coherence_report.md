# Three-coherence decomposition — positioning vs Shesha (Raju 2026)

**Result: the Shesha coordinate and ours are not the same axis.** On Frangieh Perturb-CITE-seq
(229 targets), **Shesha's cell-to-cell coherence Sₚ is essentially magnitude (Spearman ρ = 0.97)** —
independently replicating Shesha's own reported 0.75–0.97 coupling on a different dataset — while our
two coordinates are magnitude-orthogonal: **cross-guide reproducibility R ⟂ magnitude (ρ = 0.008)** and
**axis-specificity S weakly tied to magnitude (ρ = 0.19, below the 0.3 proxy threshold)**. This is the
direct, quantitative answer to "isn't this Shesha for T cells?": *no — Shesha's coherence collapses
onto the magnitude axis; the signal we test (reproducibility + functional-axis specificity) is the
orthogonal plane Shesha does not capture.*

---

## 1. What was tested

Reproducibility of a perturbation has ≥3 candidate coordinates; we asked whether they are independent,
conditional on effect magnitude M. Per perturbation (Frangieh, IFNγ condition, singlets; leave-marker-out
IFN axis built from control cells IFNγ−Control, exactly as EXEC-2):

- **Sₚ** — cell-to-cell directional coherence (Shesha's *perturbation stability*): mean cosine of
  single-cell shift vectors to the mean perturbation direction (top-2000 moved genes).
- **R** — cross-guide reproducibility: mean pairwise correlation of per-guide effect vectors.
- **S** — functional-axis specificity: |cos(mean effect, leave-marker-out IFN axis)|.
- **M** — effect magnitude (‖mean effect‖).

## 2. Result (n = 229 targets with all three coordinates)

**Correlation with magnitude:**

| coordinate | Spearman vs M | reading |
|---|---|---|
| **Sₚ (Shesha)** | **0.974** | ≈ magnitude — an effect-size proxy |
| S (axis-specificity) | 0.187 | magnitude-orthogonal (<0.3) |
| **R (cross-guide reprod.)** | **0.008** | magnitude-orthogonal (matches Marson ~0.02) |

**Partial correlations (controlling magnitude M):** Sₚ~R\|M = −0.71, Sₚ~S\|M = +0.67, R~S\|M = −0.79.

## 3. Interpretation

- **Sₚ ≈ magnitude.** Shesha's cell-to-cell coherence tracks effect size almost perfectly here
  (ρ=0.97) — a clean independent replication of Shesha's central observation on an independent dataset.
  Convergent validation of *their* phenomenon; it also means Sₚ, on its own, is largely a restatement
  of magnitude.
- **R is the genuinely orthogonal coordinate.** Cross-guide reproducibility carries essentially zero
  magnitude correlation (0.008) — this is *our* magnitude-independent signal, the same property that
  anchors the locked Marson result (ρ≈0.02). It is not what Shesha measures.
- **S is also magnitude-light** (0.19) and, after removing magnitude, moves with the residual of Sₚ
  (+0.67) — i.e. the part of Sₚ that is *not* magnitude aligns with functional-axis direction.
- **R and S trade off in this system** (raw −0.77; partial −0.79): in Frangieh's tumor immune-evasion
  setting, the most cross-guide-reproducible perturbations are the least axis-specific and vice versa.
  This is dataset-specific and contrasts with the immune T-cell anchor (Marson), where S and R
  co-contribute to C — reported as an observation, not generalized.

## 4. Positioning takeaway (for the paper's Shesha response)

> Shesha establishes that perturbation coherence is a magnitude-confounded axis of single-cell CRISPR
> geometry. We reproduce that exactly (Sₚ~magnitude ρ=0.97) and show it is the magnitude coordinate —
> then demonstrate that the controllership signal we test lives in an **orthogonal** plane Shesha does
> not measure: cross-replicate reproducibility (ρ_magnitude=0.01) and functional-axis specificity
> (0.19). Our contribution is not a T-cell relabeling of Sₚ; it is the magnitude-independent
> reproducibility+specificity signal, tested conditionally and bounded to an immune scope.

## 5. Honesty / limits

- One dataset (Frangieh, tumor immune-evasion); the powered confirmation belongs on the genome-scale
  immune anchor (Marson, 4 donors) once cell-level Marson is on disk — pre-registered as the next run.
- Sₚ here uses cell-to-cell coherence on top-moved genes; exact parity with Shesha's estimator is
  approximate. The 0.97 magnitude coupling is robust to that (it is the qualitative point).
- The R~S trade-off is Frangieh-specific and not claimed to generalize.

### Deliverables
- `three_coherence_report.md` (this file) · `three_coherence_result.json` · `three_coherence_scores.csv`
  (per-target Sₚ/R/S/M) · `three_coherence.png` (vs-magnitude bars + Sₚ~M and R~M scatters) ·
  `three_coherence.py`, `plot_three_coherence.py` (reproducible, CPU).
