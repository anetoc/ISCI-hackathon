# Master Dossier — Immune-State Controllability & Engagement Capacity

**Project:** "Built with Claude: Life Sciences" hackathon (Researcher Track). Author: Abel
Costa (hematologist/onco-hematologist, IDOR). Co-pilot: Claude Science + Claude Code (on an
institutional RTX 6000 GPU node). This document consolidates the whole project into one
referenced narrative. Every headline number is traceable to a committed artifact (path +
commit/md5 given inline).

> **Reading guide.** The project has **one locked, demonstrated result** (the immune-scoped
> controllability property), **one vision layer** built on top of it (a multi-axis immune
> capacity), and **one high-risk open test** (clinical response prediction). We are deliberate
> about which is which. Nothing below overstates a hypothesis as a result.

---

## 0. One-paragraph summary

Starting from a genome-scale Perturb-seq screen in primary human CD4+ T cells, we asked a
question that sounds simple but is methodologically treacherous: **which genes *control* a
T-cell's functional state, as opposed to merely producing a large transcriptional effect?**
The naïve answer — rank by effect magnitude — wins any benchmark *by construction*, because
known regulators have huge effects. Our contribution is a **magnitude-conditional test** that
isolates a real, orthogonal signal (axis-specificity + cross-donor reproducibility) which adds
information *beyond* magnitude, nearly doubling regulator recovery. We show this signal is a
**falsifiable property** with a clean cross-dataset boundary — it holds in immune
state-transition systems and fails in cell-autonomous ones. We then frame a broader, testable
capacity (**Immune Engagement Capacity**) that this property controls, and we put its
highest-value claim — does any axis predict CAR-T response — to an honest, well-powered test.

---

## 1. Data foundation

| Dataset | What | Role | Access |
|---|---|---|---|
| **Marson genome-scale Perturb-seq** (CZI) | 33,983 perturbation×condition × 10,282 genes, primary human CD4+ T cells, 3 culture conditions (Rest/Stim8hr/Stim48hr), 4 donors | **Primary** — defines & tests the property | `data/GWCD4i.DE_stats.h5ad` (16.8 GB); layers zscore/log_fc/p_value/baseMean |
| **Functional CAR-T atlas** (Zenodo 19066393, ML4BM-Lab/Univ Navarra; *"An open CAR-T single-cell atlas…"*) | 455,370 CD3+CAR+ cells × 48,740 genes, 14 studies, 119 patients (87 response-labeled: 60R/27NR), 11 phenotypes | **Clinical bridge** — response-prediction test | verified via Zenodo API; `data_public/cart/Atlas_integ_scArches_FINAL_V5.h5ad` |
| **BEHAV3D** (GSE172325, Nat Biotechnol 2022, PMID 35879361) | scRNA of engineered TEGs in solid-tumor organoids + engagement-sort labels | **Functional proxy** (P3) — killing vs non-killing | GEO; solid-tumor TEGs, *not* hematologic CAR-T |
| **Cross-dataset scope panel** | Schmidt GSE190604 (immune CRISPRa); Norman&Weissman 2019 K562 (non-immune differentiation); Replogle RPE1 (non-immune proliferation) | **Boundary test** for the property | scPerturb / GEO / Zenodo |
| **External CAR-T cohorts** | GSE208052 (n=9), GSE223655 (33CR/32PD) | **Direction replication** of state axis | GEO |

---

## 2. The core result (LOCKED — `reports/result_lock.md`, core commit `32e991b`)

### 2.1 The problem: magnitude wins by construction
Known T-cell regulators have ~99× larger perturbation effects than matched non-regulators
(Mann–Whitney p = 2.6e-10). So any index that correlates with effect size will "recover
regulators" trivially. Our first index (`ISCI-core`) **lost** to the raw DE-magnitude baseline
under expression-matched negatives (AUPRC 0.35 vs 0.41). That honest failure reframed the
entire question.

### 2.2 The fix: a magnitude-conditional test
The valid question is not "does feature X correlate with regulator status" but "does X add
signal **conditional on magnitude**." Two features pass this bar:
- **axis-specificity** — the perturbation moves a specific functional axis, not everything;
- **cross-donor coherence** — the effect reproduces across the 4 donors.

### 2.3 The primary deliverable: `ISCI_orthogonal`
Defined as the **mean of magnitude-residualized percentiles** of (axis-specificity,
cross-donor coherence), gated to perturbations with a **detectable effect** (magnitude ≥
dataset median n-DE; 1,260 / 2,520 genes).

| Metric | Value | Source |
|---|---|---|
| Decorrelation from magnitude | Spearman ρ = **+0.02** (orthogonal by construction) | `result_lock.md` |
| Regulator recovery (detectable set) | **AUPRC 0.722** vs magnitude **0.415** | `result_lock.md` |
| Bootstrap gain (full residual set) | **+0.229 AUPRC**, 95% CI [0.072, 0.405], P(gain>0)=99.6% | `result_lock.md` |
| Conditional-LR (specificity, coherence) | both p < 1e-4 | session record |
| Replication | all 3 culture conditions (Rest/Stim8hr/Stim48hr) | session record |
| Leakage control | survives removal of axis-marker regulators; independent positives ARID1A/INO80/IKZF1 hold | `result_lock.md` |
| Ranking file | `outputs/isci_final_ranking.csv` (2,520 genes; md5 `5337113b682c38bd0c2d5755e2078520`) | committed |

**Top-15 by `ISCI_primary_rank`:** IRF1\*, IKBKB, BCLAF1, TFAP4, CYB561D2, PDCD5, ZC3H12A,
STAT6\*, RCOR1, PRKDC, SETDB1\*, TWF1, HEXIM1, GATA3\*, SAMD1 (\* = known regulator; 19 known
positives recovered). The list mixes recovered known regulators with novel candidates
(IKBKB, ZC3H12A, RCOR1) that carry the orthogonal signal but are not in the label set.

### 2.4 The exact validated claim (do not overstate)
> Among Marson-native / curated T-cell regulators, and among perturbations with a
> **detectable** effect, axis-specificity and cross-donor coherence **add information for
> regulator status beyond perturbation magnitude** — nearly doubling regulator recovery,
> surviving leakage controls, and replicating across all three culture conditions.

**Explicitly NOT claimed here:** universal clinical resistance mechanisms; CAR-T response
prediction (that is §5, still open).

---

## 3. The property: Conditional Controllability Invariant (CCI) — immune-scoped

We asked whether the magnitude-conditional signal is a **general property** or a Marson
artifact, by running the identical test on four systems
(`reports/conditional_controllability_invariant.md`, `reports/generalization_spec.md`):

| System | Type | ΔAUPRC | 95% CI | LR p | Verdict |
|---|---|---|---|---|---|
| **Marson CD4+** | immune, KD/KO | **+0.229** | [0.072, 0.405] | <1e-4 | **PASS** |
| Schmidt GSE190604 | immune, CRISPRa | +0.138 | [−0.029, 0.434] | n.s. | near-miss (n_pos=10, underpowered) |
| Norman&Weissman K562 | non-immune, differentiation | +0.138 | [−0.033, 0.370] | 0.013 | FAIL (carried by reproducibility R, *not* axis-specificity S) |
| Replogle RPE1 | non-immune, proliferation | +0.060 | [−0.013, 0.204] | 0.195 | FAIL (robust across 4 variants) |

**Finding (fig `figures/cci_scope_4systems.png`):** the property is **immune-scoped**. The
ordering matches a pre-stated prediction: immune PASS > non-immune differentiation near-miss >
non-immune proliferation clean-FAIL. The **axis-selective component (S) is the immune-specific
part**; reproducibility (R) alone can carry weak signal in non-immune differentiation. Naming
this boundary is what makes CCI a real, falsifiable property rather than an over-claim.

Whitepaper: `reports/property_whitepaper.md`. Cross-dataset figure:
`figures/cci_invariance_crossdataset.png`.

---

## 4. The vision layer: Immune Engagement Capacity (IEC)

`reports/immune_engagement_capacity.md` reframes the earlier "Tissue Synapse Capacity" note
into a measurable, multi-axis capacity. **IEC is the organizing frame; CCI is its control
operator** (Controllers(A) = genes passing the magnitude-conditional test for axis A).

### 4.1 The axes and what we learned about their structure
Two independent analyses converge on the same structure:

- **Latent factor** (1-factor FA on L1–L4 loadings, Marson Stim48hr; fig
  `figures/tsc_latent_factor.png`): a shared "reach-and-hold" factor explains 37% variance
  (tissue access L2 +0.99, synapse L3 +0.61, durable state L1 +0.37) — but **killing (L4)
  loads ≈0 (−0.09)**, i.e. *outside* the shared capacity.
- **BEHAV3D functional proxy** (P3; fig `outputs/behav3d_p3/behav3d_p3.png`; verdict
  NULL/FAIL, and informative): the composite score does **not** separate killers from
  non-killers (AUROC 0.350, loses to all baselines) — because **L4-killing alone separates
  near-perfectly (AUROC 0.947)** while L1/L2/L3 run the opposite way. Confounder guard passed
  (CD8 enrichment 1.26–1.50×, <2× threshold; fails within CD8+ stratum too). Replication
  NOT-EVALUABLE (corrupted Pseudotime matrix; refused to fabricate).

**Both say: killing is a *separate* axis from persistence.** IEC is therefore honestly:

- **A_persist** (reach-and-hold: memory/stem + tissue access + synapse) — a clean axis;
- **A_kill** (cytotoxic execution) — independent of persistence;
- **A_resist** (exhaustion-resistance).

### 4.2 Orthogonality pre-test (local, pseudobulk; fig `figures/iec_axis_orthogonality_pseudobulk.png`)
Testing the axes on Marson pseudobulk across all 3 conditions
(`outputs/iec_latent/iec_axis_scores_pseudobulk_stim48.csv`):

| pair | Rest | Stim8hr | Stim48hr | verdict |
|---|---|---|---|---|
| persist ↔ kill | −0.23 | −0.12 | −0.07 | orthogonal ✓ |
| persist ↔ resist | +0.14 | +0.03 | −0.01 | orthogonal ✓ |
| **kill ↔ resist** | **−0.42** | **−0.44** | **−0.50** | **entangled** (crosses \|0.5\| at 48hr) |
| each vs magnitude | — | — | \|ρ\|≤0.13 | orthogonal ✓ |

**Result: IEC is honestly 2.5 axes.** Persistence is a clean, independent axis. Killing and
exhaustion-resistance are the **effector↔exhaustion coupling** — two ends of one
activation-driven continuum, not two dials. This is a real structural result that sharpens the
definition (we do not claim three independent axes when the data show two).

---

## 5. The clinical bridge — HIGH RISK, OPEN (`briefs/04_iec_clinical_prediction.md`)

**The question:** does any IEC axis predict CAR-T response at patient-level power?

**The honest prior:** this failed once (the "D4" test — T-state signature, CV-AUROC ~chance,
on underpowered cohorts n=9/n=65). The Functional CAR-T atlas gives real power (n=87 labeled
patients) and IEC gives a multi-axis test instead of a single naïve signature. **A
well-powered NULL is itself a valid, publishable result.**

**The gate (Brief 03, EVALUABLE):** 87 patients (60R/27NR), 100% IEC gene coverage, clean
per-patient labels (0 inconsistencies). Verified columns: patient=`Norm_Patient_Name`,
study=`orig_ident`, response=`Max_Response` (R={CR,PR}).

**The critical methodological control:** response is **severely study-confounded** — 22/27
non-responders come from just 2 studies (Deng, Haradvala), and several studies are 100%
responder. So **leave-one-STUDY-out CV is the primary, decisive test** (not leave-patient-out,
which could score by memorizing batch). Pre-specified verdict rule: PASS only if
leave-study-out beats all baselines (magnitude, CD8-fraction, depth, permutation null) AND
bootstrap CI excludes 0.5 AND perm-p < 0.05. Anything else = NULL.

### 5.1 RESULT — VERDICT = NULL (well-powered) — `outputs/iec_clinical/`
The test ran on CPU (87 patients, 60R/27NR, 9 studies / 5 with both classes). The decisive
finding is a textbook batch-vs-biology dissociation:

| IEC axis (agg) | leave-**patient**-out AUROC | leave-**study**-out AUROC (decisive) | perm-p (study) |
|---|---|---|---|
| **A_persist (mean)** — primary | 0.643 [0.512, 0.767] | **0.533** [0.408, 0.650] | 0.138 |
| A_persist (frac-hi) | 0.633 | 0.576 [0.455, 0.699] | 0.075 |
| A_eff_exh (mean) | 0.535 | 0.507 | 0.228 |
| A_eff_exh (frac-hi) | 0.544 | 0.520 | 0.214 |
| **CD8-fraction baseline** | 0.615 | **0.585** | — |

**A_persist scores 0.643 under leave-patient-out but collapses to 0.533 under leave-study-out**
— i.e. the apparent signal was per-study batch structure, not a transportable predictor
(exactly the failure mode the brief anticipated). Every IEC axis's leave-study-out CI includes
0.5; every perm-p > 0.05; and the **CD8-fraction baseline (0.585) beats every IEC axis**.
NULL replicates in the NHL stratum (n=77, A_persist study-out 0.489) and the infusion-product
compartment (n=73, 0.516). Figure `outputs/iec_clinical/iec_prediction.png`.

**Interpretation (honest scope):** at real power — 87 patients vs the old n=70 D4 negative — 
**no IEC axis is a transcriptional response biomarker for CAR-T under honest cross-study CV.**
Per the IEC "clinical null" falsification criterion (§3), IEC is a *descriptive* multi-axis
capacity, **not** a response predictor. This **bounds the clinical claim** and, crucially, does
**not** touch the locked immune-scoped CCI controllership result (§2–3), which is causal
perturbation biology, not a clinical biomarker. A powered, pre-specified negative is a real
result. *Caveat honestly flagged:* a heterogeneous 14-study public atlas with only 5
informative studies leaves leave-study-out CI half-widths ≈0.12 — a single-protocol
prospective cohort could still reveal a small true effect this test cannot resolve.

---

## 6. Translation: drugability of controllers (`outputs/protein_targetability_matrix.csv`)

For the controllers of the property, we built a targetability matrix (70 genes; ChEMBL/Open
Targets/HPA): **35 druggable**, with an explicit **intervention-direction** column
(titratable 35 / transient-inhibition 29 / KD-harmful-suggests-OE 4 / avoid 2) — never framed
as a therapeutic recommendation. Mechanism annotations in `reports/mechanism_cards_v2.md`.
Because the clinical-prediction test returned a well-powered NULL (§5), this layer is **not**
re-focused onto a "clinically validated" axis — none was found. It stays a hypothesis-generating
experimental triage over the locked controllers, independent of the clinical claim.

The 70 controllers are also recast into a **4-category safety-first decision board**
(`outputs/targetability_decision_board.csv`): A — manufacturing modulation (24, titratable/
epigenetic), B — engineering candidates (6, clear KD/OE direction), C — probe-only biology (18),
D — dangerous / positive-control rheostats (22). The overclaim guard is now structural: the two
genes a naive reader would call "targets" — **IKBKB, PRKDC** — land in **Category D** (IKBKB is
TCR-proximal, PRKDC broadly essential). See `reports/mechanism_and_triage.md`.

---

## 6.5 Mechanism decomposition (curated enrichment + signed perturbation graph)

**Curated gene-set enrichment** (`figures/curated_enrichment.png`): along the continuous
`ISCI_orthogonal` score (2,520 genes), 6 pre-specified T-cell gene sets tested rank-based with a
magnitude guard. **4/6 survive BH-FDR**, and the guard separates two kinds of controller:
**NF-κB activation** and **Treg/brake/apoptosis** are enriched in controllership but **NOT in
magnitude** (the magnitude-independent finding); TCR-proximal and chromatin enrich in both (TCR is
the expected high-effect rheostat / positive control); cytoskeleton and RNA-decay are high-effect
but not axis-specific.

**Signed perturbation→module graph** (`figures/signed_perturbation_graph.png`): replaces PPI
centrality (which added nothing over magnitude) with causal perturbation edges — each KD's signed
effect on each functional module (11,281 × 6). **Therapeutic convergence** (coherent movement in
the desirable direction) is a **third, independent axis**: Spearman +0.24 vs controllership, +0.18
vs magnitude. The sharpest read: **IRF1**, the #1 controller, has *negative* convergence (−0.21) —
strong controllership does not imply a desirable intervention. GATA3 (+1.70) and RCOR1 (+0.90) are
the most convergent. See `reports/signed_perturbation_graph.md`.

---

## 7. What is demonstrated vs hypothesized (the credibility ledger)

| Claim | Status | Evidence |
|---|---|---|
| Magnitude-conditional signal adds regulator information | **DEMONSTRATED** | AUPRC 0.722 vs 0.415; bootstrap CI excludes 0; 3-condition replication |
| The signal is an immune-scoped property (CCI) | **DEMONSTRATED** (with boundary) | 4-system PASS/FAIL ordering matches prediction |
| Persistence and killing are separate axes | **DEMONSTRATED** | latent factor (L4≈0) + BEHAV3D functional proxy agree |
| IEC is a measurable multi-axis capacity (2.5 axes) | **SHOWN in pseudobulk**; cell-level pending | orthogonality pre-test; Brief 02 (scVI) to confirm |
| Some IEC axis predicts CAR-T response | **NULL (well-powered, cross-study)** | leave-study-out AUROC 0.53, CI incl. 0.5; CD8-frac baseline beats all axes; n=87 |
| Controllers are druggable | **Descriptive** | targetability matrix, direction-annotated |
| Specific mechanisms enrich in controllership beyond magnitude | **DEMONSTRATED** | NF-κB + Treg/brake enriched in ISCI (q<0.02), n.s. in magnitude (p>0.35) |
| Therapeutic direction is separable from controllership | **DEMONSTRATED** | signed graph: convergence ρ=+0.24 vs ISCI; IRF1 top controller, negative convergence |
| Controllers map to safe experimental categories | **Descriptive** | 4-category board; IKBKB/PRKDC structurally flagged dangerous |

---

## 8. Reproducibility & provenance

- **One-command reproduction:** `make reproduce-core` runs the validated CCI method across the
  dataset registry (`config/datasets.yaml`) via `isci/run_cci.py` and rebuilds the dashboard.
  Marson is recomputed from the committed ranking + locked helpers with **expression-matched
  negatives** (point estimate +0.248 reproduces locked +0.229); other datasets aggregate from
  committed reports. The legacy M/R/D/A/S modules are **deprecated** (they lost to magnitude and
  were abandoned) — the driver, not those stubs, is the reproduction path.

- Core result frozen in `reports/result_lock.md` (commit `32e991b`); ranking md5
  `5337113b682c38bd0c2d5755e2078520`.
- Reusable methods packaged as the `isci-controllership` skill (8 helpers: conditional-LR,
  expression-matched negatives, bootstrap AUPRC gain, movability gate, etc.).
- Manifest `outputs/reproducibility_manifest.json` (seeds: bootstrap 0 / null 42 / cv 0;
  python 3.12, numpy 2.4.6).
- Compute split: property + local analyses on CPU (Mac/sandbox); heavy cell-level and atlas
  work on the institutional RTX 6000 via Claude Code, synced through GitHub. Every machine
  result carries its own committed report under `outputs/`.

---

*This dossier is a living document; §5 (clinical verdict) and the cell-level confirmation
(§4.2, Brief 02) will be filled in as machine results arrive. Its scope discipline — one
locked result, one vision, one honest open test — is itself the submission's central posture.*
