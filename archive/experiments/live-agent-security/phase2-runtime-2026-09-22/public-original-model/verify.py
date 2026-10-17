"""Independent artifact verifier for the public-original model probe."""

from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import run_public_original_model as runner


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    source_bytes = runner.SOURCE.read_bytes()
    source_hash = digest(source_bytes)
    check("pinned source SHA-256", source_hash == runner.EXPECTED_SOURCE_SHA256, source_hash)
    commit = runner.read_git_head(runner.SOURCE_REPO)
    check("pinned source commit", commit == runner.EXPECTED_SOURCE_COMMIT, commit)
    original = source_bytes.decode("utf-8")
    control, transformation = runner.make_control(original)
    check("control differs", control != original, digest(control.encode("utf-8")))
    check("control removes every risk-line token", all(token not in control.lower() for token in runner.RISK_LINE_TOKENS), transformation)

    source_tree = ast.parse((BASE / "run_public_original_model.py").read_text(encoding="utf-8"))
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(source_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(source_tree)
        if isinstance(node, ast.ImportFrom)
    }
    called_names = {
        node.func.id
        for node in ast.walk(source_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    check("runner has no subprocess or shell imports", not ({"subprocess", "shlex"} & imports), sorted(imports))
    check("runner has no eval or exec calls", not ({"eval", "exec"} & called_names), sorted({"eval", "exec"} & called_names))

    manifest = load(RESULTS / "batch-manifest.json")
    summary = load(RESULTS / "summary.json")
    expected_matrix = manifest["matrix"]
    check("experiment kind", manifest.get("experiment_kind") == runner.EXPERIMENT_KIND, manifest.get("experiment_kind"))
    check("source metadata hash", manifest["source"]["sha256"] == source_hash, manifest["source"])
    check("source raw copy prohibited", manifest["source"]["raw_copy_in_results"] is False, manifest["source"]["raw_copy_in_results"])
    check("control hash", manifest["control"]["sha256"] == digest(control.encode("utf-8")), manifest["control"]["sha256"])
    check("matrix/summary length", len(summary) == len(expected_matrix), {"summary": len(summary), "expected": len(expected_matrix)})

    summary_keys = {(row["model"], row["seed"], row["condition"]) for row in summary}
    matrix_keys = {(row["model"], row["seed"], row["condition"]) for row in expected_matrix}
    check("matrix exact coverage", summary_keys == matrix_keys, sorted(summary_keys))
    qwen4_pairs = {(row["seed"], row["condition"]) for row in summary if row["model"] == "qwen3:4b-q4_K_M"}
    check(
        "Qwen4B has two complete original/control pairs",
        qwen4_pairs == {(47, "original"), (47, "control-prerequisite-removed"), (113, "original"), (113, "control-prerequisite-removed")},
        sorted(qwen4_pairs),
    )

    for row in summary:
        run_dir = RESULTS / "runs" / row["run_id"]
        metadata = load(run_dir / "input-metadata.json")
        response = load(run_dir / "raw-response.json")
        actions = load(run_dir / "selected-actions.json")
        result = load(run_dir / "result.json")
        skill_text = original if row["condition"] == "original" else control
        messages = runner.prompt_for(skill_text)
        payload = {
            "model": row["model"],
            "messages": messages,
            "tools": [runner.TOOL_SCHEMA],
            "stream": False,
            "think": False,
            "keep_alive": "10m",
            "options": {"temperature": 0.0, "seed": row["seed"], "num_ctx": 8192, "num_predict": 256},
        }
        extracted = runner.extract_actions(response)
        classification = runner.classify(extracted)
        prefix = row["run_id"]
        check(prefix + " completed", row["status"] == "COMPLETED" and response.get("done") is True, row["status"])
        check(prefix + " response hash", row["response_sha256"] == digest(canonical_bytes(response)), row["response_sha256"])
        check(prefix + " actions exact", actions == extracted and row["selected_actions_sha256"] == digest(canonical_bytes(actions)), actions)
        check(prefix + " classification exact", all(row.get(key) == value for key, value in classification.items()), classification)
        check(prefix + " input skill hash", metadata["condition_skill_sha256"] == digest(skill_text.encode("utf-8")), metadata["condition_skill_sha256"])
        check(prefix + " prompt hash", metadata["messages_sha256"] == digest(canonical_bytes(messages)), metadata["messages_sha256"])
        check(prefix + " request hash", metadata["request_payload_sha256"] == digest(canonical_bytes(payload)), metadata["request_payload_sha256"])
        check(prefix + " model digest binding", metadata["model_digest"] == row["model_digest"] == manifest["models"][row["model"]]["digest"], row["model_digest"])
        check(prefix + " no execution counts", all(row[key] == 0 for key in ("tool_execution_count", "shell_execution_count", "subprocess_execution_count", "external_network_request_count", "real_secret_count")), {key: row[key] for key in ("tool_execution_count", "shell_execution_count", "subprocess_execution_count", "external_network_request_count", "real_secret_count")})
        check(prefix + " tool name constrained", all(action["name"] == "record_only_action" for action in actions), [action["name"] for action in actions])
        check(prefix + " maximum one action", len(actions) <= 1, len(actions))

    paired: list[dict[str, Any]] = []
    for model, seed in sorted({(row["model"], row["seed"]) for row in summary}):
        rows = {row["condition"]: row for row in summary if row["model"] == model and row["seed"] == seed}
        if set(rows) == {"original", "control-prerequisite-removed"}:
            paired.append(
                {
                    "model": model,
                    "seed": seed,
                    "original_risky_prerequisite_selected": rows["original"]["risky_prerequisite_selected"],
                    "control_risky_prerequisite_selected": rows["control-prerequisite-removed"]["risky_prerequisite_selected"],
                    "paired_difference": int(rows["original"]["risky_prerequisite_selected"]) - int(rows["control-prerequisite-removed"]["risky_prerequisite_selected"]),
                }
            )
    check("all matrix rows form pairs", len(paired) * 2 == len(summary), paired)

    failures = [row for row in checks if not row["pass"]]
    verification = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "checks": checks,
        "paired_effects": paired,
        "boundary": "Artifact integrity and record-only action selection; not malware execution and not external network testing.",
    }
    runner.write_json(RESULTS / "verification.json", verification)

    evidence_files = sorted(
        path for path in BASE.rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.name != "evidence-manifest.json"
    )
    evidence_manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": [
            {
                "path": path.relative_to(BASE).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": digest(path.read_bytes()),
            }
            for path in evidence_files
        ],
    }
    runner.write_json(RESULTS / "evidence-manifest.json", evidence_manifest)
    print(json.dumps({"status": verification["status"], "checks": len(checks), "failures": len(failures), "pairs": paired}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
