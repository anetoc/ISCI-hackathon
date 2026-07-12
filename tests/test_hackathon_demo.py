import json
import struct
from html.parser import HTMLParser
from pathlib import Path

from scripts.build_hackathon_demo import DEFAULT_MANIFEST, DEFAULT_OUTPUT


class SceneCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scenes = 0

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if tag == "section" and "scene" in classes:
            self.scenes += 1


def test_demo_is_offline_and_contains_six_stage_states():
    """The presentation must remain deterministic even without connectivity."""

    html = DEFAULT_OUTPUT.read_text()
    parser = SceneCounter()
    parser.feed(html)

    assert parser.scenes == 6
    assert "https://" not in html
    assert "http://" not in html
    assert "data:image/png;base64," in html
    assert "PRETEXT_SOURCE_B64" in html
    assert ".failure-grid, .judge-grid, .experiment-grid { display: grid;" not in html
    assert 'params.get("static") === "1"' in html
    assert 'params.get("scene")' in html


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


def test_static_fallback_contains_six_full_hd_scenes():
    """A failed live path must still leave a projector-ready presentation."""

    assets = Path(__file__).resolve().parents[1] / "demo_assets" / "hackathon"
    screenshots = sorted(assets.glob("[0-9][0-9]_*.png"))
    assert len(screenshots) == 6
    for screenshot in screenshots:
        header = screenshot.read_bytes()[:24]
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", header[16:24]) == (1920, 1080)
