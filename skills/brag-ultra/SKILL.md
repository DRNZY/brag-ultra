<!-- GENERATED FILE. Source of truth: the repository root.
     Regenerate with scripts/sync_skill.py --write; verify with --check. -->
---
name: brag-ultra
description: Turn any project, app, CLI tool, or website into a short, ultra-polished, shareable launch video and complete launch kit using Brag Ultra and Hyperframes. Supports multi-format responsive reflow (16:9, 9:16, 1:1), terminal/TUI recording, intelligent audio ducking (-12dB), kinetic shaders & grain, and full launch asset packaging. Reads project code and running instances directly.
---

# /brag (Brag Ultra)

You built it. Now let's brag about it — in Apple-grade ultra fidelity.

## Invocation dispatch (must happen first)

Before inspecting the project, parse the complete `/brag` invocation and pass it
to the step 4 script, which owns every flag below:

```bash
python3 scripts/generate_launch_kit.py \
  --composition ./brag-output/composition \
  --output-dir ./brag-output \
  --format all --kit --voice --terminal --no-music --no-sfx \
  --tone polished --duration 20s --title "Product"
```

`/brag` transforms the current project (web app, mobile app, desktop GUI, CLI/TUI tool, or library) into an ultra-high-polish launch video and social launch kit.

---

## What Brag Ultra does

1. **Inspects Project & Captures Real UI / CLI:** Scans project code, architecture, and live instances. Captures real mobile emulators (`adb`), web pages (Puppeteer), desktop windows, or terminal sessions (`asciinema` / CSS terminal frame).
2. **Multi-Format Planning:** Plans a real layout per aspect ratio for 16:9 Landscape (X, YouTube), 9:16 Vertical (TikTok, Reels, Shorts), and 1:1 Square (LinkedIn, Instagram). These are three authored compositions, not one composition rescaled. See the aspect note below.
3. **Apple-Grade Storyboarding & Scripting:** Crafts a high-impact narrative with critically damped springs, kinetic shaders, SVG stroke tracing, and authentic project data.
4. **Intelligent Audio Mastering & Ducking:** Narration ducks the music bed by -12dB with smooth 0.3s attack / 0.5s release curves, and SFX are mixed at impact-leveled gain.
5. **Complete Launch Kit Delivery:** Validates and renders every requested aspect with a pinned HyperFrames CLI, extracts a frame-0 baked poster, builds a two-pass animated GIF, and emits structured share copy and `launch-metadata.json`.

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

Every flag is accepted by `scripts/generate_launch_kit.py`, which is the only
component that talks to the HyperFrames CLI.

| Option | Values | Default | Effect |
|---|---|---|---|
| `--title` | string | inferred | Product title in copy and metadata |
| `--tagline` | string | inferred | One-line claim in copy and metadata |
| `--format` | `landscape` (16:9), `vertical` (9:16), `square` (1:1), `all` | `landscape` | Which aspects to render. Aliases: `portrait`, `16x9`, `9x16`, `1x1` |
| `--kit` | flag | standard render | Full launch kit: every aspect, poster, GIF, copy, metadata |
| `--tone` | preset or freeform description | `apple-keynote` | Aesthetic & pacing style. Recorded as an authoring directive |
| `--duration` | seconds (e.g. `15s`, `20s`) | auto (15–25s) | Recorded as an authoring directive; the composition's timeline governs |
| `--voice` | flag | narration off | Recorded as an authoring directive |
| `--terminal` | flag | auto-detected | Recorded as an authoring directive |
| `--no-music` | flag | music on | Recorded as an authoring directive |
| `--no-sfx` | flag | sfx on | Recorded as an authoring directive |

Render controls: `--quality` (`draft`/`looks`/`standard`/`high`/`delivery`),
`--fps`, `--poster-time`, `--no-gif`, `--no-check`, `--strict-check`,
`--skip-render`, `--dry-run`, `--timeout`, `--tags`, `--highlight`.

**Which flags change delivery, and which do not.** `--format`, `--kit` and
`--title` change what the delivery stage produces. `--tone`, `--duration`,
`--voice`, `--terminal`, `--no-music` and `--no-sfx` shape what gets authored in
steps 2 and 3. Delivery cannot apply them to a composition that is already
written, so the script records them in `brag-plan.md` and
`launch-metadata.json` for traceability and says so explicitly rather than
implying it re-encoded around them. Honour them where they belong: in the plan
and in the composition.

---

## Multi-format output is an authoring obligation

**A HyperFrames composition has exactly one aspect ratio.** It declares it with
`data-resolution` on `<html>`, and `hyperframes render` refuses to render it at
any other aspect:

```text
Output resolution incompatible
outputResolution portrait (1080x1920) does not match the aspect ratio of the
composition (1920x1080). The composition is landscape — use --resolution
landscape instead.
```

There is no `--width` / `--height` render flag and no automatic reflow. Aspect is
selected with `--resolution <preset>`, and that flag only ever has to agree with
the file.

So the three aspect ratios are three compositions. A 9:16 cut is a vertical
stack with a larger type scale and platform safe zones. A 1:1 cut drops type by
roughly a third. Neither is the 16:9 file at a different size, and the honest
alternative, letterboxing the 16:9 master, is worse than not cutting vertical at
all.

Give each aspect its own project directory, because `hyperframes check` has no
`--composition` flag and validates only a project directory's root `index.html`:

```text
brag-output/composition/
  landscape/index.html    <html data-resolution="landscape">
  portrait/index.html     <html data-resolution="portrait">
  square/index.html       <html data-resolution="square">
```

Keep element ids and `data-start` / `data-duration` values identical across the
three files, so every aspect cuts to the same frame at any given timestamp.

Full contract, including the `brag-composition.json` escape hatch for
non-standard paths, in [references/step-4-deliver.md](references/step-4-deliver.md).

---

## Core Pillars of Brag Ultra

### 1. Multi-Format Layouts
- **16:9 Landscape (`1920x1080`):** Side-by-side split layouts, duo device frames, widescreen terminal views.
- **9:16 Vertical (`1080x1920`):** Centered vertical stack, full-height mobile device frames, large font clamps, strict safe zones (padding top/bottom for platform overlays).
- **1:1 Square (`1080x1080`):** Tight focused crop, centered hero card, high-contrast typography.

### 2. Intelligent Audio Mastering & Voiceover Ducking
- Background music ducks by **-12dB** whenever voice narration or dialogue plays.
- Ducking curve: **0.3s smooth attack** before speech, **0.5s release** after speech.
- Master limiter and volume normalization: SFX punch through at 0.60–0.85 without digital clipping.

### 3. Terminal / CLI / TUI Screen Capture
- Dedicated support for terminal tools (`pluvia`, `hyperindex`, `omnihud`, `token-trimmer`, etc.).
- Replays live commands with realistic human typing cadence (40–90ms jitter), ANSI syntax colors, and synchronized keypress audio (`keyboard/keypress-*.wav`).
- High-res SVG / Canvas terminal frame with Apple traffic-light window chrome and titanium border.

### 4. Kinetic Shader & Motion Polish
- **Chromatic Aberration:** Micro RGB-split on high-velocity cuts and slam impacts.
- **Spring Physics:** GSAP critically damped curves (`ease: "expo.out"`, `ease: "power4.out"`, or `mass: 1, stiffness: 120, damping: 14`).
- **SVG Stroke Tracing:** Animated path drawing (`stroke-dashoffset`) for logos, architectural nodes, and UI outlines.

Note on grain: film grain and noise overlays are **not** used. They are listed
as an AI design crutch in the project rules, they cost render time, and on the
compressed H.264 output of a 30fps 1080p render they read as compression
artefacts rather than texture.

### 5. Complete Launch Kit Generation
Produces a turnkey release directory:
- `brag-16x9.mp4`, `brag-9x16.mp4`, `brag-1x1.mp4`, plus `brag.mp4` as a copy of the landscape render
- `brag.gif` (Two-pass palette-optimized 24fps animated preview for GitHub READMEs & Discord embeds)
- `brag.jpg` (High-res poster frame, baked into frame 0 of the landscape MP4)
- `share-copy.txt` (Concise single-post caption)
- `share-copy-variants.md` (Customized copy for X/Twitter, LinkedIn, Reddit, Product Hunt)
- `brag-plan.md` (Storyboard & timing contract, derived from the real timeline)
- `launch-metadata.json` (OpenGraph, Twitter card tags, keywords, timestamps)

Every asset named in the metadata is confirmed to exist on disk first, so the
bundle never advertises a render that failed.

---

## Output Directory

Default output goes to `brag-output/`, or to a timestamped
`brag-output-YYYY-MM-DD-HHmmss/` when `brag-output/` already exists, so a second
run never clobbers the first run's renders:

```text
brag-output/
  brag.mp4                     # Copy of the landscape render (historical filename)
  brag-16x9.mp4                # 16:9 Landscape render
  brag-9x16.mp4                # 9:16 Vertical render
  brag-1x1.mp4                 # 1:1 Square render
  brag.jpg                     # High-res poster frame (baked into frame 0)
  brag.gif                     # Two-pass palette-optimized animated preview
  brag-plan.md                 # Storyboard, timing contract, verified asset table
  composition-brief.md         # Hyperframes brief
  share-copy.txt               # Primary post caption
  share-copy-variants.md       # Multi-platform post copy
  launch-metadata.json         # OpenGraph & social metadata
  composition/
    landscape/index.html       # data-resolution="landscape"
    portrait/index.html        # data-resolution="portrait"
    square/index.html          # data-resolution="square"
```

---

## Workflow Steps

- **Step 1: Inspect & Capture Live UI / Terminal:** Read [references/step-1-inspect.md](references/step-1-inspect.md) & [references/capture-workflow.md](references/capture-workflow.md)
- **Step 2: Plan & Storyboard:** Read [references/step-2-plan.md](references/step-2-plan.md) & [references/apple-design-guide.md](references/apple-design-guide.md)
- **Step 3: Compose with Hyperframes:** Read [references/step-3-compose.md](references/step-3-compose.md) & [references/audio.md](references/audio.md). Author one composition per requested aspect, in its own project directory.
- **Step 4: Validate, Render & Deliver Launch Kit:** Read [references/step-4-deliver.md](references/step-4-deliver.md), then run `scripts/generate_launch_kit.py`.

---

## Toolchain

The HyperFrames CLI version is pinned once, in `scripts/hyperframes_cli.py`:

```text
HYPERFRAMES_VERSION = "0.8.78"
```

Every call goes through it as `npx --yes hyperframes@0.8.78 <command>`, matching
the specifier format the HyperFrames CLI itself writes into a scaffolded
`package.json`. A bare `npx hyperframes` re-resolves the registry on every
invocation, so the same command can behave differently on two consecutive runs.

The delivery script also writes that pin into each aspect project's
`package.json`, so `npm run render` inside a composition resolves the same
version later.

To bump the pin, edit `HYPERFRAMES_VERSION`, then re-run the launch kit end to
end and confirm every aspect still renders. A version change can alter lint
findings, render defaults and encoder settings.

---

## Repository Layout

The repository root is the single source of truth for this skill.
`skills/brag-ultra/` is a **generated mirror** of `SKILL.md`, `references/`,
`scripts/` and `assets/`, produced because `npx skills add` expects a
`skills/<name>/` layout. Do not hand-edit the mirror.

```bash
python3 scripts/sync_skill.py --check   # exit 1 on drift, for CI
python3 scripts/sync_skill.py --write   # regenerate
```

The mirror differs from the root in exactly one intentional way: the `name:`
field in the YAML frontmatter. The root declares `name: brag`, which is the
`/brag` invocation and what `skills-lock.json` records. A skill directory must
declare its own directory name, so the mirror declares `name: brag-ultra`. The
sync script applies that single substitution, which is what keeps the two files
from drifting.

---

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
