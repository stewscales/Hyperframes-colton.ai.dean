# DESIGN.md — trading-formats
# "10 Content Formats That Always Work — Scales Coaches Edition"
# Style reference: unknown-6 (reel-6) — primary style reference

---

## Style Prompt

Ultra-clean, credibility-first listicle. Pure white background panel dominates the top third and stays on screen the entire video — it anchors the viewer and provides instant context even on a mid-scroll entry. The creator's face-cam fills the frame as the warm, natural base layer. Each list item arrives as a crisp numbered label in white bold mono over the face-cam, bottom-third, no background plate. Overlay clips slot into the lower-centre as a vertical phone-frame proof insert each time. Hard cuts only — the rhythm is the design. Nothing fancy, nothing distracting. The speed and structure do all the work.

---

## Colors

| Role | Hex | Usage |
|---|---|---|
| White card background | `#ffffff` | Persistent title card background |
| Black type (card) | `#111111` | Title text on white card |
| Sub-label border | `#cccccc` | Thin border on the niche qualifier pill |
| Sub-label text | `#555555` | Lighter text inside `( Scales Coaches Edition )` pill |
| White label text | `#ffffff` | Lower-third `N ) Item Name` labels — over face-cam |
| Face-cam base | n/a | Jude's natural skin tone — warm daylight |

**Anti-patterns:**
- NO electric blue, no neon accents on the face-cam layer
- NO gradient text — strictly solid `#111111` on white
- NO drop shadow on the white card
- NO border on the white card itself (clean flat edge)
- NO coloured backgrounds behind the lower-third labels

---

## Typography

| Role | Font | Weight | Size (1280px tall canvas) |
|---|---|---|---|
| Title (card) | `DM Sans` | 800 | 42–46px |
| Sub-label | `DM Sans` | 400 | 20px |
| Item label (lower-third) | `Space Mono` | 700 | 36px |

Font notes:
- `DM Sans` is the inter-compatible modern rounded sans — close match to reference card type
- `Space Mono` for the `N ) Item Name` lower-thirds — geometric mono matches reference exactly
- Both embedded automatically by Hyperframes compiler

---

## Layout

**Canvas**: 720 × 1280 (9:16 vertical, 30fps)

**Layer stack (z-index order):**
1. `z-index: 1` — Jude face-cam, full-bleed base, entire duration
2. `z-index: 10` — Overlay insert clips (lower-centre, 288×512px box, centred at x=216, y=720–1232)
3. `z-index: 20` — Persistent white title card (top of frame, full video duration)
4. `z-index: 30` — Numbered item labels `N ) Item Name` (lower-third, over everything)

**White title card:**
- Position: top 5% → width ~92%, centred, so `left: 26px; right: 26px; top: 64px`
- Height: auto, ~160px to fit two lines + sub-label
- Background: `#ffffff`, `border-radius: 16px`
- Padding: `20px 24px 16px`

**Overlay insert position:**
- Centred horizontally: `left: 50%; transform: translateX(-50%)`
- Top of insert at ~56% from top (y ≈ 717px)
- Size: 240px wide × 426px tall (maintains 9:16 within the insert)
- `border-radius: 12px; overflow: hidden`

**Lower-third labels:**
- `bottom: 15%` from bottom → approximately `y: 1088px`  
- Centred: `text-align: center; width: 100%`
- Font: Space Mono 700, 36px, `#ffffff`
- `text-shadow: 0 2px 8px rgba(0,0,0,0.6)` for legibility over face-cam

---

## Motion Rules

- **Title card**: appears at t=0 with a 0.3s fade-in (`power2.out`). Stays static the entire video.
- **Overlay clips**: snap in at hard-cut boundaries (no transition effect). Brief scale entrance: `gsap.from(el, { scale: 0.95, opacity: 0, duration: 0.12, ease: "power3.out" })`
- **Item labels**: replace text instantly at each hard cut. Brief opacity fade: 0 → 1 over 0.1s.
- **NO whip transitions, NO push slides, NO blur crossfades** — the reference uses pure hard cuts.
- Exit animations banned on all labels/overlays except the final label (which fades out at end).

---

## What NOT To Do

1. No GSAP `repeat: -1` on any element
2. No transition effects between items — hard cuts replicate the reference style exactly
3. No word-by-word caption strip — labels are descriptive headers, not speech transcriptions
4. No electric blue or brand accent colours on the content layer (save brand colours for outro only)
5. No motion blur, no particle effects, no kinetic typography — this is a proof-of-concept listicle, not a visual flex
