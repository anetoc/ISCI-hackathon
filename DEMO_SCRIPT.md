# ISCI — 3-minute demo: screen-by-screen shot list

**One message:** *A good scientific agent knows when NOT to call PASS.*
**Total 3:00 · ~470 words @ 155 wpm · 6 screens.** Numbers below are the locked, current values —
read them exactly.

Central pitch (say it, then prove it):
> **Not every controller is a target. Not every targetable gene is safe. Not every biological axis
> is clinically predictive. We built the framework that adjudicates all four — and returns FAIL/NULL
> when the evidence doesn't support a claim.**

---

## SCREEN 1 — 0:00–0:25 · The question (hook)
**On screen:** title card → Marson dataset stat (33,983 perturbations × 10,282 genes, primary human CD4+ T).
**Say:**
> "Genome-scale Perturb-seq tells us which genes *change* a T cell's state. It does not tell us which
> genes *control* it. For CAR-T and T-cell engagers that difference is everything — you engineer the
> controller, not a bystander. We built this entirely inside Claude for Life Sciences, on Alex
> Marson's genome-scale CD4+ screen."

## SCREEN 2 — 0:25–1:05 · The honest failure (credibility)
**On screen:** the three FAIL baselines, then the Mann–Whitney p = 2.6e-10 magnitude gap.
**Say:**
> "Our first index failed — three times. It lost to a trivial baseline: count how many genes a
> perturbation moves. The reason matters: the ground truth is confounded by effect size. Known
> regulators have roughly 99-fold larger effects, so any 'our-score-versus-magnitude' test is rigged.
> Magnitude wins by construction."

## SCREEN 3 — 1:05–1:45 · The fix + the locked result (payoff)
**On screen:** central figure — AUPRC 0.415 → 0.722 with CIs; specificity separation panel.
**Say:**
> "The fix wasn't a fancier index — it was the right question. Not 'does our signal beat magnitude?'
> but 'does it add anything *conditional on* magnitude?' And there it is: among perturbations with the
> *same* effect size, real regulators are more state-specific and more reproducible across donors.
> That orthogonal signal nearly doubles regulator recovery — AUPRC 0.415 to 0.722. And when we ask the
> question we pre-specified — does controllership add to a model that already knows magnitude? — it
> does, even out-of-fold: an honest, leakage-free gain of +0.215, confidence interval above zero."

**Number cascade (say the level that fits your pacing; all three are in the paper):**
- **On-screen headline (most intuitive):** regulator recovery AUPRC **0.415 → 0.722**.
- **Authoritative pre-specified test (M → M+C incremental):** bootstrap gain **+0.357 [+0.117, +0.538]**, P>0 = 1.000, expression-matched negatives.
- **Leakage-free / reviewer-proof (out-of-fold, everything refit per fold):** **+0.215 [+0.074, +0.560]**, permutation p = 0.010 — the conservative number, ~0.18 of the apparent gain is optimism, and we say so.

*Judge-question readiness:* if asked "isn't that overfit on 13 positives?" the answer is Screen 3's
third bullet — we already ran the out-of-fold test and reported the shrinkage honestly. That exchange
*is* the "knows when not to call PASS" thesis in miniature.

## SCREEN 4 — 1:45–2:20 · The scope map (the differentiator: knows where it fails)
**On screen:** `figures/layer_verdict_map.png` (the 7-verdict table).
**Say:**
> "But the contribution isn't a universal score — it's a tested *scope map*. We ran the same
> adjudication everywhere the claim could break. It PASSES in the RNA anchor. It FAILS in non-immune
> systems. It FAILS on an independent external gene set — those regulators are magnitude-visible. As a
> protein-layer test it FAILS, direction-aware — a high score from an inverted feature is not a PASS.
> Every verdict is honest, including the negatives."

## SCREEN 5 — 2:20–2:45 · Controller ≠ target (the 4D framework)
**On screen:** `figures/controller_convergence_quadrant.png` — point at IRF1.
**Say:**
> "So we built a decision framework that keeps four questions separate: does it control, does it point
> the right way, is it safely targetable, does it matter clinically? The lesson is one picture: IRF1
> is our #1 controller — and it points the *wrong* way. Strong control is not a therapeutic target.
> The framework says so out loud, and the classes are stable across every threshold we tried."

## SCREEN 6 — 2:45–3:00 · The clinical null + the lesson (impact)
**On screen:** clinical NULL line (study-out AUROC 0.533) → repo + MIT license + Claude skill.
**Say:**
> "We even tested it as a CAR-T response biomarker across 87 patients — and report a well-powered
> null, because a confounded positive is worse than an honest negative. That discipline is the
> product. A good scientific agent knows when *not* to call PASS — and every step here is a
> reproducible, open Claude skill anyone can run."

---

## Recording notes
- Screen-record each figure at full resolution; zoom on the AUPRC jump (Screen 3) and on IRF1 (Screen 5).
- One `git log --oneline` scroll somewhere in Screen 6 shows the timestamped commit history.
- Pace ~155 wpm; the 6 blocks land at 3:00. If long, trim Screen 2 first (the failure can be one sentence).
- Figures to have open, in order: (2) three-negatives / magnitude gap → (3) `outputs/fig_central.png` →
  (4) `figures/layer_verdict_map.png` → (5) `figures/controller_convergence_quadrant.png` →
  (6) clinical null + repo.

## 100–200 word written summary (for the submission form)
> ISCI separates genes that *control* T-cell state from genes whose perturbation merely produces a
> large effect, on Marson's genome-scale CD4+ Perturb-seq. A first multiplicative index failed —
> beaten by effect-magnitude, because the known-regulator ground truth is magnitude-confounded. The
> fix was a conditional test: among equal-magnitude perturbations, real regulators are more
> axis-specific and more donor-reproducible — a signal orthogonal to effect size that lifts regulator
> recovery from AUPRC 0.415 to 0.722. The pre-specified incremental test (does controllership add to a
> model that already knows magnitude?) gives +0.357 [+0.117, +0.538]; hardened out-of-fold, with every
> step refit per fold, it holds at a leakage-free +0.215 [+0.074, +0.560] (permutation p = 0.010) —
> we report the shrinkage rather than hide it. Crucially, the deliverable is a *tested scope map*, not a universal score: the property
> FAILS in non-immune systems, on an external gene set, and at the protein layer (direction-aware),
> and returns a well-powered NULL as a CAR-T response biomarker. A 4D decision framework
> (controller → convergence → targetability → clinical relevance) shows the #1 controller, IRF1,
> points the wrong way — control is not a target. Claude ran every step, caught its own leakage, and
> welded provenance to every figure. The lesson: a good scientific agent knows when not to call PASS.
