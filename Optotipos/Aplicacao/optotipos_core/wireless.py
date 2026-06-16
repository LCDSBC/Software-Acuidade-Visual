from __future__ import annotations

import html
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import parse_qs, urlparse


CommandCallback = Callable[[str], None]


class RemoteServer:
    def __init__(self, callback: CommandCallback, port: int = 8765) -> None:
        self.callback = callback
        self.port = port
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.current_test = "Optotipos"

    @property
    def running(self) -> bool:
        return self._server is not None

    def start(self) -> str:
        if self._server is not None:
            return self.url()

        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
                parsed = urlparse(self.path)
                if parsed.path == "/cmd":
                    command = parse_qs(parsed.query).get("key", [""])[0]
                    if command:
                        outer.callback(command)
                    self._send_html(remote_page(outer.current_test, "Comando enviado."))
                    return
                if parsed.path == "/mirror":
                    self._send_html(mirror_page(outer.current_test))
                    return
                self._send_html(remote_page(outer.current_test, ""))

            def log_message(self, format: str, *args: object) -> None:
                return

            def _send_html(self, body: str) -> None:
                encoded = body.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        self._server = ThreadingHTTPServer(("0.0.0.0", self.port), Handler)
        self.port = int(self._server.server_address[1])
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self.url()

    def stop(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None

    def set_current_test(self, name: str) -> None:
        self.current_test = name

    def url(self) -> str:
        return f"http://{local_ip()}:{self.port}"


def local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def remote_page(current_test: str, message: str) -> str:
    safe_test = html.escape(current_test)
    safe_message = html.escape(message)
    buttons = (
        ("prev", "Anterior"),
        ("next", "Proximo"),
        ("bigger", "Aumentar"),
        ("smaller", "Diminuir"),
        ("random", "Aleatorio"),
        ("fullscreen", "Tela cheia"),
        ("blackwhite", "Fundo"),
        ("left_occlusion", "Ocluir E"),
        ("right_occlusion", "Ocluir D"),
        ("clear_occlusion", "Sem oclusao"),
    )
    button_html = "\n".join(f"<a class='btn' href='/cmd?key={key}'>{label}</a>" for key, label in buttons)
    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Controle Optotipos</title>
<style>
body {{ font-family: Arial, sans-serif; background:#111; color:#fff; margin:0; padding:24px; }}
h1 {{ font-size:24px; }}
.btn {{ display:block; padding:18px; margin:10px 0; background:#1f6feb; color:white; text-decoration:none; border-radius:10px; text-align:center; font-size:20px; }}
.msg {{ color:#9be59b; min-height:24px; }}
</style>
</head>
<body>
<h1>Controle remoto</h1>
<p>Teste atual: <strong>{safe_test}</strong></p>
<p class="msg">{safe_message}</p>
{button_html}
<p><a class="btn" href="/mirror">Modo espelho simples</a></p>
</body>
</html>"""


def mirror_page(current_test: str) -> str:
    safe_test = html.escape(current_test)
    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="2">
<title>Espelho Optotipos</title>
<style>
body {{ background:white; color:black; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; font-family:Arial, sans-serif; }}
main {{ text-align:center; }}
h1 {{ font-size:10vw; margin:0; }}
p {{ font-size:4vw; }}
</style>
</head>
<body><main><h1>OPTOTIPOS</h1><p>{safe_test}</p></main></body>
</html>"""
