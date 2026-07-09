# Phase 10 — signed perturbation graph (network done right)

The README already established that PPI/PageRank centrality adds nothing over magnitude, so
network centrality is **out of the core**. This phase replaces it with the right object: a
**perturbation-derived signed graph** — each perturbation (gene KD) → the signed effect it has
on each functional module — and asks a causal question, not a topological one: *which
controllers move persistence / killing / exhaustion / Treg modules coherently in the therapeutic
direction?* This is a mechanistic overlay, explicitly **not** a primary controllership score.

## Construction
- **Edges:** signed module effect = mean z (Stim48hr `zscore` layer) of a module's movable
  member genes, per perturbation. Matrix: 11,281 perturbations × 6 modules
  (`outputs/pert_module_signed_matrix.parquet`).
- **Therapeutic direction (pre-registered):** R_memory_stem / R_migration / R_killing should go
  **up**; NR_exhaustion / NR_Treg / toxicity_infl should go **down**.
- **Therapeutic convergence** = mean over modules of (signed effect × desired direction);
  **coherence** = how many of the 6 modules move the right way.

## Result — convergence is a THIRD, independent axis
Therapeutic convergence is only weakly correlated with controllership (Spearman vs
`ISCI_orthogonal` ρ=+0.24) and with magnitude (ρ=+0.18). It is **not redundant** with either:
controllership asks *whether* a gene controls state, convergence asks *in which direction*, and
magnitude asks *how large*. Three separable pieces of information.

![Signed perturbation→module graph, top-20 controllers](figures/signed_perturbation_graph.png)

**Reading (top-20 controllers, ordered by convergence):**
- **GATA3\*** (+1.70) and **RCOR1** (+0.90) are the most therapeutically convergent controllers
  — push memory/stem and migration up while lowering Treg/exhaustion. GATA3 is a known Th2
  regulator (external corroboration).
- **IRF1\*** — the #1 controllership gene — has *negative* convergence (−0.21): a strong,
  reproducible controller whose net module effect runs against the therapeutic direction. This
  is exactly why the two axes must stay separate: high controllership does not imply a desirable
  intervention.
- **PRKDC** and **STAT6\*** load heavily on the killing module specifically — consistent with the
  BEHAV3D finding that killing is a distinct axis from persistence.

## Scope honesty
- The graph is a **mechanistic hypothesis overlay**, not a ranking method. Convergence is a
  *direction* annotation on already-locked controllers, not a new controllership claim.
- Because convergence carries a mild magnitude correlation (ρ=+0.18), it is reported as a
  descriptive overlay, never as a magnitude-independent result — that role belongs only to
  `ISCI_orthogonal`. Artifact: `outputs/pert_module_convergence.csv`.
- CEFCON / CellOracle are the conceptual comparators (GRN + network control); our differentiator
  is that these edges are **causal perturbation effects**, not inferred GRN topology.
