# ElevenLabs package — voice-clone narration for the T-CTRL video

**What ElevenLabs does here:** it generates the *audio* (your narration, in your cloned voice).
It does **not** assemble the video. Workflow: (1) clone your voice, (2) paste the script below to get
one audio file per slide (or one continuous file), (3) drop the audio under your slides in any editor.
Assembly options are at the bottom.

All numbers in the script are verified against the locked artifacts. Numbers are spelled out where a
TTS model tends to mis-read digits (e.g. "zero point three five seven").

---

## STEP 1 · Clone your voice (Instant Voice Clone)
1. ElevenLabs → **Voices → Add a new voice → Instant Voice Clone**.
2. Upload **1–3 minutes** of clean audio of you speaking English (no music, no background noise;
   a quiet phone recording of you reading any paragraph works).
3. Name it e.g. "Abel — clinical narration". Save.
4. Model: pick **Eleven Multilingual v2** (best for a non-native English accent and clear diction) or
   **Eleven v3** if available (best pause/emphasis control).

## STEP 2 · Voice settings (for a calm, didactic clinician tone)
- **Stability: 45–55%** — low enough to sound human and warm, high enough to stay steady across a
  3-minute read. If it sounds flat, lower to ~40%.
- **Similarity: 80–90%** — keeps it clearly *your* voice.
- **Style exaggeration: 0–15%** — keep low; you want measured, not theatrical.
- **Speaker boost: On.**
- **Speed: 0.95–1.0** — slightly slower than default; this is a teaching voice.

## STEP 3 · How pauses work
- The `<break time="2.0s" />` tags below are the three "landings" — real ~2-second silences.
- Commas and em-dashes already create natural micro-pauses; don't over-tag.
- Generate **one slide at a time** (paste each block separately) so you can re-roll a single slide
  without redoing the whole thing. Name each file `s01.mp3 … s10.mp3`.

---

## THE SCRIPT — paste each block into ElevenLabs separately

### s01 — Title
I'm a hematologist. In my clinic, some patients respond beautifully to a T-cell therapy — and then, months later, the same disease comes back. <break time="2.0s" /> When that happens, we ask a question that sounds simple and isn't: which genes actually steer a T cell into the state we want — and which ones just happen to change the most when we perturb them?

### s02 — The clinical question
Telling those two apart is the whole game — and most screens can't. A real controller has to answer three questions, not one. How much did the cell move? That's reach — the size of the abnormal result. Which state program actually moved? That's precision. And did independent donors agree? That's repeatability. Magnitude alone — just the size — is necessary, but nowhere near sufficient.

### s03 — How a perturbation is read
Here's how we read one perturbation. We silence a single gene in a primary human T cell, read the whole transcriptome, and then compare where the cell went — across guides, donors and contexts. We measure three things: how far the profile moved; whether it moved along a specific state axis; and whether independent units agree. The key question is whether that direction adds anything after magnitude is already known.

### s04 — Primary result
And the answer is yes — it adds real signal. In the pre-specified test, adding direction and repeatability to a model that already knows magnitude improves how well we recover known regulators, by zero point three five seven in precision-recall. <break time="2.0s" /> Now — thirteen positives is a small set, so we re-ran the whole thing out-of-fold, refitting everything inside each training fold. The gain shrank to zero point two one five. And we show you that shrinkage — because hiding it would be the easy lie.

### s05 — Tests designed to break it
Here's the part I'm proudest of. We didn't stop at the win — we went looking for where it breaks. On a broad, independent set of functional regulators, it fails — cleanly, minus zero point two eight, with the whole interval below zero. And when we remove the four master transcription factors that define the axes, the gain collapses to essentially nothing. So the honest claim is narrow: this holds for canonical, state-defining regulators in T cells.

### s06 — Boundary across systems
And that boundary is graded, not binary. In immune T cells, it passes. In a myeloid immune line, it's a near-miss. In non-immune cells — K-five-six-two, R-P-E-one — it fails. That's a scope map: it tells you exactly where the property lives. Which is why we never call it an invariant.

### s07 — Translation limits
One more honesty check. A controller is not automatically a drug target. Our number-one controller, I-R-F-one, actually points the wrong way for intervention. And as a predictor of who responds to CAR-T across studies, the whole approach is a null — a simple CD8 fraction does better. We report that, plainly.

### s08 — The innovation is judgment
So what's the actual innovation? It's judgment. Every one of those boundaries — every failure, every null — came out of a correction loop, where Claude challenged our own headline, found a leak in how we chose controls, and forced the stricter test. The deterministic code owns the numbers. The skepticism is the science.

### s09 — Gladstone bridge (optional)
And it points to a concrete next experiment: a pre-declared, donor-resolved panel that can falsify the next claim — with the safety checkpoints stated before any synthesis.

### s10 — Delivery and close
Everything is open-source and reproducible — clone it, run one command, and twenty-one of twenty-one release gates pass. What you're left with isn't a target list. It's a tested scope map — with every pass, every failure and every null written down. <break time="2.0s" /> Because a good scientific agent doesn't just find an answer. It knows when not to call PASS.

---

## STEP 4 · Turn audio + slides into a video
Pick whichever you're comfortable with:

**A · Keynote / PowerPoint (simplest)**
1. Export each `sNN.mp3`. In the deck, drag the matching audio onto each slide.
2. Set each slide to advance when the audio ends.
3. File → Export → Video (1080p). Done — no editor needed.

**B · Any video editor (most control — CapCut, DaVinci, Premiere)**
1. Export the 10 slides as images (open the PDF, export pages as PNG) or screen-record the deck.
2. Drop `s01…s10` on the timeline; put each slide image above its audio, trimmed to length.
3. Export MP4 1080p.

**C · Local ffmpeg (if you want me to script it)**
If you export the 10 slide PNGs and the 10 mp3s into one folder, I can hand you a one-line ffmpeg
command that stitches each PNG for exactly its audio duration and concatenates them into a single MP4.
Just say the word and tell me the folder.

## Timing check
- Total spoken ≈ 3:00 at speed 0.95. If the form caps at 3:00 and you run over, cut **s09** entirely
  (it's the optional Gladstone slide) — never cut s04 or s05.
- A 2:30 fallback MP4 already exists at `demo_assets/hackathon/hackathon_fallback_2m30.mp4`.

## Number pronunciation cheat (already applied above)
0.357 → "zero point three five seven" · 0.215 → "zero point two one five" ·
−0.281 → "minus zero point two eight" · CD8 → "C-D-eight" · IRF1 → "I-R-F-one" ·
K562 → "K-five-six-two" · RPE1 → "R-P-E-one" · 21/21 → "twenty-one of twenty-one".
