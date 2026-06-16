from __future__ import annotations

import sys
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.rendering import e_pattern_cells
from optotipos_core.validation import build_optotype_validation_report, validate_optotypes


class OptotypeValidationTest(unittest.TestCase):
    def test_tumbling_e_middle_bar_is_complete_five_cells(self) -> None:
        cells = e_pattern_cells()
        self.assertTrue(all((col, 2) in cells for col in range(5)))

    def test_all_optotype_validation_checks_pass(self) -> None:
        summary = validate_optotypes()
        self.assertEqual(summary.failed_critical_count, 0)
        self.assertTrue(summary.approved_for_field_validation)
        self.assertEqual(summary.score_percent, 100.0)

    def test_optotype_validation_report_contains_core_tests(self) -> None:
        report = build_optotype_validation_report()
        self.assertIn("Snellen - linhas obrigatorias", report)
        self.assertIn("Tumbling E - grade 5x5", report)
        self.assertIn("Landolt C - abertura proporcional", report)
        self.assertIn("ETDRS - progressao LogMAR", report)
        self.assertIn("Aprovado para validacao de campo: SIM", report)


if __name__ == "__main__":
    unittest.main()
