# Judge Q&A rehearsal — spoken delivery drill

Companion to `JUDGE_QA.md` (which has the 10 canonical defense cards). This file is for
**practicing out loud**: exact numbers verified against locked artifacts, a 15–20s spoken script,
and a "if they push" fallback line for each. Read the answer aloud once; if it runs past 20s, cut
the middle clause, never the caveat.

**The one-sentence anchor (open and close every hard answer with a version of this):**
> "The contribution is a *tested scope map* — it tells you where T-cell-state controllership holds
> and where it collapses. A good scientific agent knows when *not* to call PASS."

---

## Verified number sheet (say these exactly — checked against artifacts this session)

| Quantity | Value | Source artifact |
|---|---|---|
| Descriptive ranking AUPRC | 0.415 → 0.722 | result_lock.md |
| Pre-specified incremental M→M+C | **+0.357** [+0.117, +0.538], P>0=1.000 | result_lock.md |
| Leakage-free OOF (per-fold refit) | **+0.215** [+0.074, +0.560], perm p=0.010 | isci_oof_incremental.json |
| OOF optimism (internal to OOF only) | +0.178 (0.393 − 0.215) | isci_oof_incremental.json |
| Cross-system matched C-vs-M | +0.229 [0.072, 0.405] | result_lock.md |
| External functional set (FAIL) | ΔAUPRC **−0.281** [−0.476, −0.073], n_pos=20 | positive_set_stress_test.json |
| Clinical NULL (leave-study-out) | A_persist 0.643 LPO → **0.533** LSO; CD8-frac baseline 0.585 | iec_clinical/cv_results.json |
| Orthogonality to magnitude | Spearman ρ = +0.02 | result_lock.md |

**Never say:** +0.307 as "the primary test" (that's 0.722−0.415, a different population); "the invariant
replicates"; "predicts CAR-T response"; "discovers all functional regulators".

---

## The three questions most likely to decide the score

### R1 — "This only works on canonical regulators in CD4 T cells. Isn't that too narrow to matter?"
**Spoken (18s):** "The narrowness is a *result*, not a limitation we're hiding. We ran the broad
external set and it failed — minus 0.281, interval entirely below zero. So we bounded the claim to
canonical axis-defining regulators, and stated that boundary in the ledger. A method that knows its
own domain is more useful to Gladstone than one that claims everything and replicates nowhere."
**If they push ("but the clinical reach?"):** "Correct — that's why the clinical test is reported as
a NULL, not spun. The value is the adjudication framework, portable to any Perturb-seq screen."
**Do not:** get defensive or widen the claim to sound more impressive.

### R2 — "You have thirteen positives. This is overfit."
**Spoken (17s):** "We assumed you'd ask. So we ran it out-of-fold — negative selection,
residualization, scaling and the model all refit inside each training fold. The gain shrank from an
apparent +0.393 to +0.215, and we *report* that shrinkage. The bootstrap interval still excludes
zero and permutation p is 0.010."
**If they push ("still small"):** "Agreed — that's why the next experiment is a pre-registered
54-guide panel in eight to twelve donors. Thirteen is enough for a bounded verdict, not a universal one."
**Do not:** claim the sample proves generality.

### R3 — "What did Claude actually do that a script couldn't?"
**Spoken (19s):** "Claude ran the scientific correction loop. It caught that our headline compared
the score alone versus magnitude alone, when the pre-specified test was the incremental one — and
fixing that *strengthened* the result. It exposed a leakage path in the negative selection, forced
the out-of-fold redo, and maintained a claim ledger that preserves every FAIL and NULL. The
deterministic code owns the metrics; Claude owns the skepticism."
**If they push ("so it's just prompting?"):** "The audit trail is in Git — each correction is a
commit with the before-and-after number. That's reproducible, not narrative."
**Do not:** say Claude autonomously proved anything.

---

## Six extra hostile questions not in JUDGE_QA.md

### E1 — "Effect magnitude and your score correlate at only 0.02 — did you engineer that?"
"Yes, by construction — we residualize the axis-specificity and coherence components against
magnitude before scoring. The point isn't that ρ=0.02 is a discovery; it's the *precondition* that
lets us ask whether anything is left after magnitude is removed. The answer, conditional on
magnitude, is +0.357."

### E2 — "Isn't 'controllership' just a rebranding of differential expression?"
"The opposite — magnitude *is* differential expression, and the whole project exists because
magnitude alone won on the naive benchmark. Controllership is what remains after you subtract
magnitude: state-specificity plus cross-donor repeatability. When we add it back to a
magnitude-aware model it improves regulator recovery; that's the entire claim."

### E3 — "Your protein-layer test failed. Doesn't that undermine the RNA result?"
"It bounds it, honestly. The protein panel is 24 markers — coarse — and the failure is
direction-aware: the positives had *lower* residual coherence, an inverted signal, so we call it
FAIL, not a disguised pass. Magnitude-independence is an RNA and cross-donor property. We say that
explicitly rather than quietly dropping the protein slice."

### E4 — "You cite Shesha as prior art. What stops this from being the same idea?"
"We measured it. In Frangieh, Shesha's cell-to-cell coherence correlates with magnitude at
ρ=0.97 — it collapses onto effect size. Our coordinates are orthogonal: R at 0.008, S at 0.19.
Two groups finding the magnitude trap in the same year strengthens the phenomenon; our coordinate
is the one that survives conditioning on magnitude."

### E5 — "If I clone the repo right now, does it run?"
"Yes. `uv sync --locked --extra dev` then `uv run pytest` — 151 tests pass, including under
FutureWarning-as-error. `uv run isci pipeline` on the example returns NOT-EVALUABLE by design,
because the fixture is deliberately too small — the guardrail firing is the feature. Twenty-one
automated readiness gates are green."

### E6 — "Why should this win the Gladstone prize specifically?"
"Because Gladstone rewards potential to advance the field, and the bottleneck in perturbation
biology isn't more scores — it's trust. We built the adjudication layer: a method that reports its
own FAIL and NULL boundaries and hands you a reusable pipeline to test the next dataset. That's
infrastructure the field can build on, not a one-off leaderboard entry."

---

## Delivery rules (say once before recording)
1. Lead with the verdict, then the number, then the caveat — never the reverse.
2. If you don't know a number, say "it's in the claim ledger" — never improvise a value.
3. Every FAIL/NULL is said *proudly* — it's the thesis, not an apology.
4. Silence is fine. A 2-second pause reads as confidence; a filler number reads as guessing.
5. Close hard exchanges by returning to the anchor sentence.
