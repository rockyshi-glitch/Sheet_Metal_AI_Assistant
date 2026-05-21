"""Tests for Streamlit form data helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from streamlit_app import (  # noqa: E402
    _build_chamfer_features,
    _build_circle_holes,
    _build_notch_features,
    _build_radius_features,
    _build_slot_holes,
    _circle_hole_range_notes,
    _diagnostic_svg_for_invalid_flat_plate,
    _feature_aware_validation_message,
    _format_validation_error,
    _invalid_hole_indexes_from_message,
    _preview_layer_key,
    _slot_hole_range_notes,
)


class StreamlitAppHelperTest(unittest.TestCase):
    def test_builds_circle_and_slot_holes_from_editor_rows(self) -> None:
        circle_holes = _build_circle_holes(
            [
                {"x": 35.0, "y": 35.0, "diameter": 10.0},
                {"x": None, "y": 70.0, "diameter": 8.0},
            ]
        )
        slot_holes = _build_slot_holes(
            [
                {"x": 130.0, "y": 72.0, "length": 34.0, "width": 10.0, "orientation": "horizontal"},
                {"x": 90.0, "y": None, "length": 30.0, "width": 8.0, "orientation": "vertical"},
            ]
        )

        self.assertEqual(circle_holes, [{"x": 35.0, "y": 35.0, "diameter": 10.0}])
        self.assertEqual(
            slot_holes,
            [{"type": "slot", "x": 130.0, "y": 72.0, "length": 34.0, "width": 10.0, "orientation": "horizontal"}],
        )

    def test_builds_flat_plate_features_from_editor_rows(self) -> None:
        chamfers = _build_chamfer_features(
            [
                {"corner": "lower_left", "distance": 12.0},
                {"corner": "", "distance": 8.0},
            ]
        )
        radii = _build_radius_features(
            [
                {"corner": "lower_right", "radius": 10.0},
                {"corner": "upper_left", "radius": None},
            ]
        )
        notches = _build_notch_features(
            [
                {"side": "bottom", "offset": 70.0, "width": 28.0, "depth": 10.0},
                {"side": "right", "offset": None, "width": 12.0, "depth": 6.0},
            ]
        )

        self.assertEqual(chamfers, [{"type": "corner_chamfer", "corner": "lower_left", "distance": 12.0}])
        self.assertEqual(radii, [{"type": "corner_radius", "corner": "lower_right", "radius": 10.0}])
        self.assertEqual(
            notches,
            [{"type": "edge_notch", "side": "bottom", "offset": 70.0, "width": 28.0, "depth": 10.0}],
        )

    def test_preview_layer_keys_are_scoped_by_part_type(self) -> None:
        self.assertEqual(_preview_layer_key("flat_plate", "manual_preview_layer", "HOLE"), "manual_preview_layer_flat_plate_hole")
        self.assertNotEqual(
            _preview_layer_key("flat_plate", "manual_preview_layer", "HOLE"),
            _preview_layer_key("u_bracket", "manual_preview_layer", "HOLE"),
        )

    def test_formats_hole_outside_plate_error_for_streamlit_users(self) -> None:
        data = {
            "part_type": "flat_plate",
            "part_name": "FLAT_PLATE_FEATURES_STREAMLIT",
            "material": "Aluminium 5052",
            "thickness": 2.0,
            "plate_width": 180.0,
            "plate_length": 110.0,
            "holes": [
                {"x": 35.0, "y": 35.0, "diameter": 10.0},
                {"type": "slot", "x": 300.0, "y": 1000.0, "length": 34.0, "width": 10.0, "orientation": "horizontal"},
            ],
        }

        message = _format_validation_error("holes[1].x must keep the hole inside the plate.", data)

        self.assertIn("第 2 个孔/槽孔", message)
        self.assertIn("中心 X 超出板件范围", message)
        self.assertIn("当前值为 300.00 mm", message)
        self.assertIn("建议范围约为 17.00 - 163.00 mm", message)

    def test_formats_hole_intersecting_feature_cutout_error(self) -> None:
        data = {
            "part_type": "flat_plate",
            "part_name": "FLAT_PLATE_FEATURES_STREAMLIT",
            "material": "Aluminium 5052",
            "thickness": 2.0,
            "plate_width": 180.0,
            "plate_length": 110.0,
            "holes": [
                {"x": 35.0, "y": 35.0, "diameter": 10.0},
                {"type": "slot", "x": 70.0, "y": 10.0, "length": 34.0, "width": 10.0, "orientation": "horizontal"},
            ],
            "features": [
                {"type": "corner_chamfer", "corner": "lower_left", "distance": 12.0},
                {"type": "corner_chamfer", "corner": "upper_right", "distance": 15.0},
                {"type": "edge_notch", "side": "bottom", "offset": 70.0, "width": 28.0, "depth": 10.0},
            ],
        }

        message = _feature_aware_validation_message(data)

        self.assertIsNotNone(message)
        self.assertIn("第 2 个孔/槽孔", message)
        self.assertIn("异形外轮廓", message)
        self.assertIn("缺口", message)

    def test_builds_diagnostic_svg_for_invalid_flat_plate_hole(self) -> None:
        data = {
            "part_type": "flat_plate",
            "part_name": "FLAT_PLATE_FEATURES_STREAMLIT",
            "material": "Aluminium 5052",
            "thickness": 2.0,
            "plate_width": 180.0,
            "plate_length": 110.0,
            "holes": [
                {"x": 35.0, "y": 35.0, "diameter": 10.0},
                {"type": "slot", "x": 70.0, "y": 10.0, "length": 34.0, "width": 10.0, "orientation": "horizontal"},
            ],
            "features": [
                {"type": "corner_chamfer", "corner": "lower_left", "distance": 12.0},
                {"type": "corner_chamfer", "corner": "upper_right", "distance": 15.0},
                {"type": "edge_notch", "side": "bottom", "offset": 70.0, "width": 28.0, "depth": 10.0},
            ],
        }

        svg = _diagnostic_svg_for_invalid_flat_plate(
            data,
            {"CUT", "HOLE", "TEXT"},
            "holes[1] must keep the full hole inside the cut outline.",
        )

        self.assertEqual(_invalid_hole_indexes_from_message("holes[1] must keep the full hole inside the cut outline."), {1})
        self.assertIsNotNone(svg)
        self.assertIn('class="invalid-hole"', svg)
        self.assertIn('class="invalid-hole-label"', svg)
        self.assertIn('class="cut"', svg)

    def test_formats_circle_and_slot_center_range_notes(self) -> None:
        circle_notes = _circle_hole_range_notes(
            [{"x": 35.0, "y": 35.0, "diameter": 10.0}],
            plate_width=180.0,
            plate_length=110.0,
        )
        slot_notes = _slot_hole_range_notes(
            [
                {"x": 130.0, "y": 72.0, "length": 34.0, "width": 10.0, "orientation": "horizontal"},
                {"x": 90.0, "y": 60.0, "length": 30.0, "width": 8.0, "orientation": "vertical"},
            ],
            plate_width=180.0,
            plate_length=110.0,
        )

        self.assertEqual(circle_notes, ["H1: X 5.00-175.00 mm, Y 5.00-105.00 mm"])
        self.assertEqual(
            slot_notes,
            [
                "S1: X 17.00-163.00 mm, Y 5.00-105.00 mm",
                "S2: X 4.00-176.00 mm, Y 15.00-95.00 mm",
            ],
        )

    def test_manual_parameter_inputs_are_not_wrapped_in_streamlit_form(self) -> None:
        source = (PROJECT_ROOT / "src" / "streamlit_app.py").read_text(encoding="utf-8")

        self.assertNotIn('st.form("manual_parameters")', source)
        self.assertNotIn("form_submit_button", source)
        self.assertIn('st.button("生成 DXF"', source)


if __name__ == "__main__":
    unittest.main()
