from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_headline_surfaces_preserve_the_locked_estimand_hierarchy():
    """Prevent the four valid result summaries from being relabeled as one statistic."""

    surfaces = [
        ROOT / "README.md",
        ROOT / "SUBMISSION.md",
        ROOT / "SUMMARY.md",
        ROOT / "reports/CLAIM_LEDGER.md",
        ROOT / "reports/MASTER_DOSSIER.md",
        ROOT / "docs/tctrl_live_demo.html",
    ]
    required_values = ["+0.357", "+0.215", "0.415", "0.722"]
    for surface in surfaces:
        text = surface.read_text()
        for value in required_values:
            assert value in text, f"{surface.name} missing locked value {value}"


def test_cross_system_surfaces_label_the_matched_metric_separately():
    """Keep the +0.229 comparison metric distinct from the primary M-to-M+C result."""

    surfaces = [
        ROOT / "README.md",
        ROOT / "reports/property_whitepaper.md",
        ROOT / "reports/PREREGISTRATION.md",
    ]
    for surface in surfaces:
        text = surface.read_text()
        assert "+0.229" in text
        assert "matched" in text.lower()
        assert "+0.357" in text


def test_readme_preserves_the_completed_external_scope_boundary():
    """Do not revive the superseded claim that marker ablation preserved the gain."""

    text = (ROOT / "README.md").read_text()
    assert "It does **not** survive" in text
    assert "ΔAUPRC −0.281 [−0.476, −0.073]" in text
    assert "cross-condition replication is within the same dataset" in text
    assert "survives removing regulators that are also axis markers" not in text
