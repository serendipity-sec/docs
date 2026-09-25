"""Exercise only the upstream pure graph search on synthetic capability nodes.

Does not invoke the attack authoring, victim agent, LLM, tools, or benchmark.
Upstream is imported from an explicitly provided checkout, not redistributed.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess


def main(repo: Path, output: Path):
    source = repo / "scripts" / "chain_search_ksp.py"
    spec = importlib.util.spec_from_file_location("upstream_graph", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    nodes = [{"skill_id": name, "r": 0.5, "roles": {"t1": {role: True}}}
             for name, role in [("read", "source"), ("summarize", "bridge"), ("publish", "terminal")]]
    connected = {"nodes": nodes, "edges": [{"src": "read", "dst": "summarize", "w": 1.0},
                                          {"src": "summarize", "dst": "publish", "w": 1.0}]}
    broken = {"nodes": nodes, "edges": connected["edges"][:1]}
    result = {
        "commit": subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip(),
        "scope": "Pure graph search smoke test only; roles and edges hand-authored; not ASR reproduction",
        "connected": module.search_candidates(connected, "t1", 10, chain_len=3),
        "broken": module.search_candidates(broken, "t1", 10, chain_len=3)
    }
    assert result["connected"][0]["path"] == ["read", "summarize", "publish"]
    assert result["broken"] == []
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    main(a.repo.resolve(), a.output.resolve())
