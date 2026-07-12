# Hostile-judge defense cards

Each spoken answer is designed for ≤20 seconds. The artifact is the evidence; the limitation is said
out loud when relevant; the prohibited overclaim is never used.

## Q1 — Is the result circular because the positives define the axes?

**Answer:** Axis-defining regulators are the bounded discovery population, so we explicitly use
leave-one-marker-out reconstruction whenever an axis member is evaluated. The external non-marker
set then fails, which prevents us from claiming broad regulator discovery.

**Evidence:** `reports/result_lock.md`; `outputs/positive_set_stress_test.json`.
**Limitation:** The positive class remains canonical and small.
**Do not say:** “The score discovers all functional regulators.”

## Q2 — Are thirteen positives enough?

**Answer:** They are enough for a bounded, uncertainty-reported result, not a universal claim. We use
expression-matched negatives, hierarchical bootstrap, grouped OOF and permutation testing, then
show the shrinkage rather than hide it.

**Evidence:** `outputs/isci_oof_incremental.json`.
**Limitation:** Independent prospective positives are still required.
**Do not say:** “The sample size proves generality.”

## Q3 — Why is 0.415→0.722 not the primary result?

**Answer:** That is a descriptive ranking comparison on the full detectable set. The primary test
asks whether controllership adds to a model that already knows magnitude, using matched negatives;
its gain is +0.357. They are different estimands and populations.

**Evidence:** `reports/result_lock.md`.
**Limitation:** The descriptive jump is more intuitive but less adjudicative.
**Do not say:** “The AUPRC improvement is +0.307 under the primary test.”

## Q4 — Why did the OOF gain shrink?

**Answer:** Because OOF removes optimism. Negative selection, residualization, scaling and the model
are all refit inside training folds. The honest estimate falls to +0.215, but its interval remains
above zero and permutation p is 0.010.

**Evidence:** `outputs/isci_oof_incremental.json`.
**Limitation:** OOF still contains only thirteen held-positive blocks.
**Do not say:** “The full-sample and OOF values estimate the same quantity.”

## Q5 — Is controllability immune-wide?

**Answer:** Not established. Marson CD4 is the PASS anchor; Schmidt, Frangieh and THP-1 are
directional or near-miss evidence, while non-immune systems fail. We present a bounded support map,
not an immune-wide invariant.

**Evidence:** `reports/CLAIM_LEDGER.md`; `figures/layer_verdict_map.png`.
**Limitation:** No formal cross-system heterogeneity model has been completed.
**Do not say:** “The invariant replicates across immune biology.”

## Q6 — Did Claude do science or only write code?

**Answer:** Claude participated in the scientific correction loop: it challenged the failed index,
separated estimands, exposed leakage, required stronger controls, maintained the claim ledger and
preserved FAIL, NULL and NOT-EVALUABLE outcomes. Deterministic code still owns every metric and gate.

**Evidence:** `reports/CLAIM_LEDGER.md`; `outputs/hackathon/claim_manifest.json`; Git history.
**Limitation:** Claude’s reasoning does not replace statistical validation or PI approval.
**Do not say:** “Claude autonomously proved the hypothesis.”

## Q7 — What is new relative to pert2state, Shesha, GEARS or CellOracle?

**Answer:** Those methods model perturbation effects, states or networks. Our contribution is an
adjudication coordinate: after conditioning on effect reach, does axis precision and donor
repeatability add regulator information, under explicit leakage controls and verdict boundaries?

**Evidence:** `reports/PAPER.md`; `reports/conditional_controllability_invariant.md`.
**Limitation:** ISCI is a complementary benchmark, not a replacement for perturbation models.
**Do not say:** “ISCI outperforms every perturbation foundation model.”

## Q8 — Why does the external functional-regulator set fail?

**Answer:** Those regulators are already magnitude-visible, and the residual controllership
coordinate removes rather than adds recovery: ΔAUPRC −0.281 with an interval entirely below zero.
That failure narrows the contribution to canonical axis-defining regulators.

**Evidence:** `outputs/positive_set_stress_test.json`.
**Limitation:** The external set tests a different regulator class.
**Do not say:** “The external failure validates the broad score.”

## Q9 — If the clinical test is null, where is the translational value?

**Answer:** It prevents an unsupported biomarker claim and redirects translation toward a
prospective donor-resolved perturbation experiment. Controllership can be useful experimental
biology without being a transportable clinical-response predictor.

**Evidence:** `outputs/iec_clinical/verdict.json`; `reports/DONOR_RESOLVED_CONTEXT_VALIDATION_PLAN.md`.
**Limitation:** Nothing here is a clinical biomarker or medical device claim.
**Do not say:** “The null proves no relationship with CAR-T response.”

## Q10 — What exactly should Gladstone test next?

**Answer:** A frozen 54-guide CD4 panel across paired no-stim and stimulated contexts in eight to
twelve donors, evaluated with held-gene × held-donor prediction and paired donor inference. The
extension fails if the bootstrap interval crosses zero, permutation p is at least 0.05, or fewer
than 70% of donors agree.

**Evidence:** `reports/PROSPECTIVE_DONOR_PANEL_PROTOCOL.md`;
`reports/DONOR_RESOLVED_CONTEXT_VALIDATION_PLAN.md`.
**Limitation:** Synthesis remains blocked pending sequence-specific and vector QC.
**Do not say:** “The panel is ready to order or already experimentally validated.”

