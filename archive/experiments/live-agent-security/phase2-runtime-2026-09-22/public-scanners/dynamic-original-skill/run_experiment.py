#!/usr/bin/env python3
"""Build and run the disposable, offline fake Vercel observation harness."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DOCS_ROOT = ROOT.parents[4]
RESULTS = ROOT / "results"
RAW = RESULTS / "raw"
CONTAINER_EVIDENCE = RESULTS / "container-evidence"
SOURCE_REPO = DOCS_ROOT / ".runtime" / "quarantine" / "toxicskills-goof"
INPUT = SOURCE_REPO / ".gemini" / "skills" / "vercel" / "SKILL.md"
EXPECTED_SHA256 = "d70912ce0d898712b9b5048423d89d5190ffe4775d57f3221bff35bddbe36e3e"
EXPECTED_COMMIT = "80ce2e06f52fd384163c4bd6778676019723773c"
BASE_IMAGE = "python:3.12-alpine@sha256:4c47124a8391cb7a9f571164147d154777cf012a4ece5f86097130d7a4478111"
IMAGE_TAG = "serendipity-public-skill-safe-interpreter:20260922"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def run(argv: list[str], *, cwd: Path = ROOT, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def require_success(completed: subprocess.CompletedProcess[str], label: str) -> None:
    if completed.returncode != 0:
        raise RuntimeError(
            f"{label} failed with {completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def main() -> int:
    if RESULTS.exists():
        shutil.rmtree(RESULTS)
    RAW.mkdir(parents=True)
    CONTAINER_EVIDENCE.mkdir(parents=True)
    started_at = now()

    input_sha_before = sha256_file(INPUT)
    if input_sha_before != EXPECTED_SHA256:
        raise RuntimeError(f"input hash mismatch before run: {input_sha_before}")

    git_commit = run(["git", "-C", str(SOURCE_REPO), "rev-parse", "HEAD"])
    require_success(git_commit, "git rev-parse")
    observed_commit = git_commit.stdout.strip()
    if observed_commit != EXPECTED_COMMIT:
        raise RuntimeError(f"source commit mismatch: {observed_commit}")
    git_remote = run(["git", "-C", str(SOURCE_REPO), "remote", "get-url", "origin"])
    require_success(git_remote, "git remote")
    git_status = run(["git", "-C", str(SOURCE_REPO), "status", "--short"])
    require_success(git_status, "git status")

    docker_version = run(["docker", "version", "--format", "{{json .}}"])
    write_text(RAW / "docker-version.stdout.txt", docker_version.stdout)
    write_text(RAW / "docker-version.stderr.txt", docker_version.stderr)
    require_success(docker_version, "docker version")

    base_inspect = run(["docker", "image", "inspect", BASE_IMAGE])
    write_text(RAW / "base-image-inspect.json", base_inspect.stdout)
    write_text(RAW / "base-image-inspect.stderr.txt", base_inspect.stderr)
    require_success(base_inspect, "base image inspect")

    build_argv = [
        "docker", "build", "--pull=false", "--network=none", "--provenance=false",
        "--progress=plain", "--tag", IMAGE_TAG, str(ROOT),
    ]
    build = run(build_argv, timeout=300)
    write_text(RAW / "docker-build.stdout.txt", build.stdout)
    write_text(RAW / "docker-build.stderr.txt", build.stderr)
    write_json(RAW / "docker-build-command.json", build_argv)
    require_success(build, "docker build")

    image_inspect = run(["docker", "image", "inspect", IMAGE_TAG])
    write_text(RAW / "image-inspect.json", image_inspect.stdout)
    write_text(RAW / "image-inspect.stderr.txt", image_inspect.stderr)
    require_success(image_inspect, "built image inspect")
    image_data = json.loads(image_inspect.stdout)[0]
    base_data = json.loads(base_inspect.stdout)[0]
    write_json(
        RESULTS / "image-digest.json",
        {
            "base_image_reference": BASE_IMAGE,
            "base_image_id": base_data["Id"],
            "base_repo_digests": base_data.get("RepoDigests", []),
            "built_image_tag": IMAGE_TAG,
            "built_image_id": image_data["Id"],
            "built_repo_digests": image_data.get("RepoDigests", []),
        },
    )

    container_name = f"serendipity-vercel-observe-{os.getpid()}"
    create_argv = [
        "docker", "create",
        "--name", container_name,
        "--network", "none",
        "--user", "65532:65532",
        "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=16m",
        "--tmpfs", "/workspace:rw,noexec,nosuid,nodev,size=16m",
        "--tmpfs", "/evidence:rw,noexec,nosuid,nodev,size=16m",
        "--security-opt", "no-new-privileges:true",
        "--cap-drop", "ALL",
        "--pids-limit", "32",
        "--memory", "128m",
        "--memory-swap", "128m",
        "--cpus", "0.50",
        "--ulimit", "nofile=64:64",
        "--hostname", "toxic-demo",
        "--workdir", "/workspace",
        "--env", f"EXPECTED_INPUT_SHA256={EXPECTED_SHA256}",
        "--env", f"EXPECTED_SOURCE_COMMIT={EXPECTED_COMMIT}",
        "--mount", f"type=bind,src={INPUT},dst=/input/SKILL.md,readonly",
        IMAGE_TAG,
    ]
    write_json(RAW / "docker-create-command.json", create_argv)
    container_id: str | None = None
    try:
        created = run(create_argv)
        write_text(RAW / "docker-create.stdout.txt", created.stdout)
        write_text(RAW / "docker-create.stderr.txt", created.stderr)
        require_success(created, "docker create")
        container_id = created.stdout.strip()

        inspect_before = run(["docker", "inspect", container_id])
        write_text(RAW / "container-inspect-before.json", inspect_before.stdout)
        write_text(RAW / "container-inspect-before.stderr.txt", inspect_before.stderr)
        require_success(inspect_before, "container inspect before")

        started = run(["docker", "start", container_id])
        write_text(RAW / "docker-start.stdout.txt", started.stdout)
        write_text(RAW / "docker-start.stderr.txt", started.stderr)
        require_success(started, "docker start")

        export_attempts: list[dict[str, Any]] = []
        exported_ready: subprocess.CompletedProcess[str] | None = None
        for attempt in range(1, 31):
            exported_ready = run(
                ["docker", "exec", container_id, "/usr/local/bin/python3", "/harness/export_evidence.py", "ready"],
                timeout=10,
            )
            export_attempts.append(
                {"attempt": attempt, "returncode": exported_ready.returncode, "stderr": exported_ready.stderr}
            )
            if exported_ready.returncode == 0:
                break
            time.sleep(0.2)
        write_json(RAW / "docker-exec-export-attempts.json", export_attempts)
        if exported_ready is None:
            raise RuntimeError("evidence export was not attempted")
        write_text(RAW / "docker-exec-ready.stdout.txt", exported_ready.stdout)
        write_text(RAW / "docker-exec-ready.stderr.txt", exported_ready.stderr)
        require_success(exported_ready, "readiness export")
        write_text(CONTAINER_EVIDENCE / "ready", exported_ready.stdout)

        exported_result = run(
            ["docker", "exec", container_id, "/usr/local/bin/python3", "/harness/export_evidence.py", "interpreter-result.json"]
        )
        write_text(RAW / "docker-exec-interpreter.stderr.txt", exported_result.stderr)
        require_success(exported_result, "interpreter result export")
        write_text(CONTAINER_EVIDENCE / "interpreter-result.json", exported_result.stdout)

        exported_events = run(
            ["docker", "exec", container_id, "/usr/local/bin/python3", "/harness/export_evidence.py", "events.jsonl"]
        )
        write_text(RAW / "docker-exec-events.stderr.txt", exported_events.stderr)
        require_success(exported_events, "events export")
        write_text(CONTAINER_EVIDENCE / "events.jsonl", exported_events.stdout)

        stopped = run(["docker", "stop", "--time", "5", container_id], timeout=15)
        write_text(RAW / "docker-stop.stdout.txt", stopped.stdout)
        write_text(RAW / "docker-stop.stderr.txt", stopped.stderr)
        require_success(stopped, "docker stop")

        logs = run(["docker", "logs", container_id])
        write_text(RAW / "container.stdout.txt", logs.stdout)
        write_text(RAW / "container.stderr.txt", logs.stderr)
        require_success(logs, "docker logs")

        inspect_after = run(["docker", "inspect", container_id])
        write_text(RAW / "container-inspect-after.json", inspect_after.stdout)
        write_text(RAW / "container-inspect-after.stderr.txt", inspect_after.stderr)
        require_success(inspect_after, "container inspect after")
        state_after = json.loads(inspect_after.stdout)[0]["State"]
        write_json(
            RAW / "container-process-result.json",
            {
                "returncode": state_after["ExitCode"],
                "status": state_after["Status"],
                "started_at_utc": started_at,
                "finished_at_utc": now(),
            },
        )

        input_sha_after = sha256_file(INPUT)
        inspect_data = json.loads(inspect_before.stdout)[0]
        host_config = inspect_data["HostConfig"]
        write_json(
            RESULTS / "container-config.json",
            {
                "requested_create_argv": create_argv,
                "container_id": container_id,
                "requested_safety": {
                    "network": "none",
                    "user": "65532:65532",
                    "read_only_rootfs": True,
                    "tmpfs": ["/tmp", "/workspace", "/evidence"],
                    "no_new_privileges": True,
                    "cap_drop": ["ALL"],
                    "pids_limit": 32,
                    "memory_bytes": 134217728,
                    "memory_swap_bytes": 134217728,
                    "nano_cpus": 500000000,
                },
                "observed": {
                    "network_mode": host_config["NetworkMode"],
                    "user": inspect_data["Config"]["User"],
                    "read_only_rootfs": host_config["ReadonlyRootfs"],
                    "tmpfs": host_config.get("Tmpfs"),
                    "security_opt": host_config.get("SecurityOpt"),
                    "cap_drop": host_config.get("CapDrop"),
                    "pids_limit": host_config["PidsLimit"],
                    "memory_bytes": host_config["Memory"],
                    "memory_swap_bytes": host_config["MemorySwap"],
                    "nano_cpus": host_config["NanoCpus"],
                    "mounts": inspect_data.get("Mounts", []),
                },
            },
        )
        write_json(
            RESULTS / "provenance.json",
            {
                "schema_version": 1,
                "generated_at_utc": now(),
                "experiment_condition": "DETERMINISTIC_SAFE_INTERPRETER",
                "source": {
                    "repository": git_remote.stdout.strip(),
                    "commit": observed_commit,
                    "worktree_status": [line for line in git_status.stdout.splitlines() if line],
                    "license_note": "No root license found; public source text is not copied into this artifact.",
                },
                "input": {
                    "host_path": str(INPUT),
                    "repository_relative_path": ".gemini/skills/vercel/SKILL.md",
                    "container_path": "/input/SKILL.md",
                    "format": "YAML front matter plus Markdown body",
                    "sha256_before": input_sha_before,
                    "sha256_after": input_sha_after,
                    "mounted_read_only": True,
                },
                "safety": {
                    "raw_public_skill_executed_as_code": False,
                    "raw_public_skill_sourced": False,
                    "input_passed_to_shell": False,
                    "actual_curl_npm_npx_uname_used": False,
                    "record_only_shims_used": ["curl", "npm", "npx", "uname"],
                    "external_network_success_attempted": False,
                    "external_network_success_claimed": False,
                    "host_credentials_mounted": False,
                    "docker_socket_mounted": False,
                    "defender_blocked_files_accessed": False,
                    "defender_blocked_paths_excluded": [
                        ".agents/skills/clawhub/skill.md",
                        ".agents/skills/google/SKILL.md",
                    ],
                },
                "container": {
                    "id": container_id,
                    "image_tag": IMAGE_TAG,
                    "image_id": image_data["Id"],
                },
            },
        )
        if state_after["ExitCode"] != 0:
            raise RuntimeError(f"container process failed with {state_after['ExitCode']}")
    finally:
        if container_id:
            diagnostic_logs = run(["docker", "logs", container_id])
            if not (RAW / "container.stdout.txt").exists():
                write_text(RAW / "container.stdout.txt", diagnostic_logs.stdout)
                write_text(RAW / "container.stderr.txt", diagnostic_logs.stderr)
            diagnostic_inspect = run(["docker", "inspect", container_id])
            if not (RAW / "container-inspect-finally.json").exists():
                write_text(RAW / "container-inspect-finally.json", diagnostic_inspect.stdout)
                write_text(RAW / "container-inspect-finally.stderr.txt", diagnostic_inspect.stderr)
            removed = run(["docker", "rm", "--force", container_id])
            write_text(RAW / "docker-rm.stdout.txt", removed.stdout)
            write_text(RAW / "docker-rm.stderr.txt", removed.stderr)

    validator = run([sys.executable, str(ROOT / "validate.py"), "--root", str(ROOT)])
    write_text(RAW / "validator.stdout.txt", validator.stdout)
    write_text(RAW / "validator.stderr.txt", validator.stderr)
    require_success(validator, "validator")
    print(validator.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
