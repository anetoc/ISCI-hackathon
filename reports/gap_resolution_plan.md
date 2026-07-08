# Gap-resolution plan — a senior-scientist triage (2.5 days to deadline)

The teammate's review is correct and mature. My job here is not to re-list the 5 gaps as
equals, but to **triage them** the way a PI decides where a lab's last week goes. The governing
principle: **the central claim is already defensible.** CCI = an immune-scoped controllability
property, locked, replicated 3 conditions, with a clean cross-dataset boundary. Every gap below
is about *extending* that claim, not about whether it holds. So the strategic error to avoid is
burning the last 2.5 days on an extension that, if it fails, doesn't touch the core — while
leaving the demo (30% of the score) thin.

Triage against the rubric (Demo 30 / Impact 25 / Claude-Use 25 / Depth 20):

---

## TIER A — close before Sunday (bankable; mostly CPU-local, machine-independent)

**A1. Clinical bridge (Gap 2) — run Brief 04 as a falsification test, not a positive hunt.**
This is the single highest-Impact action and the brief is already written + pre-registered.
Design is locked *before* looking at the result: endpoint `Max_Response` R vs NR, patient-level,
**leave-one-STUDY-out as the decisive test** (severe study confound: 22/27 NR from 2 studies),
baselines study/disease/CD8/magnitude, within-NHL primary. **Either outcome strengthens the
submission:** a PASS that survives leave-study-out is a real biomarker signal; a well-powered
NULL (n=87 vs the old n=9) retires the D4 negative honestly and confirms CCI is causal
biology, not a clinical predictor. *Runs on CPU — does not wait for the GPU.*

**A2. Reproducibility (Gap 5) — but the honest fix is DEPRECATE, not implement.**
The 7 `NotImplementedError` stubs live entirely in the **legacy M/R/D/A/S modules**
(`stability.py`, `insilico.py`, `network.py`, `validate.py`) — the multi-component index that
**lost to magnitude and was abandoned**. Implementing dead code would be dishonest padding.
The right move: (a) mark those modules deprecated with a header pointing to the locked method;
(b) wire `isci/run_cci.py` as the one-command driver around the **real** locked helpers
(`conditional_lr_test`, `expression_matched_negatives`, `bootstrap_auprc_gain`) + the dataset
registry + dashboard. Result: "the validated method runs by one command," which is what a
reviewer actually checks. Serves Demo + Claude-Use directly.

**A3. Overclaim guard (Gap 4) — lock the framing everywhere (cheap).**
Every mention of IKBKB/KDM1A/PRKDC etc. must read as *hypothesis-generating triage for
titratable manufacturing/experimental perturbation*, never "inhibit in the patient." One pass
over targetability doc + README + dossier + the clinical disclaimer. This closes the biggest
attack surface for near-zero cost.

**A4. Demo (rubric: 30%).** The 3-min narrative: input → core figure → result-lock → evidence
card → **honest negative** → next test. The reproducible dashboard (cross-dataset scope) and
the credibility ledger are the visual spine. This is where marginal effort pays the most.

---

## TIER B — close IF a good dataset is reachable (one focused attempt)

**B1. A better immune external validation than Schmidt (Gap 1).**
Schmidt is underpowered (n_pos=10). The ideal next system is a CD8 / CAR / TIL perturbation
screen with a clear functional axis and donor structure. The scalable pipeline we just built
(`config/datasets.yaml` → `run_cci.py` → dashboard) exists precisely so that adding one is a
config block. **Action: scout for ONE feasible immune Perturb-seq/Perturb-CITE-seq with donor
structure** (candidates to check: Frangieh Perturb-CITE-seq melanoma TILs; any CD8 exhaustion
CRISPR screen with replicates). If it downloads and runs in a day → add it, and the dashboard
gains a 5th point that either extends the immune-PASS boundary or informatively refines it.
If nothing suitable is reachable in time → document as the pre-registered next validation.
*Do not force this; a 4-system boundary with an honest "next test" is already a complete story.*

---

## TIER C — honest roadmap (state explicitly; do NOT fake in-window)

**C1. Phospho/TCR validation (Gap 3).** RNA is a proxy for what is fundamentally
phospho-signaling. No phospho-**perturbation** dataset is reachable in a week. The correct
scientific posture is a **pre-registered next experiment**: measure pLCK, pZAP70, pLAT,
pPLCγ1, pERK, pS6, NF-κB p65 (phosphoproteomics or CyTOF/CITE) and test whether CCI controllers
modulate the *timing/intensity window* of TCR signaling — not whether "TCR genes are targets."
Turning a limitation into a specific falsifiable experiment is a Researcher-Track strength.

**C2. Prospective / deeper clinical validation.** Beyond the atlas retrospective — a roadmap
item requiring controlled-access or collaborative cohorts (e.g. dbGaP phs002966 TIMING+scRNA).

---

## Positioning against the literature gaps

- **vs CEFCON** (Nat Commun 2023, network control of fate-driver regulators from scRNA GRN):
  same *goal* (find drivers, not markers), different *evidence class*. CEFCON infers control
  from a reconstructed GRN; we test it with **causal perturbation + magnitude-conditional
  falsification + a domain boundary**. Cite it as the closest prior; our differentiator is that
  we can be *wrong by dataset* — and show where.
- **vs FOXO1 master-regulator of CAR-T memory** (Nature 2024): external corroboration, not
  competition. Our clean `A_persist` axis is built from exactly these memory/stem genes
  (TCF7, LEF1, FOXO1, SELL, IL7R…). That an independent Nature paper names FOXO1 the master
  regulator of the same program the persistence axis captures is convergent support that the
  axis is biologically real — worth citing as such.

---

## The recommendation in one line

Bank Tier A (clinical falsification test + honest reproducible package + overclaim lock +
demo). Attempt Tier B only if one good immune dataset is genuinely reachable. Declare Tier C as
pre-registered next experiments. **Do not let the pursuit of an extension weaken the locked
core or the demo — the discreet, falsifiable, reproducible finding is the submission.**
