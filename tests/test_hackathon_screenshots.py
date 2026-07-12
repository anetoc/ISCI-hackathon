import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "outputs" / "hackathon" / "screenshot_manifest.json"


def test_screenshots_match_the_current_offline_demo():
    """The video may not silently reuse screenshots from an older HTML build."""

    manifest = json.loads(MANIFEST.read_text())
    demo = ROOT / manifest["demo_path"]
    assert hashlib.sha256(demo.read_bytes()).hexdigest() == manifest["demo_sha256"]
    assert (manifest["width"], manifest["height"]) == (1920, 1080)
    assert len(manifest["screenshots_sha256"]) == 6
    for relative_path, expected_sha in manifest["screenshots_sha256"].items():
        path = ROOT / relative_path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha

