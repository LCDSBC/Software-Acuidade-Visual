from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.validation import build_validation_report, field_validation_from_dict


class RealEquipmentValidationTest(unittest.TestCase):
    def test_real_equipment_script_exists(self) -> None:
        script = ROOT / "Optotipos" / "teste_equipamento_real_windows.bat"
        content = script.read_text(encoding="utf-8")
        self.assertIn("validacao_campo.json", content)
        self.assertIn("validar_fase4_windows.bat", content)
        self.assertIn("Optotipos.exe", content)

    def test_field_model_contains_equipment_fields(self) -> None:
        model = json.loads((ROOT / "Optotipos" / "Dados" / "modelo_validacao_campo.json").read_text(encoding="utf-8"))
        for key in (
            "operator_name",
            "test_date",
            "computer_model",
            "os_version",
            "gpu_or_adapter",
            "monitor_model",
            "resolution",
            "connection_type",
            "room_lighting",
        ):
            self.assertIn(key, model)

    def test_report_includes_real_equipment_section(self) -> None:
        field = field_validation_from_dict(
            {
                "operator_name": "Dra. Teste",
                "test_date": "2026-06-16",
                "computer_model": "Mini PC",
                "os_version": "Windows 11",
                "gpu_or_adapter": "HDMI",
                "monitor_model": "TV 43",
                "resolution": "3840x2160",
                "connection_type": "HDMI direto",
                "room_lighting": "controlada",
                "configured_distance_m": 4,
                "ruler_100mm_measured_mm": 100,
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
            self.assertIn("Equipamento real testado", report)
            self.assertIn("Dra. Teste", report)
            self.assertIn("TV 43", report)
            self.assertIn("HDMI direto", report)

    def test_real_equipment_document_exists(self) -> None:
        document = ROOT / "Optotipos" / "Testes" / "TESTE_EQUIPAMENTO_REAL.md"
        content = document.read_text(encoding="utf-8")
        self.assertIn("Teste em equipamento real", content)
        self.assertIn("teste_equipamento_real_windows.bat", content)
        self.assertIn("regua fisica", content)


if __name__ == "__main__":
    unittest.main()
