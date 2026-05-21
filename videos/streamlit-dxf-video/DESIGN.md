# Design System

## Overview

Sheet Metal DXF MVP is a clean Streamlit engineering tool for generating sheet metal DXF files from structured parameters. The interface is bright, spacious, and form-driven, with a single large heading, tab navigation, full-width input controls, and a restrained red accent for active state. The visual identity should feel precise, practical, and CAD-adjacent rather than decorative.

## Colors

- **Primary Surface**: `#FFFFFF` — main canvas and page background.
- **Input Surface**: `#F0F2F6` — Streamlit input fields and quiet panels.
- **Primary Text**: `#31333F` — headings, labels, and main copy.
- **Active Accent**: `#FF4B4B` — selected tab and action emphasis.
- **Link Blue**: `#0054A3` — secondary technical accent.
- **Black**: `#000000` — high contrast micro details.

## Typography

- **Interface Sans**: Source Sans, 400 and 700. Captured Streamlit UI font for labels, tabs, body copy, and buttons.
- **Technical Mono**: Source Code Pro variable, 500 to 800. Use for JSON snippets, DXF filenames, dimensions, and generated values.
- **Hierarchy**: 84px+ for video headlines, 34-46px for supporting statements, 22-28px for interface annotations, 18px minimum for labels.

## Elevation

The site is mostly flat, using subtle 1px borders and pale gray surfaces instead of shadows. For video, lift the captured UI screenshot into a soft device-like panel with a thin `#F0F2F6` border and a gentle shadow. Keep depth calm and functional: layered panels, CAD guide lines, and small callouts rather than dramatic glass effects.

## Components

- **Streamlit Header**: Large Chinese H1 with generous top whitespace.
- **Tab Selector**: Two-tab navigation with `#FF4B4B` active underline.
- **Full-Width Selectbox**: Pale gray selection bar for part type.
- **Parameter Form Grid**: Wide bordered form area with numeric inputs arranged in rows.
- **Generate Button**: Full-width bordered button at the bottom of the form.
- **JSON Upload Zone**: Secondary tab capability, useful as a workflow proof point.
- **DXF Output Summary**: Generated dimensions and download button shown after creation.

## Do's and Don'ts

### Do's

- Use a bright engineering workspace with plenty of white and light gray.
- Use `#FF4B4B` sparingly to guide the viewer's eye to action states.
- Use mono type for measurements, filenames, and JSON-to-DXF pipeline labels.
- Show the captured webpage screenshot as the recognizable product surface.
- Add CAD-inspired line work, bend lines, and dimension tags as motion graphics.

### Don'ts

- Do not make the video dark, neon, or cinematic beyond the product's quiet engineering feel.
- Do not hide the actual UI behind abstract visuals.
- Do not overuse gradients; keep surfaces mostly solid and readable.
- Do not imply the DXF is production-approved; keep engineer review language visible.
