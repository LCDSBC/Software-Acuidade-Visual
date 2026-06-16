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
    evaluate_clinical_confidence,
    expected_20_20_measurements,
    field_validation_from_dict,
    load_field_validation,
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
            self.assertIn("Validacao matematica dos optotipos", report)
            self.assertIn("TelaUnica", report)
            self.assertIn("controle por celular", report)

    def test_write_validation_report_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "Logs" / "ValidacaoClinica_Fase4.md"
            write_validation_report(destination, root=Path(directory))
            self.assertTrue(destination.exists())
            self.assertIn("Tamanho esperado do optotipo 20/20", destination.read_text(encoding="utf-8"))

    def test_clinical_confidence_is_pending_without_field_data(self) -> None:
        confidence = evaluate_clinical_confidence(None)
        self.assertEqual(confidence.score_percent, 0)
        self.assertFalse(confidence.approved_for_clinic_trial)
        self.assertIn("PENDENTE", confidence.level)

    def test_clinical_confidence_is_high_when_measurements_and_checks_pass(self) -> None:
        field = field_validation_from_dict(
            {
                "monitor_model": "TV teste",
                "resolution": "3840x2160",
                "configured_distance_m": 4,
                "ruler_100mm_measured_mm": 100.1,
                "optotype_20_20_4m_measured_mm": 5.82,
                "checks": {
                    "executaveis_abrem_sem_python": True,
                    "pacote_portatil_copiado": True,
                    "tela_unica_funciona": True,
                    "duas_telas_funciona": True,
                    "espelhamento_funciona": True,
                    "controle_celular_funciona": True,
                    "configuracoes_persistem": True,
                },
            }
        )
        confidence = evaluate_clinical_confidence(field)
        self.assertEqual(confidence.level, "ALTA")
        self.assertTrue(confidence.approved_for_clinic_trial)
        self.assertGreaterEqual(confidence.score_percent, 90)

    def test_clinical_confidence_blocks_large_physical_error(self) -> None:
        field = field_validation_from_dict(
            {
                "ruler_100mm_measured_mm": 108,
                "optotype_20_20_4m_measured_mm": 7,
                "checks": {
                    "executaveis_abrem_sem_python": True,
                    "tela_unica_funciona": True,
                },
            }
        )
        confidence = evaluate_clinical_confidence(field)
        self.assertFalse(confidence.approved_for_clinic_trial)
        self.assertIn("erro fisico", " ".join(confidence.blockers))

    def test_field_validation_can_be_loaded_from_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campo.json"
            path.write_text(
                """{
                  "monitor_model": "Monitor",
                  "resolution": "1920x1080",
                  "configured_distance_m": 4,
                  "ruler_100mm_measured_mm": 100,
                  "checks": {"tela_unica_funciona": true}
                }""",
                encoding="utf-8",
            )
            field = load_field_validation(path)
            self.assertEqual(field.monitor_model, "Monitor")
            self.assertTrue(field.checks["tela_unica_funciona"])

    def test_validation_report_includes_confidence_with_field_data(self) -> None:
        field = field_validation_from_dict(
            {
                "ruler_100mm_measured_mm": 100.0,
                "optotype_20_20_4m_measured_mm": 5.8178,
                "checks": {
                    "executaveis_abrem_sem_python": True,
                    "pacote_portatil_copiado": True,
                    "tela_unica_funciona": True,
                    "duas_telas_funciona": True,
                    "espelhamento_funciona": True,
                    "controle_celular_funciona": True,
                    "configuracoes_persistem": True,
                },
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            report = build_validation_report(root=Path(directory), field_validation=field)
            self.assertIn("Confianca clinica", report)
            self.assertIn("Aprovado para piloto em consultorio", report)
            self.assertIn("Regua virtual 100 mm", report)


if __name__ == "__main__":
    unittest.main()
