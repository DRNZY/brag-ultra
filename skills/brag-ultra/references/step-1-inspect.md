# Step 1: Inspect the Project & Environment

Read the project directory to understand what you're bragging about — whether it's a web application, mobile app, desktop GUI, CLI/TUI tool, or low-level library.

---

## 1. What to Inspect by Project Type

### A. Web & Mobile Applications
1. **`index.html` / `App.tsx` / `app/` routes:** Hero headline, tagline, value propositions, key UI components.
2. **`styles.css` / Tailwind configs:** Color palette (`:root` variables, OKLCH / HEX colors), fonts, dark mode accents.
3. **`package.json` / `app.json`:** App name, description, dependencies.

### B. CLI, TUI & Systems Tools (`pluvia`, `hyperindex`, `omnihud`, `token-trimmer`)
1. **`Cargo.toml` / `pyproject.toml` / `package.json` / `go.mod`:** Binary names, version, description.
2. **CLI Entry Points & Commands (`main.rs`, `cli.py`, `bin/`):** Command arguments, flags, subcommands (`hindex search`, `pluvia-cli load`).
3. **Help Output & README:** Run `--help` or read README command examples to extract real syntax, realistic inputs, and high-speed execution benchmarks (e.g. `2.1ms`, `ONNX CUDA`, `FTS5 BM25`).

---

## 2. The 9-Question Brag Ultra Rubric

Answer all nine questions before moving to Step 2:

```text
1. What is the product / tool?
   One sentence. What does it actually do or compute?

2. What is the most impressive benchmark, claim, or feature?
   The standout metric (e.g. "Sub-millisecond LRC sync", "Zero cloud telemetry", "10x token reduction").

3. What is the visual hook?
   The strongest visual: a responsive app screen, an Apple-grade terminal execution, an interactive waveform, or a sleek frosted glass card.

4. What actual interaction or flow should be shown?
   (Mobile app flow, desktop window capture, or live typing CLI execution).

5. What is the target format and shortest satisfying duration?
   Format: 16:9 Landscape, 9:16 Vertical, 1:1 Square, or All / Kit. Duration: 15–25s.

6. What tone fits best?
   Tone preset (e.g. apple-keynote, polished, chaotic, yc-parody) + custom creative direction.

7. What is the audio & voiceover architecture?
   Background music track + -12dB auto-ducking on voiceover + synchronized SFX (keypresses, impacts, toggles).

8. What should the primary share caption say?
   1–2 punchy sentences formatted for immediate posting.

9. What is the 3-beat user flow?
   Input / Entry → Execution / Breakthrough Action → Tangible Result / Output.
```

---

## 3. Visual & Style Extraction

Extract the following exact properties:
- **Background Color:** (e.g. `#08090D` obsidian or `#000000`)
- **Primary Text:** (e.g. `#F5F5F7` titanium)
- **Signature Brand Accent:** (e.g. Coral `#FF5C38`, Apple Blue `#0071E3`, Emerald `#10B981`)
- **Typography:** Display font (Heading) and Monospace font (Terminal / Code)
- **Device & Chrome Framing:** iPhone 16 Pro, MacBook Pro, or Titanium Pro Terminal
