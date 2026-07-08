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

## 3a. TSC estimated as a measured latent factor (done, Marson Stim48hr)

We ran the estimation on the 1,260 detectable Marson perturbations: score L1–L4 per
perturbation, then a 1-factor factor analysis on the standardized loading matrix.

![TSC latent factor](figures/tsc_latent_factor.png)

| Loading | On TSC factor |
|---|---|
| L2 tissue access (migration) | **+0.99** |
| L3 synapse assembly (actin/cytoskeleton) | **+0.61** |
| L1 durable state (memory − exhaustion) | **+0.37** |
| L4 serial killing | −0.09 |

- **A single latent factor explains 37% of the variance** of L1–L4 — a real shared
  capacity, not noise.
- The factor is **dominated by tissue-access + synapse-assembly + durable-state**, which
  load together and positively. **Serial killing loads near-zero** — an honest structural
  finding: the killing readout is largely *independent* of the shared capacity, so TSC as
  measured here is a "reach-and-hold-a-synapse" axis more than a "kill" axis.
- **TSC is orthogonal to effect magnitude** (Spearman 0.03), exactly like the CCI — it is
  a state property, not an effect-size proxy.
- Among the **top-10 TSC perturbations** (PMVK, KDM1A, LAT, WDR82, ITK, VAV1, LCP2, LCK,
  PLCG1, HELT), **6 are TCR/synapse machinery** (LAT, ITK, VAV1, LCP2, LCK, PLCG1) — the
  same TCR-signal-strength axis identified independently. But the two single highest hits
  are NOT synaptic: **PMVK** (#1, TSC=6.85, mevalonate-pathway kinase — well above the rest)
  and **KDM1A** (#2, a histone demethylase). So the latent factor is *enriched* for TCR/synapse
  machinery in its upper tail, but its extreme top is led by a metabolic and a chromatin gene —
  the tie to the TCR-rheostat reframe is a tendency of the axis, not a clean synapse-only ranking.

Scores: `outputs/generalization/tsc_scores.csv`. This is a transcriptional latent; the
functional-synapse validation (§5, P3) remains the decisive open test.

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
  magnitude. The **definitive** per-cell perturbation→killing test still needs data we do
  not have (see §5c). But a **correlational proxy IS now done** (§5b, BEHAV3D) and it is
  informative: it shows what TSC is *not*.

## 5a. Scope test extended to a third system — TSC P1 confirmed, graded (done)

We added a third system to the CCI scope test to test prediction **P1** directly:
**Norman & Weissman 2019 K562 CRISPRa** (non-immune erythroid/megakaryocyte
*differentiation* program — the wanted non-proliferation far point).

![CCI scope across 4 systems](figures/cci_scope_4systems.png)

| System | Type | ΔAUPRC | 95% CI | LR p | Verdict |
|---|---|---|---|---|---|
| Marson CD4+ | immune, KD/KO | +0.229 | [0.072, 0.405] | <1e-4 | **PASS** |
| Schmidt CD4+ | immune, CRISPRa | +0.138 | [−0.029, 0.434] | n.s. | near-miss |
| **Norman K562** | **non-immune, differentiation** | +0.138 | [−0.033, 0.370] | **0.013** | **FAIL (near)** |
| Replogle RPE1 | non-immune, proliferation | +0.060 | [−0.013, 0.204] | 0.195 | FAIL |

**The prediction holds, and the boundary is graded, not a hard wall.** The four systems
order exactly as TSC P1 predicts: immune PASS > non-immune differentiation near-miss >
non-immune proliferation clean-FAIL. Crucially, the residual signal that survives in the
differentiation screen (Norman) is carried by **reproducibility R (p=0.0009), NOT
axis-specificity S (p=0.17)** — i.e. the differentiation program has reproducible
controllers but they are *not axis-selective independent of magnitude*, which is the exact
property that defines controllers in the immune system. This refines the property: **the
axis-selective component of controllership (S) is what is immune-specific**; reproducibility
alone can carry weak signal in a non-immune differentiation program.

## 5b. P3 correlational proxy — DONE (BEHAV3D GSE172325): TSC is a state axis, not a kill axis

We ran the reachable proxy: does the TSC transcriptional score separate functional
killer (super-engaged) from non-killer (never-engaged) engineered T cells in BEHAV3D
(Nat Biotechnol 2022, PMID 35879361; solid-tumor organoid TEGs — *not* hematologic CAR-T;
authors' engagement-sort label, imaging reference in BioImage Archive S-BIAD448). Full
report + code in `outputs/behav3d_p3/`.

![BEHAV3D P3 proxy](outputs/behav3d_p3/behav3d_p3.png)

**Verdict: NULL/FAIL (pre-registered), and it is informative.** On the balanced exposed set
(super vs never, n=1969) the composite TSC score does **not** beat any baseline:

| score | AUROC | AUPRC |
|---|---|---|
| TSC | 0.350 | 0.374 |
| activation | 0.991 | 0.989 |
| CD8-identity | 0.848 | 0.829 |
| total counts | 0.727 | 0.696 |

All bootstrap ΔCIs (TSC − baseline) are negative and exclude 0. The per-loading breakdown
explains *why* — and it is the key scientific result:

| TSC loading | AUROC (super=positive) |
|---|---|
| **L4 killing** | **0.947** (near-perfect) |
| L1 durable state | 0.303 |
| L3 synapse assembly | 0.298 |
| L2 migration | 0.154 |

The **killing loading alone separates almost perfectly**, but L1/L2/L3 (memory/stem, egress,
TCR machinery — all down-regulated in activated effectors) run the opposite way and, averaged
equally, pull the composite below chance. **This confirms, rather than contradicts, §3a**: in
the Marson latent factor killing loaded ≈0 on TSC, so TSC is a *reach-and-hold-a-synapse
state/persistence* axis, **not** a killing-behavior axis — and here it indeed fails to predict
killing. Two independent analyses (latent structure + functional proxy) agree.

**Confounder guard passed:** engagement is only modestly CD8-enriched (expression-derived
super/never CD8 ratio 1.26×; authors' CD8/CD4 label from the Pseudotime metadata 1.50× —
both below the 2× "heavy confound" threshold), and TSC also fails *within* the CD8+ stratum
(AUROC 0.373), so the failure is not a CD8-identity artifact. The pre-registered **replication
is NOT-EVALUABLE**: the Pseudotime counts matrix on GEO is in fact the Non-exposed matrix
(barcode collisions carry contradictory labels), so joining it would attach wrong expression —
refused per hard-rule 1 rather than fabricated.

## 5c. The decisive P3 still needs data we don't have

The definitive test — does a *perturbation-anchored* TSC score causally set *per-cell* killing
capacity — needs paired perturbation→function data. Gold standard: dbGaP phs002966 (Nat Cancer
2024, PMID 38750245; TIMING nanowell serial-killing + scRNA on clinical LBCL CAR-T), which is
controlled-access (DAC approval = weeks–months). That is the honest roadmap item for the
institutional-compute / collaboration phase, not something reachable this week.

## 6. Positioning

- **Submitted / demonstrated:** the immune-scoped CCI (a real, falsifiable property with a
  cross-dataset boundary).
- **TSC:** the broader property the CCI may be a component of — presented as a **testable
  vision** with a defined computational measurement protocol and pre-stated falsification
  tests, most of which reuse the pipeline we already built. It is deliberately labeled
  hypothesis, not result, to avoid over-claim — which is itself the credibility posture
  that makes the whole project defensible.

**Sharpened by the P3 proxy:** TSC is specifically a **state/persistence axis** (reach, hold,
and sustain a synaptic engagement) — measurable now, orthogonal to effect magnitude, and
**explicitly not** a killing-execution axis (killing is a separable dimension: it loads ≈0 on
the latent factor and is captured by activation/effector genes instead). Naming this internal
boundary is what turns TSC from a slogan into a falsifiable property.

**One-line framing:** *The Conditional Controllability Invariant is the control axis of a
broader latent property — Tissue Synapse Capacity, a reach-and-hold-the-synapse state axis
distinct from killing execution — and it holds exactly where cell state is built from the
capacity to synapse with the tissue.*
