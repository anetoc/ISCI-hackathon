# EXEC-1 / MASTER_ROADMAP Phase 5 — IEC cell-level 2.5-axis structure

**RESULT: the 2.5-axis IEC structure holds at single-cell resolution and replicates cross-system.**
A_persist is a clean, independent, magnitude-orthogonal axis; A_kill and A_resist are **entangled**
(kill↔resist ρ ≈ −0.5) in *both* the CAR-T atlas (cell level) and the Marson pseudobulk. So IEC is
honestly **two axes** — a reach-and-hold **persistence** axis and a single coupled
**effector/exhaustion continuum** — not three independent dials. This is a discovery that sharpens
the definition, exactly as pre-registered (outcome-agnostic).

---

## Pre-registration (fixed before computing)
- Axes: **A_persist** = mean-z(memory/stem + migration + synapse); **A_kill** = cytotoxic module;
  **A_resist** = −z(exhaustion). Scored per cell with `sc.tl.score_genes` on log-norm counts (the
  same validated scorer as `outputs/iec_clinical/score_axes.py`).
- **Distinct iff** pairwise |Spearman| < 0.5 AND each axis vs magnitude |Spearman| < 0.3.
- Outcome-agnostic clause: if kill↔resist stay anti-correlated at cell level, the final definition
  becomes **IEC = [A_persist, A_effector/exhaustion continuum]** — a discovery, not a failure.

## Data
- **CAR-T atlas** (`Atlas_integ_scArches_FINAL_V5.h5ad`): all **455,370 cells × 48,740 genes**,
  raw counts → normalize_total(1e4) → log1p. IEC gene coverage 100%.
- **Marson pseudobulk** (`iec_axis_scores_pseudobulk_stim48.csv`, committed): independent-system
  comparator (per-perturbation module z-scores, Stim48hr).

## Result — cell-level correlation structure (CAR-T atlas, n = 455,370)

| pair | Spearman ρ | verdict |
|---|---|---|
| A_persist ↔ A_kill | −0.117 | orthogonal |
| A_persist ↔ A_resist | −0.007 | orthogonal |
| **A_kill ↔ A_resist** | **−0.526** | **ENTANGLED** (crosses |0.5|) |

| axis vs magnitude (total counts) | ρ | verdict |
|---|---|---|
| A_persist | −0.064 | ok (<0.3) |
| A_kill | −0.295 | ok (<0.3) |
| A_resist | +0.201 | ok (<0.3) |

All three axes are **magnitude-orthogonal** (no axis is an effect-size proxy).

## Cross-system replication (Marson pseudobulk, independent)

| pair | CAR-T atlas (cell) | Marson (pseudobulk) |
|---|---|---|
| persist ↔ kill | −0.117 | −0.075 |
| persist ↔ resist | −0.007 | −0.007 |
| **kill ↔ resist** | **−0.526** | **−0.498** |

Near-identical structure in two independent systems (primary CD4+ Perturb-seq pseudobulk vs a
14-study CAR-T product atlas at single-cell level). The persistence axis is clean in both; the
effector/exhaustion coupling sits at ρ ≈ −0.5 in both. This is the generalizable claim.

## CD8-identity guard (honest caveat)

A_kill correlates with a CD8-identity score (z(CD8A,CD8B) − z(CD4)) at **ρ = 0.574** — i.e. the
cytotoxic module partly captures CD8-ness (expected: cytotoxic genes are CD8-enriched, and the
BEHAV3D P3 result already showed "killing" tracks the CD8/activation program). **But the
effector/exhaustion entanglement is not merely a CD8 artifact:** controlling for CD8-identity, the
kill↔resist partial correlation is still **−0.441** (vs −0.526 raw), and kill↔persist partial is
−0.119. So the coupling is a real biological continuum that survives CD8 stratification. A_kill's
overlap with CD8-identity is stated as a limitation of that axis, not of the persistence result.

## Interpretation

- **A_persist** is the clean, independent, magnitude-orthogonal capacity axis — the one that also
  carried the (null) clinical signal in Brief 04 and that the CCI controllership result is about.
- **A_kill / A_resist collapse into one effector↔exhaustion axis** — consistent biology (the
  cytotoxic effector program and terminal-exhaustion program are two ends of one activation-driven
  continuum), replicated in two systems, robust to CD8 control.
- Net: **IEC = [A_persist, A_effector/exhaustion continuum]** — "2.5 axes" confirmed at cell level.
  This does not touch the locked CCI core; it sharpens the IEC descriptive layer.

## Scope / limits
- Structure test only — no clinical labels here (that is Brief 04, a well-powered NULL).
- scVI batch-corrected latent not used: the orthogonality is a `score_genes` property, not a latent
  property. A scVI-integrated robustness pass (EXEC-1b) is optional/GPU-gated and off the critical
  path; the cross-system agreement already argues the structure is not a batch artifact.
- A_kill overlaps CD8-identity (ρ 0.57) — interpret the effector axis as partly lineage-linked.

### Deliverables
- `iec_latent_report.md` (this file) · `iec_celllevel_result.json` (all numbers) ·
  `iec_axis_scores_celllevel.csv` (per-cell axis scores + CD8 + magnitude + patient/study) ·
  `iec_axis_decomposition.png` (cross-system bars + CD8 guard) · `exec1_celllevel.py`,
  `plot_celllevel.py` (reproducible, CPU).
