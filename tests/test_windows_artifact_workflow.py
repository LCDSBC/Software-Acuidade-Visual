from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WindowsArtifactWorkflowTest(unittest.TestCase):
    def test_github_actions_workflow_exists(self) -> None:
        workflow = ROOT / ".github" / "workflows" / "build-windows-portable.yml"
        content = workflow.read_text(encoding="utf-8")
        self.assertIn("windows-latest", content)
        self.assertIn("build_windows.bat", content)
        self.assertIn("Optotipos_Profissional_Windows_Portatil", content)
        self.assertIn("Optotipos_Profissional_Setup", content)
        self.assertIn("innosetup", content)
        self.assertIn("actions/upload-artifact", content)

    def test_inno_setup_script_exists(self) -> None:
        script = ROOT / "Optotipos" / "Installer" / "OptotiposProfissional.iss"
        content = script.read_text(encoding="utf-8")
        self.assertIn("Optotipos Profissional", content)
        self.assertIn("Optotipos.exe", content)
        self.assertIn("Configurador.exe", content)
        self.assertIn("PrivilegesRequired=lowest", content)

    def test_build_script_packages_manual_and_executables(self) -> None:
        build_script = ROOT / "Optotipos" / "build_windows.bat"
        content = build_script.read_text(encoding="utf-8")
        self.assertIn("Optotipos.exe", content)
        self.assertIn("Configurador.exe", content)
        self.assertIn("Manual", content)
        self.assertIn("dist\\Optotipos_Portatil", content)

    def test_readme_explains_artifact_download(self) -> None:
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Gerar arquivo baixavel pelo GitHub Actions", content)
        self.assertIn("Optotipos_Profissional_Windows_Portatil", content)
        self.assertIn("Optotipos_Profissional_Setup", content)


if __name__ == "__main__":
    unittest.main()
