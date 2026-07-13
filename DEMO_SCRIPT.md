# T-CTRL — submitted 2:42 judge narration

**Run contract:** ten slides in `docs/hackathon_judge_demo.html`, synchronized to the submitted
video and the approved light medical deck. The full-sample, out-of-fold, descriptive and matched
comparators remain distinct: **+0.357**, **+0.215**, **0.415→0.722** and **+0.229**.

## SLIDE 1 — Title

> I'm a hematologist. Some patients respond to a T-cell therapy, then relapse months later. So we
> ask a question that sounds simple and isn't: which genes actually steer a T cell into the state
> we want, and which ones just change the most when we perturb them?

## SLIDE 2 — Clinical question

> Telling those apart is the whole game, and most screens cannot. A real controller answers three
> questions. How much did the cell move? That is reach. Which state program moved? That is
> precision. And did independent donors agree? That is repeatability. Magnitude alone is necessary,
> but nowhere near sufficient.

## SLIDE 3 — Perturbation readout

> We silence one gene in a primary human T cell, read the whole transcriptome, and compare where
> the cell went across guides, donors and contexts. The key question is whether direction adds
> information after magnitude is already known.

## SLIDE 4 — Primary result

> It does. In the pre-specified test, adding direction and repeatability to a model that already
> knows magnitude improves recovery of known regulators by +0.357 AUPRC. Because thirteen positives
> is a small set, we also ran a separate, stricter test: a fully refit, leakage-free out-of-fold
> estimate of +0.215. These are two different measurements, not one number shrinking, and we report
> both.

## SLIDE 5 — Tests designed to break the result

> We then looked for where the result breaks. On a broad external set of regulators it fails:
> minus 0.281, with the whole interval below zero. Remove the four master transcription factors and
> the gain collapses. The honest claim is narrow: canonical, state-defining regulators in T cells.

## SLIDE 6 — Boundary across systems

> The boundary is graded. Immune T cells pass, a myeloid line is a near-miss, and non-immune cells
> fail. That is a scope map: it tells us where the property appears and prevents us from calling it
> a universal invariant.

## SLIDE 7 — Translation limits

> A controller is not automatically a drug target. Our top controller, IRF1, points in an
> unfavorable intervention direction. As a CAR-T response predictor, the approach is NULL: a simple
> CD8-fraction baseline performs better. We report that result plainly.

## SLIDE 8 — Judgment

> The innovation is judgment. Every FAIL, NULL and NOT-EVALUABLE result came from a correction loop
> where Claude challenged our headline, exposed a leakage path and forced a stricter test. The code
> owns the numbers. The skepticism is the science.

## SLIDE 9 — Gladstone bridge

> That correction loop points to a concrete next experiment: a pre-declared, donor-resolved panel
> designed to falsify the next claim before any guide is promoted.

## SLIDE 10 — Open-source delivery

> Everything is open source. Clone it, run one command, and twenty-one of twenty-one automated gates
> pass. What remains is not a target list. It is a tested scope map with every pass, failure and null
> written down. A good scientific agent does not just find an answer. It knows when not to call PASS.

## Controls

- `→`, `Space` or `PageDown`: next slide.
- `←` or `PageUp`: previous slide.
- `Home` / `End`: first / last slide.
- `F`: full screen.
- `R`: reset the timer and return to slide 1.
