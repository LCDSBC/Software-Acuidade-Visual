from __future__ import annotations

import sys
import unittest
from pathlib import Path
from urllib.request import urlopen


APP_DIR = Path(__file__).resolve().parents[1] / "Optotipos" / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.wireless import RemoteServer, mirror_page, remote_page


def fetch(url: str) -> str:
    with urlopen(url, timeout=3) as response:
        return response.read().decode("utf-8")


class WirelessControlTest(unittest.TestCase):
    def test_remote_page_contains_mobile_controls(self) -> None:
        html = remote_page("Snellen Letras", "")
        self.assertIn("Controle remoto", html)
        self.assertIn("/cmd?key=next", html)
        self.assertIn("/cmd?key=left_occlusion", html)
        self.assertIn("Modo espelho simples", html)

    def test_mirror_page_contains_current_test(self) -> None:
        html = mirror_page("Landolt C")
        self.assertIn("OPTOTIPOS", html)
        self.assertIn("Landolt C", html)
        self.assertIn("refresh", html)

    def test_remote_server_receives_phone_commands(self) -> None:
        received: list[str] = []
        server = RemoteServer(received.append, port=0)
        try:
            server.set_current_test("Tumbling E")
            server.start()
            base = f"http://127.0.0.1:{server.port}"
            index = fetch(base + "/")
            self.assertIn("Tumbling E", index)

            command_response = fetch(base + "/cmd?key=next")
            self.assertIn("Comando enviado", command_response)
            self.assertEqual(received, ["next"])

            mirror = fetch(base + "/mirror")
            self.assertIn("Tumbling E", mirror)
        finally:
            server.stop()
        self.assertFalse(server.running)

    def test_start_is_idempotent_while_running(self) -> None:
        server = RemoteServer(lambda _command: None, port=0)
        try:
            first = server.start()
            second = server.start()
            self.assertEqual(first, second)
            self.assertTrue(server.running)
        finally:
            server.stop()


if __name__ == "__main__":
    unittest.main()
