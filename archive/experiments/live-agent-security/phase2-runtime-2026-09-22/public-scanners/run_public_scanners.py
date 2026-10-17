"""Run public-sample scanners without executing any public Skill or MCP server.

The runner points static Skill scanners at fixed files in docs/.runtime/quarantine.
It never invokes those files as agent skills. MCP Scanner receives only frozen JSON
metadata copied from the MIT-licensed Appsecco lab; it never receives an MCP config.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


BASE = Path(__file__).resolve().parent
DOCS = BASE.parents[3]
WORKSPACE = DOCS.parent
QUARANTINE = DOCS / ".runtime" / "quarantine"
SCANNER_RUNTIME = WORKSPACE / "platform" / ".runtime" / "live-agent-security-scanners"
ISOLATED_HOME = DOCS / ".runtime" / "public-scanners-isolated-home"
SNYK_RUNTIME = DOCS / ".runtime" / "public-scanners-snyk-0.6.4"

TOXIC_REPO = QUARANTINE / "toxicskills-goof"
MCP_REPO = QUARANTINE / "vulnerable-mcp-servers-lab"

SKILL_CASES = {
    "TS-VERCEL-AGENTS": TOXIC_REPO / ".agents" / "skills" / "vercel",
    "TS-VERCEL-GEMINI": TOXIC_REPO / ".gemini" / "skills" / "vercel",
    "TS-TESTING-GUIDELINES": TOXIC_REPO / ".gemini" / "skills" / "testing-guidelines",
    "TS-CLAWHUB": TOXIC_REPO / ".gemini" / "skills" / "clawhub",
    "TS-SNYK-SKILL": TOXIC_REPO / ".gemini" / "skills" / "snyk-skill",
}

EXPECTED_BUT_BLOCKED = {
    "TS-GOOGLE": TOXIC_REPO / ".agents" / "skills" / "google" / "SKILL.md",
    "TS-CLAWHUB-AGENTS": TOXIC_REPO / ".agents" / "skills" / "clawhub" / "skill.md",
}

MCP_CASES = {
    "MCP-INDIRECT-INJECTION": (BASE / "inputs" / "mcp" / "appsecco-indirect-injection-resources.json", "resources"),
    "MCP-MALICIOUS-TOOLS": (BASE / "inputs" / "mcp" / "appsecco-malicious-tools-resources.json", "resources"),
    "MCP-TYPOSQUAT-METADATA": (BASE / "inputs" / "mcp" / "appsecco-typosquat-tools.json", "tools"),
    "MCP-RCE-METADATA": (BASE / "inputs" / "mcp" / "appsecco-rce-tools.json", "tools"),
}

MCP_SOURCE_FILES = {
    "MCP-INDIRECT-INJECTION": MCP_REPO / "vulnerable-mcp-server-indirect-prompt-injection" / "index.js",
    "MCP-MALICIOUS-TOOLS": MCP_REPO / "vulnerable-mcp-server-malicious-tools" / "index.js",
    "MCP-TYPOSQUAT-METADATA": MCP_REPO / "vulnerable-mcp-server-namespace-typosquatting" / "index.js",
    "MCP-RCE-METADATA": MCP_REPO / "vulnerable-mcp-server-malicious-code-exec" / "index.js",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(DOCS.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def git_value(repo: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def inspect_file(path: Path) -> dict:
    record = {"path": relative_or_absolute(path)}
    try:
        record.update(
            status="READABLE",
            size_bytes=path.stat().st_size,
            sha256=sha256(path),
        )
    except (OSError, PermissionError) as exc:
        record.update(status="UNREADABLE_OR_ABSENT", error=f"{type(exc).__name__}: {exc}")
    return record


def build_manifest() -> dict:
    toxic_status = git_value(TOXIC_REPO, "status", "--short") or ""
    mcp_status = git_value(MCP_REPO, "status", "--short") or ""
    skill_inputs = {}
    for case, directory in SKILL_CASES.items():
        skill_inputs[case] = inspect_file(directory / "SKILL.md")

    blocked = {case: inspect_file(path) for case, path in EXPECTED_BUT_BLOCKED.items()}
    for record in blocked.values():
        if record["status"] != "READABLE":
            record["classification"] = "AV_BLOCKED_OR_REMOVED; no bypass attempted"

    mcp_inputs = {}
    for case, (frozen, kind) in MCP_CASES.items():
        mcp_inputs[case] = {
            "kind": kind,
            "frozen_input": inspect_file(frozen),
            "public_source": inspect_file(MCP_SOURCE_FILES[case]),
        }

    scanner_binaries = {
        "cisco-skill": inspect_file(
            SCANNER_RUNTIME / "cisco-skill" / "Scripts" / "skill-scanner.exe"
        ),
        "cisco-mcp": inspect_file(
            SCANNER_RUNTIME / "cisco-mcp" / "Scripts" / "mcp-scanner.exe"
        ),
        "skillspector": inspect_file(
            SCANNER_RUNTIME / "skillspector" / "Scripts" / "skillspector.exe"
        ),
    }

    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "safety": {
            "public_skill_or_mcp_code_executed": False,
            "skill_handling": "static scanners receive a directory path only",
            "mcp_handling": "Cisco static subcommand receives frozen JSON only; no MCP config or server command",
            "credential_values_recorded": False,
        },
        "repositories": {
            "toxicskills-goof": {
                "path": relative_or_absolute(TOXIC_REPO),
                "remote": git_value(TOXIC_REPO, "remote", "get-url", "origin"),
                "commit": git_value(TOXIC_REPO, "rev-parse", "HEAD"),
                "worktree_clean": not bool(toxic_status),
                "worktree_status": toxic_status.splitlines(),
                "license": "NO_ROOT_LICENSE_FOUND; source text is not copied into this artifact",
            },
            "vulnerable-mcp-servers-lab": {
                "path": relative_or_absolute(MCP_REPO),
                "remote": git_value(MCP_REPO, "remote", "get-url", "origin"),
                "commit": git_value(MCP_REPO, "rev-parse", "HEAD"),
                "worktree_clean": not bool(mcp_status),
                "worktree_status": mcp_status.splitlines(),
                "license": "MIT; notice retained at inputs/mcp/LICENSE-appsecco.txt",
            },
        },
        "skill_inputs": skill_inputs,
        "blocked_or_absent_skill_inputs": blocked,
        "mcp_inputs": mcp_inputs,
        "scanner_binaries": scanner_binaries,
    }


def base_environment(*, codex_auth: bool = False) -> dict[str, str]:
    allowed = {
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "PATHEXT",
        "PATH",
        "TEMP",
        "TMP",
        "NUMBER_OF_PROCESSORS",
        "PROCESSOR_ARCHITECTURE",
        "USERNAME",
        "USERDOMAIN",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
    }
    env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    ISOLATED_HOME.mkdir(parents=True, exist_ok=True)
    env.update(
        {
            "HOME": str(ISOLATED_HOME),
            "USERPROFILE": str(ISOLATED_HOME),
            "APPDATA": str(ISOLATED_HOME / "AppData"),
            "LOCALAPPDATA": str(ISOLATED_HOME / "LocalAppData"),
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "NO_COLOR": "1",
            "LITELLM_LOCAL_MODEL_COST_MAP": "True",
            "MCP_SCANNER_VIRUSTOTAL_ENABLED": "false",
            "LANGCHAIN_TRACING_V2": "false",
            "LANGSMITH_TRACING": "false",
        }
    )
    if codex_auth:
        # SkillSpector's codex_cli provider invokes Codex with an ephemeral,
        # read-only, tools-disabled configuration. User roots are retained only
        # so the installed CLI can find its existing login session.
        for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "CODEX_HOME"):
            if os.environ.get(key):
                env[key] = os.environ[key]
    return env


def selected_inputs(paths: Iterable[Path]) -> list[dict]:
    records: list[dict] = []
    for path in paths:
        if path.is_dir():
            files = sorted(p for p in path.rglob("*") if p.is_file())
        else:
            files = [path]
        records.extend(inspect_file(file) for file in files)
    return records


def execute(
    scanner: str,
    case: str,
    command: list[Path | str],
    *,
    inputs: Iterable[Path] = (),
    env_overrides: dict[str, str] | None = None,
    codex_auth: bool = False,
    timeout: int = 300,
) -> dict:
    destination = BASE / "results" / scanner / case
    destination.mkdir(parents=True, exist_ok=True)
    command_text = [str(part) for part in command]
    record = {
        "schema_version": 1,
        "scanner": scanner,
        "case": case,
        "command": command_text,
        "cwd": relative_or_absolute(ISOLATED_HOME),
        "inputs": selected_inputs(inputs),
        "started_at": utc_now(),
        "status": "RUNNING",
        "public_skill_or_mcp_code_executed": False,
        "environment_condition": {
            key: value
            for key, value in (env_overrides or {}).items()
            if key not in {"OPENAI_API_KEY", "SNYK_TOKEN"}
        },
        "credential_values_recorded": False,
    }
    (destination / "execution.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    env = base_environment(codex_auth=codex_auth)
    if env_overrides:
        env.update(env_overrides)
    start = time.monotonic()
    try:
        result = subprocess.run(
            command_text,
            cwd=ISOLATED_HOME,
            env=env,
            capture_output=True,
            timeout=timeout,
        )
        (destination / "stdout.txt").write_bytes(result.stdout)
        (destination / "stderr.txt").write_bytes(result.stderr)
        record.update(status="EXITED", exit_code=result.returncode)
    except subprocess.TimeoutExpired as exc:
        (destination / "stdout.txt").write_bytes(exc.stdout or b"")
        (destination / "stderr.txt").write_bytes(exc.stderr or b"")
        record.update(status="TIMEOUT", exit_code=None)
    except KeyboardInterrupt:
        (destination / "stdout.txt").write_text("", encoding="utf-8")
        (destination / "stderr.txt").write_text(
            "Interrupted because the shared local-model runtime was needed by another experiment.\n",
            encoding="utf-8",
        )
        record.update(status="INTERRUPTED_SHARED_RUNTIME", exit_code=None)
    except OSError as exc:
        (destination / "stdout.txt").write_text("", encoding="utf-8")
        (destination / "stderr.txt").write_text(str(exc), encoding="utf-8")
        record.update(status="LAUNCH_ERROR", exit_code=None, error=f"{type(exc).__name__}: {exc}")
    record["duration_seconds"] = round(time.monotonic() - start, 3)
    record["finished_at"] = utc_now()
    (destination / "execution.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"{scanner}/{case}: {record['status']} exit={record.get('exit_code')} "
        f"duration={record['duration_seconds']}s",
        flush=True,
    )
    return record


def report_path(scanner: str, case: str) -> Path:
    path = BASE / "results" / scanner / case / "report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def run_static_skill_scanners() -> None:
    cisco = SCANNER_RUNTIME / "cisco-skill" / "Scripts" / "skill-scanner.exe"
    skillspector = SCANNER_RUNTIME / "skillspector" / "Scripts" / "skillspector.exe"
    for case, target in SKILL_CASES.items():
        skill_file = target / "SKILL.md"
        if inspect_file(skill_file)["status"] != "READABLE":
            continue
        cisco_report = report_path("cisco-skill-static", case)
        execute(
            "cisco-skill-static",
            case,
            [
                cisco,
                "scan",
                target,
                "--use-behavioral",
                "--format",
                "json",
                "--output",
                cisco_report,
            ],
            inputs=[skill_file],
            timeout=300,
        )
        skill_report = report_path("skillspector-static", case)
        execute(
            "skillspector-static",
            case,
            [
                skillspector,
                "scan",
                target,
                "--no-llm",
                "--format",
                "json",
                "--output",
                skill_report,
            ],
            inputs=[skill_file],
            timeout=300,
        )


def run_static_mcp_scanner() -> None:
    scanner = SCANNER_RUNTIME / "cisco-mcp" / "Scripts" / "mcp-scanner.exe"
    for case, (target, kind) in MCP_CASES.items():
        execute(
            "cisco-mcp-yara-static",
            case,
            [
                scanner,
                "--analyzers",
                "yara",
                "--format",
                "raw",
                "static",
                f"--{kind}",
                target,
            ],
            inputs=[target, MCP_SOURCE_FILES[case]],
            timeout=300,
        )


def run_skillspector_ollama() -> None:
    scanner = SCANNER_RUNTIME / "skillspector" / "Scripts" / "skillspector.exe"
    case = "TS-VERCEL-GEMINI"
    target = SKILL_CASES[case]
    for model in ("qwen3:1.7b-q4_K_M", "qwen3:4b-q4_K_M"):
        slug = model.replace(":", "-").replace("_", "-").lower()
        output = report_path(f"skillspector-ollama-{slug}", case)
        execute(
            f"skillspector-ollama-{slug}",
            case,
            [scanner, "scan", target, "--format", "json", "--output", output],
            inputs=[target / "SKILL.md"],
            env_overrides={
                "SKILLSPECTOR_PROVIDER": "ollama",
                "OLLAMA_BASE_URL": "http://127.0.0.1:11437/v1",
                "SKILLSPECTOR_MODEL": model,
                "SKILLSPECTOR_TEMPERATURE": "0",
                "SKILLSPECTOR_SEED": "20260922",
            },
            timeout=900,
        )


def run_skillspector_codex() -> None:
    scanner = SCANNER_RUNTIME / "skillspector" / "Scripts" / "skillspector.exe"
    case = "TS-VERCEL-GEMINI"
    target = SKILL_CASES[case]
    output = report_path("skillspector-codex-cli", case)
    execute(
        "skillspector-codex-cli",
        case,
        [scanner, "scan", target, "--format", "json", "--output", output],
        inputs=[target / "SKILL.md"],
        env_overrides={"SKILLSPECTOR_PROVIDER": "codex_cli"},
        codex_auth=True,
        timeout=1200,
    )


def run_versions() -> None:
    tools = {
        "cisco-skill": SCANNER_RUNTIME / "cisco-skill" / "Scripts" / "skill-scanner.exe",
        "cisco-mcp": SCANNER_RUNTIME / "cisco-mcp" / "Scripts" / "mcp-scanner.exe",
        "skillspector": SCANNER_RUNTIME / "skillspector" / "Scripts" / "skillspector.exe",
    }
    for name, executable in tools.items():
        execute("tool-versions", name, [executable, "--version"], timeout=120)
    distributions = {
        "cisco-skill-package": (
            SCANNER_RUNTIME / "cisco-skill" / "Scripts" / "python.exe",
            "cisco-ai-skill-scanner",
        ),
        "cisco-mcp-package": (
            SCANNER_RUNTIME / "cisco-mcp" / "Scripts" / "python.exe",
            "cisco-ai-mcp-scanner",
        ),
        "skillspector-package": (
            SCANNER_RUNTIME / "skillspector" / "Scripts" / "python.exe",
            "skillspector",
        ),
    }
    for case, (python, distribution) in distributions.items():
        execute(
            "tool-versions",
            case,
            [
                python,
                "-c",
                f"import importlib.metadata; print(importlib.metadata.version({distribution!r}))",
            ],
            timeout=120,
        )
    codex = shutil.which("codex")
    if codex:
        execute(
            "tool-versions",
            "codex-cli",
            [codex, "--version"],
            codex_auth=True,
            timeout=120,
        )


def install_and_probe_snyk() -> None:
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv was not found on PATH")
    python = SNYK_RUNTIME / "Scripts" / "python.exe"
    scanner = SNYK_RUNTIME / "Scripts" / "snyk-agent-scan.exe"
    if not python.exists():
        execute(
            "snyk-agent-scan-0.6.4",
            "setup-venv",
            [uv, "venv", "--python", "3.13", SNYK_RUNTIME],
            timeout=300,
        )
    execute(
        "snyk-agent-scan-0.6.4",
        "setup-install",
        [uv, "pip", "install", "--python", python, "snyk-agent-scan==0.6.4"],
        timeout=600,
    )
    execute(
        "snyk-agent-scan-0.6.4",
        "package-version",
        [
            python,
            "-c",
            "import importlib.metadata; print(importlib.metadata.version('snyk-agent-scan'))",
        ],
        timeout=120,
    )
    execute(
        "snyk-agent-scan-0.6.4",
        "scan-help",
        [scanner, "scan", "--help"],
        timeout=120,
    )
    # Direct SKILL.md input only. No MCP config can be interpreted or launched.
    # SNYK_TOKEN is intentionally absent from base_environment().
    target = SKILL_CASES["TS-VERCEL-GEMINI"] / "SKILL.md"
    storage = (
        BASE
        / "results"
        / "snyk-agent-scan-0.6.4"
        / "TS-VERCEL-GEMINI-BLOCKED-CREDENTIAL"
        / "storage.json"
    )
    execute(
        "snyk-agent-scan-0.6.4",
        "TS-VERCEL-GEMINI-BLOCKED-CREDENTIAL",
        [
            scanner,
            "scan",
            "--print-errors",
            "--verbose",
            "--json",
            "--storage-file",
            storage,
            target,
        ],
        inputs=[target],
        timeout=300,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=("manifest", "versions", "static", "ollama", "codex", "snyk", "all"),
        default="all",
        nargs="?",
    )
    args = parser.parse_args()

    manifest = build_manifest()
    (BASE / "provenance.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("provenance.json written", flush=True)
    if args.mode == "manifest":
        return
    if args.mode in {"versions", "all"}:
        run_versions()
    if args.mode in {"static", "all"}:
        run_static_skill_scanners()
        run_static_mcp_scanner()
    if args.mode in {"ollama", "all"}:
        run_skillspector_ollama()
    if args.mode in {"codex", "all"}:
        run_skillspector_codex()
    if args.mode in {"snyk", "all"}:
        install_and_probe_snyk()


if __name__ == "__main__":
    main()
