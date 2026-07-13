# Video narration — spoken copy (researcher / hematologist voice)

A ~3-minute narration written to be *said*, not read. First person, a clinician-scientist telling
one honest story. Time cues are guides, not handcuffs. Word count ≈ 430 (≈ 2:50 at a calm pace).
Deliver it slower than feels natural; the pauses marked "( )" are where the point lands.

Companion assets: on-screen visuals from `DEMO_SCRIPT.md`; hard-question answers in
`JUDGE_QA_REHEARSAL.md`. Every number here is verified against the locked artifacts.

---

## SCENE 1 · The clinical wound (0:00–0:30)
*On screen: a patient timeline — CAR-T infusion, early response, then relapse.*

"I'm a hematologist. In my clinic, some patients respond beautifully to a T-cell therapy —
and then, months later, the same disease comes back. ( ) When that happens, we ask a question that
sounds simple and isn't: which genes actually *steer* a T cell into the state we want — and which
ones just happen to change when we perturb them? Telling those two apart is the whole game. And most
screens can't."

## SCENE 2 · Why the obvious answer is wrong (0:30–1:05)
*On screen: a ranked list sorted by effect size; a few real regulators buried far down.*

"The tempting shortcut is: reward the gene that causes the biggest change. We tried exactly that —
and it lost. ( ) It turns out the genes we already *know* are regulators tend to have large effects,
so ranking by effect size just rediscovers what magnitude already told you. It feels like signal.
It's mostly the size of the hammer. So we stopped asking 'what changes the most' and asked a
sharper question."

## SCENE 3 · The real question, and the honest answer (1:05–1:45)
*On screen: the central figure — matched comparison, AUPRC 0.415 → 0.722.*

"Among perturbations with the *same* effect size — the same size hammer — which genes move the cell
toward a specific functional state, and do it *repeatably*, across different human donors? ( ) That
signal is real. Adding it to a model that already knows magnitude improves how well we recover known
regulators — a pre-specified gain of plus 0.357. And because thirteen positives is a small set, we
re-ran it fully out-of-fold. The gain shrank to plus 0.215 — and we *show* you that shrinkage,
because hiding it would be the easy lie."

## SCENE 4 · The part most projects skip (1:45–2:25)
*On screen: the verdict map — PASS, near-miss, FAIL, NULL across systems.*

"Here's what I'm proudest of. We didn't stop at the win — we went looking for where it breaks. ( )
On a broad external set of regulators, it fails — cleanly, minus 0.281. At the protein layer, it
fails. As a predictor of who responds to CAR-T across studies, it's a null — a simple CD8 fraction
does better. So the honest claim is narrow: this holds for canonical, state-defining regulators in
T cells. ( ) That boundary isn't a disappointment. It's the result. A method that tells you where it
*doesn't* work is a method you can actually trust."

## SCENE 5 · What Claude did, and what's next (2:25–3:00)
*On screen: the claim ledger; the live decision board.*

"Every one of those boundaries came out of a correction loop — Claude challenged our own headline,
found a leak in how we chose controls, and forced the stricter test. The deterministic code owns the
numbers; the skepticism is the science. ( ) What you're left with isn't a target list — it's a
tested scope map, with every PASS, FAIL and NULL written down and reproducible. Because a good
scientific agent doesn't just find an answer. ( ) It knows when *not* to call PASS."

---

## Delivery notes
- **Tone:** you're explaining to a smart colleague who isn't in your subfield — warm, unhurried,
  never selling. The numbers are quiet; the *reasoning* is the emphasis.
- **The three landings** (say these a touch slower, then pause): "It's mostly the size of the hammer."
  · "we *show* you that shrinkage." · "It knows when not to call PASS."
- **Never** rush Scene 4 to save time — cut a clause from Scene 2 instead. The failures are the thesis.
- If you flub a number, don't correct mid-sentence — finish, breathe, retake the line. It cuts clean.
