"""Tests for U-bracket sheet metal calculations and input validation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sheet_metal_math import (  # noqa: E402
    CornerChamfer,
    CornerRadius,
    EdgeNotch,
    FlatPlateParams,
    LBracketParams,
    LBracketWithHolesParams,
    SlotHole,
    UBracketParams,
    UBracketWithHolesParams,
    calculate_bend_allowance,
    calculate_flat_plate_pattern,
    calculate_l_bracket_flat_pattern,
    calculate_l_bracket_with_holes_flat_pattern,
    calculate_u_bracket_flat_pattern,
    calculate_u_bracket_with_holes_flat_pattern,
)


VALID_U_BRACKET_DATA = {
    "part_name": "U_BRACKET_001",
    "material": "Aluminium 5052",
    "thickness": 2.0,
    "inside_bend_radius": 2.0,
    "k_factor": 0.38,
    "part_length": 200.0,
    "bottom_width": 100.0,
    "left_flange_height": 40.0,
    "right_flange_height": 40.0,
    "bend_angle": 90,
}

VALID_U_BRACKET_WITH_HOLES_DATA = {
    **VALID_U_BRACKET_DATA,
    "part_type": "u_bracket_with_holes",
    "part_name": "U_BRACKET_HOLES_001",
    "min_hole_to_bend_distance": 8.0,
    "holes": [
        {"face": "bottom", "x": 50.0, "y": 60.0, "diameter": 12.0},
        {"face": "bottom", "x": 50.0, "y": 140.0, "diameter": 12.0},
        {"face": "left_flange", "x": 18.0, "y": 100.0, "diameter": 8.0},
        {"face": "right_flange", "x": 22.0, "y": 100.0, "diameter": 8.0},
    ],
}

VALID_L_BRACKET_DATA = {
    "part_type": "l_bracket",
    "part_name": "L_BRACKET_001",
    "material": "Aluminium 5052",
    "thickness": 2.0,
    "inside_bend_radius": 2.0,
    "k_factor": 0.38,
    "part_length": 200.0,
    "base_width": 100.0,
    "flange_height": 40.0,
    "bend_angle": 90,
}

VALID_L_BRACKET_WITH_HOLES_DATA = {
    **VALID_L_BRACKET_DATA,
    "part_type": "l_bracket_with_holes",
    "part_name": "L_BRACKET_HOLES_001",
    "min_hole_to_bend_distance": 8.0,
    "holes": [
        {"face": "base", "x": 50.0, "y": 60.0, "diameter": 12.0},
        {"face": "base", "x": 50.0, "y": 140.0, "diameter": 12.0},
        {"face": "flange", "x": 18.0, "y": 100.0, "diameter": 8.0},
    ],
}

VALID_FLAT_PLATE_DATA = {
    "part_type": "flat_plate",
    "part_name": "FLAT_PLATE_001",
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


class SheetMetalMathTest(unittest.TestCase):
    def test_calculates_bend_allowance_for_sample_part(self) -> None:
        bend_allowance = calculate_bend_allowance(
            bend_angle=90.0,
            inside_bend_radius=2.0,
            k_factor=0.38,
            thickness=2.0,
        )

        self.assertAlmostEqual(bend_allowance, 4.335397861953914, places=6)

    def test_calculates_u_bracket_flat_pattern_for_sample_part(self) -> None:
        params = UBracketParams.from_dict(VALID_U_BRACKET_DATA)
        pattern = calculate_u_bracket_flat_pattern(params)

        self.assertAlmostEqual(pattern.flat_width, 188.67079572390783, places=6)
        self.assertAlmostEqual(pattern.flat_length, 200.0, places=6)
        self.assertAlmostEqual(pattern.left_bend_x, 42.16769893097696, places=6)
        self.assertAlmostEqual(pattern.right_bend_x, 146.50309679293086, places=6)
        self.assertEqual(
            pattern.cut_outline,
            [
                (0.0, 0.0),
                (pattern.flat_width, 0.0),
                (pattern.flat_width, pattern.flat_length),
                (0.0, pattern.flat_length),
                (0.0, 0.0),
            ],
        )

    def test_calculates_u_bracket_with_holes_flat_pattern(self) -> None:
        params = UBracketWithHolesParams.from_dict(VALID_U_BRACKET_WITH_HOLES_DATA)
        pattern = calculate_u_bracket_with_holes_flat_pattern(params)

        self.assertAlmostEqual(pattern.flat_width, 188.67079572390783, places=6)
        self.assertEqual(pattern.hole_faces, ["bottom", "bottom", "left_flange", "right_flange"])
        self.assertEqual(len(pattern.holes), 4)
        self.assertAlmostEqual(pattern.holes[0].x, 94.33539786195391, places=6)
        self.assertAlmostEqual(pattern.holes[2].x, 18.0, places=6)
        self.assertAlmostEqual(pattern.holes[3].x, 170.67079572390783, places=6)
        self.assertEqual(pattern.min_hole_to_bend_distance, 8.0)

    def test_calculates_u_bracket_with_slot_hole_flat_pattern(self) -> None:
        data = dict(
            VALID_U_BRACKET_WITH_HOLES_DATA,
            holes=[{"type": "slot", "face": "bottom", "x": 50.0, "y": 100.0, "length": 24.0, "width": 8.0}],
        )

        params = UBracketWithHolesParams.from_dict(data)
        pattern = calculate_u_bracket_with_holes_flat_pattern(params)

        self.assertIsInstance(pattern.holes[0], SlotHole)
        self.assertEqual(pattern.hole_faces, ["bottom"])
        self.assertAlmostEqual(pattern.holes[0].x, 94.33539786195391, places=6)
        self.assertEqual(pattern.holes[0].orientation, "horizontal")

    def test_rejects_u_bracket_slot_hole_too_close_to_bend_adjacent_edge(self) -> None:
        data = dict(
            VALID_U_BRACKET_WITH_HOLES_DATA,
            holes=[{"type": "slot", "face": "bottom", "x": 18.0, "y": 100.0, "length": 24.0, "width": 8.0}],
        )

        with self.assertRaisesRegex(ValueError, "bend influence zone"):
            UBracketWithHolesParams.from_dict(data)

    def test_rejects_u_bracket_hole_too_close_to_bend_adjacent_edge(self) -> None:
        data = dict(
            VALID_U_BRACKET_WITH_HOLES_DATA,
            holes=[{"face": "bottom", "x": 10.0, "y": 60.0, "diameter": 8.0}],
        )

        with self.assertRaisesRegex(ValueError, r"bend-line clearance: 8\.17 mm, face-edge clearance: 6\.00 mm"):
            UBracketWithHolesParams.from_dict(data)

    def test_rejects_u_bracket_hole_outside_own_face(self) -> None:
        data = dict(
            VALID_U_BRACKET_WITH_HOLES_DATA,
            holes=[{"face": "left_flange", "x": 3.0, "y": 60.0, "diameter": 8.0}],
        )

        with self.assertRaisesRegex(ValueError, r"holes\[0\]\.x must keep the hole inside the face"):
            UBracketWithHolesParams.from_dict(data)

    def test_calculates_l_bracket_flat_pattern_for_sample_part(self) -> None:
        params = LBracketParams.from_dict(VALID_L_BRACKET_DATA)
        pattern = calculate_l_bracket_flat_pattern(params)

        self.assertAlmostEqual(pattern.flat_width, 144.3353978619539, places=6)
        self.assertAlmostEqual(pattern.flat_length, 200.0, places=6)
        self.assertAlmostEqual(pattern.bend_x, 42.16769893097696, places=6)
        self.assertEqual(
            pattern.cut_outline,
            [
                (0.0, 0.0),
                (pattern.flat_width, 0.0),
                (pattern.flat_width, pattern.flat_length),
                (0.0, pattern.flat_length),
                (0.0, 0.0),
            ],
        )

    def test_calculates_l_bracket_with_holes_flat_pattern(self) -> None:
        params = LBracketWithHolesParams.from_dict(VALID_L_BRACKET_WITH_HOLES_DATA)
        pattern = calculate_l_bracket_with_holes_flat_pattern(params)

        self.assertAlmostEqual(pattern.flat_width, 144.3353978619539, places=6)
        self.assertEqual(pattern.hole_faces, ["base", "base", "flange"])
        self.assertEqual(len(pattern.holes), 3)
        self.assertAlmostEqual(pattern.holes[0].x, 94.33539786195391, places=6)
        self.assertAlmostEqual(pattern.holes[2].x, 18.0, places=6)
        self.assertEqual(pattern.min_hole_to_bend_distance, 8.0)

    def test_rejects_l_bracket_hole_too_close_to_bend_adjacent_edge(self) -> None:
        data = dict(
            VALID_L_BRACKET_WITH_HOLES_DATA,
            holes=[{"face": "base", "x": 10.0, "y": 60.0, "diameter": 8.0}],
        )

        with self.assertRaisesRegex(ValueError, r"bend-line clearance: 8\.17 mm, face-edge clearance: 6\.00 mm"):
            LBracketWithHolesParams.from_dict(data)

    def test_rejects_l_bracket_hole_outside_own_face(self) -> None:
        data = dict(
            VALID_L_BRACKET_WITH_HOLES_DATA,
            holes=[{"face": "flange", "x": 3.0, "y": 60.0, "diameter": 8.0}],
        )

        with self.assertRaisesRegex(ValueError, r"holes\[0\]\.x must keep the hole inside the face"):
            LBracketWithHolesParams.from_dict(data)

    def test_calculates_flat_plate_pattern_for_sample_part(self) -> None:
        params = FlatPlateParams.from_dict(VALID_FLAT_PLATE_DATA)
        pattern = calculate_flat_plate_pattern(params)

        self.assertAlmostEqual(pattern.flat_width, 160.0, places=6)
        self.assertAlmostEqual(pattern.flat_length, 100.0, places=6)
        self.assertEqual(len(pattern.holes), 4)
        self.assertEqual(pattern.holes[0].radius, 5.0)
        self.assertEqual(
            pattern.cut_outline,
            [
                (0.0, 0.0),
                (160.0, 0.0),
                (160.0, 100.0),
                (0.0, 100.0),
                (0.0, 0.0),
            ],
        )
        self.assertEqual(pattern.features, [])

    def test_calculates_flat_plate_pattern_with_chamfer_and_edge_notch_features(self) -> None:
        data = dict(
            VALID_FLAT_PLATE_DATA,
            plate_width=120.0,
            plate_length=80.0,
            holes=[],
            features=[
                {"type": "corner_chamfer", "corner": "lower_left", "distance": 10.0},
                {"type": "corner_chamfer", "corner": "upper_right", "distance": 12.0},
                {"type": "edge_notch", "side": "bottom", "offset": 40.0, "width": 20.0, "depth": 8.0},
            ],
        )

        params = FlatPlateParams.from_dict(data)
        pattern = calculate_flat_plate_pattern(params)

        self.assertIsInstance(pattern.features[0], CornerChamfer)
        self.assertIsInstance(pattern.features[2], EdgeNotch)
        self.assertEqual(
            pattern.cut_outline,
            [
                (10.0, 0.0),
                (40.0, 0.0),
                (40.0, 8.0),
                (60.0, 8.0),
                (60.0, 0.0),
                (120.0, 0.0),
                (120.0, 68.0),
                (108.0, 80.0),
                (0.0, 80.0),
                (0.0, 10.0),
                (10.0, 0.0),
            ],
        )

    def test_calculates_flat_plate_pattern_with_corner_radius_feature(self) -> None:
        data = dict(
            VALID_FLAT_PLATE_DATA,
            plate_width=120.0,
            plate_length=80.0,
            holes=[],
            features=[
                {"type": "corner_radius", "corner": "lower_right", "radius": 10.0},
                {"type": "edge_notch", "side": "bottom", "offset": 40.0, "width": 20.0, "depth": 8.0},
            ],
        )

        params = FlatPlateParams.from_dict(data)
        pattern = calculate_flat_plate_pattern(params)

        self.assertIsInstance(pattern.features[0], CornerRadius)
        self.assertEqual(pattern.cut_outline[0], (0.0, 0.0))
        self.assertIn((110.0, 0.0), pattern.cut_outline)
        self.assertIn((120.0, 10.0), pattern.cut_outline)
        self.assertGreater(len(pattern.cut_outline), 12)

    def test_rejects_corner_with_both_chamfer_and_radius(self) -> None:
        data = dict(
            VALID_FLAT_PLATE_DATA,
            holes=[],
            features=[
                {"type": "corner_chamfer", "corner": "lower_left", "distance": 10.0},
                {"type": "corner_radius", "corner": "lower_left", "radius": 8.0},
            ],
        )

        with self.assertRaisesRegex(ValueError, "cannot have both chamfer and corner radius"):
            FlatPlateParams.from_dict(data)

    def test_accepts_flat_plate_slot_hole(self) -> None:
        data = dict(
            VALID_FLAT_PLATE_DATA,
            holes=[{"type": "slot", "x": 80.0, "y": 50.0, "length": 34.0, "width": 10.0}],
        )

        params = FlatPlateParams.from_dict(data)

        self.assertIsInstance(params.holes[0], SlotHole)
        self.assertEqual(params.holes[0].orientation, "horizontal")
        self.assertAlmostEqual(params.holes[0].radius, 5.0)
        self.assertEqual(params.holes[0].check_centers, [(68.0, 50.0), (92.0, 50.0)])

    def test_rejects_missing_required_field(self) -> None:
        data = dict(VALID_U_BRACKET_DATA)
        del data["thickness"]

        with self.assertRaisesRegex(ValueError, "Missing required field"):
            UBracketParams.from_dict(data)

    def test_rejects_non_positive_dimensions(self) -> None:
        data = dict(VALID_U_BRACKET_DATA, bottom_width=0)

        with self.assertRaisesRegex(ValueError, "bottom_width must be greater than 0"):
            UBracketParams.from_dict(data)

    def test_rejects_invalid_k_factor(self) -> None:
        data = dict(VALID_U_BRACKET_DATA, k_factor=1.2)

        with self.assertRaisesRegex(ValueError, "k_factor must be between 0 and 1"):
            UBracketParams.from_dict(data)

    def test_rejects_invalid_bend_angle(self) -> None:
        data = dict(VALID_U_BRACKET_DATA, bend_angle=0)

        with self.assertRaisesRegex(ValueError, "bend_angle must be greater than 0"):
            UBracketParams.from_dict(data)

    def test_rejects_invalid_l_bracket_dimension(self) -> None:
        data = dict(VALID_L_BRACKET_DATA, flange_height=-1)

        with self.assertRaisesRegex(ValueError, "flange_height must be greater than 0"):
            LBracketParams.from_dict(data)

    def test_rejects_flat_plate_hole_outside_plate(self) -> None:
        data = dict(VALID_FLAT_PLATE_DATA)
        data["holes"] = [{"x": 3.0, "y": 30.0, "diameter": 10.0}]

        with self.assertRaisesRegex(ValueError, r"holes\[0\]\.x must keep the hole inside the plate"):
            FlatPlateParams.from_dict(data)

    def test_rejects_flat_plate_invalid_holes_value(self) -> None:
        data = dict(VALID_FLAT_PLATE_DATA, holes="not a list")

        with self.assertRaisesRegex(ValueError, "holes must be a list"):
            FlatPlateParams.from_dict(data)

    def test_rejects_flat_plate_notch_overlapping_chamfer(self) -> None:
        data = dict(
            VALID_FLAT_PLATE_DATA,
            holes=[],
            features=[
                {"type": "corner_chamfer", "corner": "lower_left", "distance": 10.0},
                {"type": "edge_notch", "side": "bottom", "offset": 5.0, "width": 20.0, "depth": 8.0},
            ],
        )

        with self.assertRaisesRegex(ValueError, "bottom edge notch must fit"):
            FlatPlateParams.from_dict(data)

    def test_rejects_hole_inside_removed_edge_notch_area(self) -> None:
        data = dict(
            VALID_FLAT_PLATE_DATA,
            holes=[{"x": 50.0, "y": 4.0, "diameter": 4.0}],
            features=[{"type": "edge_notch", "side": "bottom", "offset": 40.0, "width": 20.0, "depth": 8.0}],
        )

        with self.assertRaisesRegex(ValueError, "hole center inside the cut outline"):
            FlatPlateParams.from_dict(data)

    def test_rejects_slot_hole_too_close_to_plate_edge(self) -> None:
        data = dict(
            VALID_FLAT_PLATE_DATA,
            holes=[{"type": "slot", "x": 12.0, "y": 50.0, "length": 34.0, "width": 10.0}],
        )

        with self.assertRaisesRegex(ValueError, r"holes\[0\]\.x must keep the hole inside the plate"):
            FlatPlateParams.from_dict(data)


if __name__ == "__main__":
    unittest.main()
