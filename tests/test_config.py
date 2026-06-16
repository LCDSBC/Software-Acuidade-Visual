from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.config import (
    export_backup,
    import_backup,
    load_config,
    load_profile,
    save_config_file,
    save_profile,
)


class ConfigTest(unittest.TestCase):
    def test_default_config_and_save(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_config(root)
            self.assertEqual(config.get("Distancia.txt", "Distancia"), "4")

            save_config_file("Distancia.txt", {"Distancia": "6", "Unidade": "m"}, root)
            updated = load_config(root)
            self.assertEqual(updated.get_float("Distancia.txt", "Distancia", 0), 6)

    def test_profile_roundtrip_preserves_key_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save_config_file("Tela.txt", {"LarguraTelaMM": "600"}, root)
            profile = save_profile("Teste_4m", root)
            self.assertTrue(profile.exists())
            self.assertIn("LarguraTelaMM=600", profile.read_text(encoding="utf-8"))

            save_config_file("Tela.txt", {"LarguraTelaMM": "500"}, root)
            load_profile("Teste_4m.ini", root)
            self.assertEqual(load_config(root).get("Tela.txt", "LarguraTelaMM"), "600")

    def test_backup_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save_config_file("Distancia.txt", {"Distancia": "5"}, root)
            backup = export_backup(root / "BackupCalibracao.opt", root)
            self.assertTrue(backup.exists())

            restored = root / "restored"
            import_backup(backup, restored)
            self.assertEqual(load_config(restored).get("Distancia.txt", "Distancia"), "5")


if __name__ == "__main__":
    unittest.main()
