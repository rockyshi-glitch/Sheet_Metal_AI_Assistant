"""Command-line behavior tests for invalid input paths."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_SCRIPT = PROJECT_ROOT / "src" / "main.py"


VALID_U_BRACKET_DATA = {
    "part_name": "U_BRACKET_CLI_TEST",
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


class MainCliTest(unittest.TestCase):
    def _run_main(self, input_path: Path, output_dir: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(MAIN_SCRIPT),
                "--input",
                str(input_path),
                "--output-dir",
                str(output_dir),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_invalid_json_returns_clear_error_and_no_dxf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "bad.json"
            output_dir = temp_path / "output"
            input_path.write_text("{not valid json", encoding="utf-8")

            result = self._run_main(input_path, output_dir)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Input error:", result.stderr)
            self.assertIn("is not valid JSON", result.stderr)
            self.assertFalse(list(output_dir.glob("*.dxf")) if output_dir.exists() else False)

    def test_unknown_part_type_returns_clear_error_and_no_dxf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "unknown_part.json"
            output_dir = temp_path / "output"
            data = dict(VALID_U_BRACKET_DATA, part_type="z_bracket")
            input_path.write_text(json.dumps(data), encoding="utf-8")

            result = self._run_main(input_path, output_dir)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Input error:", result.stderr)
            self.assertIn(
                "part_type must be 'u_bracket', 'u_bracket_with_holes', 'l_bracket', "
                "'l_bracket_with_holes', or 'flat_plate'",
                result.stderr,
            )
            self.assertFalse(list(output_dir.glob("*.dxf")) if output_dir.exists() else False)

    def test_invalid_dimension_returns_clear_error_and_no_dxf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "invalid_dimension.json"
            output_dir = temp_path / "output"
            data = dict(VALID_U_BRACKET_DATA, thickness=0)
            input_path.write_text(json.dumps(data), encoding="utf-8")

            result = self._run_main(input_path, output_dir)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Input error:", result.stderr)
            self.assertIn("thickness must be greater than 0", result.stderr)
            self.assertFalse(list(output_dir.glob("*.dxf")) if output_dir.exists() else False)

    def test_missing_input_file_returns_clear_error_and_no_dxf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "missing.json"
            output_dir = temp_path / "output"

            result = self._run_main(input_path, output_dir)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Input error:", result.stderr)
            self.assertIn("could not read", result.stderr)
            self.assertFalse(list(output_dir.glob("*.dxf")) if output_dir.exists() else False)

    def test_missing_required_field_returns_clear_error_and_no_dxf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "missing_field.json"
            output_dir = temp_path / "output"
            data = dict(VALID_U_BRACKET_DATA)
            del data["bottom_width"]
            input_path.write_text(json.dumps(data), encoding="utf-8")

            result = self._run_main(input_path, output_dir)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Input error:", result.stderr)
            self.assertIn("Missing required field(s): bottom_width", result.stderr)
            self.assertFalse(list(output_dir.glob("*.dxf")) if output_dir.exists() else False)

    def test_successful_u_bracket_run_generates_dxf_and_prints_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "u_bracket.json"
            output_dir = temp_path / "output"
            input_path.write_text(json.dumps(VALID_U_BRACKET_DATA), encoding="utf-8")

            result = self._run_main(input_path, output_dir)
            output_path = output_dir / "U_BRACKET_CLI_TEST.dxf"

            self.assertEqual(result.returncode, 0)
            self.assertTrue(output_path.exists())
            self.assertIn(f"Generated DXF: {output_path}", result.stdout)
            self.assertIn("Part type: u_bracket", result.stdout)
            self.assertIn("Flat size: 188.67 x 200.00 mm", result.stdout)
            self.assertIn("Bend allowance: 4.335 mm", result.stdout)

    def test_accepts_positional_input_path_for_project_plan_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "u_bracket.json"
            output_dir = temp_path / "output"
            input_path.write_text(json.dumps(VALID_U_BRACKET_DATA), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(MAIN_SCRIPT),
                    str(input_path),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue((output_dir / "U_BRACKET_CLI_TEST.dxf").exists())

    def test_can_generate_freecad_outline_text_variant_with_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "u_bracket.json"
            output_dir = temp_path / "output"
            input_path.write_text(json.dumps(VALID_U_BRACKET_DATA), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(MAIN_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output-dir",
                    str(output_dir),
                    "--text-mode",
                    "outline",
                    "--file-suffix",
                    "_FREECAD",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue((output_dir / "U_BRACKET_CLI_TEST_FREECAD.dxf").exists())
            self.assertIn("Text mode: outline", result.stdout)

    def test_can_generate_browser_svg_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "u_bracket.json"
            output_dir = temp_path / "output"
            input_path.write_text(json.dumps(VALID_U_BRACKET_DATA), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(MAIN_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output-dir",
                    str(output_dir),
                    "--preview-svg",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            preview_path = output_dir / "U_BRACKET_CLI_TEST_preview.svg"
            self.assertEqual(result.returncode, 0)
            self.assertTrue(preview_path.exists())
            self.assertIn(f"Generated SVG preview: {preview_path}", result.stdout)


if __name__ == "__main__":
    unittest.main()
