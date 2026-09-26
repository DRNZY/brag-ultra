# Step 4: Validate, Render & Deliver Launch Kit

Brag Ultra delivers a complete launch kit ready for multi-platform distribution across Twitter/X, LinkedIn, YouTube, TikTok/Reels, GitHub READMEs, and Discord.

The whole step is one command:

```bash
python3 scripts/generate_launch_kit.py \
  --composition ./brag-output/composition \
  --output-dir  ./brag-output \
  --format all --kit \
  --title "Pluvia" \
  --tagline "Rainmeter's desktop engine, rebuilt as a native Linux app."
```

It performs every step below, then writes `share-copy.txt`,
`share-copy-variants.md`, `brag-plan.md` and `launch-metadata.json`. The
remaining sections document what it does and the rules it enforces, so you can
reproduce a single stage by hand when you need to.

---

## 0. The pinned CLI

Every HyperFrames call goes through `scripts/hyperframes_cli.py`, which pins one
version for the whole skill:

```text
HYPERFRAMES_VERSION = "0.8.78"
npx --yes hyperframes@0.8.78 <command>
```

This is not a stylistic choice. A bare `npx hyperframes` re-resolves the
registry on every invocation, so a render can change behaviour between two runs
of the same command. The specifier format matches the one the HyperFrames CLI
itself writes into the `package.json` it scaffolds.

The script also writes that pin into each aspect project's own `package.json`,
so someone who later runs `npm run render` inside a composition gets the same
version:

```json
{
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "npx --yes hyperframes@0.8.78 preview",
    "check": "npx --yes hyperframes@0.8.78 check",
    "render": "npx --yes hyperframes@0.8.78 render",
    "publish": "npx --yes hyperframes@0.8.78 publish"
  },
  "bragUltra": { "hyperframes": "0.8.78", "pin": "hyperframes@0.8.78" }
}
```

---

## 1. Aspect ratios are an authoring obligation, not a render flag

This is the part most worth reading, because the previous version of this
document got it wrong in two ways.

**There are no `--width` / `--height` render flags.** The render command has no
such options. Aspect is selected with `--resolution <preset>`, where the presets
are `landscape` (1920x1080), `portrait` (1080x1920), `square` (1080x1080), plus
`-4k` variants.

**`--resolution` does not rescale or reflow anything.** A composition declares
exactly one aspect via `data-resolution` on `<html>`, and rendering it at any
other aspect fails hard:

```text
Output resolution incompatible

outputResolution portrait (1080x1920) does not match the aspect ratio of the
composition (1920x1080). The composition is landscape — use --resolution
landscape instead.
```

The CLI does contain a routine (`applyResolutionPreset()`) that rewrites
`data-resolution`, `data-width`, `data-height` and the viewport meta tag, but it
is only reachable from `hyperframes init --resolution`, never from `render`.
Running it by hand gives a landscape layout with portrait dimensions:
letterboxed, overflowing, and exactly the "awkward black bars" this skill claims
to avoid.

So: **one composition entry file per aspect, each authored as a real layout at
those dimensions.** A 9:16 cut is a vertical stack with a larger type scale and
vertical safe zones. A 1:1 cut drops type by roughly a third and may keep the
two-up and three-up rows. Neither is the landscape file at a different size.

### One project directory per aspect

`hyperframes check` accepts no `--composition` flag. It validates exactly one
entry point: the root `index.html` of the project directory it is pointed at.
Pointing it at a directory that also contains `index-portrait.html` and
`index-square.html` fails with:

```text
multiple_root_compositions: Multiple root-level HTML files with
data-composition-id: index-portrait.html, index-square.html, index.html. The
runtime may discover both as entry points, causing duplicate audio playback.
```

That error aborts the check before layout and contrast sampling runs at all, so
you get zero coverage of the two aspects you most wanted verified.

The layout that works, and that `generate_launch_kit.py` looks for first:

```text
composition/
  landscape/
    index.html            <html data-resolution="landscape">
    hyperframes.json
    assets/
  portrait/
    index.html            <html data-resolution="portrait">
    hyperframes.json
    assets/
  square/
    index.html            <html data-resolution="square">
    hyperframes.json
    assets/
```

Each directory is a self-contained HyperFrames project. `check` validates every
one of them, and each `render` runs with `--resolution` matching the file it is
already guaranteed to match.

A flat single-directory layout also works for a single aspect
(`index-portrait.html` beside `index.html`), and is still detected, but with two
or more aspects in one directory only `index.html` can be checked.

For projects that do not follow either convention, drop a
`brag-composition.json` in the composition root:

```json
{
  "aspects": {
    "landscape": "index.html",
    "portrait": "compositions/v.html",
    "square": "compositions/s.html"
  }
}
```

### The preflight the script runs for you

Before spending a render, Brag Ultra reads the `data-resolution` each entry
file actually declares and refuses to continue on a mismatch. This is the check
that would have caught the original bug, and it turns a wasted render into an
up-front error naming the exact file and the aspect it needs:

```text
error: composition/index-portrait.html declares data-resolution="landscape" but
portrait requires "portrait".
  HyperFrames renders a composition only at its own declared aspect, so this
  would fail with "Output resolution incompatible".
  Either author a 1080x1920 layout, or request --format landscape.
```

---

## 2. Validation

Run once per aspect project, because each is a separate project:

```bash
cd <output-dir>/composition/portrait
npx --yes hyperframes@0.8.78 check .
```

It validates layout overflow and clipping at 9 sampled timestamps, motion
integrity, and WCAG AA contrast. Fix all errors. Warnings are reported and
carried into the launch kit's warning list rather than blocking, because many
are cosmetic.

Two lint findings are expected on an older composition and are safe to leave:
`nested_structure_needs_subcomposition` (a full-screen `<section>` containing
elements) and contrast warnings inside a dense app mockup.

---

## 3. Rendering

One render per aspect, each with the `--resolution` its own entry file declares:

```bash
cd <output-dir>/composition/landscape
npx --yes hyperframes@0.8.78 render . --composition index.html \
  --resolution landscape --quality delivery --skill brag \
  --output ../brag-16x9.mp4

cd <output-dir>/composition/portrait
npx --yes hyperframes@0.8.78 render . --composition index.html \
  --resolution portrait --quality delivery --skill brag \
  --output ../brag-9x16.mp4

cd <output-dir>/composition/square
npx --yes hyperframes@0.8.78 render . --composition index.html \
  --resolution square --quality delivery --skill brag \
  --output ../brag-1x1.mp4
```

`--quality` accepts `draft`, `looks` (default, CRF 16), `standard`/`high`, and
`delivery` (high). `--skill brag` records the workflow on anonymous render
telemetry.

Keep every aspect's element ids and `data-start` / `data-duration` values
identical across the three files, so all three cut to the same frame at any
given timestamp and can be cut against each other without re-timing.

---

## 4. High-Res Poster Frame Extraction & Frame 0 Baking

### Extract Settled Poster

Pick the strongest settled frame timestamp (e.g. `3.2s` where headline and
device are fully visible):

```bash
ffmpeg -y -ss 3.2 -i ../brag-16x9.mp4 -frames:v 1 -q:v 2 ../brag.jpg
```

Clamp the timestamp inside the render's duration. Asking for 3.2s of a 2.1s
render produces a zero-byte JPG, which then gets baked into frame 0 as a broken
image. The script clamps for you and discards a failed extraction.

### Bake Poster as Frame 0

Bake `brag.jpg` into frame 0 of the MP4 so Twitter/X, Slack, and Discord
automatically display the crisp poster before playback without custom platform
tags:

```bash
ffmpeg -y -i ../brag-16x9.mp4 -i ../brag.jpg \
  -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
  -c:a copy -movflags +faststart ../brag-16x9.baked.mp4 \
  && mv ../brag-16x9.baked.mp4 ../brag-16x9.mp4
```

This is a full re-encode of the video track, so run it once, at the end, after
the aspect's render is otherwise final.

---

## 5. Two-Pass Palette-Optimized Animated GIF (`brag.gif`)

Generate an ultra-crisp, high-fps animated GIF optimized for GitHub READMEs,
documentation, and Discord previews (<10MB):

```bash
ffmpeg -y -i ../brag-16x9.mp4 -vf "fps=24,scale=800:-1:flags=lanczos,palettegen=stats_mode=diff" ../palette.png
ffmpeg -y -i ../brag-16x9.mp4 -i ../palette.png -filter_complex "fps=24,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" ../brag.gif
rm ../palette.png
```

Built from the landscape render only. Skip with `--no-gif`.

---

## 6. Structured Launch Metadata & Share Copy

All four files are generated from real inputs, not a template: clip names,
start times and durations come from `hyperframes timeline --json` on the same
pinned CLI used for the render, and every asset listed in the metadata is
confirmed to exist on disk before it is named.

### `share-copy.txt` (Canonical Post Caption)

Two or three lines. Concrete claims, no hype adjectives, no emoji:

```text
Built Pluvia. Rainmeter's desktop engine, rebuilt as a native Linux app.
In the video: scene 1, scene 2, scene 3.
Rendered at 1920x1080, 1080x1920, 1080x1080 from one HTML composition.
Source and link below.
#opensource #rust #linux #wayland
```

If only some aspects rendered, the aspect line is omitted rather than claiming
files that do not exist.

### `share-copy-variants.md` (Multi-Platform Copy)

Customized copy for:

- **X / Twitter:** Hook first, short sentences, relevant tags.
- **LinkedIn:** Professional craft narrative, architectural insight, engineering
  takeaway.
- **Reddit (r/rust, r/react, r/linux):** Technical deep-dive context, including
  the honest note that the renderer will not rescale a composition to a new
  aspect, which is the thing anyone attempting the same thing gets wrong first.
- **Product Hunt:** Maker tagline, 3 core bullets, question to the community.

Each is written to its platform's reading behaviour rather than being the same
paragraph with the platform name swapped in.

### `brag-plan.md` (Storyboard & Timing Contract)

Records the invocation and which flags delivery actually honours, the
composition entry directory, the real timeline table, a verified-asset table
with per-file sizes, any requested-but-not-rendered aspect with the reason, and
the authoring note about multi-aspect being an obligation.

A useful property of this flag table: `--format`, `--kit` and `--title` change
delivery output. `--tone`, `--duration`, `--voice`, `--terminal`, `--no-music`
and `--no-sfx` are recorded as *authoring directives*, because they change what
gets composed in step 2 and step 3, not how an existing composition is encoded.
Delivery cannot apply them on its own, and the table says so rather than
implying otherwise.

### `launch-metadata.json` (OpenGraph & Social Bundle)

```json
{
  "title": "Pluvia — Rainmeter's desktop engine, rebuilt as a native Linux app.",
  "product": "Pluvia",
  "openGraph": {
    "title": "Pluvia",
    "type": "video.other",
    "image": "brag.jpg",
    "video": "brag-16x9.mp4"
  },
  "twitter": {
    "card": "player",
    "site": "@drnzy",
    "image": "brag.jpg",
    "player": "brag-16x9.mp4"
  },
  "tags": ["opensource", "rust", "linux", "wayland"],
  "assets": {
    "videos": {
      "landscape": { "file": "brag-16x9.mp4", "resolution": "1920x1080", "bytes": 1626948 },
      "portrait":  { "file": "brag-9x16.mp4", "resolution": "1080x1920", "bytes": 1716439 },
      "square":    { "file": "brag-1x1.mp4", "resolution": "1080x1080", "bytes": 1297738 }
    },
    "poster": "brag.jpg",
    "gif": "brag.gif",
    "caption": "share-copy.txt",
    "copyVariants": "share-copy-variants.md",
    "plan": "brag-plan.md"
  },
  "invocation": { "tone": "apple-keynote", "formats": ["landscape", "portrait", "square"] },
  "tooling": { "hyperframes": "0.8.78", "durationSeconds": 18 },
  "warnings": [],
  "generatedAt": "2026-09-26T14:40:00Z"
}
```

`openGraph.image` and `twitter.player` name the landscape render. An asset
field is `null` rather than a filename when the file is absent, so the metadata
can never advertise a render that failed.

---

## 7. Final Launch Kit Output Structure

```text
brag-output/
├── brag-16x9.mp4           # 1920x1080 (YouTube, X)
├── brag-9x16.mp4           # 1080x1920 (TikTok, Reels, Shorts)
├── brag-1x1.mp4            # 1080x1080 (LinkedIn, Instagram)
├── brag.jpg                # Full-resolution poster thumbnail
├── brag.gif                # Two-pass palette-optimized README GIF
├── share-copy.txt          # Clean primary caption
├── share-copy-variants.md  # Tailored captions for X, LinkedIn, Reddit, Product Hunt
├── brag-plan.md            # Storyboard & timing contract
├── launch-metadata.json    # OpenGraph & social tags
├── composition-brief.md    # Hyperframes brief
└── composition/
    ├── landscape/index.html
    ├── portrait/index.html
    └── square/index.html
```

`brag.mp4` is written as an alias of the landscape render when a single-aspect
run needs the historical filename.

## 8. Exit codes

| Code | Meaning |
|---|---|
| 0 | Ran to completion. Read the warnings summary: `0` does not mean every aspect rendered. |
| 2 | Bad arguments, or the composition directory does not exist. |
| 3 | The pinned HyperFrames CLI could not be resolved. |
| 4 | No requested aspect has a composition, or one declares the wrong aspect. |
| 5 | Completed, but no video was produced. |
