# Storyboard

**Format:** 1920x1080 landscape  
**Audio:** Caption-led demo, no generated voiceover in this first pass  
**VO direction:** Calm technical product tour if narration is added later  
**Style basis:** DESIGN.md, captured Streamlit screenshot, engineering/CAD motion graphics

## Asset Audit

| Asset | Type | Assign to Beat | Role |
| --- | --- | --- | --- |
| `capture/screenshots/scroll-000.png` | Website screenshot | Beats 1-5 | Main product UI surface |
| `capture/assets/svgs/open.svg` | SVG icon | Beat 2 | Selectbox cue |
| `capture/assets/svgs/icon-1.svg` | SVG icon | Beat 4 | Download/link cue |
| `capture/assets/svgs/e1t4gh341.svg` | SVG icon | Beat 5 | Utility icon accent |

## Beat 1 — Hook (0.00-4.00s)

**Text:** JSON parameters to DXF in one local tool.

**Concept:** The viewer starts in a bright engineering workspace. The captured Streamlit page slides into view as the actual product, not a mockup. Thin CAD guide lines sketch themselves behind it, implying the interface is connected to geometry.

**Visual:** White background, UI screenshot in a large framed panel, red active-tab accent echoed by a small pipeline label. Floating mono labels read `JSON`, `Python`, `ezdxf`, `DXF`.

**Transition:** Soft push upward into the parameter beat.

## Beat 2 — Parameters (4.00-9.00s)

**Text:** Pick a bracket type. Fill in bend and material parameters.

**Concept:** The form becomes the hero. Parameter chips lift from the screenshot and arrange into a readable engineering checklist.

**Visual:** Highlight rings trace around part type, thickness, bend radius, K factor, and dimensions. A small U bracket flat outline draws at the right edge.

**Transition:** Red line sweep across the form into generation.

## Beat 3 — Shared Engine (9.00-14.00s)

**Text:** The Web UI uses the same tested Python generation path.

**Concept:** The video briefly reveals the product's internal pipeline. It should feel reassuring: no duplicate logic, just one path from validated parameters to DXF.

**Visual:** Three stacked cards: `Streamlit form`, `generation.py`, `DXF layers`. A connector line animates through them. Small badges show `CUT`, `BEND`, `TEXT`, and `HOLE`.

**Transition:** Zoom through the final `DXF` badge into the result beat.

## Beat 4 — Generate And Download (14.00-19.00s)

**Text:** Generate, review flat size, download DXF.

**Concept:** A clean action moment. The button pulses once, metrics count into place, and the DXF file appears as a tangible output.

**Visual:** Button strip, metrics `188.67 x 200.00 mm`, `BA 4.335 mm`, and a file tile `U_BRACKET_STREAMLIT.dxf`.

**Transition:** Gentle crossfade into the review reminder.

## Beat 5 — Engineer Review (19.00-24.00s)

**Text:** Draft first. Engineer review before production.

**Concept:** End with trust, not hype. A CAD-style flat pattern sits beside the product UI while the message clarifies the workflow boundary.

**Visual:** U bracket outline, dashed bend lines, layer labels, and final CTA: `Open in FreeCAD or AutoCAD`.

**Transition:** Final fade to white.

## Production Architecture

```text
streamlit-dxf-video/
├── index.html
├── DESIGN.md
├── SCRIPT.md
├── STORYBOARD.md
├── narration.txt
├── capture/
│   ├── screenshots/
│   ├── assets/
│   └── extracted/
└── renders/
```
