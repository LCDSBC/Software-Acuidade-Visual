from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

try:
    from tkinter import Canvas
except ModuleNotFoundError:  # pragma: no cover - used only in headless test environments.
    Canvas = Any

from .calibration import (
    DisplayCalibration,
    SNELLEN_CLINICAL_DENOMINATORS,
    etdrs_line_denominators,
    etdrs_line_logmars,
    format_logmar,
    format_snellen,
    snellen_letter_height_px,
)
from .catalog import VisualTest


SNELLEN_DENOMINATORS = SNELLEN_CLINICAL_DENOMINATORS
ROTATIONS = (0, 90, 180, 270)
ETDRS_OPTOTYPES_PER_LINE = 5
OPTOTYPE_GRID = 5


@dataclass
class RenderState:
    denominator: float = 20
    randomize: bool = False
    single_line: bool = False
    occlusion: str = "none"
    contrast: float = 1.0
    seed: int = 1


@dataclass(frozen=True)
class RenderOptions:
    background: str = "white"
    foreground: str = "black"
    horizontal_mirror: bool = False
    vertical_mirror: bool = False
    rotation: int = 0
    filter_name: str = "Nenhum"


@dataclass(frozen=True)
class ClinicalLine:
    denominator: float
    logmar: float
    optotype_size_px: int
    stroke_width_px: int
    optotype_count: int
    letter_spacing_px: int
    row_spacing_px: int

    @property
    def total_width_px(self) -> int:
        return self.optotype_count * self.optotype_size_px + (self.optotype_count - 1) * self.letter_spacing_px


def clear(canvas: Canvas, background: str) -> None:
    canvas.delete("all")
    canvas.configure(background=background)


def render_test(
    canvas: Canvas,
    test: VisualTest,
    calibration: DisplayCalibration,
    state: RenderState,
    options: RenderOptions,
) -> None:
    width = max(canvas.winfo_width(), 800)
    height = max(canvas.winfo_height(), 600)
    clear(canvas, options.background)

    renderer = test.renderer
    if renderer in {"chart", "directional", "landolt", "shapes", "etdrs"}:
        draw_acuity_chart(canvas, width, height, test, calibration, state, options)
    elif renderer == "duochrome":
        draw_duochrome(canvas, width, height, calibration, state, options)
    elif renderer == "clock":
        draw_astigmatic_clock(canvas, width, height, state, options)
    elif renderer == "fan":
        draw_astigmatic_fan(canvas, width, height, options)
    elif renderer == "cross_cylinder":
        draw_cross_cylinder(canvas, width, height, options)
    elif renderer == "fogging":
        draw_fogging(canvas, width, height, options)
    elif renderer == "balance":
        draw_binocular_balance(canvas, width, height, options)
    elif renderer == "worth":
        draw_worth(canvas, width, height)
    elif renderer in {"vectogram", "fusion", "vergence", "fixation", "suppression"}:
        draw_binocular_pattern(canvas, width, height, test.name, options)
    elif renderer in {"stereo_circles", "randot", "fly", "stereo_shapes"}:
        draw_stereo(canvas, width, height, test.name, options)
    elif renderer in {"motility_h", "motility_points", "saccades", "pursuits"}:
        draw_motility(canvas, width, height, test.name, renderer, options)
    elif renderer == "contrast_letters":
        draw_contrast_letters(canvas, width, height)
    elif renderer == "contrast_levels":
        draw_contrast_levels(canvas, width, height)
    elif renderer == "sine_contrast":
        draw_sine_contrast(canvas, width, height)
    elif renderer in {"ishihara", "hrr"}:
        draw_color_plate(canvas, width, height, renderer)
    elif renderer in {"hue_tiles", "hue_tiles_large"}:
        draw_hue_tiles(canvas, width, height, large=renderer == "hue_tiles_large")
    elif renderer.startswith("filter_"):
        draw_filter(canvas, width, height, renderer)
    else:
        canvas.create_text(width / 2, height / 2, text=test.name, fill=options.foreground, font=("Arial", 64, "bold"))

    draw_overlay(canvas, width, height, test, calibration, state, options)


def draw_acuity_chart(
    canvas: Canvas,
    width: int,
    height: int,
    test: VisualTest,
    calibration: DisplayCalibration,
    state: RenderState,
    options: RenderOptions,
) -> None:
    denominators = [state.denominator] if state.single_line else list(etdrs_line_denominators() if test.renderer == "etdrs" else SNELLEN_DENOMINATORS)
    logmars = [0.0] if state.single_line else list(etdrs_line_logmars() if test.renderer == "etdrs" else [0.0] * len(denominators))
    usable_top = 76
    usable_height = height - 170
    rng = random.Random(state.seed)

    lines = [clinical_line(calibration, denominator, ETDRS_OPTOTYPES_PER_LINE if test.renderer == "etdrs" else min(8, index + 1)) for index, denominator in enumerate(denominators)]
    total_height = sum(line.optotype_size_px for line in lines) + sum(line.row_spacing_px for line in lines[:-1])
    scale = min(1.0, usable_height / max(total_height, 1))
    y = usable_top + max(0, usable_height - total_height * scale) / 2

    for index, (denominator, line) in enumerate(zip(denominators, lines)):
        size = max(8, round(line.optotype_size_px * scale))
        stroke = max(1, round(line.stroke_width_px * scale))
        row_spacing = max(10, round(line.row_spacing_px * scale))
        center_y = y + size / 2
        symbol_count = line.optotype_count
        symbols = choose_symbols(test.symbols, symbol_count, rng if state.randomize else None)
        spacing = etdrs_spacing_px(size) if test.renderer == "etdrs" else max(round(size * 0.6), stroke * 2)
        x_positions = centered_positions(width, symbol_count, size + spacing)
        for x, symbol in zip(x_positions, symbols):
            draw_symbol(canvas, x, center_y, size, stroke, symbol, test.renderer, options, rng)
        label = line_label(float(denominator), logmars[index] if index < len(logmars) else None, test.renderer)
        canvas.create_text(26, center_y, text=label, fill=options.foreground, anchor="w", font=("Arial", 14))
        y += size + row_spacing


def clinical_line(calibration: DisplayCalibration, denominator: float, optotype_count: int) -> ClinicalLine:
    size = snellen_letter_height_px(calibration, denominator)
    stroke = max(1, round(size / OPTOTYPE_GRID))
    return ClinicalLine(
        denominator=denominator,
        logmar=0.0 if denominator <= 0 else math.log10(denominator / 20),
        optotype_size_px=size,
        stroke_width_px=stroke,
        optotype_count=optotype_count,
        letter_spacing_px=size,
        row_spacing_px=size,
    )


def etdrs_spacing_px(size: int) -> int:
    return size


def line_label(denominator: float, logmar: float | None, renderer: str) -> str:
    if renderer == "etdrs" and logmar is not None:
        return f"{format_snellen(float(denominator))}  {logmar:.1f} LogMAR"
    return f"{format_snellen(float(denominator))}  {format_logmar(float(denominator))}"


def choose_symbols(symbols: tuple[str, ...], count: int, rng: random.Random | None) -> list[str]:
    if not symbols:
        return ["+"] * count
    if rng:
        return [rng.choice(symbols) for _ in range(count)]
    return [symbols[index % len(symbols)] for index in range(count)]


def centered_positions(width: int, count: int, spacing: float) -> list[float]:
    if count <= 1:
        return [width / 2]
    total = spacing * (count - 1)
    start = width / 2 - total / 2
    return [start + index * spacing for index in range(count)]


def transform_angle(options: RenderOptions, base_angle: int = 0) -> int:
    angle = (base_angle + options.rotation) % 360
    if options.horizontal_mirror:
        angle = (180 - angle) % 360
    if options.vertical_mirror:
        angle = (-angle) % 360
    return angle


def draw_symbol(
    canvas: Canvas,
    x: float,
    y: float,
    size: int,
    stroke: int,
    symbol: str,
    renderer: str,
    options: RenderOptions,
    rng: random.Random,
) -> None:
    if renderer == "directional":
        angle = transform_angle(options, rng.choice(ROTATIONS))
        draw_grid_optotype(canvas, x, y, size, stroke, "E", options.foreground, angle)
    elif renderer == "landolt":
        draw_landolt_c(canvas, x, y, size, stroke, transform_angle(options, rng.choice(ROTATIONS)), options.foreground)
    elif renderer == "shapes":
        draw_shape(canvas, x, y, size, symbol, options.foreground)
    else:
        draw_grid_optotype(canvas, x, y, size, stroke, symbol, options.foreground, options.rotation)


def draw_grid_optotype(canvas: Canvas, x: float, y: float, size: int, stroke: int, symbol: str, color: str, angle: int = 0) -> None:
    symbol = symbol.upper()
    if symbol == "E":
        draw_cell_pattern(canvas, x, y, size, e_pattern_cells(), color, angle)
    elif symbol in {"C", "D", "H", "O", "S"}:
        draw_cell_pattern(canvas, x, y, size, block_letter_cells(symbol), color, angle)
    elif symbol in {"K", "N", "R", "V", "Z"}:
        draw_stroked_letter(canvas, x, y, size, stroke, symbol, color, angle)
    else:
        draw_cell_pattern(canvas, x, y, size, block_letter_cells("O"), color, angle)


def e_pattern_cells() -> set[tuple[int, int]]:
    return {(0, row) for row in range(5)} | {(col, 0) for col in range(5)} | {(col, 2) for col in range(5)} | {(col, 4) for col in range(5)}


def block_letter_cells(symbol: str) -> set[tuple[int, int]]:
    if symbol == "C":
        return {(col, 0) for col in range(1, 5)} | {(0, row) for row in range(5)} | {(col, 4) for col in range(1, 5)}
    if symbol == "D":
        return {(0, row) for row in range(5)} | {(col, 0) for col in range(4)} | {(col, 4) for col in range(4)} | {(4, row) for row in range(1, 4)}
    if symbol == "H":
        return {(0, row) for row in range(5)} | {(4, row) for row in range(5)} | {(col, 2) for col in range(5)}
    if symbol == "S":
        return {(col, 0) for col in range(5)} | {(0, 1), (0, 2)} | {(col, 2) for col in range(5)} | {(4, 2), (4, 3)} | {(col, 4) for col in range(5)}
    return {(col, 0) for col in range(5)} | {(col, 4) for col in range(5)} | {(0, row) for row in range(5)} | {(4, row) for row in range(5)}


def draw_cell_pattern(canvas: Canvas, x: float, y: float, size: int, cells: set[tuple[int, int]], color: str, angle: int = 0) -> None:
    cell = size / OPTOTYPE_GRID
    for col, row in cells:
        points = rotated_cell_points(x, y, size, col, row, angle)
        canvas.create_polygon(*points, fill=color, outline=color)


def rotated_cell_points(x: float, y: float, size: int, col: int, row: int, angle: int) -> list[float]:
    cell = size / OPTOTYPE_GRID
    left = -size / 2 + col * cell
    top = -size / 2 + row * cell
    points = ((left, top), (left + cell, top), (left + cell, top + cell), (left, top + cell))
    rotated: list[float] = []
    radians = math.radians(angle % 360)
    cos_a = math.cos(radians)
    sin_a = math.sin(radians)
    for px, py in points:
        rotated.extend((x + px * cos_a - py * sin_a, y + px * sin_a + py * cos_a))
    return rotated


def draw_stroked_letter(canvas: Canvas, x: float, y: float, size: int, stroke: int, symbol: str, color: str, angle: int = 0) -> None:
    half = size / 2
    cell = size / OPTOTYPE_GRID
    segments = {
        "K": [(-half + cell / 2, -half, -half + cell / 2, half), (-half + cell, 0, half, -half), (-half + cell, 0, half, half)],
        "N": [(-half + cell / 2, -half, -half + cell / 2, half), (half - cell / 2, -half, half - cell / 2, half), (-half + cell, -half, half - cell, half)],
        "R": [(-half + cell / 2, -half, -half + cell / 2, half), (-half, -half + cell / 2, half - cell, -half + cell / 2), (half - cell / 2, -half + cell, half - cell / 2, 0), (-half, cell / 2, half - cell, cell / 2), (-half + cell, cell / 2, half, half)],
        "V": [(-half + cell / 2, -half, 0, half), (half - cell / 2, -half, 0, half)],
        "Z": [(-half, -half + cell / 2, half, -half + cell / 2), (half - cell / 2, -half + cell, -half + cell / 2, half - cell), (-half, half - cell / 2, half, half - cell / 2)],
    }.get(symbol, [])
    for x1, y1, x2, y2 in segments:
        rx1, ry1 = rotate_point(x1, y1, angle)
        rx2, ry2 = rotate_point(x2, y2, angle)
        canvas.create_line(x + rx1, y + ry1, x + rx2, y + ry2, fill=color, width=stroke, capstyle="projecting", joinstyle="miter")


def rotate_point(px: float, py: float, angle: int) -> tuple[float, float]:
    radians = math.radians(angle % 360)
    return (px * math.cos(radians) - py * math.sin(radians), px * math.sin(radians) + py * math.cos(radians))


def landolt_gap_px(size: int) -> int:
    return max(1, round(size / OPTOTYPE_GRID))


def draw_landolt_c(canvas: Canvas, x: float, y: float, size: int, stroke: int, angle: int, color: str) -> None:
    radius = size / 2 - stroke / 2
    thickness = max(1, stroke)
    canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=color, width=thickness)
    gap = landolt_gap_px(size)
    if angle == 0:
        coords = (x + radius - thickness, y - gap / 2, x + radius + thickness * 2, y + gap / 2)
    elif angle == 90:
        coords = (x - gap / 2, y - radius - thickness * 2, x + gap / 2, y - radius + thickness)
    elif angle == 180:
        coords = (x - radius - thickness * 2, y - gap / 2, x - radius + thickness, y + gap / 2)
    else:
        coords = (x - gap / 2, y + radius - thickness, x + gap / 2, y + radius + thickness * 2)
    canvas.create_rectangle(*coords, fill=canvas["background"], outline=canvas["background"])


def draw_shape(canvas: Canvas, x: float, y: float, size: int, symbol: str, color: str) -> None:
    r = size * 0.35
    if symbol in {"circle", "apple"}:
        canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, width=max(4, size // 12))
        if symbol == "apple":
            canvas.create_line(x, y - r, x + r * 0.2, y - r * 1.35, fill=color, width=max(3, size // 18))
    elif symbol in {"square", "cake"}:
        canvas.create_rectangle(x - r, y - r, x + r, y + r, outline=color, width=max(4, size // 12))
        if symbol == "cake":
            canvas.create_line(x - r, y, x + r, y, fill=color, width=max(3, size // 18))
    elif symbol == "house":
        canvas.create_polygon(x - r, y, x, y - r, x + r, y, outline=color, fill="", width=max(4, size // 12))
        canvas.create_rectangle(x - r * 0.8, y, x + r * 0.8, y + r, outline=color, width=max(4, size // 12))
    elif symbol == "hand":
        canvas.create_text(x, y, text="5", fill=color, font=("Arial", size, "bold"))
    elif symbol == "horse":
        canvas.create_text(x, y, text="H", fill=color, font=("Arial", size, "bold"))
    elif symbol == "phone":
        canvas.create_rectangle(x - r, y - r, x + r, y + r, outline=color, width=max(4, size // 12))
        canvas.create_oval(x - r * 0.2, y + r * 0.65, x + r * 0.2, y + r * 0.9, fill=color, outline=color)
    else:
        canvas.create_text(x, y, text="?", fill=color, font=("Arial", size, "bold"))


def draw_duochrome(canvas: Canvas, width: int, height: int, calibration: DisplayCalibration, state: RenderState, options: RenderOptions) -> None:
    canvas.create_rectangle(0, 0, width / 2, height, fill="#b90000", outline="")
    canvas.create_rectangle(width / 2, 0, width, height, fill="#00843d", outline="")
    canvas.create_line(width / 2, 0, width / 2, height, fill="black", width=2)
    size = min(snellen_letter_height_px(calibration, state.denominator or 30), round(height * 0.28))
    stroke = max(1, round(size / OPTOTYPE_GRID))
    for x, label in ((width * 0.25, "VERMELHO"), (width * 0.75, "VERDE")):
        canvas.create_text(x, height * 0.18, text=label, fill="white", font=("Arial", 28, "bold"))
    for x_offset in (0, width / 2):
        positions = centered_positions(width / 2, 4, size * 1.45)
        for x, symbol in zip([position + x_offset for position in positions], ("O", "C", "D", "K")):
            draw_grid_optotype(canvas, x, height * 0.55, size, stroke, symbol, "white", 0)


def draw_astigmatic_clock(canvas: Canvas, width: int, height: int, state: RenderState, options: RenderOptions) -> None:
    cx, cy = width / 2, height / 2
    radius = min(width, height) * 0.34
    line_color = contrast_color(options.foreground, state.contrast)
    for degree in range(0, 180, 10):
        angle = math.radians(degree)
        x1, y1 = cx + math.cos(angle) * radius * 0.18, cy + math.sin(angle) * radius * 0.18
        x2, y2 = cx + math.cos(angle) * radius, cy + math.sin(angle) * radius
        x3, y3 = cx - math.cos(angle) * radius * 0.18, cy - math.sin(angle) * radius * 0.18
        x4, y4 = cx - math.cos(angle) * radius, cy - math.sin(angle) * radius
        canvas.create_line(x3, y3, x4, y4, fill=line_color, width=4)
        canvas.create_line(x1, y1, x2, y2, fill=line_color, width=4)
        if degree % 30 == 0:
            tx, ty = cx + math.cos(angle) * radius * 1.15, cy + math.sin(angle) * radius * 1.15
            canvas.create_text(tx, ty, text=str(degree), fill=options.foreground, font=("Arial", 18, "bold"))
    canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill=options.foreground, outline="")


def contrast_color(base: str, contrast: float) -> str:
    contrast = max(0.05, min(1.0, contrast))
    if base == "white":
        value = round(255 * contrast)
    else:
        value = round(255 * (1 - contrast))
    return f"#{value:02x}{value:02x}{value:02x}"


def draw_astigmatic_fan(canvas: Canvas, width: int, height: int, options: RenderOptions) -> None:
    cx, cy = width / 2, height * 0.72
    radius = min(width, height) * 0.58
    for degree in range(20, 161, 10):
        angle = math.radians(180 + degree)
        canvas.create_line(cx, cy, cx + math.cos(angle) * radius, cy + math.sin(angle) * radius, fill=options.foreground, width=4)
    canvas.create_text(cx, height * 0.14, text="Ventilador Astigmatico", fill=options.foreground, font=("Arial", 34, "bold"))


def draw_cross_cylinder(canvas: Canvas, width: int, height: int, options: RenderOptions) -> None:
    cx, cy = width / 2, height / 2
    size = min(width, height) * 0.55
    for offset in range(-6, 7):
        x = cx + offset * size / 12
        canvas.create_line(x, cy - size / 2, x, cy + size / 2, fill=options.foreground, width=2)
        y = cy + offset * size / 12
        canvas.create_line(cx - size / 2, y, cx + size / 2, y, fill=options.foreground, width=2)
    canvas.create_line(cx - size / 2, cy, cx + size / 2, cy, fill=options.foreground, width=6)
    canvas.create_line(cx, cy - size / 2, cx, cy + size / 2, fill=options.foreground, width=6)


def draw_fogging(canvas: Canvas, width: int, height: int, options: RenderOptions) -> None:
    for i, text in enumerate(("N", "H", "R", "V", "K")):
        gray = 80 + i * 28
        color = f"#{gray:02x}{gray:02x}{gray:02x}"
        canvas.create_text(width * (0.22 + i * 0.14), height / 2, text=text, fill=color, font=("Arial", 92, "bold"))
    canvas.create_text(width / 2, height * 0.2, text="Nevoa Refrativa", fill=options.foreground, font=("Arial", 30, "bold"))


def draw_binocular_balance(canvas: Canvas, width: int, height: int, options: RenderOptions) -> None:
    canvas.create_text(width * 0.3, height / 2, text="O D K", fill="#d02020", font=("Arial", 74, "bold"))
    canvas.create_text(width * 0.7, height / 2, text="V R S", fill="#2040d0", font=("Arial", 74, "bold"))
    canvas.create_line(width / 2, height * 0.2, width / 2, height * 0.8, fill=options.foreground, width=3)


def draw_worth(canvas: Canvas, width: int, height: int) -> None:
    cx, cy = width / 2, height / 2
    r = min(width, height) * 0.08
    points = ((cx, cy - r * 2.8, "#d00000"), (cx - r * 2.2, cy, "#00a000"), (cx + r * 2.2, cy, "#00a000"), (cx, cy + r * 2.6, "#ffffff"))
    for x, y, color in points:
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="black", width=4)


def draw_binocular_pattern(canvas: Canvas, width: int, height: int, title: str, options: RenderOptions) -> None:
    cx, cy = width / 2, height / 2
    canvas.create_text(cx, height * 0.14, text=title, fill=options.foreground, font=("Arial", 34, "bold"))
    for shift, color in ((-35, "#d02020"), (35, "#2080d0")):
        canvas.create_rectangle(cx - 220 + shift, cy - 130, cx + 220 + shift, cy + 130, outline=color, width=7)
        canvas.create_oval(cx - 90 + shift, cy - 70, cx + 90 + shift, cy + 70, outline=color, width=6)
    canvas.create_line(cx - 280, cy, cx + 280, cy, fill=options.foreground, width=2, dash=(8, 8))


def draw_stereo(canvas: Canvas, width: int, height: int, title: str, options: RenderOptions) -> None:
    canvas.create_text(width / 2, height * 0.12, text=title, fill=options.foreground, font=("Arial", 34, "bold"))
    rng = random.Random(42)
    for index in range(90):
        x = rng.randint(int(width * 0.18), int(width * 0.82))
        y = rng.randint(int(height * 0.24), int(height * 0.82))
        r = rng.randint(3, 8)
        color = "#555555" if index % 2 else "#999999"
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
    for ring in range(4):
        r = 45 + ring * 34
        canvas.create_oval(width / 2 - r, height / 2 - r, width / 2 + r, height / 2 + r, outline=options.foreground, width=4)


def draw_motility(canvas: Canvas, width: int, height: int, title: str, renderer: str, options: RenderOptions) -> None:
    canvas.create_text(width / 2, height * 0.1, text=title, fill=options.foreground, font=("Arial", 34, "bold"))
    cx, cy = width / 2, height / 2
    if renderer == "motility_h":
        points = [(width * 0.25, height * 0.25), (width * 0.25, height * 0.75), (width * 0.5, height * 0.5), (width * 0.75, height * 0.25), (width * 0.75, height * 0.75)]
        canvas.create_line(*sum(([x, y] for x, y in points), []), fill=options.foreground, width=4)
    elif renderer == "saccades":
        for x in (width * 0.25, width * 0.5, width * 0.75):
            canvas.create_oval(x - 22, cy - 22, x + 22, cy + 22, fill=options.foreground, outline="")
    else:
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x = cx + math.cos(rad) * width * 0.25
            y = cy + math.sin(rad) * height * 0.25
            canvas.create_line(cx, cy, x, y, fill=options.foreground, width=2)
            canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill=options.foreground, outline="")


def draw_contrast_letters(canvas: Canvas, width: int, height: int) -> None:
    letters = ("P", "E", "L", "L", "I", "R", "O", "B", "S", "O", "N")
    for index, letter in enumerate(letters):
        shade = 20 + index * 18
        color = f"#{shade:02x}{shade:02x}{shade:02x}"
        canvas.create_text(width * (0.12 + index * 0.075), height / 2, text=letter, fill=color, font=("Arial", 68, "bold"))


def draw_contrast_levels(canvas: Canvas, width: int, height: int) -> None:
    for index in range(10):
        shade = int(255 - index * 22)
        color = f"#{shade:02x}{shade:02x}{shade:02x}"
        x1 = width * 0.12 + index * width * 0.075
        canvas.create_rectangle(x1, height * 0.3, x1 + width * 0.06, height * 0.7, fill=color, outline="black")


def draw_sine_contrast(canvas: Canvas, width: int, height: int) -> None:
    for x in range(0, width, 4):
        value = int(127 + 110 * math.sin(x / width * math.pi * 18))
        color = f"#{value:02x}{value:02x}{value:02x}"
        canvas.create_rectangle(x, height * 0.25, x + 4, height * 0.75, fill=color, outline="")


def draw_color_plate(canvas: Canvas, width: int, height: int, renderer: str) -> None:
    rng = random.Random(7 if renderer == "ishihara" else 9)
    cx, cy = width / 2, height / 2
    radius = min(width, height) * 0.34
    for _ in range(300):
        angle = rng.random() * math.tau
        distance = radius * math.sqrt(rng.random())
        x = cx + math.cos(angle) * distance
        y = cy + math.sin(angle) * distance
        r = rng.randint(5, 14)
        color = rng.choice(("#b65a3c", "#d98e53", "#8aaa62", "#7f9a4b", "#c77964"))
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
    canvas.create_text(cx, cy, text="12" if renderer == "ishihara" else "X", fill="#476b38", font=("Arial", int(radius * 0.75), "bold"))


def draw_hue_tiles(canvas: Canvas, width: int, height: int, large: bool = False) -> None:
    count = 32 if large else 15
    tile_w = width * 0.75 / count
    for index in range(count):
        hue = index / count
        r, g, b = hsv_to_rgb(hue, 0.65, 0.9)
        x1 = width * 0.125 + index * tile_w
        canvas.create_rectangle(x1, height * 0.42, x1 + tile_w - 2, height * 0.58, fill=f"#{r:02x}{g:02x}{b:02x}", outline="black")


def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    values = ((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))[i % 6]
    return tuple(int(channel * 255) for channel in values)


def draw_filter(canvas: Canvas, width: int, height: int, renderer: str) -> None:
    colors = {
        "filter_red": "#b00000",
        "filter_green": "#008000",
        "filter_blue": "#0030a0",
        "filter_polarized": "#dddddd",
        "filter_anaglyph": "#6a2fb8",
    }
    color = colors.get(renderer, "#ffffff")
    canvas.create_rectangle(0, 0, width, height, fill=color, outline="")
    canvas.create_text(width / 2, height / 2, text=renderer.replace("filter_", "Filtro ").title(), fill="white" if renderer != "filter_polarized" else "black", font=("Arial", 64, "bold"))


def draw_overlay(
    canvas: Canvas,
    width: int,
    height: int,
    test: VisualTest,
    calibration: DisplayCalibration,
    state: RenderState,
    options: RenderOptions,
) -> None:
    canvas.create_text(width / 2, 28, text=test.name, fill=options.foreground, font=("Arial", 20, "bold"))
    info = f"Distancia {calibration.distance_m:g} m | Escala {calibration.scale_factor:.4f} | {format_snellen(float(state.denominator))}"
    canvas.create_text(width / 2, height - 26, text=info, fill=options.foreground, font=("Arial", 14))
    if state.occlusion == "left":
        canvas.create_rectangle(0, 0, width / 2, height, fill=options.background, outline="")
    elif state.occlusion == "right":
        canvas.create_rectangle(width / 2, 0, width, height, fill=options.background, outline="")
    filter_name = options.filter_name.lower()
    if filter_name in {"vermelho", "verde", "azul"}:
        color = {"vermelho": "#ff0000", "verde": "#00aa00", "azul": "#0040ff"}[filter_name]
        canvas.create_rectangle(0, 0, width, height, fill=color, outline="", stipple="gray50")
