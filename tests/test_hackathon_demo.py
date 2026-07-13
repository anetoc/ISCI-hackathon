import json
import struct
from html.parser import HTMLParser
from pathlib import Path

from scripts.build_hackathon_demo import DEFAULT_MANIFEST, DEFAULT_OUTPUT, DEFAULT_TIMING


class SceneCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scenes = 0

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if tag == "section" and "slide" in classes:
            self.scenes += 1


def test_demo_is_offline_and_contains_the_ten_approved_slides():
    """The public demo must reproduce the submitted deck without connectivity."""

    html = DEFAULT_OUTPUT.read_text()
    parser = SceneCounter()
    parser.feed(html)

    assert parser.scenes == 10
    assert "https://" not in html
    assert "http://" not in html
    assert "data:image/png;base64," in html
    assert "PRETEXT_SOURCE_B64" not in html
    assert "~/.claude" not in html
    assert ".failure-grid, .judge-grid, .experiment-grid { display: grid;" not in html
    assert 'params.get("static") === "1"' in html
    assert 'params.get("scene")' in html
    assert 'params.get("autoplay") === "1"' in html
    assert "Interactive T-CTRL judge deck shown in the submitted video" in html


def test_demo_embeds_the_frozen_verdict_contract_and_numbers():
    """Visible claims and the machine manifest must agree exactly."""

    html = DEFAULT_OUTPUT.read_text()
    manifest = json.loads(DEFAULT_MANIFEST.read_text())
    assert [claim["verdict"] for claim in manifest["claims"]] == [
        "PASS",
        "FAIL",
        "NULL",
        "NOT-EVALUABLE",
    ]
    for value in ("+0.357", "+0.215", "−0.281", "0.533", "p=0.138"):
        assert value in html
    assert manifest["axes_sha256"] in html


def test_static_fallback_contains_ten_full_hd_slides():
    """A failed live path must still leave a projector-ready presentation."""

    assets = Path(__file__).resolve().parents[1] / "demo_assets" / "hackathon"
    screenshots = sorted(assets.glob("[0-9][0-9]_*.png"))
    assert len(screenshots) == 10
    for screenshot in screenshots:
        header = screenshot.read_bytes()[:24]
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", header[16:24]) == (1920, 1080)


def test_autoplay_timing_matches_the_submitted_two_minute_forty_two_deck():
    """HTML autoplay and video rendering must consume one shared timing contract."""

    timing = json.loads(DEFAULT_TIMING.read_text())
    assert len(timing["scenes"]) == 10
    assert sum(scene["duration_seconds"] for scene in timing["scenes"]) == 162
    assert timing["target_seconds"] == 162
