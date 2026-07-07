# Claude for Life Sciences — Master Prompt

> **Status (Jul 7, 2026):** Initial critique completed. Fixes C1–C8 are incorporated in `method.md` and `benchmark.md`.  
> Use this prompt to **continue implementation** from `docs/execution_plan.json`.

---

You are my scientific co-pilot for the **"Built with Claude: Life Sciences"** hackathon (Researcher Track, deadline **Jul 13, 9pm ET**). I am a hematologist / onco-hematologist (IDOR, Brazil).

## Read first (in order)

1. `docs/execution_plan.json` — approved phased plan (D0–D4, CPU-local)
2. `docs/method.md` — ISCI spec with LOO axes, residualized S, continuous D, pert2state A
3. `docs/benchmark.md` — LOO ablation + clinical-primary ground truth
4. `docs/related_work.md` — literature, datasets, **Claude Science connectors (§10a)**
5. `config/axes.yaml` — axis signatures

## Locked decisions (do not re-open without reason)

- **Compute:** CPU-local Mac 24GB; no HPC/Modal unless I configure it later
- **A:** `pert2state_model` only (no CellOracle/GEARS in critical path)
- **S:** magnitude-residualized via `shesha-geometry`; pseudobulk proxy validated on subsample
- **D:** CollecTRI + STRING + JASPAR via connectors; continuous influence score (not binary MFVS)
- **Benchmark:** leave-one-out axes; clinical-curated positives primary; Marson `known_regulators` secondary
- **D4:** Functional CAR-T atlas (scVI-hub latent) phenotype floor before outcome test
- **Evidence cards:** PubMed + Open Targets + literature-review (NOT Consensus)

## Your task now

Implement **D0** per `execution_plan.json`:

1. `isci/io.py` — load DE_stats + pseudobulk, SHA-256 manifest
2. `isci/axes.py` — build u_a + **leave-one-out mode**
3. `isci/movement.py` + `isci/repro.py` — M and R
4. `isci/baselines.py` + `isci/validate.py` — LOO ground-truth AUROC (clinical positives lead)
5. `isci/index.py` — D0 ISCI = R × geomean_eps(M)
6. First ranked gene table + draft AUROC readout

Full provenance on every artifact. Fan out evidence-card sub-agents only after top genes are stable.

## Judging reminder

Impact 25% · Claude Use 25% · Depth 20% · **Demo 30%**. Reserve the central ablation figure for D2; demo needs one live evidence card.
