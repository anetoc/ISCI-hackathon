# TSC Prediction P3 — Functional Synapse / Killing Dataset Scout

**Question (P3):** Does a *transcriptional* signature (the ISCI-derived Tissue Synapse
Capacity score) predict **functional** immune-synapse / cytotoxic quality — serial-killing
rate, synapse-formation efficiency, MTOC polarization — better than raw effect magnitude?

**Scope of this scout:** metadata + literature only. NO full datasets downloaded.
Sources queried: GEO (NCBI E-utilities), ArrayExpress/BioStudies, PubMed/PMC, PRIDE/ProteomeXchange.

> **Connector status note:** the PRIDE/ProteomeXchange search API returned upstream `403 Forbidden`
> on every route (`pride_search_projects`, `pride_find_projects_for_protein`) throughout this scout —
> an upstream outage, not a sandbox block. Phosphoproteomics candidates below were therefore
> identified via PubMed; their PXD accessions must be confirmed from the papers directly.

---

## Bottom line

The **strong form of P3 - a *perturbation-anchored* transcriptional score predicting a *functional*
synapse/killing readout - is NOT testable now with openly reachable public data.** No public
Perturb-seq / CRISPR screen pairs single-cell transcriptomes with a per-cell killing or
synapse-imaging phenotype. The two datasets that genuinely pair transcriptome + functional
killing readout are either **dbGaP-gated** (clinical CAR-T) or use a **non-perturbational, gamma-delta-TEG /
organoid** design.

A **weaker, correlational surrogate of P3 IS testable in <=1 week, locally**: BEHAV3D
(**GSE172325**) links live-imaging killing *behavior* to scRNA-seq of the same engineered T cells,
so you can ask "does a killing-behavior transcriptional signature exist and does the TSC score
track it?" - a correlational, not causal/perturbational, test. Treat it as the honest interim P3
proxy; the decisive perturbation->function test remains a roadmap / wet-lab collaboration item.

---

## Candidate table

| # | Source / accession | Functional readout | Linkable to signature? | Size | Feasibility |
|---|---|---|---|---|---|
| 1 | **dbGaP phs002966.v1.p1** - Nature Cancer 2024 (PMID 38750245, DOI 10.1038/s43018-024-00768-3) | **TIMING nanowell live-imaging serial-killing + subcellular profiling**, same cells | **YES** - scRNA-seq on the *same* CAR-T cells; "CD8-fit" multifunctional signature already derived | Clinical LBCL axi-cel infusion products (cohort size not verified in this scout) | **GATED-institutional** (dbGaP controlled; DAC approval = weeks-months, not 1 wk) |
| 2 | **GSE172325** - BEHAV3D, Nat Biotechnol 2022 (PMID 35879361, DOI 10.1038/s41587-022-01397-w) | Live-imaging **behavioral classification** (killing/engagement behaviors) of engineered T cells vs breast-cancer organoids | **YES (correlational)** - behavior signatures mapped to scRNA-seq; count matrices on GEO FTP | 25 samples; scRNA + bulk | **LOCAL** - open supplementary matrices. *Caveat: gamma-delta-TCR TEGs, not CAR/alpha-beta; behavior->transcriptome at signature/cluster level, not perturbational* |
| 3 | **GSE207143** - CLASH, "Massively parallel engineering of persistent CAR-Ts" | **Functional persistence** (guide enrichment/dropout in vitro + in vivo) - a killing-adjacent selection phenotype | Partial - perturbation <-> persistence, NOT synapse/killing imaging | 86 samples (guide-count libraries) | **LOCAL** - but wrong readout for synapse P3 (persistence != synapse quality) |
| 4 | **GSE214231** - speedingCARs, PMID 36323661 | 180 CAR signaling-domain variants + scRNA-seq after 36 h co-culture (activation/effector state) | Partial - CAR-variant <-> transcriptional state; functional cytotoxicity measured separately | 14 samples, 3 donors | **LOCAL** - variant screen, effector-state proxy not per-cell killing |
| 5 | **CD2 phosphoproteomics** - Sci Signal 2020 (PMID 32398348, DOI 10.1126/scisignal.aaz1965) | **Phosphoproteome of CD2 costimulation controlling lytic-granule / MTOC polarization** in human CD8 CTL - protein-level synapse-signaling readout | Protein-level synapse proxy (not transcriptome; would bridge to STRING/CCI axis) | Human CD8 CTL phosphoproteome | **NOT-REACHABLE now** - PRIDE 403; PXD accession must be read from paper |
| 6 | **GSE201970** - "CD58 loss confers functional impairment of CAR T" (PMID 35728062) | CAR-T functional impairment (bulk, WT vs CD58-KO co-culture) | Coarse - genotype <-> bulk expression, no per-cell killing | 4 samples | **LOCAL** - too coarse for P3 (n=4, bulk) |
| 7 | **GSE233484** - "Tumor cells impair immunological synapse formation via CNS metabolite" (PMID 38821061) | Synapse-formation impairment; resistant/sensitive tumor RNA-seq | Coarse - tumor-side transcriptome, not T-cell synapse per cell | 9 samples | **LOCAL** - tumor-centric, not the T-cell synapse axis |

**Also screened, not synapse-functional:** GSE289212 / GSE159960-family NK cytotoxicity series,
GSE180834 / GSE192827 tumor-side CRISPR immune-evasion screens, GSE215086 (BATF-KO CAR-T),
GSE225184 (CAR-T metabolism) - all have functional framing but no paired per-cell
synapse/killing-imaging readout linkable to a perturbational transcriptional score.

---

## Detail on the two datasets that matter

### #1 - dbGaP phs002966 (the gold standard, gated)
The Nature Cancer 2024 study is the closest thing in existence to the P3 design: it integrates
**timelapse imaging microscopy in nanowell grids (TIMING serial-killing)**, subcellular profiling,
and **single-cell RNA-seq on the same infusion-product CAR-T cells** from large-B-cell-lymphoma
patients (exact cohort size not confirmed in this metadata-only scout), and derives a
multifunctional "CD8-fit" signature that predicts complete response.
That is exactly "transcriptional signature <-> functional killing quality." **But** gene expression
+ TCR sequences are deposited under **dbGaP controlled access (phs002966.v1.p1)** - a Data Access
Committee application is required (typically weeks to months). **Not 1-week feasible**; flag as the
target dataset for a formal dbGaP request or a collaboration with the originating group.

### #2 - GSE172325 / BEHAV3D (the feasible interim proxy, LOCAL)
BEHAV3D captures live-imaging **behavioral phenotypes** (T-cell engagement/killing dynamics
against patient-derived breast-cancer organoids) and links them to **scRNA-seq of the same TEGs**
at different targeting stages. Supplementary count matrices + metadata are open on GEO FTP
(`GSE172325_*_counts.csv.gz`, `*_metadata.csv.gz`, pseudotime tables). This lets you test the
**correlational** surrogate: derive the TSC transcriptional score on these cells and ask whether it
tracks the behavioral killing classes - and, critically, whether it beats effect-magnitude/activation
signatures at that. **Caveats that keep this honest:** (a) the effector is a gamma-delta-V9V2-TCR-engineered
T cell (TEG), not a CAR/alpha-beta T cell - cross-modality generalization claim; (b) behavior is linked to
transcriptome at the signature/cluster level, not as a within-cell causal perturbation, so it tests
*association* (does a killing-behavior signature exist and does TSC recover it), not the
perturbational controllership claim.

---

## Honest verdict on P3

- **Decisive form (perturbation -> functional synapse quality): NOT testable now** with open public
  data. No public Perturb-seq/CRISPR screen carries a paired per-cell killing or synapse-imaging
  readout. This is a genuine **roadmap / wet-lab collaboration** item - exactly the gap the scout
  was expected to surface.
- **Correlational surrogate (transcriptional signature <-> killing behavior): testable in <=1 week,
  LOCAL**, via BEHAV3D **GSE172325**. Frame explicitly as a *generalization/association* check, not
  the causal test, and note the gamma-delta-TEG -> CAR-T transfer.
- **Clinical gold standard exists but is gated**: dbGaP **phs002966** (Nature Cancer 2024) pairs
  TIMING serial-killing + scRNA-seq in clinical CAR-T. Worth a formal dbGaP DAC request as a
  post-hackathon validation, not a D0-D4 deliverable.
- **Protein-level synapse proxy** (phosphoproteomics of MTOC/lytic-granule polarization, e.g. the
  CD2 Sci Signal 2020 study) could bridge TSC to a physical synapse-signaling axis via STRING/CCI,
  but the PRIDE connector is down (403) and the PXD accession must be recovered from the paper
  before feasibility can be judged.

**Recommended action for the submission:** use GSE172325 as an openly reproducible interim P3 proxy
(clearly labelled correlational), and cite phs002966 as the decisive dataset requiring controlled
access - turning the "we can't test P3 yet" limitation into a concrete, credible validation roadmap.

---
*Attribution: candidate discovery used PubMed (NCBI) records and GEO metadata via NCBI E-utilities.
Key papers: PMID 38750245 (DOI 10.1038/s43018-024-00768-3), PMID 35879361 (DOI 10.1038/s41587-022-01397-w),
PMID 32398348 (DOI 10.1126/scisignal.aaz1965), PMID 36323661.*
