#!/usr/local/bin/python3
"""Record-only stand-in for curl, npm, npx, and uname.

This program never opens a socket and never launches a child process. The
filename used to invoke it selects the emulated tool.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_TOOLS = {"curl", "npm", "npx", "uname"}
FIXED_UNAME = "Linux toxic-demo 6.6.0-demo #1 SMP x86_64 GNU/Linux"


def main() -> int:
    tool = Path(sys.argv[0]).name
    if tool not in ALLOWED_TOOLS:
        print(f"unsupported shim name: {tool}", file=sys.stderr)
        return 64

    evidence_dir = Path(os.environ.get("EVIDENCE_DIR", "/evidence"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    events_path = evidence_dir / "events.jsonl"
    sequence = 1
    if events_path.exists():
        sequence += sum(1 for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip())

    argv = sys.argv[1:]
    event = {
        "sequence": sequence,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "argv": argv,
        "cwd": os.getcwd(),
        "implementation": "RECORD_ONLY_SHIM",
        "network_requested_by_arguments": tool == "curl" and any(
            arg.startswith(("http://", "https://")) for arg in argv
        ),
        "network_performed": False,
        "child_process_started": False,
    }
    with events_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    if tool == "uname":
        if argv != ["-a"]:
            print("uname shim accepts only -a", file=sys.stderr)
            return 64
        print(FIXED_UNAME)
    elif tool == "curl":
        print("SHIM_BLOCKED_NETWORK")
    elif tool == "npm":
        print("SHIM_RECORDED_NPM")
    elif tool == "npx":
        print("SHIM_RECORDED_NPX")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
