# Step 4: Validate, Render & Deliver Launch Kit

Brag Ultra delivers a complete launch kit ready for multi-platform distribution across Twitter/X, LinkedIn, YouTube, TikTok/Reels, GitHub READMEs, and Discord.

---

## 1. Validation & Pre-render Gate

```bash
cd <output-dir>/composition
npx hyperframes check
```

Fix all errors reported by `check`. It validates:
- Layout overflow and clipping across target aspect ratios.
- WCAG color contrast compliance for text readability.
- Audio asset existence and timing attributes.

---

## 2. Rendering Multi-Format Video

### Primary Render
```bash
npx hyperframes render --quality high --output ../brag.mp4
```

### Multi-Format Renders (When `--format all` or `--kit` is enabled)
If responsive reflow variants are configured:
```bash
# 16:9 Landscape (1920x1080) for X & YouTube
npx hyperframes render --width 1920 --height 1080 --output ../brag-16x9.mp4

# 9:16 Vertical (1080x1920) for TikTok, Reels, Shorts
npx hyperframes render --width 1080 --height 1920 --output ../brag-9x16.mp4

# 1:1 Square (1080x1080) for LinkedIn & Instagram
npx hyperframes render --width 1080 --height 1080 --output ../brag-1x1.mp4
```

---

## 3. High-Res Poster Frame Extraction & Frame 0 Baking

### Extract Settled Poster
Pick the strongest settled frame timestamp (e.g. `3.2s` where headline and device are fully visible):
```bash
ffmpeg -ss 3.2 -i ../brag.mp4 -frames:v 1 -q:v 2 ../brag.jpg
```

### Bake Poster as Frame 0
Bake `brag.jpg` into frame 0 of the MP4 so Twitter/X, Slack, and Discord automatically display the crisp poster before playback without custom platform tags:
```bash
ffmpeg -y -i ../brag.mp4 -i ../brag.jpg \
  -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
  -c:a copy -movflags +faststart ../brag.baked.mp4 \
  && mv ../brag.baked.mp4 ../brag.mp4
```

---

## 4. Two-Pass Palette-Optimized Animated GIF (`brag.gif`)

Generate an ultra-crisp, high-fps animated GIF optimized for GitHub READMEs, documentation, and Discord previews (<10MB):

```bash
ffmpeg -y -i ../brag.mp4 -vf "fps=24,scale=800:-1:flags=lanczos,palettegen=stats_mode=diff" ../palette.png
ffmpeg -y -i ../brag.mp4 -i ../palette.png -filter_complex "fps=24,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" ../brag.gif
rm ../palette.png
```

---

## 5. Structured Launch Metadata & Share Copy

### `share-copy.txt` (Canonical Post Caption)
Write `<output-dir>/share-copy.txt` with a concise, punchy 1–2 sentence post:
```text
Built [Product Name] — [one-liner claim].
[Core highlight or benchmark].
Link & open source below 🚀
```

### `share-copy-variants.md` (Multi-Platform Copy)
Write `<output-dir>/share-copy-variants.md` with customized copy for:
- **Twitter / X:** Fast, hook-first, short sentences, relevant tags.
- **LinkedIn:** Professional craft narrative, architectural insight, engineering takeaway.
- **Reddit (r/rust, r/react, r/linux):** Technical deep-dive context, benchmarks, repo link.
- **Product Hunt:** Maker tagline, 3 core bullets, question to the community.

### `launch-metadata.json` (OpenGraph & SEO Bundle)
Write `<output-dir>/launch-metadata.json`:
```json
{
  "title": "[Product Name] — [Tagline]",
  "description": "[1-sentence description]",
  "openGraph": {
    "title": "[Product Name]",
    "type": "video.other",
    "image": "brag.jpg",
    "video": "brag.mp4"
  },
  "twitter": {
    "card": "player",
    "site": "@drnzy",
    "image": "brag.jpg",
    "player": "brag.mp4"
  },
  "tags": ["[Tag1]", "[Tag2]", "[Tag3]"],
  "generatedAt": "2026-09-23T14:42:00Z"
}
```

---

## 6. Final Launch Kit Output Structure

```text
brag-output/
├── brag.mp4                 # Primary mastered video with Frame-0 poster baked in
├── brag-16x9.mp4            # Landscape export (YouTube, X)
├── brag-9x16.mp4            # Vertical export (TikTok, Reels, Shorts)
├── brag-1x1.mp4             # Square export (LinkedIn, Instagram)
├── brag.jpg                 # Full-resolution poster thumbnail
├── brag.gif                 # Two-pass palette-optimized README GIF
├── share-copy.txt           # Clean primary caption
├── share-copy-variants.md   # Tailored captions for X, LinkedIn, Reddit, Product Hunt
├── launch-metadata.json     # OpenGraph & social tags
├── brag-plan.md             # Storyboard & timing contract
├── composition-brief.md     # Hyperframes brief
└── composition/             # Source Hyperframes project
```
