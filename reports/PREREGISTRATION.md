# Pre-registration — Conditional Controllability Invariant (CCI) test protocol

> **What this document is, honestly.** This is a **frozen analysis protocol** with two tiers:
> (A) a transparent *retrospective specification* of the tests already run — their criteria were
> fixed in code before adjudication ("pre-specified"), and the git history is the evidence; and
> (B) a genuine **pre-registration** of tests **not yet run** (results do not exist at commit
> time), so their PASS/FAIL criteria and directional predictions are locked here *before* the data
> is touched. We do **not** relabel completed work as "pre-registered" — the distinction is the
> whole point.
>
> **Timestamp.** The authoritative timestamp is this file's **git commit SHA** (immutable once
> pushed to GitHub). To additionally mint a citable DOI, cut a GitHub Release and enable the
> Zenodo–GitHub integration (this archives the tagged commit and issues a DOI). That step needs the
> repository owner's GitHub/Zenodo authorization and is therefore left to the maintainer; see
> "How to mint the DOI" at the end.

---

## 1. The frozen protocol (applies to every dataset, run or unrun)

**Object.** For a perturbation screen with per-perturbation effect statistics and a functional
state axis (a signed gene set), define per perturbation `g`:
- `M(g)` = effect **magnitude** (e.g. number/size of DE genes).
- `S(g)` = **axis-specificity** (alignment of the perturbation's effect with the state axis,
  leave-marker-out to avoid label leakage).
- `R(g)` = **cross-replicate reproducibility** (e.g. cross-donor / cross-guide coherence).
- Residualize `S, R` on `M`; form `C = mean(Sᵣ, Rᵣ)` on the **detectable** subset
  (magnitude ≥ dataset-median n-DE).

**Positives / negatives (mandatory, no exceptions).**
- Positives = a **credible, externally-defined regulator label set** for the cell type. *If no
  credible regulator set exists, the test has no positives and is NOT RUN* (NOT-EVALUABLE — never
  invent labels).
- Negatives = **expression/power-matched** non-regulators via the locked
  `expression_matched_negatives` helper (match on `target_baseMean` + `n_cells_target`), the same
  matching used in every CCI test. Un-matched negatives reintroduce the magnitude confound and are
  disallowed.

**Decision rule (fixed).** The property **HOLDS (PASS)** in a system iff **all three**:
1. bootstrap **ΔAUPRC(M → M+C) > 0 with 95% CI excluding 0** (1,000 resamples), AND
2. **conditional LR p < 0.05** (does C add over M for regulator status), AND
3. **|Spearman(C, M)| small** (C is orthogonal to magnitude, i.e. not an effect-size proxy).

It is **FAILED** if any condition fails. It is **NOT-EVALUABLE** if the intake gate (effect
matrix + credible positives + matched negatives + clean axis) is not met. A FAIL/NOT-EVALUABLE is a
**boundary**, reported as such — the goalposts do not move.

**Method is frozen in code.** All statistics come from `skills/isci-controllership/kernel.py`
(`bootstrap_auprc_gain`, `expression_matched_negatives`, `conditional_lr_test`). Only data varies.
One-command driver: `python isci/run_cci.py`.

---

## 2. Tier A — retrospective specification of COMPLETED tests (already adjudicated)

These are **pre-specified, not pre-registered** (criteria fixed in code before the result; git
history is the record). Reported for full transparency; numbers are locked in `result_lock.md` and
`outputs/dashboard/cci_runs.json`.

| System | Domain | Predicted before run | Result | Verdict |
|---|---|---|---|---|
| Marson CD4+ | immune (anchor) | property holds | ΔAUPRC +0.229 [0.072,0.405], LR<1e-4, ρ+0.02 | **PASS** |
| Schmidt CRISPRa | immune | same-sign (power-limited) | +0.138 [−0.029,0.434], LR n.s. | near-miss |
| Norman K562 | non-immune (differentiation) | weaker/absent | +0.138 [−0.033,0.370], LR 0.013, signal from R not S | **FAIL** |
| Replogle RPE1 | non-immune (proliferation) | absent | +0.060 [−0.013,0.204], LR 0.195 | **FAIL (robust)** |
| Frangieh Perturb-CITE | immune (evasion) | same-sign (power-limited) | +0.118 [−0.018,0.336], LR n.s. | near-miss |

Pre-stated ordering (immune > differentiation > proliferation) was met.

---

## 3. Tier B — GENUINE PRE-REGISTRATION of tests NOT YET RUN

Results do not exist at this commit. Criteria and directional predictions are locked **now**.

### B1 — Non-T immune far-test (scope-sharpening; decisive either way)
- **Question:** does CCI hold in a **non-T immune** screen (myeloid / macrophage / DC / NK)?
- **Design:** identical frozen protocol; positives = canonical regulators of the chosen cell type's
  functional axis (e.g. M1/M2 polarization, DC maturation, NK cytotoxicity); expression-matched
  negatives; leave-marker-out axis.
- **Pre-stated predictions (locked):**
  - **PASS** ⇒ the property is **immune-wide** ("immune relational state transitions"), not
    T-cell-specific. This *widens* the claim.
  - **FAIL** ⇒ the property is **T-cell-scoped** ("T-cell state controllability"). This *tightens*
    the claim. **Prediction: we expect PASS** (the mechanistic story is relational-state, not
    T-cell-idiosyncratic), and will report a FAIL honestly as a boundary if observed.
- **Stop rule:** if no dataset meets the intake gate within the feasibility window, this is
  declared NOT-EVALUABLE-BY-DEADLINE and remains pre-registered for later — not forced.

### B2 — CD8 / CAR-T Perturb-seq immune replication (Paper-2 keystone)
- **Question:** does CCI replicate in a **well-powered CD8/CAR-T** human screen (replacing
  underpowered Schmidt, n_pos=10)?
- **Pre-stated prediction (locked): PASS**, same immune axis-specificity component S carrying the
  signal (S significant, not just R). A FAIL, or a signal carried by R alone, would **bound** the
  claim to CD4+ and is reported as such.

### B3 — Functional P3 (transcriptional score → measured killing/synapse)
- **Question:** does a TSC/IEC transcriptional score predict **functional** serial-killing / synapse
  quality **beyond magnitude and beyond a CD8-identity baseline**?
- **Pre-stated criteria (locked):** PASS iff score beats magnitude AND beats CD8-fraction baseline
  on held-out data (bootstrap ΔAUROC CI excludes 0). **Prediction: uncertain** — the two functional
  proxies to date (BEHAV3D, clinical CAR-T) returned NULLs that bound the claim; a clean PASS
  requires paired perturbation→function data (dbGaP phs002966 or wet-lab). Registered so the verdict
  cannot be back-fitted.

---

## 4. Deviations log
*(Append any protocol deviation here with date + reason. Empty at registration.)*
- none.

---

## How to mint the DOI (maintainer action)
1. Push this file; the commit SHA is the primary timestamp.
2. On GitHub: **Releases → Draft a new release**, tag e.g. `prereg-v1`.
3. Enable **Zenodo ↔ GitHub** for the repo (zenodo.org/account/settings/github) *before* publishing
   the release; publishing then auto-archives the tagged commit and issues a DOI.
4. Add the DOI badge here and in `CLAIM_LEDGER.md` (replacing the "no OSF/Zenodo timestamp" caveat
   for Tier B).
