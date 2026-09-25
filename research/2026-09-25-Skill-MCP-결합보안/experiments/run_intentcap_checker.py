"""Exercise only the inspected, standard-library IntentCap checker on synthetic traces.

No agent, MCP server, target skill, API, or sink is executed. The checkout is
external and pinned; no third-party source is copied into this submission.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

PIN = "1886fd50dbd51344c62acd1d224375054ac076e9"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    commit = subprocess.check_output(
        ["git", "-C", str(args.checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    assert commit == PIN, "Review a changed checkout before importing its checker"
    source = args.checkout / "src/intentcap/checker.py"
    spec = importlib.util.spec_from_file_location("reviewed_intentcap_checker", source)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    trace = {
        "labels": {"user:task": {"allowed": {"select": ["destination"]}},
                   "document:body": {"allowed": {}}},
        "leases": [{"id": "task-lease", "op": "publish", "object": "mock:issues",
                    "holder": "report-agent", "args": {"repo": {"equals": "team/private"}},
                    "allowed_arg_keys": ["repo", "body"], "budget": {"invocations": 1},
                    "control_may_depend_on": ["user:task"],
                    "data_may_depend_on": ["document:body"],
                    "intent": {"must_derive_from": ["user:task"],
                               "requires_approval": ["approval:team-only"]}}],
        "events": [{"id": "publish-1", "op": "publish", "object": "mock:issues",
                    "holder": "report-agent", "args": {"repo": "team/private", "body": "CANARY SUMMARY"},
                    "decision": "destination", "mode": "select",
                    "control_provenance": ["user:task"],
                    "data_provenance": ["document:body"],
                    "intent_provenance": ["user:task"], "approvals": ["approval:team-only"]}]
    }
    cases = []
    def record(name: str, fixture: dict, expected: list[bool]) -> None:
        verdicts = module.check_trace(fixture)
        actual = [item["allowed"] for item in verdicts]
        cases.append({"name": name, "trace": fixture, "expected": expected,
                      "actual": actual, "verdicts": verdicts})
        assert actual == expected, (name, verdicts)

    record("authorized_destination_and_source", copy.deepcopy(trace), [True])
    changed = copy.deepcopy(trace)
    changed["events"][0]["control_provenance"] = ["document:body"]
    record("document_cannot_choose_destination", changed, [False])
    changed = copy.deepcopy(trace)
    changed["events"][0]["args"]["repo"] = "public/demo"
    record("destination_outside_lease", changed, [False])
    changed = copy.deepcopy(trace)
    changed["events"].append(copy.deepcopy(changed["events"][0]))
    changed["events"][1]["id"] = "publish-2"
    record("single_use_budget", changed, [True, False])
    result = {"checked_on": "2026-09-25", "repository": "https://github.com/yunwei37/agentcap",
              "commit": commit, "checker_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "python": sys.version, "scope": "pure check_trace; synthetic input; no live enforcement",
              "limitations": ["Hand-authored trusted labels, leases, and provenance",
                              "No automatic extraction or provenance authenticity validation",
                              "Four cases are a behavior check, not an accuracy or ASR evaluation"],
              "cases": cases}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"cases": len(cases), "events": sum(len(c["actual"]) for c in cases),
                      "all_expected": True, "target_actions_executed": 0}))


if __name__ == "__main__":
    main()
