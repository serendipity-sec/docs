"""Inert scanner-input experiment. Does not run skills, MCP servers or LLMs.

Use the environment with cisco-ai-skill-scanner==2.1.0. Outputs are written only
under an explicitly provided work directory and evidence directory.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone


def contextual_rule(case: dict) -> str:
    """Handwritten policy illustration, NOT a learned or validated detector."""
    if not case["path_connected"]:
        return "no_candidate_under_policy"
    if case["scope_allows"] is False:
        return "blocked_by_control"
    if case["scope_allows"] is None or case["sink_audience"] == "unknown":
        return "insufficient_evidence"
    if case["source_label"] == "private" and case["sink_audience"] == "public" and not case["explicit_release"]:
        return "candidate"
    return "no_candidate_under_policy"


def run_scans(work: Path, evidence: Path) -> None:
    fixtures_path = Path(__file__).with_name("fixtures.json")
    fixtures = json.loads(fixtures_path.read_text(encoding="utf-8"))
    work.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    results = []
    # Exclude credentials and user-specific scanner configuration from subprocesses.
    child_env = {k: v for k, v in os.environ.items() if k.upper() in {
        "SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP", "COMSPEC",
        "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS"
    }}
    child_env.update(PYTHONUTF8="1", LITELLM_LOCAL_MODEL_COST_MAP="True", DO_NOT_TRACK="1")
    for set_name, members in fixtures["scan_sets"].items():
        target = work / set_name
        for name in members:
            directory = target / name
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "SKILL.md").write_text(fixtures["skills"][name], encoding="utf-8")
        output = work / f"{set_name}.json"
        command = [sys.executable, "-X", "utf8", "-m", "skill_scanner.cli.cli", "scan-all", str(target),
                   "--recursive", "--check-overlap", "--use-behavioral", "--format", "json", "--output", str(output)]
        proc = subprocess.run(command, cwd=work, env=child_env, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=180)
        report = json.loads(output.read_text(encoding="utf-8")) if output.exists() else None
        results.append({"set": set_name, "command": command, "exit_code": proc.returncode,
                        "stdout": proc.stdout, "stderr": proc.stderr, "report": report})
    output = {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "scanner_version": importlib.metadata.version("cisco-ai-skill-scanner"),
        "fixtures_sha256": hashlib.sha256(fixtures_path.read_bytes()).hexdigest(),
        "scope": "Offline package scanning only. No victim agent, live server, LLM, or network actions.",
        "runs": results,
        "context_illustration": [{**c, "actual": contextual_rule(c)} for c in fixtures["context_cases"]],
        "context_warning": "Manually annotated policy cases; checking these is not evidence of detection accuracy. The Cisco input stays the same for all eight contexts."
    }
    (evidence / "skill-scanner-results.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in results:
        print(r["set"], "exit", r["exit_code"], "report_available", r["report"] is not None)
    assert all(c["actual"] == c["expected"] for c in output["context_illustration"])
    if any(r["exit_code"] != 0 or r["report"] is None for r in results):
        raise SystemExit("A scanner run failed; inspect raw evidence instead of calling it clean.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--evidence", type=Path, required=True)
    a = p.parse_args()
    run_scans(a.work.resolve(), a.evidence.resolve())
