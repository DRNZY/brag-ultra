# Brag Ultra

Turn any project, app, CLI tool, or website into an ultra-polished launch video and complete social launch kit.

Built on top of [Hyperframes](https://github.com/latent-spaces/hyperframes), Brag Ultra inspects your codebase or live running environment, drafts a storyboard tailored to your stack, and renders multi-format video assets with synchronized audio, kinetic motion, and automated narration ducking.

---

## Highlights

* **Multi-Format Responsive Reflow**: Automatically lays out scenes for 16:9 Landscape (YouTube, X), 9:16 Vertical (TikTok, Reels, Shorts), and 1:1 Square (LinkedIn, Instagram).
* **Authentic UI & Terminal Capture**: Embeds real web interfaces, mobile emulator streams, desktop windows, or crisp vector terminal replays (`asciinema` / CSS terminal engine).
* **Intelligent Audio Mastering**: Smooth background music ducking (-12dB) under Kokoro voiceovers with realistic sound effects mapped to UI transitions.
* **Apple-Grade Motion Polish**: Spring physics, kinetic typography, subtle film grain, and stroke-traced SVG architecture diagrams.
* **Complete Launch Kit**: Outputs multi-aspect MP4s, poster frames, animated preview GIFs, and optimized social share copy.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/DRNZY/brag-ultra.git
cd brag-ultra

# Install Python audio analysis tools (optional, for beat-sync)
cd scripts
uv sync
```

To install as an Antigravity agent skill:

```bash
mkdir -p ~/.gemini/config/skills/brag
cp -r * ~/.gemini/config/skills/brag/
```

---

## Quick Usage

Inside your coding assistant or agent session, simply invoke:

```bash
/brag
```

### Options

* `/brag --format 9:16`: Render in vertical format for Reels/TikTok.
* `/brag --format 1:1`: Render in square format for feeds.
* `/brag --kit`: Render all three aspect ratios and generate a complete launch asset package (MP4s, GIF previews, poster JPGs, share text).
* `/brag --voice`: Enable automated narration and voiceover generation.
* `/brag --tone polished`: Select a specific creative tone (`default`, `polished`, `cinematic`, `retro-synth`, `cyberpunk`, `minimal`, `terminal`).

---

## Output Structure

When executed, Brag Ultra generates a self-contained bundle:

```
brag-output/
├── brag.mp4                  # 16:9 Landscape master video
├── brag-vertical.mp4         # 9:16 Mobile reel
├── brag-square.mp4           # 1:1 Feed video
├── brag-preview.gif          # 2-pass optimized animated preview
├── brag-poster.jpg           # High-DPI frame-0 video poster
├── share-copy.txt            # Ready-to-publish social captions
├── launch-metadata.json      # Structured tags, timestamps, and cue points
└── composition/              # Hyperframes HTML/CSS source project
```

---

## Upstream & Acknowledgements

Brag Ultra is built upon the original `brag` skill architecture by [Shunit Haviv Hakimi / Latent Spaces](https://github.com/latent-spaces/brag), extended with multi-format reflow, terminal vector replay, intelligent audio ducking, and launch kit packaging.

---

## License

[MIT License](LICENSE) © 2026 DRNZY.
