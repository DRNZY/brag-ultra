# Apple Design System Guide for Launch Videos

How to craft launch videos that embody Apple's keynote aesthetic: quiet confidence, tactile physics, human-centric copy, and breathtaking visual restraint.

---

## 1. Core Visual Principles

### Typography (SF Pro Aesthetic)
- **Primary Typefaces:** `'SF Pro Display'`, `'SF Pro Text'`, `'Plus Jakarta Sans'`, `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`.
- **Title Tracking:** Tight optical kerning for hero headlines (`letter-spacing: -0.035em` for 64px+, `-0.02em` for 32px-48px).
- **Hierarchy:** High contrast pairing — bold, weighty titles (`font-weight: 800` or `700`) with crisp, light, legible subtitles (`font-weight: 500`, opacity `0.75` - `0.85`).
- **Never Use Generic Text:** All copy must be sharp, authentic, and project-specific. Banned: "Title", "Headline", "Feature Callout", "Lorem ipsum", "Streamline your workflow".

### Materials, Glassmorphism & Depth
- **Obsidian & Pure Neutrals:** Deep space black (`#000000`), obsidian dark (`#090A0F`, `#0B0D14`), or titanium light (`#F5F5F7`, `#FFFFFF`).
- **Vibrant Accents:** One signature accent color derived from the product (e.g., Coral `#FF5C38`, Apple Blue `#0071E3`, Emerald `#10B981`, Purple `#AF52DE`), used with restraint.
- **Translucent Materials:** Multi-stop frosted glass:
  ```css
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5), 0 0 1px 1px rgba(255, 255, 255, 0.05) inset;
  ```
- **Precision Hairlines:** 1px borders with subtle gradients (`rgba(255, 255, 255, 0.12)` fading to `rgba(255, 255, 255, 0.04)`).

---

## 2. Apple Device Framing

When presenting mobile, tablet, or desktop products, frame them inside precision Apple hardware bezels:

### iPhone 16 Pro Bezel (Mobile)
- Titanium frame (`border: 3px solid rgba(255, 255, 255, 0.15); border-radius: 48px;`)
- Dynamic Island cutout (`width: 110px; height: 32px; background: #000; border-radius: 20px;`)
- Corner radius on screen content: `42px`
- Screen reflection: Diagonal subtle gradient sheen across the glass.

### MacBook Pro / Studio Display (Desktop & Web)
- Sleek aluminum unibody bezel with subtle camera notch or rounded corners.
- Drop shadow: Diffuse, ambient shadow grounding the device (`0 40px 80px rgba(0, 0, 0, 0.6)`).

---

## 3. Motion Physics & Spring Dynamics

Apple motion is **fluid, physical, and continuous**:
- **Critically Damped Settles:** No jarring linear animations or cartoonish bouncing.
  - GSAP easing: `ease: "power4.out"`, `ease: "expo.out"`, or `ease: "circ.out"`.
  - Spring overshoot only on gestural throws / releases (`ease: "back.out(1.2)"`).
- **Scale on Reveal:** Subtle entrance from `scale: 0.94` to `1.0` with `y: 30` to `0` over `0.6s` - `0.8s`.
- **Coordinate Transformations:** Always animate `x`, `y`, `scale`, `opacity`, and `rotation` — never layout-triggering properties (`top`, `left`, `width`, `height`).

---

## 4. Copywriting Philosophy

- **Quiet Confidence:** State the breakthrough plainly. Let the craftsmanship speak.
- **Short & Punchy:** Three-word claims beat three-sentence paragraphs.
  - *"Turn screenshots into dinners."*
  - *"Zero cloud. Zero tracking. 100% on-device."*
  - *"Your camera roll, finally organized."*
- **Focus on Experience, Not Tech Specs:** Lead with the feeling and the outcome, back it up with the technology (e.g. On-Device OCR, Local SQLite).
