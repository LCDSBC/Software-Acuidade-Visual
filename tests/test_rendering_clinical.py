from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.calibration import DisplayCalibration, etdrs_line_denominators, etdrs_line_logmars
from optotipos_core.catalog import TESTS, test_by_key
from optotipos_core.rendering import (
    ETDRS_OPTOTYPES_PER_LINE,
    SNELLEN_DENOMINATORS,
    RenderOptions,
    RenderState,
    block_letter_cells,
    clinical_line,
    contrast_color,
    draw_astigmatic_clock,
    draw_asset_backed_test,
    draw_landolt_c,
    draw_hue_tiles,
    draw_symbol,
    e_pattern_cells,
    etdrs_spacing_px,
    landolt_gap_px,
    pelli_gray_from_log_contrast,
    pelli_robson_triplets,
    render_test,
    rotate_point,
    rotated_cell_points,
    transform_angle,
)


class FakeCanvas:
    def __init__(self, width: int = 1920, height: int = 1080) -> None:
        self.width = width
        self.height = height
        self.background = "white"
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def winfo_width(self) -> int:
        return self.width

    def winfo_height(self) -> int:
        return self.height

    def winfo_exists(self) -> bool:
        return True

    def __getitem__(self, key: str) -> str:
        if key == "background":
            return self.background
        raise KeyError(key)

    def configure(self, **kwargs: object) -> None:
        if "background" in kwargs:
            self.background = str(kwargs["background"])
        self.calls.append(("configure", tuple(), kwargs))

    def delete(self, *args: object) -> None:
        self.calls.append(("delete", args, {}))

    def create_polygon(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("polygon", args, kwargs))

    def create_rectangle(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("rectangle", args, kwargs))

    def create_text(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("text", args, kwargs))

    def create_line(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("line", args, kwargs))

    def create_oval(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("oval", args, kwargs))


class ClinicalRenderingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.calibration = DisplayCalibration(
            distance_m=4,
            screen_width_mm=597,
            screen_height_mm=336,
            resolution_width=1920,
            resolution_height=1080,
            scale_factor=1.0,
        )

    def test_snellen_required_lines_are_present(self) -> None:
        self.assertEqual(SNELLEN_DENOMINATORS, (400, 300, 200, 100, 80, 60, 50, 40, 30, 25, 20, 15, 10))

    def test_clinical_line_uses_five_by_five_stroke(self) -> None:
        line = clinical_line(self.calibration, 20, 5)
        self.assertEqual(line.stroke_width_px, round(line.optotype_size_px / 5))
        self.assertEqual(line.letter_spacing_px, line.optotype_size_px)
        self.assertEqual(line.row_spacing_px, line.optotype_size_px)

    def test_etdrs_progression_has_five_letters_and_log_steps(self) -> None:
        logmars = etdrs_line_logmars()
        denominators = etdrs_line_denominators()
        self.assertEqual(len(logmars), len(denominators))
        self.assertEqual(round(logmars[0] - logmars[1], 1), 0.1)
        self.assertEqual(ETDRS_OPTOTYPES_PER_LINE, 5)
        self.assertEqual(etdrs_spacing_px(120), 120)

    def test_tumbling_e_uses_rotatable_five_by_five_pattern(self) -> None:
        cells = e_pattern_cells()
        self.assertIn((0, 0), cells)
        self.assertIn((4, 4), cells)
        canvas = FakeCanvas()
        draw_symbol(canvas, 100, 100, 100, 20, "E", "directional", RenderOptions(), random.Random(3))
        self.assertGreaterEqual(len([call for call in canvas.calls if call[0] == "polygon"]), len(cells))

    def test_landolt_c_gap_is_one_fifth_of_size(self) -> None:
        self.assertEqual(landolt_gap_px(100), 20)

    def test_block_snellen_letters_have_five_by_five_bounds(self) -> None:
        for symbol in ("C", "D", "H", "O", "S"):
            cells = block_letter_cells(symbol)
            self.assertTrue(all(0 <= col <= 4 and 0 <= row <= 4 for col, row in cells))

    def test_duochrome_draws_red_green_halves_and_calibrated_letters(self) -> None:
        canvas = FakeCanvas()
        render_test(canvas, test_by_key("duochrome"), self.calibration, RenderState(denominator=30), RenderOptions())
        rectangles = [call for call in canvas.calls if call[0] == "rectangle"]
        polygons = [call for call in canvas.calls if call[0] == "polygon"]
        self.assertGreaterEqual(len(rectangles), 2)
        self.assertGreater(len(polygons), 0)

    def test_pelli_robson_has_descending_triplet_contrast(self) -> None:
        triplets = pelli_robson_triplets()
        self.assertEqual(len(triplets), 24)
        self.assertGreater(triplets[0][1], triplets[-1][1])
        self.assertLess(pelli_gray_from_log_contrast(triplets[0][1]), pelli_gray_from_log_contrast(triplets[-1][1]))

    def test_farnsworth_d15_and_100_hue_draw_ordered_tiles(self) -> None:
        d15 = FakeCanvas()
        draw_hue_tiles(d15, 1200, 800, large=False)
        self.assertEqual(len([call for call in d15.calls if call[0] == "rectangle"]), 15)
        hue100 = FakeCanvas()
        draw_hue_tiles(hue100, 1600, 900, large=True)
        self.assertEqual(len([call for call in hue100.calls if call[0] == "rectangle"]), 85)

    def test_licensed_asset_missing_draws_clinical_block_notice(self) -> None:
        canvas = FakeCanvas()
        draw_asset_backed_test(canvas, 1280, 720, "ishihara", "Ishihara", RenderOptions())
        texts = [call for call in canvas.calls if call[0] == "text"]
        self.assertTrue(any("USO CLINICO BLOQUEADO" in str(call[2].get("text", "")) for call in texts))

    def test_render_all_registered_tests_without_gui(self) -> None:
        for test in TESTS:
            canvas = FakeCanvas(1280, 720)
            with self.subTest(test=test.key):
                render_test(
                    canvas,
                    test,
                    self.calibration,
                    RenderState(denominator=30, randomize=True, seed=5),
                    RenderOptions(filter_name="Vermelho"),
                )
                self.assertGreater(len(canvas.calls), 2)

    def test_astigmatic_clock_has_uniform_full_180_degree_lines(self) -> None:
        canvas = FakeCanvas()
        draw_astigmatic_clock(canvas, 1000, 800, RenderState(contrast=1.0), RenderOptions())
        lines = [call for call in canvas.calls if call[0] == "line"]
        self.assertEqual(len(lines), 36)
        self.assertTrue(all(call[2].get("width") == 4 for call in lines))

    def test_transform_angle_applies_mirrors_and_rotation(self) -> None:
        options = RenderOptions(horizontal_mirror=True, vertical_mirror=False, rotation=90)
        self.assertEqual(transform_angle(options, 0), 90)
        vertical = RenderOptions(horizontal_mirror=False, vertical_mirror=True, rotation=0)
        self.assertEqual(transform_angle(vertical, 90), 270)

    def test_contrast_color_stays_in_gray_scale(self) -> None:
        self.assertEqual(contrast_color("black", 1.0), "#000000")
        self.assertEqual(contrast_color("white", 1.0), "#ffffff")

    def test_landolt_all_gap_orientations_draw_mask(self) -> None:
        for angle in (0, 90, 180, 270):
            canvas = FakeCanvas()
            draw_landolt_c(canvas, 100, 100, 100, 20, angle, "black")
            self.assertEqual(len([call for call in canvas.calls if call[0] == "oval"]), 1)
            self.assertEqual(len([call for call in canvas.calls if call[0] == "rectangle"]), 1)

    def test_rotation_helpers_preserve_centered_geometry(self) -> None:
        points = rotated_cell_points(50, 50, 100, 0, 0, 90)
        self.assertEqual(len(points), 8)
        self.assertAlmostEqual(rotate_point(10, 0, 90)[0], 0, places=6)
        self.assertAlmostEqual(rotate_point(10, 0, 90)[1], 10, places=6)

    def test_horizontal_mirror_reflects_cell_geometry(self) -> None:
        normal = rotated_cell_points(50, 50, 100, 0, 0, 0)
        mirrored = rotated_cell_points(50, 50, 100, 0, 0, 0, mirror_x=True)
        normal_x = normal[0::2]
        mirrored_x = mirrored[0::2]
        self.assertEqual(sorted(round(x, 6) for x in mirrored_x), sorted(round(100 - x, 6) for x in normal_x))

    def test_vertical_mirror_reflects_cell_geometry(self) -> None:
        normal = rotated_cell_points(50, 50, 100, 0, 0, 0)
        mirrored = rotated_cell_points(50, 50, 100, 0, 0, 0, mirror_y=True)
        normal_y = normal[1::2]
        mirrored_y = mirrored[1::2]
        self.assertEqual(sorted(round(y, 6) for y in mirrored_y), sorted(round(100 - y, 6) for y in normal_y))

    def test_rotate_point_supports_mirror_effect(self) -> None:
        self.assertEqual(rotate_point(10, 5, 0, mirror_x=True), (-10.0, 5.0))
        self.assertEqual(rotate_point(10, 5, 0, mirror_y=True), (10.0, -5.0))


if __name__ == "__main__":
    unittest.main()
