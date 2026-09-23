# Live App, Terminal & Emulator Capture Workflow

Capturing real screen recordings, terminal sessions, and high-resolution screenshots from running applications and CLI tools elevates the video from an abstract mockup to an authentic product showcase.

---

## 1. Terminal, CLI & TUI Tools (`pluvia`, `hyperindex`, `omnihud`, `token-trimmer`)

Developer tools and CLI utilities shine when their terminal interactions are rendered with pristine typography and authentic execution.

### Method A: `asciinema` + High-DPI Replay
1. **Record Terminal Interaction:**
   ```bash
   asciinema rec demo.cast --command "hindex search 'fast audio dsp' --tui"
   ```
2. **Convert to SVG / Frame Sequence:**
   ```bash
   # Convert to high-DPI vector SVG
   termtosvg <composition-assets-dir>/terminal_demo.svg -c "hindex search 'fast audio dsp'"
   # Or render to animated GIF / MP4 via agg
   agg --font-family "JetBrains Mono" --font-size 20 --theme monokai demo.cast <composition-assets-dir>/terminal_clip.gif
   ```

### Method B: Native Hyperframes HTML/CSS Terminal Engine
Instead of pixelated video embeds, recreate the terminal natively inside Hyperframes for crisp, vector-sharp scaling at 4K:
```html
<div class="terminal-window">
  <div class="terminal-titlebar">
    <div class="window-controls">
      <span class="control close"></span>
      <span class="control minimize"></span>
      <span class="control expand"></span>
    </div>
    <span class="terminal-title">darnell@drnzy-pro: ~/Projects/hyperindex</span>
  </div>
  <div class="terminal-body">
    <div class="command-line">
      <span class="prompt">$</span>
      <span class="command" id="typed-cmd">hindex search "acoustic resonance"</span>
      <span class="cursor"></span>
    </div>
    <div class="terminal-output" id="output-block">
      <div class="ansi-cyan">⚡ Found 14 matches in 2.1ms (GPU CUDA ONNX)</div>
      <div class="ansi-dim">crates/cadence-dsp/src/filter.rs:84</div>
    </div>
  </div>
</div>
```

### Method C: PTY Stream / Script Replay with Synced Audio
- Animate the prompt typing character-by-character with randomized jitter (`40ms–90ms` delay).
- Trigger a randomized `keypress-*.wav` from `assets/sfx/keyboard/` on each character for an authentic tactile typing soundscape.

---

## 2. Mobile Apps (React Native, Expo, Android/iOS, Flutter)

### Method A: Android Emulator / Physical Device (`adb`)
1. **Launch App:**
   ```bash
   adb shell am start -n <package.name>/.MainActivity
   ```
2. **Capture Full-Res Screenshot:**
   ```bash
   adb exec-out screencap -p > <composition-assets-dir>/real_screen_1.png
   ```
3. **Capture High-FPS Screen Recording:**
   ```bash
   adb shell screenrecord --bit-rate 16000000 --time-limit 10 /sdcard/app_demo.mp4
   adb pull /sdcard/app_demo.mp4 <composition-assets-dir>/real_demo.mp4
   ```

### Method B: Expo / React Native Web Preview
1. Start Metro bundler: `npx expo start --web`
2. Capture with Puppeteer at exact mobile viewport:
   - Width: `393`, Height: `852` (iPhone 16 Pro resolution)
   - `deviceScaleFactor: 3` (Retina sharpness)
3. Save directly to `<output-dir>/composition/assets/screen_mobile.png`.

---

## 3. Web Applications (Next.js, Vite, React, Svelte, Vue)

### High-DPI Puppeteer Capture
1. Ensure local dev server is running (`http://localhost:3000` or `5173`).
2. Run automated headless capture:
   - Viewport: `1920x1080` (or `3840x2160` for 4K)
   - `deviceScaleFactor: 2`
3. Simulate user interactions (`puppeteer_click`, `puppeteer_fill` search bars or toggle tabs).
4. Save crisp PNGs/MP4s into `<output-dir>/composition/assets/`.

---

## 4. Desktop Applications (GTK4, Libadwaita, Qt, Electron, Tauri, X11/Wayland)

### High-Fidelity Desktop Window Capture
1. Launch desktop app (e.g. `pluvia-studio &` or `cadence &`).
2. Identify window ID via `xdotool search --name "Pluvia Studio"` or `swaymsg -t get_tree`.
3. Capture crisp PNG:
   ```bash
   import -window $(xdotool search --name "Pluvia Studio" | head -1) <composition-assets-dir>/app_window.png
   ```
4. Record interaction clip with FFmpeg:
   ```bash
   ffmpeg -y -f x11grab -video_size 1920x1080 -i :0.0+0,0 -t 6 <composition-assets-dir>/desktop_clip.mp4
   ```

---

## 5. Embedding Captured Assets in Composition

1. **Mobile Frame (iPhone 16 Pro):**
   ```html
   <div class="device-bezel iphone-16-pro">
     <div class="dynamic-island"></div>
     <img src="assets/real_screen_1.png" class="device-screen" alt="Real App Screen" />
   </div>
   ```

2. **Desktop Frame (MacBook Pro / Studio Display):**
   ```html
   <div class="device-bezel macbook-pro">
     <video src="assets/real_demo.mp4" data-start="2.5" data-duration="4.5" muted autoplay playsinline></video>
   </div>
   ```

3. **Terminal Frame (CLI / TUI):**
   ```html
   <div class="device-bezel terminal-pro">
     <div class="terminal-content">...</div>
   </div>
   ```
