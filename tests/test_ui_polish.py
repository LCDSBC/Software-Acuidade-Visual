from __future__ import annotations

import sys
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.main_app import format_status_text, mirror_status_text, shortcut_hint_text


class UIPolishTest(unittest.TestCase):
    def test_shortcut_hint_lists_core_controls(self) -> None:
        text = shortcut_hint_text()
        self.assertIn("+/- tamanho", text)
        self.assertIn("Ctrl+Alt+C configurador", text)
        self.assertIn("M monitor", text)

    def test_mirror_status_text(self) -> None:
        self.assertEqual(mirror_status_text(False, False), "Espelho OFF")
        self.assertEqual(mirror_status_text(True, False), "Espelho H")
        self.assertEqual(mirror_status_text(True, True), "Espelho H+V")

    def test_status_text_includes_clinical_context(self) -> None:
        text = format_status_text("Snellen Letras", 4, "DuasTelas", 2, True, False)
        self.assertIn("Snellen Letras", text)
        self.assertIn("Distancia 4 m", text)
        self.assertIn("DuasTelas", text)
        self.assertIn("2 monitor(es)", text)
        self.assertIn("Espelho H", text)


if __name__ == "__main__":
    unittest.main()
