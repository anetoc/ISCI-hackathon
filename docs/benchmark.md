# Benchmark & Ablation Design — ISCI

> Central figure for **Depth (20%)** criterion. Companion to `method.md` §6–7 and `plan.md` §14.

## Question

Does ISCI recover known T-cell state **controllers** better than baselines, and does each component (D, A, S) add measurable signal?

## Ground truth

### Positive set (two tiers — avoids circular curation)

1. **Dataset-native:** `known_regulators=True` in Marson supplementary table  
   `polarization_prediction_condition_comparison_regulator_coefficients.csv`
2. **Clinical/mechanistic curated:** FOXO1, TCF7, TOX/TOX2, NR4A1/2/3, BATF3, IKZF1, ETS1, ARID1A, INO80, BACH2, ID3, PRDM1, IRF4

### Negative set

- Housekeeping genes with high DE magnitude but no control evidence
- Genes with high `n_total_de_genes` / `n_downstream` but absent from positive sets
- Randomly sampled non-TF genes matched for expression level

## Metrics

| Metric | Use |
|--------|-----|
| AUROC | Overall recovery of positive controllers |
| AUPRC | Important when positives are rare (~10–50 genes) |
| Precision@k | k = 20, 50 — "are top nominations clinically actionable?" |
| Rank correlation | Cross-dataset transfer (Marson → Belk/Schmidt/Frangieh) |

## Baselines (increasing difficulty)

1. **DE magnitude** — `n_total_de_genes` or mean `|zscore|`
2. **Effect size** — `n_downstream`, `ontarget_effect_size`
3. **Centrality-only** — PageRank / out-degree on GRN without FVS/MDS
4. **pert2state_model** — Marson's own linear regression (Fig. 4); **honest strong baseline**

## Ablation curve (central figure)

Compare AUROC/AUPRC across:

- ISCI full (M + R + D + A + S)
- −D (drop structural control)
- −A (drop in-silico)
- −S (drop stability)
- M + R only (D0)
- Each baseline alone

**Hypothesis:** Each component increases AUPRC; S and D provide the largest jump over pert2state.

## Robustness checks (prevent leakage)

- **Holdout ground-truth:** fit any learned weights without canonical controllers in training set
- **Cross-donor:** rank on 3 donors, evaluate on held-out 4th
- **Cross-condition:** Stim8hr train → Rest/Stim48hr test (context-specificity is a feature, not a bug — report both)

## External transfer (D3)

Train ranking on Marson → test recovery of hits in:

- Belk 2022 (exhaustion CRISPR, Gladstone)
- Schmidt 2022 (CRISPRa/i in primary T)
- Frangieh Perturb-CITE-seq

Tool: `pertpy` Distance / Augur metrics on harmonized perturbation sets.

## Clinical bridge benchmark (D4 — optional gold)

Project per-sample **controllability signature** onto CAR-T cohorts:

- Haradhvala GSE151511 and/or Functional CAR-T atlas (Zenodo 10.5281/zenodo.17213452)
- Compare ISCI signature vs TCF7/FOXO1-regulon vs tcellMIL/SCENIC features
- Endpoint: responder vs non-responder separation (AUROC); report honestly if underpowered

## Reporting rules

- Separate **hypothesis generated** from **evidence supported** in clinical narrative
- Every top gene gets an evidence card: ISCI score + PubMed/Consensus + Open Targets link
- No hallucinated citations — connector-sourced only
