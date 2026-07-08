# Benchmark & Ablation Design — ISCI

> Central figure for **Depth (20%)** and **Demo (30%)**. Companion to `method.md` and `docs/execution_plan.json`.
> **Revision:** incorporates fixes C1–C8 (Jul 7, 2026 peer review).

## Question

Under **leave-one-out axis construction**, does ISCI recover known T-cell **controllers** better than baselines, and does each component (D, A, residualized S) add measurable signal?

---

## C1 — Leave-one-out axes (non-negotiable)

Ground-truth genes (FOXO1, TCF7, TOX, BACH2, …) appear in `config/axes.yaml` marker sets. Scoring them on axes they define is **circular**.

**Rule:** when scoring gene `g`, rebuild every axis signature **without** `g`. Report **all** headline AUROC/AUPRC only under LOO.

---

## Ground truth (C2)

### Primary positives (headline claim)

Independently curated from literature — **not** derived from Marson polarization model:

FOXO1, TCF7, TOX, TOX2, NR4A1, NR4A2, NR4A3, BATF3, IKZF1, ETS1, ARID1A, INO80, BACH2, ID3, PRDM1, IRF4

Sources: Belk 2022, FOXO1 Nature 2024, Zhang Nature 2023, Haradhvala 2022, Marson mechanistic follow-ups.

### Secondary positives (confirmation only)

`known_regulators=True` in Marson supplementary  
`polarization_prediction_condition_comparison_regulator_coefficients.csv`

**Report separately.** State in write-up: labels derived from same dataset → weaker external test.

### Negatives

- **Expression-matched** non-controllers via GTEx (`mcp-expression`) — fixes "easy negatives" problem
- High `n_total_de_genes` / `n_downstream` without control evidence
- Housekeeping genes (GAPDH, ACTB, …) with high perturbation magnitude

---

## Metrics

| Metric | Use |
|--------|-----|
| AUROC | Recovery of primary clinical positives (LOO) |
| AUPRC | Positives are rare (~15–50 genes) |
| Precision@k | k = 20, 50 — clinical actionability |
| Rank correlation | Marson → Frangieh/Belk/Schmidt transfer |

---

## Baselines (increasing difficulty)

1. **DE magnitude** — `n_total_de_genes` or mean `|zscore|`
2. **Effect size** — `n_downstream`, `ontarget_effect_size`
3. **Centrality-only** — PageRank on connector-grounded GRN
4. **pert2state_model** — Marson linear regression (Fig. 4) — **must-beat baseline**

All baselines evaluated under **same LOO axis protocol**.

---

## Ablation curve (central demo figure)

Compare AUROC/AUPRC:

| Model | Description |
|-------|-------------|
| ISCI-full | M + R + D + A + S (residualized) |
| ISCI − D | Drop structural control |
| ISCI − A | Drop pert2state concordance |
| ISCI − S | Drop stability |
| ISCI M+R | D0 minimum |
| Each baseline | Alone |

**Expected (honest):** full ISCI > pert2state > DE magnitude on primary positives; residualized S adds incremental AUPRC beyond M; raw S would not (C3).

Include **cross-donor** and **cross-condition** holdout panels if space allows.

---

## Robustness checks

- **Holdout ground-truth:** any learned weights fit without canonical controllers in training fold
- **Cross-donor:** train ranking on 3 donors, evaluate on 4th
- **Cross-condition:** Stim8hr → Rest/Stim48hr (report context-specificity)
- **Weight sensitivity:** R weights w1 ∈ {0.3, 0.5, 0.7}; geomean ε ∈ {1e-4, 1e-3, 1e-2}

---

## External transfer (D3)

Priority order (feasibility):

1. **Frangieh** — `pertpy` `pt.data.frangieh_2021` (zero download friction)
2. **Belk 2022** — Gladstone tie-in (ARID1A/INO80); GEO via `mcp-omics-archives`
3. **Schmidt 2022** — CRISPRa/i primary T

Metric: rank correlation of controllability; recovery of dataset-specific hits vs DE bruto.

---

## Clinical bridge (D4)

### Step 1 — Phenotype floor (minimum acceptable result)

Project ISCI controllability signature onto **Functional CAR-T atlas** (Zenodo 10.5281/zenodo.17213452) using **precomputed scVI-hub latent**.

Verify separation: exhaustion-like vs memory/stem-like phenotypes (11 atlas phenotypes). Correct for study/batch (13 studies).

This figure **must land** even if outcome data are weak.

### Step 2 — Outcome test (stretch)

Only after phenotype floor: responder vs non-responder AUROC with study as covariate/holdout.

Benchmark: TCF7/FOXO1-regulon reference. Secondary: Haradhvala GSE197268 or Deng GSE151511 if time.

Report underpowered results honestly.

---

## Null models (C6)

Do not use a single label permutation for all components. See `method.md` §5.

---

## Reporting rules

- Separate **hypothesis generated** from **evidence supported**
- Evidence cards: **PubMed + Open Targets + literature-review** (Claude Science) — not Consensus
- No hallucinated citations
- Demo spine: **ablation figure** + **one live evidence card** + phenotype-floor or outcome plot

---

## Peer-review fix checklist

| ID | Issue | Fix | Status |
|----|-------|-----|--------|
| C1 | Axis/ground-truth overlap | LOO axes | Specified |
| C2 | Marson-native labels circular | Clinical primary, Marson secondary | Specified |
| C3 | Raw S ≈ magnitude | Residualize via shesha-geometry | Specified |
| C4 | Geomean zeros genes | ε floor on geomean | Specified |
| C5 | Binary driver set unstable | Continuous influence D | Specified |
| C6 | Single null invalid for D,S | Component-appropriate nulls | Specified |
| C7 | A too costly | pert2state only; descope GEARS/CellOracle | Specified |
| C8 | New work only | Event-timestamped commits; stubs only pre-event | Specified |
