# Submission — Built with Claude: Life Sciences (Researcher Track)

## Title
**Conditional controllability of T-cell state: a magnitude-deconfounded, falsifiable, immune-scoped property — with an honest CAR-T clinical null**

## One-line pitch
A magnitude-conditional signal that nearly doubles regulator recovery in genome-scale T-cell
Perturb-seq, hardened into a falsifiable immune-scoped *property*, extended into a multi-axis
engagement *capacity*, and stress-tested against CAR-T response where we report a well-powered
negative — every step run and self-audited by Claude.

## 150-word summary
Perturbation screens call "hits" by effect size, so a gene that shifts many transcripts looks like a
regulator whether or not it *controls* a state axis. In a genome-scale Perturb-seq atlas of primary
human CD4+ T cells, known regulators have ~100× more effect than non-regulators, so magnitude wins
by construction. We define controllership *conditional on magnitude* — axis-specificity plus
cross-donor coherence, each residualized against effect size — and show it is orthogonal to
magnitude yet nearly doubles regulator recovery (AUPRC 0.722 vs 0.415; bootstrap gain +0.229, CI
[0.072, 0.405]). It behaves as a falsifiable, immune-scoped property (PASS in immune, FAIL in
non-immune systems), decomposes into ~2.5 engagement axes, and — tested honestly across studies —
does **not** predict CAR-T response (a well-powered null; a CD8-fraction baseline beats every axis).
Claude ran every computation and caught its own leakage and overclaims.

---

## How the project maps to the judging criteria

### Impact (25%)
The contribution is a **method the field lacks**: an operational, magnitude-deconfounded definition
of a *controller* that is falsifiable on held-out perturbation systems, plus a discipline for the
CAR-T translation question. The most impactful output is arguably the **honest clinical null** — it
tells hematologists precisely where the transcriptional-state hypothesis pays off (controllership as
perturbation biology) and where it does not (cross-study response prediction), redirecting effort
toward composition and cross-study design. For onco-hematology (CAR-T failure, T-cell-engager
resistance), a demarcated boundary is more useful than an un-transportable positive.

### Claude Use (25%)
Claude was the scientist-operator, not a code assistant. It: ingested the data and literature;
proposed and repeatedly **red-teamed its own method**, discovering that the original five-component
index lost to a trivial magnitude baseline and pivoting to the conditional test; caught train/test
leakage and re-ran with expression-matched negatives; built a one-command reproducible pipeline,
a dataset registry, and a visual dashboard; retrieved and title-verified every literature citation
to avoid fabrication; and wrote the manuscript, decision board, and this submission. Multiple
adversarial self-audit rounds are visible in the commit history — the negative results are the proof
the tool was used for science, not salesmanship.

### Depth (20%)
The analysis spans magnitude-conditional benchmarking with bootstrapped CIs and conditional
likelihood-ratio tests; leakage controls and independent-positive replication; a four-system
falsifiability test with pre-registered verdicts; a multi-axis capacity decomposition validated
against a functional-killing proxy; magnitude-guarded curated enrichment; a signed
perturbation→module graph establishing therapeutic direction as a third independent axis; and a
pre-registered leave-one-study-out clinical test with a permutation null and a compositional
baseline. Every headline number is reproducible from committed artifacts.

### Demo (30%)
A 3-minute narrated demo (script in `DEMO_SCRIPT.md`) walks the arc: the magnitude confound → the
conditional fix and the doubled recovery → the four-system immune-scoped boundary → the honest
clinical null → mechanism without overclaim. On-screen: the four-system forest plot, the axis-
orthogonality heatmap, the leave-study-out null, the curated-enrichment quadrants, and the signed
graph. The interactive dashboard (`outputs/dashboard/`) lets a viewer see each dataset's verdict
against its pre-registered prediction.

### Gladstone prize (greatest potential to advance the field)
The reusable object is a **falsifiable property with a one-command test**: add a dataset as a config
block, get a PASS/FAIL against its pre-registered prediction. That turns "is this signal real?" into
a runnable experiment, and the immune-scoped boundary plus the well-powered clinical null give the
community a calibrated, non-overclaimed foundation to build on.

---

## Where we are honest about limits
- Few positives (12–21); bootstrap-stabilized and cross-condition-replicated, but a fully
  independent external positive set is future work.
- Cell-level confirmation of the 2.5-axis structure is **done** (single-cell replication on the
  455k-cell CAR-T atlas, CD8-controlled). Foundation-model triangulation (scGPT) remains scoped
  (brief in `briefs/`) but pending GPU execution.
- The clinical result is a **negative**; nothing here is a validated biomarker or medical advice.

## Links
- **Repo:** https://github.com/anetoc/ISCI-hackathon *(made public before submission)*
- **Reproduce:** `make reproduce-core`
- **Manuscript:** `reports/PAPER.md` · **Literature review:** `reports/literature_review.md`
- **Master dossier:** `reports/MASTER_DOSSIER.md` · **Demo script:** `DEMO_SCRIPT.md`

## Team
Abel Costa (hematologist / onco-hematologist, IDOR, Brazil) with Claude Science as the autonomous
analysis agent.