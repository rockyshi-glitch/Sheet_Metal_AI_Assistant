"""Command-line entry point for the sheet metal DXF MVP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from generation import generate_dxf_from_data, generate_svg_preview_from_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "examples" / "u_bracket_sample.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a sheet metal DXF from JSON parameters.")
    parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        help="Optional positional path to the sheet metal JSON parameter file.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        dest="input_option",
        help="Path to the sheet metal JSON parameter file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where the generated DXF will be saved.",
    )
    parser.add_argument(
        "--text-mode",
        choices=("standard", "outline"),
        default="standard",
        help="Use 'standard' TEXT for AutoCAD or outline text geometry for FreeCAD inspection.",
    )
    parser.add_argument(
        "--file-suffix",
        default="",
        help="Optional suffix appended to the generated DXF file name before .dxf.",
    )
    parser.add_argument(
        "--preview-svg",
        action="store_true",
        help="Also generate a browser-friendly SVG inspection preview.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input_option or args.input_path or DEFAULT_INPUT
    try:
        with input_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except OSError as exc:
        print(f"Input error: could not read {input_path}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except json.JSONDecodeError as exc:
        print(f"Input error: {input_path} is not valid JSON: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    try:
        result = generate_dxf_from_data(
            data,
            args.output_dir,
            text_mode=args.text_mode,
            file_suffix=args.file_suffix,
        )
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Generated DXF: {result.output_path}")
    print(f"Part type: {result.part_type}")
    print(f"Text mode: {args.text_mode}")
    print(f"Flat size: {result.pattern.flat_width:.2f} x {result.pattern.flat_length:.2f} mm")
    if hasattr(result.pattern, "bend_allowance"):
        print(f"Bend allowance: {result.pattern.bend_allowance:.3f} mm")
    if hasattr(result.pattern, "holes"):
        print(f"Holes: {len(result.pattern.holes)}")
    if args.preview_svg:
        preview = generate_svg_preview_from_data(data, args.output_dir)
        print(f"Generated SVG preview: {preview.output_path}")


if __name__ == "__main__":
    main()
