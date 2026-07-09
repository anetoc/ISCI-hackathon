# Integration architecture — see canonical `INTEGRATION_ARCHITECTURE.md`

**This draft has been superseded.** Claude Science independently produced the canonical, code-backed
version at **`reports/INTEGRATION_ARCHITECTURE.md`** (the `CondInfo(X | magnitude)` operator, the
controllability tensor `T[gene, axis, system, modality]`, the modality-adapter contract, and the
`isci/run_layer.py` driver). The two documents converged on the same design independently — same
modality-agnostic operator, same late-fusion/rank-of-residuals discipline, same GPU-produces-features /
CPU-runs-test split, same bench-to-bedside ladder — which is itself a validation of the design.

Use the uppercase file as the single source of truth. Two pieces from this draft are now concrete
artifacts rather than proposals:

- The **RNA↔protein cross-layer** exercise → `outputs/external_tcell/cross_layer_report.md` (Frangieh
  concordance ρ=0.24, native protein layer AUROC 0.90; Papalexi native-PD-L1 rescue AUROC 0.77).
- The **three-coherence decomposition** (Shesha Sₚ vs our cross-donor R vs axis-specificity S) →
  `outputs/three_coherence/three_coherence_report.md` (Sₚ ≈ magnitude ρ=0.97; R ⟂ magnitude ρ=0.01).

Both are ready to register as slices/evidence in the controllability tensor (`isci/run_layer.py`).
