---
name: brag-ultra
description: Turn any project, app, CLI tool, or website into a short, ultra-polished, shareable launch video and complete launch kit using Brag Ultra and Hyperframes. Supports multi-format responsive reflow (16:9, 9:16, 1:1), terminal/TUI recording, intelligent audio ducking (-12dB), kinetic shaders & grain, and full launch asset packaging. Reads project code and running instances directly.
---

# /brag (Brag Ultra)

You built it. Now let's brag about it — in Apple-grade ultra fidelity.

## Invocation dispatch (must happen first)

Before inspecting the project, parse the complete `/brag` invocation. If the
invocation contains `--voice`, set `voice.enabled = true`. If `--format` or `--kit`
is supplied, configure the rendering pipeline accordingly.

`/brag` transforms the current project (web app, mobile app, desktop GUI, CLI/TUI tool, or library) into an ultra-high-polish launch video and social launch kit.

---

## What Brag Ultra does

1. **Inspects Project & Captures Real UI / CLI:** Scans project code, architecture, and live instances. Captures real mobile emulators (`adb`), web pages (Puppeteer), desktop windows, or terminal sessions (`asciinema` / CSS terminal frame).
2. **Multi-Format Responsive Planning:** Plans adaptive layouts for 16:9 Landscape (X, YouTube), 9:16 Vertical (TikTok, Reels, Shorts), and 1:1 Square (LinkedIn, Instagram).
3. **Apple-Grade Storyboarding & Scripting:** Crafts a high-impact narrative with critically damped springs, kinetic shaders, SVG stroke tracing, and authentic project data.
4. **Intelligent Audio Mastering & Ducking:** Automatically ducks background music by -12dB under voice narration (Kokoro TTS) with smooth 0.3s attack / 0.5s release curves and mixes impact-leveled SFX.
5. **Complete Launch Kit Delivery:** Renders multi-format MP4s, extracts frame-0 baked poster JPGs, generates crisp two-pass animated preview GIFs, and outputs structured social copy & `launch-metadata.json`.

---

## Parsing the invocation

The user may invoke with natural language or flags:

```bash
/brag
/brag --tone polished --format vertical
/brag --format all --kit --voice
/brag --tone chaotic --format square
/brag this CLI tool. Make it feel like an Apple developer keynote.
```

### Supported Flags & Options

| Option | Values | Default | Description |
|---|---|---|---|
| `--tone` | preset or freeform description | `apple-keynote` / inferred | Aesthetic & pacing style |
| `--format` | `landscape` (16:9), `vertical` (9:16), `square` (1:1), `all` | `landscape` | Video aspect ratio and CSS reflow target |
| `--duration` | seconds (e.g. `15s`, `20s`) | auto (15–25s) | Total duration |
| `--voice` | flag | narration off | Opt-in Kokoro voiceover with -12dB auto-ducking |
| `--kit` | flag | standard render | Generate full launch kit (MP4s, GIF, poster JPG, metadata JSON) |
| `--terminal` | flag | auto-detected | Enable CLI/TUI terminal playback & chrome |
| `--no-music` | flag | music on | Disable background music bed |
| `--no-sfx` | flag | sfx on | Disable sound effects |
| `--title` | string | inferred | Custom product title |

When `--format all` or `--kit` is specified, generate all 3 aspect ratios (`16:9`, `9:16`, `1:1`) alongside the animated GIF and metadata bundle.

---

## Core Pillars of Brag Ultra

### 1. Multi-Format Responsive Reflow
No awkward black bars or naive letterboxing. The composition reflows intelligently:
- **16:9 Landscape (`1920x1080`):** Side-by-side split layouts, duo device frames, widescreen terminal views.
- **9:16 Vertical (`1080x1920`):** Centered vertical stack, full-height mobile device frames, large font clamps, strict safe zones (padding top/bottom for platform overlays).
- **1:1 Square (`1080x1080`):** Tight focused crop, centered hero card, high-contrast typography.

### 2. Intelligent Audio Mastering & Voiceover Ducking
- Background music automatically ducks by **-12dB** whenever voice narration or dialogue plays.
- Ducking curve: **0.3s smooth attack** before speech, **0.5s release** after speech.
- Master limiter and volume normalization: SFX punch through at 0.60–0.85 without digital clipping.

### 3. Terminal / CLI / TUI Screen Capture
- Dedicated support for terminal tools (`pluvia`, `hyperindex`, `omnihud`, `token-trimmer`, etc.).
- Replays live commands with realistic human typing cadence (40–90ms jitter), ANSI syntax colors, and synchronized keypress audio (`keyboard/keypress-*.wav`).
- High-res SVG / Canvas terminal frame with Apple traffic-light window chrome and titanium border.

### 4. Kinetic Shader & Motion Polish
- **Film Grain Texture:** Subtle SVG `feTurbulence` / canvas noise (3–5% opacity) eliminating color banding and adding cinematic warmth.
- **Chromatic Aberration:** Micro RGB-split on high-velocity cuts and slam impacts.
- **Spring Physics:** GSAP critically damped curves (`ease: "expo.out"`, `ease: "power4.out"`, or `mass: 1, stiffness: 120, damping: 14`).
- **SVG Stroke Tracing:** Animated path drawing (`stroke-dashoffset`) for logos, architectural nodes, and UI outlines.

### 5. Complete Launch Kit Generation
Produces a turnkey release directory:
- `brag.mp4` / `brag-16x9.mp4`, `brag-9x16.mp4`, `brag-1x1.mp4`
- `brag.gif` (Two-pass palette-optimized 30fps animated preview for GitHub READMEs & Discord embeds under 10MB)
- `brag.jpg` (High-res poster frame, baked directly into frame 0 of the MP4)
- `share-copy.txt` (Concise single-post caption)
- `share-copy-variants.md` (Customized captions for X/Twitter, LinkedIn, Reddit, Product Hunt)
- `launch-metadata.json` (OpenGraph, Twitter card tags, keywords, timestamps)

---

## Output Directory

Default output goes to `brag-output/` (or timestamped `brag-output-YYYY-MM-DD-HHmmss/` if existing):

```text
brag-output/
  brag.mp4                     # Primary rendered video
  brag-16x9.mp4                # 16:9 Landscape render (if multi-format)
  brag-9x16.mp4                # 9:16 Vertical render (if multi-format)
  brag-1x1.mp4                 # 1:1 Square render (if multi-format)
  brag.jpg                     # High-res poster frame (baked into frame 0)
  brag.gif                     # High-res animated GIF preview
  brag-plan.md                 # Storyboard & creative plan
  composition-brief.md         # Hyperframes brief
  share-copy.txt               # Primary post caption
  share-copy-variants.md       # Multi-platform post copy
  launch-metadata.json         # OpenGraph & social metadata
  composition/                 # Hyperframes source project
```

---

## Workflow Steps

- **Step 1: Inspect & Capture Live UI / Terminal:** Read [references/step-1-inspect.md](references/step-1-inspect.md) & [references/capture-workflow.md](references/capture-workflow.md)
- **Step 2: Plan & Storyboard:** Read [references/step-2-plan.md](references/step-2-plan.md) & [references/apple-design-guide.md](references/apple-design-guide.md)
- **Step 3: Compose with Hyperframes:** Read [references/step-3-compose.md](references/step-3-compose.md) & [references/audio.md](references/audio.md)
- **Step 4: Validate, Render & Deliver Launch Kit:** Read [references/step-4-deliver.md](references/step-4-deliver.md)

---

## Tone Presets

Full definitions in [references/tones.md](references/tones.md):

| Tone | Energy | One-Liner |
|---|---|---|
| `apple-keynote` | Quiet confidence, tactile physics, sublime restraint | Flagship Apple product reveal aesthetic |
| `default` | Playful, clean, postable | Good-vibes consumer & creative showcase |
| `polished` | Serious, elegant, high-craft | Premium developer tool or enterprise product |
| `yc-parody` | Deadpan startup energy | Serious delivery of audacious or quirky concepts |
| `chaotic` | Fast, loud, unhinged | High-velocity hype reel |
| `deadpan` | Calm, dry, understated | Minimalist timing where restraint is the punchline |
| `cinematic` | Dramatic, blockbuster-scale | Big motion, orchestral/synth swells, trailer pacing |
| `app-store` | Smooth, feature-card clean | Crisp UI walkthrough with tactile micro-interactions |
