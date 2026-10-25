
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import os
import subprocess
from urllib.parse import urlparse

PROJECT_DIR = Path(__file__).resolve().parent
WEB_DIR = PROJECT_DIR / "web"

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))

ENGINE_NAME = "threatlens.exe" if os.name == "nt" else "threatlens"
ENGINE_PATH = PROJECT_DIR / ENGINE_NAME
MAX_BODY_SIZE = 1_000_000


class ThreatLensHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/status":
            self.send_json({
                "status": "backend_running",
                "cpp_engine_available": ENGINE_PATH.is_file(),
                "message": "ThreatLens backend is responding."
            })
            return

        if path == "/":
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/analyze":
            self.send_json({"error": "Endpoint not found."}, 404)
            return

        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "text/plain":
            self.send_json({"error": "Content-Type must be text/plain."}, 415)
            return

        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self.send_json({"error": "Invalid Content-Length."}, 411)
            return

        if length < 1 or length > MAX_BODY_SIZE:
            self.send_json({"error": "Log must be between 1 byte and 1 MB."}, 413)
            return

        if not ENGINE_PATH.is_file():
            self.send_json({"error": "C++ engine is missing."}, 503)
            return

        try:
            log_text = self.rfile.read(length).decode("utf-8")
        except UnicodeDecodeError:
            self.send_json({"error": "Log must be valid UTF-8."}, 400)
            return

        try:
            completed = subprocess.run(
                [str(ENGINE_PATH), "--json"],
                input=log_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=5,
                cwd=str(PROJECT_DIR),
                shell=False,
                check=False
            )

            if completed.returncode != 0:
                self.send_json({"error": "C++ analysis failed."}, 500)
                return

            result = json.loads(completed.stdout)
            if not isinstance(result, dict) or result.get("success") is not True:
                raise ValueError("Unexpected C++ response")

            self.send_json(result)

        except subprocess.TimeoutExpired:
            self.send_json({"error": "Analysis timed out."}, 504)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            self.send_json({"error": "Could not process the C++ response."}, 500)

    def log_message(self, format, *args):
        print("{} - {}".format(self.client_address[0], format % args))


if __name__ == "__main__":
    if not WEB_DIR.is_dir():
        raise SystemExit("ERROR: web folder not found.")

    server = ThreadingHTTPServer((HOST, PORT), ThreatLensHandler)
    print("ThreatLens server running at http://{}:{}".format(HOST, PORT))
    print("C++ engine available: {}".format(ENGINE_PATH.is_file()))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nThreatLens server stopped.")
    finally:
        server.server_close()
