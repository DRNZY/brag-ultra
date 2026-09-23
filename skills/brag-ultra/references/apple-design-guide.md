# Apple Design System & Kinetic Motion Guide

How to craft launch videos that embody Apple's keynote aesthetic: quiet confidence, tactile physics, human-centric copy, kinetic shader polish, and breathtaking visual restraint.

---

## 1. Core Visual Hierarchy & Typography

### Typography (SF Pro / Plus Jakarta Aesthetic)
- **Primary Typefaces:** `'SF Pro Display'`, `'SF Pro Text'`, `'Plus Jakarta Sans'`, `'JetBrains Mono'` (for CLI / Code), `-apple-system, BlinkMacSystemFont, sans-serif`.
- **Title Tracking:** Tight optical kerning for hero headlines (`letter-spacing: -0.04em` for 64px+, `-0.02em` for 32px–48px).
- **Hierarchy:** High-contrast pairing — bold, weighty titles (`font-weight: 800` or `700`) with crisp, light, legible subtitles (`font-weight: 500`, opacity `0.75`–`0.85`).
- **Never Use Generic Text:** All copy must be sharp, authentic, and project-specific.

### Materials & Glassmorphism
- **Obsidian Dark & Titanium Light:** Deep obsidian (`#08090D`, `#0E1117`), pure titanium (`#F5F5F7`, `#FFFFFF`).
- **Precision Hairlines:** 1px borders with subtle gradients (`rgba(255, 255, 255, 0.12)` fading to `rgba(255, 255, 255, 0.03)`).
- **Multi-stop Frosted Glass:**
  ```css
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(28px) saturate(190%);
  -webkit-backdrop-filter: blur(28px) saturate(190%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.55), 0 0 1px 1px rgba(255, 255, 255, 0.06) inset;
  ```

---

## 2. Kinetic Shaders & Visual Texture

### Apple-Grade Film Grain Overlay
Eliminate color banding in dark gradients and provide tactile photographic texture using an animated SVG turbulence filter:
```html
<svg class="grain-overlay" xmlns="http://www.w3.org/2000/svg">
  <filter id="grain">
    <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="3" stitchTiles="stitch" />
    <feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.04 0" />
  </filter>
  <rect width="100%" height="100%" filter="url(#grain)" />
</svg>
```
```css
.grain-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 999;
  opacity: 0.8;
  mix-blend-mode: overlay;
}
```

### Lens Chromatic Aberration
Subtle RGB color splitting on high-velocity slams and transitional camera shakes:
```css
.chromatic-hit {
  text-shadow: -2px 0 1px rgba(255, 0, 80, 0.4), 2px 0 1px rgba(0, 220, 255, 0.4);
}
```

### SVG Path Stroke Animations
For architecture graphs, checkmarks, line charts, and outline logos:
```css
.path-draw {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: drawPath 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes drawPath {
  to { stroke-dashoffset: 0; }
}
```

---

## 3. Physical Spring Motion Dynamics

Apple motion is **fluid, physical, and continuous**:
- **Critically Damped Settles:** No jarring linear animations or cartoonish bouncing.
  - GSAP Easing: `ease: "expo.out"`, `ease: "power4.out"`, or `ease: "circ.out"`.
  - Spring Physics: `mass: 1.0, stiffness: 140, damping: 16`.
- **Scale on Reveal:** Subtle entrance from `scale: 0.94` to `1.0` with `y: 28` to `0` over `0.6s–0.8s`.
- **Coordinate Transforms:** Always animate GPU-composited properties (`x`, `y`, `scale`, `opacity`, `rotation`) — never layout properties (`top`, `left`, `width`, `height`).

---

## 4. Multi-Format Responsive Reflow & Framing

### Device Hardware Frames
- **iPhone 16 Pro (Mobile):** Titanium bezel (`border-radius: 52px`), Dynamic Island pill (`110x32px`), reflective gradient sheen.
- **MacBook Pro / Studio Display (Desktop):** Aluminum unibody, glass corner radiuses, diffuse floor shadow (`0 40px 80px rgba(0, 0, 0, 0.6)`).
- **Pro Terminal (CLI / DevTools):** Titanium titlebar with traffic light buttons (`#FF5F56`, `#FFBD2E`, `#27C93F`), JetBrains Mono typography, glowing prompt cursor.

### Responsive Aspect Ratio Reflow Table

| Format | Dimensions | Layout Strategy | Safe Zone Padding |
|---|---|---|---|
| **16:9 Landscape** | `1920x1080` | Two-column split, widescreen terminal, hero + feature cards | Top/Bottom: 60px, Sides: 80px |
| **9:16 Vertical** | `1080x1920` | Single-column stack, full-height mobile frame, giant top titles | Top: 160px, Bottom: 240px (Shorts/TikTok UI) |
| **1:1 Square** | `1080x1080` | Centered focal card, tight typography, compact bezel | All sides: 60px |

```css
/* Responsive container query / aspect ratio adapting */
@container (max-aspect-ratio: 1/1) {
  .hero-container {
    flex-direction: column;
    gap: 32px;
  }
  .device-bezel {
    max-width: 85%;
  }
}
```
