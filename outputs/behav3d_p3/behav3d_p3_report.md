# BEHAV3D (GSE172325) — correlational proxy for the TSC P3 test

**Verdict: NULL / FAIL** (pre-registered primary), with a fully **NOT-EVALUABLE** replication.
The transcriptional TSC score does **not** separate functional killer (super-engaged) from
non-killer (never-engaged) TEGs; it is in fact *inversely* associated with engagement and
loses to every baseline. This is an honest negative — and it is **consistent** with the locked
TSC finding that serial killing loads ≈0 on the TSC latent factor (`tissue_synapse_capacity.md`
§3a: "TSC as measured here is a reach-and-hold-a-synapse axis more than a kill axis").

---

## 1. Dataset provenance (verified)

- **GSE172325** = BEHAV3D. GEO `Series_title`: *"Behavioral-transcriptomic landscape of
  engineered T cells targeting human cancer organoids"*; `Series_pubmed_id = 35879361`
  (Nat Biotechnol 2022, DOI 10.1038/s41587-022-01397-w). Confirmed against GEO.
- Solid-tumor breast-cancer organoids (PDOs) + engineered Vγ9/Vδ2-TCR T cells (**TEGs**),
  **not** hematologic CAR-T. Live-imaging behavioral reference is a separate deposit
  (BioImage Archive S-BIAD448); we test only the **transcriptome-level** signature here.
- Supplementary files (GEO FTP, sizes verified):

  | File | Size |
  |---|---|
  | `GSE172325_10T_vs_13T_exposed_TEGs_counts.csv.gz` | 5.99 MB |
  | `GSE172325_10T_vs_13T_exposed_TEGs_metadata.csv.gz` | 6.3 KB |
  | `GSE172325_Non_exposed_TEGs_counts.csv.gz` | 14.96 MB |
  | `GSE172325_Non_exposed_TEGs_metadata.csv.gz` | 41 KB |
  | `GSE172325_Pseudotime_TEGs_counts.csv.gz` | 14.96 MB |
  | `GSE172325_Pseudotime_TEGs_metadata.csv.gz` | 10 KB |
  | `GSE172325_KAR4630_KAR4631_ndata.txt.gz` | 2.85 MB (bulk organoid RNA) |
  | `GSE172325_KAR4630_KAR4631_readCounts_raw.txt.gz` | 1.30 MB (bulk organoid RNA) |

## 2. The functional label (authors', not invented)

Per-cell engagement/behavior class in metadata column `exp_condition`:
`super-engaged` (the paper's serial-killing "super-engager" population) /
`medium-exposed` (intermediate) / `never-engaged`. This is the authors' engagement-sort
label — a **functional-behavior proxy**, not the imaging-derived behavioral cluster itself
(that lives in S-BIAD448). Framed as a signature-level generalization/association check, as
the brief requires.

**Pre-registered contrast (fixed before any metric):** positive = `super-engaged`,
negative = `never-engaged`, `medium-exposed` dropped from the primary (kept only for the
ordering sanity check).

## 3. TSC score & baselines

Normalize→log1p, then `scanpy.tl.score_genes` on the same Marson L1–L4 modules
(`config/axes.yaml`, `outputs/movability_gate.json`) + a GO/Reactome synapse set (report §4):

- **L1 durable state** = z(memory/stem) − z(exhaustion)
- **L2 tissue access** = migration (CCR7, SELL, S1PR1, ITGAL, RHOA, WASF2, CORO1A, CXCR3)
- **L3 synapse assembly** = immune-synapse/cytoskeleton (LCK, LAT, ZAP70, PLCG1, VAV1, LCP2,
  ITK, FYN, WAS, WASF2, ARP2/3, CORO1A, RHOA, CDC42, RAC2, TLN1, PXN, MYH9, CD2, CD58)
- **L4 serial killing** = GZMB, PRF1, NKG7, GNLY, IFNG, FASLG, GZMA
- **TSC** = mean of z-scored L1–L4 (report §2 construction). Gene-set coverage in
  `behav3d_p3_results.json`.

**Competing baselines:** (1) **activation** module (IL2, IL2RA, CD69, TNF, IRF4, NR4A1, IFNG,
TBX21, EOMES, STAT1, IRF1); (2) **CD8-identity** = z(CD8A,CD8B,GZMB,PRF1,NKG7) − z(CD4,IL7R);
(3) **total counts** (magnitude). PASS required beating activation *and* CD8-identity.

## 4. Confounder guard (reported before the test)

The exposed metadata has **no** `Cell_type` column, so the CD8/CD4 cross-tab uses an
**expression-derived** CD8 call (CD8A or CD8B > 0):

| engagement | CD8+ | CD8− | CD8+ fraction |
|---|---|---|---|
| super-engaged | 745 | 189 | **0.798** |
| never-engaged | 654 | 381 | **0.632** |
| medium-exposed | 322 | 153 | 0.674 |

Ratio super/never = **1.26×** — below the 2× "heavy confound" threshold. Per the guard rule
the primary test is still run in the **CD8+ stratum** as well; the verdict is unchanged
(TSC AUROC 0.373 there), so the failure is **not** a CD8/CD4 artifact — TSC fails to
separate killer vs non-killer *within* the CD8 compartment too.

**Authors'-label corroboration (Pseudotime metadata).** The exposed set has no `Cell_type`
column, but the Pseudotime metadata *does* carry the authors' own CD8/CD4 call (CD8 /
CD4 IL17− / CD4 IL17+). Its counts matrix is unusable (§6), but the cross-tab is a
metadata-only operation and is fully evaluable — a real-label check on the same confounder:

| engagement | CD8 | CD4 | CD8 fraction |
|---|---|---|---|
| super-engaged | 675 | 336 | **0.668** |
| medium-exposed | 409 | 357 | 0.534 |
| never-engaged | 341 | 423 | **0.446** |

Ratio super/never = **1.50×** — again below the 2× threshold, and consistent with the
expression-derived 1.26× above. Engagement is *modestly* CD8-enriched in both datasets but
not heavily confounded, so the primary test is not merely recapitulating CD8-ness; and TSC
loses to the CD8-identity baseline anyway (§5), so the honest reading holds either way.

## 5. Result — primary test (exposed, super vs never, n = 1969)

| score | AUROC | AUPRC |
|---|---|---|
| **TSC** | **0.350** | **0.374** |
| activation | 0.991 | 0.989 |
| cd8_identity | 0.848 | 0.829 |
| total_counts | 0.727 | 0.696 |

Bootstrap 95% CI on the difference (TSC − baseline), 2000 resamples — **all negative, all
exclude 0**:

| vs baseline | ΔAUROC [95% CI] | ΔAUPRC [95% CI] |
|---|---|---|
| activation | −0.641 [−0.666, −0.616] | −0.614 [−0.636, −0.591] |
| cd8_identity | −0.498 [−0.527, −0.470] | −0.454 [−0.479, −0.430] |
| total_counts | −0.377 [−0.411, −0.345] | −0.322 [−0.352, −0.293] |

Orthogonality: Spearman(TSC, activation) = −0.273, (TSC, cd8_identity) = −0.115,
(TSC, total_counts) = −0.115 — TSC is weakly *anti*-correlated with magnitude/activation.

**Why TSC fails — per-loading AUROC (super = positive):**

| loading | AUROC |
|---|---|
| L4 killing | **0.947** |
| L1 durable state | 0.303 |
| L3 synapse assembly | 0.298 |
| L2 tissue access (migration) | 0.154 |

The **killing loading alone separates almost perfectly** (0.947 — super-engagers are cytotoxic
effectors, as expected). But the three other loadings run the *opposite* way: L1/L2/L3 are
built from memory/stem, egress/chemotaxis (CCR7, SELL, S1PR1) and TCR-machinery markers that
are **down-regulated in activated effector cells**. Averaged equally into TSC, they overwhelm
L4 and pull the composite below chance. Activation and total-counts separate well because the
super/never sort is essentially an **activation-state axis** (activation mean by class:
medium −0.95 < never −0.57 < super +1.11).

## 6. Replication — NOT-EVALUABLE (data-availability limitation, not a null)

The pre-registered replication (`Pseudotime_TEGs`, n=3296) **cannot be run**: there is no valid
count matrix on GEO for its engagement metadata.

- `GSE172325_Pseudotime_TEGs_counts.csv.gz` shares **7664/7664** barcodes with the Non_exposed
  matrix (it *is* the non-exposed counts) → only 254 spurious matches to the pseudotime metadata.
- The 1516 pseudotime-metadata barcodes that appear in the **exposed** counts are **well-ID
  collisions across independent plate layouts, not the same cells**: the same barcode carries
  *contradictory* engagement labels between the two files (e.g. 200 cells labelled
  `super-engaged` in the exposed metadata are `never-engaged` in the pseudotime metadata; full
  off-diagonal cross-tab in `behav3d_p3_results.json`).

Joining on these barcodes would attach wrong expression to cells, so per CLAUDE.md hard rule 1
we refuse and report **NOT-EVALUABLE** rather than fabricate a replication.

## 7. Honest verdict

**NULL / FAIL** for the pre-registered proxy. The composite TSC score does not beat any
baseline and is inversely related to functional engagement/killing; it fails to beat the
CD8-identity and activation baselines both overall and within the CD8+ stratum. The functional
killer phenotype in BEHAV3D is captured by **activation magnitude and cytotoxic-effector genes**,
not by the TSC "reach-and-hold-a-synapse" composite.

Crucially this is **not a contradiction** of the locked immune-scoped CCI/TSC result — it is the
functional echo of the already-documented structural finding that **serial killing loads ≈0 on
the TSC latent factor** (§3a). TSC, as constructed, is a reach/hold/persistence state axis; this
proxy shows it does not double as a killing-behavior predictor. A genuine P3 test of *whether
TSC controllers causally set killing capacity* still requires per-cell perturbation→killing data
(not present here).

### Scope caveats (as required)
- Solid-tumor organoid + TEG system, **not** hematologic CAR-T.
- Signature-level / correlational association, not the definitive per-cell perturbation→killing test.
- Label is the authors' engagement-sort proxy; imaging behavioral clusters are in S-BIAD448.

### Deliverables
- `behav3d_p3_report.md` (this file) · `behav3d_tsc_scores.csv` (2444 cells: TSC, L1–L4,
  3 baselines, CD8 call, label) · `behav3d_p3.png` (TSC distribution + ROC + PR + per-loading
  AUROC) · `behav3d_p3_results.json` (all numbers) · `behav3d_p3_analysis.py` (reproducible).
