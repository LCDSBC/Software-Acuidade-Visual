from __future__ import annotations

import math

from optotipos_core.calibration import (
    DisplayCalibration,
    denominator_from_logmar,
    format_snellen,
    logmar_from_denominator,
    snellen_letter_height_mm,
    snellen_letter_height_px,
)


def test_snellen_20_20_letter_height_at_four_meters() -> None:
    height = snellen_letter_height_mm(4, 20)
    expected = 4_000 * math.tan(math.radians(5 / 60))
    assert abs(height - expected) < 0.01


def test_logmar_conversion_roundtrip() -> None:
    denominator = denominator_from_logmar(0.3)
    assert abs(logmar_from_denominator(denominator) - 0.3) < 0.001


def test_pixel_height_uses_calibration_scale() -> None:
    calibration = DisplayCalibration(
        distance_m=4,
        screen_width_mm=597,
        screen_height_mm=336,
        resolution_width=1920,
        resolution_height=1080,
        scale_factor=1.0,
    )
    assert snellen_letter_height_px(calibration, 20) > 40
    assert format_snellen(20.0) == "20/20"
