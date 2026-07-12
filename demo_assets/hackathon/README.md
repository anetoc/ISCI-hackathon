# Hackathon stage fallback

The six PNG files in this directory are static 1920×1080 fallbacks generated from the committed
offline demo. They contain no external assets or live model output.

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

Change `scene=1` through `scene=6`. If the live path fails, present the PNGs in lexical order.

## Regeneration

```bash
python scripts/build_hackathon_claim_manifest.py
python scripts/plot_hackathon_hero.py
python scripts/build_hackathon_demo.py
```

The claim-manifest tests must pass before recapturing screenshots.

