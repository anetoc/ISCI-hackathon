import json

from scripts.build_hackathon_claim_manifest import ROOT, adjudicate, selected_payload, sha256


MANIFEST_PATH = ROOT / "outputs" / "hackathon" / "claim_manifest.json"
CONFIG_PATH = ROOT / "config" / "hackathon_claims.yaml"


def test_frozen_claims_recompute_the_four_distinct_verdicts():
    """The demo may explain verdicts, but it cannot improvise or relabel them."""

    import yaml

    config = yaml.safe_load(CONFIG_PATH.read_text())
    observed = {}
    for claim in config["claims"]:
        verdict, _ = adjudicate(claim, selected_payload(claim))
        observed[claim["claim_id"]] = verdict

    assert observed == {
        "C1-CONTROLLABILITY": "PASS",
        "C2-EXTERNAL-FUNCTIONAL": "FAIL",
        "C3-CART-CLINICAL": "NULL",
        "C4-SCGPT": "NOT-EVALUABLE",
    }


def test_committed_manifest_matches_current_evidence_and_axes():
    """Every stage claim must retain content-addressed provenance."""

    manifest = json.loads(MANIFEST_PATH.read_text())
    assert manifest["axes_sha256"] == sha256(ROOT / "config" / "axes.yaml")
    assert manifest["config_sha256"] == sha256(CONFIG_PATH)
    for claim in manifest["claims"]:
        assert claim["data_sha256"] == sha256(ROOT / claim["evidence_path"])


def test_primary_estimands_remain_visibly_separate():
    """Discovery, OOF and descriptive summaries are different estimands."""

    manifest = json.loads(MANIFEST_PATH.read_text())
    primary = manifest["claims"][0]["metrics"]
    assert primary["authoritative_full_sample"]["discovery_gain"] == 0.357
    assert primary["leakage_free_oof"]["gain"] == 0.2151
    assert "descriptive_auprc" not in primary
