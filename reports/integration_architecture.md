# Integration architecture — CCI/IEC as a layer-agnostic controllability platform

**Status: forward architecture / design (vision layer). NOT results, NOT claims.** Everything here
respects the claim tiers in `result_lock.md` and the Shesha positioning in `PRD v2` §1: the
magnitude-confound diagnosis is *convergent with Raju 2026*, not ours-alone; what is ours is the
immune-functional, cross-donor, axis-specific, falsifiable-boundary, controller≠target, clinical-null
package. This document is the **software-engineering + multiomic + bench-to-bedside** blueprint for
turning that package into an extensible platform. It is written to be reviewed and vetoed by Claude
Science before any of it becomes a claim.

Author lane: this is the engineering/architecture contribution (the "hands"); the science/positioning
lives with Claude Science (the "brain").

---

## 0. Where we are (grounded, synced)

- Locked core `ISCI_orthogonal` (AUPRC 0.722 vs 0.415; ΔAUPRC +0.229 [0.072, 0.405]; ρ_magnitude +0.02).
- Immune-scoped boundary: Marson PASS > Schmidt near-miss > Norman near-FAIL > Replogle FAIL.
- **Now synced & citable (P5–P7, commits `3b4d649`/`3db1dab`/`5bf3c0c`, integrated on Mac `56634c1`):**
  P5 single-cell 2.5-axis confirmed on 455k CAR-T atlas (persist orthogonal, kill↔resist −0.53,
  survives CD8 control −0.44); P6 Frangieh = **3rd** replication of C⊥magnitude (0.02/0.05/0.03),
  ΔAUPRC +0.118 (near-miss); P7 Papalexi NOT-EVALUABLE (no baseline axis).
- Clinical NULL (CAR-T atlas, leave-study-out 0.533 < CD8 baseline 0.585). Controller≠target
  (therapeutic convergence a 3rd independent axis).

The rest of this document is **not yet done** — it is the integration design.

---

## 1. The one unifying abstraction (the new perspective)

Everything we have built is one operator applied once. The leverage is to make it **layer-agnostic**:

```
Controllership(g → A | M)  ::=  does perturbing g move a functional axis A
                                reproducibly and axis-specifically,
                                CONDITIONAL on effect magnitude M?
```

Today this operator is instantiated on **one substrate** (RNA Perturb-seq, T-cell state axes,
cross-donor replicates). The architectural claim: `Controllership` is defined purely over a
**(perturbation, effect-matrix, functional-axis, replicate-structure, magnitude)** tuple — nothing in
it is RNA-specific. So the same operator runs on protein, phospho, chromatin, or spatial effect
matrices the moment each is expressed in that tuple. **Multiomic integration and software
extensibility are the same problem**: define the tuple as a contract, write one adapter per layer, and
the locked kernel runs unchanged.

This also cleanly positions us vs Shesha: Shesha's cell-to-cell coherence, our cross-donor coherence,
and our axis-specificity are **three coordinates of the same reproducibility geometry**. The operator
above is agnostic to which coordinate you feed as the conditional feature — so Shesha's Sₚ becomes a
*fourth registered feature* we can test head-to-head, not a competitor.

---

## 2. Software / computational architecture

### 2.1 The stable core (already exists — freeze it as a library)
`skills/isci-controllership/kernel.py` is the locked statistical kernel (expression_matched_negatives,
conditional_lr_test, bootstrap_auprc_gain, controllership_score, movability_gate,
clinical_reversal_score, matched_null_enrichment, confounder_ledger). **Action:** version it as a real
installable package (`isci-controllership==1.0`, pinned), deduplicate the `skill/` vs `skills/` copies
(one source of truth), and pin its API — every downstream layer imports it, never reimplements.

### 2.2 The integration contract (the keystone)
Define a canonical, typed schema — the single thing every omic layer must produce:

```
PerturbationEffectMatrix         # one per (dataset, layer)
  effect:    perturbation × feature  (signed effect vs matched control)
  replicates: per-(perturbation, replicate) effect vectors   # donors/wells/HTO/cells
  magnitude:  per-perturbation M
  axis:       signed feature-loading vector(s)  (leave-marker-out enforced)
  labels:     {positives, admissible_negatives}  # never invented
  provenance: {git_sha, data_sha256, axes_sha256, layer, adapter, timestamp}
```

Enforce it with `pydantic` (or dataclasses + a validator). Once data is in this shape, the kernel is
layer-blind. This is the difference between "a pile of scripts" and "a platform."

### 2.3 Adapters (one per data source, the only per-dataset code)
Formalize `isci/adapters/<name>.py` implementing `Adapter.to_effect_matrix(raw) -> PerturbationEffectMatrix`.
The registry (`config/datasets.yaml`) already models this; make it real. Adapters we need:
`rna_perturbseq` (Marson/Schmidt/Frangieh — generalize the committed `cci_external.py` pipeline),
`cite_protein`, `phospho`, `atac`, `spatial`. **New datasets = a config block + maybe an adapter; zero
kernel changes.** (Frangieh proved the pattern; `cci_external.py` is the seed of `rna_perturbseq`.)

### 2.4 The gate as a first-class type
EVALUABLE / NOT-EVALUABLE / PASS / FAIL is not a comment — make it a returned enum with a machine-
checkable `reason`. Every adapter runs an **admissibility gate** (effect matrix? ≥2 replicates?
credible non-circular axis? real label set?) before the kernel is allowed to run. This is what caught
Shifrut (regulators-only) and Papalexi (no baseline axis) cheaply; encode it so it can never be
skipped. Gate-first is the platform's safety property.

### 2.5 Provenance & reproducibility spine
Content-addressed manifests (`git_sha`, `data_sha256`, `axes_sha256`, command, timestamp) on every
`cci_result.json`; `make reproduce-core` regenerates the locked figure from the frozen ranking; large
data stays out of Git. **Gaps to close (real, and they cost the Depth/Execution rubric):** there is no
`tests/` dir despite the AGENTS.md contract — add unit tests pinning kernel behavior on a tiny fixture
(bootstrap-gain sign, matched-negative count, LR `adds` flag, gate transitions) and a CI that runs
them + `make reproduce-core` on a synthetic dataset.

### 2.6 Fusion, done honestly (NOT concatenation)
Multi-omic controllership must be **late fusion**, not feature concatenation (which reintroduces the
magnitude/scale confound the whole method exists to avoid). Per layer: run the full CCI independently →
get per-layer C, ΔAUPRC, confounder ledger. Then a **cross-layer concordance operator**: a controller
"survives" only if it passes in ≥2 layers with concordant direction. Aggregate by rank, not by sum.
This mirrors the existing matched-null / confounder-ledger discipline, one level up.

### 2.7 Compute tiering (matches this environment)
CPU-local (the CCI test, pseudobulk — everything demonstrated so far); GPU (scVI latent, foundation
models — RTX 6000, contention-aware); HPC/Modal (genome-scale cell-level, 22M-cell Marson). The
registry tags each dataset's tier; the runner dispatches. Nothing on the critical path needs GPU —
that is a deliberate architectural property, not an accident.

---

## 3. Multiomic integration — each axis has a native layer

The deep point: IEC's axes are not all best measured in RNA. Multiomics is not decoration — **each axis
becomes causally testable only in its native layer**, and cross-layer agreement is a new falsification.

| IEC axis | Native layer(s) | Why | Data status |
|---|---|---|---|
| **A_persist** (memory/stem, reach-and-hold) | chromatin (ATAC/CUT&RUN) + memory-TF | persistence is an epigenetic commitment (TCF7/FOXO1 regulons) | `data_public/chromatin/` empty — roadmap |
| **A_kill** (cytotoxic execution) | protein / functional (CITE, degranulation, cytokine) | killing is a protein/secretion phenotype; RNA A_kill overlaps CD8-identity (ρ 0.57, P5) | CITE present in Frangieh/Papalexi (unused) |
| **A_resist** (exhaustion-resistance) | chromatin + surface checkpoint (ATAC + CITE) | exhaustion is chromatin-encoded + surface-marked (PD1/LAG3/TIM3) | roadmap |
| **TCR rheostat** (controls all three) | **phospho** (pLCK/pZAP70/pLAT/pPLCγ1/pERK/pS6/NF-κB p65) | TCR signaling IS phosphorylation; RNA is only a proxy (`tcr_reframe.md`) | `data_public/phosphoproteomics/` empty — roadmap |

**The new multiomic test (strong, falsifiable):** a controller called in RNA is *transcription-only*
unless it also moves its axis in the native layer. Run the SAME `Controllership` operator per layer;
require cross-layer concordance (§2.6). A controller that moves the RNA persistence axis but not the
chromatin persistence program is a bookkeeping artifact — this is a sharper filter than any single-layer
FDR, and it directly answers "is this a real dial?"

**Cheapest first multiomic step (no new data):** the CITE protein matrices for Frangieh and Papalexi are
already on disk and unused. Score A_kill / checkpoint axes at the *protein* level and test whether the
RNA-level controllers concord — a same-dataset RNA↔protein cross-layer check, runnable now on CPU.

---

## 4. The three-coherence framework (positions us vs Shesha AND generates a new claim)

Reproducibility has ≥3 independent coordinates. Registering all three in one comparison is both the
honest Shesha response and a novel testable structure:

1. **Cell-to-cell coherence** (Shesha Sₚ) — directional agreement of single-cell shift vectors within a
   perturbation.
2. **Cross-donor coherence** (ours, R) — reproducibility across 4 human donors.
3. **Axis-specificity** (ours, S) — alignment to a defined functional axis, leave-marker-out.

Pre-registered question (PRD P4 priority 2): **do the three capture independent information?** Compute
all three per perturbation on a dataset that supports cell-level + donor-level (Marson, or the CAR-T
atlas), then a partial-correlation / conditional-LR ladder: does each add over magnitude *and* over the
others? Outcome-agnostic — if they collapse, that's a unification; if independent, that's a richer
controllership geometry than either group has shown. This is the single highest-leverage "new
perspective," because it converts the Shesha overlap from a threat into our organizing framework.

---

## 5. Bench-to-bedside as a chain of falsifiable gates (not a pipeline)

Translation fails when it is a linear "discovery → target → trial" story. Reframe it as the same
PASS/FAIL/NOT-EVALUABLE discipline, staged — each gate can honestly stop the chain:

```
G0 Controllership   CCI on perturbation atlas         → controllers ≠ associates (magnitude-conditional)
G1 Axis assignment  IEC 2.5-axis                       → which capacity does it set?
G2 Decoupling       controller ≠ target (convergence)  → is it desirable to move, not just movable?
G3 Multiomic causal §3 cross-layer concordance         → does it move the axis in its NATIVE layer?
G4 Functional       wet-lab mini-panel (8–12)          → expansion/killing/persistence/exhaustion
G5 Manufacturing    titratable modulation in mfg        → the tractable bedside route (Category A)
G6 Clinical readback outcome association                → HONEST NULL today; a validation gate, not a claim
```

Each edge is a registered gate with an acceptance criterion, mirroring `generalization_spec.md`.
Key translational reframes (new perspectives):

- **The clinical NULL is a localizer, not a dead end.** It says the signal is not in bulk pre-infusion
  product transcriptome under cross-study CV. That *predicts where it is*: product-visible **sensitivity**
  vs post-infusion, niche/time-dependent **resistance** (`literature_gaps_roadmap.md`). Spatial (G-spatial)
  and temporal (manufacturing-timing) decompositions are the honest next tests — the NULL scopes them.
- **Manufacturing modulation (G5) is the shortest path to bedside.** Category-A controllers (KDM1A,
  CXXC1, MED13, RCOR1) are *titrated during CAR-T manufacturing*, sidestepping systemic-drug delivery
  and the target-vs-controller trap. This is where "controllership" becomes a product parameter, not a
  drug — the most credible bench-to-bedside route for a hematology group.
- **Temporal controllability.** The TCR rheostat (`tcr_reframe.md`) implies *when* you perturb matters
  (dasatinib "rest" restores memory). Controllership + timing = a manufacturing schedule, a new axis
  beyond "which gene."
- **Patient-state conditioning (honestly gated).** Whether the controller set shifts by patient state is
  the personalization question — explicitly downstream of, and bounded by, the clinical NULL; not
  claimed until G6 has power.

---

## 6. New perspectives / novel angles (summary)

1. **Controllability atlas** — the registry scaled to N immune systems = a map of *where* immune-state
   controllability holds (immune-scoped boundary as a growing, queryable resource, not a one-off table).
2. **Three-coherence decomposition** (§4) — Shesha + donor + axis as orthogonal reproducibility
   coordinates; the unifying, novel structural claim.
3. **Cross-layer controllership as a filter** (§3) — sharper than single-layer FDR; the multiomic falsification.
4. **In-silico as a prior, not a predictor** — foundation models (scGPT/pert2state/STATE) as a cheap
   pre-screen whose hits MUST pass the conditional test; a model that fails to beat the linear baseline
   is a reportable result (PRD P4; MASTER_ROADMAP P11).
5. **Manufacturing-parameter framing of controllership** (§5, G5) — the translational unlock.
6. **The gate as a data type** (§2.4) — reproducible honesty as software, not prose.

---

## 7. Concrete engineering backlog (mapped to PRD phases; this machine's lane)

- **Now, CPU, no new data:** (a) RNA↔protein cross-layer check on the on-disk Frangieh/Papalexi CITE
  matrices (§3 cheapest step); (b) three-coherence decomposition on Marson/atlas (§4); (c) add `tests/`
  + CI (§2.5). All independent, all committable.
- **Platformization:** formalize `PerturbationEffectMatrix` contract (§2.2) + `isci/adapters/` (§2.3) +
  gate enum (§2.4); refactor the committed `cci_external.py` into `rna_perturbseq` adapter.
- **GPU-gated (when RTX 6000 frees):** scVI latent robustness (EXEC-1b); foundation-model triangulation
  (P11 / EXEC-4).
- **Roadmap / FRONTIER (needs data):** phospho TCR/NF-κB (native layer for the rheostat); ATAC for
  persistence/resistance; spatial niche (IDOR differentiator); wet-lab mini-panel.

## 8. Guardrails (inherited, non-negotiable)

Nothing here changes `result_lock.md`. No layer's signal enters a claim without: pre-registration,
magnitude-matched negatives, leave-marker-out (non-circular) axis, a PASS/FAIL/NOT-EVALUABLE verdict,
and provenance. Shesha is cited as convergent prior art in every artifact. "Controller" never silently
becomes "target"; "capacity" never silently becomes "biomarker"; the clinical result stays NULL until a
powered gate says otherwise.
