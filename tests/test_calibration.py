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
    denominator_from_logmar,
    format_snellen,
    logmar_from_denominator,
    snellen_letter_height_mm,
    snellen_letter_height_px,
)


class CalibrationTest(unittest.TestCase):
    def test_snellen_20_20_letter_height_at_four_meters(self) -> None:
        height = snellen_letter_height_mm(4, 20)
        expected = 4_000 * math.tan(math.radians(5 / 60))
        self.assertLess(abs(height - expected), 0.01)

    def test_logmar_conversion_roundtrip(self) -> None:
        denominator = denominator_from_logmar(0.3)
        self.assertLess(abs(logmar_from_denominator(denominator) - 0.3), 0.001)

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


if __name__ == "__main__":
    unittest.main()
