"""Shared evidence helpers for the additive phase-2 experiments."""

from __future__ import annotations

import hashlib
import http.server
import json
import queue
import shutil
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


def prepare_batch(
    *,
    base: Path,
    batch: Path,
    code_names: tuple[str, ...],
    runtime: dict,
    contract_dimensions: dict,
) -> dict:
    """Create an immutable batch contract, or reject an incompatible resume.

    The contract binds the selected model/runtime, the exact source files and the
    complete expected matrix.  Existing batches are never silently rewritten.
    """

    source_manifest = [
        {"file": name, "sha256": sha256_file(base / name)} for name in sorted(code_names)
    ]
    runtime_bytes = (json.dumps(runtime, ensure_ascii=False, indent=2) + "\n").encode()
    manifest_bytes = (json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n").encode()
    runtime_sha256 = hashlib.sha256(runtime_bytes).hexdigest()
    code_manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    contract = {
        "format": "serendipity-phase2-batch-contract-v1",
        "batch": batch.name,
        "code_manifest_sha256": code_manifest_sha256,
        "runtime_sha256": runtime_sha256,
        **contract_dimensions,
    }
    contract_bytes = (json.dumps(contract, ensure_ascii=False, indent=2) + "\n").encode()
    contract_sha256 = hashlib.sha256(contract_bytes).hexdigest()
    contract_path = batch / "batch-contract.json"

    if contract_path.exists():
        existing = contract_path.read_bytes()
        if existing != contract_bytes:
            raise RuntimeError(
                f"Refusing incompatible resume for {batch.name}: batch-contract.json differs"
            )
        if not (batch / "runtime.json").exists() or sha256_file(batch / "runtime.json") != runtime_sha256:
            raise RuntimeError(f"Refusing resume for {batch.name}: runtime.json hash mismatch")
        if not (batch / "code" / "manifest.json").exists() or sha256_file(batch / "code" / "manifest.json") != code_manifest_sha256:
            raise RuntimeError(f"Refusing resume for {batch.name}: code manifest hash mismatch")
        for item in source_manifest:
            copied = batch / "code" / item["file"]
            if not copied.exists() or sha256_file(copied) != item["sha256"]:
                raise RuntimeError(
                    f"Refusing resume for {batch.name}: copied source mismatch for {item['file']}"
                )
    else:
        if batch.exists() and any(batch.iterdir()):
            raise RuntimeError(
                f"Refusing to adopt non-empty uncontracted batch {batch.name}; use a new batch name"
            )
        code = batch / "code"
        code.mkdir(parents=True, exist_ok=True)
        for name in code_names:
            shutil.copyfile(base / name, code / name)
        (code / "manifest.json").write_bytes(manifest_bytes)
        (batch / "runtime.json").write_bytes(runtime_bytes)
        contract_path.write_bytes(contract_bytes)

    return {
        "batch_contract_sha256": contract_sha256,
        "code_manifest_sha256": code_manifest_sha256,
        "runtime_sha256": runtime_sha256,
    }


def bind_run_input(output: Path, input_hashes: dict, dimensions: dict) -> dict:
    """Write and return the per-run input contract and its canonical hash."""

    contract = {
        "format": "serendipity-phase2-run-input-v1",
        **dimensions,
        "input_hashes": input_hashes,
    }
    input_sha256 = canonical_sha256(contract)
    write_json(output / "input-contract.json", {**contract, "input_sha256": input_sha256})
    return {
        "input_hashes": dict(input_hashes),
        "input_contract": contract,
        "input_sha256": input_sha256,
    }


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
