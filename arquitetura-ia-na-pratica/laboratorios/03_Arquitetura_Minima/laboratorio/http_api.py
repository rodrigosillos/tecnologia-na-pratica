"""Loopback-only teaching server, not a production HTTP stack."""
import argparse
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import socket
from uuid import uuid4

from adapters import DEMO_IDENTITIES, StubGenerator
from bootstrap import wire
from contracts import Query
from policy import strict_json
from settings import Settings

ERROR_STATUS = {"dependency_timeout":504, "deadline_exceeded":504,
    "dependency_unavailable":503, "invalid_output":502,
    "budget_exceeded":503, "usage_unknown":503,
    "generation_incomplete":502, "generation_refused":502}


def parse_query(raw):
    obj = strict_json(raw.decode("utf-8"))
    if not isinstance(obj, dict) or set(obj) != {"topic", "language"}:
        raise ValueError("invalid request fields")
    return Query(obj["topic"], obj["language"])


def status_for(outcome):
    return 200 if outcome.status != "error" else ERROR_STATUS[outcome.reason]


def make_server(service, port=0):
    class Handler(BaseHTTPRequestHandler):
        server_version = "CopilotLab/1"
        sys_version = ""

        def setup(self):
            super().setup()
            self.connection.settimeout(2.0)

        def log_message(self, *args):
            pass  # No raw requests, identities or texts in default logs.

        def send_json(self, status, payload):
            rid = str(uuid4())
            payload = dict(payload, request_id=rid)
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Request-ID", rid)
            self.send_header("Connection", "close")
            if status == 401:
                self.send_header("WWW-Authenticate", 'Bearer realm="lab"')
            if status == 405:
                self.send_header("Allow", "POST")
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True

        def fail(self, status, reason):
            self.send_json(status, {"status":"error", "reason":reason})

        def do_GET(self):
            if self.path == "/health":
                self.send_json(200, {"status":"ok"})
            else:
                self.fail(405 if self.path == "/v1/answers" else 404,
                          "method_not_allowed" if self.path == "/v1/answers"
                          else "not_found")

        def do_POST(self):
            if self.path != "/v1/answers":
                return self.fail(404, "not_found")
            auth = self.headers.get_all("Authorization", [])
            principal = (DEMO_IDENTITIES.get(auth[0][7:])
                if len(auth) == 1 and auth[0].startswith("Bearer ") else None)
            if principal is None:
                return self.fail(401, "unauthenticated")
            if self.headers.get("Content-Type") != "application/json":
                return self.fail(415, "unsupported_media_type")
            lengths = self.headers.get_all("Content-Length", [])
            if self.headers.get("Transfer-Encoding") is not None:
                return self.fail(400, "unsupported_transfer_encoding")
            if not lengths:
                return self.fail(411, "length_required")
            if len(lengths) != 1 or not re.fullmatch(r"[0-9]{1,8}", lengths[0]):
                return self.fail(400, "invalid_length")
            size = int(lengths[0])
            if size > service.settings.max_body_bytes:
                return self.fail(413, "body_too_large")
            try:
                raw = self.rfile.read(size)
                if len(raw) != size: raise ValueError("short body")
                query = parse_query(raw)
            except (ValueError, RecursionError):
                return self.fail(400, "invalid_request")
            except (TimeoutError, socket.timeout):
                return self.fail(408, "request_timeout")
            try:
                outcome = service.answer(principal, query)
                self.send_json(status_for(outcome), asdict(outcome))
            except Exception:
                # Last-resort HTTP boundary; never turn a bug into abstention.
                self.fail(500, "internal_error")

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--mode", choices=StubGenerator.MODES, default="good")
    parser.add_argument("--timeout-ms", type=int, default=2500)
    parser.add_argument("--budget-microusd", type=int, default=1000)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535: parser.error("invalid port")
    try:
        settings = Settings(timeout_ms=args.timeout_ms,
                            budget_microusd=args.budget_microusd)
    except ValueError as exc: parser.error(str(exc))
    with make_server(wire(settings, args.mode), args.port) as server:
        print(f"Local lab: http://127.0.0.1:{server.server_port}")
        print("Public demo tokens only. Stop with Ctrl+C.")
        try: server.serve_forever()
        except KeyboardInterrupt: pass


if __name__ == "__main__": main()
