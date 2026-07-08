# Reproducible & scalable CCI pipeline — add a dataset in one config block

**Goal:** make the Conditional Controllability Invariant test a *pipeline*, not a series of
hand runs. Anyone can add a new dataset (another Perturb-seq screen, another disease system)
by editing one YAML block; the runner produces a canonical result; the dashboard aggregates
every result into one visual. This is the "scale to other datasets + make it visual" layer.

## The three pieces

### 1. Dataset registry — `config/datasets.yaml`
One block per dataset. Fields: `id`, `label`, `system` (immune|non-immune — this is the
falsifiable prediction axis), `path`, `adapter`, positive-set source, and your
**pre-registered** `expected_verdict`. A copy-paste template sits at the bottom of the file.
Adding a dataset = adding a block. No code change for standard Perturb-seq `.h5ad` inputs.

### 2. Canonical per-dataset result — `outputs/<id>/cci_result.json`
Every run — whether local or on the GPU machine via Claude Code — writes the SAME schema:
```json
{"id","label","system","perturbation","n_pos",
 "delta_auprc","ci_lo","ci_hi","lr_p","spearman_mag","verdict","report"}
```
This canonical contract is what makes results from different machines/sessions
interoperable. The runner (`isci/run_cci.py`, to be wired to the registry) calls the same
locked helpers from the `isci-controllership` skill (`conditional_lr_test`,
`expression_matched_negatives`, `bootstrap_auprc_gain`) so the *method* is identical across
datasets — only the data changes.

### 3. Visual aggregation — `isci/build_dashboard.py`
Scans `outputs/*/cci_result.json` (+ the seeded `cci_runs.json`) and emits:
- **`outputs/dashboard/cci_dashboard.html`** — self-contained interactive table (verdict
  pills, ΔAUPRC forest bars with CIs), no server needed; open in any browser.
- **`figures/cci_dashboard_static.png`** — a static forest plot for the paper/README.

Re-run `python isci/build_dashboard.py` after any new dataset finishes; the page updates
itself. The current state (4 datasets, 1 PASS, immune-scoped) is shown below.

![CCI cross-dataset dashboard](figures/cci_dashboard_static.png)

## How to add a dataset (the whole loop)
1. Put the `.h5ad` under `data_public/<name>/` (server-side download on the GPU machine for
   big files; CPU-local for anything ≤ a few GB).
2. Add a block to `config/datasets.yaml` with your pre-registered `expected_verdict`.
3. Run the CCI test (`isci/run_cci.py --id <your_id>`), which writes `outputs/<id>/cci_result.json`.
4. `python isci/build_dashboard.py` → the dashboard now includes your dataset.
5. Commit `outputs/<id>/` + the updated dashboard; push.

## Why this design (reviewer-facing)
- **Falsifiability is built in:** each dataset carries a *pre-registered* prediction
  (immune→PASS, non-immune→FAIL); the dashboard shows prediction vs outcome, so the property
  can be broken by the next dataset — that is the point.
- **Method is frozen, data is free:** the same skill helpers run on every dataset, so a new
  PASS/FAIL can't come from a method tweak. Only the input changed.
- **Machine-agnostic:** the canonical JSON contract means a result computed on the RTX 6000
  via Claude Code drops into the same dashboard as a CPU-local result.

## What is scaffolded vs wired
- **Done & populated with real results:** registry (4 datasets), canonical seed
  (`outputs/dashboard/cci_runs.json`), dashboard generator (HTML + static PNG).
- **To wire next:** `isci/run_cci.py` as a thin driver that reads the registry, dispatches to
  the adapter, calls the locked helpers, and writes `cci_result.json` — so steps 3–4 above are
  one command. The scientific core (the helpers) already exists and is locked; this is glue.
