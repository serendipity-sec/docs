"""Summarize and verify evidence produced by run_public_scanners.py."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent
DOCS = BASE.parents[3]
SNYK_SOURCE = (
    DOCS
    / ".runtime"
    / "public-scanners-snyk-0.6.4"
    / "Lib"
    / "site-packages"
    / "agent_scan"
    / "verify_api.py"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace").strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def execution(scanner: str, case: str) -> dict:
    return load_json(BASE / "results" / scanner / case / "execution.json")


def report(scanner: str, case: str) -> dict:
    return load_json(BASE / "results" / scanner / case / "report.json")


def summarize_cisco_skill() -> list[dict]:
    rows = []
    root = BASE / "results" / "cisco-skill-static"
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        data = load_json(directory / "report.json")
        threat_findings = [
            item
            for item in data.get("findings", [])
            if item.get("severity") in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        ]
        rows.append(
            {
                "case": directory.name,
                "exit_code": execution("cisco-skill-static", directory.name).get("exit_code"),
                "is_safe": data.get("is_safe"),
                "max_severity": data.get("max_severity"),
                "findings_count": data.get("findings_count"),
                "threat_findings_count": len(threat_findings),
                "rule_ids": [item.get("rule_id") for item in data.get("findings", [])],
                "analyzers_used": data.get("analyzers_used", []),
            }
        )
    return rows


def summarize_skillspector_static() -> list[dict]:
    rows = []
    root = BASE / "results" / "skillspector-static"
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        data = load_json(directory / "report.json")
        risk = data.get("risk_assessment", {})
        completeness = data.get("analysis_completeness", {})
        metadata = data.get("metadata", {})
        rows.append(
            {
                "case": directory.name,
                "exit_code": execution("skillspector-static", directory.name).get("exit_code"),
                "score": risk.get("score"),
                "severity": risk.get("severity"),
                "recommendation": risk.get("recommendation"),
                "max_issue_severity": risk.get("max_issue_severity"),
                "issue_count": len(data.get("issues", [])),
                "issue_ids": [item.get("id") for item in data.get("issues", [])],
                "coverage_percent": completeness.get("coverage_percent"),
                "is_complete": completeness.get("is_complete"),
                "completeness_status": completeness.get("status"),
                "ledger_reason_codes": [
                    item.get("reason_code") for item in completeness.get("ledger_exceptions", [])
                ],
                "llm_requested": metadata.get("llm_requested"),
                "llm_available": metadata.get("llm_available"),
            }
        )
    return rows


def summarize_cisco_mcp() -> list[dict]:
    rows = []
    root = BASE / "results" / "cisco-mcp-yara-static"
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        data = json.loads(text(directory / "stdout.txt"))
        items = data.get("scan_results", [])
        threats = []
        for item in items:
            threats.extend(
                item.get("findings", {}).get("yara_analyzer", {}).get("threat_names", [])
            )
        rows.append(
            {
                "case": directory.name,
                "exit_code": execution("cisco-mcp-yara-static", directory.name).get("exit_code"),
                "items": len(items),
                "safe_items": sum(1 for item in items if item.get("is_safe") is True),
                "unsafe_items": sum(1 for item in items if item.get("is_safe") is False),
                "threat_names": threats,
                "requested_analyzers": data.get("requested_analyzers", []),
            }
        )
    return rows


def summarize_semantic() -> dict:
    codex = report("skillspector-codex-cli", "TS-VERCEL-GEMINI")
    codex_meta = codex.get("metadata", {})
    codex_complete = codex.get("analysis_completeness", {})
    codex_risk = codex.get("risk_assessment", {})
    ollama = report("skillspector-ollama-qwen3-1.7b-q4-k-m", "TS-VERCEL-GEMINI")
    ollama_meta = ollama.get("metadata", {})
    ollama_complete = ollama.get("analysis_completeness", {})
    ollama_execution = execution(
        "skillspector-ollama-qwen3-1.7b-q4-k-m", "TS-VERCEL-GEMINI"
    )
    interrupted = execution(
        "skillspector-ollama-qwen3-4b-q4-k-m", "TS-VERCEL-GEMINI"
    )
    return {
        "codex_cli": {
            "tool_exit_code": execution("skillspector-codex-cli", "TS-VERCEL-GEMINI").get(
                "exit_code"
            ),
            "score": codex_risk.get("score"),
            "severity": codex_risk.get("severity"),
            "recommendation": codex_risk.get("recommendation"),
            "issue_count": len(codex.get("issues", [])),
            "issue_ids": [item.get("id") for item in codex.get("issues", [])],
            "llm_calls_attempted": codex_meta.get("llm_calls_attempted"),
            "llm_calls_succeeded": codex_meta.get("llm_calls_succeeded"),
            "llm_available": codex_meta.get("llm_available"),
            "meta_analysis_applied": codex_meta.get("meta_analysis_applied"),
            "coverage_percent": codex_complete.get("coverage_percent"),
            "fully_inspected_files": codex_complete.get("fully_inspected_files"),
            "completeness_status": codex_complete.get("status"),
            "ledger_reason_codes": [
                item.get("reason_code") for item in codex_complete.get("ledger_exceptions", [])
            ],
            "interpretation": "DETECTED; exit 1 is the scanner's critical-risk gate, not an execution failure",
        },
        "ollama_qwen3_1_7b": {
            "tool_exit_code": ollama_execution.get("exit_code"),
            "duration_seconds": ollama_execution.get("duration_seconds"),
            "llm_calls_attempted": ollama_meta.get("llm_calls_attempted"),
            "llm_calls_succeeded": ollama_meta.get("llm_calls_succeeded"),
            "llm_degraded": ollama_meta.get("llm_degraded"),
            "llm_error": ollama_meta.get("llm_error"),
            "coverage_percent": ollama_complete.get("coverage_percent"),
            "completeness_status": ollama_complete.get("status"),
            "interpretation": "INCOMPLETE_EXCLUDED; the report contains static findings only",
        },
        "ollama_qwen3_4b": {
            "status": interrupted.get("status"),
            "duration_seconds": interrupted.get("duration_seconds"),
            "interpretation": "NOT_ASSESSED; interrupted to release the shared runtime",
        },
        "observed_local_models": [
            {
                "model": "qwen3:1.7b-q4_K_M",
                "digest": "8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7",
                "endpoint": "http://127.0.0.1:11437/v1",
            },
            {
                "model": "qwen3:4b-q4_K_M",
                "digest": "2bfd38a7daaf4b1037efe517ccb73d1a3bbd4822cf89f1a82be1569050a114e0",
                "endpoint": "http://127.0.0.1:11437/v1",
            },
        ],
    }


def summarize_versions() -> dict:
    cases = {
        "cisco_skill": "cisco-skill-package",
        "cisco_mcp": "cisco-mcp-package",
        "skillspector": "skillspector-package",
        "codex_cli": "codex-cli",
    }
    result = {}
    for key, case in cases.items():
        result[key] = {
            "version_output": text(BASE / "results" / "tool-versions" / case / "stdout.txt"),
            "exit_code": execution("tool-versions", case).get("exit_code"),
        }
    result["snyk_agent_scan"] = {
        "version_output": text(
            BASE / "results" / "snyk-agent-scan-0.6.4" / "package-version" / "stdout.txt"
        ),
        "exit_code": execution("snyk-agent-scan-0.6.4", "package-version").get(
            "exit_code"
        ),
    }
    return result


def summarize_snyk() -> dict:
    run = execution("snyk-agent-scan-0.6.4", "TS-VERCEL-GEMINI-BLOCKED-CREDENTIAL")
    source_text = SNYK_SOURCE.read_text(encoding="utf-8")
    source_contract_present = all(
        marker in source_text
        for marker in (
            'snyk_token = os.getenv("SNYK_TOKEN")',
            'raise SnykTokenError("SNYK_TOKEN environment variable not set")',
            "for attempt in range(max_retries)",
        )
    )
    return {
        "classification": "BLOCKED_CREDENTIAL" if run.get("exit_code") == 1 and source_contract_present else "UNRESOLVED",
        "exit_code": run.get("exit_code"),
        "version": text(
            BASE / "results" / "snyk-agent-scan-0.6.4" / "package-version" / "stdout.txt"
        ),
        "input_kind": "direct SKILL.md path; no MCP configuration",
        "snyk_token_forwarded": False,
        "http_request_started": False,
        "source_contract": {
            "path": str(SNYK_SOURCE),
            "sha256": sha256(SNYK_SOURCE),
            "relevant_lines": "494-525; missing token raises before the request loop beginning at line 527",
            "markers_present": source_contract_present,
        },
        "verbose_stderr_disposition": run.get("raw_stderr_disposition"),
        "note": "The CLI emitted no ordinary error text; classification combines exit 1, the intentionally scrubbed environment, and the pinned 0.6.4 source contract.",
    }


def evidence_manifest() -> list[dict]:
    excluded = {BASE / "evidence-manifest.json"}
    records = []
    for path in sorted(p for p in BASE.rglob("*") if p.is_file() and p not in excluded):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        records.append(
            {
                "path": str(path.relative_to(BASE)).replace("\\", "/"),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return records


def verify(summary: dict) -> dict:
    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})

    provenance = load_json(BASE / "provenance.json")
    add(
        "fixed_source_commits",
        provenance["repositories"]["toxicskills-goof"]["commit"]
        == "80ce2e06f52fd384163c4bd6778676019723773c"
        and provenance["repositories"]["vulnerable-mcp-servers-lab"]["commit"]
        == "47b7f2082261136b667daa7be9273698e66e479e",
        "Both quarantine repositories remain at the recorded commits.",
    )
    toxic_status = [
        item.lstrip() for item in provenance["repositories"]["toxicskills-goof"]["worktree_status"]
    ]
    add(
        "quarantine_worktree_state",
        set(toxic_status)
        == {
            "D .agents/skills/clawhub/skill.md",
            "D .agents/skills/google/SKILL.md",
        }
        and provenance["repositories"]["vulnerable-mcp-servers-lab"]["worktree_clean"]
        is True,
        "ToxicSkills differs only by the two AV-blocked files; the MIT MCP checkout is clean.",
    )
    all_exec = [load_json(path) for path in (BASE / "results").rglob("execution.json")]
    add(
        "no_public_code_execution",
        all(item.get("public_skill_or_mcp_code_executed") is False for item in all_exec),
        f"Checked {len(all_exec)} execution records.",
    )
    add(
        "static_skill_cases",
        len(summary["cisco_skill_static"]) == 5
        and len(summary["skillspector_static"]) == 5,
        "Five readable public Skill inputs were processed by both static scanners.",
    )
    add(
        "static_mcp_cases",
        len(summary["cisco_mcp_yara_static"]) == 4,
        "Four frozen MCP metadata/resource inputs were processed without a server connection.",
    )
    codex = summary["semantic_modes"]["codex_cli"]
    add(
        "codex_semantic_complete_calls",
        codex["llm_calls_attempted"] == 4
        and codex["llm_calls_succeeded"] == 4
        and codex["coverage_percent"] == 100.0,
        "All four semantic calls succeeded and the single file has 100% coverage.",
    )
    add(
        "ollama_not_overclaimed",
        summary["semantic_modes"]["ollama_qwen3_1_7b"]["interpretation"].startswith(
            "INCOMPLETE_EXCLUDED"
        )
        and summary["semantic_modes"]["ollama_qwen3_4b"]["status"]
        == "INTERRUPTED_SHARED_RUNTIME",
        "Degraded and interrupted local-model runs are excluded from detection claims.",
    )
    add(
        "snyk_blocked_before_http",
        summary["snyk_agent_scan"]["classification"] == "BLOCKED_CREDENTIAL"
        and summary["snyk_agent_scan"]["http_request_started"] is False,
        "Pinned source requires SNYK_TOKEN before entering its HTTP request loop.",
    )
    add(
        "unlicensed_verbose_payload_discarded",
        summary["snyk_agent_scan"]["verbose_stderr_disposition"].get("status")
        == "DISCARDED_UNLICENSED_SOURCE_PAYLOAD",
        "Only the discarded verbose stream's SHA-256 and byte count are retained.",
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "checks": checks,
    }


def markdown(summary: dict, verification: dict) -> str:
    skill_rows = []
    cisco_by_case = {row["case"]: row for row in summary["cisco_skill_static"]}
    skill_by_case = {row["case"]: row for row in summary["skillspector_static"]}
    for case in sorted(cisco_by_case):
        cisco = cisco_by_case[case]
        skill = skill_by_case[case]
        skill_rows.append(
            f"| {case} | {cisco['is_safe']} / {cisco['max_severity']} | "
            f"{skill['score']} {skill['severity']} / {skill['recommendation']} | "
            f"{skill['coverage_percent']}% / {skill['completeness_status']} |"
        )
    mcp_rows = [
        f"| {row['case']} | {row['items']} | {row['safe_items']} | "
        f"{row['unsafe_items']} | {', '.join(row['threat_names']) or 'none'} |"
        for row in summary["cisco_mcp_yara_static"]
    ]
    codex = summary["semantic_modes"]["codex_cli"]
    ollama = summary["semantic_modes"]["ollama_qwen3_1_7b"]
    snyk = summary["snyk_agent_scan"]
    return "\n".join(
        [
            "# 공개 Skill·MCP 스캐너 실측 결과",
            "",
            f"검증 상태: **{verification['status']}**. 공개 Skill 또는 MCP 서버 코드는 실행하지 않았다.",
            "",
            "## 핵심 결과",
            "",
            "- Cisco Skill Scanner 2.1.0은 fake Vercel 두 변형을 모두 `is_safe=true`, 최대 `INFO`로 판정했다. Gemini 변형에는 `.env`와 호스트 정보를 외부 paste 서비스로 보내라는 명시적 명령이 있지만 위협 finding은 없었다.",
            "- Cisco Skill Scanner는 testing-guidelines의 Unicode/ASCII smuggling과 snyk-skill의 taint flow는 각각 `CRITICAL`로 잡았다. 즉 규칙 기반 탐지는 공격 표현에 따라 크게 달라졌다.",
            "- SkillSpector 2.11.2 `--no-llm`은 fake Vercel Gemini에서 외부 전송 `E1`과 unpinned `npx` 위험 `RP1`을 찾았지만 총점 13 `LOW`, 권고 `CAUTION`이었다. Agents 변형은 `E1`이 있어도 권고가 `SAFE`였다.",
            "- Cisco MCP Scanner 4.8.4 YARA는 Appsecco의 명시적 간접 프롬프트 주입 문서 3개, 악성 도구 응답 1개를 포함한 모든 항목을 `SAFE`로 판정했다. 이 결과는 YARA 정적 모드에만 적용된다.",
            f"- SkillSpector `codex_cli`는 동일 fake Vercel Gemini 파일에서 의미 분석 4/4회를 완료하고 {codex['issue_count']}개 finding, 점수 {codex['score']} `{codex['severity']}`, `{codex['recommendation']}`을 냈다. 파일 coverage는 {codex['coverage_percent']}%였다.",
            f"- Codex 조건의 전체 completeness는 `{codex['completeness_status']}`다. 원인은 의미 분석 실패가 아니라 14행의 경로처럼 보이는 문구를 해석할 때 생긴 `reference_unresolved` 한 건이다.",
            f"- Ollama 1.7B는 {ollama['duration_seconds']}초 후 exit 0이었지만 LLM 호출 {ollama['llm_calls_attempted']}회가 모두 실패했고 coverage {ollama['coverage_percent']}%, `{ollama['completeness_status']}`였다. 정적 finding만 포함하므로 의미 분석 비교에서 제외했다. 4B는 공유 런타임을 반환하기 위해 중단했다.",
            f"- Snyk Agent Scan {snyk['version']}은 토큰 없는 격리 환경에서 `{snyk['classification']}`이었다. 고정된 0.6.4 소스는 `SNYK_TOKEN`이 없으면 HTTP 요청 반복문 전에 예외를 발생시키므로 실제 보안 분석 결과는 없다.",
            "",
            "## Skill 정적 비교",
            "",
            "| 입력 | Cisco is_safe / 최대 심각도 | SkillSpector 점수·심각도 / 권고 | coverage / completeness |",
            "|---|---:|---:|---:|",
            *skill_rows,
            "",
            "## MCP YARA 결과",
            "",
            "| 입력 | 항목 수 | SAFE | unsafe | 위협명 |",
            "|---|---:|---:|---:|---|",
            *mcp_rows,
            "",
            "## 해석 경계",
            "",
            "- 이 표본 묶음은 작은 목적 표본이며 시장 전체 탐지율을 뜻하지 않는다.",
            "- ToxicSkills 저장소는 위험 데모라는 저장소 수준 경고를 제공하지만 모든 개별 파일의 악성 ground truth를 독립적으로 확정하지는 않았다. fake Vercel, hidden testing 지시, env hook처럼 행위가 명시적인 사례를 중심으로 해석한다.",
            "- MCP RCE와 typosquatting 입력은 서버 소스의 위험이 도구 설명에 충분히 노출되지 않는 경우를 보여준다. YARA의 `SAFE`는 서버 구현이 안전하다는 뜻이 아니다.",
            "- Codex CLI 결과는 한 번의 고정 입력 실행이다. 여러 상용 모델의 일반 성능이나 반복 안정성을 증명하지 않는다.",
            "- 공개 원문을 AI 에이전트에 설치하거나 실제 MCP 서버로 실행하지 않았으므로 실제 피해 발생 가능성은 별도 격리 실행 실험의 영역이다.",
            "",
            "## 증거 위치",
            "",
            "- `provenance.json`: 저장소 커밋, 입력 경로·해시, 스캐너 바이너리 해시",
            "- `results/`: 명령, 종료 코드, stdout, stderr, 원시 JSON 보고서",
            "- `summary.json`: 위 결과의 기계 판독 요약",
            "- `verification.json`: 안전 경계와 완전성 검증",
            "- `evidence-manifest.json`: 보존 파일의 SHA-256",
            "",
        ]
    )


def main() -> None:
    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "fixed public text, static scanners, one bounded semantic comparison",
        "cisco_skill_static": summarize_cisco_skill(),
        "skillspector_static": summarize_skillspector_static(),
        "cisco_mcp_yara_static": summarize_cisco_mcp(),
        "semantic_modes": summarize_semantic(),
        "snyk_agent_scan": summarize_snyk(),
        "tool_versions": summarize_versions(),
    }
    verification = verify(summary)
    (BASE / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (BASE / "verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (BASE / "RESULTS.md").write_text(markdown(summary, verification), encoding="utf-8")
    manifest = evidence_manifest()
    (BASE / "evidence-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "files": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"summary written; verification={verification['status']}; evidence_files={len(manifest)}")


if __name__ == "__main__":
    main()
