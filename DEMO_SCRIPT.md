# T-CTRL — 2:30 hackathon stage script

**One message:** *A good scientific agent knows when not to call PASS.*

**Run contract:** six scenes in `docs/hackathon_judge_demo.html`; target 2:20–2:30; never mix the
full-sample, OOF and descriptive estimands. Press `R` before each rehearsal to reset the timer.

## SCENE 1 — 0:00–0:20 · The problem

> Most perturbation screens call a gene a controller because it changes many transcripts. But
> movement is not control. A large effect can be directionless or irreproducible. We built an
> auditable scientific-judgment workflow, demonstrated through T-CTRL, which computes our controllability index (ISCI), that asks whether the evidence
> deserves a PASS — and knows when it does not.

**Transition:** “It began by rejecting our own result.”

## SCENE 2 — 0:20–0:45 · The useful failure

> Our first five-component index failed. Its AUPRC was 0.35; magnitude alone reached 0.41. Claude
> did not polish the score. It challenged the construct, separated reach, precision and
> repeatability, demanded native matched negatives, leave-one-marker-out axes and out-of-fold
> refitting, and preserved the failure in the record.

**Transition:** “The right question was not whether control beats magnitude.”

## SCENE 3 — 0:45–1:12 · The bounded result

> The right question was whether precision and repeatability add information after magnitude is
> already known. In canonical axis-defining CD4 T-cell regulators, the full-sample M-to-M-plus-C
> gain is plus 0.357, with confidence interval above zero. In the stricter leakage-free evaluation,
> every learnable step is refit inside the folds. The gain shrinks honestly to plus 0.215, confidence
> interval plus 0.074 to plus 0.560, with permutation p equals 0.010.

**Transition:** “Now watch the claim pass through the frozen gate.”

## SCENE 4 — 1:12–1:42 · Claude scientific judgment

> One bounded claim enters with public evidence and explicit controls. Deterministic code computes
> the metrics and applies frozen gates. Claude critiques the claim, identifies missing controls,
> assembles the evidence and explains the verdict. The OOF interval excludes zero and the
> permutation test passes, so this claim receives PASS. The boundary matters: canonical
> axis-defining regulators, not every functional regulator and not therapeutic target nomination.

**Transition:** “Trust comes from the verdicts that were refused.”

## SCENE 5 — 1:42–2:05 · The trust proof

> Three plausible extensions did not receive PASS. Broad external functional regulators receive
> FAIL: the conditional score loses to magnitude. CAR-T clinical prediction receives NULL: study-out
> AUROC is 0.533 and a simple CD8-fraction baseline does better. scGPT receives NOT-EVALUABLE because
> the required expression profiles were absent. No biological result was fabricated from missing
> inputs.

**Transition:** “The next claim should be tested prospectively.”

## SCENE 6 — 2:05–2:30 · Gladstone bridge

> We designed the next falsification experiment: 54 guides, 25 target genes, paired contexts and
> eight to twelve independent donors. Fifty-three guide identities are confirmed; PAPOLG-1 remains
> low-support, and all synthesis is blocked until reference, off-target, on-target and vector QC
> pass. The product is not a target list. It is an auditable way to know whether a biological claim
> survives — and a concrete experiment Gladstone can now run donor by donor.

## Locked number hierarchy

- Authoritative full-sample M→M+C: **+0.357**, 95% CI **[+0.117,+0.538]**.
- Leakage-free OOF: **+0.215**, 95% CI **[+0.074,+0.560]**, permutation **p=0.010**.
- Descriptive ranking only: **0.415→0.722**; use only if asked.
- Matched cross-system comparator only: **+0.229 [0.072,0.405]**; use only if asked.

## Recording and rehearsal contract

- Record the deterministic local HTML; do not invoke a remote model during the stage demo.
- Run three consecutive rehearsals at or below 2:30.
- Keep `figures/hackathon_hero.png` and a PDF/screenshot sequence as offline fallbacks.
- If time is cut, omit the final sentence of Scenes 2 and 5; never omit the scope boundary.
- Do not say “universal”, “validated biomarker”, “therapeutic target” or “Claude decided the gate”.
