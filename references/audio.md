# Audio Reference & Mastering Guide

All SFX are CC0 (Kenney.nl, public domain). Music and SFX should be used by default unless the user passes `--no-music`, `--no-sfx`, the required assets are missing, or the plan explicitly chooses silence as a creative device.

---

## 1. Intelligent Audio Mastering & Voiceover Ducking

When narration/voiceover (`--voice`) or dialogue is present:
- **Background Music Ducking:** Automatically duck the music bed by **-12dB** (e.g. from volume `0.35` down to `0.09–0.11`) during active speech segments.
- **Envelope Curves:**
  - **Attack:** Smooth fade-down over `0.30s` before the first spoken syllable.
  - **Release:** Smooth fade-up over `0.50s` after speech concludes.
  - **Hold:** Keep steady ducked level across natural pauses between adjacent sentences (<0.8s) to avoid distracting volume pumping.

### Mastering Gain Staging Table

| Element | Target RMS / Volume | Peak Limiting | Character |
|---|---|---|---|
| **Voiceover (Kokoro TTS)** | `0.90 – 1.00` | Hard cap at -0.1 dB | Crisp, centered, presence-boosted |
| **Background Music Bed (Normal)** | `0.30 – 0.38` | Soft curve | Warm, energetic foundation |
| **Background Music Bed (Ducked)** | `0.09 – 0.12` (-12dB) | Soft curve | Subtle texture under spoken dialogue |
| **Impact / Hero Reveal SFX** | `0.70 – 0.85` | -0.3 dB peak | Punchy, resonant, clean transient |
| **UI Clicks / Toggles** | `0.45 – 0.60` | -1.0 dB peak | Sharp, light micro-feedback |
| **Typing Keystrokes** | `0.35 – 0.50` | -1.5 dB peak | Randomized velocity, organic cadence |

---

## 2. Multi-Track Timeline Architecture

Ensure each audio layer has a dedicated, non-overlapping `data-track-index` to prevent audio collisions in Hyperframes:

```html
<!-- Track 1: Voiceover Narration (Highest Priority) -->
<audio id="vo" data-start="0.5" data-duration="4.2" data-track-index="1" data-volume="1.0" src="assets/voiceover.wav"></audio>

<!-- Track 10: Background Music Bed (With Ducking Keyframes) -->
<audio id="bg-music" data-start="0" data-duration="20" data-track-index="10" data-volume="0.35" src="assets/music/happy-beats-business-moves-vol-1-by-ende-dot-app.mp3"></audio>

<!-- Track 20+: Synced SFX Layers -->
<audio id="sfx-slam" data-start="0.2" data-duration="1.2" data-track-index="20" data-volume="0.80" src="assets/sfx/impact/impactBell_heavy_000.ogg"></audio>
<audio id="sfx-key1" data-start="1.4" data-duration="0.3" data-track-index="21" data-volume="0.45" src="assets/sfx/keyboard/keypress-004.wav"></audio>
<audio id="sfx-click" data-start="3.8" data-duration="0.5" data-track-index="22" data-volume="0.65" src="assets/sfx/interface/click_002.ogg"></audio>
```

---

## 3. Audio-Reactive Visuals

Hyperframes can extract RMS energy and sub-bass frequency bands from the music track to dynamically modulate visual elements:
- **Atmospheric Glow:** Background radial gradient or hero card glow pulses subtly with the bass rhythm.
- **Card Scale / Elevation:** Device bezels or metric badges gain slight breathing motion (+1.5% scale) on heavy transients.
- **Chromatic Intensity:** Kinetic shader aberration flares softly on bass drops.
- **Restraint Rule:** Never display generic frequency bars or strobing visualizers; only modulate authentic UI properties.

---

## 4. Beat and Cue Detection

Beat synchronization aligns major product reveals to strong musical transients:

1. **Bundled Cue Presets (Instant):**
   ```text
   <skill-dir>/assets/music/cues/<track-stem>.music-cues.json
   ```
2. **Extended Python Cue Analysis (`analyze_music_cues.py`):**
   ```bash
   uv run --project <skill-dir>/scripts \
     python <skill-dir>/scripts/analyze_music_cues.py <track>.mp3 \
     --output-json <output-dir>/composition/assets/music/cues/<stem>.music-cues.json \
     --output-md  <output-dir>/composition/assets/music/cues/<stem>.music-cues.md
   ```
3. **Hyperframes CLI Beats (`hyperframes beats`):**
   ```bash
   npx hyperframes beats <output-dir>/composition
   ```

### Beat Sync Tolerances
- **Major Product Reveals:** Align within `±0.15s` of a `strongCue`.
- **Sequential Lists / Badges:** Snap within `±0.10s` of a `beats[]` timestamp.
- **Text Legibility Floor:** If BPM is high (>110 BPM), reveal every second beat or batch reveals to preserve the 0.8s readability rule.

---

## 5. SFX Catalog & Sound Design Strategy

### UI & Micro-interactions (`assets/sfx/interface/` & `assets/sfx/ui/`)
- `click_001` through `click_005.ogg`: Crisp, tactile button activations.
- `switch_001` through `switch_007.ogg`: Binary toggles, dark-mode switches, filter pills.
- `drop_001` through `drop_003.ogg`: Floating card settlements, toast arrivals.
- `select_008.ogg`: Tab navigation, segmented control toggles.

### Impacts & Weight (`assets/sfx/impact/`)
- `impactSoft_medium_000` through `004.ogg`: Safe, punchy scene reveals.
- `impactBell_heavy_000` / `003` / `004.ogg`: Apple-grade resonant hero moments and logo slams.
- `impactMetal_light_002` / `impactGlass_light_001`: Metric count-up completions, badge awards.

### Typing & Terminal Cadence (`assets/sfx/keyboard/`)
- 32 discrete WAV keystroke files (`keypress-001.wav` to `keypress-032.wav`).
- Select randomly per character in typing animations to create a natural, non-repetitive mechanical keyboard soundscape.
