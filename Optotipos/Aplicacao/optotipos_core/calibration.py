from __future__ import annotations

import math
from dataclasses import dataclass

from .config import RuntimeConfig


MIN_DISTANCE_M = 1.0
MAX_DISTANCE_M = 20.0
REFERENCE_SNELLEN_NUMERATOR_FT = 20.0
STANDARD_LETTER_ARC_MINUTES = 5.0


@dataclass(frozen=True)
class DisplayCalibration:
    distance_m: float
    screen_width_mm: float
    screen_height_mm: float
    resolution_width: int
    resolution_height: int
    scale_factor: float

    @property
    def pixels_per_mm_x(self) -> float:
        return (self.resolution_width / self.screen_width_mm) * self.scale_factor

    @property
    def pixels_per_mm_y(self) -> float:
        return (self.resolution_height / self.screen_height_mm) * self.scale_factor

    @property
    def pixels_per_mm(self) -> float:
        return (self.pixels_per_mm_x + self.pixels_per_mm_y) / 2


def clamp_distance(distance_m: float) -> float:
    return max(MIN_DISTANCE_M, min(MAX_DISTANCE_M, distance_m))


def calibration_from_config(config: RuntimeConfig) -> DisplayCalibration:
    distance = config.get_float("Distancia.txt", "Distancia", 4.0)
    unit = config.get("Distancia.txt", "Unidade", "m").lower()
    if unit == "mm":
        distance = distance / 1000
    elif unit == "cm":
        distance = distance / 100

    width_mm = config.get_float("Tela.txt", "LarguraTelaMM", 597.0)
    height_mm = config.get_float("Tela.txt", "AlturaTelaMM", 336.0)
    return DisplayCalibration(
        distance_m=clamp_distance(distance),
        screen_width_mm=max(width_mm, 1.0),
        screen_height_mm=max(height_mm, 1.0),
        resolution_width=max(config.get_int("Tela.txt", "ResolucaoLargura", 1920), 1),
        resolution_height=max(config.get_int("Tela.txt", "ResolucaoAltura", 1080), 1),
        scale_factor=max(config.get_float("Escala.txt", "FatorEscala", 1.0), 0.1),
    )


def millimeters_for_visual_angle(distance_m: float, arc_minutes: float) -> float:
    angle_radians = math.radians(arc_minutes / 60.0)
    return 2 * distance_m * 1000 * math.tan(angle_radians / 2)


def snellen_letter_height_mm(distance_m: float, denominator_ft: float) -> float:
    multiplier = denominator_ft / REFERENCE_SNELLEN_NUMERATOR_FT
    return millimeters_for_visual_angle(distance_m, STANDARD_LETTER_ARC_MINUTES * multiplier)


def snellen_letter_height_px(calibration: DisplayCalibration, denominator_ft: float) -> int:
    height_mm = snellen_letter_height_mm(calibration.distance_m, denominator_ft)
    return max(8, round(height_mm * calibration.pixels_per_mm))


def denominator_from_logmar(logmar: float) -> float:
    decimal_acuity = 10 ** (-logmar)
    if decimal_acuity <= 0:
        return 400.0
    return REFERENCE_SNELLEN_NUMERATOR_FT / decimal_acuity


def logmar_from_denominator(denominator_ft: float) -> float:
    decimal_acuity = REFERENCE_SNELLEN_NUMERATOR_FT / max(denominator_ft, 1.0)
    return -math.log10(decimal_acuity)


def etdrs_line_denominators() -> list[float]:
    return [200, 160, 125, 100, 80, 63, 50, 40, 32, 25, 20, 16, 12.5, 10]


def format_snellen(denominator_ft: float) -> str:
    if denominator_ft.is_integer():
        return f"20/{int(denominator_ft)}"
    return f"20/{denominator_ft:g}"


def format_logmar(denominator_ft: float) -> str:
    return f"{logmar_from_denominator(denominator_ft):.2f} LogMAR"
