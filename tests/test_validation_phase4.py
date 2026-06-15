from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.config import load_config
from optotipos_core.validation import (
    build_validation_report,
    expected_20_20_measurements,
    measurement_result,
    portable_status,
    write_validation_report,
)


class Phase4ValidationTest(unittest.TestCase):
    def test_expected_20_20_measurements_for_field_distances(self) -> None:
        measurements = expected_20_20_measurements()
        self.assertEqual([item.distance_m for item in measurements], [4.0, 5.0, 6.0])
        self.assertAlmostEqual(measurements[0].expected_height_mm, 5.8178, places=3)
        self.assertAlmostEqual(measurements[1].expected_height_mm, 7.2722, places=3)
        self.assertAlmostEqual(measurements[2].expected_height_mm, 8.7266, places=3)
        self.assertAlmostEqual(measurements[0].expected_stroke_mm, measurements[0].expected_height_mm / 5)

    def test_measurement_result_flags_pass_and_fail(self) -> None:
        passed = measurement_result("20/20 4m", 5.8178, 5.86)
        failed = measurement_result("20/20 4m", 5.8178, 6.5)
        self.assertTrue(passed.passed)
        self.assertFalse(failed.passed)
        self.assertGreater(failed.error_percent, 2)

    def test_portable_status_detects_missing_executables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            load_config(root)
            status = portable_status(root)
            self.assertFalse(status.optotipos_exe_exists)
            self.assertFalse(status.configurador_exe_exists)
            self.assertTrue(status.config_files_ok)
            self.assertFalse(status.ready_for_windows_trial)

    def test_validation_report_contains_phase4_checklist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = build_validation_report(root=root)
            self.assertIn("Relatorio de Validacao Clinica - Fase 4", report)
            self.assertIn("Optotipo 20/20 a 4 m", report)
            self.assertIn("TelaUnica", report)
            self.assertIn("controle por celular", report)

    def test_write_validation_report_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "Logs" / "ValidacaoClinica_Fase4.md"
            write_validation_report(destination, root=Path(directory))
            self.assertTrue(destination.exists())
            self.assertIn("Tamanho esperado do optotipo 20/20", destination.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
