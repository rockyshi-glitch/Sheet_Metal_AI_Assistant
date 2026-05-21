"""Tests for SVG flat pattern previews."""

from __future__ import annotations

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sheet_metal_math import (  # noqa: E402
    FlatPlateParams,
    LBracketWithHolesParams,
    UBracketParams,
    UBracketWithHolesParams,
    calculate_flat_plate_pattern,
    calculate_l_bracket_with_holes_flat_pattern,
    calculate_u_bracket_flat_pattern,
    calculate_u_bracket_with_holes_flat_pattern,
)
from svg_preview import DRAWING_BOTTOM, DRAWING_TOP, _hole_bounds, _preview_transform, pattern_to_svg  # noqa: E402


class SvgPreviewTest(unittest.TestCase):
    def test_renders_u_bracket_bend_lines(self) -> None:
        pattern = calculate_u_bracket_flat_pattern(
            UBracketParams.from_dict(
                {
                    "part_name": "U_BRACKET_PREVIEW",
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
            )
        )

        svg = pattern_to_svg(pattern)

        self.assertIn("<svg", svg)
        self.assertIn('class="cut"', svg)
        self.assertEqual(svg.count('class="bend"'), 2)
        self.assertIn("U_BRACKET_PREVIEW", svg)
        self.assertIn("MATERIAL: Aluminium 5052", svg)
        self.assertIn("THICKNESS: 2.00 mm", svg)
        self.assertIn("FLAT SIZE: 188.67 x 200.00 mm", svg)
        self.assertIn("BEND ALLOWANCE: 4.335 mm", svg)
        self.assertIn("WIDTH 188.67 mm", svg)
        self.assertIn("LENGTH 200.00 mm", svg)
        self.assertIn('text-anchor="middle"', svg)
        self.assertIn('transform="rotate(-90', svg)
        self.assertIn("B1 BEND UP VERIFY", svg)
        self.assertIn("B2 BEND UP VERIFY", svg)
        self.assertNotIn("CUT red", svg)
        self.assertIn('class="cut legend-sample"', svg)
        self.assertIn('class="bend legend-sample"', svg)

    def test_renders_u_bracket_with_holes_and_bend_lines(self) -> None:
        pattern = calculate_u_bracket_with_holes_flat_pattern(
            UBracketWithHolesParams.from_dict(
                {
                    "part_type": "u_bracket_with_holes",
                    "part_name": "U_BRACKET_HOLES_PREVIEW",
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
        )

        svg = pattern_to_svg(pattern)

        self.assertEqual(svg.count('class="bend"'), 2)
        self.assertEqual(svg.count('class="hole"'), 2)
        self.assertIn("HOLES: 2", svg)
        self.assertIn("HOLE TABLE", svg)
        self.assertIn("BOTTOM", svg)
        self.assertIn("LEFT", svg)

    def test_renders_l_bracket_with_holes_and_bend_line(self) -> None:
        pattern = calculate_l_bracket_with_holes_flat_pattern(
            LBracketWithHolesParams.from_dict(
                {
                    "part_type": "l_bracket_with_holes",
                    "part_name": "L_BRACKET_HOLES_PREVIEW",
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
        )

        svg = pattern_to_svg(pattern)

        self.assertEqual(svg.count('class="bend"'), 1)
        self.assertEqual(svg.count('class="hole"'), 2)
        self.assertIn("HOLES: 2", svg)
        self.assertIn("BASE", svg)
        self.assertIn("FLANGE", svg)

    def test_renders_flat_plate_holes(self) -> None:
        pattern = calculate_flat_plate_pattern(
            FlatPlateParams.from_dict(
                {
                    "part_type": "flat_plate",
                    "part_name": "FLAT_PREVIEW",
                    "material": "Aluminium 5052",
                    "thickness": 2.0,
                    "plate_width": 160.0,
                    "plate_length": 100.0,
                    "holes": [
                        {"x": 30.0, "y": 30.0, "diameter": 10.0},
                        {"x": 130.0, "y": 70.0, "diameter": 10.0},
                    ],
                }
            )
        )

        svg = pattern_to_svg(pattern)

        self.assertEqual(svg.count('class="hole"'), 2)
        self.assertIn("H1", svg)
        self.assertIn("H2", svg)
        self.assertIn("HOLES: 2", svg)
        self.assertIn("HOLE TABLE", svg)
        self.assertIn("ID    X      Y      DIA", svg)
        self.assertIn("H1", svg)
        self.assertIn("30.0", svg)
        self.assertIn("10.0", svg)

    def test_renders_flat_plate_slot_hole(self) -> None:
        pattern = calculate_flat_plate_pattern(
            FlatPlateParams.from_dict(
                {
                    "part_type": "flat_plate",
                    "part_name": "SLOT_PREVIEW",
                    "material": "Aluminium 5052",
                    "thickness": 2.0,
                    "plate_width": 160.0,
                    "plate_length": 100.0,
                    "holes": [{"type": "slot", "x": 80.0, "y": 50.0, "length": 34.0, "width": 10.0}],
                }
            )
        )

        svg = pattern_to_svg(pattern)

        self.assertIn('<path class="hole"', svg)
        self.assertIn("34.0x10.0", svg)
        self.assertIn("HOLES: 1", svg)

    def test_can_highlight_invalid_flat_plate_hole(self) -> None:
        pattern = calculate_flat_plate_pattern(
            FlatPlateParams.from_dict(
                {
                    "part_type": "flat_plate",
                    "part_name": "INVALID_MARKER_PREVIEW",
                    "material": "Aluminium 5052",
                    "thickness": 2.0,
                    "plate_width": 180.0,
                    "plate_length": 110.0,
                    "holes": [
                        {"x": 35.0, "y": 35.0, "diameter": 10.0},
                        {"type": "slot", "x": 130.0, "y": 72.0, "length": 34.0, "width": 10.0},
                    ],
                }
            )
        )

        svg = pattern_to_svg(pattern, invalid_hole_indexes={1})

        self.assertIn('class="hole"', svg)
        self.assertIn('class="invalid-hole"', svg)
        self.assertIn('class="invalid-hole-label"', svg)

    def test_hole_labels_do_not_cross_hole_geometry(self) -> None:
        pattern = calculate_flat_plate_pattern(
            FlatPlateParams.from_dict(
                {
                    "part_type": "flat_plate",
                    "part_name": "HOLE_LABEL_PREVIEW",
                    "material": "Aluminium 5052",
                    "thickness": 2.0,
                    "plate_width": 180.0,
                    "plate_length": 110.0,
                    "holes": [
                        {"x": 35.0, "y": 35.0, "diameter": 10.0},
                        {"type": "slot", "x": 130.0, "y": 72.0, "length": 34.0, "width": 10.0},
                    ],
                }
            )
        )

        svg = pattern_to_svg(pattern)
        root = ET.fromstring(svg)
        scale, offset_x, offset_y = _preview_transform(pattern.flat_width, pattern.flat_length)
        labels_by_text = {
            element.text: element
            for element in root.findall("{http://www.w3.org/2000/svg}text")
            if element.attrib.get("class") == "hole-label"
        }

        self.assertEqual(set(labels_by_text), {"H1", "H2"})
        for index, hole in enumerate(pattern.holes, start=1):
            _, top, _, bottom = _hole_bounds(hole, scale, offset_x, offset_y, pattern.flat_length)
            label_y = float(labels_by_text[f"H{index}"].attrib["y"])
            self.assertLess(label_y, top)
            self.assertLess(label_y + 4.0, top)

    def test_renders_flat_plate_featured_outline_summary(self) -> None:
        pattern = calculate_flat_plate_pattern(
            FlatPlateParams.from_dict(
                {
                    "part_type": "flat_plate",
                    "part_name": "FEATURE_PREVIEW",
                    "material": "Aluminium 5052",
                    "thickness": 2.0,
                    "plate_width": 120.0,
                    "plate_length": 80.0,
                    "holes": [],
                    "features": [
                        {"type": "corner_chamfer", "corner": "lower_left", "distance": 10.0},
                        {"type": "corner_radius", "corner": "lower_right", "radius": 8.0},
                        {"type": "edge_notch", "side": "bottom", "offset": 40.0, "width": 20.0, "depth": 8.0},
                    ],
                }
            )
        )

        svg = pattern_to_svg(pattern)

        self.assertIn("FEATURES: 1 CHAMFER, 1 ROUND CORNER, 1 EDGE NOTCH", svg)
        self.assertIn('class="cut"', svg)

    def test_can_hide_preview_layers(self) -> None:
        pattern = calculate_flat_plate_pattern(
            FlatPlateParams.from_dict(
                {
                    "part_type": "flat_plate",
                    "part_name": "FLAT_LAYER_FILTER",
                    "material": "Aluminium 5052",
                    "thickness": 2.0,
                    "plate_width": 160.0,
                    "plate_length": 100.0,
                    "holes": [{"x": 30.0, "y": 30.0, "diameter": 10.0}],
                }
            )
        )

        svg = pattern_to_svg(pattern, visible_layers={"CUT"})

        self.assertIn('class="cut"', svg)
        self.assertNotIn('class="hole"', svg)
        self.assertNotIn("FLAT_LAYER_FILTER", svg.split("</style>", maxsplit=1)[1])
        self.assertNotIn("WIDTH 160.00 mm", svg)

    def test_can_hide_bend_label_without_hiding_bend_line(self) -> None:
        pattern = calculate_u_bracket_flat_pattern(
            UBracketParams.from_dict(
                {
                    "part_name": "U_BRACKET_NO_TEXT",
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
            )
        )

        svg = pattern_to_svg(pattern, visible_layers={"CUT", "BEND"})

        self.assertEqual(svg.count('class="bend"'), 2)
        self.assertNotIn('class="bend-label"', svg)

    def test_large_preview_outline_stays_below_header_text(self) -> None:
        pattern = calculate_flat_plate_pattern(
            FlatPlateParams.from_dict(
                {
                    "part_type": "flat_plate",
                    "part_name": "LARGE_FLAT_PREVIEW",
                    "material": "Aluminium 5052",
                    "thickness": 2.0,
                    "plate_width": 2000.0,
                    "plate_length": 1200.0,
                    "holes": [],
                }
            )
        )

        svg = pattern_to_svg(pattern)
        root = ET.fromstring(svg)
        polyline = root.find("{http://www.w3.org/2000/svg}polyline")
        self.assertIsNotNone(polyline)
        points = [
            tuple(float(value) for value in point.split(","))
            for point in polyline.attrib["points"].split()
        ]
        y_values = [point[1] for point in points]

        self.assertGreaterEqual(min(y_values), DRAWING_TOP)
        self.assertLessEqual(max(y_values), DRAWING_BOTTOM)

    def test_dimension_arrowheads_stay_inside_dimension_lines(self) -> None:
        pattern = calculate_flat_plate_pattern(
            FlatPlateParams.from_dict(
                {
                    "part_type": "flat_plate",
                    "part_name": "DIMENSION_ARROW_PREVIEW",
                    "material": "Aluminium 5052",
                    "thickness": 2.0,
                    "plate_width": 160.0,
                    "plate_length": 100.0,
                    "holes": [],
                }
            )
        )

        svg = pattern_to_svg(pattern)
        root = ET.fromstring(svg)
        dimension_lines = [
            line
            for line in root.findall("{http://www.w3.org/2000/svg}line")
            if line.attrib.get("class") == "dimension"
        ]
        arrows = [
            polygon
            for polygon in root.findall("{http://www.w3.org/2000/svg}polygon")
            if polygon.attrib.get("class") == "dimension-arrow"
        ]

        self.assertEqual(len(dimension_lines), 2)
        self.assertEqual(len(arrows), 4)
        for line in dimension_lines:
            self.assertNotIn("marker-start", line.attrib)
            self.assertNotIn("marker-end", line.attrib)

        horizontal_line = dimension_lines[0]
        vertical_line = dimension_lines[1]
        horizontal_min_x = min(float(horizontal_line.attrib["x1"]), float(horizontal_line.attrib["x2"]))
        horizontal_max_x = max(float(horizontal_line.attrib["x1"]), float(horizontal_line.attrib["x2"]))
        vertical_min_y = min(float(vertical_line.attrib["y1"]), float(vertical_line.attrib["y2"]))
        vertical_max_y = max(float(vertical_line.attrib["y1"]), float(vertical_line.attrib["y2"]))

        for arrow in arrows[:2]:
            x_values = [float(point.split(",")[0]) for point in arrow.attrib["points"].split()]
            self.assertGreaterEqual(min(x_values), horizontal_min_x)
            self.assertLessEqual(max(x_values), horizontal_max_x)
        for arrow in arrows[2:]:
            y_values = [float(point.split(",")[1]) for point in arrow.attrib["points"].split()]
            self.assertGreaterEqual(min(y_values), vertical_min_y)
            self.assertLessEqual(max(y_values), vertical_max_y)


if __name__ == "__main__":
    unittest.main()
