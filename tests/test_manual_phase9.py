from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL_DIR = ROOT / "Optotipos" / "Manual"


class ManualPhase9Test(unittest.TestCase):
    def test_manual_files_exist(self) -> None:
        for name in ("README.md", "MANUAL_DE_USO.md", "GUIA_RAPIDO.md", "SOLUCAO_DE_PROBLEMAS.md"):
            with self.subTest(name=name):
                self.assertTrue((MANUAL_DIR / name).is_file())

    def test_main_manual_contains_core_workflows(self) -> None:
        content = (MANUAL_DIR / "MANUAL_DE_USO.md").read_text(encoding="utf-8")
        for topic in (
            "Configurador.exe",
            "Optotipos.exe",
            "Calibracao da tela",
            "Controle pelo celular",
            "Testes com ativos licenciados",
            "Relatorio de confianca clinica",
        ):
            with self.subTest(topic=topic):
                self.assertIn(topic, content)

    def test_quick_guide_contains_first_run_checklist(self) -> None:
        content = (MANUAL_DIR / "GUIA_RAPIDO.md").read_text(encoding="utf-8")
        self.assertIn("Primeira vez", content)
        self.assertIn("Distancia=4", content)
        self.assertIn("teste_equipamento_real_windows.bat", content)

    def test_troubleshooting_contains_common_failures(self) -> None:
        content = (MANUAL_DIR / "SOLUCAO_DE_PROBLEMAS.md").read_text(encoding="utf-8")
        for topic in (
            "Optotipos.exe nao abre",
            "Duas telas nao funciona",
            "Celular nao acessa Wireless",
            "confianca baixa",
        ):
            with self.subTest(topic=topic):
                self.assertIn(topic, content)

    def test_root_readme_links_phase9_manual(self) -> None:
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Fase 9 - Manual de uso", content)
        self.assertIn("Optotipos/Manual/MANUAL_DE_USO.md", content)


if __name__ == "__main__":
    unittest.main()
