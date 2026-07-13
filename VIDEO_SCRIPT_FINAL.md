# Video narration — ONE continuous take (paste whole into ElevenLabs)

**Settings:** cloned voice · Speed **1.10** · Stability ~50% · Similarity 85–90% · Multilingual v2.
**Generate as a SINGLE file** (do not split). The blank line between paragraphs is your slide-change
point — I'll sync the slides to those pauses when I assemble the video, so the transitions ride the
narration smoothly instead of cutting.
Projected ≈ 3:00–3:10 at 1.10. All numbers verified against the locked artifacts.

---

I'm a hematologist. Some patients respond to a T-cell therapy, then relapse months later. <break time="1.0s" /> So we ask a question that sounds simple and isn't: which genes actually steer a T cell into the state we want — and which ones just change the most when we perturb them?

Telling those apart is the whole game, and most screens can't. A real controller answers three questions. How much did the cell move — that's reach. Which state program moved — that's precision. And did independent donors agree — that's repeatability. Magnitude alone is necessary, but nowhere near sufficient.

So we silence one gene in a primary human T cell, read the whole transcriptome, and compare where the cell went across guides, donors and contexts. The key question: does direction add anything after magnitude is already known?

It does. Adding direction and repeatability to a model that already knows magnitude improves recovery of known regulators, by zero point three five seven. <break time="1.0s" /> Thirteen positives is small, so we re-ran it out-of-fold — and the gain shrank to zero point two one five. We show you that shrinkage, because hiding it would be the easy lie.

Here's the part I'm proudest of: we went looking for where it breaks. On a broad external set of regulators, it fails — minus zero point two eight, the whole interval below zero. Remove the four master transcription factors, and the gain collapses. So the honest claim is narrow: canonical, state-defining regulators in T cells.

And the boundary is graded. Immune T cells pass. A myeloid line is a near-miss. Non-immune cells fail. That's a scope map — it tells you exactly where the property lives. Which is why we never call it an invariant.

A controller is not a drug target. Our top controller, I-R-F-one, points the wrong way for intervention. And as a CAR-T response predictor, the approach is a null — a simple CD8 fraction does better. We report that plainly.

So the real innovation is judgment. Every failure, every null came from a correction loop where Claude challenged our own headline, found a leak in the controls, and forced the stricter test. The code owns the numbers. The skepticism is the science.

And it points to a concrete next experiment: a pre-declared, donor-resolved panel that can falsify the next claim.

Everything is open-source: clone it, run one command, twenty-one of twenty-one gates pass. What's left isn't a target list — it's a tested scope map, with every pass, failure and null written down. <break time="1.0s" /> Because a good scientific agent doesn't just find an answer. It knows when not to call PASS.

---

## After you generate
Send me the single mp3. I'll detect the ten natural pauses and cross-dissolve each slide onto them —
one smooth take, no hard cuts.

## Slide map (for my sync — you don't read these)
1 title · 2 clinical question · 3 how a perturbation is read · 4 primary result ·
5 tests to break it · 6 boundary across systems · 7 translation limits · 8 judgment ·
9 Gladstone bridge · 10 delivery + close

## Number pronunciation (already spelled in the text)
0.357 → "zero point three five seven" · 0.215 → "zero point two one five" ·
−0.281 → "minus zero point two eight" · IRF1 → "I-R-F-one" · CD8 → "C-D-eight" ·
21/21 → "twenty-one of twenty-one".
