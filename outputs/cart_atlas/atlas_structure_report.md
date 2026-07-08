# CAR-T atlas — structure + patient-response label GATE (Brief 03)

**VERDICT: EVALUABLE** — patient-level response labels exist, are clean, patient-mappable,
and adequately powered (87 labeled patients, 60 responders / 27 non-responders; 263,928
labeled cells). Brief 04 (clinical prediction) can proceed **with the confound controls
documented in §5** (leave-patient-out CV is mandatory; response is partially structured by
study and disease — NHL-dominated — so per-study reporting and a within-NHL primary are
required).

---

## 1. Provenance (verified against the actual download)

- **Zenodo record 19066393**, concept DOI `10.5281/zenodo.17213452` (ML4BM-Lab / Univ.
  Navarra). Title: *"An open CAR-T single-cell atlas to enable in-depth characterization and
  rational engineering of CAR-T products."* Confirmed via Zenodo API.
- Four files on the record (sizes verified):

  | file | size | note |
  |---|---|---|
  | `Atlas_integ_scArches_FINAL_V5.h5ad.gz` | 2.73 GB | **downloaded + gated (this report)** — integrated CD3+CAR+ object |
  | `Python_scVI_adata_big_V4_state4.h5ad.gz` | 2.42 GB | scVI object (has latent) — for Brief 02 |
  | `Python_scVI_adata_big_V4_state4_Normalized.h5ad.gz` | 5.06 GB | normalized variant |
  | `scVI_hub_adata.h5ad` | 15.47 GB | full scVI hub object |

- Downloaded server-side with `aria2c -x16 -s16` to `data_public/cart/`; gzip integrity
  verified (`gzip -t` OK); decompressed to 15.18 GB. **No files uploaded from a laptop.**
- **Reported numbers vs the brief's expectations:** brief said "~414k CD3+CAR+ after QC, 11
  phenotypes, a trained scVI model." Actual integrated object: **455,370 cells**, **11
  phenotypes** (`manual_celltype_annotation_high`) ✓, scVI evidenced by `_scvi_batch`/
  `_scvi_labels` in `obs` — but the **scVI latent embedding is NOT in this object's `obsm`**
  (see §3); it lives in the `Python_scVI_*`/`scVI_hub` files. Numbers are close to but not
  identical to the brief's estimates — reported as found.

## 2. Structure

- **Shape:** 455,370 cells × 48,740 genes.
- **X = raw integer counts** (min 0, max 310, integer-valued, variable library sizes 852–5423
  in the sampled head). No `.raw`, no `layers`. Brief 04 normalizes/log1p itself.
- **`var_names` = HGNC gene symbols** (A1BG, A1BG-AS1, …) — direct match for the IEC gene sets.
- **`obsm`:** `X_umap` only. **No `X_scVI`.** `uns`: `neighbors`, `umap`, `leiden`,
  `cell_type_colors`.
- **Studies:** 14 (`orig_ident` / `celltypist_majority_voting`): Bai, Boroughs, Deng, Good,
  Haradvala, Jordana, Li_X_Cancer_Cell_letter, Li_X, Lynn, Melenhorst, Rodriguez_Marquez,
  Sheih, Wang, Xhangolli (+ healthy/mouse subsets).
- **Patients:** 119 unique (`Norm_Patient_Name`, 0 missing). **Samples/products:** 193
  (`Product` = `_scvi_batch`).
- **Phenotypes (11):** CD8 cytotoxic (160,580), Proliferative T (122,294), CD4 central memory
  (89,699), CD4 effector memory, CD8 effector memory, Ribosomal-enriched, Regulatory T, CD8
  memory, Monocyte-like T, CD4 cytotoxic, Apoptotic T. → **CD4/CD8 identity is derivable**
  (needed for the CD8-identity baseline in Brief 04) even though there is no explicit CD4/CD8
  column.
- 56 `obs` columns total (full schema in `atlas_structure_raw.json`). Beyond the gate columns,
  the atlas carries rich engineering metadata: `ScFv`, `Antigen`, `CAR_Construct`, `CAR_Gen`,
  `Costim_Domain_1`, `Product`, `Sex`, `Age`, `Time_Point` (24 levels), `Stimulated`,
  `Technology`, cell-cycle (`S.Score`/`G2M.Score`/`Phase`), QC (`nCount_RNA`, `mitoRatio`).

## 3. Note for Brief 02 (scVI axes)

This integrated object has **no cell-level scVI latent in `obsm`** (only UMAP). Brief 02's
cell-level IEC-axis estimation on the CAR-T atlas should use `Python_scVI_adata_big_V4_state4`
(has the latent / states) or re-run scVI on this counts matrix on the RTX 6000. Flagging so
Brief 02 pulls the right object rather than assuming the latent is here.

## 4. THE GATE — patient-level response labels (the decisive check)

**Response columns present and populated** (`obs`):

| column | categories (cell counts) | cells labeled | patients labeled |
|---|---|---|---|
| `Initial_Response` | CR 179,828 · PR 35,183 · NR 48,917 | 263,928 | 87 |
| `Max_Response` (primary) | CR 184,867 · PR 30,144 · NR 48,917 | 263,928 | 87 |
| `Anytime_Response` | Yes 215,011 · No 48,917 | 263,928 | 87 |
| `Anytime_CR` | Yes/No | 263,928 | 87 |
| `Relapse` | No 104,861 · Yes 47,492 | 152,353 | 34 |

**Patient-level counts (primary = `Max_Response`, one row per patient):**
- **87 / 119 patients labeled.** CR 51 · PR 9 · NR 27 → **responders (CR/PR) = 60, non-responders (NR) = 27.**
- The 32 unlabeled patients are the **healthy donors + osteosarcoma mouse-model CTILs** (191,442
  cells) — correctly missing, not a data defect.
- **Within-patient label consistency: perfect.** 0 patients carry more than one distinct value
  for any response column → labels are patient-level constants, safely mappable cell→patient.
- Labeled patients span diseases NHL 77 · CLL 4 · MM 3 · ALL 2 · PCL 1; per-patient cell counts
  range 52 – 25,263 (median 1,573).
- Toxicity labels also present at patient level: `CRS`/`CRS_Grade`, `ICANS`/`ICANS_Grade`
  (242,570 cells labeled) — enables the secondary ICANS analysis the brief mentions.

`atlas_patient_response.csv` written: one row per patient × {study, disease, n_cells,
Initial/Max/Anytime response, Relapse, CRS, ICANS}.

## 5. Confound check — response × study/disease (decides whether CV is meaningful)

**Patient-level study × response (CR/PR/NR), labeled patients only:**

| study | CR | PR | NR |
|---|---|---|---|
| Haradvala_et_al | 20 | 2 | 9 |
| Deng_et_al | 9 | 1 | 13 |
| Li_X_Cancer_Cell_letter | 6 | 3 | 3 |
| Good_et_al | 6 | 2 | 1 |
| Sheih_et_al | 4 | 0 | 0 |
| Jordana_et_al | 2 | 1 | 0 |
| Melenhorst_et_al | 2 | 0 | 0 |
| Bai_et_al | 1 | 0 | 1 |
| Li_X_et_al | 1 | 0 | 0 |

Collapsed to responder (R = CR/PR) vs NR: **9 studies contribute labeled patients; 5 carry
BOTH R and NR.** Assessment:

- **Not cleanly confounded, but partially structured.** The two dominant labeled studies —
  Haradvala (n=31) and Deng (n=23) — each contain both R and NR, so leave-patient-out CV is
  genuinely informative and not forced to learn batch. Deng even skews NR-heavy (13 NR / 10 R),
  the opposite of the small studies, which breaks a naive "study ⇒ outcome" shortcut.
- **But** four small studies are single-class responders (Sheih, Melenhorst, Li_X, Jordana =
  all CR/PR), so a model could exploit study identity there. And response is **disease-confounded**
  (77/87 labeled patients are NHL).

**Mandatory controls for Brief 04 (pre-register):** (1) **leave-patient-out CV** at minimum,
**leave-study-out** as the honest generalization test; (2) report AUROC/AUPRC **per study** and
pooled, not just pooled; (3) run a **within-NHL primary** (77 patients) so disease is held
roughly constant; (4) baselines must include **study/disease dummies, CD8 fraction, and effect
magnitude** — an axis only "wins" if it beats those under leave-study-out. (5) Consider
`Time_Point` (pre-infusion product vs in-vivo) — decide which timepoint's cells carry the
response signal before scoring.

## 6. IEC gene-set coverage (Brief 04 feasibility)

All IEC axes are **100% covered** in `var_names`:

| axis | genes present / total |
|---|---|
| A_persist — memory/stem | 9/9 |
| A_persist — migration | 8/8 |
| A_persist — synapse assembly | 18/18 |
| A_kill — cytotoxic | 7/7 |
| A_resist — exhaustion (inverted) | 9/9 |
| CD8-identity baseline | 4/4 (CD8A, CD8B, CD4, IL7R) |

## 7. Verdict

**EVALUABLE.** The atlas carries clean, patient-level, patient-mappable CAR-T **response**
labels (87 patients, 60 R / 27 NR by Max_Response; 264k labeled cells) — a real, adequately
powered clinical endpoint, and a large step up from the underpowered prior clinical attempt
(D4, n=9/65) noted in `reports/immune_engagement_capacity.md` §3. IEC gene coverage is complete
and CD4/CD8 identity is derivable. Response is **partially confounded** with study and disease
(NHL-dominated), so Brief 04 must use leave-patient-out (ideally leave-study-out) CV, report
per-study, run a within-NHL primary, and beat study/disease/CD8/magnitude baselines. **No labels
were invented or imputed** — the missing 32 patients are healthy/mouse controls and stay missing.

### Deliverables
- `atlas_structure_report.md` (this file)
- `atlas_patient_response.csv` — one row per patient (id, study, disease, n_cells, responses, tox)
- `gate_result.json` — all gate numbers (counts, cross-tabs, consistency, IEC coverage)
- `atlas_structure_raw.json` — full 56-column obs schema
- `inspect_atlas.py`, `gate.py` — reproducible
