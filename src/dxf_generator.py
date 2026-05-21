"""DXF generation helpers for sheet metal flat patterns."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import ezdxf
from ezdxf.addons import text2path

from sheet_metal_math import (
    CircularHole,
    CornerChamfer,
    CornerRadius,
    EdgeNotch,
    FlatPlateFeature,
    FlatPlatePattern,
    LBracketFlatPattern,
    LBracketWithHolesFlatPattern,
    SlotHole,
    UBracketFlatPattern,
    UBracketWithHolesFlatPattern,
)

TextMode = Literal["standard", "outline"]


def _ensure_layer(doc: ezdxf.document.Drawing, name: str, color: int, linetype: str = "CONTINUOUS") -> None:
    if name not in doc.layers:
        doc.layers.add(name, color=color, linetype=linetype)


def _add_dashed_vertical_line(
    msp: ezdxf.layouts.Modelspace,
    x: float,
    y_start: float,
    y_end: float,
    *,
    dash_length: float = 12.0,
    gap_length: float = 5.0,
) -> None:
    """Draw visible bend dashes as real geometry for CAD import compatibility."""
    y = min(y_start, y_end)
    limit = max(y_start, y_end)
    while y < limit:
        dash_end = min(y + dash_length, limit)
        if dash_end > y:
            msp.add_line(
                (x, y),
                (x, dash_end),
                dxfattribs={"layer": "BEND"},
            )
        y = dash_end + gap_length


def _add_visible_text(
    msp: ezdxf.layouts.Modelspace,
    text: str,
    insert: tuple[float, float],
    *,
    height: float = 5.0,
    text_mode: TextMode = "standard",
) -> None:
    """Add text using either AutoCAD-friendly TEXT or FreeCAD-friendly outlines."""
    text_entity = msp.add_text(
        text,
        dxfattribs={"layer": "TEXT", "height": height},
    )
    text_entity.set_placement(insert)
    if text_mode == "standard":
        return

    for outline in text2path.virtual_entities(text_entity, kind=text2path.Kind.LWPOLYLINES):
        outline.dxf.layer = "TEXT"
        msp.add_entity(outline)
    msp.delete_entity(text_entity)


def _create_dxf_document() -> ezdxf.document.Drawing:
    """Create a DXF document with the MVP layer set."""
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM

    if "DASHED" not in doc.linetypes:
        doc.linetypes.add(
            "DASHED",
            pattern=[0.2, 5.0, -2.5],
            description="Dashed line for bend marks",
        )

    _ensure_layer(doc, "CUT", color=1)
    _ensure_layer(doc, "BEND", color=5, linetype="DASHED")
    _ensure_layer(doc, "HOLE", color=3)
    _ensure_layer(doc, "TEXT", color=7)
    return doc


def _add_cut_outline(msp: ezdxf.layouts.Modelspace, cut_outline: list[tuple[float, float]]) -> None:
    msp.add_lwpolyline(cut_outline, close=True, dxfattribs={"layer": "CUT"})


def _add_holes(
    msp: ezdxf.layouts.Modelspace,
    pattern: FlatPlatePattern | UBracketWithHolesFlatPattern | LBracketWithHolesFlatPattern,
) -> None:
    for hole in pattern.holes:
        if isinstance(hole, CircularHole):
            msp.add_circle(
                (hole.x, hole.y),
                hole.radius,
                dxfattribs={"layer": "HOLE"},
            )
        else:
            _add_slot_hole(msp, hole)


def _add_slot_hole(msp: ezdxf.layouts.Modelspace, slot: SlotHole) -> None:
    radius = slot.radius
    half_straight = slot.straight_length / 2.0
    if slot.orientation == "horizontal":
        left_center = (slot.x - half_straight, slot.y)
        right_center = (slot.x + half_straight, slot.y)
        msp.add_line((left_center[0], slot.y + radius), (right_center[0], slot.y + radius), dxfattribs={"layer": "HOLE"})
        msp.add_line((right_center[0], slot.y - radius), (left_center[0], slot.y - radius), dxfattribs={"layer": "HOLE"})
        msp.add_arc(right_center, radius, 270.0, 90.0, dxfattribs={"layer": "HOLE"})
        msp.add_arc(left_center, radius, 90.0, 270.0, dxfattribs={"layer": "HOLE"})
        return

    bottom_center = (slot.x, slot.y - half_straight)
    top_center = (slot.x, slot.y + half_straight)
    msp.add_line((slot.x + radius, bottom_center[1]), (slot.x + radius, top_center[1]), dxfattribs={"layer": "HOLE"})
    msp.add_line((slot.x - radius, top_center[1]), (slot.x - radius, bottom_center[1]), dxfattribs={"layer": "HOLE"})
    msp.add_arc(top_center, radius, 0.0, 180.0, dxfattribs={"layer": "HOLE"})
    msp.add_arc(bottom_center, radius, 180.0, 360.0, dxfattribs={"layer": "HOLE"})


def _summarize_holes(pattern: FlatPlatePattern | UBracketWithHolesFlatPattern | LBracketWithHolesFlatPattern) -> str:
    if not pattern.holes:
        return "HOLES: NONE"
    circular_holes = [hole for hole in pattern.holes if isinstance(hole, CircularHole)]
    slot_holes = [hole for hole in pattern.holes if isinstance(hole, SlotHole)]
    if circular_holes and not slot_holes:
        diameters = sorted({round(hole.diameter, 3) for hole in circular_holes})
        if len(diameters) == 1:
            return f"HOLES: {len(pattern.holes)}x DIA {diameters[0]:.2f} mm"
    if slot_holes and not circular_holes:
        return f"HOLES: {len(slot_holes)} SLOT, SEE HOLE LABELS"
    return f"HOLES: {len(pattern.holes)} TOTAL, SEE HOLE LABELS"


def _summarize_features(features: list[FlatPlateFeature]) -> str:
    if not features:
        return "FEATURES: NONE"
    chamfer_count = sum(1 for feature in features if isinstance(feature, CornerChamfer))
    radius_count = sum(1 for feature in features if isinstance(feature, CornerRadius))
    notch_count = sum(1 for feature in features if isinstance(feature, EdgeNotch))
    parts = []
    if chamfer_count:
        parts.append(f"{chamfer_count} CHAMFER")
    if radius_count:
        parts.append(f"{radius_count} ROUND CORNER")
    if notch_count:
        parts.append(f"{notch_count} EDGE NOTCH")
    return "FEATURES: " + ", ".join(parts)


def _add_hole_labels(
    msp: ezdxf.layouts.Modelspace,
    pattern: FlatPlatePattern | UBracketWithHolesFlatPattern | LBracketWithHolesFlatPattern,
    *,
    text_mode: TextMode,
) -> None:
    for index, hole in enumerate(pattern.holes, start=1):
        face_prefix = ""
        if hasattr(pattern, "hole_faces"):
            face_prefix = pattern.hole_faces[index - 1].upper().replace("_FLANGE", "") + " "
        if isinstance(hole, SlotHole):
            label = f"H{index} {face_prefix}SLOT {hole.length:.2f}x{hole.width:.2f}"
        else:
            label = f"H{index} {face_prefix}DIA {hole.diameter:.2f}"
        label_x = min(hole.x + hole.radius + 3.0, pattern.flat_width - 35.0)
        label_y = min(hole.y + hole.radius + 3.0, pattern.flat_length - 8.0)
        _add_visible_text(
            msp,
            label,
            (max(label_x, 0.0), max(label_y, 0.0)),
            height=3.0,
            text_mode=text_mode,
        )


def _add_info_text(
    msp: ezdxf.layouts.Modelspace,
    text_lines: list[str],
    *,
    text_x: float,
    text_y: float,
    height: float = 5.0,
    line_spacing: float = 9.0,
    text_mode: TextMode = "standard",
) -> None:
    for index, text in enumerate(text_lines):
        _add_visible_text(
            msp,
            text,
            (text_x, text_y - index * line_spacing),
            height=height,
            text_mode=text_mode,
        )


def generate_u_bracket_dxf(pattern: UBracketFlatPattern, output_path: Path, *, text_mode: TextMode = "standard") -> Path:
    """Generate a U-bracket DXF flat pattern with CUT, BEND, and TEXT layers."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = _create_dxf_document()

    msp = doc.modelspace()
    _add_cut_outline(msp, pattern.cut_outline)
    if isinstance(pattern, UBracketWithHolesFlatPattern):
        _add_holes(msp, pattern)
        _add_hole_labels(msp, pattern, text_mode=text_mode)

    for bend_x in (pattern.left_bend_x, pattern.right_bend_x):
        _add_dashed_vertical_line(
            msp,
            bend_x,
            0.0,
            pattern.flat_length,
        )

    text_lines = [
        f"PART: {pattern.part_name}",
        f"MATERIAL: {pattern.material}",
        f"THICKNESS: {pattern.thickness:.2f} mm",
        f"FLAT SIZE: {pattern.flat_width:.2f} x {pattern.flat_length:.2f} mm",
        f"BEND ALLOWANCE: {pattern.bend_allowance:.3f} mm",
    ]
    if isinstance(pattern, UBracketWithHolesFlatPattern):
        text_lines.extend(
            [
                "TYPE: U_BRACKET_WITH_HOLES",
                "HOLE ORIGIN: FACE LOCAL, UNFOLDED TO FLAT",
                _summarize_holes(pattern),
                f"MIN HOLE-BEND EDGE: {pattern.min_hole_to_bend_distance:.2f} mm",
            ]
        )
    text_x = 0.0
    text_y = pattern.flat_length + 12.0 + (len(text_lines) - 1) * 9.0
    _add_info_text(msp, text_lines, text_x=text_x, text_y=text_y, text_mode=text_mode)

    doc.saveas(output_path)
    return output_path


def generate_l_bracket_dxf(pattern: LBracketFlatPattern, output_path: Path, *, text_mode: TextMode = "standard") -> Path:
    """Generate an L-bracket DXF flat pattern with CUT, BEND, and TEXT layers."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = _create_dxf_document()

    msp = doc.modelspace()
    _add_cut_outline(msp, pattern.cut_outline)
    if isinstance(pattern, LBracketWithHolesFlatPattern):
        _add_holes(msp, pattern)
        _add_hole_labels(msp, pattern, text_mode=text_mode)

    _add_dashed_vertical_line(
        msp,
        pattern.bend_x,
        0.0,
        pattern.flat_length,
    )

    part_type_text = "TYPE: L_BRACKET_WITH_HOLES" if isinstance(pattern, LBracketWithHolesFlatPattern) else "TYPE: L_BRACKET"
    text_lines = [
        f"PART: {pattern.part_name}",
        part_type_text,
        f"MATERIAL: {pattern.material}",
        f"THICKNESS: {pattern.thickness:.2f} mm",
        f"FLAT SIZE: {pattern.flat_width:.2f} x {pattern.flat_length:.2f} mm",
        f"BEND ALLOWANCE: {pattern.bend_allowance:.3f} mm",
    ]
    if isinstance(pattern, LBracketWithHolesFlatPattern):
        text_lines.extend(
            [
                "HOLE ORIGIN: FACE LOCAL, UNFOLDED TO FLAT",
                _summarize_holes(pattern),
                f"MIN HOLE-BEND EDGE: {pattern.min_hole_to_bend_distance:.2f} mm",
            ]
        )
    text_x = 0.0
    text_y = pattern.flat_length + 12.0 + (len(text_lines) - 1) * 9.0
    _add_info_text(msp, text_lines, text_x=text_x, text_y=text_y, text_mode=text_mode)

    doc.saveas(output_path)
    return output_path


def generate_flat_plate_dxf(pattern: FlatPlatePattern, output_path: Path, *, text_mode: TextMode = "standard") -> Path:
    """Generate a flat plate DXF with CUT, HOLE, and TEXT layers."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = _create_dxf_document()

    msp = doc.modelspace()
    _add_cut_outline(msp, pattern.cut_outline)
    _add_holes(msp, pattern)
    _add_hole_labels(msp, pattern, text_mode=text_mode)

    text_lines = [
        f"PART: {pattern.part_name}",
        "TYPE: FLAT_PLATE",
        f"MATERIAL: {pattern.material}",
        f"THICKNESS: {pattern.thickness:.2f} mm",
        f"FLAT SIZE: {pattern.flat_width:.2f} x {pattern.flat_length:.2f} mm",
        "HOLE ORIGIN: LOWER LEFT CORNER",
        _summarize_holes(pattern),
        _summarize_features(pattern.features),
    ]
    text_x = 0.0
    text_y = pattern.flat_length + 12.0 + (len(text_lines) - 1) * 9.0
    _add_info_text(msp, text_lines, text_x=text_x, text_y=text_y, text_mode=text_mode)

    doc.saveas(output_path)
    return output_path
