"""Run Cisco MCP Scanner's static JSON/YARA path. No live MCP connections."""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
from datetime import datetime, timezone


async def main(work: Path, evidence: Path):
    os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    from mcpscanner.core.analyzers.static_analyzer import StaticAnalyzer
    from mcpscanner.core.analyzers.yara_analyzer import YaraAnalyzer
    fixtures_path = Path(__file__).with_name("fixtures.json")
    fixtures = json.loads(fixtures_path.read_text(encoding="utf-8"))
    scanner = StaticAnalyzer(analyzers=[YaraAnalyzer()])
    work.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in ("mcp_snapshot", "mcp_positive_control", "mcp_rule_wiring_control"):
        target = work / f"{name}.json"
        target.write_text(json.dumps(fixtures[name]), encoding="utf-8")
        result = await scanner.scan_tools_file(target)
        serialized = []
        for r in result:
            item = dict(r)
            item["findings"] = [vars(f) for f in r["findings"]]
            serialized.append(item)
        rows.append({"fixture": name, "result": serialized})
    output = {"time_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
              "scanner_version": importlib.metadata.version("cisco-ai-mcp-scanner"),
              "fixtures_sha256": hashlib.sha256(fixtures_path.read_bytes()).hexdigest(),
              "mode": "StaticAnalyzer + YaraAnalyzer only; no server, LLM, API or behavioral-code analysis", "runs": rows}
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "mcp-scanner-results.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False))
    if any(item.get("status") != "completed" for row in rows for item in row["result"]):
        raise SystemExit("A scan did not complete; inspect evidence before interpreting findings.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--evidence", type=Path, required=True)
    a = p.parse_args()
    asyncio.run(main(a.work.resolve(), a.evidence.resolve()))
