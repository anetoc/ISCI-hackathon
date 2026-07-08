#!/usr/bin/env python
"""Aggregate every outputs/*/cci_result.json (+ the seeded cci_runs.json) into one
self-contained HTML dashboard. Re-run after any new dataset finishes:
    python isci/build_dashboard.py
"""
import json, glob, os, datetime, html

VCOLOR = {"PASS": "#2e7d32", "NEAR-MISS": "#f9a825", "FAIL": "#c62828",
          "QUEUED": "#9e9e9e", None: "#9e9e9e"}


def load_runs():
    runs = {}
    seed = "outputs/dashboard/cci_runs.json"
    if os.path.exists(seed):
        for r in json.load(open(seed)):
            runs[r["id"]] = r
    for f in glob.glob("outputs/*/cci_result.json"):   # per-dataset canonical results
        r = json.load(open(f))
        runs[r["id"]] = r
    return list(runs.values())


def bar(delta, lo, hi, w=260, span=(-0.1, 0.5)):
    def x(v):
        return (v - span[0]) / (span[1] - span[0]) * w
    xl, xh, xd, xz = x(lo or 0), x(hi or 0), x(delta), x(0)
    return ('<svg width="%d" height="26">'
            '<line x1="%.1f" y1="0" x2="%.1f" y2="26" stroke="#bbb" stroke-dasharray="3"/>'
            '<line x1="%.1f" y1="13" x2="%.1f" y2="13" stroke="#555" stroke-width="2"/>'
            '<circle cx="%.1f" cy="13" r="5" fill="#1565c0"/></svg>'
            % (w, xz, xz, xl, xh, xd))


def build():
    runs = load_runs()
    order = {"PASS": 0, "NEAR-MISS": 1, "FAIL": 2, "QUEUED": 3, None: 3}
    runs.sort(key=lambda r: (r.get("system", ""), order.get(r.get("verdict"), 3)))
    rows = ""
    for r in runs:
        v = r.get("verdict") or "QUEUED"
        c = VCOLOR.get(v, "#9e9e9e")
        d, lo, hi = r.get("delta_auprc"), r.get("ci_lo"), r.get("ci_hi")
        ci = "[%+.3f, %+.3f]" % (lo, hi) if lo is not None else "&mdash;"
        dtxt = "%+.3f" % d if d is not None else "&mdash;"
        lrp = r.get("lr_p")
        lrp = ("%.1e" % lrp) if isinstance(lrp, (int, float)) else "n.s."
        rows += ('<tr><td><b>%s</b><br><span class=sub>%s</span></td>'
                 '<td>%s</td><td class=num>%s</td><td class=num>%s</td>'
                 '<td class=num>%s</td><td>%s</td>'
                 '<td><span class=pill style="background:%s">%s</span></td></tr>'
                 % (html.escape(r.get("label", r["id"])),
                    html.escape(r.get("perturbation", "")),
                    html.escape(r.get("system", "")), dtxt, ci, lrp,
                    bar(d or 0, lo, hi), c, v))
    npass = sum(1 for r in runs if r.get("verdict") == "PASS")
    CSS = ("body{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:2rem;"
           "color:#222;max-width:1000px}h1{font-size:22px;margin-bottom:.2rem}"
           ".sub{color:#888;font-size:12px}table{border-collapse:collapse;width:100%;margin-top:1rem}"
           "th,td{padding:.5rem .6rem;border-bottom:1px solid #eee;text-align:left;vertical-align:top}"
           "th{font-size:12px;text-transform:uppercase;color:#666}.num{font-variant-numeric:tabular-nums}"
           ".pill{color:#fff;padding:.15rem .5rem;border-radius:10px;font-size:12px;font-weight:600}"
           ".hdr{background:#f5f7fa;padding:1rem;border-radius:8px}.key{font-size:13px;color:#555;margin-top:.6rem}")
    head = ("<!doctype html><meta charset=utf-8><title>CCI dashboard</title><style>" + CSS + "</style>"
            "<div class=hdr><h1>Conditional Controllability Invariant &mdash; cross-dataset dashboard</h1>"
            "<div class=sub>Generated " + str(datetime.date.today()) + " &middot; " + str(len(runs))
            + " datasets &middot; " + str(npass) + " PASS &middot; immune-scoped property</div>"
            "<div class=key>Each row = one dataset through the identical magnitude-conditional CCI test. "
            "&Delta;AUPRC = regulator-recovery gain of the orthogonal signal over the effect-magnitude "
            "baseline; bar shows &Delta;AUPRC (dot) with 95% bootstrap CI (line), dashed = 0 (no gain). "
            "<b>Prediction:</b> immune state-transition systems PASS, cell-autonomous systems FAIL.</div></div>"
            "<table><tr><th>Dataset</th><th>System</th><th>&Delta;AUPRC</th><th>95% CI</th><th>LR p</th>"
            "<th>gain vs magnitude</th><th>verdict</th></tr>")
    doc = (head + rows + "</table><p class=sub>Add a dataset: edit config/datasets.yaml, "
           "run isci/run_cci.py, rebuild this page.</p>")
    os.makedirs("outputs/dashboard", exist_ok=True)
    open("outputs/dashboard/cci_dashboard.html", "w").write(doc)
    print("wrote outputs/dashboard/cci_dashboard.html (%d datasets, %d PASS)" % (len(runs), npass))


if __name__ == "__main__":
    build()
