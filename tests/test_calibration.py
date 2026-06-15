from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.calibration import (
    DisplayCalibration,
    calibration_report,
    calibration_from_config,
    clamp_distance,
    denominator_from_logmar,
    etdrs_line_logmars,
    format_snellen,
    logmar_from_denominator,
    optotype_stroke_width_mm,
    optotype_stroke_width_px,
    snellen_letter_height_mm,
    snellen_letter_height_px,
)
from optotipos_core.config import RuntimeConfig


class CalibrationTest(unittest.TestCase):
    def test_snellen_20_20_letter_height_at_four_meters(self) -> None:
        height = snellen_letter_height_mm(4, 20)
        expected = 4_000 * math.tan(math.radians(5 / 60))
        self.assertLess(abs(height - expected), 0.01)

    def test_logmar_conversion_roundtrip(self) -> None:
        denominator = denominator_from_logmar(0.3)
        self.assertLess(abs(logmar_from_denominator(denominator) - 0.3), 0.001)
        self.assertEqual(denominator_from_logmar(1000), 400.0)

    def test_pixel_height_uses_calibration_scale(self) -> None:
        calibration = DisplayCalibration(
            distance_m=4,
            screen_width_mm=597,
            screen_height_mm=336,
            resolution_width=1920,
            resolution_height=1080,
            scale_factor=1.0,
        )
        self.assertGreater(snellen_letter_height_px(calibration, 20), 15)
        self.assertEqual(format_snellen(20.0), "20/20")

    def test_optotype_stroke_is_one_fifth_of_letter_height(self) -> None:
        height = snellen_letter_height_mm(4, 20)
        self.assertAlmostEqual(optotype_stroke_width_mm(4, 20), height / 5)

    def test_pixel_mm_roundtrip_and_stroke_width(self) -> None:
        calibration = DisplayCalibration(
            distance_m=4,
            screen_width_mm=500,
            screen_height_mm=250,
            resolution_width=1000,
            resolution_height=500,
            scale_factor=1.0,
        )
        self.assertEqual(calibration.mm_to_px(10), 20)
        self.assertEqual(calibration.mm_to_px(10, "x"), 20)
        self.assertEqual(calibration.mm_to_px(10, "y"), 20)
        self.assertEqual(calibration.px_to_mm(20), 10)
        self.assertEqual(calibration.px_to_mm(20, "x"), 10)
        self.assertEqual(calibration.px_to_mm(20, "y"), 10)
        self.assertEqual(optotype_stroke_width_px(calibration, 20), round(snellen_letter_height_px(calibration, 20) / 5))

    def test_calibration_report_contains_precision_and_error(self) -> None:
        calibration = DisplayCalibration(
            distance_m=4,
            screen_width_mm=500,
            screen_height_mm=250,
            resolution_width=1000,
            resolution_height=500,
            scale_factor=1.0,
        )
        report = calibration_report(calibration)
        self.assertGreater(report.precision_percent, 99)
        self.assertEqual(report.scale_factor, 1.0)
        self.assertIn("Precisao estimada", report.as_lines()[0])

    def test_zero_pixel_density_is_reported_as_error(self) -> None:
        calibration = DisplayCalibration(
            distance_m=4,
            screen_width_mm=1,
            screen_height_mm=1,
            resolution_width=0,
            resolution_height=0,
            scale_factor=1.0,
        )
        self.assertEqual(calibration.axis_difference_percent, 100.0)
        self.assertEqual(calibration.px_to_mm(10), 0.0)

    def test_etdrs_logmar_lines_are_tenth_steps(self) -> None:
        lines = etdrs_line_logmars()
        self.assertEqual(lines[0], 1.0)
        self.assertEqual(lines[-1], -0.3)
        self.assertTrue(all(round(lines[index] - lines[index + 1], 1) == 0.1 for index in range(len(lines) - 1)))

    def test_distance_and_config_units_are_clamped(self) -> None:
        values = {
            "Distancia.txt": {"Distancia": "4000", "Unidade": "mm"},
            "Tela.txt": {"LarguraTelaMM": "597", "AlturaTelaMM": "336", "ResolucaoLargura": "1920", "ResolucaoAltura": "1080"},
            "Escala.txt": {"FatorEscala": "1.0"},
        }
        config = RuntimeConfig(root=Path("."), values=values)
        self.assertEqual(calibration_from_config(config).distance_m, 4)
        values["Distancia.txt"] = {"Distancia": "2500", "Unidade": "cm"}
        self.assertEqual(calibration_from_config(config).distance_m, 20)
        self.assertEqual(clamp_distance(0.5), 1.0)
        self.assertEqual(clamp_distance(25), 20.0)


if __name__ == "__main__":
    unittest.main()
