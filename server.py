
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import subprocess
import threading
from urllib.parse import urlparse

PROJECT_DIR = Path(__file__).resolve().parent
WEB_DIR = PROJECT_DIR / "web"
ENGINE_PATH = PROJECT_DIR / "threatlens.exe"

HOST = "127.0.0.1"
PORT = 8000
MAX_BODY_SIZE = 1_000_000  # 1 MB
ENGINE_TIMEOUT_SECONDS = 5

# Limit concurrent engine runs to avoid resource exhaustion.
ENGINE_LOCK = threading.Lock()


class ThreatLensHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
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
        path = urlparse(self.path).path

        if path != "/api/analyze":
            self.send_json({
                "error": "Endpoint not found."
            }, 404)
            return

        # Require a plain-text request body.
        content_type = self.headers.get("Content-Type", "")
        if content_type.split(";", 1)[0].strip().lower() != "text/plain":
            self.send_json({
                "error": "Content-Type must be text/plain."
            }, 415)
            return

        # Reject missing, malformed, or excessively large bodies.
        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self.send_json({
                "error": "A valid Content-Length header is required."
            }, 411)
            return

        if content_length < 1:
            self.send_json({
                "error": "The uploaded log is empty."
            }, 400)
            return

        if content_length > MAX_BODY_SIZE:
            self.send_json({
                "error": "Log file exceeds the 1 MB limit."
            }, 413)
            return

        if not ENGINE_PATH.is_file():
            self.send_json({
                "error": "C++ engine is missing. Compile main.cpp first."
            }, 503)
            return

        try:
            raw_body = self.rfile.read(content_length)
            log_text = raw_body.decode("utf-8")

        except UnicodeDecodeError:
            self.send_json({
                "error": "Log file must contain valid UTF-8 text."
            }, 400)
            return

        # The C++ engine reads the submitted text from stdin.
        # No client-supplied filename or shell command is executed.
        try:
            with ENGINE_LOCK:
                completed = subprocess.run(
                    [str(ENGINE_PATH), "--json"],
                    input=log_text,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="strict",
                    timeout=ENGINE_TIMEOUT_SECONDS,
                    cwd=str(PROJECT_DIR),
                    shell=False,
                    check=False
                )

            if completed.returncode != 0:
                print("C++ engine exited with an error.")
                self.send_json({
                    "error": "The C++ engine failed to analyze the log."
                }, 500)
                return

            result = json.loads(completed.stdout)

            if not isinstance(result, dict) or result.get("success") is not True:
                raise ValueError("Unexpected engine response")

            self.send_json(result)

        except subprocess.TimeoutExpired:
            self.send_json({
                "error": "Analysis timed out. Please try a smaller log."
            }, 504)

        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            print("ThreatLens could not process the C++ engine response.")
            self.send_json({
                "error": "Could not process the C++ engine response."
            }, 500)

    def log_message(self, format, *args):
        # Keep normal request logs without exposing uploaded log contents.
        print("{} - {}".format(self.client_address[0], format % args))


if __name__ == "__main__":
    if not WEB_DIR.is_dir():
        raise SystemExit("ERROR: The web folder does not exist.")

    server = ThreadingHTTPServer((HOST, PORT), ThreatLensHandler)

    print("ThreatLens server running at http://{}:{}".format(HOST, PORT))
    print("C++ engine available: {}".format(ENGINE_PATH.is_file()))
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nThreatLens server stopped.")
    finally:
        server.server_close()
