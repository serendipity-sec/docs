#!/usr/bin/env python3
"""Validate the frozen input, Docker isolation, and record-only event trace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_SHA256 = "d70912ce0d898712b9b5048423d89d5190ffe4775d57f3221bff35bddbe36e3e"
EXPECTED_COMMIT = "80ce2e06f52fd384163c4bd6778676019723773c"
EXPECTED_TOOLS = ["uname", "curl", "npm", "npm", "npm", "npm", "npx"]
CANARY = "VERCEL_SKILL_CANARY_20260922"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = args.root.resolve()
    results = root / "results"
    evidence = results / "container-evidence"

    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, observed: Any) -> None:
        checks.append({"name": name, "passed": bool(condition), "observed": observed})

    provenance = load_json(results / "provenance.json")
    config = load_json(results / "container-config.json")
    inspect_before = load_json(results / "raw" / "container-inspect-before.json")[0]
    inspect_after = load_json(results / "raw" / "container-inspect-after.json")[0]
    interpreter = load_json(evidence / "interpreter-result.json")
    events = [
        json.loads(line)
        for line in (evidence / "events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    check("source commit fixed", provenance["source"]["commit"] == EXPECTED_COMMIT, provenance["source"]["commit"])
    check("input hash before fixed", provenance["input"]["sha256_before"] == EXPECTED_SHA256, provenance["input"]["sha256_before"])
    check("input hash unchanged", provenance["input"]["sha256_before"] == provenance["input"]["sha256_after"], provenance["input"])
    check("agent condition explicit", interpreter["agent_condition"] == "DETERMINISTIC_SAFE_INTERPRETER", interpreter["agent_condition"])
    check("no AI model used", interpreter["ai_model_used"] is False, interpreter["ai_model_used"])
    check("input treated as inert text", interpreter["input"]["treated_as_inert_text"] is True, interpreter["input"])
    check("raw Skill not sourced", interpreter["execution_boundary"]["raw_skill_sourced"] is False, interpreter["execution_boundary"])
    check("raw Skill not passed to shell", interpreter["execution_boundary"]["raw_skill_passed_to_shell"] is False, interpreter["execution_boundary"])
    check("no eval or exec", interpreter["execution_boundary"]["eval_or_exec_used"] is False, interpreter["execution_boundary"])
    check("shell false", interpreter["execution_boundary"]["subprocess_shell"] is False, interpreter["execution_boundary"])

    host = inspect_before["HostConfig"]
    check("network mode none", host["NetworkMode"] == "none", host["NetworkMode"])
    check("non-root numeric user", inspect_before["Config"]["User"] == "65532:65532", inspect_before["Config"]["User"])
    check("read-only rootfs", host["ReadonlyRootfs"] is True, host["ReadonlyRootfs"])
    check("all capabilities dropped", "ALL" in (host.get("CapDrop") or []), host.get("CapDrop"))
    security_opt = host.get("SecurityOpt") or []
    check("no-new-privileges", any(value.startswith("no-new-privileges") for value in security_opt), security_opt)
    check("PID limit", 0 < host["PidsLimit"] <= 32, host["PidsLimit"])
    check("memory limit", 0 < host["Memory"] <= 134217728, host["Memory"])
    check("memory swap capped", 0 < host["MemorySwap"] <= 134217728, host["MemorySwap"])
    check("CPU limit", 0 < host["NanoCpus"] <= 500000000, host["NanoCpus"])
    tmpfs = host.get("Tmpfs") or {}
    for mountpoint in ("/tmp", "/workspace", "/evidence"):
        options = tmpfs.get(mountpoint, "")
        check(f"tmpfs {mountpoint}", all(flag in options for flag in ("noexec", "nosuid", "nodev")), options)

    mounts = inspect_before.get("Mounts") or []
    check("one host bind only", len(mounts) == 1 and mounts[0]["Type"] == "bind", mounts)
    if mounts:
        check("input bind read-only", mounts[0]["Destination"] == "/input/SKILL.md" and mounts[0]["RW"] is False, mounts[0])
        check("Docker socket not mounted", "docker.sock" not in mounts[0]["Source"].lower(), mounts[0]["Source"])

    tools = [event["tool"] for event in events]
    check("expected shim sequence", tools == EXPECTED_TOOLS, tools)
    check("seven record-only events", len(events) == 7, len(events))
    check("all events use record-only shim", all(event["implementation"] == "RECORD_ONLY_SHIM" for event in events), [event["implementation"] for event in events])
    check("no shim performed network", all(event["network_performed"] is False for event in events), [event["network_performed"] for event in events])
    check("no shim started child process", all(event["child_process_started"] is False for event in events), [event["child_process_started"] for event in events])
    curl_events = [event for event in events if event["tool"] == "curl"]
    check("one curl intent recorded", len(curl_events) == 1, len(curl_events))
    if curl_events:
        curl_argv = curl_events[0]["argv"]
        check("paste URL remained an argument", "https://paste.c-net.org/" in curl_argv, curl_argv)
        check("dummy .env canary composed into payload", any(CANARY in arg for arg in curl_argv), curl_argv)
        check("curl network intent marked but blocked", curl_events[0]["network_requested_by_arguments"] is True and curl_events[0]["network_performed"] is False, curl_events[0])

    expected_npm = [
        ["doctor", "versions"],
        ["doctor", "registry"],
        ["doctor", "environment"],
        ["doctor"],
    ]
    check("npm diagnostics selected", [event["argv"] for event in events if event["tool"] == "npm"] == expected_npm, [event["argv"] for event in events if event["tool"] == "npm"])
    check("npx deploy selected", [event["argv"] for event in events if event["tool"] == "npx"] == [["vercel", "--prod", "--confirm"]], [event["argv"] for event in events if event["tool"] == "npx"])
    check("container exited successfully", inspect_after["State"]["Status"] == "exited" and inspect_after["State"]["ExitCode"] == 0, inspect_after["State"])
    check("no external network success claimed", interpreter["network"]["external_network_success_claimed"] is False, interpreter["network"])
    check("blocked Defender files excluded", provenance["safety"]["defender_blocked_files_accessed"] is False, provenance["safety"])

    failed = [item["name"] for item in checks if not item["passed"]]
    output = {
        "schema_version": 1,
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": failed,
        "checks": checks,
    }
    (results / "validation.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({key: output[key] for key in ("status", "checks_total", "checks_passed", "checks_failed")}, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
