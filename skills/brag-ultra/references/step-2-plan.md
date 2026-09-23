# Step 2: Write the Brag Plan

Write `<output-dir>/brag-plan.md`. This is the creative north star and contract for the video composition.

---

## Structure of `brag-plan.md`

```markdown
# Brag Plan: [Product Name]

## 1. Product & Breakthrough Claim
- **Summary:** [One sentence what it does]
- **The Angle:** [The creative hook — why this tool is extraordinary]
- **Standout Metric:** [e.g. 2.1ms search speed, 32-bit floating point audio, 100% on-device]

## 2. Format & Motion Dynamics
- **Formats:** [16:9 Landscape / 9:16 Vertical / 1:1 Square / All]
- **Target Duration:** [15–25 seconds]
- **Spring Physics:** GSAP Critically Damped (`ease: "expo.out"`, `stiffness: 140, damping: 16`)
- **Kinetic Shaders:** [Film grain overlay 4%, chromatic impact split, SVG path trace]

## 3. Visual Identity & Framing
- **Background:** `#08090D` (Obsidian)
- **Text:** `#F5F5F7` (Titanium Light)
- **Accent:** [Brand Accent HEX]
- **Device Frame:** [iPhone 16 Pro Dynamic Island / MacBook Pro / Pro Titanium Terminal]
- **Fonts:** Display (`SF Pro / Plus Jakarta Sans`), Code (`JetBrains Mono`)

## 4. Audio & Mastering Architecture
- **Music Bed:** [Track filename from assets/music/]
- **Voiceover Narration:** [Disabled / Kokoro TTS voice `af_heart`]
- **Ducking Policy:** Automatic -12dB music ducking during voice segments (0.3s attack, 0.5s release)
- **SFX Palette:** [Keyboard typing, soft impacts, click triggers, bell finish]

## 5. Storyboard

### Scene 1 — The Hook — [Duration: 2.5s]
- **Visual:** [High-contrast title slam or terminal launch]
- **Copy:** "[Opening Hook Line]"
- **Interaction / Sequential:** [Cursor typing command or phone sliding in]
- **Audio / SFX:** [Impact hit at 0.1s, keystroke sounds on typing]
- **Transition:** [Fast scale-in `power4.out`] → Scene 2

### Scene 2 — The Core Engine / Flow — [Duration: 4.5s]
- **Visual:** [Real UI interaction or split-screen feature execution]
- **Copy:** "[Action description or live output]"
- **Interaction / Sequential:** [3 items appearing in sequence or live search filtering]
- **Audio / SFX:** [Subtle click at each item arrival]
- **Transition:** [Slide wipe with motion blur] → Scene 3

### Scene 3 — Key Benchmark & Power Highlight — [Duration: 4.0s]
- **Visual:** [Metric counter counting up, or SVG architecture graph path drawing]
- **Copy:** "[Specific claim / benchmark]"
- **Audio / SFX:** [Glass shimmer / metal ring on count completion]
- **Transition:** [Smooth zoom settle] → Scene 4

### Scene 4 — Outro & Brand Slam — [Duration: 3.0s]
- **Visual:** [Full product logo, GitHub repo / URL badge, Apple-grade diffuse glow]
- **Copy:** "[Product Name] — [Final Punchline]"
- **Audio / SFX:** [Resonant heavy bell `impactBell_heavy_000`, music swell and fade]

---

## 6. Voiceover Script (Optional — when `--voice` enabled)
- **0.0s – 2.5s:** "[Hook narration]"
- **2.5s – 7.0s:** "[Feature & execution narration]"
- **7.0s – 11.0s:** "[Benchmark & performance claim]"
- **11.0s – 14.0s:** "[Closing invitation / call to action]"
```
