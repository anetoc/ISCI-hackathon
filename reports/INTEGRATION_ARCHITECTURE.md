# Integration architecture: from a single-modality controllability signal to a multiomic, bench-to-bedside platform

*A design document. It proposes how to grow the locked CCI/IEC result into a multiomic system without
breaking the discipline that made it credible. Every external tool named below is a capability that
exists in this environment's catalog; nothing here assumes a resource we don't have. This is
architecture and vision, not a claim of completed work — completed results are in `PAPER.md` and
`MASTER_DOSSIER.md`.*

---

## 0. One operator, many layers

The most valuable thing we built is not "a T-cell controllability score." It is an **operator**:

> **CondInfo(X | magnitude):** does feature *X* carry information about controller status *after*
> conditioning on effect magnitude, tested against expression/power-matched negatives, with a
> bootstrapped incremental-AUPRC gain and a permutation null?

Everything downstream is an application of that operator. In the current paper *X* = {cross-donor
RNA coherence, axis-specificity}. But the operator is **modality-agnostic**. Nothing in it is RNA-
specific. Replace *X* with protein-level coherence, chromatin accessibility change, a
foundation-model embedding neighborhood, or a spatial-niche effect, and the *same* test asks the
*same* falsifiable question. That is the architectural backbone: **one operator, many evidence
layers, each residualized against magnitude and each independently falsifiable.**

This reframes multiomics correctly. We are not "adding modalities to improve a predictor" (which
invites overfitting and the magnitude trap in new clothing). We are asking, per modality: *does this
orthogonal view of the perturbation add controllership information the RNA view did not?* A modality
that adds nothing is a reportable negative, exactly as PageRank centrality was. The honesty scales
with the system.

---

## 1. The controllability tensor

Represent the whole program as one sparse tensor **T[gene, axis, system, modality]**, whose entries
are *evidence scores* for "gene controls axis, in this system, seen through this modality," each
already magnitude-residualized. The current result populates one slab:
`T[·, {persist,kill,resist}, Marson_CD4, RNA_coherence]`. Every expansion below fills additional
`modality` or `system` slices of the *same* object.

Two rules keep the tensor honest and are non-negotiable design invariants:

1. **Every entry carries provenance and a magnitude residual.** No raw score enters the tensor; only
   the residual-against-magnitude percentile does, with a data SHA, method version, and matched-null
   record attached. This is the existing `isci.repro` stamp generalized to a cell of the tensor.
2. **Aggregation across modalities is rank-based and late.** We never average raw modality scores
   (different scales, different confounds). We combine *ranks* of *residuals*, and we always report
   the per-modality slice next to the aggregate, so a reader sees which modality carried a claim.
   This is the same rank-product / residualized-percentile discipline already locked for RNA.

The tensor is the integration point. "Add a modality" = "compute one operator over a new data source
and write a slice." That is a plugin, not a rewrite.

---

## 2. Multiomic evidence layers

Each layer below is an independent overlay. The design contract is identical: compute a
per-perturbation (or per-gene) feature, residualize against magnitude, run `CondInfo`, write a
tensor slice, emit an evidence card. Layers are ordered by 1-week feasibility.

### 2.1 Protein co-regulation — CITE-seq / totalVI  *(scvi-tools)*
The Frangieh system is already Perturb-**CITE**-seq: it carries surface protein. `totalVI`
(scvi-tools) learns a joint RNA+protein latent, giving a *protein-level* axis-specificity and
coherence. **Question:** does protein-level coherence add controllership information beyond
RNA-level? This directly tests whether our RNA signal is a transcriptional shadow of a
protein-level control event. Feasible now; the data is in hand.

### 2.2 Chromatin control — accessibility from sequence  *(borzoi, evo2, mcp-regulation)*
Two complementary reads. (i) **Empirical:** ENCODE accessibility/ChIP and JASPAR/UniBind TF-binding
(`mcp-regulation`) tell us whether a controller TF has *real* binding evidence at the genes of the
axis it supposedly controls — a mechanistic corroboration layer, not an inference. (ii)
**Predictive:** `borzoi` predicts accessibility/expression tracks from DNA and scores the regulatory
effect of a variant; for a controller, we can ask whether its target axis-genes' regulatory windows
carry predicted signal, and `evo2` scores sequence-level constraint. **Question:** do controllers
concentrate at loci with real TF-binding and predicted regulatory potential more than
magnitude-matched non-controllers? This is the honest version of the abandoned "D/network"
component — evidence, not inferred topology.

### 2.3 Spatial niche — where control happens  *(scvi-tools: cell2location / DestVI / Tangram)*
The clinical null taught us that *composition* (CD8 fraction) beat every transcriptional axis. That
is a spatial/compositional signal we have not exploited. Mapping IEC axes onto spatial
transcriptomics of lymphoma or the CAR-T–tumor interface (cell2location for deconvolution, Tangram
for mapping) asks: **is the persistence axis spatially organized relative to tumor contact?** This is
the natural home for the "reach-and-hold synapse" hypothesis that BEHAV3D hinted at, and it targets
exactly the compositional axis the null flagged as dominant.

### 2.4 Protein structure & drugability  *(boltz / chai1, fair-esm2, mcp-protein-annotation)*
For the Category-A/B controllers, structure prediction (`boltz`, `chai1`) and protein LM mutation
scoring (`fair-esm2`) turn the decision board from a triage table into a *tractability dossier*:
predicted structure, ligandability, domain architecture (`InterPro`/`Pfam`), interaction context
(`STRING`), and tissue expression (`Human Protein Atlas`). **Question, kept honest:** is a controller
structurally modulable *and* does the intervention direction (from the signed graph) point the
therapeutically desirable way? Structure informs *how*, never *whether* — the clinical null still
bounds the claim.

### 2.5 Sequence & perturbation foundation models  *(scGPT, evo2)*
Already scoped (Brief 05): zero-shot, matched-negative concordance — does an FM that never saw our
labels place controllers in a distinguished region? This is a *triangulation* slice, deliberately
independent, never a fine-tuned predictor.

### 2.6 Proteomics / phospho archives  *(mcp-omics-archives: PRIDE)*
TCR signaling is phospho-signaling; RNA is a proxy. The NF-κB / TCR-proximal enrichment we found is
a hypothesis that phospho-proteomics (pLCK, pZAP70, pLAT, pPLCγ1, pERK, pS6, p65) is the right
readout for. PRIDE (`mcp-omics-archives`) is where public phospho datasets live. This is a
roadmap-tier corroboration layer, not a one-week build, and should be pre-registered.

### 2.7 Patient-cohort genomics & trials  *(mcp-cancer-models, mcp-clinical-trials)*
The bedside end: cBioPortal (`mcp-cancer-models`) tells us whether a controller is mutated/altered in
lymphoma/CLL/myeloma cohorts and how that tracks with outcome; ClinicalTrials.gov
(`mcp-clinical-trials`) tells us whether any controller is already a trial target. This closes the
evidence card: mechanism → tractability → is anyone already testing it.

---

## 3. Software architecture

### 3.1 Layering
```
                 ┌─────────────────────────────────────────────┐
   presentation  │  dashboard (HTML) · evidence cards · PAPER   │
                 ├─────────────────────────────────────────────┤
   aggregation   │  controllability tensor  T[gene,axis,sys,mod]│  ← rank-of-residuals, late fusion
                 ├─────────────────────────────────────────────┤
   operator      │  CondInfo(X | magnitude)  — the locked test  │  ← modality-agnostic, ONE impl
                 ├─────────────────────────────────────────────┤
   modality      │ RNA │ protein │ chromatin │ spatial │ FM │ … │  ← plugins, one contract each
   adapters      ├─────────────────────────────────────────────┤
   data registry │  config/datasets.yaml  (system + expected)   │  ← already built
                 └─────────────────────────────────────────────┘
```

The invariant: **the operator layer has exactly one implementation** (the locked
`isci-controllership` skill helpers). Modalities differ only in how they produce the feature *X* and
the matched-negative set; they all call the same `CondInfo`. This is what prevents each new modality
from quietly inventing its own, unauditable version of the test — the single most likely way this
project could rot.

### 3.2 The modality-adapter contract
Every modality plugin implements the same four functions, mirroring the registry pattern already in
`isci/run_cci.py`:
```
feature(perturbation, axis, data)      -> per-unit score X
matched_negatives(positives, meta)     -> expression/power-matched negatives  (locked helper)
residualize(X, magnitude)              -> magnitude-orthogonal residual        (locked helper)
verdict(residual, negatives)           -> {gain, ci, perm_p, PASS/FAIL}        (locked CondInfo)
```
A new modality is a file that fills `feature()` and declares its magnitude covariate. Everything
else is inherited. `run_cci.py` already does this for datasets; the generalization is `run_layer.py`
doing it for modalities, writing tensor slices to the canonical `cci_result.json` contract.

### 3.3 Provenance as a first-class citizen
Extend the existing SHA/env/git/seed stamp so every tensor entry is reproducible in isolation, and
every evidence card resolves claim → modality → data → method version → citation. This is the "claim
carries its verdict" discipline already in the evidence cards, made structural across modalities. A
reviewer can pull any single number back to the exact cell and code that produced it. That
auditability *is* the product's moat as much as any single result.

### 3.4 Compute placement (engineering realism)
- **Local / CPU (Mac, this session):** all operator work, aggregation, dashboards, evidence cards,
  the registry — everything that is a residualized test over precomputed features. This is cheap and
  is where the science-critical logic lives.
- **Remote / GPU (`remote-compute-ssh`, vuno-idor):** the feature-*production* steps that need it —
  totalVI/scVI training, borzoi/evo2 inference, scGPT embedding, spatial mapping. These emit feature
  files that come back to the local operator. The split is clean: **GPU produces features, CPU runs
  the falsifiable test.** No scientific claim depends on the GPU step succeeding; a failed feature
  job just leaves a tensor slice empty, reported as such.
- **Contract for handoff:** feature files are the interface. A GPU job's only obligation is to write
  a per-perturbation feature table with a provenance stamp; the operator layer consumes it
  identically regardless of which modality produced it.

### 3.5 What NOT to build
- **No end-to-end learned multiomic predictor of clinical response.** The null is decisive: at
  current power that is fitting batch structure. A late-fusion, per-modality, falsifiable tensor is
  the honest architecture; a black-box multiomic classifier is the trap we already fell into and
  climbed out of.
- **No inferred-GRN control component as a deliverable.** It lost to magnitude once (PageRank added
  nothing) and CEFCON already occupies that niche. Keep GRN as an *evidence overlay* (real TF-binding
  from `mcp-regulation`), never as a driver of the ranking.

---

## 4. Bench-to-bedside: the honest translation ladder

Translation here is not a pipeline; it is a **ladder of falsifiable rungs**, each of which can fail
and bound the claim. We have climbed the first two and hit an honest wall on the fourth. The
architecture's job is to make each rung a runnable test, not a narrative.

| Rung | Claim | Status | What the next rung needs |
|---|---|---|---|
| 1. Perturbation biology | Controllership ≠ magnitude, immune-scoped | **DONE** (locked, 3-immune-system magnitude-independence, single-cell confirmed) | — |
| 2. Capacity structure | Engagement is a ~2.5-axis capacity | **DONE** (pseudobulk + single-cell, CD8-controlled) | protein/spatial confirmation of the axes |
| 3. Mechanism | Specific families (NF-κB, Treg-brake) control axes independent of magnitude | **DONE, hypothesis-grade** | phospho-proteomic readout (PRIDE); TF-binding corroboration (ENCODE/UniBind) |
| 4. Clinical association | An axis predicts CAR-T response | **NULL, well-powered** (batch, not biology) | composition-aware, cross-study design; the CD8-fraction lesson |
| 5. Tractability | A controller is safely modulable in the desirable direction | **triaged, not tested** | structure/ligandability (boltz/ESM2); cohort genomics (cBioPortal); trial landscape |
| 6. Intervention | Modulating a controller changes engagement in cells | **not started** | wet-lab CRISPRi/a mini-panel (8–12 candidates), the frontier rung |

The ladder is the translational contribution. It says precisely where the bench-to-bedside path is
supported (rungs 1–3), where it currently breaks (rung 4, and *why* — composition confound), and what
the minimal next experiment is (rung 6, a small titrated CRISPRi/a panel reading persistence /
killing / exhaustion / cytokines / viability). A hematologist reading this knows what to fund next
and what not to believe yet — which is the whole point of translational honesty.

### 4.1 The bedside-facing artifact
The deliverable a clinician actually uses is not the tensor; it is the **evidence card per
controller**: axis controlled, direction of desirable intervention, tractability tier, whether it is
mutated in the relevant malignancy (cBioPortal), whether a trial already targets it
(ClinicalTrials.gov), and — stated plainly — that no axis is a validated response biomarker. Every
card carries its own scope line and the clinical disclaimer. This is where software architecture
serves the clinic: the same provenance graph that satisfies a Nature Methods reviewer generates a
traceable, non-overclaimed card a tumor board could read.

---

## 5. Concrete build order

**One-week, local + one GPU pass (highest value, lowest risk):**
1. `totalVI` on Frangieh — protein-level controllership slice (data in hand; tests RNA-vs-protein).
2. TF-binding corroboration for the top controllers via `mcp-regulation` (ENCODE/JASPAR/UniBind) —
   pure API, no GPU, directly strengthens the mechanism rung.
3. Generalize `run_cci.py` → `run_layer.py` so a modality is a plugin; wire the tensor + one new
   dashboard panel showing per-modality slices side by side.
4. Evidence-card generator extended with cBioPortal + ClinicalTrials.gov fields (rung 5).

**Frontier (pre-registered, not this week):**
5. Spatial mapping of IEC axes (the composition lesson from the null).
6. Phospho-proteomic readout of the NF-κB/TCR hypothesis (PRIDE).
7. Wet-lab CRISPRi/a mini-panel — the only rung that converts association into intervention.

**The discipline that must survive all of it:** one operator implementation; magnitude residual on
every entry; per-modality slices always shown next to aggregates; a negative modality reported as a
negative; and the clinical null never quietly upgraded. The architecture is worth more than any
single new omic because it makes every future layer *falsifiable on arrival*.