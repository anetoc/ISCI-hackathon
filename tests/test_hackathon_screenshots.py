import hashlib
import json
from pathlib import Path

from scripts.capture_hackathon_screenshots import DECK, expected_screenshots, validate_screenshots


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "outputs" / "hackathon" / "screenshot_manifest.json"


def test_screenshots_match_the_approved_judge_deck():
    """The public demo and fallback may not reuse renders from an older deck."""

    manifest = json.loads(MANIFEST.read_text())
    deck = ROOT / manifest["deck_path"]
    assert deck == DECK
    assert hashlib.sha256(deck.read_bytes()).hexdigest() == manifest["deck_sha256"]
    assert (manifest["width"], manifest["height"]) == (1920, 1080)
    assert len(manifest["screenshots_sha256"]) == 10
    for relative_path, expected_sha in manifest["screenshots_sha256"].items():
        path = ROOT / relative_path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha


def test_existing_deck_renders_can_be_validated_without_recapturing():
    """The reuse path must enforce the same ten-slide Full-HD contract."""

    timing = json.loads((ROOT / "config" / "hackathon_timing.json").read_text())
    screenshots = expected_screenshots(timing)
    validate_screenshots(screenshots, expected_count=10)
    assert len(screenshots) == 10
