# Immune Engagement Capacity (IEC) — a measurable, multi-axis immune capacity

**Status: formal definition (Phase 0). This reframes and generalizes the earlier "Tissue
Synapse Capacity" (TSC) note.** The BEHAV3D P3 proxy result forced the generalization: the
single composite "synapse capacity" score failed because it averaged over axes that are
*independent*. The honest structure the data show is not one axis but a **small set of
orthogonal axes**, each measurable, each with its own controllers. That set is what we name
here.

---

## 1. Why rename TSC → IEC

"Tissue Synapse Capacity" was too narrow in two ways:
1. It implied one thing (synapse assembly), but the measured latent factor is dominated by
   **tissue access (L2, loading +0.99)** and **durable state (L1, +0.37)**, with synapse
   assembly (L3, +0.61) important but not sole — and **killing (L4) loading ≈0** (−0.09),
   i.e. *outside* the shared factor entirely.
2. The BEHAV3D functional proxy showed the composite does **not** predict killing — because
   killing is a **separate axis**, not part of the same capacity.

So the object is not "synapse capacity." It is a **capacity for productive immune
engagement** that decomposes into orthogonal axes. We call it **Immune Engagement Capacity
(IEC)**. (Name is provisional — Abel has veto; alternatives considered: keep "TSC" redefined
as multi-axis, or "T-cell Functional Capacity." IEC is chosen because it is honest about the
*engagement* core the latent factor actually measures, without over-claiming "synapse.")

## 2. Definition

**IEC is a latent immune capacity, defined not as one score but as a vector of orthogonal,
individually-measurable axes.** For a cell (or perturbation, or patient pseudobulk) *x*:

```
IEC(x) = [ A_persist(x),  A_kill(x),  A_resist(x) ]
```

where each axis is a z-scored module score, and — this is the load-bearing claim — the axes
are **empirically orthogonal** (pairwise |Spearman| below a pre-set threshold, e.g. 0.3) so
that no axis is a rename of another or of raw effect magnitude.

| Axis | What it is | Measured from | Empirical anchor |
|---|---|---|---|
| **A_persist** — reach-and-hold | durable memory/stem state + tissue access/egress + synapse-assembly machinery | L1+L2+L3 modules | the shared latent factor (37% var); orthogonal to magnitude (ρ≈0.03) |
| **A_kill** — cytotoxic execution | serial-killing effector program | L4 module (GZMB, PRF1, NKG7, GNLY, IFNG, FASLG, GZMA) | loads ≈0 on the persist factor; separates BEHAV3D killers at AUROC 0.95 |
| **A_resist** — exhaustion-resistance | absence of terminal-exhaustion program | exhaustion module (inverted) | the resistance-module axis from the clinical modules |

**Relation to CCI (the control operator).** IEC axes are *state descriptors*; the
**Conditional Controllability Invariant** identifies which perturbations *control* each axis.
Formally, for each axis A we ask: which genes, when perturbed, move A **reproducibly and
axis-specifically, conditional on effect magnitude** (the CCI test). So:

```
Controllers(A) = { g : CCI(g → A) passes the magnitude-conditional test }
```

IEC says *what the capacity is*; CCI says *what sets it*. This is the connection that makes
the capacity actionable (drugability = tractable controllers of a clinically-relevant axis).

## 3. The null and the falsification criteria

Each axis, and the capacity as a whole, is **falsifiable**. Pre-registered criteria:

- **Orthogonality null.** If two axes have |Spearman| > 0.5 across cells, they are not
  distinct axes — collapse them. (A_persist vs A_kill already pass: killing loads ≈0.)
- **Magnitude null.** If an axis correlates with effect magnitude at |ρ| > 0.3, it is an
  effect-size proxy, not a capacity — reject it. (A_persist passes at ρ≈0.03.)
- **Controllership null (per axis).** If the CCI test for an axis has bootstrap ΔAUPRC CI
  including 0 AND conditional-LR n.s., that axis has no identifiable controllers beyond
  magnitude — report NULL for that axis (as we did for non-immune systems).
- **Clinical null (the decisive, high-risk test).** If no axis predicts treatment response
  under honest patient-level cross-validation better than baselines (magnitude, subset
  fraction, CD8-identity), then IEC is a descriptive capacity but **not** a response
  biomarker — and we say so. This has failed once already (D4, T-state signature,
  CV-AUROC ~chance, underpowered n=9/n=65); the atlas test (Phase 2) is the powered retry.

## 3a. Orthogonality pre-test (pseudobulk, done local) — 2.5 axes, not 3

Before the GPU cell-level run (Brief 02), we tested axis orthogonality on the Marson
pseudobulk (per-perturbation module z-scores) across all three culture conditions. Result
(`outputs/iec_latent/iec_axis_scores_pseudobulk_stim48.csv`, figure below):

![IEC axis orthogonality](figures/iec_axis_orthogonality_pseudobulk.png)

| pair | Rest | Stim8hr | Stim48hr | verdict |
|---|---|---|---|---|
| persist ↔ kill | −0.23 | −0.12 | −0.07 | **orthogonal** (\|ρ\|<0.5) ✓ |
| persist ↔ resist | +0.14 | +0.03 | −0.01 | **orthogonal** ✓ |
| **kill ↔ resist** | **−0.42** | **−0.44** | **−0.50** | **entangled** — fails the \|0.5\| null at 48hr |
| each vs magnitude | — | — | \|ρ\|≤0.13 | all orthogonal to magnitude ✓ |

**Finding:** persistence is a clean, independent axis (orthogonal to both others and to
magnitude, in all three conditions). But **killing and exhaustion-resistance are NOT
independent** — they anti-correlate at ρ≈−0.42 to −0.50 and cross the collapse threshold at
48 hr. Biologically this is the well-known **effector↔exhaustion coupling**: the cytotoxic
program and the terminal-exhaustion program are two ends of one activation-driven continuum,
not separate dials. So IEC is honestly **2.5 axes**: a clean *persistence* axis, plus a
single coupled *effector/exhaustion* axis (killing high ⇄ exhaustion-resistance low). This is
a real structural result, not a modeling failure — and it sharpens the definition: we do not
claim three independent dials when the data show the effector and exhaustion programs are one.

The cell-level scVI run (Brief 02) tests whether this 2.5-axis structure holds at single-cell
resolution and replicates in the CAR-T atlas — the pseudobulk pre-test says it should.

## 4. What would CONFIRM IEC as more than a redescription

- Each axis is orthogonal to the others and to magnitude ✓ (partially shown; to be
  re-confirmed at cell level, Phase 1).
- Each axis has reproducible, axis-specific controllers by the CCI test (shown for the
  immune anchor; A_kill controllers not yet isolated).
- **At least one axis carries clinical signal** the others/baselines don't (Phase 2 — open).
- The controllers of a clinically-relevant axis are enriched for tractable targets with a
  coherent intervention direction (Phase 3).

## 5. Honest positioning

- **Demonstrated so far:** the immune-scoped CCI (a real, falsifiable controllership
  property with a cross-dataset boundary), and the latent structure showing persistence and
  killing are separate axes (BEHAV3D confirms killing is not in the persistence factor).
- **This document's claim:** IEC is the *organizing frame* — a measurable multi-axis
  capacity — not yet a validated response biomarker. The clinical-prediction axis is the
  high-risk, still-open test, and it carries an explicit negative prior.
- **Deliberately not claimed:** that IEC predicts response (not yet tested at power), or that
  any axis is causal in patients (needs perturbation→outcome data we don't have).

**One-line framing:** *Immune Engagement Capacity is a measurable vector of orthogonal
immune-state axes — reach-and-hold persistence, cytotoxic execution, exhaustion-resistance —
whose controllers are identified by the Conditional Controllability Invariant; the open
question is whether any single axis predicts therapy response at patient-level power.*
