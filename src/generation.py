"""Shared DXF generation workflow for CLI and Streamlit entry points."""

from __future__ import annotations

import json
import re
import tempfile
from io import BytesIO
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from dxf_generator import TextMode, generate_flat_plate_dxf, generate_l_bracket_dxf, generate_u_bracket_dxf
from sheet_metal_math import (
    FlatPlateParams,
    FlatPlatePattern,
    LBracketFlatPattern,
    LBracketParams,
    LBracketWithHolesFlatPattern,
    LBracketWithHolesParams,
    UBracketFlatPattern,
    UBracketParams,
    UBracketWithHolesFlatPattern,
    UBracketWithHolesParams,
    calculate_flat_plate_pattern,
    calculate_l_bracket_flat_pattern,
    calculate_l_bracket_with_holes_flat_pattern,
    calculate_u_bracket_flat_pattern,
    calculate_u_bracket_with_holes_flat_pattern,
)
from svg_preview import pattern_to_svg


@dataclass(frozen=True)
class GenerationResult:
    part_type: str
    output_path: Path
    pattern: UBracketFlatPattern | UBracketWithHolesFlatPattern | LBracketFlatPattern | LBracketWithHolesFlatPattern | FlatPlatePattern


@dataclass(frozen=True)
class PreviewResult:
    part_type: str
    output_path: Path
    pattern: UBracketFlatPattern | UBracketWithHolesFlatPattern | LBracketFlatPattern | LBracketWithHolesFlatPattern | FlatPlatePattern


@dataclass(frozen=True)
class DeliveryPackageResult:
    part_type: str
    package_name: str
    package_bytes: bytes
    files: tuple[str, ...]
    pattern: UBracketFlatPattern | UBracketWithHolesFlatPattern | LBracketFlatPattern | LBracketWithHolesFlatPattern | FlatPlatePattern


@dataclass(frozen=True)
class PatternResult:
    part_type: str
    pattern: UBracketFlatPattern | UBracketWithHolesFlatPattern | LBracketFlatPattern | LBracketWithHolesFlatPattern | FlatPlatePattern


def normalize_part_type(data: dict) -> str:
    return str(data.get("part_type", "u_bracket")).strip().lower()


def _safe_file_stem(part_name: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(part_name).strip()).strip("._")
    return safe_name or "sheet_metal_part"


def _generator_for_part_type(part_type: str):
    if part_type in {"u_bracket", "u_bracket_with_holes"}:
        return generate_u_bracket_dxf
    if part_type in {"l_bracket", "l_bracket_with_holes"}:
        return generate_l_bracket_dxf
    return generate_flat_plate_dxf


def calculate_pattern_from_data(data: dict) -> PatternResult:
    """Validate JSON-like parameters and calculate the flat pattern without writing files."""
    part_type = normalize_part_type(data)
    if part_type == "u_bracket":
        params = UBracketParams.from_dict(data)
        pattern = calculate_u_bracket_flat_pattern(params)
    elif part_type == "u_bracket_with_holes":
        params = UBracketWithHolesParams.from_dict(data)
        pattern = calculate_u_bracket_with_holes_flat_pattern(params)
    elif part_type == "l_bracket":
        params = LBracketParams.from_dict(data)
        pattern = calculate_l_bracket_flat_pattern(params)
    elif part_type == "l_bracket_with_holes":
        params = LBracketWithHolesParams.from_dict(data)
        pattern = calculate_l_bracket_with_holes_flat_pattern(params)
    elif part_type == "flat_plate":
        params = FlatPlateParams.from_dict(data)
        pattern = calculate_flat_plate_pattern(params)
    else:
        raise ValueError(
            "part_type must be 'u_bracket', 'u_bracket_with_holes', 'l_bracket', "
            "'l_bracket_with_holes', or 'flat_plate'."
        )

    return PatternResult(part_type=part_type, pattern=pattern)


def generate_dxf_from_data(
    data: dict,
    output_dir: Path,
    *,
    text_mode: TextMode = "standard",
    file_suffix: str = "",
) -> GenerationResult:
    """Validate JSON-like parameters, calculate the flat pattern, and write a DXF."""
    result = calculate_pattern_from_data(data)
    pattern = result.pattern
    generator = _generator_for_part_type(result.part_type)

    output_path = output_dir / f"{pattern.part_name}{file_suffix}.dxf"
    generator(pattern, output_path, text_mode=text_mode)
    return GenerationResult(part_type=result.part_type, output_path=output_path, pattern=pattern)


def generate_svg_preview_from_data(
    data: dict,
    output_dir: Path,
    *,
    visible_layers: set[str] | None = None,
    file_suffix: str = "_preview",
) -> PreviewResult:
    """Validate JSON-like parameters, calculate the flat pattern, and write an SVG preview."""
    result = calculate_pattern_from_data(data)
    output_path = output_dir / f"{result.pattern.part_name}{file_suffix}.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(pattern_to_svg(result.pattern, visible_layers=visible_layers), encoding="utf-8")
    return PreviewResult(part_type=result.part_type, output_path=output_path, pattern=result.pattern)


def generate_delivery_package_from_data(data: dict) -> DeliveryPackageResult:
    """Build a ZIP package with editable DXF, browser SVG preview, and source JSON parameters."""
    result = calculate_pattern_from_data(data)
    pattern = result.pattern
    file_stem = _safe_file_stem(pattern.part_name)
    dxf_name = f"{file_stem}.dxf"
    svg_name = f"{file_stem}_preview.svg"
    json_name = f"{file_stem}_parameters.json"
    package_name = f"{file_stem}_delivery_package.zip"

    with tempfile.TemporaryDirectory() as temp_dir:
        dxf_path = Path(temp_dir) / dxf_name
        _generator_for_part_type(result.part_type)(pattern, dxf_path, text_mode="standard")
        dxf_bytes = dxf_path.read_bytes()

    svg = pattern_to_svg(pattern).encode("utf-8")
    parameters_json = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

    package_buffer = BytesIO()
    with ZipFile(package_buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(dxf_name, dxf_bytes)
        archive.writestr(svg_name, svg)
        archive.writestr(json_name, parameters_json)

    return DeliveryPackageResult(
        part_type=result.part_type,
        package_name=package_name,
        package_bytes=package_buffer.getvalue(),
        files=(dxf_name, svg_name, json_name),
        pattern=pattern,
    )
