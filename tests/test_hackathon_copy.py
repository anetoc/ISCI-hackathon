import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_stage_script_is_six_scenes_and_within_two_thirty_word_budget():
    """Keep the spoken path short enough to survive normal live-demo pacing."""

    text = (ROOT / "DEMO_SCRIPT.md").read_text()
    spoken_lines = [line.removeprefix("> ") for line in text.splitlines() if line.startswith("> ")]
    spoken_words = re.findall(r"\b[\w+.–-]+\b", " ".join(spoken_lines))

    assert text.count("## SCENE ") == 6
    assert 300 <= len(spoken_words) <= 380
    for value in ("+0.357", "+0.215", "0.415→0.722", "+0.229"):
        assert value in text


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
