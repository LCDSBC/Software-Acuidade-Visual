from __future__ import annotations

import sys
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.main_app import MonitorRect, bounded_monitor, plan_monitor_layout


class MonitorModeTest(unittest.TestCase):
    def test_monitor_geometry_format(self) -> None:
        monitor = MonitorRect(1920, 0, 1920, 1080)
        self.assertEqual(monitor.geometry(), "1920x1080+1920+0")

    def test_bounded_monitor_clamps_index(self) -> None:
        monitors = [MonitorRect(0, 0, 1920, 1080), MonitorRect(1920, 0, 1920, 1080)]
        self.assertEqual(bounded_monitor(monitors, -2), monitors[0])
        self.assertEqual(bounded_monitor(monitors, 4), monitors[1])

    def test_bounded_monitor_returns_default_without_detection(self) -> None:
        monitor = bounded_monitor([], 0)
        self.assertEqual(monitor.width, 1280)
        self.assertEqual(monitor.height, 720)

    def test_tela_unica_uses_selected_test_monitor(self) -> None:
        monitors = [MonitorRect(0, 0, 1920, 1080), MonitorRect(1920, 0, 1920, 1080)]
        plan = plan_monitor_layout("TelaUnica", monitors, examiner_index=0, test_index=1, fullscreen=True)
        self.assertEqual(plan.effective_mode, "TelaUnica")
        self.assertEqual(plan.main_monitor, monitors[1])
        self.assertTrue(plan.main_fullscreen)
        self.assertEqual(plan.display_windows, ())
        self.assertEqual(plan.total_canvases, 1)

    def test_duas_telas_creates_examiner_and_test_window(self) -> None:
        monitors = [MonitorRect(0, 0, 1920, 1080), MonitorRect(1920, 0, 3840, 2160)]
        plan = plan_monitor_layout("DuasTelas", monitors, examiner_index=0, test_index=1, fullscreen=True)
        self.assertEqual(plan.effective_mode, "DuasTelas")
        self.assertEqual(plan.main_monitor, monitors[0])
        self.assertFalse(plan.main_fullscreen)
        self.assertEqual(len(plan.display_windows), 1)
        self.assertEqual(plan.display_windows[0].title, "Exibicao de Testes")
        self.assertEqual(plan.display_windows[0].monitor, monitors[1])
        self.assertTrue(plan.display_windows[0].fullscreen)
        self.assertEqual(plan.total_canvases, 2)

    def test_duas_telas_falls_back_with_single_monitor(self) -> None:
        monitors = [MonitorRect(0, 0, 1920, 1080)]
        plan = plan_monitor_layout("DuasTelas", monitors, fullscreen=True)
        self.assertEqual(plan.effective_mode, "TelaUnica")
        self.assertIn("dois monitores", plan.fallback_reason)
        self.assertEqual(plan.total_canvases, 1)

    def test_espelhamento_creates_window_for_each_extra_monitor(self) -> None:
        monitors = [
            MonitorRect(0, 0, 1920, 1080),
            MonitorRect(1920, 0, 1920, 1080),
            MonitorRect(3840, 0, 1280, 720),
        ]
        plan = plan_monitor_layout("Espelhamento", monitors, fullscreen=True)
        self.assertEqual(plan.effective_mode, "Espelhamento")
        self.assertEqual(plan.main_monitor, monitors[0])
        self.assertEqual([display.monitor for display in plan.display_windows], monitors[1:])
        self.assertEqual([display.title for display in plan.display_windows], ["Espelho 1", "Espelho 2"])
        self.assertEqual(plan.total_canvases, 3)

    def test_espelhamento_falls_back_with_single_monitor(self) -> None:
        plan = plan_monitor_layout("Espelhamento", [MonitorRect(0, 0, 1920, 1080)], fullscreen=False)
        self.assertEqual(plan.effective_mode, "TelaUnica")
        self.assertFalse(plan.main_fullscreen)
        self.assertIn("monitores adicionais", plan.fallback_reason)

    def test_invalid_mode_falls_back_to_tela_unica(self) -> None:
        monitors = [MonitorRect(0, 0, 1920, 1080)]
        plan = plan_monitor_layout("ModoInvalido", monitors, fullscreen=True)
        self.assertEqual(plan.requested_mode, "ModoInvalido")
        self.assertEqual(plan.effective_mode, "TelaUnica")


if __name__ == "__main__":
    unittest.main()
