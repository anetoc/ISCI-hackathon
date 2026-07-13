# Claude for Life Sciences — historical initial prompt

> **Historical record:** this prompt preserves the initial five-component design. That design later
> failed against magnitude and is not the current implementation contract. Use `AGENTS.md`,
> `docs/method.md` and `reports/result_lock.md` for current work.

---

You are my scientific co-pilot for the **"Built with Claude: Life Sciences"** hackathon (Researcher Track, deadline **Jul 13, 9pm ET**). I am a hematologist / onco-hematologist (IDOR, Brazil).

## Read first (in order)

1. `archive/d0/README.md` — record of why the initial D0 method was rejected
2. `docs/method.md` — current magnitude-conditional ISCI contract
3. `docs/benchmark.md` — current benchmark and leakage-control contract
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
4. `archive/d0/baselines.py` + `isci/validate.py` — original proposed benchmark path
5. `archive/d0/index.py` — original D0 aggregation, now rejected
6. First ranked gene table + draft AUROC readout

Full provenance on every artifact. Fan out evidence-card sub-agents only after top genes are stable.

## Judging reminder

Impact 25% · Claude Use 25% · Depth 20% · **Demo 30%**. Reserve the central ablation figure for D2; demo needs one live evidence card.
