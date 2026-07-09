# Phases 8–9 — curated mechanism enrichment + experimental triage board

Two CPU-local phases from the roadmap, both about turning the locked ranking into *interpretable
mechanism* without overclaiming. Neither touches the locked core.

## Phase 8 — curated gene-set enrichment along the continuous score

**Why not GO/Reactome:** broad GO families are too wide for small T-regulator sets and nothing
survived FDR in the earlier top-50 family analysis. Instead we pre-registered **6 narrow,
T-cell-relevant curated sets** and tested **rank-based enrichment along the continuous
`ISCI_orthogonal` score** (Mann-Whitney of set members vs rest, over 2,520 genes) — not a top-N
cut. Crucially, every set is **also** tested against magnitude, so we can separate
controllership from effect size.

**Result (4 of 6 sets survive BH-FDR on controllership):**

| Curated set | median ISCI pctile | ISCI q (BH) | magnitude p | Interpretation |
|---|---|---|---|---|
| TCR-proximal / phospho | 0.86 | 9e-5 | 2e-8 | controller **and** high-magnitude → the rheostat / positive control |
| chromatin modifiers (T) | 0.86 | 2e-4 | 4e-3 | controller, also elevated magnitude |
| **Treg / brake / apoptosis** | 0.92 | 8e-3 | **0.39 (n.s.)** | **magnitude-independent controller** |
| **NF-κB activation** | 0.82 | 0.017 | **0.35 (n.s.)** | **magnitude-independent controller** |
| cytoskeleton / synapse | 0.52 | 0.22 | 5e-3 | high-magnitude, not a specific controller |
| RNA-decay brakes | 0.33 | 0.78 | 7e-3 | high-magnitude, not a specific controller |

![Curated enrichment: controllership vs magnitude](figures/curated_enrichment.png)

**The clean finding:** **NF-κB activation** and **Treg/brake/apoptosis** are enriched in
controllership (`ISCI_orthogonal`) but **NOT in magnitude** — these are the families where high
CCI is *not* an effect-size proxy. TCR-proximal and chromatin enrich in both (TCR is the
expected high-effect rheostat / positive control — enrichment there validates the pipeline sees
the activation axis, it is not a therapeutic call). Cytoskeleton and RNA-decay are high-effect
but not axis-specific controllers. This is exactly the magnitude-vs-controllership separation
the method is built to make, now resolved at the level of curated mechanism.
Artifacts: `outputs/curated_enrichment_continuous.csv`, `outputs/curated_enrichment_magnitude_guard.csv`.

## Phase 9 — targetability as a 4-category experimental decision board

The targetability matrix (70 genes) is recast into a **safety-first experimental triage board**
— a decision aid for *which experiment*, never a therapeutic recommendation. Assignment rule
is transparent and dangerous flags override everything.

| Category | n | What it means | Top members (by triage score) |
|---|---|---|---|
| **A — manufacturing modulation** | 24 | titratable/transient in manufacturing (epigenetic/reverser); NOT systemic inhibition | KDM1A, CXXC1, RCOR1, PPP1R15B, SAMD1 |
| **B — engineering candidates** | 6 | clear KD/OE direction, viability-safe; need expansion/killing/persistence assays | MAP3K5, IRF2BP1, INPP5D, NR4A3, ARHGAP30 |
| **C — probe-only biology** | 18 | understand mechanism, not a target | BCLAF1, HEXIM1, PDCD5, STAT6, CYB561D2, TWF1 |
| **D — dangerous / positive-control rheostats** | 22 | TCR-proximal, broadly-essential, oncogenic-risk → axis controls or titrated only | IKBKB, PRKDC, MED13, CDC25B |

**The overclaim guard, made structural:** the genes a naive reader might call "targets" —
**IKBKB, PRKDC** — land in **Category D (dangerous)**, because IKBKB is TCR-proximal and PRKDC
is broadly essential. The board makes the safe reading the default one: no candidate is a
patient-facing therapeutic; the highest-priority ones (Category A) are **titratable
manufacturing/experimental perturbations**. Artifact: `outputs/targetability_decision_board.csv`.

## Scope honesty
- The curated enrichment is a **mechanistic prioritization**, not a claim of causal family
  membership — the sets are hypotheses, tested continuously and magnitude-guarded.
- The board is **hypothesis-generating triage**, explicitly separated from the locked CCI result
  and carrying no therapeutic recommendation.
