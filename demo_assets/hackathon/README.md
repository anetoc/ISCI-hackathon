# Hackathon stage fallback

The ten PNG files in this directory are deterministic 1920×1080 renders of the approved public
PowerPoint deck. The interactive page, submitted video and fallback MP4 use the same visual order.
They contain no external assets or live model output.

## Live presentation

Open `docs/hackathon_judge_demo.html` in a current Chromium/Safari browser.

- `→`, `Space` or `PageDown`: next scene
- `←` or `PageUp`: previous scene
- `Home` / `End`: first / last scene
- `R`: reset scene and rehearsal timer

## Static presentation

Open a specific scene without controls:

```text
docs/hackathon_judge_demo.html?static=1&scene=1
```

Change `scene=1` through `scene=10`. If the live path fails, present the PNGs in lexical order.

## Regeneration

```bash
python scripts/build_hackathon_claim_manifest.py
python scripts/capture_hackathon_screenshots.py
python scripts/build_hackathon_demo.py
python scripts/build_hackathon_video.py
```

The claim-manifest tests must pass before recapturing screenshots.
