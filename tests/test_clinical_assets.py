from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.clinical_assets import LICENSED_ASSET_SPECS, validate_all_asset_packs, validate_asset_pack
from optotipos_core.config import load_config
from optotipos_core.validation import build_validation_report


class ClinicalAssetsTest(unittest.TestCase):
    def test_missing_manifest_blocks_professional_test(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            status = validate_asset_pack("ishihara", Path(directory))
            self.assertFalse(status.ready)
            self.assertIn("manifest.json ausente", status.errors[0])

    def test_valid_licensed_manifest_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset_dir = root / "Testes" / "Assets" / "randot"
            asset_dir.mkdir(parents=True)
            (asset_dir / "plate_01.png").write_text("placeholder licensed binary", encoding="utf-8")
            (asset_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "source": "licensed supplier",
                        "version": "1.0",
                        "license": {"licensed": True},
                        "files": [{"path": "plate_01.png"}],
                    }
                ),
                encoding="utf-8",
            )
            status = validate_asset_pack("randot", root)
            self.assertTrue(status.ready)
            self.assertEqual(status.file_count, 1)

    def test_unlicensed_manifest_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset_dir = root / "Testes" / "Assets" / "fly_test"
            asset_dir.mkdir(parents=True)
            (asset_dir / "plate_01.png").write_text("placeholder", encoding="utf-8")
            (asset_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "source": "unknown",
                        "version": "1.0",
                        "license": {"licensed": False},
                        "files": [{"path": "plate_01.png"}],
                    }
                ),
                encoding="utf-8",
            )
            status = validate_asset_pack("fly_test", root)
            self.assertFalse(status.ready)
            self.assertIn("licenca nao confirmada", " ".join(status.errors))

    def test_all_asset_packs_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            statuses = validate_all_asset_packs(Path(directory))
            self.assertEqual(len(statuses), len(LICENSED_ASSET_SPECS))

    def test_validation_report_lists_licensed_asset_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            load_config(root)
            report = build_validation_report(root=root)
            self.assertIn("Testes profissionais dependentes de ativos licenciados", report)
            self.assertIn("Ishihara", report)
            self.assertIn("BLOQUEADO", report)


if __name__ == "__main__":
    unittest.main()
