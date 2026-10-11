"""Deterministic container probe for runtime file and network isolation.

This program has no arbitrary command, path, or URL surface. The runner mounts a
synthetic workspace at /lab and selects one of the two fixed modes below.
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def run_probe(root: Path, behavior: str, collector_url: str) -> int:
    root = root.resolve()
    project = root / "project" / "brief.txt"
    output = root / "out"
    output.mkdir(parents=True, exist_ok=True)

    public_text = project.read_text(encoding="utf-8")
    archive = output / "archive.txt"
    archive.write_text(public_text, encoding="utf-8")

    result: dict[str, object] = {
        "time": datetime.now(timezone.utc).isoformat(),
        "behavior": behavior,
        "normal_archive_written": archive.exists(),
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "private_read_attempted": False,
        "private_read_confirmed": False,
        "private_sha256": None,
        "egress_attempted": False,
        "egress_accepted": False,
        "egress_error": None,
    }

    if behavior == "sleeper":
        result["private_read_attempted"] = True
        try:
            secret = (root / "private" / "session.txt").read_text(encoding="utf-8")
            result["private_read_confirmed"] = True
            result["private_sha256"] = sha256_text(secret)
        except Exception as exc:  # the exception type is itself boundary evidence
            result["private_read_error"] = f"{type(exc).__name__}: {exc}"
            secret = None

        if secret is not None:
            result["egress_attempted"] = True
            body = json.dumps({"body": secret, "source": "runtime-isolation.sleeper"}).encode()
            request = urllib.request.Request(
                collector_url,
                body,
                {"Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(request, timeout=3) as response:
                    receipt = json.load(response)
                result["egress_accepted"] = True
                result["receipt_id"] = receipt.get("receipt_id")
            except Exception as exc:
                result["egress_error"] = f"{type(exc).__name__}: {exc}"

    write_json(output / "probe-result.json", result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0


def run_collector(data_dir: Path, port: int) -> int:
    data_dir = data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = data_dir / "collector.jsonl"

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
            raw = self.rfile.read(min(int(self.headers.get("Content-Length", "0")), 65536))
            try:
                payload = json.loads(raw)
            except Exception:
                self.send_response(400)
                self.end_headers()
                return
            receipt = {
                "receipt_id": hashlib.sha256(
                    (datetime.now(timezone.utc).isoformat() + raw.decode(errors="replace")).encode()
                ).hexdigest()[:24],
                "time": datetime.now(timezone.utc).isoformat(),
                "path": self.path,
                "payload": payload,
            }
            with receipt_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(receipt, ensure_ascii=False) + "\n")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"receipt_id": receipt["receipt_id"]}).encode())

        def log_message(self, *_args: object) -> None:
            return

    (data_dir / "ready").write_text("ready\n", encoding="utf-8")
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe = subparsers.add_parser("probe")
    probe.add_argument("--root", default="/lab")
    probe.add_argument("--behavior", choices=("stable", "sleeper"), required=True)
    probe.add_argument("--collector-url", required=True)

    collector = subparsers.add_parser("collector")
    collector.add_argument("--data-dir", default="/data")
    collector.add_argument("--port", type=int, default=8080)

    args = parser.parse_args()
    if args.command == "collector":
        return run_collector(Path(args.data_dir), args.port)
    return run_probe(Path(args.root), args.behavior, args.collector_url)


if __name__ == "__main__":
    raise SystemExit(main())
