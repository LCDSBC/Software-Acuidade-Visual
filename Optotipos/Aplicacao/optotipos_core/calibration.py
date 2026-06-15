from __future__ import annotations

import math
from dataclasses import dataclass

from .config import RuntimeConfig


MIN_DISTANCE_M = 1.0
MAX_DISTANCE_M = 20.0
REFERENCE_SNELLEN_NUMERATOR_FT = 20.0
STANDARD_LETTER_ARC_MINUTES = 5.0
SNELLEN_CLINICAL_DENOMINATORS = (400, 300, 200, 100, 80, 60, 50, 40, 30, 25, 20, 15, 10)
ETDRS_LOGMAR_LINES = tuple(round(value / 10, 1) for value in range(10, -4, -1))


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

    @property
    def axis_difference_percent(self) -> float:
        average = self.pixels_per_mm
        if average == 0:
            return 100.0
        return abs(self.pixels_per_mm_x - self.pixels_per_mm_y) / average * 100

    def mm_to_px(self, value_mm: float, axis: str = "average") -> float:
        if axis == "x":
            return value_mm * self.pixels_per_mm_x
        if axis == "y":
            return value_mm * self.pixels_per_mm_y
        return value_mm * self.pixels_per_mm

    def px_to_mm(self, value_px: float, axis: str = "average") -> float:
        pixels_per_mm = self.pixels_per_mm
        if axis == "x":
            pixels_per_mm = self.pixels_per_mm_x
        elif axis == "y":
            pixels_per_mm = self.pixels_per_mm_y
        if pixels_per_mm == 0:
            return 0.0
        return value_px / pixels_per_mm


@dataclass(frozen=True)
class CalibrationReport:
    precision_percent: float
    max_estimated_error_percent: float
    max_estimated_error_mm_per_100mm: float
    scale_factor: float
    pixels_per_mm_x: float
    pixels_per_mm_y: float
    pixels_per_mm_average: float
    distance_m: float

    def as_lines(self) -> list[str]:
        return [
            f"Precisao estimada: {self.precision_percent:.2f}%",
            f"Erro maximo estimado: {self.max_estimated_error_percent:.2f}%",
            f"Erro em 100 mm: {self.max_estimated_error_mm_per_100mm:.2f} mm",
            f"Escala aplicada: {self.scale_factor:.4f}",
            f"Pixels/mm X: {self.pixels_per_mm_x:.4f}",
            f"Pixels/mm Y: {self.pixels_per_mm_y:.4f}",
            f"Distancia: {self.distance_m:g} m",
        ]


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


def optotype_stroke_width_mm(distance_m: float, denominator_ft: float) -> float:
    return snellen_letter_height_mm(distance_m, denominator_ft) / 5


def optotype_stroke_width_px(calibration: DisplayCalibration, denominator_ft: float) -> int:
    return max(1, round(snellen_letter_height_px(calibration, denominator_ft) / 5))


def denominator_from_logmar(logmar: float) -> float:
    decimal_acuity = 10 ** (-logmar)
    if decimal_acuity <= 0:
        return 400.0
    return REFERENCE_SNELLEN_NUMERATOR_FT / decimal_acuity


def logmar_from_denominator(denominator_ft: float) -> float:
    decimal_acuity = REFERENCE_SNELLEN_NUMERATOR_FT / max(denominator_ft, 1.0)
    return -math.log10(decimal_acuity)


def etdrs_line_denominators() -> list[float]:
    return [denominator_from_logmar(logmar) for logmar in ETDRS_LOGMAR_LINES]


def etdrs_line_logmars() -> list[float]:
    return list(ETDRS_LOGMAR_LINES)


def format_snellen(denominator_ft: float) -> str:
    if denominator_ft.is_integer():
        return f"20/{int(denominator_ft)}"
    return f"20/{denominator_ft:g}"


def format_logmar(denominator_ft: float) -> str:
    return f"{logmar_from_denominator(denominator_ft):.2f} LogMAR"


def calibration_report(calibration: DisplayCalibration) -> CalibrationReport:
    axis_error = calibration.axis_difference_percent / 2
    quantization_error = 0.5 / max(calibration.mm_to_px(100), 1) * 100
    max_error = axis_error + quantization_error
    precision = max(0.0, min(100.0, 100.0 - max_error))
    return CalibrationReport(
        precision_percent=precision,
        max_estimated_error_percent=max_error,
        max_estimated_error_mm_per_100mm=max_error,
        scale_factor=calibration.scale_factor,
        pixels_per_mm_x=calibration.pixels_per_mm_x,
        pixels_per_mm_y=calibration.pixels_per_mm_y,
        pixels_per_mm_average=calibration.pixels_per_mm,
        distance_m=calibration.distance_m,
    )
