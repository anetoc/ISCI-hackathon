# Experimental protocols (Paper 2 / prospective) — gaps 9, 8/17, 18, 19

These gaps cannot be computed in silico. They are design stubs so the roadmap is concrete, NOT
claimed as results. Each is a wet-lab or clinical protocol requiring institutional resources and, for
the cohort, IRB/CEP approval.

## Gap 9 — Phospho-flow / phosphoproteomics time course (rheostat vs state controllers)
- **Cells:** primary human T cells; ideally CD19/BCMA CAR-T or TCR-stimulated CD8.
- **Perturbations:** IKBKB (NF-κB), LAT/LCK/ZAP70/PLCG1 (TCR-proximal positives/rheostat), ZC3H12A
  (Regnase-1), RCOR1/KDM1A/CXXC1/MED13 (non-TCR candidates from the controller map).
- **Short time course (signaling):** 5/15/30/60 min post-stimulation — pLCK, pZAP70, pLAT, pPLCγ1,
  pERK, pS6, p65/NF-κB, NFAT nuclear translocation.
- **Long time course (state):** 24–72 h — memory/exhaustion/killing markers.
- **Decision rule:** separate rheostat controllers (move early phospho-signaling) from state
  controllers (move late state without proximal signaling change) from toxic controllers (reduce
  everything via inviability). Directly tests the controller-map hypotheses (Fig. IEC controller map).

## Gap 18/19 — Functional + multiomic validation of the 8–12 gene panel
- **Panel:** positive controls (GATA3, STAT6, IRF1); novel controllers (ZC3H12A, RCOR1, BCLAF1,
  TFAP4, PDCD5, TWF1, CXXC1, MED13); dangerous controls (IKBKB, PRKDC).
- **Functional readouts:** viability, expansion, serial killing (Incucyte/live-cell), CD107a, GZMB,
  IFNγ, exhaustion after repeated antigen (PD-1/TIM-3/LAG-3/TOX), memory (TCF7/CCR7/SELL/IL7R).
- **Chromatin/RNA layer (mechanism):** ATAC-seq / CUT&RUN for chromatin candidates; SLAM-seq / mRNA
  decay for RNA candidates (ZC3H12A). Confirms the controller acts on its predicted mechanistic layer.
- **Advancement gate (per candidate):** moves desired axis AND preserves viability/expansion AND
  reproducible direction across ≥2 donors AND beats a global-activation control.

## Gap 8/17 — Prospective single-protocol cohort (the correct clinical test)
- **Rationale:** the public multi-study atlas gave a well-powered NULL (leave-study-out collapse); the
  right test is a single-protocol prospective cohort, not more mining of the same atlas.
- **Population:** one disease (LBCL *or* ALL *or* MM) and one therapy (CD19 CAR-T *or* BCMA CAR-T *or*
  bispecific) — do NOT pool into the primary endpoint.
- **Samples:** pre-infusion product; blood D7/D14/D28; marrow/tissue if available.
- **Readouts:** scRNA + CITE-seq, CyTOF/flow IEC panel, TCR clonality, CAR copy/expansion, cytokines;
  uniform outcome (CR/PR/NR, MRD, PFS, CRS/ICANS).
- **Mandatory baselines (the atlas showed these dominate):** CD8 fraction, Treg fraction, disease,
  product/timepoint, tumor burden, lymphodepletion, batch/protocol.
- **First objective (not AUROC):** show IEC axes are stable and do NOT collapse after controlling
  CD4/CD8/composition. Second: test whether A_persist or kill/exhaustion decoupling adds over
  composition. **Requires IRB/CEP protocol, pseudonymization, frozen analysis plan, no individual
  clinical return** before any institutional data is touched.
