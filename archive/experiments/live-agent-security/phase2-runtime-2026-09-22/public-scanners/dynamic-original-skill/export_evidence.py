#!/usr/local/bin/python3
"""Export one allowlisted tmpfs evidence file to stdout without a shell."""

from __future__ import annotations

import sys
from pathlib import Path


ALLOWED = {"ready", "events.jsonl", "interpreter-result.json"}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ALLOWED:
        print("only fixed evidence filenames are allowed", file=sys.stderr)
        return 64
    path = Path("/evidence") / sys.argv[1]
    if not path.is_file():
        print(f"evidence not ready: {sys.argv[1]}", file=sys.stderr)
        return 75
    sys.stdout.buffer.write(path.read_bytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
