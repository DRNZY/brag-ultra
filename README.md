# Brag Ultra

Turn code into high-fidelity launch videos and social release kits.

Brag Ultra inspects your project, understands what makes it unique, and generates an Apple-keynote aesthetic video (15–25s) with multi-format layouts, mastered audio, and complete launch assets.

---

## Highlights

* **Multi-Format Responsive Reflow:** Native layouts for 16:9 Landscape (X, YouTube), 9:16 Vertical (TikTok, Reels, Shorts), and 1:1 Square (LinkedIn, Instagram).
* **Intelligent Audio & Voiceover Ducking:** Automatic -12dB background music ducking under narration with smooth 0.3s attack / 0.5s release curves, plus synced tactile keystrokes and impact SFX.
* **Terminal & CLI Replay:** Native support for developer tools, terminal capture, realistic human typing cadence, and high-DPI vector terminal frames.
* **Kinetic Shaders & Spring Physics:** Subtle film grain overlays (SVG `feTurbulence`), lens chromatic aberration on transients, critically damped spring physics, and animated SVG path tracing.
* **Complete Launch Kit:** Outputs mastered MP4s, frame-0 baked poster JPGs, two-pass palette-optimized animated GIFs (<10MB), and structured social copy + OpenGraph metadata.

---

## Installation

```bash
npx skills add DRNZY/brag-ultra
```

---

## Usage

In any project directory, invoke `/brag` in your AI coding assistant:

```bash
# Standard high-polish launch video
/brag

# Mobile vertical format with Kokoro voiceover
/brag --format vertical --voice

# Complete multi-format social release bundle
/brag --format all --kit

# Custom tone direction
/brag --tone apple-keynote
```

---

## Generated Launch Kit

Each run produces a ready-to-share bundle inside `brag-output/`:

```text
brag-output/
├── brag.mp4                 # Mastered MP4 with frame-0 poster
├── brag-16x9.mp4            # Landscape export (YouTube, X)
├── brag-9x16.mp4            # Vertical export (Reels, TikTok, Shorts)
├── brag-1x1.mp4             # Square export (LinkedIn, Instagram)
├── brag.jpg                 # High-resolution poster frame
├── brag.gif                 # Two-pass palette-optimized GIF preview
├── share-copy.txt           # Postable single-caption copy
├── share-copy-variants.md   # Tailored copy for X, LinkedIn, Reddit, PH
└── launch-metadata.json     # OpenGraph and Twitter card metadata
```

---

## Tone Presets

* `apple-keynote`: Quiet confidence, tactile physics, human-centric copy, sublime restraint.
* `polished`: Refined, elegant, high craft for developer infrastructure and SaaS.
* `default`: Playful, direct, clean showcase for indie products.
* `yc-parody`: Deadpan seriousness applied to unorthodox projects.
* `chaotic`: High-velocity hype reel with aggressive cuts and tilts.
* `deadpan`: Minimalist timing where restraint is the punchline.
* `cinematic`: Trailer-scale pacing with atmospheric lighting and score.
* `app-store`: Clean feature-card walkthrough with tactile UI feedback.

---

## License

MIT License — Copyright (c) 2026 Shunit Haviv Hakimi & DRNZY.
