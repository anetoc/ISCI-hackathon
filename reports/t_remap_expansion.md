# T-REMAP — expansion: reverse-mapping clinical modules onto perturbations

**Status: expansion (built on the locked ISCI_orthogonal core).** This asks the
inverted question: instead of "does a controller predict response?", we ask
"which perturbations move T cells *away from* clinical resistance programs and
*toward* sensitivity programs?"

## Why this escapes the failure of the D4 clinical bridge

The D4 bridge tested whether **mean state-signature scores** predict CAR-T response
— it failed (CV-AUROC ≈ 0.53). T-REMAP does something different and better-posed:

1. **Movability gate (de-risking, `outputs/movability_gate.json`).** Before building
   anything, we checked whether the genes that *define* each clinical module are even
   moved by perturbations in the CD4+ data. **All 6 modules pass** (57–100% of member
   genes are responsive in Stim48hr, vs genome background) — unlike the D4 signature,
   the module target genes ARE reachable by perturbation.
2. **External-anchored labels.** Module composition comes from literature (movability-
   filtered); clinical polarity (resistance vs sensitivity) is anchored on the atlas
   differential-abundance direction — not re-derived from the weak signal being tested.

## Signed modules (movability-passed genes)

**Resistance (push cells OUT of these):** NR_Treg, NR_exhaustion, toxicity_inflammatory.
**Sensitivity (push cells INTO these):** R_memory_stem, R_migration_synapse, R_killing_activation.

## ClinicalReversalScore

For each perturbation `g` (Stim48hr): `reversal = mean_z(sensitivity modules) − mean_z(resistance modules)`.

- **Permutation null (1000×, shuffling module identity):** observed max\|reversal\|
  among top-10 = 4.45 vs null 95th-pct 1.98, **p = 0.001** — the reversal structure is
  not random module assignment.
- **Weakly magnitude-dependent:** Spearman(\|reversal\|, magnitude) = **+0.18** — far below
  the ~0.99-driven confound of the raw benchmark, so reversal is largely (not entirely)
  its own signal. A magnitude-residualized `reversal_resid` is also stored.
- Top candidates carry high `ISCI_orthogonal` (0.66–0.88), so they pass the controllership
  filter too.

## Result (top reversal candidates, detectable effect)

Leading genes: **PLCG1, LAT, LCP2, VAV1, CD247, CD3G** (TCR-proximal signaling),
**GATA3** (strong Treg-module reversal — consistent with Th2/anti-Treg biology),
**KDM1A, CREBBP, PMVK, KIFAP3**.

![reversal heatmap](figures/module_reversal_heatmap.png)

## Honest caveats (must read before interpreting)

- **These are KNOCKDOWN effect vectors.** A high reversal score means *knocking the gene
  down* shifts cells toward sensitivity. The therapeutic reading (inhibit vs engineer-in)
  depends on that sign and is **hypothesis-generating, not a target call.**
- **The TCR-signaling hits are likely partly an activation-axis artifact.** Knocking down
  PLCG1/LAT/VAV1/CD3G broadly reduces activation, which mechanically looks like "more
  memory-like, less terminal-effector." This is expected and does **not** by itself mean
  these are good therapeutic targets — flagged, not hidden.
- **The most interesting non-obvious hits** are the chromatin/transcription controllers
  (KDM1A, CREBBP, GATA3) that reverse specific modules without being generic activation
  knobs — these are the candidates worth following.
- Clinical polarity leans on a single atlas with a weak (p=0.04, uncorrected) Treg signal.
  External direction-replication (GSE216571 TCE / GSE208052 CAR-T) is the next gate.

## Artifacts

`results/module_reversal_scores.parquet` (11,281 perturbations × 6 modules + reversal/resid/ISCI),
`figures/module_reversal_heatmap.png`, `outputs/movability_gate.json`.
