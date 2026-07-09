# RESULT LOCK — ISCI core (frozen for submission)

**Status: FROZEN.** Do not change the primary ranking or its definition unless a
reproducibility bug is found. The T-REMAP expansion builds *on top of* this lock;
it must not overwrite it.

_Locked: 2026-07-08. Core commit: `32e991b` (see `git log`)._

## Primary deliverable

| Field | Value |
|-------|-------|
| **Primary score** | `ISCI_orthogonal` |
| **Definition** | mean of magnitude-**residualized** percentiles of (axis-specificity, cross-donor coherence) |
| **Eligibility** | `detectable_effect == True` (perturbation effect magnitude ≥ dataset median n-DE) |
| **Decorrelation from magnitude** | Spearman ρ = +0.02 (orthogonal by construction) |
| **Regulator recovery (detectable set)** | AUPRC 0.722 vs magnitude 0.415 |
| **Bootstrap gain (full residual set)** | +0.229 AUPRC, 95% CI [0.072, 0.405], P(gain>0) = 99.6% |
| **Ranking file** | `outputs/isci_final_ranking.csv` (md5 `5337113b682c38bd0c2d5755e2078520`) |
| **Central figure** | `outputs/fig_central.png` |
| **Evidence cards** | `outputs/evidence_cards.md` (v3, relevance-tagged) |

## Secondary / not-primary

- **`ISCI_combined`** — geomean of raw percentiles incl. magnitude. Effect-weighted,
  magnitude-dominated at the top. Kept in the CSV as a labeled secondary column; **not** the headline.
- **DEPRECATED: `rank_product(M_pos, Q, R)`** — the original D0 aggregator. It lost to
  DE-magnitude under expression-matched negatives (AUPRC 0.35 vs 0.41). Retained only in
  `outputs/manifest_d0.json` as the historical D0 run; **not** a final deliverable.

## The validated claim (exact wording — do not overstate)

> Among **canonical, axis-defining** T-cell state regulators, and among perturbations with a
> **detectable** effect, **axis-specificity and cross-donor coherence add information
> for regulator status beyond perturbation magnitude** (pre-specified incremental test
> M → M+C: gain +0.357 [+0.117, +0.538], P>0 = 1.000, expression-matched negatives).
> The signal replicates across all three culture conditions.

**Scope boundary — established by later negative tests, NOT future work:**
- The gain does **NOT** survive removing the four axis-defining master TFs (GATA3/TBX21/STAT6/IRF1):
  point gain drops to near zero (underpowered at n=9, but a real bound).
- On an **independent external functional-regulator set** (20 non-marker regulators, Shifrut/Schmidt/Belk),
  the orthogonal score **LOSES to magnitude** (ΔAUPRC −0.281 [−0.476, −0.073], CI excludes 0).
  → The property is specific to canonical axis-defining regulators, NOT broad functional regulators.

**NOT claimed:** a broad functional-regulator discovery engine; universal clinical resistance
mechanisms; CAR-T response prediction (that bridge was a cross-study negative with residual
uncertainty, not a proof of no effect); that ISCI beats magnitude *globally* (the point is
conditional-on-magnitude, not versus); a demonstrated cross-system "invariant" (systems' CIs
overlap; no formal heterogeneity test).

## Top-15 candidate state-shift controllers (primary rank)

Recovered known regulators (sanity check): **IRF1 (#1), STAT6 (#8), SETDB1 (#11), GATA3 (#14).**
Novel nominations (not in label set): **IKBKB (#2, NF-κB), BCLAF1 (#3), TFAP4 (#4), CYB561D2 (#5),
PDCD5 (#6), ZC3H12A (#7, Regnase-1), RCOR1 (#9), PRKDC (#10), TWF1 (#12), HEXIM1 (#13), SAMD1 (#15).**

Sell as *candidate state-shift controllers under a magnitude-controlled criterion* — not as
"therapeutic targets ready for engineering."

## Known limitation (must appear, not hidden)

Positives are few (12–21 depending on set). The signal is bootstrap-stabilized and
cross-condition-replicated. The fully independent external positive set **has now been tested and the
signal FAILED against magnitude** (see scope boundary above) — the property is bounded to canonical
axis-defining regulators, not the broad functional-regulator class. Cross-condition "replication" is
across correlated conditions of the *same* dataset, not independent cohorts.
