# GSE216571 Direction-Replication Attempt — HARD GATE TRIGGERED

## Verdict
**GATE STOPPED: metadata not parseable to patient-level response labels — future validation.**
No responder/non-responder (or CR/PR/PD) label exists in the GEO deposit for GSE216571.
The direction-replication test (resistance modules higher in non-responders / sensitivity
modules higher in responders) **cannot be run** and was NOT forced. No labels were fabricated.

## Dataset
- GSE216571 — GEO series title "The Preexisting T Cell Landscape Determines Response to
  T Cell-Engager Therapy" (relapsed/refractory multiple myeloma, bone-marrow CD3/CD45, 10x 5';
  BioProject PRJNA894244). Author/journal not verified in-session — not cited here.
- RAW tar downloaded (723 MB, 62 per-sample genes×cells count CSVs). All 62 parsed.
- 1 sample dropped: PT18_late_CD3 (total_counts = 0, empty file).
- Cohorts recovered from sample titles/filenames:
  - TCE patients: 18 patients, 48 samples (timepoints: pre / early / late; sorts: CD3 / CD45)
  - CAR-T pre: 9 samples;  Healthy in-vitro (HDIV): 4 samples

## Why the gate triggered (evidence)
The ONLY per-sample metadata fields in the GEO series matrix are:
  tissue = bone marrow MNC | cell type = T&NK or CD45+ | genotype = n.a. | treatment = RRMM.
Sample identity encodes patient (PT1–PT19), timepoint (pre/early/late), sort (CD3/CD45) —
but NO clinical response. Supplementary = RAW.tar + filelist.txt only; filenames carry no
response token (apparent "PR" hits were substring matches inside "_pre_"). The responder
classification lives only in the paper's supplementary tables and is NOT mapped to the GEO
PT IDs in any deposited file. Mapping it by hand would be fabrication → gate holds.

## What WAS produced (honest, reusable groundwork)
Per-sample pseudobulk module scores on real expression (CPM → log2(CPM+1) → mean over module
genes; all 34 module genes detected in every sample). This matrix is response-test-ready the
moment true patient labels are obtained (e.g. from the authors / paper supplement). Until then
it is DESCRIPTIVE ONLY.

### Descriptive observations (NOT a response test; timepoint/cohort contrasts only)
- NR_exhaustion: TCE late > TCE pre (median 5.04 vs 4.39, all TCE; 5.12 vs 4.33 CD3-only) — exhaustion accrues on therapy,
  biologically coherent with the paper's thesis, but says nothing about responder split.
- R_memory_stem / R_migration: decline pre→late in TCE — coherent with memory→effector drift.
- All contrasts are between cohorts/timepoints, which are NOT response groups. No p-values on
  clinical outcome are reported because no outcome label exists.

## Modules that replicated DIRECTION
NONE — the direction test could not be performed (no labels). This is a STOP, not a negative result.

## Recommendation
To complete this validation: obtain the patient-level response mapping (PT ID → responder
status, and the pre-treatment baseline definition) from the paper's supplementary tables or the
corresponding author. Then run Mann-Whitney per module on the baseline (pre) CD3 samples,
patient-level, one score per patient. The score matrix (module_scores_per_sample.csv) is ready.
