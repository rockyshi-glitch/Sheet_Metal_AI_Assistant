"""Tests for DXF output compatibility details."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import ezdxf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dxf_generator import generate_flat_plate_dxf, generate_l_bracket_dxf, generate_u_bracket_dxf  # noqa: E402
from sheet_metal_math import (  # noqa: E402
    FlatPlateParams,
    LBracketParams,
    LBracketWithHolesParams,
    UBracketParams,
    UBracketWithHolesParams,
    calculate_flat_plate_pattern,
    calculate_l_bracket_flat_pattern,
    calculate_l_bracket_with_holes_flat_pattern,
    calculate_u_bracket_flat_pattern,
    calculate_u_bracket_with_holes_flat_pattern,
)


class DxfGeneratorTest(unittest.TestCase):
    def test_generates_autocad_friendly_bend_and_text_entities(self) -> None:
        params = UBracketParams(
            part_name="U_BRACKET_TEST",
            material="Aluminium 5052",
            thickness=2.0,
            inside_bend_radius=2.0,
            k_factor=0.38,
            part_length=200.0,
            bottom_width=100.0,
            left_flange_height=40.0,
            right_flange_height=40.0,
            bend_angle=90.0,
        )
        pattern = calculate_u_bracket_flat_pattern(params)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "U_BRACKET_TEST.dxf"
            generate_u_bracket_dxf(pattern, output_path)

            doc = ezdxf.readfile(output_path)
            layers = {layer.dxf.name for layer in doc.layers}
            self.assertTrue({"CUT", "BEND", "TEXT"}.issubset(layers))

            entities = list(doc.modelspace())
            bend_lines = [entity for entity in entities if entity.dxf.layer == "BEND" and entity.dxftype() == "LINE"]
            text_entities = [entity for entity in entities if entity.dxf.layer == "TEXT" and entity.dxftype() == "TEXT"]
            text_outlines = [
                entity for entity in entities if entity.dxf.layer == "TEXT" and entity.dxftype() == "LWPOLYLINE"
            ]
            text_values = [entity.dxf.text for entity in text_entities]
            text_y_positions = [entity.dxf.insert.y for entity in text_entities]

            self.assertGreater(len(bend_lines), 2)
            self.assertEqual(len(text_entities), 5)
            self.assertEqual(len(text_outlines), 0)
            self.assertEqual(text_values[0], "PART: U_BRACKET_TEST")
            self.assertGreater(text_y_positions[0], text_y_positions[-1])

    def test_generates_freecad_outline_text_without_standard_text(self) -> None:
        params = UBracketParams(
            part_name="U_BRACKET_FREECAD_TEST",
            material="Aluminium 5052",
            thickness=2.0,
            inside_bend_radius=2.0,
            k_factor=0.38,
            part_length=200.0,
            bottom_width=100.0,
            left_flange_height=40.0,
            right_flange_height=40.0,
            bend_angle=90.0,
        )
        pattern = calculate_u_bracket_flat_pattern(params)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "U_BRACKET_FREECAD_TEST.dxf"
            generate_u_bracket_dxf(pattern, output_path, text_mode="outline")

            doc = ezdxf.readfile(output_path)
            entities = list(doc.modelspace())
            text_entities = [entity for entity in entities if entity.dxf.layer == "TEXT" and entity.dxftype() == "TEXT"]
            text_outlines = [
                entity for entity in entities if entity.dxf.layer == "TEXT" and entity.dxftype() == "LWPOLYLINE"
            ]

            self.assertEqual(len(text_entities), 0)
            self.assertGreater(len(text_outlines), 0)

    def test_generates_u_bracket_with_holes_dxf(self) -> None:
        params = UBracketWithHolesParams.from_dict(
            {
                "part_type": "u_bracket_with_holes",
                "part_name": "U_BRACKET_HOLES_TEST",
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
                "holes": [
                    {"face": "bottom", "x": 50.0, "y": 60.0, "diameter": 12.0},
                    {"face": "left_flange", "x": 18.0, "y": 100.0, "diameter": 8.0},
                ],
            }
        )
        pattern = calculate_u_bracket_with_holes_flat_pattern(params)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "U_BRACKET_HOLES_TEST.dxf"
            generate_u_bracket_dxf(pattern, output_path)

            doc = ezdxf.readfile(output_path)
            entities = list(doc.modelspace())
            layers = {layer.dxf.name for layer in doc.layers}
            holes = [entity for entity in entities if entity.dxf.layer == "HOLE" and entity.dxftype() == "CIRCLE"]
            bend_lines = [entity for entity in entities if entity.dxf.layer == "BEND" and entity.dxftype() == "LINE"]
            text_values = {
                entity.dxf.text
                for entity in entities
                if entity.dxf.layer == "TEXT" and entity.dxftype() == "TEXT"
            }

            self.assertTrue({"CUT", "BEND", "HOLE", "TEXT"}.issubset(layers))
            self.assertEqual(len(holes), 2)
            self.assertGreater(len(bend_lines), 2)
            self.assertIn("TYPE: U_BRACKET_WITH_HOLES", text_values)
            self.assertIn("HOLES: 2 TOTAL, SEE HOLE LABELS", text_values)
            self.assertIn("H1 BOTTOM DIA 12.00", text_values)
            self.assertIn("H2 LEFT DIA 8.00", text_values)

    def test_generates_l_bracket_dxf_with_single_bend_and_visible_text(self) -> None:
        params = LBracketParams(
            part_name="L_BRACKET_TEST",
            material="Aluminium 5052",
            thickness=2.0,
            inside_bend_radius=2.0,
            k_factor=0.38,
            part_length=200.0,
            base_width=100.0,
            flange_height=40.0,
            bend_angle=90.0,
        )
        pattern = calculate_l_bracket_flat_pattern(params)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "L_BRACKET_TEST.dxf"
            generate_l_bracket_dxf(pattern, output_path)

            doc = ezdxf.readfile(output_path)
            layers = {layer.dxf.name for layer in doc.layers}
            self.assertTrue({"CUT", "BEND", "TEXT"}.issubset(layers))

            entities = list(doc.modelspace())
            cut_outlines = [entity for entity in entities if entity.dxf.layer == "CUT" and entity.dxftype() == "LWPOLYLINE"]
            bend_lines = [entity for entity in entities if entity.dxf.layer == "BEND" and entity.dxftype() == "LINE"]
            text_entities = [entity for entity in entities if entity.dxf.layer == "TEXT" and entity.dxftype() == "TEXT"]
            text_outlines = [
                entity for entity in entities if entity.dxf.layer == "TEXT" and entity.dxftype() == "LWPOLYLINE"
            ]

            self.assertEqual(len(cut_outlines), 1)
            self.assertGreater(len(bend_lines), 2)
            self.assertEqual(len(text_entities), 6)
            self.assertEqual(len(text_outlines), 0)

    def test_generates_l_bracket_with_holes_dxf(self) -> None:
        params = LBracketWithHolesParams.from_dict(
            {
                "part_type": "l_bracket_with_holes",
                "part_name": "L_BRACKET_HOLES_TEST",
                "material": "Aluminium 5052",
                "thickness": 2.0,
                "inside_bend_radius": 2.0,
                "k_factor": 0.38,
                "part_length": 200.0,
                "base_width": 100.0,
                "flange_height": 40.0,
                "bend_angle": 90.0,
                "min_hole_to_bend_distance": 8.0,
                "holes": [
                    {"face": "base", "x": 50.0, "y": 60.0, "diameter": 12.0},
                    {"face": "flange", "x": 18.0, "y": 100.0, "diameter": 8.0},
                ],
            }
        )
        pattern = calculate_l_bracket_with_holes_flat_pattern(params)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "L_BRACKET_HOLES_TEST.dxf"
            generate_l_bracket_dxf(pattern, output_path)

            doc = ezdxf.readfile(output_path)
            entities = list(doc.modelspace())
            layers = {layer.dxf.name for layer in doc.layers}
            holes = [entity for entity in entities if entity.dxf.layer == "HOLE" and entity.dxftype() == "CIRCLE"]
            bend_lines = [entity for entity in entities if entity.dxf.layer == "BEND" and entity.dxftype() == "LINE"]
            text_values = {
                entity.dxf.text
                for entity in entities
                if entity.dxf.layer == "TEXT" and entity.dxftype() == "TEXT"
            }

            self.assertTrue({"CUT", "BEND", "HOLE", "TEXT"}.issubset(layers))
            self.assertEqual(len(holes), 2)
            self.assertGreater(len(bend_lines), 2)
            self.assertIn("TYPE: L_BRACKET_WITH_HOLES", text_values)
            self.assertIn("HOLES: 2 TOTAL, SEE HOLE LABELS", text_values)
            self.assertIn("H1 BASE DIA 12.00", text_values)
            self.assertIn("H2 FLANGE DIA 8.00", text_values)

    def test_generates_flat_plate_dxf_with_hole_layer(self) -> None:
        params = FlatPlateParams.from_dict(
            {
                "part_type": "flat_plate",
                "part_name": "FLAT_PLATE_TEST",
                "material": "Aluminium 5052",
                "thickness": 2.0,
                "plate_width": 160.0,
                "plate_length": 100.0,
                "holes": [
                    {"x": 30.0, "y": 30.0, "diameter": 10.0},
                    {"x": 130.0, "y": 30.0, "diameter": 10.0},
                    {"x": 30.0, "y": 70.0, "diameter": 10.0},
                    {"x": 130.0, "y": 70.0, "diameter": 10.0},
                ],
            }
        )
        pattern = calculate_flat_plate_pattern(params)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "FLAT_PLATE_TEST.dxf"
            generate_flat_plate_dxf(pattern, output_path)

            doc = ezdxf.readfile(output_path)
            layers = {layer.dxf.name for layer in doc.layers}
            self.assertTrue({"CUT", "HOLE", "TEXT"}.issubset(layers))

            entities = list(doc.modelspace())
            cut_outlines = [entity for entity in entities if entity.dxf.layer == "CUT" and entity.dxftype() == "LWPOLYLINE"]
            holes = [entity for entity in entities if entity.dxf.layer == "HOLE" and entity.dxftype() == "CIRCLE"]
            text_entities = [entity for entity in entities if entity.dxf.layer == "TEXT" and entity.dxftype() == "TEXT"]
            text_outlines = [
                entity for entity in entities if entity.dxf.layer == "TEXT" and entity.dxftype() == "LWPOLYLINE"
            ]
            text_values = {entity.dxf.text for entity in text_entities}

            self.assertEqual(len(cut_outlines), 1)
            self.assertEqual(len(holes), 4)
            self.assertEqual(len(text_entities), 12)
            self.assertIn("HOLE ORIGIN: LOWER LEFT CORNER", text_values)
            self.assertIn("HOLES: 4x DIA 10.00 mm", text_values)
            self.assertIn("FEATURES: NONE", text_values)
            self.assertIn("H1 DIA 10.00", text_values)
            self.assertIn("H4 DIA 10.00", text_values)
            self.assertEqual(len(text_outlines), 0)

    def test_generates_flat_plate_dxf_with_featured_cut_outline(self) -> None:
        params = FlatPlateParams.from_dict(
            {
                "part_type": "flat_plate",
                "part_name": "FLAT_PLATE_FEATURE_TEST",
                "material": "Aluminium 5052",
                "thickness": 2.0,
                "plate_width": 120.0,
                "plate_length": 80.0,
                "holes": [],
                "features": [
                    {"type": "corner_chamfer", "corner": "lower_left", "distance": 10.0},
                    {"type": "corner_radius", "corner": "lower_right", "radius": 8.0},
                    {"type": "corner_chamfer", "corner": "upper_right", "distance": 12.0},
                    {"type": "edge_notch", "side": "bottom", "offset": 40.0, "width": 20.0, "depth": 8.0},
                ],
            }
        )
        pattern = calculate_flat_plate_pattern(params)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "FLAT_PLATE_FEATURE_TEST.dxf"
            generate_flat_plate_dxf(pattern, output_path)

            doc = ezdxf.readfile(output_path)
            entities = list(doc.modelspace())
            cut_outline = [
                entity for entity in entities if entity.dxf.layer == "CUT" and entity.dxftype() == "LWPOLYLINE"
            ][0]
            outline_points = [(round(point[0], 3), round(point[1], 3)) for point in cut_outline.get_points()]
            text_values = {
                entity.dxf.text
                for entity in entities
                if entity.dxf.layer == "TEXT" and entity.dxftype() == "TEXT"
            }

            self.assertIn((40.0, 8.0), outline_points)
            self.assertIn((120.0, 8.0), outline_points)
            self.assertIn((108.0, 80.0), outline_points)
            self.assertIn("FEATURES: 2 CHAMFER, 1 ROUND CORNER, 1 EDGE NOTCH", text_values)

    def test_generates_flat_plate_dxf_with_slot_hole_geometry(self) -> None:
        params = FlatPlateParams.from_dict(
            {
                "part_type": "flat_plate",
                "part_name": "FLAT_PLATE_SLOT_TEST",
                "material": "Aluminium 5052",
                "thickness": 2.0,
                "plate_width": 160.0,
                "plate_length": 100.0,
                "holes": [{"type": "slot", "x": 80.0, "y": 50.0, "length": 34.0, "width": 10.0}],
            }
        )
        pattern = calculate_flat_plate_pattern(params)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "FLAT_PLATE_SLOT_TEST.dxf"
            generate_flat_plate_dxf(pattern, output_path)

            doc = ezdxf.readfile(output_path)
            entities = list(doc.modelspace())
            slot_lines = [entity for entity in entities if entity.dxf.layer == "HOLE" and entity.dxftype() == "LINE"]
            slot_arcs = [entity for entity in entities if entity.dxf.layer == "HOLE" and entity.dxftype() == "ARC"]
            text_values = {
                entity.dxf.text
                for entity in entities
                if entity.dxf.layer == "TEXT" and entity.dxftype() == "TEXT"
            }

            self.assertEqual(len(slot_lines), 2)
            self.assertEqual(len(slot_arcs), 2)
            self.assertIn("HOLES: 1 SLOT, SEE HOLE LABELS", text_values)
            self.assertIn("H1 SLOT 34.00x10.00", text_values)


if __name__ == "__main__":
    unittest.main()
