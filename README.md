# ISCI — Immune-State Controllability Index

**Built with Claude: Life Sciences** hackathon (Researcher Track) — genome-scale Perturb-seq in primary human CD4+ T cells → separating genes that *control* T-cell state transitions from genes that are merely *associated* with them.

> **Build environment:** Claude for Life Sciences (CPU-local, Mac 24GB). MIT open source.
> Every result below was produced during the event; all analysis code is timestamped in the commit history.

## The result, in one sentence

**Among perturbations with the same effect magnitude, known T-cell-state regulators produce effects that are more *state-specific* (concentrated on a functional axis) and more *reproducible across donors* — a signal orthogonal to effect size that nearly doubles regulator recovery (AUPRC 0.41 → 0.64, bootstrap gain +0.23 [95% CI 0.07–0.40], P>0 = 99.6%).**

![Central result](outputs/fig_central.png)

## Why this is the headline (and what we discarded to get here)

The original design was a five-component product `ISCI = R·S·geomean(M,D,A)`. Run honestly on the real data, it **failed three times**, and the failures were informative:

1. **The full index lost to a trivial effect-magnitude baseline** under expression-matched negatives (AUPRC 0.35 vs 0.41; AUROC 0.72 vs 0.83 — magnitude ahead on both).
2. **Network influence (PageRank/in-degree) added nothing** over magnitude, even though PageRank is orthogonal to it (ρ ≈ 0.00).
3. **The clinical bridge did not predict CAR-T response** at the patient level (CV-AUROC ≈ 0.53).

The common cause: **the ground truth is confounded by magnitude.** Known regulators have ~99× more differential-expression effect than non-regulators (Mann–Whitney p = 2.6e-10), so *any* test of "index vs magnitude" is rigged — magnitude wins by construction.

**The fix is a conditional test, not a better index.** Asking *"does a feature add signal **conditional on** magnitude?"* instead of *"does it beat magnitude?"* reveals a genuine, magnitude-independent controllership signal:

| Component | What it measures | Adds over magnitude? |
|-----------|------------------|----------------------|
| **axis-specificity** (residualized) | effect concentrated on a state axis vs diffuse | **yes** — LR p < 1e-4 |
| **cross-donor coherence** (residualized) | same direction across donors | **yes** — LR p < 1e-4 |
| effect magnitude | n. downstream DE genes | (the confound) |
| network influence (PageRank, in-degree) | structural position | no |
| guide coherence | same direction across guides | no |

**Robustness:** survives removing regulators that are also axis markers (not leakage); replicates on independent structural positives (ARID1A/INO80/IKZF1, p = 0.013); replicates in **all three** culture conditions (Rest / Stim-8h / Stim-48h, all p < 1e-3).

**The methodological contribution stands on its own:** in-dataset controllability benchmarks are confounded by effect magnitude, and only a magnitude-conditional test (or a magnitude-independent external outcome) can distinguish control from association. This is a reusable caution for the field.

## Deliverables

| Artifact | What it is |
|----------|------------|
| [outputs/fig_central.png](outputs/fig_central.png) | Central figure — orthogonal signal vs magnitude, bootstrap CIs |
| [outputs/isci_final_ranking.csv](outputs/isci_final_ranking.csv) | 2,520 genes ranked by magnitude-independent controllership signal (`ISCI_orthogonal`), gated on detectable effect |
| [outputs/evidence_cards.md](outputs/evidence_cards.md) | Top-15 candidate controllers, each claim tagged by evidence level + PubMed citations with auto-assessed relevance |
| [outputs/d4/](outputs/d4/) | CAR-T clinical bridge (honest negative + Treg-composition signal) |
| [outputs/network_influence.csv](outputs/network_influence.csv) | Causal intervention-graph influence metrics |
| [outputs/manifest_d0.json](outputs/manifest_d0.json) | Reproducibility manifest (data SHA-256, env, git-SHA, seeds) |

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/execution_plan.json](docs/execution_plan.json) | **Approved phased plan** from Claude Science (D0–D4) |
| [docs/method.md](docs/method.md) | ISCI spec with C1–C8 peer-review fixes |
| [docs/benchmark.md](docs/benchmark.md) | LOO ablation design + ground-truth tiers |
| [docs/related_work.md](docs/related_work.md) | Literature, datasets, connectors |
| [docs/plan.md](docs/plan.md) | Full strategic plan (D0–D6) |
| [docs/claude_science_prompt.md](docs/claude_science_prompt.md) | Master prompt (initial critique; fixes now in method.md) |

## Primary data (not in git — download locally)

```bash
aws s3 cp --no-sign-request \
  s3://genome-scale-tcell-perturb-seq/marson2025_data/GWCD4i.DE_stats.h5ad \
  data/

aws s3 cp --no-sign-request \
  s3://genome-scale-tcell-perturb-seq/marson2025_data/GWCD4i.pseudobulk_merged.h5ad \
  data/
```

## Setup

```bash
uv sync   # Python 3.11+, or: pip install -e .
```

## Reproduce

```bash
python scripts/run_d0.py          # loads DE_stats, builds LOO axes, ranks genes
# conditional test + bootstrap + figure: see notebooks/ and outputs/
```

Every output carries a provenance stamp (data SHA-256, conda env, git-SHA, seed) via `isci.repro`.

## Package layout

`isci/` — `io` (backed AnnData + SHA-256 manifest) · `axes` (leave-one-out axis construction) · `movement` (M, NES-style enrichment) · `qc` (Q, on-target validity) · `repro` (R, cross-donor/guide reproducibility) · `network` (causal intervention graph, influence scores) · `index` (rank-product / residualized aggregation) · `baselines` (DE-magnitude, effect-size, centrality) · `validate` (expression-matched negatives, AUPRC/AUROC, conditional LR) · `evidence` (PubMed-cited evidence cards).

## Expansion: T-REMAP (reverse-mapping clinical modules)

Built **on top of** the locked core (see [reports/result_lock.md](reports/result_lock.md)),
T-REMAP inverts the failed clinical-bridge question. Instead of "does a controller predict
response?", it asks "which perturbations push T cells *away from* clinical resistance
programs and *toward* sensitivity programs?"

- **Movability gate** ([outputs/movability_gate.json](outputs/movability_gate.json)) — all 6
  clinical modules pass: their member genes ARE moved by perturbations (57–100% responsive),
  unlike the D4 mean-signature that failed.
- **ClinicalReversalScore** = mean-z(sensitivity modules) − mean-z(resistance modules) per
  perturbation. Permutation null **p = 0.001**; only weakly magnitude-dependent (ρ = 0.18).
- **Heatmap** ([figures/module_reversal_heatmap.png](figures/module_reversal_heatmap.png)) —
  top candidates × 6 modules. Non-obvious hits (KDM1A, CREBBP, GATA3) reverse specific modules
  without being generic activation knobs; TCR-signaling hits are flagged as a likely
  activation-axis artifact. See [reports/t_remap_expansion.md](reports/t_remap_expansion.md).

Hypothesis-generating, not a target call — the caveats in the report are load-bearing.

## Multi-omic expansion: two layers of T-cell controllability

Built on the locked core, the expansion tests whether the controllers hold up under
harder statistics and external cohorts. The headline that emerges:

> **T-cell controllership has two layers: a known TCR-signal-strength rheostat, and a
> magnitude-independent layer of reproducible, axis-specific state controllers.**

- **Statistical rigor** ([reports/mechanism_cards_v2.md](reports/mechanism_cards_v2.md),
  [outputs/family_enrichment_matched_null.csv](outputs/family_enrichment_matched_null.csv)):
  family enrichment tested against **two matched nulls** (with/without TCR-shutdown). Honest
  negative — chromatin/tx is nominal in the TCR-free null (fold 1.46, p=0.024) but attenuates
  once TCR is controlled and **nothing survives FDR**. The families are a chromatin-leaning
  description, not an over-represented signal.
- **Confounder ledger v2** ([outputs/confounder_ledger_v2.json](outputs/confounder_ledger_v2.json)):
  ISCI_orthogonal stays clean against all nine confounders (stress, cell-cycle, mitochondrial,
  IFN added; max |ρ| = 0.10) — the core is confounder-robust.
- **TCR reframe** ([reports/tcr_reframe.md](reports/tcr_reframe.md),
  [figures/tcr_reframe_convergence.png](figures/tcr_reframe_convergence.png)): the raw T-REMAP
  axis recovers the TCR signaling machinery (the rheostat); after full residualization only
  7/20 reversers survive (IRF2BP1, MED13, PDCD10, CXXC1 robust). TCR signal strength is a
  biological rheostat **and** a translational confounder — literature-anchored (dasatinib/rest
  Weber 2021 PMC8049103; LCK Wu 2023 PMID 36696897; Regnase-1 recovered independently).
- **External direction validation** (patient-level gate, direction-only, no predictor):
  - **CAR-T GSE208052** (n=9 scRNA) — sensitivity axis replicates (R_memory_stem p=0.032); resistance does not.
  - **CAR-T GSE223655** (bulk, gate passed 33 CR/32 PD) — **R_memory_stem replicates robustly**
    (CD8+CAR product p=0.0043, positive in all 6 sorted fractions of the 12-patient pool).
    Two independent studies now agree on the memory-stem sensitivity axis.
  - **Compartment hypothesis:** sensitivity is CAR-T-product-visible; resistance appears
    post-infusion / niche-dependent.
- **Targetability triage** ([outputs/protein_targetability_matrix.csv](outputs/protein_targetability_matrix.csv)):
  70 candidates annotated (protein class, localization, druggability), with a
  `translation_triage_score` and a mandatory `intervention_direction` column — explicitly a
  hypothesis-generating layer **separate from** the validated core, not a therapeutic target call.

Roadmap for the parts that need more compute or tissue:
[phospho + spatial](reports/phospho_spatial_roadmap.md),
[compute volumetria](reports/compute_volumetria.md),
[literature gaps](reports/literature_gaps_roadmap.md).

## Limitations & future work

- **Clinical bridge is a negative result.** T-state signatures do not predict CAR-T response in the current cohort (n = 70 infusion products); only Treg composition is suggestive (uncorrected p = 0.04). Needs a larger, magnitude-independent outcome cohort.
- **External validation is direction-only, small-N.** Two CAR-T cohorts (GSE208052 n=9, GSE223655 33 CR/32 PD) confirm the *direction* of the memory-stem sensitivity axis (one-sided, uncorrected, no AUROC); this is replication of direction, not a validated response predictor. Resistance-axis validation (GSE197268, post-infusion) is gated on patient-level labels.
- **Family enrichment is a statistical negative** with broad GO/Reactome sets — the mechanistic families are descriptive, not FDR-significant.
- **Chromatin layer (borzoi/evo2 on top controllers)** was scoped as cut-first stretch and not reached.

## Author

Abel Costa — hematologist / onco-hematologist, IDOR (São Paulo)

## License

MIT — see [LICENSE](LICENSE).
