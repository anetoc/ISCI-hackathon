# ISCI — Immune-State Controllability Index

**Built with Claude: Life Sciences** hackathon (Researcher Track) — a magnitude-conditional framework that *adjudicates* T-cell-state controllership: it separates genes that **control** state from genes whose effect is merely large, and — just as importantly — **maps where that separation holds and where it collapses** (into magnitude, protein layer, external gene sets, or cross-study clinical batch). The product is not a target list; it is a tested scope map. Anchored on genome-scale Perturb-seq in primary human CD4+ T cells.

> **Build environment:** Claude for Life Sciences (CPU-local, Mac 24GB). MIT open source.
> Every result below was produced during the event; all analysis code is timestamped in the commit history.

## The result, in one sentence

**Among perturbations with the same effect magnitude, known T-cell-state regulators produce effects that are more *state-specific* and more *reproducible across donors*: the authoritative pre-specified M→M+C test gains +0.357 AUPRC (0.539→0.896; 95% CI +0.117 to +0.538), and the fully refit leakage-free OOF estimate remains positive at +0.215 (95% CI +0.074 to +0.560; permutation p=0.010).**

The simpler ranking-quality view is AUPRC 0.415→0.722. The matched-negative three-condition
`C`-versus-`M` aggregate is +0.229 [0.072, 0.405]. These are different estimands, not interchangeable
versions of one number; the hierarchy is frozen in `reports/result_lock.md`.

![Central result](outputs/fig_central.png)

> **Interactive:** open [`docs/tctrl_live_demo.html`](docs/tctrl_live_demo.html) — a self-contained
> live decision board (Controller × Convergence map with per-gene hover, class distribution, top-12
> decision cards, the PASS/FAIL/NULL claim contract, and the threshold-stability proof). No server, no
> install; open in any browser.

> **Hackathon stage package:** open [`docs/hackathon_judge_demo.html`](docs/hackathon_judge_demo.html)
> for the deterministic 2:30 judge narrative, or use the committed Full-HD
> [`MP4 fallback`](demo_assets/hackathon/hackathon_fallback_2m30.mp4). Both are generated from the
> same frozen claim and timing manifests and run fully offline.

> **Medical-language presentation:** [`outputs/isci_hackathon_medical_deck.pptx`](outputs/isci_hackathon_medical_deck.pptx)
> explains the question, evidence, limits and Gladstone experiment with the project's real figures.
> See [`DELIVERABLE.md`](DELIVERABLE.md) for a plain-language map of the complete artifact.

## What the framework actually delivers — an adjudication table

The deliverable is not the ranking; it is a system that returns an honest verdict for each question,
including the ones where the answer is *no*:

| Question | Verdict |
|----------|---------|
| Does the signal recover canonical regulators in the Marson CD4+ RNA anchor? | **PASS** (AUPRC 0.415→0.722) |
| Is it independent of effect magnitude? | **Yes**, in the anchor (Spearman +0.02) |
| Is this just "Shesha for T cells"? | **No** — Shesha's coherence tracks magnitude (ρ=0.97); ours is orthogonal (R 0.008, S 0.19) |
| Does it generalize to broad external functional regulators? | **FAIL** (ΔAUPRC −0.281; those are magnitude-visible) |
| Does it hold at the protein layer? | **FAIL** (direction-aware; inverted residual on coarse ADT) |
| Does any axis predict CAR-T clinical response? | **NULL** (well-powered; study-out 0.533, CD8-frac beats all) |
| Is a controller a therapeutic target? | **No** — convergence is a separate axis (IRF1 = #1 controller, wrong direction) |
| Are there magnitude-independent mechanisms to prioritize? | **Yes** — NF-κB and Treg-brake enrich in controllership, not magnitude |

That table — where control exists, where it collapses, and where a translational claim would
overreach — is the contribution. A good scientific agent knows when *not* to call PASS.

## What is NOT claimed

To keep the scope honest and legible:

- **Not a validated clinical biomarker.** No axis predicts CAR-T response under honest cross-study CV — that test returned a well-powered null (§ clinical), and nothing here is medical advice.
- **Not a therapeutic recommendation.** Controllership ranks *where the axis is steerable*, not what to give a patient; the drugability layer is experimental triage, not a treatment list.
- **Not a magnitude-conditional PASS for every layer.** The full protein-level CCI was run and returns an honest **FAIL** — magnitude-independence is an RNA/cross-donor property that collapses onto magnitude on a coarse surface-protein panel; the tensor carries it as a tested FAIL slice, not a PASS.
- **Not proven beyond canonical regulators.** The gain attenuates when axis-defining master TFs are removed from the (small, n≈13) positive set — an underpowered, honestly-reported limitation, not a demonstrated null.
- **Not a formal pre-registration.** "Pre-specified" means criteria were fixed in code before the adjudicated result was computed, not filed on an external registry.

## Why this is the headline (and what we discarded to get here)

The original design was a five-component product `ISCI = R·S·geomean(M,D,A)`. Run honestly on the real data, it **failed three times**, and the failures were informative:

1. **The full index lost to a trivial effect-magnitude baseline** under expression-matched negatives (AUPRC 0.35 vs 0.41; AUROC 0.72 vs 0.83 — magnitude ahead on both).
2. **Network influence (PageRank/in-degree) added nothing** over magnitude, even though PageRank is orthogonal to it (ρ ≈ 0.00).
3. **The clinical bridge did not predict CAR-T response** — tested as a **well-powered null** on the Functional CAR-T atlas (455,370 CD3+CAR+ cells, 119 patients, 87 response-labeled; test run at patient level): under honest leave-one-**study**-out CV, the best axis (A_persist) collapses from patient-out AUROC 0.643 to study-out 0.533 (CI includes 0.5), and a trivial CD8-fraction baseline beats every axis. Reported as an honest negative, not buried.

The common cause: **the ground truth is confounded by magnitude.** Known regulators have ~99× more differential-expression effect than non-regulators (Mann–Whitney p = 2.6e-10), so *any* test of "index vs magnitude" is rigged — magnitude wins by construction.

**The fix is a conditional test, not a better index.** Asking *"does a feature add signal **conditional on** magnitude?"* instead of *"does it beat magnitude?"* reveals a genuine, magnitude-independent controllership signal:

| Component | What it measures | Adds over magnitude? |
|-----------|------------------|----------------------|
| **axis-specificity** (residualized) | effect concentrated on a state axis vs diffuse | **yes** — LR p < 1e-4 |
| **cross-donor coherence** (residualized) | same direction across donors | **yes** — LR p < 1e-4 |
| effect magnitude | n. downstream DE genes | (the confound) |
| network influence (PageRank, in-degree) | structural position | no |
| guide coherence | same direction across guides | no |

**Robustness and boundary:** the gate is stable across effect thresholds and the signal repeats in
**all three** culture conditions (Rest / Stim-8h / Stim-48h, all p < 1e-3). It does **not** survive
removing GATA3/TBX21/STAT6/IRF1, and the independent external functional-regulator set returns a
clean **FAIL** (ΔAUPRC −0.281 [−0.476, −0.073]). The supported scope is therefore canonical,
axis-defining regulators; cross-condition replication is within the same dataset, not an independent
cohort.

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
| [reports/PROJECT_PENDING_REGISTER.md](reports/PROJECT_PENDING_REGISTER.md) | Live pending register: prospective blockers, release debt and non-blocking scientific extensions |

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
make reproduce-core   # runs the validated CCI test across the dataset registry + builds the dashboard
```

This runs `isci/run_cci.py` over `config/datasets.yaml`: the Marson smoke path is recomputed from
the committed ranking + the locked `isci-controllership` skill helpers with **expression-matched
negatives** (single-condition diagnostic +0.248), while other systems aggregate committed heavy-run
reports into `outputs/dashboard/`. The dashboard uses the standardized matched `C`-versus-`M`
metric (+0.229 for Marson) for cross-system comparison; it does not replace the authoritative
full-sample M→M+C result (+0.357) or leakage-free OOF estimate (+0.215). The legacy five-component modules
(`isci/stability|insilico|network`) are **deprecated** — they lost to magnitude and were abandoned;
the driver, not those stubs, is the reproduction path. Every output carries a provenance stamp
(data SHA-256, conda env, git-SHA, seed) via `isci.repro`.

## Package layout

`isci/` — `io` (backed AnnData + SHA-256 manifest) · `axes` (leave-one-out axis construction) · `movement` (M, NES-style enrichment) · `qc` (Q, on-target validity) · `repro` (R, cross-donor/guide reproducibility) · `index` (rank-product / residualized aggregation) · `baselines` (DE-magnitude, effect-size, centrality) · `validate` (expression-matched negatives, AUPRC/AUROC, conditional LR) · `evidence` (PubMed-cited evidence cards) · `run_cci` (one-command driver over the dataset registry) · `build_dashboard` (visual result contract).

**Bring your own Perturb-seq dataset:** [`docs/dataset_spec.md`](docs/dataset_spec.md) defines the
versioned DatasetSpec v1 contract, supported input layouts, conservative capability tiers and the
synthetic contract fixture used before any large dataset is opened. The CSV/Parquet adapter already
canonicalizes mapped columns, verifies provenance and downgrades claims from observed coverage.

> **Deprecated** (kept for provenance only): `stability` / `insilico` / `network` were the original five-component index (M·R·D·A·S). It lost to the effect-magnitude baseline under expression-matched negatives and was abandoned; the validated method is the magnitude-conditional test in the `isci-controllership` skill, driven by `run_cci`.

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

## The property: a Conditional Controllability Invariant (immune-scoped)

The strongest form of the result is not an index on one dataset but a **named,
falsifiable property** tested for cross-dataset invariance:

> **Conditional Controllability Invariant (CCI):** after conditioning on effect
> **magnitude**, a reproducible, axis-specific residual signal `C` separates genes
> that *control* a cell-state transition from genes merely *associated* with it.

Formal definition, null, and falsification criterion:
[reports/conditional_controllability_invariant.md](reports/conditional_controllability_invariant.md);
dataset-agnostic protocol: [reports/generalization_spec.md](reports/generalization_spec.md);
full whitepaper: [reports/property_whitepaper.md](reports/property_whitepaper.md).

![Cross-dataset invariance](figures/cci_invariance_crossdataset.png)

| System | Cell type | Modality | Standardized matched C-vs-M ΔAUPRC | 95% CI | Verdict |
|---|---|---|---|---|---|
| **Marson** | CD4+ T (immune) | CRISPR KD/KO | **+0.229** | [0.072, 0.405] | **PASS** |
| Schmidt | CD4+ T (immune) | CRISPRa | +0.138 | [−0.029, 0.434] | near-miss (n_pos=10) |
| Norman | K562 (non-immune) | CRISPRa | +0.138 | [−0.033, 0.370] | **FAIL** (near-miss, n_pos=13) |
| **Replogle** | RPE1 (non-immune) | CRISPRi | **+0.060** | [−0.013, 0.204] | **FAIL (robust)** |

**The property is immune-scoped**, tested across **four** perturbation systems. It holds in the
anchor, shows the same directional signal under an opposite modality (CRISPRa; underpowered), and
fails in two non-immune screens (K562 differentiation, RPE1 proliferation) — a **demarcated
boundary**, not a universal claim. The Norman K562 near-miss is informative: its residual signal
comes from cross-guide reproducibility (R, p=0.0009), not axis-specificity (S, p=0.17) — the
immune-specific axis structure is what distinguishes the PASS. The
FAIL is mechanistically coherent: in proliferation screens controllers act by dosage on
a single dominant axis, so magnitude and controllership are collinear and conditioning on
`M` removes the signal; in immune state transitions, regulators are directional and
axis-selective independent of size, which is what `C` detects. Both the PASS and the FAIL
are open and reproducible via the `isci-controllership` skill.

## The capacity: Immune Engagement Capacity (IEC)

Around the locked core, we ask whether the immune-engagement phenotype is a measurable
**multi-axis capacity** — persistence, killing, resistance as separable axes. At single-cell
pseudobulk, **persistence is a clean axis** (|ρ|<0.08 vs the others) but **killing and resistance
stay entangled** (ρ≈−0.45): about **2.5 separable axes, not 3** — and we report the half rather
than rounding up. A BEHAV3D functional-killing proxy agrees that killing is its own axis
(persistence factor loads ≈0 on killing). Cell-level confirmation on the GPU is scoped in
`briefs/02_iec_latent_scvi.md`. Formal definition: `reports/immune_engagement_capacity.md`.

## Mechanism decomposition (curated enrichment + signed graph)

- **Curated gene-set enrichment** ([figures/curated_enrichment.png](figures/curated_enrichment.png)):
  along the continuous `ISCI_orthogonal` score, 6 pre-specified T-cell sets tested rank-based with
  a magnitude guard. **4/6 survive BH-FDR**, and the guard separates two kinds: **NF-κB activation**
  and **Treg/brake/apoptosis** enrich in controllership but **NOT in magnitude** (the clean,
  magnitude-independent finding); TCR-proximal and chromatin enrich in both (TCR is the expected
  high-effect rheostat / positive control). See [reports/mechanism_and_triage.md](reports/mechanism_and_triage.md).
- **Signed perturbation→module graph** ([figures/signed_perturbation_graph.png](figures/signed_perturbation_graph.png)):
  replaces PPI centrality (which added nothing over magnitude) with causal perturbation edges.
  **Therapeutic convergence is a third, independent axis** (Spearman +0.24 vs controllership, +0.18
  vs magnitude): the #1 controller **IRF1 points the *wrong* way** (convergence −0.21) — strong
  controllership ≠ desirable intervention. See [reports/signed_perturbation_graph.md](reports/signed_perturbation_graph.md).
- **Safety-first decision board** ([outputs/targetability_decision_board.csv](outputs/targetability_decision_board.csv)):
  the 70 controllers sorted into A (manufacturing modulation, 24) / B (engineering candidates, 6) /
  C (probe-only, 18) / D (dangerous rheostats, 22). The overclaim guard is structural — the two
  most drug-like genes, **IKBKB and PRKDC, land in Category D**.

## Limitations & future work

- **Clinical bridge is a well-powered negative result.** No IEC axis predicts CAR-T response under honest leave-one-study-out CV on the Functional CAR-T atlas (n=87 patients, 9 studies, >1M cells): A_persist study-out AUROC 0.533 [0.408, 0.650], perm-p 0.14; every axis CI includes 0.5; CD8-fraction baseline (0.585) beats them all. The patient-out signal (0.643) was per-study batch, not transportable biology. This bounds the clinical claim — IEC is a descriptive multi-axis capacity, **not** a response biomarker — and does not touch the locked CCI core.
- **External validation is direction-only, small-N.** Two CAR-T cohorts (GSE208052 n=9, GSE223655 33 CR/32 PD) confirm the *direction* of the memory-stem sensitivity axis (one-sided, uncorrected, no AUROC); this is replication of direction, not a validated response predictor. Resistance-axis validation (GSE197268, post-infusion) is gated on patient-level labels.
- **Broad GO/Reactome family enrichment is a statistical negative** — but *curated* T-cell gene sets tested continuously along the score **do** survive FDR (4/6), with NF-κB and Treg/brake enriched independent of magnitude (see Mechanism decomposition above). The lesson: set granularity matters; broad ontologies wash out the signal.
- **Foundation-model triangulation** (perturbation FMs / sequence models on top controllers) is scoped for the GPU machine (`briefs/`), not yet run.
- **IEC cell-level confirmation** (2.5-axis test) is **done**: the pseudobulk structure replicates at single-cell resolution on the 455,370-cell CAR-T atlas (persistence orthogonal, ρ=−0.12/−0.01; killing↔resistance entangled, ρ=−0.53; all axes magnitude-independent; entanglement survives CD8-fraction control, ρ=−0.44).

## Author

Abel Costa — hematologist / onco-hematologist, IDOR (São Paulo)

## License

MIT — see [LICENSE](LICENSE).
