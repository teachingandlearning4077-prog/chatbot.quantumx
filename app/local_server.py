from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs
import cgi

from app.engine import ChatEngine

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_FILE = ROOT / "app" / "templates" / "index.html"

engines_by_session: dict[str, ChatEngine] = {}


def _parse_cookie(raw_cookie: str | None) -> dict[str, str]:
    if not raw_cookie:
        return {}
    parts = [p.strip() for p in raw_cookie.split(";") if p.strip()]
    out: dict[str, str] = {}
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            out[key.strip()] = value.strip()
    return out


class QuantumXHandler(SimpleHTTPRequestHandler):
    def _get_engine(self) -> tuple[str, ChatEngine, bool]:
        cookies = _parse_cookie(self.headers.get("Cookie"))
        session_id = cookies.get("qx_session")
        created = False
        if not session_id:
            session_id = os.urandom(12).hex()
            created = True

        if session_id not in engines_by_session:
            engines_by_session[session_id] = ChatEngine()

        return session_id, engines_by_session[session_id], created

    def _write_json(self, data: dict, status: int = 200, set_cookie: str | None = None) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if set_cookie:
            self.send_header("Set-Cookie", set_cookie)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            session_id, _, created = self._get_engine()
            html = TEMPLATE_FILE.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            if created:
                self.send_header("Set-Cookie", f"qx_session={session_id}; HttpOnly; SameSite=Lax")
            self.end_headers()
            self.wfile.write(html)
            return

        if self.path == "/health":
            self._write_json(
                {
                    "status": "ok",
                    "name": "QuantumX",
                    "active_sessions": len(engines_by_session),
                    "runtime": "local_server",
                }
            )
            return

        if self.path.startswith("/static/"):
            self.path = "/app" + self.path
            return super().do_GET()

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:
        if self.path != "/chat":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        content_type = self.headers.get("Content-Type", "")
        message = ""
        mode = "text"

        if content_type.startswith("multipart/form-data"):
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type},
            )
            message = (form.getfirst("message", "") or "").strip()
            mode = (form.getfirst("mode", "text") or "text").strip()
        else:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length).decode("utf-8")
            data = parse_qs(raw_body, keep_blank_values=True)
            message = (data.get("message", [""])[0] or "").strip()
            mode = (data.get("mode", ["text"])[0] or "text").strip()
        valid_mode = mode if mode in {"text", "image"} else "text"

        if not message:
            self._write_json(
                {
                    "response": "Mensagem vazia. Digite algo para continuar.",
                    "image_base64": None,
                    "mode": valid_mode,
                },
                status=400,
            )
            return

        session_id, engine, created = self._get_engine()
        result = engine.ask(message, mode=valid_mode)
        payload = {"response": result.text, "image_base64": result.image_base64, "mode": valid_mode}

        cookie = f"qx_session={session_id}; HttpOnly; SameSite=Lax" if created else None
        self._write_json(payload, status=200, set_cookie=cookie)


def run_local_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    os.chdir(ROOT)
    server = ThreadingHTTPServer((host, port), QuantumXHandler)
    print(f"QuantumX local server rodando em http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_local_server()
