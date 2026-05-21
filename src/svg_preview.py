"""SVG preview helpers for Streamlit sheet metal flat patterns."""

from __future__ import annotations

from html import escape
from typing import Iterable, Union

from sheet_metal_math import (
    CircularHole,
    CornerChamfer,
    CornerRadius,
    EdgeNotch,
    FlatPlatePattern,
    LBracketFlatPattern,
    LBracketWithHolesFlatPattern,
    SlotHole,
    UBracketFlatPattern,
    UBracketWithHolesFlatPattern,
)


Pattern = Union[UBracketFlatPattern, UBracketWithHolesFlatPattern, LBracketFlatPattern, LBracketWithHolesFlatPattern, FlatPlatePattern]
LayerName = str

SVG_WIDTH = 780
SVG_HEIGHT = 560
SVG_PADDING_X = 78
DRAWING_TOP = 132
DRAWING_BOTTOM = 390
DEFAULT_VISIBLE_LAYERS = frozenset({"CUT", "BEND", "HOLE", "TEXT"})


def _preview_transform(flat_width: float, flat_length: float) -> tuple[float, float, float]:
    scale = min(
        (SVG_WIDTH - SVG_PADDING_X * 2) / flat_width,
        (DRAWING_BOTTOM - DRAWING_TOP) / flat_length,
    )
    offset_x = (SVG_WIDTH - flat_width * scale) / 2.0
    offset_y = DRAWING_TOP + (DRAWING_BOTTOM - DRAWING_TOP - flat_length * scale) / 2.0
    return scale, offset_x, offset_y


def _scaled_points(points: Iterable[tuple[float, float]], flat_width: float, flat_length: float) -> list[tuple[float, float]]:
    scale, offset_x, offset_y = _preview_transform(flat_width, flat_length)
    return [(offset_x + x * scale, offset_y + (flat_length - y) * scale) for x, y in points]


def _point_string(points: Iterable[tuple[float, float]]) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def _line(x1: float, y1: float, x2: float, y2: float, class_name: str) -> str:
    return f'<line class="{class_name}" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" />'


def _arrow_line(x1: float, y1: float, x2: float, y2: float, class_name: str) -> str:
    return (
        f'<line class="{class_name}" x1="{x1:.2f}" y1="{y1:.2f}" '
        f'x2="{x2:.2f}" y2="{y2:.2f}" marker-end="url(#arrow)" />'
    )


def _polygon(points: Iterable[tuple[float, float]], class_name: str) -> str:
    return f'<polygon class="{class_name}" points="{_point_string(points)}" />'


def _dimension_arrowheads(x1: float, y1: float, x2: float, y2: float) -> list[str]:
    dx = x2 - x1
    dy = y2 - y1
    length = (dx * dx + dy * dy) ** 0.5
    if length == 0:
        return []

    arrow_length = 10.0
    arrow_half_width = 4.5
    ux = dx / length
    uy = dy / length
    px = -uy
    py = ux

    start_base_x = x1 + ux * arrow_length
    start_base_y = y1 + uy * arrow_length
    end_base_x = x2 - ux * arrow_length
    end_base_y = y2 - uy * arrow_length

    start_arrow = [
        (x1, y1),
        (start_base_x + px * arrow_half_width, start_base_y + py * arrow_half_width),
        (start_base_x - px * arrow_half_width, start_base_y - py * arrow_half_width),
    ]
    end_arrow = [
        (x2, y2),
        (end_base_x - px * arrow_half_width, end_base_y - py * arrow_half_width),
        (end_base_x + px * arrow_half_width, end_base_y + py * arrow_half_width),
    ]
    return [
        _polygon(start_arrow, "dimension-arrow"),
        _polygon(end_arrow, "dimension-arrow"),
    ]


def _dimension_line(x1: float, y1: float, x2: float, y2: float) -> list[str]:
    return [
        _line(x1, y1, x2, y2, "dimension"),
        *_dimension_arrowheads(x1, y1, x2, y2),
    ]


def _text(
    x: float,
    y: float,
    content: str,
    class_name: str = "label",
    *,
    anchor: str | None = None,
    transform: str | None = None,
) -> str:
    attributes = [
        f'class="{class_name}"',
        f'x="{x:.2f}"',
        f'y="{y:.2f}"',
    ]
    if anchor:
        attributes.append(f'text-anchor="{anchor}"')
    if transform:
        attributes.append(f'transform="{transform}"')
    return f'<text {" ".join(attributes)}>{escape(content)}</text>'


def _pattern_info_lines(pattern: Pattern) -> list[str]:
    lines = [
        f"MATERIAL: {pattern.material}",
        f"THICKNESS: {pattern.thickness:.2f} mm",
        f"FLAT SIZE: {pattern.flat_width:.2f} x {pattern.flat_length:.2f} mm",
    ]
    if hasattr(pattern, "bend_allowance"):
        lines.append(f"BEND ALLOWANCE: {pattern.bend_allowance:.3f} mm")
    if hasattr(pattern, "holes"):
        lines.append(f"HOLES: {len(pattern.holes)}")
    if hasattr(pattern, "features") and pattern.features:
        chamfer_count = sum(1 for feature in pattern.features if isinstance(feature, CornerChamfer))
        radius_count = sum(1 for feature in pattern.features if isinstance(feature, CornerRadius))
        notch_count = sum(1 for feature in pattern.features if isinstance(feature, EdgeNotch))
        summary_parts = []
        if chamfer_count:
            summary_parts.append(f"{chamfer_count} CHAMFER")
        if radius_count:
            summary_parts.append(f"{radius_count} ROUND CORNER")
        if notch_count:
            summary_parts.append(f"{notch_count} EDGE NOTCH")
        lines.append("FEATURES: " + ", ".join(summary_parts))
    return lines


def _normalize_visible_layers(visible_layers: Iterable[LayerName] | None) -> set[str]:
    if visible_layers is None:
        return set(DEFAULT_VISIBLE_LAYERS)
    return {str(layer).strip().upper() for layer in visible_layers}


def _dimension_elements(
    left_x: float,
    right_x: float,
    top_y: float,
    bottom_y: float,
    flat_width: float,
    flat_length: float,
) -> list[str]:
    dim_y = bottom_y + 34.0
    dim_x = left_x - 36.0
    length_label_y = (top_y + bottom_y) / 2.0
    return [
        _line(left_x, bottom_y, left_x, dim_y + 7.0, "extension"),
        _line(right_x, bottom_y, right_x, dim_y + 7.0, "extension"),
        *_dimension_line(left_x, dim_y, right_x, dim_y),
        _text((left_x + right_x) / 2.0, dim_y - 9.0, f"WIDTH {flat_width:.2f} mm", "dim-label", anchor="middle"),
        _line(left_x, top_y, dim_x - 7.0, top_y, "extension"),
        _line(left_x, bottom_y, dim_x - 7.0, bottom_y, "extension"),
        *_dimension_line(dim_x, top_y, dim_x, bottom_y),
        _text(
            dim_x - 11.0,
            length_label_y,
            f"LENGTH {flat_length:.2f} mm",
            "dim-label",
            anchor="middle",
            transform=f"rotate(-90 {dim_x - 11.0:.2f} {length_label_y:.2f})",
        ),
    ]


def _bend_direction_elements(
    bend_positions: Iterable[tuple[float, str]],
    scale: float,
    offset_x: float,
    top_y: float,
    bend_angle: float | None = None,
) -> list[str]:
    elements = []
    angle_text = f"{bend_angle:.0f} DEG" if bend_angle is not None else None
    for x_mm, label in bend_positions:
        x = offset_x + x_mm * scale
        arrow_y = top_y - 14.0
        elements.append(_arrow_line(x - 16.0, arrow_y, x + 16.0, arrow_y, "fold-arrow"))
        note = f"{label} BEND UP {angle_text} VERIFY" if angle_text else f"{label} BEND UP VERIFY"
        elements.append(_text(x, arrow_y - 8.0, note, "bend-note", anchor="middle"))
    return elements


def _hole_table_elements(pattern: FlatPlatePattern | UBracketWithHolesFlatPattern | LBracketWithHolesFlatPattern) -> list[str]:
    if not pattern.holes:
        return [_text(520, 34, "HOLE TABLE: NONE", "table-text")]

    elements = [
        _text(520, 30, "HOLE TABLE", "table-title"),
        _text(520, 48, "ID    X      Y      DIA/SIZE", "table-text"),
    ]
    for index, hole in enumerate(pattern.holes[:6], start=1):
        size_text = f"{hole.diameter:>6.1f}"
        if isinstance(hole, SlotHole):
            size_text = f"{hole.length:.1f}x{hole.width:.1f}"
        face_text = ""
        if hasattr(pattern, "hole_faces"):
            face_text = pattern.hole_faces[index - 1].replace("_flange", "").upper() + " "
        elements.append(
            _text(
                520,
                48 + index * 16,
                f"H{index:<2} {face_text}{hole.x:>6.1f} {hole.y:>6.1f} {size_text}",
                "table-text",
            )
        )
    if len(pattern.holes) > 6:
        elements.append(_text(520, 48 + 7 * 16, f"+ {len(pattern.holes) - 6} MORE", "table-text"))
    return elements


def _legend_elements(y: float) -> list[str]:
    return [
        _line(24, y, 52, y, "cut legend-sample"),
        _text(60, y + 4, "CUT", "legend"),
        _line(118, y, 146, y, "bend legend-sample"),
        _text(154, y + 4, "BEND", "legend"),
        '<circle class="hole legend-sample" cx="238.00" cy="{:.2f}" r="7.00" />'.format(y),
        _text(252, y + 4, "HOLE", "legend"),
    ]


def _slot_path(slot: SlotHole, scale: float, offset_x: float, offset_y: float, flat_length: float) -> str:
    radius = slot.radius * scale
    half_straight = slot.straight_length * scale / 2.0
    cx = offset_x + slot.x * scale
    cy = offset_y + (flat_length - slot.y) * scale
    if slot.orientation == "horizontal":
        left_x = cx - half_straight
        right_x = cx + half_straight
        return (
            f'<path class="hole" d="M {left_x:.2f},{cy - radius:.2f} '
            f'L {right_x:.2f},{cy - radius:.2f} '
            f'A {radius:.2f},{radius:.2f} 0 0 1 {right_x:.2f},{cy + radius:.2f} '
            f'L {left_x:.2f},{cy + radius:.2f} '
            f'A {radius:.2f},{radius:.2f} 0 0 1 {left_x:.2f},{cy - radius:.2f} Z" />'
        )

    bottom_y = cy + half_straight
    top_y = cy - half_straight
    return (
        f'<path class="hole" d="M {cx + radius:.2f},{bottom_y:.2f} '
        f'L {cx + radius:.2f},{top_y:.2f} '
        f'A {radius:.2f},{radius:.2f} 0 0 1 {cx - radius:.2f},{top_y:.2f} '
        f'L {cx - radius:.2f},{bottom_y:.2f} '
        f'A {radius:.2f},{radius:.2f} 0 0 1 {cx + radius:.2f},{bottom_y:.2f} Z" />'
    )


def _hole_bounds(hole: Union[CircularHole, SlotHole], scale: float, offset_x: float, offset_y: float, flat_length: float) -> tuple[float, float, float, float]:
    cx = offset_x + hole.x * scale
    cy = offset_y + (flat_length - hole.y) * scale
    if isinstance(hole, SlotHole):
        half_width = (hole.length if hole.orientation == "horizontal" else hole.width) * scale / 2.0
        half_height = (hole.width if hole.orientation == "horizontal" else hole.length) * scale / 2.0
    else:
        half_width = hole.radius * scale
        half_height = hole.radius * scale
    return cx - half_width, cy - half_height, cx + half_width, cy + half_height


def _hole_label(hole: Union[CircularHole, SlotHole], label: str, scale: float, offset_x: float, offset_y: float, flat_length: float, top_y: float, bottom_y: float) -> str:
    left, top, right, bottom = _hole_bounds(hole, scale, offset_x, offset_y, flat_length)
    label_x = (left + right) / 2.0
    label_y = top - 9.0
    if label_y - 13.0 < top_y:
        label_y = bottom + 19.0
    if label_y + 4.0 > bottom_y:
        label_y = top - 9.0
    return _text(label_x, label_y, label, "hole-label", anchor="middle")


def pattern_to_svg(
    pattern: Pattern,
    visible_layers: Iterable[LayerName] | None = None,
    invalid_hole_indexes: Iterable[int] | None = None,
) -> str:
    """Render a simple non-production SVG preview of a calculated flat pattern."""
    layers = _normalize_visible_layers(visible_layers)
    invalid_holes = set(invalid_hole_indexes or [])
    flat_width = pattern.flat_width
    flat_length = pattern.flat_length
    outline = _scaled_points(pattern.cut_outline, flat_width, flat_length)
    scale, offset_x, offset_y = _preview_transform(flat_width, flat_length)
    top_y = offset_y
    bottom_y = offset_y + flat_length * scale
    left_x = offset_x
    right_x = offset_x + flat_width * scale

    elements = []
    if "CUT" in layers:
        elements.append(f'<polyline class="cut" points="{_point_string(outline)}" />')

    if isinstance(pattern, UBracketFlatPattern):
        if "BEND" in layers:
            bend_positions = ((pattern.left_bend_x, "B1"), (pattern.right_bend_x, "B2"))
            for x_mm, label in bend_positions:
                x = offset_x + x_mm * scale
                elements.append(_line(x, top_y, x, bottom_y, "bend"))
                if "TEXT" in layers:
                    elements.append(_text(x + 7, top_y + 22, label, "bend-label"))
            if "TEXT" in layers:
                elements.extend(_bend_direction_elements(bend_positions, scale, offset_x, top_y))
        if isinstance(pattern, UBracketWithHolesFlatPattern) and "HOLE" in layers:
            for index, hole in enumerate(pattern.holes, start=1):
                cx = offset_x + hole.x * scale
                cy = offset_y + (flat_length - hole.y) * scale
                r = hole.radius * scale
                if isinstance(hole, CircularHole):
                    elements.append(f'<circle class="hole" cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" />')
                else:
                    elements.append(_slot_path(hole, scale, offset_x, offset_y, flat_length))
                if "TEXT" in layers:
                    elements.append(_hole_label(hole, f"H{index}", scale, offset_x, offset_y, flat_length, top_y, bottom_y))
    elif isinstance(pattern, LBracketFlatPattern):
        if "BEND" in layers:
            x = offset_x + pattern.bend_x * scale
            elements.append(_line(x, top_y, x, bottom_y, "bend"))
            if "TEXT" in layers:
                elements.append(_text(x + 7, top_y + 22, "B1", "bend-label"))
                elements.extend(_bend_direction_elements(((pattern.bend_x, "B1"),), scale, offset_x, top_y))
        if isinstance(pattern, LBracketWithHolesFlatPattern) and "HOLE" in layers:
            for index, hole in enumerate(pattern.holes, start=1):
                cx = offset_x + hole.x * scale
                cy = offset_y + (flat_length - hole.y) * scale
                r = hole.radius * scale
                if isinstance(hole, CircularHole):
                    elements.append(f'<circle class="hole" cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" />')
                else:
                    elements.append(_slot_path(hole, scale, offset_x, offset_y, flat_length))
                if "TEXT" in layers:
                    elements.append(_hole_label(hole, f"H{index}", scale, offset_x, offset_y, flat_length, top_y, bottom_y))
    else:
        if "HOLE" in layers:
            for index, hole in enumerate(pattern.holes, start=1):
                cx = offset_x + hole.x * scale
                cy = offset_y + (flat_length - hole.y) * scale
                r = hole.radius * scale
                hole_class = "invalid-hole" if index - 1 in invalid_holes else "hole"
                label_class = "invalid-hole-label" if index - 1 in invalid_holes else "hole-label"
                if isinstance(hole, CircularHole):
                    elements.append(f'<circle class="{hole_class}" cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" />')
                else:
                    slot_svg = _slot_path(hole, scale, offset_x, offset_y, flat_length)
                    elements.append(slot_svg.replace('class="hole"', f'class="{hole_class}"', 1))
                if "TEXT" in layers:
                    elements.append(
                        _hole_label(hole, f"H{index}", scale, offset_x, offset_y, flat_length, top_y, bottom_y).replace(
                            'class="hole-label"',
                            f'class="{label_class}"',
                            1,
                        )
                    )

    title = f"{pattern.part_name} | {flat_width:.2f} x {flat_length:.2f} mm"
    text_elements = []
    if "TEXT" in layers:
        text_elements = [
            _text(24, 30, pattern.part_name),
            *[
                _text(24, 52 + index * 16, line, "meta")
                for index, line in enumerate(_pattern_info_lines(pattern))
            ],
            *_legend_elements(SVG_HEIGHT - 28),
        ]
        text_elements.extend(_dimension_elements(left_x, right_x, top_y, bottom_y, flat_width, flat_length))
        if isinstance(pattern, (FlatPlatePattern, UBracketWithHolesFlatPattern, LBracketWithHolesFlatPattern)):
            text_elements.extend(_hole_table_elements(pattern))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" role="img" aria-label="{escape(title)}">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#374151" />
    </marker>
  </defs>
  <style>
    .bg {{ fill: #f8fafc; }}
    .grid {{ stroke: #e5e7eb; stroke-width: 1; }}
    .cut {{ fill: none; stroke: #dc2626; stroke-width: 3; stroke-linejoin: round; }}
    .bend {{ stroke: #2563eb; stroke-width: 2; stroke-dasharray: 10 8; }}
    .hole {{ fill: none; stroke: #16a34a; stroke-width: 3; }}
    .invalid-hole {{ fill: #ef4444; fill-opacity: 0.22; stroke: #dc2626; stroke-width: 3; stroke-dasharray: 7 5; }}
    .dimension, .extension {{ stroke: #374151; stroke-width: 1.4; }}
    .dimension-arrow {{ fill: #374151; stroke: none; }}
    .fold-arrow {{ stroke: #7c3aed; stroke-width: 2; }}
    .label, .bend-label, .hole-label {{ fill: #111827; font-family: Arial, sans-serif; font-size: 16px; font-weight: 700; }}
    .invalid-hole-label {{ fill: #b91c1c; font-family: Arial, sans-serif; font-size: 16px; font-weight: 700; }}
    .meta {{ fill: #4b5563; font-family: Arial, sans-serif; font-size: 13px; }}
    .dim-label, .bend-note {{ fill: #374151; font-family: Arial, sans-serif; font-size: 12px; font-weight: 700; }}
    .table-title {{ fill: #111827; font-family: Arial, sans-serif; font-size: 13px; font-weight: 700; }}
    .table-text {{ fill: #4b5563; font-family: Arial, sans-serif; font-size: 12px; font-family: monospace; }}
    .legend {{ fill: #111827; font-family: Arial, sans-serif; font-size: 13px; font-weight: 700; }}
    .legend-sample {{ stroke-width: 3; }}
  </style>
  <rect class="bg" x="0" y="0" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="14" />
  <rect class="draw-safe-zone" x="{SVG_PADDING_X:.2f}" y="{DRAWING_TOP:.2f}" width="{SVG_WIDTH - SVG_PADDING_X * 2:.2f}" height="{DRAWING_BOTTOM - DRAWING_TOP:.2f}" fill="none" />
  <line class="grid" x1="{offset_x:.2f}" y1="{top_y:.2f}" x2="{offset_x + flat_width * scale:.2f}" y2="{top_y:.2f}" />
  <line class="grid" x1="{offset_x:.2f}" y1="{bottom_y:.2f}" x2="{offset_x + flat_width * scale:.2f}" y2="{bottom_y:.2f}" />
  {"".join(elements)}
  {"".join(text_elements)}
</svg>"""
