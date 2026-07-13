import re
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]


def test_internal_production_material_is_not_part_of_the_public_repository():
    """Keep recording, rehearsal and form-production material outside the research package."""

    internal_paths = [
        "DEMO_SCRIPT.md",
        "ELEVENLABS_PACKAGE.md",
        "ELEVENLABS_SCRIPT_SHORT.md",
        "HACKATHON_RUNBOOK.md",
        "JUDGE_QA_REHEARSAL.md",
        "RECORDING_SCRIPT.md",
        "VIDEO_NARRATION.md",
        "VIDEO_SCRIPT_FINAL.md",
        "scripts/build_final_narrated_video.py",
        "scripts/build_hackathon_video.py",
        "scripts/validate_submission_video.py",
        "outputs/hackathon/video_manifest.json",
        "demo_assets/hackathon/hackathon_fallback_2m42.mp4",
    ]
    assert not [path for path in internal_paths if (ROOT / path).exists()]


def test_every_judge_card_has_evidence_limitation_and_overclaim_boundary():
    """Fast answers remain auditable instead of becoming improvised sales claims."""

    text = (ROOT / "JUDGE_QA.md").read_text()
    assert len(re.findall(r"^## Q\d+", text, flags=re.MULTILINE)) == 10
    assert text.count("**Answer:**") == 10
    assert text.count("**Evidence:**") == 10
    assert text.count("**Limitation:**") == 10
    assert text.count("**Do not say:**") == 10


def test_submission_summary_stays_within_form_limit():
    """The submission copy should not be truncated by a 150-word field."""

    text = (ROOT / "SUBMISSION.md").read_text()
    summary = text.split("## 150-word summary", 1)[1].split("---", 1)[0]
    words = re.findall(r"\b[\w+→-]+\b", summary)
    assert 140 <= len(words) <= 150


def test_public_related_work_is_not_mixed_with_portuguese_planning_copy():
    """Keep the public English document separate from any future pt-BR translation."""

    text = (ROOT / "docs" / "related_work.md").read_text()
    portuguese_markers = [
        "Objetivo:",
        "Pergunta-chave",
        "Por que importa",
        "Como abordar",
        "dúvidas de regras",
        "obrigatórias para",
        "prêmio Gladstone",
        "não são nosso foco",
        "Parceiros técnicos",
    ]
    assert not [marker for marker in portuguese_markers if marker in text]


def test_judge_surfaces_use_one_product_name_and_one_method_name():
    """Historical research labels belong in the evidence archive, not the stage vocabulary."""

    surfaces = [
        ROOT / "README.md",
        ROOT / "DELIVERABLE.md",
        ROOT / "SUBMISSION.md",
        ROOT / "JUDGE_QA.md",
        ROOT / "SUMMARY.md",
        ROOT / "config" / "hackathon_claims.yaml",
        ROOT / "outputs" / "hackathon" / "claim_manifest.json",
        ROOT / "docs" / "hackathon_judge_demo.template.html",
        ROOT / "docs" / "hackathon_judge_demo.html",
        ROOT / "docs" / "tctrl_live_demo.html",
    ]
    secondary_brand = re.compile(r"\b(?:CCI|IEC|TSC)\b|T-REMAP")
    for surface in surfaces:
        match = secondary_brand.search(surface.read_text())
        assert match is None, f"{surface} exposes secondary stage brand {match.group(0)}"

    with ZipFile(ROOT / "outputs" / "tctrl_hackathon_deck.pptx") as deck:
        slide_xml = " ".join(
            deck.read(name).decode("utf-8")
            for name in deck.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        )
    match = secondary_brand.search(slide_xml)
    assert match is None, f"judge deck exposes secondary stage brand {match.group(0)}"


def test_readme_is_a_public_entry_point_with_a_bounded_judge_capsule():
    """Serve judges the submitted demo while preserving the reproducible research path."""

    text = (ROOT / "README.md").read_text()
    start_here = text.split("## Start here", 1)[1].split("## The result", 1)[0]

    for audience in (
        "Hackathon judges",
        "New readers",
        "Researchers",
        "Bring your own data",
        "Scientific reviewers",
    ):
        assert audience in start_here

    judge_row = next(line for line in start_here.splitlines() if "Hackathon judges" in line)
    assert "https://youtu.be/7Rz4PpmQZuI" in judge_row
    assert "interactive overview" in judge_row
    assert "fallback" not in judge_row.lower()
    assert "2:42 narrated demo" in start_here
    assert "deterministic offline" in start_here
    assert "## Repository map — four layers" in text
