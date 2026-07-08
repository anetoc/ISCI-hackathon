# ISCI Direction-Replication — GSE208052 (CAR-T infusion products)

## Task
Test whether the signed clinical T-cell modules derived from the Functional CAR-T atlas
**replicate direction** in an independent cohort. This is DIRECTION-REPLICATION ONLY —
not a response predictor. Unit of analysis = patient (pseudobulk), not cell.

## Dataset
- **GSE208052** (Varadarajan lab; Haradhvala/Rezvan et al.). scRNA-seq of CD19 CAR-T
  **infusion products** from **9 LBCL patients**, response scored at **3 months**.
- Processed normalized expression CSV: 21,551 genes x 21,469 cells (SAVER-recovered,
  Seurat-normalized). Cell barcodes encode patient+response: CR-1..CR-5, PD-1..PD-4.
- **HARD GATE: PASSED.** Metadata parses to patient-level response directly from the
  barcode suffix. GROUPING NOTE: the barcode "PD-1..PD-4" bucket is the dataset's own
  label and is a **non-CR** bucket, not pure progressive disease. The series
  overall_design states the 3-month breakdown is **5 CR, 2 PD, 2 PR** (and at 6 months
  4 CR, 3 PD, 2 PR); the "5xCR/4xPD" phrasing appears only in the Sample_title field,
  which collapses the 2 PR patients into the "PD" label. We therefore analyze
  **Responder = CR (n=5) vs Non-responder = non-CR (n=4, = 2 PD + 2 PR at 3 mo)**, using
  the labels the dataset barcodes carry. This CR-vs-(PD+PR) dichotomy is a deliberate
  simplification, disclosed here; it does not match a literal "5 CR, 4 PD" overall_design.

## Method
1. Pseudobulk: mean normalized expression per gene per patient (9 patients), streamed
   from the CSV. Cells/patient: CR-1 1353, CR-2 3619, CR-3 1506, CR-4 1864, CR-5 1969,
   PD-1 4779, PD-2 3408, PD-3 2830, PD-4 141.
2. Gene z-score across the 9 patients; module score = mean z of member genes per patient.
3. Direction test: one-sided Mann-Whitney U in the atlas-expected direction
   (resistance: PD>CR; sensitivity: CR>PD). All module genes were present in the
   dataset (38 gene slots across 6 modules; 34 unique after de-duplicating TIGIT,
   ENTPD1, CCR7, SELL, each shared by two modules); genes_missing empty for every module.

## Result — 3 / 6 modules replicated direction
All three **SENSITIVITY** modules pointed the atlas-expected way (higher in responders);
all three **RESISTANCE** modules did NOT (they trended higher in responders here).

       module    category expected  CR_mean  PD_mean  delta  direction_consistent  mannwhitney_p_onesided  genes_used genes_missing
      NR_Treg  resistance    PD>CR    0.263   -0.329 -0.591                 False                   0.857           7            []
NR_exhaustion  resistance    PD>CR    0.211   -0.264 -0.475                 False                   0.635           6            []
toxicity_infl  resistance    PD>CR    0.062   -0.077 -0.138                 False                   0.722           4            []
R_memory_stem sensitivity    CR>PD    0.433   -0.541  0.973                  True                   0.032           8            []
  R_migration sensitivity    CR>PD    0.281   -0.351  0.633                  True                   0.206           7            []
    R_killing sensitivity    CR>PD    0.009   -0.012  0.021                  True                   0.548           6            []

## Interpretation (small-N — this is direction replication with n=9, not a validation)
- **Sensitivity axis reproduces independently.** R_memory_stem / R_migration / R_killing
  are all higher in CR than PD, and R_memory_stem reaches nominal significance (p=0.032,
  one-sided, uncorrected). This is concordant with both the atlas and GSE208052's own
  published finding (responders enriched in killing, migration, actin/TCR-clustering).
- **Resistance axis does NOT replicate here.** NR_Treg, NR_exhaustion and toxicity_infl
  trended higher in responders (opposite the atlas), all non-significant. In this specific
  cohort — infusion *products* (pre-infusion), not post-infusion/tumor T cells — Treg and
  exhaustion signal in the product may not track 3-month resistance; the atlas Treg
  finding was itself only p=0.04 uncorrected. Direction is cohort/compartment-dependent.

## Honest caveats
- **n=9** (5 vs 4). No multiple-testing survival is claimed; p-values are one-sided,
  uncorrected, reported as effect-direction descriptors only.
- Infusion-product compartment differs from the atlas's mix; a resistance program present
  in expanded/tumor-infiltrating T cells need not be visible pre-infusion.
- No AUROC / classifier reported by design.

## Verdict
GATE PASSED. The **sensitivity axis direction replicates** in an independent CAR-T cohort
(3/3, one nominally significant); the **resistance axis does not** in this product-stage
cohort (0/3). Reported as small-N (n=9) direction replication with a CR-vs-non-CR
(2 PD + 2 PR) grouping as disclosed above.
