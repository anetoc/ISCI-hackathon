# Hackathon recording and submission runbook

## Release object

The stage product is T-CTRL, which computes ISCI (our Immune-State Controllability Index): an auditable scientific-judgment workflow. The live
path, autoplay path, MP4 and static PNGs all consume the same frozen claims and timing contract.

## One-command package gate

```bash
make hackathon-package
```

Expected terminal result:

```text
AUTOMATED_GATES_PASS_HUMAN_GATES_PENDING: 21/21 automated gates passed
```

The status deliberately remains `HUMAN_GATES_PENDING` until the narrated rehearsals, PI wording
approval and logged-out public-link checks are completed.

## Presentation ladder

1. **Live, presenter-controlled:** open `docs/hackathon_judge_demo.html`; use arrow keys.
2. **Autoplay rehearsal:** open `docs/hackathon_judge_demo.html?autoplay=1`.
3. **Timed offline fallback:** open `demo_assets/hackathon/hackathon_fallback_2m30.mp4`.
4. **Manual static fallback:** present `demo_assets/hackathon/01_*.png` through `06_*.png`.
5. **Judge deck:** open `outputs/tctrl_hackathon_deck.pptx`; slides 1–8 form
   the core narrative and slides 9–10 are the judge appendix.

Never invoke a remote model during the stage presentation. The Claude contribution is visible in
the scientific correction history and explanation layer; statistics and gates remain deterministic.

## Recording setup

- Record at 1920×1080, 30 fps, with the browser in full screen.
- Enable Do Not Disturb; close mail, chat, password managers and unrelated browser tabs.
- Use a local copy of the demo and disconnect network after opening it as a final offline check.
- Record microphone on a separate track when possible; avoid background music under scientific claims.
- Keep the cursor still or outside the frame; navigate with arrow keys.
- Read exact confidence intervals from `DEMO_SCRIPT.md`; do not improvise the estimand labels.
- Export H.264/AAC and watch the complete exported file, not only the editing timeline.

Validate the exported narrated file before upload:

```bash
uv run python scripts/validate_submission_video.py /absolute/path/to/final_narrated_demo.mp4
```

To rebuild the approved 10-slide narrated cut from the reviewed continuous audio:

```bash
uv run python scripts/build_tctrl_scope_figure.py
uv run python scripts/finalize_tctrl_hackathon_deck.py
uv run python scripts/build_final_narrated_video.py \
  --audio /absolute/path/to/reviewed_narration.mp3 \
  --output /absolute/path/to/final_narrated_demo.mp4
```

This is intentionally separate from `make hackathon-package`: the package rebuilds the silent,
deterministic visual fallback, while the submission video requires reviewed human narration.
The submitted narrated cut is 2:42 and remains below the form's 3:00 maximum; the deterministic
offline fallback remains fixed at 2:30.

## Three-rehearsal human gate

| Rehearsal | Duration | Number errors | Overclaims | Technical faults | PASS? |
|---|---:|---:|---:|---:|---|
| 1 |  |  |  |  |  |
| 2 |  |  |  |  |  |
| 3 |  |  |  |  |  |

PASS requires all three runs ≤3:00, zero mixed estimands, zero prohibited overclaims and no technical
fault that requires restarting the presentation.

## Final scientific language gate

Required:

- “canonical axis-defining regulators” and “detectable-effect perturbations” on the primary PASS;
- full-sample `+0.357` and OOF `+0.215` identified as different estimands;
- external functional-regulator `FAIL`, clinical `NULL`, scGPT `NOT-EVALUABLE`;
- controller is not therapeutic desirability;
- prospective panel is proposed and synthesis-blocked, not experimentally validated.

Forbidden:

- universal or immune-wide invariant;
- validated biomarker or therapeutic target claim;
- completed off-target result;
- “Claude decided the statistical gate”;
- treating missing scGPT inputs as a biological null.

## Submission checklist

- [ ] `make hackathon-package` passes from the submission commit.
- [ ] PI approves `SUBMISSION.md`, `DEMO_SCRIPT.md` and Scene 6 falsification language.
- [ ] Three narrated rehearsals pass and are logged above.
- [ ] Final recording is watched end-to-end with headphones.
- [ ] Repository is public and opens in a logged-out/private browser.
- [ ] Demo HTML, MP4 and manuscript links open without local filesystem assumptions.
- [ ] No raw `.h5ad`/`.h5mu`, credentials or `.env.secure` files are tracked.
- [ ] Uploaded video permissions allow judges to view without sign-in.
- [ ] Submission preview preserves symbols, confidence intervals and line breaks.
- [ ] Final submit is performed only after the irreversible form preview is approved.
