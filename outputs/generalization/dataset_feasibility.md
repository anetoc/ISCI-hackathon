# CCI Generalization — External Perturb-seq Dataset Feasibility

**Scope of this document.** Metadata-only scouting for the Conditional Controllability Invariant (CCI) generalization test, per `generalization_spec.md`. No full matrices were downloaded. Sizes for harmonized files are the **exact byte sizes** of the scPerturb v1.4 release (Zenodo record `13350497`, `sanderlab/scPerturb`); GEO structure was read via the omics-archives connector; primary-source sizes (Replogle Figshare+) are cited where scPerturb is the practical download.

The intake gate has four hard requirements. Two are cheap (an effect matrix + ≥2 replicates — nearly every Perturb-seq has these). **Two are the real filters:** a credible **state axis** (signed gene set the system actually moves along) and a credible **regulator label set** (known controllers = the AUPRC positives). The verdict for each dataset is driven almost entirely by whether that axis+label pair exists *for that specific cell system* — not by data size.

Verdict legend (from the spec):
- **LOCAL-FEASIBLE** — admissible, fits 24 GB after pseudobulk, and a credible axis+label pair exists → run the CCI protocol locally.
- **GATED-institutional** — admissible with a valid axis+label pair, but cell-level h5ad ≫ 20 GB and no pseudobulk/DE form is published → defer to HPC/Modal.
- **NOT-EVALUABLE** — admissible data but **no credible axis+label pair** (or gated purely on compute with no axis anyway). No verdict is forced; the blocker is stated. This is the honest outcome for most non-immune systems.

---

## Tier A — NEAR-transfer (immune Perturb-seq)

These share cell type (T cell / immune) with Marson, so the **axis and label sets transfer directly**: reuse the T-cell state axes (memory / effector / exhaustion / Treg) and the curated immune-regulator set already intersected with measured genes in the Marson track.

| Dataset | Accession / source | Size (harmonized h5ad) | System | Perturbation | Replicate structure | State axis available? | Regulator labels? | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Schmidt–Marson 2022 (CRISPRa Perturb-seq)** | GEO **GSE190604** (parent GSE174255; IL-2/IFN-γ sort = GSE190846); *Science* 2022 | Not in scPerturb; cell-level via GEO supp (est. 2–5 GB raw → pseudobulk ≪1 GB) | Primary human CD4+ T cells, TCR-stimulated | Pooled **CRISPRa** (gene activation), ~70 gene panel | Guide-level; 2 donors, IL-2/IFN-γ hi/lo sorted bins | **YES** — effector/cytokine (IL2, IFNG program) + activation axis; same T-cell axes as Marson | **YES** — Marson immune-regulator set; overlaps Marson gene panel | **LOCAL-FEASIBLE** ✅ (best near candidate — matched cell type, opposite perturbation direction = strongest CCI transfer test) |
| **Shifrut–Marson 2018** | scPerturb `ShifrutMarson2018.h5ad` | **871 MB** | Primary human CD8+ T cells | CRISPR-KO, arrayed/pooled | guide replicates | YES — T-cell activation/proliferation | YES — same immune set | LOCAL-FEASIBLE ✅ (backup near; KO in CD8 complements CD4 KD) |
| **Frangieh 2021 (Perturb-CITE-seq)** | scPerturb `FrangiehIzar2021_RNA.h5ad` (+ `_protein` 25 MB) | **1459 MB** | Melanoma + **autologous T-cell co-culture** (immune-adjacent) | CRISPR-KO, immune-evasion panel | 3 conditions (control / IFN-γ / co-culture), guide reps | PARTIAL — IFN-γ response / immune-evasion program exists, but it is a *tumor-cell* axis, not a T-state axis | PARTIAL — validated immune-evasion regulators (their own hits) usable as labels | LOCAL-FEASIBLE ⚠️ (evaluable as an immune-response axis on tumor cells; weaker "T-state" claim — use as secondary) |
| **Papalexi–Satija 2021 (ECCITE-seq)** | scPerturb `PapalexiSatija2021_eccite_RNA.h5ad` (+protein 1 MB) | **147 MB** | THP-1 (myeloid leukemia line) | CRISPR-KO, IFN-γ/PD-L1 regulators | guide replicates | PARTIAL — IFN-γ / PD-L1 response axis (not a lymphocyte state axis) | PARTIAL — known IFN-γ pathway regulators as labels | LOCAL-FEASIBLE ⚠️ (smallest file; myeloid not T — axis is a signaling response, not a differentiation state) |

## Tier B — FAR-transfer (non-immune genome-scale)

Here the axis+label pair is the binding constraint. K562/RPE1 have **no differentiation-state axis** analogous to memory/effector; the closest system-appropriate axes are proliferation / stress / lineage programs, and the label set must come from an orthogonal source (essential genes, known TFs, or the dataset's own validated regulators). The spec explicitly anticipates most of these are **NOT-EVALUABLE**, which is itself an informative boundary on the property.

| Dataset | Accession / source | Size (harmonized h5ad) | System | Perturbation | Replicate structure | State axis available? | Regulator labels? | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Replogle 2022 — RPE1 essential** | scPerturb `ReplogleWeissman2022_rpe1.h5ad`; primary Figshare+ (Weissman lab), *Cell* 2022 | **1237 MB** | RPE1 (retinal epithelial, near-diploid) | genome-scale **CRISPRi**, ~2k essential genes | strong: many cells/guide, 2 guides/gene | PARTIAL — no differentiation axis, but robust **proliferation / integrated-stress-response** programs; well-characterized | **YES (orthogonal)** — CORUM complexes / known TF & essential-gene sets; Replogle's own clustered regulators | **LOCAL-FEASIBLE** ✅ (best far candidate — cleanest axis+label pair of the non-immune set, moderate size, pseudobulk trivial) |
| **Replogle 2022 — K562 essential** | scPerturb `ReplogleWeissman2022_K562_essential.h5ad` | **1547 MB** | K562 (CML erythroleukemia) | CRISPRi, ~2k essential genes | strong (as above) | PARTIAL — proliferation/stress; K562 also has a weak **erythroid** program (hematologic relevance) | YES (orthogonal, as above) | LOCAL-FEASIBLE ✅ (backup far; hematologic lineage is a bonus tie to the clinical theme) |
| **Replogle 2022 — K562 genome-wide** | scPerturb `ReplogleWeissman2022_K562_gwps.h5ad` | **8806 MB** | K562 | genome-scale CRISPRi, ~9.9k genes | strong | PARTIAL (as K562 essential) | YES (orthogonal) | GATED-institutional ⚠️ (8.8 GB cell-level; loads on 24 GB but pseudobulk pass is tight — defer to HPC, or just use the essential subset which answers the same question) |
| **Norman–Weissman 2019** | GEO **GSE133344**; scPerturb `NormanWeissman2019_filtered.h5ad` | **699 MB** | K562 | CRISPRa, single + **combinatorial** pairs | guide reps | PARTIAL — differentiation-like programs (erythroid/megakaryocyte) reported for some TFs | PARTIAL — the activating TFs are candidate labels but not an independent controller set | NOT-EVALUABLE ⚠️→ borderline (usable only if we accept their TF panel as labels; report as exploratory, not a clean far PASS/FAIL) |
| Joung–Zhang 2023 (TF atlas) | scPerturb `JoungZhang2023_atlas.h5ad` | 5804 MB | hESC | genome-scale TF ORF overexpression | — | axis = lineage, but hundreds of fates, no single signed axis | labels ill-defined (every perturbation is a TF) | NOT-EVALUABLE (no single credible axis+label pair) |
| Srivatsan–Trapnell 2020 (sci-Plex) | scPerturb `SrivatsanTrapnell2020_sciplex3.h5ad` | 2527 MB | A549/K562/MCF7 | small-molecule (drugs), not genetic | dose reps | drug-response, not a controller-gene axis | **NO** — perturbations are compounds, not genes → no regulator labels | NOT-EVALUABLE (chemical perturbation; incompatible with a gene-controller label set) |

---

## Ranked recommendation — the 1 near + 1 far to actually run

### NEAR (run first): **Schmidt–Marson 2022 CRISPRa Perturb-seq — GSE190604**
The strongest possible generalization test short of a new tissue: **same cell type (primary human CD4+ T cells), same lab-quality data, but the opposite perturbation modality (CRISPRa activation vs Marson's KO/KD).** If CCI holds when the perturbation direction flips, the invariant is a property of the *state geometry*, not of a particular knockdown signature — exactly the claim we want to defend. The axis (IL-2/IFN-γ effector program) and regulator labels transfer directly from the Marson track, and the IL-2/IFN-γ hi/lo sorted bins (GSE190846) give a built-in functional readout. Cell-level data is modest; pseudobulk DE is trivially local. **If the connector-listed GEO supp turns out to be raw counts only, budget one preprocessing pass (align to Marson gene space → pseudobulk per guide → DE) before the CCI protocol.**

Fallback if Schmidt preprocessing stalls: **Shifrut–Marson 2018** (871 MB harmonized, ready-to-pseudobulk, CD8 KO) — same immune axes, no custom preprocessing.

### FAR (run second): **Replogle 2022 RPE1 essential — `ReplogleWeissman2022_rpe1.h5ad` (1237 MB)**
Of every non-immune option this is the only one with a genuinely *clean* axis+label pair: a well-characterized proliferation/integrated-stress-response axis and an orthogonal, non-circular label set (CORUM complexes / known essential regulators, independent of the axis definition). 1.2 GB loads and pseudobulks comfortably on 24 GB. This is the honest far test: **PASS → the invariant reaches beyond immunity; FAIL → we've mapped a real boundary (immune-scoped property).** Either outcome is publishable and neither is spun.

Fallback: **K562 essential** (1547 MB) — same design, adds a weak erythroid/hematologic lineage angle that ties to the clinical theme; use the **genome-wide K562 (8.8 GB)** only on HPC and only if a reviewer demands genome-scale coverage — the essential subset answers the invariance question at a fraction of the cost.

### Explicit honesty note (for the writeup)
Most FAR non-immune systems are **NOT-EVALUABLE** by construction — Joung (no single axis), sci-Plex (chemical, no gene labels), Norman (labels not independent of the axis). We are *not* forcing verdicts on these. The far test rests on Replogle because it is the one non-immune dataset where a controller-vs-associate distinction can be defined without circularity. Reporting the others as not-evaluable is part of the result, not a failure to find data.

---

### Provenance
- Harmonized h5ad sizes: scPerturb v1.4, Zenodo `10.5281/zenodo.13350497` (file byte sizes read from Zenodo API).
- GEO structure (Schmidt GSE190604/GSE190846/GSE174255, Norman GSE133344): NCBI GEO via omics-archives connector.
- Replogle primary distribution: Weissman lab Figshare+ (`plus.figshare.com`), *Cell* 2022; scPerturb mirror used for local download.
- No expression matrices were downloaded for this scouting pass.
