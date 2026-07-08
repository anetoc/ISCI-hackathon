# CLAUDE.md — context for Claude Code running on the institutional machine

You are Claude Code running **on Abel's Ubuntu GPU server** (48 cores, 125 GB RAM,
RTX 6000 Ada 48 GB, working dir `/mnt/dados2/abel-tsc`, ~4.4 TB free, outbound HTTPS
works). Your job is to execute the **heavy compute** for this project that a laptop
cannot. The scientific reasoning and provenance live with Claude Science (the "brain");
you are the "hands". Read this file fully before acting.

## What this project is (do not re-derive — it is settled)

**ISCI → Conditional Controllability Invariant (CCI).** In Perturb-seq, ranking genes by
effect **magnitude** is confounded: known regulators simply have larger effects. The valid
question is whether a feature adds signal **conditional on magnitude**. The CCI: after
conditioning on magnitude M, a reproducible, axis-specific residual signal `C` separates
genes that CONTROL a cell-state transition from genes merely associated with it.

**The locked result (DO NOT modify):**
- Primary deliverable `ISCI_orthogonal` PASSES in immune Marson CD4+ Perturb-seq:
  bootstrap ΔAUPRC +0.229 [0.072, 0.405], conditional LR p<1e-4.
- The property is **immune-scoped** (tested across 4 systems):
  Marson (immune) PASS +0.229 > Schmidt (immune CRISPRa) near-miss +0.138 >
  Norman (non-immune differentiation) near-miss FAIL +0.138 (carried by reproducibility R,
  not axis-specificity S) > Replogle RPE1 (non-immune proliferation) clean FAIL +0.060.
- See `reports/property_whitepaper.md`, `reports/conditional_controllability_invariant.md`
  (formal def + falsification criterion), `reports/generalization_spec.md` (dataset-agnostic
  protocol), `reports/tissue_synapse_capacity.md` (the TSC vision layer).

**TSC (Tissue Synapse Capacity)** is a VISION/HYPOTHESIS layer, NOT a demonstrated result:
CCI may be the "control axis" of a broader latent capacity to build/sustain an immune
synapse. Its decisive test (P3: does a TSC transcriptional score predict FUNCTIONAL
synapse/killing?) needs functional data — that is what the tasks here are about.

## Hard rules (violating these breaks the science)

1. **Never fabricate data, labels, or results.** If a dataset lacks the labels/axis a task
   needs, STOP and report NOT-EVALUABLE. Do not invent positives or clinical outcomes.
2. **Never modify the locked result** (ISCI_orthogonal ranking or the CCI numbers above)
   unless you find a reproducibility bug — then report it, don't silently "fix".
3. **Pre-register before you peek.** Fix the axis, positives, and negatives BEFORE computing
   ΔAUPRC. Magnitude-matched negatives + leave-marker-out axis are mandatory.
4. **Report honestly.** A FAIL / near-miss / NOT-EVALUABLE is a valid, valuable result. Never
   move the goalposts to manufacture a PASS.
5. **Verify every external accession** against its source before relying on it; cite the
   data-availability statement.

## Conventions

- Env: miniforge at `/mnt/dados2/abel-tsc/miniforge3`, conda env `tsc`
  (python 3.12, scanpy/anndata/scikit-learn/pandas/numpy/scipy/pyarrow/gseapy).
- Data downloads **server-side** from public repos (S3/GEO/Zenodo) — never uploaded.
- Each task lives in `briefs/<name>.md` with an explicit protocol + expected outputs.
- Write outputs to `outputs/<task>/` and a short `report.md`; **commit with a clear message**.
- Git identity: `git -c user.name="Abel Costa" -c user.email="anetoc@users.noreply.github.com"`.
- **Sync protocol:** pull before work, commit + push when a task finishes. Abel relays
  results back to Claude Science, who reviews and writes the next brief.

## Tooling — use OUR method skill, not ad-hoc code

This repo ships the project's own skill at `skills/isci-controllership/` (SKILL.md +
kernel.py). It is the **single source of truth** for the CCI method: expression-matched
negatives, leave-marker-out axes, conditional LR test, bootstrap AUPRC gain, movability
gate, clinical reversal score, matched-null enrichment, confounder ledger. **Reuse these
helpers — do not re-implement the statistics.**

- The kernel.py functions are plain numpy/pandas/scipy/sklearn (no external deps). Import
  them directly: `import sys; sys.path.insert(0, "skills/isci-controllership"); import kernel`
  then e.g. `kernel.bootstrap_auprc_gain(...)`, `kernel.expression_matched_negatives(...)`.
- To have Claude Code auto-discover it as a native skill, copy it once:
  `mkdir -p .claude/skills && cp -r skills/isci-controllership .claude/skills/`
  (`.claude/` is machine-local / gitignored — recreate it after a fresh clone).
- Environment: build a pip venv from `envs/requirements_machine.txt` (see its header).
  Heavy GPU extras (scvi-tools, rapids) are listed but commented — install only when a
  task needs cell-level latent estimation on the GPU.

Do NOT install unrelated Claude Code marketplace plugins — they cost context every turn
and add nothing to this analysis. The only tooling we need is this repo's skill + the venv.

## Active task

See `briefs/01_behav3d_p3_proxy.md` — the first job (BEHAV3D GSE172325 as a correlational
proxy for the TSC P3 test). Read it fully; follow its protocol exactly.
