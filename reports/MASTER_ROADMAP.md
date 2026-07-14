# CCI / IEC — full phased roadmap (deadline-agnostic)

> **Status note (2026-07-13):** this document now distinguishes completed hackathon work from
> bounded outcomes and genuinely external follow-up. The live inventory of unfinished work is
> `reports/PROJECT_PENDING_REGISTER.md`; scientific verdicts remain governed by
> `reports/CLAIM_LEDGER.md` and `reports/result_lock.md`.

**Framing (yours):** don't triage by Sunday; lay out every phase, ordered, and run as far as
we get — AI compresses each phase hard. So this is the complete arc: what is **done**, what is
**executable here** (with the data + tools in this environment), and what is a genuine
**frontier** (needs wet-lab, protein/phospho, or spatial data that does not exist in-window).
The one rule that governs all of it, from the locked core: **the primary claim never moves;
every phase builds beside it, never on top of it.**

The bounded thesis every phase tests, in one sentence:
> *Among detectable-effect, canonical axis-defining CD4+ T-cell regulators, axis-specificity and
> cross-donor coherence add information beyond perturbation magnitude; external failures prevent
> extending that result to a universal or immune-wide controller property.*

Legend: **[DONE]** complete and committed · **[BOUNDED]** executed but negative, limited or
structurally non-evaluable · **[FRONTIER]** needs data, compute or wet-lab work not available in
the hackathon window and is not presented as completed.

---

## PHASE 0 — Lock the project law  **[DONE]**
The claim taxonomy is frozen so no later phase can drift the story:
- **Primary claim:** CCI / `ISCI_orthogonal` — magnitude-conditional and bounded to canonical axis-defining regulators. Authoritative M→M+C +0.357 [+0.117,+0.538]; leakage-free OOF +0.215 [+0.074,+0.560], permutation p=0.010; descriptive AUPRC 0.415→0.722; matched cross-system aggregate +0.229 [0.072,0.405]; Spearman vs magnitude +0.02; 3 conditions.
- **Secondary claims:** T-REMAP, IEC, targetability, phospho, spatial, clinical bridge.
- **Hypotheses (never targets):** IKBKB, ZC3H12A, RCOR1, KDM1A, CXXC1, MED13, IRF2BP1, PDCD10…
- **Not claims:** "predicts CAR-T response", "these are therapeutic targets", "TSC predicts killing", "network/PageRank is essential".
Artifacts: `result_lock.md`, `conditional_controllability_invariant.md`, `MASTER_DOSSIER.md`.

## PHASE 1 — Boundary as a result (3-system → 4-system scope)  **[DONE]**
CCI tested across Marson CD4+ (PASS), Schmidt CRISPRa (near-miss), Norman K562 differentiation
(FAIL near-miss), Replogle RPE1 proliferation (FAIL robust). The graded boundary IS the finding.
Artifacts: `property_whitepaper.md`, `cci_scope_4systems.png`, the scalable dashboard.

## PHASE 2 — IEC definition + clinical null  **[DONE]**
IEC = A_persist (clean axis) / A_kill / A_resist (kill↔resist entangled → "2.5 axes"). Clinical
null **tested and honest**: on the CAR-T atlas (n=87), A_persist leave-patient-out 0.643
**collapses to leave-study-out 0.533**; CD8-fraction baseline (0.585) beats every axis → IEC is
a *descriptive capacity, not a response biomarker*. Bounds the clinical claim; core untouched.
Artifacts: `immune_engagement_capacity.md`, `MASTER_DOSSIER.md` §5.1, `outputs/iec_clinical/`.

## PHASE 3 — Reproducible & scalable pipeline  **[DONE]**
Dataset registry (`config/datasets.yaml`), canonical `cci_result.json` contract, dashboard,
DatasetSpec v1, CLI and bounded H5AD adapters are committed. `make reproduce-core` recomputes the
Marson method check from committed summaries and aggregates the heavy external lanes; the README
states this boundary explicitly. The abandoned M/R/D/A/S implementation is preserved under
`archive/d0/`, not presented as the final method.

## PHASE 4 — Submission package  **[DONE — SUBMITTED]**
The 2:42 narrated video, interactive demo, README, executed notebook, manuscript, claim ledger,
deck, static renders and automated overclaim/provenance gates are public. The Researcher Track
submission is author-confirmed. Private platform receipts and internal recording or rehearsal
notes are intentionally excluded because they are operational material, not research evidence.

---
## ── frontier of what's demonstrated; everything below EXTENDS the claim ──
---

## PHASE 5 — IEC cell-level structure (the 2.5-axis test)  **[DONE]**
The CAR-T atlas analysis covered 455,370 cells. Persistence remained separable while killing and
resistance formed an effector/exhaustion continuum (Spearman −0.53; −0.44 after CD8 control).
This confirms IEC as a descriptive 2.5-axis structure, not a clinical-response predictor. The
scVI-integrated robustness pass remains optional and does not alter this bounded result.

## PHASE 6 — External immune validation  **[BOUNDED]**
Schmidt remained a near-miss and the broad external non-marker functional-regulator stress test
failed against magnitude (ΔAUPRC −0.281 [−0.476, −0.073]). Frangieh protein evidence also failed
to add direction-aware signal over RNA magnitude. These are completed boundary results, not
unfinished attempts. A well-powered donor-resolved CD8/CAR-T replication remains prospective.

## PHASE 7 — Sharpen the domain boundary  **[DONE — NO IMMUNE-WIDE CLAIM]**
The four-system scope map and myeloid extension were executed. Non-immune systems failed and the
myeloid preregistered test was a near-miss, so the evidence does not support an immune-wide
invariant. The public claim remains restricted to detectable-effect, canonical axis-defining
T-cell regulators in the Marson CD4+ anchor.

## PHASE 8 — Curated mechanism sets + rank-based enrichment  **[DONE]**
Replace broad GO/Reactome (too wide for small T-regulator families; nothing survived FDR) with
**pre-registered curated gene sets**: TCR-proximal/phospho, NF-κB activation window, T-cell
chromatin modifiers, RNA-decay brakes (Regnase-1/ZC3H12A), cytoskeleton/synapse, Treg/brake.
Test rank-based enrichment along the *continuous* `ISCI_orthogonal` score (not just top-50), and
tag each gene on three independent axes: **our-data evidence / literature evidence /
tractability** (a gene high in our data + poor in literature = novel candidate; the inverse =
known marker, not a controller in this system).

## PHASE 9 — Targetability as an experimental decision board  **[DONE]**
Recast the targetability matrix into a 4-category triage (never a therapeutic recommendation):
- **A — manufacturing modulation** (KDM1A, CXXC1, MED13, RCOR1, SETDB1-like): titratable/transient in manufacturing, not systemic inhibition.
- **B — engineering candidates** (clear KD/OE direction, viability-safe): require expansion/killing/persistence assays.
- **C — probe-only biology** (BCLAF1, HEXIM1, SAMD1, CYB561D2, TWF1): understand mechanism, not target.
- **D — dangerous/positive-control rheostats** (TCR-proximal, PRKDC, broad-essential): axis controls or titrated perturbations only.

## PHASE 10 — Signed perturbation graph (network done right)  **[DONE]**
Drop PPI/PageRank centrality from the core (it added nothing over magnitude — confirmed). Build
a **perturbation-derived signed graph** (perturbed gene → modules/genes moved) and ask "which
controllers have convergent effects on persistence/TCR/exhaustion modules?" — not "who is a hub
in STRING?". Position CEFCON / CellOracle as conceptual baselines; our differentiator is causal
perturbation + magnitude-conditional testing. Exploratory layer, explicitly not a primary score.

## PHASE 11 — In-silico / foundation-model triangulation  **[BOUNDED — NOT-EVALUABLE]**
The locked scGPT branch could not be validly evaluated because the required perturbation
expression profiles were absent in the available runtime. No gene-token substitute was used and
no target was promoted. Obtaining the large expression inputs and rerunning the frozen comparator
remains a non-blocking compute extension.

---
## ── genuine frontier: needs data/assays that do not exist in-window ──
---

## PHASE 12 — Phospho/protein validation of the TCR rheostat  **[FRONTIER]**
RNA is a proxy; TCR is fundamentally phospho-signaling. Pre-registered next experiment
(phospho-flow / CyTOF / phosphoproteomics): pLCK, pZAP70, pLAT, pPLCγ1, pERK, pS6, NF-κB p65 —
test whether CCI controllers modulate the *timing/intensity window* of TCR signaling, not
whether "TCR genes are targets". Three layers: TCR module as positive control → residualize
(don't erase; only 7/20 reversers survive full residualization) → validate in protein/phospho.

## PHASE 13 — Spatial / niche localization (the IDOR differential)  **[FRONTIER]**
Not prediction validation — mechanism *localization*: where do sensitivity/resistance modules
sit relative to the tumor–T interface, Treg-rich and macrophage-rich niches, checkpoint axes
(PDCD1–CD274, TIGIT–PVR, CTLA4–CD80/86, CXCL9/10–CXCR3, TGFB, IL10)? DLBCL or myeloma with
Visium/Xenium/CosMx/GeoMx. Tests the pre-registered hypothesis that resistance emerges
post-infusion in the niche while sensitivity is product-visible. A real literature gap — few
connect perturbational controllers to a spatial resistance niche.

## PHASE 14 — Wet-lab / collaboration  **[FRONTIER, 3–6 months]**
CRISPRi/a or titrated pharmacological perturbation of 8–12 candidates in CD19 CAR-T or a T-cell
engager model; readouts: expansion, serial restimulation, killing, exhaustion, memory markers,
cytokines, phospho-flow, ATAC/CUT&RUN for chromatin hits. This is where a hypothesis map becomes
biology.

---

## Execution order after the hackathon build
1. Run the frozen off-target and guide-promotion workflow before any prospective synthesis.
2. Execute the donor-resolved paired-context experiment only after guide promotion is frozen.
3. Treat foundation-model, phospho, spatial and broader immune replications as independent
   extensions; none is required to preserve the locked hackathon claim.

## The line to defend to a reviewer
> We do not claim a computational score predicts clinical response. We show that, within
> detectable-effect canonical CD4+ T-cell regulators, precision and donor repeatability add
> information after magnitude is known. The property fails on a broader external regulator set,
> so the contribution is the auditable boundary and the prospective experiment it motivates, not
> a universal target-discovery claim.
