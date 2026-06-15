from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPTOTIPOS = ROOT / "Optotipos"


class Phase1FoundationTest(unittest.TestCase):
    def test_required_portable_directories_exist(self) -> None:
        required = ("Configuracoes", "Perfis", "Testes", "Dados", "Backup", "Logs", "Aplicacao")
        for directory in required:
            with self.subTest(directory=directory):
                self.assertTrue((OPTOTIPOS / directory).is_dir())

    def test_required_configuration_files_exist(self) -> None:
        required = (
            "Tela.txt",
            "Distancia.txt",
            "Escala.txt",
            "Inversao.txt",
            "Monitores.txt",
            "Exibicao.txt",
            "Atalhos.txt",
        )
        for file_name in required:
            with self.subTest(file_name=file_name):
                self.assertTrue((OPTOTIPOS / "Configuracoes" / file_name).is_file())

    def test_default_distance_is_clinically_valid(self) -> None:
        content = (OPTOTIPOS / "Configuracoes" / "Distancia.txt").read_text(encoding="utf-8")
        self.assertIn("Distancia=4", content)
        self.assertIn("Unidade=m", content)
        self.assertNotIn("Unidade=mm", content)

    def test_independent_entry_points_exist(self) -> None:
        self.assertTrue((ROOT / "Configurador" / "Configurador.pyw").is_file())
        self.assertTrue((OPTOTIPOS / "Optotipos.pyw").is_file())
        self.assertTrue((OPTOTIPOS / "Configurador.pyw").is_file())

    def test_windows_build_script_exists(self) -> None:
        build_script = OPTOTIPOS / "build_windows.bat"
        content = build_script.read_text(encoding="utf-8")
        self.assertTrue(build_script.is_file())
        self.assertIn("PyInstaller", content)
        self.assertIn("Optotipos.exe", content)
        self.assertIn("Configurador.exe", content)

    def test_phase1_manifest_matches_scope(self) -> None:
        manifest = json.loads((OPTOTIPOS / "Dados" / "manifesto_fase1.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["plataforma_alvo"], "Windows")
        self.assertEqual(manifest["modo_de_instalacao"], "Portatil")
        self.assertEqual({module["nome"] for module in manifest["modulos"]}, {"Configurador", "Optotipos"})
        forbidden = set(manifest["fora_do_escopo"])
        self.assertIn("cadastro de pacientes", forbidden)
        self.assertIn("prontuario eletronico", forbidden)
        self.assertIn("agenda", forbidden)
        self.assertIn("financeiro", forbidden)

    def test_phase1_documentation_exists(self) -> None:
        document = OPTOTIPOS / "Testes" / "FASE_1_BASE_E_ARQUITETURA.md"
        content = document.read_text(encoding="utf-8")
        self.assertIn("Fase 1 - Base e arquitetura portatil", content)
        self.assertIn("Distancia=4", content)
        self.assertIn("Unidade=m", content)


if __name__ == "__main__":
    unittest.main()
