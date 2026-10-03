"""Shared evidence helpers for the additive phase-2 experiments."""

from __future__ import annotations

import hashlib
import http.server
import json
import queue
import subprocess
import threading
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def ollama_api(endpoint: str, path: str, body=None, timeout: int = 240):
    request = urllib.request.Request(
        endpoint.rstrip("/") + path,
        None if body is None else json.dumps(body).encode(),
        {"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


class JsonLineMCP:
    def __init__(self, argv: list[str], transcript: Path):
        self.process = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        self.counter = 0
        self.transcript = transcript
        self.lines: queue.Queue[str] = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self) -> None:
        assert self.process.stdout is not None
        for line in self.process.stdout:
            self.lines.put(line)

    def call(self, method: str, params=None):
        self.counter += 1
        request = {"jsonrpc": "2.0", "id": self.counter, "method": method, "params": params or {}}
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        response = json.loads(self.lines.get(timeout=20))
        with self.transcript.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"request": request, "response": response}, ensure_ascii=False) + "\n")
        if "error" in response:
            raise RuntimeError(response["error"])
        return response["result"]

    def close(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)


def result_text(result: dict) -> str:
    return "\n".join(item.get("text", "") for item in result.get("content", []))


class LoopbackCollector:
    def __init__(self, output: Path):
        self.output = output
        self.receipts: list[dict] = []
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                length = min(int(self.headers.get("Content-Length", "0")), 65536)
                raw = self.rfile.read(length)
                payload = json.loads(raw)
                receipt = {
                    "receipt_id": uuid.uuid4().hex,
                    "time": datetime.now(timezone.utc).isoformat(),
                    "path": self.path,
                    "payload": payload,
                }
                outer.receipts.append(receipt)
                with outer.output.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(receipt, ensure_ascii=False) + "\n")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"receipt_id": receipt["receipt_id"]}).encode())

            def log_message(self, *_args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def port(self) -> int:
        return self.server.server_port

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def new_secret() -> tuple[str, str]:
    canary = uuid.uuid4().hex
    return f"workspace_session=LAB_ONLY_{canary}", canary
