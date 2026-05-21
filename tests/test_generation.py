"""Tests for the shared DXF generation workflow."""

from __future__ import annotations

import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from generation import (  # noqa: E402
    calculate_pattern_from_data,
    generate_delivery_package_from_data,
    generate_dxf_from_data,
    generate_svg_preview_from_data,
)


class GenerationWorkflowTest(unittest.TestCase):
    def test_calculates_pattern_without_writing_dxf(self) -> None:
        data = {
            "part_type": "l_bracket",
            "part_name": "L_BRACKET_PREVIEW_TEST",
            "material": "Aluminium 5052",
            "thickness": 2.0,
            "inside_bend_radius": 2.0,
            "k_factor": 0.38,
            "part_length": 200.0,
            "base_width": 100.0,
            "flange_height": 40.0,
            "bend_angle": 90.0,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            result = calculate_pattern_from_data(data)

            self.assertEqual(result.part_type, "l_bracket")
            self.assertAlmostEqual(result.pattern.flat_width, 144.3353978619539, places=6)
            self.assertEqual(list(Path(temp_dir).glob("*.dxf")), [])

    def test_generates_u_bracket_dxf_from_parameter_dict(self) -> None:
        data = {
            "part_type": "u_bracket",
            "part_name": "U_BRACKET_WORKFLOW_TEST",
            "material": "Aluminium 5052",
            "thickness": 2.0,
            "inside_bend_radius": 2.0,
            "k_factor": 0.38,
            "part_length": 200.0,
            "bottom_width": 100.0,
            "left_flange_height": 40.0,
            "right_flange_height": 40.0,
            "bend_angle": 90.0,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_dxf_from_data(data, Path(temp_dir))

            self.assertEqual(result.part_type, "u_bracket")
            self.assertTrue(result.output_path.exists())
            self.assertEqual(result.output_path.name, "U_BRACKET_WORKFLOW_TEST.dxf")
            self.assertAlmostEqual(result.pattern.flat_width, 188.67079572390783, places=6)

    def test_generates_u_bracket_with_holes_dxf_from_parameter_dict(self) -> None:
        data = {
            "part_type": "u_bracket_with_holes",
            "part_name": "U_BRACKET_HOLES_WORKFLOW_TEST",
            "material": "Aluminium 5052",
            "thickness": 2.0,
            "inside_bend_radius": 2.0,
            "k_factor": 0.38,
            "part_length": 200.0,
            "bottom_width": 100.0,
            "left_flange_height": 40.0,
            "right_flange_height": 40.0,
            "bend_angle": 90.0,
            "min_hole_to_bend_distance": 8.0,
            "holes": [{"face": "bottom", "x": 50.0, "y": 60.0, "diameter": 12.0}],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_dxf_from_data(data, Path(temp_dir))

            self.assertEqual(result.part_type, "u_bracket_with_holes")
            self.assertTrue(result.output_path.exists())
            self.assertEqual(result.output_path.name, "U_BRACKET_HOLES_WORKFLOW_TEST.dxf")
            self.assertEqual(len(result.pattern.holes), 1)

    def test_generates_l_bracket_with_holes_dxf_from_parameter_dict(self) -> None:
        data = {
            "part_type": "l_bracket_with_holes",
            "part_name": "L_BRACKET_HOLES_WORKFLOW_TEST",
            "material": "Aluminium 5052",
            "thickness": 2.0,
            "inside_bend_radius": 2.0,
            "k_factor": 0.38,
            "part_length": 200.0,
            "base_width": 100.0,
            "flange_height": 40.0,
            "bend_angle": 90.0,
            "min_hole_to_bend_distance": 8.0,
            "holes": [{"face": "base", "x": 50.0, "y": 60.0, "diameter": 12.0}],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_dxf_from_data(data, Path(temp_dir))

            self.assertEqual(result.part_type, "l_bracket_with_holes")
            self.assertTrue(result.output_path.exists())
            self.assertEqual(result.output_path.name, "L_BRACKET_HOLES_WORKFLOW_TEST.dxf")
            self.assertEqual(len(result.pattern.holes), 1)

    def test_rejects_unknown_part_type_before_writing_dxf(self) -> None:
        data = {"part_type": "unknown", "part_name": "SHOULD_NOT_WRITE"}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            with self.assertRaisesRegex(ValueError, "part_type must be"):
                generate_dxf_from_data(data, output_dir)

            self.assertEqual(list(output_dir.glob("*.dxf")), [])

    def test_generates_svg_preview_from_parameter_dict(self) -> None:
        data = {
            "part_type": "flat_plate",
            "part_name": "FLAT_PREVIEW_WORKFLOW_TEST",
            "material": "Aluminium 5052",
            "thickness": 2.0,
            "plate_width": 160.0,
            "plate_length": 100.0,
            "holes": [{"x": 30.0, "y": 30.0, "diameter": 10.0}],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_svg_preview_from_data(data, Path(temp_dir), visible_layers={"CUT", "HOLE", "TEXT"})

            self.assertEqual(result.part_type, "flat_plate")
            self.assertEqual(result.output_path.name, "FLAT_PREVIEW_WORKFLOW_TEST_preview.svg")
            self.assertTrue(result.output_path.exists())
            svg = result.output_path.read_text(encoding="utf-8")
            self.assertIn("<svg", svg)
            self.assertIn("FLAT_PREVIEW_WORKFLOW_TEST", svg)
            self.assertIn("HOLES: 1", svg)

    def test_generates_delivery_package_with_dxf_svg_and_json(self) -> None:
        data = {
            "part_type": "l_bracket",
            "part_name": "L BRACKET PACKAGE TEST",
            "material": "Aluminium 5052",
            "thickness": 2.0,
            "inside_bend_radius": 2.0,
            "k_factor": 0.38,
            "part_length": 200.0,
            "base_width": 100.0,
            "flange_height": 40.0,
            "bend_angle": 90.0,
        }

        package = generate_delivery_package_from_data(data)

        self.assertEqual(package.part_type, "l_bracket")
        self.assertEqual(package.package_name, "L_BRACKET_PACKAGE_TEST_delivery_package.zip")
        self.assertEqual(
            package.files,
            (
                "L_BRACKET_PACKAGE_TEST.dxf",
                "L_BRACKET_PACKAGE_TEST_preview.svg",
                "L_BRACKET_PACKAGE_TEST_parameters.json",
            ),
        )
        with ZipFile(BytesIO(package.package_bytes)) as archive:
            self.assertEqual(set(archive.namelist()), set(package.files))
            self.assertTrue(archive.read("L_BRACKET_PACKAGE_TEST.dxf").startswith(b"  0"))
            self.assertIn(b"<svg", archive.read("L_BRACKET_PACKAGE_TEST_preview.svg"))
            self.assertIn(b'"part_type": "l_bracket"', archive.read("L_BRACKET_PACKAGE_TEST_parameters.json"))


if __name__ == "__main__":
    unittest.main()
