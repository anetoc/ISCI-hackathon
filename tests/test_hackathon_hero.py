import json

from scripts.plot_hackathon_hero import DEFAULT_MANIFEST, build_figure


def test_hero_figure_is_16_by_9_and_uses_locked_numbers():
    """The stage figure must remain widescreen and sourced from the claim manifest."""

    manifest = json.loads(DEFAULT_MANIFEST.read_text())
    figure = build_figure(manifest)
    width, height = figure.get_size_inches()
    visible_text = {text.get_text() for text in figure.axes[0].texts}

    assert width / height == 16 / 9
    assert "Full-sample M→M+C  +0.357" in visible_text
    assert "Leakage-free OOF  +0.215" in visible_text
    assert {"PASS", "FAIL", "NULL", "NOT-EVALUABLE"}.issubset(visible_text)
