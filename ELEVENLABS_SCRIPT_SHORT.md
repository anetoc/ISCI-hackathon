# ElevenLabs script — SHORT cut (fits 3:00)

**Settings:** same cloned voice · **Speed = 1.10** · Stability ~50% · Similarity 85–90% · Multilingual v2.
**Projected length ≈ 2:49** (436 words + three 1.2s landings) at speed 1.10 — under 3:00 with ~10s margin.
All numbers verified against the locked artifacts; digits spelled out so the TTS reads them right.

> Measured from your own 4:18 file: at 0.95 you speak ~137 wpm, so at 1.10 ≈ 159 wpm.
> This cut is 590 → 436 words. If you still run long, cut **s09** (Gladstone) — never s04/s05.

---

## Option A — one continuous file (matches what you did)
Paste this whole block, generate once:

I'm a hematologist. Some patients respond to a T-cell therapy, then relapse months later. <break time="1.2s" /> So we ask a question that sounds simple and isn't: which genes actually steer a T cell into the state we want — and which ones just change the most when we perturb them?

Telling those apart is the whole game, and most screens can't. A real controller answers three questions. How much did the cell move — that's reach. Which state program moved — that's precision. And did independent donors agree — that's repeatability. Magnitude alone is necessary, but nowhere near sufficient.

So we silence one gene in a primary human T cell, read the whole transcriptome, and compare where the cell went across guides, donors and contexts. The key question: does direction add anything after magnitude is already known?

It does. Adding direction and repeatability to a model that already knows magnitude improves recovery of known regulators, by zero point three five seven. <break time="1.2s" /> Thirteen positives is small, so we re-ran it out-of-fold — and the gain shrank to zero point two one five. We show you that shrinkage, because hiding it would be the easy lie.

Here's the part I'm proudest of: we went looking for where it breaks. On a broad external set of regulators, it fails — minus zero point two eight, the whole interval below zero. Remove the four master transcription factors, and the gain collapses. So the honest claim is narrow: canonical, state-defining regulators in T cells.

And the boundary is graded. Immune T cells pass. A myeloid line is a near-miss. Non-immune cells fail. That's a scope map — it tells you exactly where the property lives. Which is why we never call it an invariant.

A controller is not a drug target. Our top controller, I-R-F-one, points the wrong way for intervention. And as a CAR-T response predictor, the approach is a null — a simple CD8 fraction does better. We report that plainly.

So the real innovation is judgment. Every failure, every null came from a correction loop where Claude challenged our own headline, found a leak in the controls, and forced the stricter test. The code owns the numbers. The skepticism is the science.

And it points to a concrete next experiment: a pre-declared, donor-resolved panel that can falsify the next claim.

Everything is open-source: clone it, run one command, twenty-one of twenty-one gates pass. What's left isn't a target list — it's a tested scope map, with every pass, failure and null written down. <break time="1.2s" /> Because a good scientific agent doesn't just find an answer. It knows when not to call PASS.

---

## Option B — per-slide files (better for video sync: s01.mp3 … s10.mp3)

### s01
I'm a hematologist. Some patients respond to a T-cell therapy, then relapse months later. <break time="1.2s" /> So we ask a question that sounds simple and isn't: which genes actually steer a T cell into the state we want — and which ones just change the most when we perturb them?

### s02
Telling those apart is the whole game, and most screens can't. A real controller answers three questions. How much did the cell move — that's reach. Which state program moved — that's precision. And did independent donors agree — that's repeatability. Magnitude alone is necessary, but nowhere near sufficient.

### s03
So we silence one gene in a primary human T cell, read the whole transcriptome, and compare where the cell went across guides, donors and contexts. The key question: does direction add anything after magnitude is already known?

### s04
It does. Adding direction and repeatability to a model that already knows magnitude improves recovery of known regulators, by zero point three five seven. <break time="1.2s" /> Thirteen positives is small, so we re-ran it out-of-fold — and the gain shrank to zero point two one five. We show you that shrinkage, because hiding it would be the easy lie.

### s05
Here's the part I'm proudest of: we went looking for where it breaks. On a broad external set of regulators, it fails — minus zero point two eight, the whole interval below zero. Remove the four master transcription factors, and the gain collapses. So the honest claim is narrow: canonical, state-defining regulators in T cells.

### s06
And the boundary is graded. Immune T cells pass. A myeloid line is a near-miss. Non-immune cells fail. That's a scope map — it tells you exactly where the property lives. Which is why we never call it an invariant.

### s07
A controller is not a drug target. Our top controller, I-R-F-one, points the wrong way for intervention. And as a CAR-T response predictor, the approach is a null — a simple CD8 fraction does better. We report that plainly.

### s08
So the real innovation is judgment. Every failure, every null came from a correction loop where Claude challenged our own headline, found a leak in the controls, and forced the stricter test. The code owns the numbers. The skepticism is the science.

### s09
And it points to a concrete next experiment: a pre-declared, donor-resolved panel that can falsify the next claim.

### s10
Everything is open-source: clone it, run one command, twenty-one of twenty-one gates pass. What's left isn't a target list — it's a tested scope map, with every pass, failure and null written down. <break time="1.2s" /> Because a good scientific agent doesn't just find an answer. It knows when not to call PASS.

---

## Number pronunciation (already applied)
0.357 → "zero point three five seven" · 0.215 → "zero point two one five" ·
−0.281 → "minus zero point two eight" · IRF1 → "I-R-F-one" · CD8 → "C-D-eight" ·
21/21 → "twenty-one of twenty-one". (K562/RPE1 dropped from s06 to save time.)
