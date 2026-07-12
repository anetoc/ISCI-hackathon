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

