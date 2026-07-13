import json
from pathlib import Path

from scripts.release_provenance import SNAPSHOT_SCHEMA, source_snapshot


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = [
    ROOT / "outputs" / "hackathon" / "claim_manifest.json",
    ROOT / "outputs" / "hackathon" / "screenshot_manifest.json",
    ROOT / "outputs" / "hackathon" / "readiness_report.json",
]


def test_release_manifests_bind_the_exact_source_files_that_generated_them():
    """A base Git SHA alone cannot identify pre-commit working-tree sources."""

    for manifest_path in MANIFESTS:
        manifest = json.loads(manifest_path.read_text())
        recorded = manifest["source_snapshot"]
        paths = [ROOT / relative for relative in recorded["files_sha256"]]
        recomputed = source_snapshot(paths, ROOT)

        assert recorded["schema_version"] == SNAPSHOT_SCHEMA
        assert recorded == recomputed, manifest_path.name
        assert isinstance(manifest["source_paths_dirty"], bool)
        assert manifest["git_sha_semantics"].startswith("Base revision at generation time")
