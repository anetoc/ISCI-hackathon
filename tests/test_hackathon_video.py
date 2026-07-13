import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "demo_assets" / "hackathon" / "hackathon_fallback_2m30.mp4"
MANIFEST = ROOT / "outputs" / "hackathon" / "video_manifest.json"


def test_fallback_video_matches_committed_media_manifest():
    """The binary fallback must be exactly the media artifact that was validated."""

    manifest = json.loads(MANIFEST.read_text())
    assert VIDEO.read_bytes()[4:8] == b"ftyp"
    assert hashlib.sha256(VIDEO.read_bytes()).hexdigest() == manifest["output_sha256"]
    assert manifest["duration_seconds"] == 150.0
    assert (manifest["width"], manifest["height"]) == (1920, 1080)
    assert (manifest["video_codec"], manifest["audio_codec"]) == ("h264", "aac")
    assert manifest["audio_content"] == "silence"

