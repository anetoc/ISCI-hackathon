# Historical D0 analysis — deprecated

These files preserve the first ISCI formulation for scientific transparency. The D0 score combined
directional movement, quality and reproducibility with a rank product. Under native matched
negatives it lost to effect magnitude (AUPRC 0.35 versus 0.41), so it was rejected rather than
retuned after seeing the benchmark.

This directory is an archive, not a supported execution path. The current method is documented in
`../../docs/method.md`; the frozen result hierarchy is in `../../reports/result_lock.md`; and the
supported reusable interface is the `isci` CLI.

Archived files:

- `run_d0.py` — original one-off driver; retained as history and not expected to run against the
  current package layout.
- `manifest_d0.json` — provenance of the failed D0 run.
- `d0_benchmark.json` — comparison against magnitude.
- `isci_d0_ranked.csv` — historical ranking, not a final deliverable.
- `index.py` and `baselines.py` — original aggregation/baseline helpers removed from the wheel.

