# GSE223655 — Direction-Replication of ISCI Sensitivity Modules

**Dataset:** GSE223655 — *"Characteristics of premanufacture CD8+ T cells determine CAR-T efficacy in patients with DLBCL"* (bulk RNA-seq, tandem CD19/CD20 CAR-T, r/r DLBCL).
**Design:** 65 samples across 6 sorted compartments from CR and PD patients; per-sample FPKM (`GSE223655_fpkm.txt.gz`).
**Task:** Direction-replication ONLY of the 3 ISCI **sensitivity** modules (R_memory_stem, R_migration, R_killing). No response predictor, no AUROC, patient/sample-level only.

## HARD GATE — PASSED
The GEO series-matrix carries an explicit per-sample `disease state` field (`CR patient` / `PD patient`) aligned 1:1 to GSM accessions, patient IDs, cell subtype, and the FPKM sample columns (positional `sample1`..`sample65` ↔ Sample 1..65). Labels are directly patient-mappable — **no fabrication required**. All 65 samples labelled: **33 CR / 32 PD**, balanced within every compartment.

| Compartment | CR | PD |
|---|---|---|
| CD8+CAR T cells (product) | 6 | 5 |
| CD4+CAR T cells (product) | 6 | 6 |
| Non-Naïve CD4 (apheresis) | 6 | 6 |
| Non-Naïve CD8 (apheresis) | 5 | 5 |
| Naïve CD4 (apheresis) | 5 | 5 |
| Naïve CD8 (apheresis) | 5 | 5 |

Gene coverage: **all 41 module genes present** in the FPKM matrix (8/8, 7/7, 6/6, 7/7, 6/6, 4/4).

## Method
Per compartment: collapse transcript rows to genes (sum FPKM), log2(FPKM+1), per-gene z-score across that compartment's samples, module score = mean z over module genes. One-sided Mann–Whitney U, CR > PD for sensitivity modules (uncorrected, direction-only). Resistance modules reported for completeness (CR < PD expected).

## PRIMARY compartment — CD8+CAR T product (analog of GSE208052 CD8 arm)
| Module | Axis | n CR/PD | mean CR | mean PD | Δ(CR−PD) | p (1-sided) |
|---|---|---|---|---|---|---|
| R_memory_stem | sensitivity | 6/5 | +0.413 | -0.496 | +0.909 | 0.0043 |
| R_migration | sensitivity | 6/5 | -0.035 | +0.042 | -0.077 | 0.6039 |
| R_killing | sensitivity | 6/5 | -0.033 | +0.040 | -0.073 | 0.5346 |
| NR_Treg | resistance | 6/5 | -0.005 | +0.006 | -0.011 | 0.6039 |
| NR_exhaustion | resistance | 6/5 | -0.069 | +0.082 | -0.151 | 0.5346 |
| toxicity_infl | resistance | 6/5 | +0.128 | -0.153 | +0.281 | 0.8355 |

**R_memory_stem replicates strongly and significantly (Δ=+0.91, p=0.0043).** R_migration and R_killing do not (Δ≈0, n.s.).

## Cross-compartment view (sensitivity Δ, CR−PD; * = p<0.05 one-sided)
R_memory_stem is **positive (CR>PD) in ALL 6 compartments** and significant in 5 (CD8+CAR p=0.004, CD4+CAR p=0.047, Non-Naïve CD4 p=0.047, Naïve CD4 p=0.028, Naïve CD8 p=0.004). **Note:** these 6 compartments are sorted cell fractions from the same ~12-patient cohort (not independent samples), so they are correlated repeated measures, not 6 independent tests. R_migration: positive in 5/6 but never significant. R_killing: inconsistent sign, never significant.

## Verdict
**1 of 3 sensitivity modules replicates by direction — R_memory_stem — but robustly.** It is the single most reproducible axis, positive across every sorted CD4/CD8 product and apheresis compartment, exactly matching this study's own conclusion that CR patients carry higher memory-gene/transcription-factor expression in CD8 CAR-T *and* in source naive cells. This is a fully independent (different cohort, different platform — bulk vs scRNA-seq, tandem CD19/CD20 vs CD19) replication of the memory-stem sensitivity signal seen in GSE208052 (n=9), strengthening the compartment hypothesis for the memory-stem component specifically. The migration and killing components of the sensitivity axis do **not** replicate here.

## Honest caveats
- **Small N** (5–6 per group per compartment); one-sided, **uncorrected** p-values; **direction-only** — no effect-size CI, no multiplicity control, no response classifier.
- Positive results should be read as *direction consistency*, not calibrated prediction. With 3 modules × 6 compartments = 18 one-sided tests, some nominal hits are expected by chance. The R_memory_stem pattern is consistent (6/6 correct sign, 5/6 nominally significant), but the 6 compartments are **NOT independent cohorts** — they are different sorted cell fractions (CD4/CD8 CAR product, non-naïve, naïve) drawn from the same pool of only **12 unique patients** (ids 19,21,24,31,54,56,59,73,77,79,80,87). The two lowest-p compartments (CD8+CAR and Naïve CD8, both p=0.004) share 10/10 of the same patients, so their p-values are correlated repeated measures, not independent replications. The cross-compartment consistency therefore reflects that the memory-stem signal is stable across cell fractions within one cohort — it does **not** constitute 6 independent tests and should not be read as such.
- Same-study circularity risk is low for *cross-dataset* claims: GSE223655 is independent of the atlas that defined the modules, but its own DE analysis motivated the memory-stem hypothesis, so this confirms *transferability of a pre-specified module*, not blind discovery.
- FPKM (not raw counts); no batch/donor modeling beyond within-compartment z-scoring.

## Artifacts
- `outputs/external/gse223655_module_scores.csv` — per-sample module scores (all 6 modules × 65 samples) with GSM, patient id, compartment, CR/PD.
- `outputs/external/gse223655_mannwhitney_all.csv` — full test table (6 modules × 6 compartments).
- `outputs/external/gse223655_sensitivity_heatmap.png` — sensitivity Δ heatmap.
