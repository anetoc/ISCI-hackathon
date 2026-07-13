# CCI / IEC — full phased roadmap (deadline-agnostic)

> **Status note (2026-07-12):** this document preserves the original phased strategy, but several
> `[HERE]` labels are now historical because the corresponding analyses were completed. The live
> inventory of unfinished work is `reports/PROJECT_PENDING_REGISTER.md`; scientific verdicts remain
> governed by `reports/CLAIM_LEDGER.md` and `reports/result_lock.md`.

**Framing (yours):** don't triage by Sunday; lay out every phase, ordered, and run as far as
we get — AI compresses each phase hard. So this is the complete arc: what is **done**, what is
**executable here** (with the data + tools in this environment), and what is a genuine
**frontier** (needs wet-lab, protein/phospho, or spatial data that does not exist in-window).
The one rule that governs all of it, from the locked core: **the primary claim never moves;
every phase builds beside it, never on top of it.**

The thesis every phase serves, in one sentence:
> *In immune state transitions, real controllers leave a magnitude-independent residual
> signature (axis-specificity + cross-donor coherence); this property has a domain boundary,
> fails informatively outside it, and generates a prioritized experimental map for T-cell
> reprogramming.*

Legend: **[DONE]** complete & committed · **[HERE]** executable in this environment
(CPU-local or the RTX 6000 via Claude Code) · **[FRONTIER]** needs data/wet-lab not available
now — pre-registered, not faked.

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

## PHASE 3 — Reproducible & scalable pipeline  **[HERE, in progress]**
Dataset registry (`config/datasets.yaml`) + canonical `cci_result.json` contract + dashboard
(HTML + static forest plot). **To finish:** wire `isci/run_cci.py` as the one-command driver
around the locked skill helpers, and deprecate the legacy M/R/D/A/S stub modules (honest — they
were the abandoned index). Deliverable: `make reproduce-core` runs the validated method end to
end. Serves Demo + reproducibility directly. *CPU-local, no dependency — do next.*

## PHASE 4 — Submission package  **[HERE]**
The 3-min demo (input → core figure → result-lock → evidence card → **honest negative** → next
gate) + README/writeup + overclaim lock pass (every candidate reads as *titratable
manufacturing/experimental perturbation hypothesis*, never "inhibit in patient") + make repo
public with large data outside Git. This is 30% of the rubric and must not be sacrificed to any
later phase.

---
## ── frontier of what's demonstrated; everything below EXTENDS the claim ──
---

## PHASE 5 — IEC cell-level structure (the 2.5-axis test)  **[HERE, GPU machine]**
Brief 02, corrected: the integrated atlas object has **no `X_scVI`** — use the `Python_scVI_*`
/ `scVI_hub` file. Score A_persist/A_kill/A_resist per cell on Marson subsample + atlas; test
pairwise Spearman, vs-magnitude, and **whether A_kill is separable from CD8 identity** (partial
correlation). Pre-registered outcome-agnostic: if kill↔resist stay anti-correlated at cell
level, the final definition becomes **IEC = [A_persist, A_effector/exhaustion continuum]** —
that is a discovery, not a failure. Decides if IEC is biological structure or just a useful
pseudobulk decomposition. *Confirmation/robustness, not headline — pseudobulk pre-test already
de-risked it.*

## PHASE 6 — A better immune external validation than Schmidt  **[HERE if reachable]**
Schmidt is underpowered (n_pos=10). Priority target: a **CD8 / TIL / CAR / Perturb-CITE-seq**
screen with a clear functional axis and replicates (candidates to scout: Frangieh
Perturb-CITE-seq melanoma TIL; a CD8 exhaustion CRISPR screen with donors). Test is not "same
genes" but "does C add ΔAUPRC conditional on magnitude?". With the Phase-3 registry, adding one
is a config block. Pre-registered PASS: ΔAUPRC CI excludes 0 + conditional LR significant + C ≈
orthogonal to magnitude. *One focused attempt; a 4-system boundary + honest "next test" is
already complete.*

## PHASE 7 — Sharpen the domain boundary (is CCI T-cell- or immune-scoped?)  **[HERE if reachable]**
Two orthogonal far-tests, each informative whichever way it lands:
- **Non-T immune** (myeloid / DC / NK perturbation screen): PASS → claim widens to "immune relational state transitions"; FAIL → claim tightens to "T-cell state controllability".
- **Non-immune, non-proliferation** (a second stress/differentiation screen): separates "non-immune" from "proliferation is a single axis" — Norman already hints the residual there is carried by reproducibility R, not axis-specificity S.

## PHASE 8 — Curated mechanism sets + rank-based enrichment  **[HERE]**
Replace broad GO/Reactome (too wide for small T-regulator families; nothing survived FDR) with
**pre-registered curated gene sets**: TCR-proximal/phospho, NF-κB activation window, T-cell
chromatin modifiers, RNA-decay brakes (Regnase-1/ZC3H12A), cytoskeleton/synapse, Treg/brake.
Test rank-based enrichment along the *continuous* `ISCI_orthogonal` score (not just top-50), and
tag each gene on three independent axes: **our-data evidence / literature evidence /
tractability** (a gene high in our data + poor in literature = novel candidate; the inverse =
known marker, not a controller in this system).

## PHASE 9 — Targetability as an experimental decision board  **[HERE]**
Recast the targetability matrix into a 4-category triage (never a therapeutic recommendation):
- **A — manufacturing modulation** (KDM1A, CXXC1, MED13, RCOR1, SETDB1-like): titratable/transient in manufacturing, not systemic inhibition.
- **B — engineering candidates** (clear KD/OE direction, viability-safe): require expansion/killing/persistence assays.
- **C — probe-only biology** (BCLAF1, HEXIM1, SAMD1, CYB561D2, TWF1): understand mechanism, not target.
- **D — dangerous/positive-control rheostats** (TCR-proximal, PRKDC, broad-essential): axis controls or titrated perturbations only.

## PHASE 10 — Signed perturbation graph (network done right)  **[HERE]**
Drop PPI/PageRank centrality from the core (it added nothing over magnitude — confirmed). Build
a **perturbation-derived signed graph** (perturbed gene → modules/genes moved) and ask "which
controllers have convergent effects on persistence/TCR/exhaustion modules?" — not "who is a hub
in STRING?". Position CEFCON / CellOracle as conceptual baselines; our differentiator is causal
perturbation + magnitude-conditional testing. Exploratory layer, explicitly not a primary score.

## PHASE 11 — In-silico / foundation-model triangulation  **[HERE, GPU machine]**
Strict order, each as *triangulation not proof*: linear/pert2state baseline (mandatory) →
CellOracle/GEARS/scGPT/STATE only if they add **out-of-sample direction concordance** over the
linear baseline. No in-silico model promotes a target alone. If a model doesn't beat linear,
that is itself a reportable result. (scVI/scGPT/evo2 are available on the RTX 6000.)

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

## Execution order (what I'd actually run next, here)
1. **Phase 3 finish** — `run_cci.py` driver + deprecate legacy stubs *(CPU, now)*.
2. **Phase 4** — demo + writeup + overclaim lock + public repo *(now; protects 30% of score)*.
3. **Phase 8 + 9** — curated mechanism sets + triage board *(CPU, high value, no new data)*.
4. **Phase 5** — IEC cell-level on the correct scVI file *(GPU machine, when free)*.
5. **Phase 6/7** — one better immune external + a boundary far-test *(if a dataset is reachable in a day)*.
6. **Phase 10/11** — signed perturbation graph + foundation-model triangulation *(closure/robustness)*.
7. **Phases 12–14** — declared as pre-registered next experiments; not faked in-window.

## The line I'd defend to a reviewer (unchanged across every phase)
> We do not claim a computational score predicts clinical response. We propose and test a
> falsifiable property: in immune state transitions, real controllers leave a residual signature
> of axis-specificity and biological coherence that does not reduce to effect magnitude. It has a
> domain boundary, informative failures, and generates prioritized experimental hypotheses for
> T-cell reprogramming. Conservative enough to be credible; ambitious enough to matter.
