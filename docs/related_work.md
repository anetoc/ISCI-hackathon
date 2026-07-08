# Related Work & Data Landscape — Immune-State Controllability

> Living document for the "Built with Claude: Life Sciences" hackathon (Researcher Track).
> Purpose: (1) ground the project in the literature, (2) map every dataset/tool we can use,
> (3) define the novelty gap, (4) list concrete questions for IDOR immunologists and Anthropic office hours.
> Language: English (repo/judge-facing). Author: Abel Costa (IDOR).

---

## 0. One-paragraph thesis

Genome-scale perturbation maps tell us which genes *change* T-cell state, but not which genes
*control* it in a therapeutically actionable, reproducible way. We define the **Immune-State
Controllability Index (ISCI)** to separate *controllers* from mere *associates*, validate it against
known regulators and independent screens, and — as the flagship step — project the resulting
controllability signature onto **real patient cohorts treated with CAR-T and bispecific/T-cell-engager
therapies** to test whether it stratifies response vs. resistance and nominates mechanism.

---

## 1. The clinical problem: resistance & sensitivity to T-cell–redirecting therapies

CAR-T and bispecific antibodies / T-cell engagers (TCE) have transformed treatment of hematologic
malignancies, yet **40–60% of patients fail to achieve durable responses**. Resistance falls into three
overlapping buckets (Sci Direct 2024 S1525001624003411; Cancers 2025 PMC12609497; Front Immunol 2026):

1. **Tumor-intrinsic escape** — antigen loss/downregulation (CD19, BCMA), splicing, trogocytosis,
   promoter methylation, genomic alterations (TP53, MYC). Explains a *minority* of relapses.
2. **T-cell dysfunction / lack of fitness** — exhaustion, tonic signaling, CAR-Treg conversion,
   loss of stem/memory potential. **This is the axis ISCI targets.**
3. **Immunosuppressive microenvironment** — Tregs, MDSCs, TGF-β, IL-10.

Crystal Mackall's framing (SITC 2021): resistance = *tumor escapes antigen* **or** *the T cell fails* —
two different problems solved in different ways. Our project attacks "the T cell fails".

**Key clinical observations linking T-cell STATE to outcome (our validation anchors):**
- Pre-manufacture / infusion-product **stem-like & central memory CD8** (CCR7+, LEF1+, TCF7+, CD45RA+CD27+)
  predict durable response; effector-memory/exhausted/senescent (CD57+) predict failure
  (Blood 2023 PMID 37875502; Blood 2019-122513; Front Immunol 2024.1378944; PMC12755975).
- **CAR-Tregs** (CD4+ HELIOS+ / FOXP3-like) among non-responders drive relapse
  (Haradhvala Nat Med 2022; Good et al.).
- Non-response to BCMA bispecifics ↔ failure of cytotoxic CD8 expansion + sustained Tregs + exhaustion
  (PD-1/TIM-3/LAG-3), **not** antigen loss (MajesTEC-1 correlatives Blood 2023-173550; ResisTec Blood 2025-918).
- **Endogenous TCF7 transcript and the FOXO1 regulon predict CAR-T / TIL response in patients**
  (Doan/Klebanoff/Chan et al., *FOXO1 is a master regulator of memory programming in CAR T cells*,
  Nature 2024, s41586-024-07300-8, Extended Data Fig. 10). ← direct proof that a *controllability-type
  signature* can be predictive; our ISCI generalizes this idea beyond single genes.

---

## 2. The biology: what controls T-cell state (ground-truth gene set)

Curated from functional-genomics and mechanistic studies. These become our **positive controls** to
benchmark ISCI (does it rank them high?).

**Memory / stemness / persistence (pro-response):**
- **FOXO1** — master regulator of memory programming in CAR-T; OE improves persistence; TCF1 alone
  insufficient (Nature 2024 s41586-024-07300-8; Thno v15p3345).
- **TCF7/TCF1, LEF1, KLF2, IL7R, SELL/CD62L, CCR7, BACH2, ID3, MYB** — stem/memory program.
- **TET2** loss → CCR7+CD45RO+ memory, enhanced persistence (clinical observation).

**Exhaustion / dysfunction (pro-resistance):**
- **TOX, TOX2** — install & epigenetically program exhaustion (Khan 2019; Seo; Nature 2024 review).
- **NR4A1/2/3, IRF4, BLIMP1/PRDM1, EOMES, ID2, BATF** — exhaustion / terminal differentiation.
- **NFIL3** — driver of CAR-T dysfunction (AACR 2026 C008).

**Chromatin / epigenetic controllers (Gladstone — perfect for our story):**
- **ARID1A / cBAF (SWI/SNF)** and **INO80** — depletion limits exhaustion chromatin, improves persistence
  (Belk et al., *Genome-wide CRISPR screens of T cell exhaustion...*, Cancer Cell 2022, PMC9949532).
- **AP-1 family** accessibility drives exhaustion loci (PDCD1, CTLA4, HAVCR2) (PNAS 2021 2104758118).

**Bidirectional / context-dependent hubs:**
- **BATF3** — OE counters exhaustion, promotes memory (orthogonal screens, bioRxiv 2023.05.01.538906).
- **IKZF1/IKAROS, ETS1, RBPJ–IRF1, FLI1** — CTL differentiation checkpoints
  (Zhang et al., *Single-cell CRISPR screens in vivo map T cell fate regulomes*, Nature 2023 s41586-023-06733-x).

---

## 3. Methods landscape: controllability & perturbation modeling

### 3a. Network-control / driver-gene (closest prior art — our conceptual baseline)
- **CEFCON** (Wang et al., Nat Commun 2023, s41467-023-44103-3) — infers cell-lineage GRN from scRNA-seq,
  applies **network control theory (MFVS + MDS)** + attention-based *influence score* to rank driver
  regulators of cell-fate decisions. **The method most similar to ours.** We use its control formalism
  for the D component and as a baseline. Open source.
- Structural controllability foundations: Liu, Slotine & Barabási (driver nodes / minimum input theory);
  linkage-logic / FVS (Mochizuki, Fiedler) — biological nets are ~80% driver-nodes, i.e. hard to control.
- Sample-specific network control benchmarks (PLoS Comput Biol 1008962): MDS/NCUA on CSN/SSN
  outperform DEG for personalized driver/target discovery.

### 3b. GRN inference from perturbation data
- **PSGRN** (Deng & Guan, Sci Adv aeb3376; **winner of GSK.ai CausalBench Challenge**) — self-training with
  synthetic gold standards. **CausalBench / BetterBoost** (arXiv 2308.15395) — GRNBoost + interventional
  p-values. **perturbVI** (SuSiE-PCA; mancusolab) — regulatory modules from Perturb-seq.
  **CID** (causal + scBERT; Fu & Cheng) — driver genes + directional KO prediction.
- **decoupler + CollecTRI**, **SCENIC/pySCENIC**, **GRNBoost2** — regulon/TF-activity inference.

### 3c. In-silico perturbation / foundation models (our A component + generalization)
- **CellOracle** (Kamimoto et al., Nature 2022, s41586-022-05688-9) — GRN + in-silico TF perturbation,
  simulates cell-state shift (RNA-velocity-like). Open source (morris-lab).
- **GEARS** (Roohani et al.) — GNN prediction of unseen perturbations. **scGPT / scFoundation** —
  transformer foundation models for perturbation.
- **Benchmark of in-silico perturbation** (bioRxiv 2024.12.20.629581) compares Linear, CellOracle, GEARS,
  scGen, CPA, CellOT, scGPT, scFoundation. Key lesson: **simple/linear baselines are strong** → we must
  beat them explicitly.
- **Arc Virtual Cell Atlas** (>600M cells), **Tahoe-100M** (100M cells, 1,100+ drug perturbations, 50 lines),
  **State** (Arc virtual-cell model; beats linear baselines; predicts perturbation-induced shifts),
  **Tahoe-x1** (3B-param scGPT-style). Usable as external in-silico layer / context transfer.

### 3d. Stability of cell states (our S component — the original twist)
- **Geometric coherence of single-cell CRISPR perturbations** (arXiv 2604.16642) — perturbations differ in
  *geometric stability*; high-magnitude/low-stability shifts are "hallucinatory intermediates" no real cell
  occupies. Directly relevant to CAR-T optimizing into an *exhaustion local minimum* / iPSC de-differentiation.
  **No existing driver-gene score incorporates target-state stability** → our novelty.
- Waddington-landscape / attractor framing (used by CEFCON) supports "a controller lands in a deep attractor".

### 3e. Perturbation analysis toolkits (engineering substrate)
- **pertpy** (Heumos et al., Nat Methods 2025, s41592-025-02909-7; scverse) — Mixscape, Augur,
  Distance/DistanceTest (Wasserstein, MMD, energy, MMD, classifier-proba...), >30 harmonized datasets.
- **scanpy / anndata / mudata / scvi-tools** (scverse) — core single-cell stack.
- **ProjecTILs** (Andreatta & Carmona, Nat Commun 2021; carmonalab) — reference T-cell state atlases
  (CD4/CD8 TIL), state classification, gene sets for exhaustion/cytotoxicity/memory.

---

## 4. Datasets — full inventory (4 layers)

### Layer 1 — Perturbation (causal; "who controls")
| Dataset | Scope | Access | Role |
|---|---|---|---|
| **Marson CD4+ genome-scale Perturb-seq** (Zhu, Dann et al., bioRxiv 2025.12.23.696273) | 12,748 genes, 4 donors, 3 conditions (Rest/Stim8h/Stim48h), 22M cells | CZI Virtual Cells; `s3://genome-scale-tcell-perturb-seq/marson2025_data/` (MIT); code `emdann/GWT_perturbseq_analysis_2025`; SRP643211/GSE314342 | **Primary.** Use `GWCD4i.DE_stats.h5ad` (33,983×10,282) + `pseudobulk_merged.h5ad` + suppl. tables |
| **Belk 2022 exhaustion CRISPR + in vivo Perturb-seq** (Cancer Cell, PMC9949532) | genome-wide; ARID1A/INO80 | GEO (paper) | Ortho validation (Gladstone tie-in) |
| **Schmidt 2022** CRISPRa/i in primary T (Science) | cytokine regulators (IL2/IFNG) | GEO | Ortho validation |
| **Frangieh 2021 Perturb-CITE-seq** (Nat Genet 00779-1) | 248 genes, RNA+20 proteins, 218k cells, IFNγ/co-culture | scPerturb Zenodo 10044268; pertpy | Ortho validation (immune evasion, +protein) |
| **Arc Atlas / Tahoe-100M / State / Tahoe-x1** | giga-scale perturbation | Arc portal; HuggingFace | In-silico / context transfer |

### Layer 2 — T-cell state references (define the axes)
- **ProjecTILs** CD4 & CD8 TIL atlases (figshare 24886611; carmonalab) + canonical gene sets.
- **CELLxGENE / Human Cell Atlas** for broader context.
- Axes to define: activation, Th1/Th2 (dataset ships signatures), exhaustion-like (TOX/PDCD1/LAG3/HAVCR2),
  memory/stem-like (TCF7/IL7R/CCR7/SELL), CD4-CTL/cytotoxicity (GZMB/PRF1/GNLY/NKG7), Treg (FOXP3/IL2RA), Tfh (CXCL13).

### Layer 3 — Multi-omics (mechanism beyond transcriptome; optional expansion)
- **Chromatin/epigenome:** ATAC-seq of exhaustion (Belk 2022; PNAS 2021 2104758118); AP-1/TOX regulons;
  methylation controllers **TET2/DNMT3A** (Clin Epigenetics 2026 s13148-026-02085-1). Multiome/footprinting.
- **Protein:** CITE-seq (Frangieh); CyTOF (Good et al.).
- **Spatial:** tumor/lymphoma niche spatial transcriptomics (enrichment of controllability programs in
  exhausted/cytotoxic niches) — only if IDOR or public data available.

### Layer 4 — PATIENT cohorts on T-redirecting therapy (translation; "who responds")
| Cohort | Disease / Therapy | Access | Signal |
|---|---|---|---|
| **Haradhvala 2022** (Nat Med) | LBCL / axi-cel + tisa-cel; 32 pts (IP + PBMC serial) | **GSE197268** (suppl. processado; raw dbGaP) | CAR-Treg in non-responders; memory-like CD8 in responders |
| **Deng 2020** (Nat Med) | LBCL / anti-CD19 products; 24 infusion products | **GSE151511**, **GSE150992** | Exhausted CD4/CD8 in PR/PD; LAG3/TIGIT/BATF/ID2 |
| **Good et al.** | LBCL / CD19 CAR-T | (paper) | CD4+HELIOS+ CAR-Treg predicts PD |
| **Premanufacture CD8** (Blood 2023, PMID 37875502) | DLBCL / CD19/CD20 CAR-T; 58 pts | GEO | Stem-like memory CD8 → durable response |
| Additional CAR-T | LBCL | GSE241783, GSE253872, GSE273170, GSE243325 | serial/product profiling |
| **MajesTEC-1 correlatives** | MM / teclistamab (BCMA×CD3) | (Blood abstracts) | exhaustion in non-responders |
| **ResisTec** (IFM) | MM / teclistamab; 100 pts longitudinal | NCT05945524 | immune remodeling vs MRD |
| **Functional CAR-T atlas** | 13 studies, >1M cells, response/ICANS | Zenodo [10.5281/zenodo.17213452](https://doi.org/10.5281/zenodo.17213452); ShinyCell app | Meta-atlas for phenotype enrichment |
| **Blinatumomab / CD3×CD19 TCE** | ALL, T-cell engager | Literature + trial correlatives | Bispecific arm of clinical story |
| **Deng 2020 + Li 2023** (tcellNF training) | LBCL CAR-T products | GEO (see tcellNF paper) | Joint optimization baseline for D4 |

**Use:** project the ISCI controllability signature into ≥1 CAR-T cohort (start GSE151511) → test
responder vs non-responder separation; compare to TCF7/FOXO1-regulon reference **and** tcellMIL/SCENIC baselines.

### Annotation / network / druggability
Open Targets, ChEMBL (druggability), STRING + decoupler/CollecTRI (regulons), human TF lists,
ClinicalTrials.gov (translational context). All available as Claude for Life Sciences connectors.

---

## 3f. Closest semantic neighbors (what already looks like our idea)

| Work | What it does | Overlap with ISCI | How we differ |
|---|---|---|---|
| **pert2state_model** (Dann/Marson; `emdann/pert2state_model`, MIT) | Fits **linear regression**: reconstruct an observational state signature as a linear combination of perturbation effect vectors; nominates regulators (Fig. 4 of the Marson preprint) | **Highest overlap** — same dataset, same question ("who moves cells toward a state?") | ISCI adds **reproducibility gating (R)**, **network control (D)**, **in-silico concordance (A)**, **state stability (S)**, explicit **controller vs associate** baselines, and **clinical bridge** to CAR-T/bispecific cohorts. pert2state is the baseline to beat, not ignore. |
| **CEFCON** (Nat Commun 2023) | GRN + MFVS/MDS driver regulators from scRNA-seq | Overlap on **D** (structural control) | CEFCON is observational scRNA-seq, not genome-scale Perturb-seq; no clinical translation; no stability term. |
| **tcellMIL** (`zinagoodlab/tcellMIL`; Blood 2025-5897; NeurIPS 2025) | Attention-MIL predicts **3-month CAR-T response** from infusion-product scRNA; SCENIC regulons; **in-silico TF perturbation** to nominate edits | Overlap on **clinical prediction** + in-silico perturbation | tcellMIL starts from **patient outcome labels**; ISCI starts from **causal perturbation map** then projects forward. Complementary — we can benchmark ISCI signature vs tcellMIL/SCENIC features on same cohorts. |
| **tcellNF** (OpenReview uuQjL4L0J9) | Normalizing flows on CAR-T scRNA conditioned on durable response; imputes perturbation effects | Overlap on CAR-T outcome modeling | Generative/flow-based; no explicit controllability index or network control. |
| **Functional CAR-T atlas** (`ML4BM-Lab/Functional-cart-atlas`; Zenodo 17213452) | >1M cells, 13 studies, 11 phenotypes, response/ICANS metadata | Overlap on **CAR-T product characterization** | Atlas/resource, not a controllability method. Use for phenotype labels + validation of our signature enrichment. |
| **Augur / pertpy Distance** | Ranks cell types or perturbations by response magnitude | Overlap on "which perturbations matter most" | Phenomenological ranking, not multi-component controllability with clinical bridge. |
| **Augur-style + Marson regulator coefficients** (shipped in dataset suppl. tables) | Pre-computed polarization/activation regulator ranks per condition | Overlap on Th1/Th2/activation axes | We extend to exhaustion/memory/cytotoxicity + ISCI formalism + patient validation. |

**Positioning sentence for judges:** pert2state_model asks "which perturbations reconstruct this signature?"; ISCI asks "which genes **control** therapeutically relevant state transitions in a **reproducible, structurally grounded, stable, and clinically projectable** way?"

---

## 5. Novelty gap (what nobody has done, feasible in a week)

No prior work unites, over this newly released CD4+ genome-scale map:
1. **directional movement** along *clinically defined* T-cell axes, weighted by
2. **reproducibility** (cross-donor/cross-guide, already in the data), plus
3. **structural network control** (driver-node/FVS-MDS), plus
4. **in-silico concordance** (CellOracle/GEARS/State), plus
5. **target-state stability** (geometric coherence) — *novel component*, and then
6. **cross-validation against independent functional screens**, and
7. **projection onto patient CAR-T / bispecific cohorts** to predict resistance/sensitivity,
8. delivered as an **auditable, provenance-tracked Claude Science skill** with per-gene traceable citations.

We are not inventing a new inference method from scratch (high risk in 7 days); we are defining a
**defensible, benchmarked, clinically-bridged controllability index** and proving each component adds signal.

---

## 6. Open-source repos to reuse / cite (respect "new work only" — integration code written during event)
- `emdann/GWT_perturbseq_analysis_2025` (dataset code — study, don't copy)
- `morris-lab/CellOracle`, CEFCON, `GuanLab/PSGRN`, `mancusolab/perturbvi`, `Dionysos-o/CID`
- `scverse/pertpy`, `scverse/scanpy`, `scverse/scvi-tools`, `saezlab/decoupler`
- `carmonalab/ProjecTILs`, `causalbench`
- Arc `State` GitHub / `tahoebio/Tahoe-x1` (HuggingFace)

---

## 6b. Mechanism matrix — resistance & sensitivity (what ISCI should explain)

| Mechanism class | CAR-T manifestation | Bispecific/TCE manifestation | Omics layer to integrate | ISCI axis link |
|---|---|---|---|---|
| **T-cell intrinsic exhaustion** | Product enriched in Tex markers (PDCD1, LAG3, HAVCR2, TOX) | Non-responders: sustained PD-1/TIM-3/LAG-3 on CD4/CD8 | scRNA, CITE-seq, ATAC (Belk/PNAS 2021) | exhaustion-like ↓ controllability on memory axis |
| **Loss of stem/memory potential** | Low TCF7/FOXO1/IL7R; high effector/senescent (CD57+) | Failure to expand functional CD8 | scRNA + regulons (FOXO1 Nature 2024) | memory-like controllability score |
| **CAR-Treg / suppressive subsets** | CD4+ HELIOS+ CAR-Treg in non-responders (Haradhvala, Good) | Sustained CD38+ Tregs in non-responders (teclistamab) | scRNA, CyTOF | Treg axis + negative control nodes |
| **Tonic signaling / activation overload** | CD28ζ products; chronic activation → dysfunction | Early CD38+ activation without functional expansion | scRNA, phospho-flow (if available) | activation axis |
| **Epigenetic lock-in of exhaustion** | Irreversible Tex chromatin (ATAC); AP-1/TOX enhancers | Same programs in BM/PB longitudinal | ATAC/multiome, methylation (TET2/DNMT3A) | D + S components |
| **Metabolic fitness** | Glycolysis/OXPHOS imbalance; mTORC1 (IKAROS/ETS1 axis) | Myeloid-rich BM niche limiting effector expansion | scRNA + metabolic gene sets | activation + memory axes |
| **Antigen escape** | CD19 loss, splicing, methylation | BCMA loss (minor in teclistamab) | DNA-seq, flow | **Out of ISCI scope** — report as confounder |
| **TME immunosuppression** | Tregs, MDSCs, TGF-β in tumor/BM | Myeloid expansion at expense of effectors (ResisTec) | scRNA spatial (niche) | spatial validation layer (optional) |

**Clinical translation rule:** ISCI nominates **T-cell-intrinsic control nodes**; we explicitly flag when resistance is likely **tumor-intrinsic** or **microenvironmental** so clinicians don't over-interpret.

---

## 7. Questions for IDOR immunologists (validation of domain)
1. Do the functional axes (activation, Th1/Th2, exhaustion-like, memory-like, CD4-CTL) make biological
   sense for **CD4+**? Missing any (Treg induction, Tfh, senescence)?
2. Is **CD4-CTL / cytotoxicity** defensible as a clinical axis in CD4, or should we lead with Th1/effector?
3. Which genes do they trust as **true controllers** of T-cell state (so we check ISCI recovers them)?
4. For the patient bridge: which cohort/endpoint is most credible clinically (durable CR vs ORR vs PFS)?
5. Access to **spatial transcriptomics** of lymphoma/tumor T-infiltrate (niche validation)?
6. Priority clinical framing: CAR-T failure, bispecific/TCE resistance, or broad immune reprogramming?
7. Any IDOR CAR-T / bispecific patient data (even bulk) usable under proper governance for a later phase?

## 7b. Who to ask — help network (prioritized)

### IDOR — imunologia / hemato (seu diferencial clínico)
**Objetivo:** validar eixos, priorizar narrativa clínica, acesso a dados locais.

| Pergunta-chave | Por que importa |
|---|---|
| Quais eixos de estado T são clinicamente acionáveis em **CD4+** no contexto hemato? | Evita overclaim de CD4-CTL |
| Para **CAR-T** vs **biespecífico**, qual endpoint vocês confiam mais (CR durável, MRD, PFS)? | Define D4 |
| Top 10 genes que vocês consideram "controladores reais" de exaustão/memória? | Ground-truth clínico além da literatura |
| Existe coorte IDOR (mesmo bulk RNA) de pacientes CAR-T/biespecífico com desfecho? | Pode virar validação exclusiva pós-hackathon |
| Dados de **spatial** em linfoma com infiltrado T? | Habilita camada de nicho |

**Como abordar:** enviar 1-pager com Fig. esquemática ISCI + tabela de eixos + top-20 genes preliminares; pedir 30 min de revisão assíncrona.

### Discord do hackathon (Anthropic / Cerebral Valley)
- `#questions` — dúvidas de regras, datasets, submissão
- `#office-hours` — 17–18h ET diário (ter–sex)
- `#announcements` — lives e deadlines
- Ping `@CV` em `#hackathon-access` se role não aparecer

### Lives Anthropic (obrigatórias para Claude Use)
| Data | Quem | O que extrair para o projeto |
|---|---|---|
| Ter 7/jul 12h ET | Kickoff | Regras, critérios de julgamento, datasets Gladstone |
| Qua 8/jul 12h ET | Alexander Tarashansky | Features subutilizadas do Claude Science; skills/provenance |
| Sex 10/jul 12h ET | Sukrit Silas (Gladstone) | Alinhar ISCI com screening in silico → **prêmio Gladstone** |
| Qui 16/jul 12h ET | Final judging | Narrativa da demo |

### Gladstone / datasets opcionais do evento (não são nosso foco primário, mas conectam)
- **Marson Perturb-seq** — nosso dataset principal (já mapeado)
- **ChromBPNet / Corces VEP** (`vep.corces.gladstone.org`) — variantes → cromatina por tipo celular; útil se quisermos camada regulatória genômica
- **Zoonomia / HARs** (Pollard lab) — evolução regulatória; tangencial ao projeto T-cell, mas forte para prêmio Gladstone se conectarmos enhancers de genes controladores

### Parceiros técnicos (via connectors, não humanos)
PubMed, Consensus, Open Targets, ClinicalTrials, bioRxiv, Wiley Scholar Gateway — ver §10.

---

## 8. Questions for Anthropic office hours / lives
- Best pattern to package the pipeline as a **Claude Science skill** + expose provenance in submission.
- Local compute limits (Mac 24GB) vs HPC/connectors — when to offload.
- Sukrit Silas (Gladstone, Jul 10 live): align controllability with in-silico genome-wide PPI screening
  (relevant to the Gladstone prize).
- Alexander Tarashansky (Jul 8 live): Claude Science capabilities we may be under-using.

---

## 9. Claude Science — official features (product + docs)

**What it is:** a **beta app** (not a new model) for macOS/Linux that orchestrates analyses with **full provenance** — code, environment, conversation welded to every artifact.

### Core capabilities (from [claude.com/product/claude-science](https://claude.com/product/claude-science))
| Feature | What it means for ISCI |
|---|---|
| **Domain specialists** | Pre-configured for genomics, single-cell, proteomics, structural biology, cheminformatics |
| **60+ scientific databases** | Query without learning each API; we use connectors for traceable citations |
| **Provenance on every artifact** | Code + env + conversation → audit trail (our SaMD-style deliverable) |
| **Background fact-checker** | Flags untraceable numbers/citations before results surface |
| **Native renderers** | Proteins, alignments, genomic tracks, chemical structures, PDFs |
| **Figure iteration** | Plain-language edits to figures; agent edits underlying code |
| **Manuscript drafting** | Markdown/LaTeX alongside analysis |
| **Persistent Python/R kernels** | Fast iteration; variables stay in memory |
| **Compute: local → HPC → Modal** | Slurm over SSH; batch scripts; scales beyond Mac 24GB |
| **Skills + connectors** | Save pipeline as reusable skill; every future session inherits it |
| **NVIDIA BioNeMo Agent Toolkit** | Evo 2, Boltz-2, OpenFold3 — optional structural/cheminformatics layer |
| **Privacy** | Runs on your infrastructure; data stays local |

### Life Sciences marketplace (`anthropics/life-sciences`) — plugins to install in Claude Code
**MCP servers:** pubmed, biorxiv, consensus, wiley-scholar-gateway, open-targets, chembl, clinical-trials, synapse, 10x-genomics, biorender, owkin, cortellis, adisinsight, medidata, tooluniverse

**Skills:** single-cell-rna-qc, scvi-tools, nextflow-development, instrument-data-to-allotrope, clinical-trial-protocol, scientific-problem-selection

**Install pattern (Claude Code):**
```
/plugin marketplace add https://github.com/anthropics/life-sciences.git
/plugin install pubmed@life-sciences
/plugin install open-targets@life-sciences
# ... etc.
```

### Featured connectors (Claude Science app — Customize → Connectors)
Benchling, BioMart, CellGuide, bioRxiv/medRxiv, ClinicalTrials.gov, Medidata, and partner directory at claude.com/connectors. Add custom MCP via URL or local command.

---

## 10. Connectors — two environments (do not conflate)

**Build and demo run in Claude for Life Sciences.** Cursor MCPs are for local planning only.

### 10a. Claude for Life Sciences (primary — use in implementation)

| Connector / skill | ISCI stage |
|---|---|
| `mcp-pubmed` | Evidence cards; literature per gene |
| `mcp-biorxiv` | Preprint checks (Marson, Belk, Shesha) |
| `mcp-open-targets` | Druggability, disease (LBCL/MM/ALL) |
| `mcp-chembl` | Druggability of controller genes |
| `mcp-clinical-trials` | CAR-T / TCE trial context |
| `mcp-protein-annotation` (STRING, InterPro, HPA) | **D** — PPI network (Gladstone hook) |
| `mcp-regulation` (ENCODE, JASPAR, UniBind) | **D** — TF→target edges for GRN |
| `mcp-omics-archives` (GEO, ArrayExpress) | D3/D4 — GSE151511, Belk, Schmidt |
| `mcp-genes-ontologies` (MyGene, GO, Reactome) | Axis validation; evidence cards |
| `mcp-expression` (GTEx) | Benchmark negatives (expression-matched) |
| `mcp-cellguide` (CELLxGENE) | Validate `axes.yaml` markers |
| `mcp-human-genetics` (GWAS, eQTL) | Optional controller support |
| `scvi-tools` | D4 — CAR-T atlas latent projection |
| `scgpt` | Optional A/S embedding (stretch) |
| `literature-review` | Hallucination-safe evidence synthesis |
| `figure-style` / `paper-narrative` | Demo central figure |
| `hematology-medical-writer` | Clinician report |
| Sub-agents (`host.delegate`) | Parallel evidence cards (Claude Use 25%) |

**Not available in Claude Science (Cursor-only — do not depend on):** Consensus, Wiley Scholar Gateway, Cortellis, Medidata, Synapse, Owkin, tooluniverse.

### 10b. Cursor workspace (planning / secondary)

| Connector | Notes |
|---|---|
| PubMed, Open Targets, bioRxiv, ClinicalTrials | Overlap with Claude Science |
| Consensus | Useful in Cursor; **not** in Claude Science build path |
| Context7 | Library docs during local editing |

**Workflow rule:** every top gene gets an evidence card: ISCI score + **PubMed + Open Targets + literature-review** (no hallucinated references).

---

## 11. Open-source repos — extended inspiration list

| Repo | License | Use in hackathon |
|---|---|---|
| `emdann/GWT_perturbseq_analysis_2025` | — | Understand data structure; figure map |
| `emdann/pert2state_model` | MIT | **Baseline to beat** (Marson's own approach) |
| `morris-lab/CellOracle` | MIT | Descoped (CPU-local); pert2state for A |
| CEFCON | open | Component D reference |
| `GuanLab/PSGRN` | — | GRN inference benchmark |
| `scverse/pertpy` | BSD | Mixscape, Augur, Distance, harmonized datasets |
| `carmonalab/ProjecTILs` | — | State reference atlases |
| `zinagoodlab/tcellMIL` | — | Clinical prediction baseline for D4 |
| `ML4BM-Lab/Functional-cart-atlas` | — | CAR-T meta-atlas validation |
| `causalbench` | — | GRN evaluation framework |
| Arc `State` / `tahoebio/Tahoe-x1` | open | Foundation perturbation models (D6) |
| `kundajelab/chrombpnet` | — | Optional regulatory genomics (Gladstone track tie-in) |

---

## 12. Reference shortlist (for citation manager)
- Zhu, Dann et al. bioRxiv 2025.12.23.696273 (Marson CD4+ Perturb-seq)
- Belk et al. Cancer Cell 2022; PMC9949532 (exhaustion CRISPR; ARID1A/INO80)
- Zhang et al. Nature 2023 s41586-023-06733-x (in vivo T-cell fate regulomes)
- Doan/Klebanoff et al. Nature 2024 s41586-024-07300-8 (FOXO1; TCF7/FOXO1 regulon predicts response)
- Kamimoto et al. Nature 2022 s41586-022-05688-9 (CellOracle)
- Wang et al. Nat Commun 2023 s41467-023-44103-3 (CEFCON)
- Heumos et al. Nat Methods 2025 s41592-025-02909-7 (pertpy)
- Andreatta & Carmona Nat Commun 2021 s41467-021-23324-4 (ProjecTILs)
- Frangieh et al. Nat Genet 2021 00779-1 (Perturb-CITE-seq)
- Haradhvala et al. Nat Med 2022 (GSE197268); Deng et al. Nat Med 2020 (GSE151511 / GSE150992)
- Geometric coherence, arXiv 2604.16642 (stability)
- Cancers 2025 PMC12609497; Front Immunol 2026 1861111 (resistance reviews)
- Dann E. pert2state_model (GitHub); Zhu/Dann Fig. 4 regression model (bioRxiv 2025.12.23.696273)
- Tsui et al. tcellMIL (Blood 2025-5897; NeurIPS 2025; github.com/zinagoodlab/tcellMIL)
- Functional CAR-T atlas (Zenodo 10.5281/zenodo.17213452)
