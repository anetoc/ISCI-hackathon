# Brief 03 — Download & validate the Functional CAR-T atlas (gate before the clinical test)

**Goal:** get the Functional CAR-T atlas onto the machine and VERIFY it has what Brief 04
(the clinical prediction test) needs — patient-level response labels — BEFORE any heavy
analysis. This is a feasibility + label gate, deliberately separate from the test itself so we
never build a predictor on labels that don't exist.

## Data source — RESOLVE AND VERIFY FIRST (do not trust the strings below)
The "Functional CAR-T atlas" (ML4BM-Lab / Univ Navarra) is the target, but the exact
identifiers below are **unverified leads to confirm yourself**, not established fact:
- Candidate Zenodo record ~19066393 / concept DOI ~10.5281/zenodo.17213452; candidate
  preprint bioRxiv ~2025.10.11.681788; candidate GitHub ML4BM-Lab/Functional-cart-atlas.
- **Step 0a — resolve the real source:** search Zenodo/GitHub for "Functional CAR-T atlas
  ML4BM-Lab", confirm the actual record ID, DOI, and file list from the live page, and
  record what you found. If these candidate IDs are wrong or dead, find the correct ones and
  report the discrepancy — do not proceed on an unconfirmed link.
- Expected content to verify against the real download (all UNCONFIRMED): ~>1M cells,
  ~414k CD3+CAR+ after QC, phenotypes, a scVI model, clinical-response + ICANS metadata.
  **Report what the files actually contain; trust nothing in this brief as a number.**

## Environment
pip venv from `envs/requirements_machine.txt` + scanpy/anndata. Download **server-side** with
`wget`/`requests` directly on the machine (files are public; do not upload from a laptop).
Cache under `/mnt/dados2/abel-tsc/data_public/cart/`.

## Protocol (gate, not analysis)
1. **Download** the main atlas AnnData (the CD3+CAR+ / integrated object). Log file names + sizes.
2. **Structure report:** shape (cells × genes), `obs` columns, `obsm` keys (X_scVI/X_umap?),
   layers, and n_studies. Print `obs` dtypes and the unique values (or count) of every column
   that could carry: patient ID, study ID, response label, ICANS grade, cell phenotype, CD4/CD8.
3. **THE GATE — patient-level response labels:**
   - Is there a per-cell or per-patient **response** column (CR/PR/NR, responder/non-responder,
     or similar)? Report its exact name, its categories, and the counts.
   - How many **unique patients** have a non-missing response label? Cross-tab patients × response.
   - Is response confounded with **study/batch**? (e.g. does one study contribute all responders?)
     Report a patient-level study × response cross-tab — this decides whether leave-patient-out CV
     is even meaningful or whether it will just learn batch.
4. **Phenotype/axis feasibility:** confirm the genes needed for the IEC axes (persist/kill/resist
   sets) are present in `var_names`; report coverage per axis.

## Deliverables (commit)
- `outputs/cart_atlas/atlas_structure_report.md` — provenance (verified numbers), full obs schema,
  the response-label gate result (column, categories, n_patients, patients×response, study×response
  confound), IEC gene coverage, and an explicit **EVALUABLE / NOT-EVALUABLE** verdict for Brief 04.
- `outputs/cart_atlas/atlas_patient_response.csv` — patient_id, study, response, ICANS, n_cells
  (one row per patient) IF labels exist.
- Commit: `CAR-T atlas: structure + patient-response label gate (EVALUABLE|NOT-EVALUABLE)`.

## STOP condition
If there is **no patient-level response label** mappable to cells, STOP and report
NOT-EVALUABLE — do NOT proceed to a prediction test, and do NOT invent or impute response.
Hand back to Claude Science to pick an alternative labeled cohort.
