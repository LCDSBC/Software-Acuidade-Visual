from __future__ import annotations

import sys
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.main_app import MonitorRect, bounded_monitor


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


if __name__ == "__main__":
    unittest.main()
