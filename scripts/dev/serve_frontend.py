"""Serve the Vite production build and proxy API calls to FastAPI (npm is not required)."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os
import urllib.error
import urllib.request

DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
BACKEND = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
API_EXACT = {"/ping", "/auth", "/etd", "/gspr", "/standards", "/evidence", "/imports"}
API_PREFIXES = (
    "/api/",
    "/auth/",
    "/etd/",
    "/gspr/",
    "/device-profiles",
    "/standards",
    "/evidence",
    "/imports",
)


class Handler(SimpleHTTPRequestHandler):
    def _should_proxy(self) -> bool:
        path = self.path.split("?", 1)[0]
        if path in API_EXACT or path == "/api":
            return True
        return any(path.startswith(prefix) for prefix in API_PREFIXES)

    def do_GET(self):
        if self._should_proxy():
            return self._proxy()
        path = self.path.split("?", 1)[0]
        fs_path = self.translate_path(path)
        if not os.path.isfile(fs_path):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        return self._proxy()

    def do_PUT(self):
        return self._proxy()

    def do_DELETE(self):
        return self._proxy()

    def do_PATCH(self):
        return self._proxy()

    def _proxy(self):
        path = self.path
        if path.startswith("/api"):
            path = path[4:] or "/"
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length) if length else None
        req = urllib.request.Request(
            BACKEND + path,
            data=body,
            method=self.command,
            headers={
                k: v
                for k, v in self.headers.items()
                if k.lower() not in {"host", "content-length"}
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = resp.read()
                self.send_response(resp.status)
                for key, value in resp.headers.items():
                    if key.lower() not in {"transfer-encoding", "connection"}:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            for key, value in exc.headers.items():
                if key.lower() not in {"transfer-encoding", "connection"}:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(payload)


if __name__ == "__main__":
    os.chdir(DIST)
    port = int(os.environ.get("PORT", "5173"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving {DIST} on http://127.0.0.1:{port}")
    server.serve_forever()
