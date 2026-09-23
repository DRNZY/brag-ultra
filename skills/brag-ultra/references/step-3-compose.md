# Step 3: Compose with Hyperframes

Write `<output-dir>/composition-brief.md` before building or editing the Hyperframes composition.

---

## Structure of `composition-brief.md`

```markdown
# Hyperframes Composition Brief: [App / Tool Name]

## Objective
Create an Apple-grade launch video for [App / Tool Name] with responsive multi-format styling, kinetic shaders, and mastered audio.

## Output Specifications
- **Composition Directory:** `<output-dir>/composition/`
- **Output Videos:** `<output-dir>/brag.mp4` (and multi-format targets: 16:9 `1920x1080`, 9:16 `1080x1920`, 1:1 `1080x1080`)
- **Duration:** [15–25 seconds]
- **Target Formats:** [Landscape / Vertical / Square / All]

## Visual Polish & Shaders
- **Film Grain:** Include SVG `feTurbulence` overlay (3–5% opacity) over the entire viewport.
- **Chromatic Aberration:** Micro RGB-split on impact cuts (`.chromatic-hit`).
- **Path Animations:** SVG stroke drawing for architecture lines, arrows, or badges.
- **Device Frames:** Apple iPhone 16 Pro Dynamic Island, MacBook Pro, or Titanium Pro Terminal.

## Audio Mastering Contract
- **Music Track:** `assets/music/[track].mp3` (Base volume: 0.35).
- **Voiceover:** When enabled, place `assets/voiceover.wav` on Track 1. Music must duck to 0.10 (-12dB) during speech with 0.3s attack / 0.5s release.
- **SFX Trigger Layers:**
  - Keystrokes: `assets/sfx/keyboard/keypress-*.wav` (Volume 0.40).
  - Reveal Hits: `assets/sfx/impact/impactBell_heavy_000.ogg` (Volume 0.80).
  - UI Toggles: `assets/sfx/interface/click_002.ogg` (Volume 0.60).

## Responsive CSS Reflow Rules
- Use CSS `@container` queries or viewport units (`cqw`, `cqh`, `vw`, `vh`) so elements adapt seamlessly:
  - **16:9 (`1920x1080`):** Side-by-side split layout (Text on left, Device/Terminal on right).
  - **9:16 (`1080x1920`):** Vertical stack layout (Headline at top safe zone, Device centered, Result at bottom).
  - **1:1 (`1080x1080`):** Centered high-impact card with generous padding.
```

---

## Audio Asset Staging

Always copy required audio files into the local composition directory:

```bash
mkdir -p <output-dir>/composition/assets/music
mkdir -p <output-dir>/composition/assets/sfx/interface <output-dir>/composition/assets/sfx/impact <output-dir>/composition/assets/sfx/keyboard

# Copy music
cp <skill-dir>/assets/music/happy-beats-business-moves-vol-1-by-ende-dot-app.mp3 <output-dir>/composition/assets/music/

# Copy selected SFX
cp <skill-dir>/assets/sfx/impact/impactBell_heavy_000.ogg <output-dir>/composition/assets/sfx/impact/
cp <skill-dir>/assets/sfx/interface/click_002.ogg <output-dir>/composition/assets/sfx/interface/
cp <skill-dir>/assets/sfx/keyboard/*.wav <output-dir>/composition/assets/sfx/keyboard/
```

---

## Voiceover Generation & Ducking Keyframes

When `--voice` is active:
```bash
npx hyperframes tts "<Narration Script>" --voice af_heart --output <output-dir>/composition/assets/voiceover.wav
```

Wire into the composition HTML with dedicated track indices:
```html
<!-- Voiceover Track -->
<audio id="vo" data-start="0.5" data-duration="5.2" data-track-index="1" data-volume="1.0" src="assets/voiceover.wav"></audio>

<!-- Background Music Track with -12dB Ducking -->
<audio id="bg-music" data-start="0" data-duration="20" data-track-index="10" data-volume="0.35" src="assets/music/happy-beats-business-moves-vol-1-by-ende-dot-app.mp3"></audio>
```

---

## Validation Gate

Always validate before rendering:
```bash
cd <output-dir>/composition
npx hyperframes check
```
Every reported WCAG contrast issue or layout overflow must be resolved before proceeding.
