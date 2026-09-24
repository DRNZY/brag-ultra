# Brag Ultra

Turn codebases into launch videos and social release kits.

Brag Ultra inspects a project repository, extracts key features, and generates product videos with multi-format layouts, audio mixing, and export assets.

---

## Features

* Multi-format layouts for 16:9 landscape (YouTube, X), 9:16 vertical (Reels, TikTok, Shorts), and 1:1 square (Instagram, LinkedIn).
* Audio ducking with -12dB background music attenuation during voiceover, plus typing and transition sound effects.
* Terminal and CLI session playback with customizable typing cadence.
* SVG turbulence film grain overlays and spring physics transitions.
* Bundled release package including mastered MP4s, poster JPGs, optimized GIF previews, and social copy drafts.

---

## Installation

```bash
npx skills add DRNZY/brag-ultra
```

---

## Usage

In any project directory, invoke `/brag` in your AI coding assistant:

```bash
# Standard launch video
/brag

# Mobile vertical format with voiceover
/brag --format vertical --voice

# Multi-format social release bundle
/brag --format all --kit

# Specific tone preset
/brag --tone apple-keynote
```

---

## Generated launch kit

Each run produces output files inside `brag-output/`:

```text
brag-output/
├── brag.mp4                 # Mastered MP4 with frame-0 poster
├── brag-16x9.mp4            # Landscape export (YouTube, X)
├── brag-9x16.mp4            # Vertical export (Reels, TikTok, Shorts)
├── brag-1x1.mp4             # Square export (LinkedIn, Instagram)
├── brag.jpg                 # High-resolution poster frame
├── brag.gif                 # Palette-optimized GIF preview
├── share-copy.txt           # Post caption draft
├── share-copy-variants.md   # Tailored copy for X, LinkedIn, Reddit, and Product Hunt
└── launch-metadata.json     # OpenGraph and Twitter card metadata
```

---

## Tone presets

* `apple-keynote`: Restrained pacing, tactile physics, human-focused copy.
* `polished`: Clean presentation for developer tools and infrastructure.
* `default`: Direct showcase for indie products.
* `yc-parody`: Deadpan delivery for experimental tools.
* `chaotic`: Fast pacing with rapid cuts.
* `deadpan`: Minimalist timing.
* `cinematic`: Slower pacing with atmospheric audio.
* `app-store`: Feature card walkthrough with UI focus.

---

## License

MIT License. Copyright (c) 2026 Shunit Haviv Hakimi and DRNZY.
