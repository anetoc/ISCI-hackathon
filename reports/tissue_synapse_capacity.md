# Tissue Synapse Capacity (TSC) — a candidate broader property

**Status: vision layer / testable hypothesis, NOT a demonstrated result.** This note
proposes TSC as the broader property of which the Conditional Controllability
Invariant (CCI) may be one measurable component, defines how TSC could be *measured
computationally*, and states the falsification tests. The demonstrated, submitted
result remains the immune-scoped CCI; TSC is the "why it matters / where next" frame.

---

## 1. The idea, and why the CCI boundary motivates it

The CCI is **immune-scoped**: it PASSes where cell state is *relational* (T-cell
memory/effector/exhaustion/Treg — states defined by the capacity to form and sustain
productive contacts) and FAILs where state is *cell-autonomous* (RPE1 proliferation —
dosage on a single cell-cycle axis). The unifying reading:

> **Controllership is separable from magnitude precisely where cell state is governed
> by the capacity to build and sustain a functional synapse with the tissue.**

We name that latent capacity **Tissue Synapse Capacity (TSC)**: how well a T cell can
(a) hold a durable, self-renewing state, (b) traffic to and access the target tissue,
(c) assemble the immune synapse / cytoskeletal machinery, and (d) deliver serial
cytotoxic engagement. Under this frame the CCI is *not the property itself* — it is the
**control axis of TSC**: it identifies which genes *control* this capacity, distinct
from those that merely mark it.

## 2. Empirical grounding (honest, modest)

A composition check of the top-50 controllers in each system (descriptive, small-n):

| Functional family | Immune (Marson, PASS) | Non-immune (Replogle, FAIL) |
|---|---|---|
| synapse / cytoskeleton / adhesion | 3/50 (TWF1, ARHGAP30, MYO9A) | 0/50 |
| cell-cycle / replication | 0/50 | 3/50 (ATR, CDK1, SMC1A) |

A **clean double-dissociation** — synapse machinery only among immune controllers,
cell-cycle machinery only among non-immune controllers — consistent with TSC. But the
counts are small and (as with our matched-null family test) **not FDR-significant**, so
this is *suggestive directional evidence*, not proof of enrichment. Stated as such.

The external replication also weighs on the **state** side of TSC more than the synapse
side: R_memory_stem (durable-state capacity) replicated direction in **two** independent
CAR-T cohorts (GSE208052 p=0.032; GSE223655 CD8+CAR p=0.0043), whereas the synapse-act
modules (R_migration/R_killing) replicated cleanly in only one. So today's strongest
external support is for TSC's *state-holding* component, not the *synaptic-act* component
— which is exactly why the synapse validation below is the necessary next test.

## 3. Formal proposal — TSC as a latent variable with measurable loadings

TSC(cell/perturbation/patient) is a **latent capacity** with observable loadings:

| Loading | What it captures | Computational readout (available here) |
|---|---|---|
| **L1 durable state** | memory/stemness vs terminal exhaustion | module scores (R_memory_stem, NR_exhaustion) |
| **L2 tissue access** | migration / chemotaxis | R_migration module score |
| **L3 synapse assembly** | actin / MTOC / adhesion machinery | synapse/cytoskeleton gene-set score |
| **L4 serial killing** | lytic delivery / engagement | R_killing module score |
| **CCI control axis** | *which genes control the above* | conditional controllership (the invariant) |

TSC is then estimated as the shared latent factor across L1–L4 (e.g. first factor of a
factor analysis / probabilistic PCA on the per-perturbation loading matrix), and the CCI
identifies its controllers. This is measurable **from the transcriptome alone** with
tools already in hand.

## 4. How to measure TSC computationally — the pipeline (tools available here)

1. **Loading scores** per perturbation/cell: score L1–L4 module sets on any Perturb-seq
   or scRNA dataset (the movability-gated modules already exist).
2. **Synapse/cytoskeleton gene-set (L3):** assemble from GO/Reactome ("immune synapse",
   "actin cytoskeleton", "T cell receptor signaling", "leukocyte migration") — the same
   Enrichr GMT route used in the family-enrichment analysis.
3. **Latent estimation:** factor-analyze the L1–L4 matrix → TSC score; report loadings
   and variance explained. (`scvi-tools` for a probabilistic latent space if cell-level;
   plain factor analysis for pseudobulk.)
4. **Controllers of TSC:** run the CCI protocol with TSC as the target axis — does a
   magnitude-conditional signal recover TSC controllers? (`isci-controllership` skill.)
5. **Protein/interaction layer:** STRING + Human Protein Atlas (connectors) to check the
   synapse loading's controllers form an interaction module and localize to the synapse.
6. **Tractability:** Open Targets / ChEMBL for which TSC controllers are druggable
   (the targetability matrix pattern).

## 5. Falsification tests (what would confirm or kill TSC)

TSC makes **specific, testable predictions**:

- **P1 (scope):** the CCI PASSes in systems whose state is synaptic/relational and FAILs
  in cell-autonomous ones. Test: add more systems — another synaptic immune screen
  (predict PASS), another autonomous non-immune screen e.g. differentiation/stress
  (predict FAIL). Same machinery we already ran; each new system is a PASS/FAIL point.
- **P2 (composition):** TSC controllers are enriched in synapse/cytoskeleton/adhesion vs
  a matched null — the current check is directional but under-powered; a larger controller
  set or a dedicated synapse GMT would test it properly.
- **P3 (function, the decisive one):** a TSC score predicts *functional* synapse quality —
  serial-killing rate, synapse-formation efficiency, MTOC polarization — better than
  magnitude. **This requires a functional dataset we do NOT have here** (live-imaging /
  serial-killing CAR-T screens; ProteomeXchange phospho for synapse signaling). This is
  the honest gap: TSC as a transcriptional latent is measurable now; TSC as a predictor
  of physical synapse function needs data on the institutional-compute / collaboration roadmap.

## 6. Positioning

- **Submitted / demonstrated:** the immune-scoped CCI (a real, falsifiable property with a
  cross-dataset boundary).
- **TSC:** the broader property the CCI may be a component of — presented as a **testable
  vision** with a defined computational measurement protocol and pre-stated falsification
  tests, most of which reuse the pipeline we already built. It is deliberately labeled
  hypothesis, not result, to avoid over-claim — which is itself the credibility posture
  that makes the whole project defensible.

**One-line framing:** *The Conditional Controllability Invariant is the control axis of a
broader latent property — Tissue Synapse Capacity — and it holds exactly where cell state
is built from the capacity to synapse with the tissue.*
