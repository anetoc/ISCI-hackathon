# Submission — Built with Claude: Life Sciences (Researcher Track)

## Title
**T-CTRL — Which genes actually steer T-cell state?**

## One-line pitch
T-CTRL, which computes the ISCI controllability index, is an auditable scientific-judgment workflow that
challenged a failed score, rebuilt the leakage controls and returns explicit PASS, FAIL, NULL or
NOT-EVALUABLE verdicts with provenance.

## 150-word summary
Perturbation screens call hits by effect size, so a gene that shifts many transcripts can mimic
state control. In human CD4+ T cells, our first index lost
to magnitude (AUPRC 0.35 versus 0.41). Claude-guided scientific critique separated reach, precision
and repeatability and required native matched negatives, leave-one-marker-out axes and fully refit
out-of-fold evaluation. Among detectable-effect, canonical axis-defining regulators, the
authoritative M→M+C gain is +0.357 AUPRC (95% CI [+0.117,+0.538]); leakage-free OOF remains +0.215
([+0.074,+0.560], permutation p=0.010). Descriptive: 0.415→0.722. Deterministic gates
also return FAIL on an external non-marker regulator set, NULL for CAR-T response prediction and
NOT-EVALUABLE for scGPT when required inputs are absent. Claude critiques and explains; versioned
code computes every metric and verdict. ISCI is not a universal score or target list, but an
auditable way to know whether a bounded biological claim survives.

---

## How the project maps to the judging criteria

### Impact (25%)
The contribution is a workflow the field lacks: a magnitude-controlled definition of a bounded
state controller plus an executable discipline for deciding whether evidence supports, refutes,
fails to improve or cannot validly evaluate a claim. It protects perturbation biology from false
controller calls and makes negative or structurally blocked results useful rather than invisible.

### Claude Use (25%)
Claude was the scientific critic and evidence operator, not merely a code assistant. It challenged
the failed five-component index, separated estimands, exposed leakage risks, demanded stronger
controls, maintained the claim ledger and explained bounded verdicts. Deterministic, versioned code
still computes all metrics and applies the frozen gates. The preserved FAIL, NULL and
NOT-EVALUABLE cases demonstrate scientific abstention rather than salesmanship.

### Depth (20%)
The analysis includes magnitude-conditional benchmarking, native expression-matched negatives,
leave-one-marker-out axes, hierarchical bootstrap, grouped OOF with every learnable step refit,
permutation nulls, independent negative stress tests, a multi-study clinical null and explicit
non-evaluable gates. Every stage claim is content-addressed in
`outputs/hackathon/claim_manifest.json`.

### Demo (30%)
A 2:30 deterministic offline demo (`docs/hackathon_judge_demo.html`) walks one primary claim through
evidence, leakage controls, a frozen gate, PASS and an explicit scope boundary. A compact trust
matrix then shows FAIL, NULL and NOT-EVALUABLE before ending on a prospective donor-resolved
Gladstone experiment. Six Full-HD static fallbacks are committed in `demo_assets/hackathon/`.

### Gladstone prize (greatest potential to advance the field)
The next falsification is already designed: 54 guides across 25 target genes, paired no-stim and
stimulated contexts and 8–12 independent donors. Fifty-three guide identities are confirmed;
PAPOLG-1 remains low-support, and synthesis is explicitly blocked pending reference, off-target,
on-target and vector-compatibility QC. The analysis and promotion gates are frozen in advance.

---

## Where we are honest about limits
- Few positives (12–21); bootstrap-stabilized and cross-condition-replicated. A fully independent
  external functional-regulator set was tested and failed, bounding the claim to canonical,
  axis-defining regulators.
- Foundation-model triangulation is currently **NOT-EVALUABLE**, because the required perturbation
  expression profiles were absent locally; no gene-token substitute or fabricated metric was used.
- The clinical result is a **negative**; nothing here is a validated biomarker or medical advice.

## Links
- **Repo:** https://github.com/anetoc/ISCI-hackathon
- **Demo video (2:42):** https://youtu.be/7Rz4PpmQZuI
- **Interactive demo:** https://anetoc.github.io/ISCI-hackathon/
- **Reproduce:** `make reproduce-core`
- **Manuscript:** `reports/PAPER.md` · **Literature review:** `reports/literature_review.md`
- **Master dossier:** `reports/MASTER_DOSSIER.md` · **Demo script:** `DEMO_SCRIPT.md`

## Team
Abel Costa (hematologist / onco-hematologist, IDOR, Brazil). Claude Science and Claude Code were
research and engineering tools; scientific authorship and accountability remain with Abel Costa.
