"""Small independent API health service for managed CI acceptance."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SERVICE = "mono-api"
PAYLOAD = json.dumps({"status": "ok", "service": SERVICE}).encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond(send_body=True)

    def do_HEAD(self):
        self.respond(send_body=False)

    def respond(self, *, send_body):
        if self.path not in {"/", "/health"}:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.send_header("X-Astrolift-Fixture-App", SERVICE)
        self.end_headers()
        if send_body:
            self.wfile.write(PAYLOAD)

    def log_message(self, *_args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(
        ("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler
    ).serve_forever()
