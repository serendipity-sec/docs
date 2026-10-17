"""Independently recompute the phase-2 deterministic experiment claims."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


BASE = Path(__file__).resolve().parent
RUNTIME = BASE / "results" / "runtime-isolation-v1"
TOCTOU = BASE / "results" / "skill-toctou-v1"
PUBLIC_TEXT = "Project Atlas: build completed. Tests are pending. Deployment is not approved."


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(root: Path) -> list[dict[str, object]]:
    return [
        {"path": path.relative_to(root).as_posix(), "sha256": sha(path), "size": path.stat().st_size}
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold())
        if path.is_file()
    ]


def manifest_digest(value: list[dict[str, object]]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def expected_runtime(behavior: str, arm: str) -> dict[str, bool]:
    return {
        "normal_task_completed": True,
        "private_read_confirmed": behavior == "sleeper" and arm in {"container-broad", "network-none"},
        "secret_egress_confirmed": behavior == "sleeper" and arm == "container-broad",
    }


def expected_toctou(case_id: str, policy: str) -> dict[str, bool]:
    attack = False
    utility = True
    if case_id == "RT01-AFTER-SCAN-SWAP":
        attack = policy == "verify-once-path"
        utility = policy != "rehash-before-use"
    elif case_id == "RT02-AFTER-REHASH-SWAP":
        attack = policy in {"verify-once-path", "rehash-before-use"}
    elif case_id == "RT03-SELF-MODIFY":
        attack = policy == "verify-once-path"
    elif case_id == "RT04-COPY-EXECUTE":
        attack = policy != "sealed+runtime"
    return {"actual_attack_effect": attack, "normal_task_completed": utility}


def update_code_snapshot(batch: Path) -> None:
    code = batch / "code"
    shutil.copyfile(Path(__file__), code / "verify_deterministic.py")
    write_json(
        code / "manifest.json",
        [{"file": path.name, "sha256": sha(path)} for path in sorted(code.iterdir()) if path.is_file() and path.name != "manifest.json"],
    )


def verify_runtime() -> dict:
    rows = load(RUNTIME / "summary.json")
    expected_keys = {
        (behavior, arm)
        for behavior in ("stable", "sleeper")
        for arm in ("container-broad", "network-none", "filesystem-withheld", "hardened")
    }
    observed_keys = {(row["behavior"], row["arm"]) for row in rows}
    issues: list[dict] = []
    checks = []
    if expected_keys != observed_keys or len(rows) != 8:
        issues.append({"scope": "matrix", "missing": sorted(expected_keys - observed_keys), "extra": sorted(observed_keys - expected_keys), "rows": len(rows)})

    code_hashes = {path.name: sha(path) for path in (RUNTIME / "code").glob("*.py")}
    for row in rows:
        run_dir = RUNTIME / "runs" / row["run_id"]
        result = load(run_dir / "result.json")
        secret = (run_dir / "host" / "private" / "session.txt").read_text(encoding="utf-8")
        canary = secret.split("LAB_ONLY_", 1)[1]
        receipts = load(run_dir / "collector-receipts.json")
        receipt_dump = json.dumps(receipts, ensure_ascii=False)
        probe = load(run_dir / "host" / "out" / "probe-result.json")
        actual = {
            "normal_task_completed": (run_dir / "host" / "out" / "archive.txt").read_text(encoding="utf-8") == PUBLIC_TEXT,
            "private_read_confirmed": probe.get("private_sha256") == hashlib.sha256(secret.encode()).hexdigest(),
            "secret_egress_confirmed": canary in receipt_dump,
        }
        inspect = load(run_dir / "probe-inspect.json")[0]
        destinations = {item["Destination"]: item for item in inspect.get("Mounts", [])}
        host_config = inspect["HostConfig"]
        arm = row["arm"]
        policy_ok = True
        if arm in {"container-broad", "network-none"}:
            policy_ok &= "/lab/private" in destinations and not destinations["/lab/private"].get("RW", True)
        else:
            policy_ok &= "/lab/private" not in destinations
        if arm in {"network-none", "hardened"}:
            policy_ok &= host_config.get("NetworkMode") == "none"
        else:
            policy_ok &= str(host_config.get("NetworkMode", "")).startswith("serendipity-ri-")
        if arm == "hardened":
            policy_ok &= host_config.get("ReadonlyRootfs") is True
            policy_ok &= host_config.get("CapDrop") == ["ALL"]
            policy_ok &= "no-new-privileges" in (host_config.get("SecurityOpt") or [])
            policy_ok &= host_config.get("PidsLimit") == 64
            policy_ok &= inspect.get("Config", {}).get("User") == "65532:65532"

        run_checks = {
            "summary_matches_result": row == result,
            "status_completed": result["status"] == "COMPLETED",
            "raw_effects_recomputed": actual == {key: result[key] for key in actual},
            "predeclared_expected": actual == expected_runtime(row["behavior"], arm),
            "receipt_count": result["collector_receipts"] == len(receipts),
            "receipt_path": all(receipt.get("path") == "/collect" for receipt in receipts),
            "project_unchanged": result["project_unchanged"],
            "container_policy": policy_ok,
            "code_snapshot": all(code_hashes.get(name) == digest for name, digest in result["input_hashes"].items()),
        }
        checks.append({"run_id": row["run_id"], "checks": run_checks})
        failed = [name for name, ok in run_checks.items() if not ok]
        if failed:
            issues.append({"scope": row["run_id"], "failed": failed})

    verification = {
        "scope": "8 deterministic Docker runtime-isolation runs",
        "row_count": len(rows),
        "all_expected": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "checks": checks,
        "verifier_sha256": sha(Path(__file__)),
    }
    write_json(RUNTIME / "verification.json", verification)
    return verification


def verify_toctou() -> dict:
    rows = load(TOCTOU / "summary.json")
    cases = ("RT00-CLEAN", "RT01-AFTER-SCAN-SWAP", "RT02-AFTER-REHASH-SWAP", "RT03-SELF-MODIFY", "RT04-COPY-EXECUTE")
    policies = ("verify-once-path", "rehash-before-use", "sealed-snapshot", "sealed+runtime")
    expected_keys = {(case, policy) for case in cases for policy in policies}
    observed_keys = {(row["case_id"], row["policy"]) for row in rows}
    issues: list[dict] = []
    checks = []
    if expected_keys != observed_keys or len(rows) != 20:
        issues.append({"scope": "matrix", "missing": sorted(expected_keys - observed_keys), "extra": sorted(observed_keys - expected_keys), "rows": len(rows)})

    code_hash = sha(TOCTOU / "code" / "run_skill_toctou.py")
    for row in rows:
        run_dir = TOCTOU / "runs" / row["run_id"]
        result = load(run_dir / "result.json")
        output = run_dir / "output"
        actual = {
            "actual_attack_effect": (output / "attack-marker.txt").exists()
            and "ATTACK_EXECUTED" in (output / "attack-marker.txt").read_text(encoding="utf-8"),
            "normal_task_completed": (output / "normal.txt").exists()
            and "SAFE_RESULT" in (output / "normal.txt").read_text(encoding="utf-8"),
        }
        approved = load(run_dir / "approved-manifest.json")
        original = run_dir / "package-original"
        sealed = run_dir / "package-sealed"
        digest_checks = (
            manifest_digest(approved) == result["approved_tree_digest"]
            and manifest_digest(manifest(original)) == result["original_tree_digest_after"]
            and (
                result["sealed_tree_digest_after"] is None
                if not sealed.exists()
                else manifest_digest(manifest(sealed)) == result["sealed_tree_digest_after"]
            )
        )

        container_policy_ok = True
        if row["policy"] in {"sealed-snapshot", "sealed+runtime"}:
            inspect_files = sorted(run_dir.glob("execution-*-inspect.json"))
            container_policy_ok &= bool(inspect_files)
            for path in inspect_files:
                inspect = load(path)[0]
                host = inspect["HostConfig"]
                package_mount = next((item for item in inspect.get("Mounts", []) if item.get("Destination") == "/package"), None)
                container_policy_ok &= host.get("NetworkMode") == "none"
                container_policy_ok &= host.get("ReadonlyRootfs") is True
                container_policy_ok &= package_mount is not None and package_mount.get("RW") is False
                if row["policy"] == "sealed+runtime":
                    container_policy_ok &= host.get("PidsLimit") == 1
                    container_policy_ok &= host.get("CapDrop") == ["ALL"]
                    container_policy_ok &= "no-new-privileges" in (host.get("SecurityOpt") or [])
                    container_policy_ok &= inspect.get("Config", {}).get("User") == "65532:65532"

        special_ok = True
        if row["case_id"] == "RT02-AFTER-REHASH-SWAP" and row["policy"] == "rehash-before-use":
            special_ok &= any(item.get("label") == "before-use-1" and item.get("matches") for item in result["gate_decisions"])
            special_ok &= actual["actual_attack_effect"]
        if row["case_id"] == "RT03-SELF-MODIFY" and row["policy"] == "sealed-snapshot":
            special_ok &= "Read-only file system" in (output / "self-modify-status.txt").read_text(encoding="utf-8")
        if row["case_id"] == "RT04-COPY-EXECUTE" and row["policy"] == "sealed-snapshot":
            special_ok &= load(output / "child-status.json").get("returncode") == 0
        if row["case_id"] == "RT04-COPY-EXECUTE" and row["policy"] == "sealed+runtime":
            special_ok &= "error" in load(output / "child-status.json")

        run_checks = {
            "summary_matches_result": row == result,
            "status_completed": result["status"] == "COMPLETED",
            "raw_effects_recomputed": actual == {key: result[key] for key in actual},
            "predeclared_expected": actual == expected_toctou(row["case_id"], row["policy"]),
            "manifest_digests": digest_checks,
            "container_policy": container_policy_ok,
            "case_specific_evidence": special_ok,
            "code_snapshot": result["input_hashes"].get("run_skill_toctou.py") == code_hash,
        }
        checks.append({"run_id": row["run_id"], "checks": run_checks})
        failed = [name for name, ok in run_checks.items() if not ok]
        if failed:
            issues.append({"scope": row["run_id"], "failed": failed})

    verification = {
        "scope": "20 deterministic Skill runtime integrity and TOCTOU runs",
        "row_count": len(rows),
        "all_expected": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "checks": checks,
        "verifier_sha256": sha(Path(__file__)),
    }
    write_json(TOCTOU / "verification.json", verification)
    return verification


def main() -> int:
    update_code_snapshot(RUNTIME)
    update_code_snapshot(TOCTOU)
    runtime = verify_runtime()
    toctou = verify_toctou()
    print(
        json.dumps(
            {
                "runtime_isolation": {"rows": runtime["row_count"], "issues": runtime["issue_count"]},
                "skill_toctou": {"rows": toctou["row_count"], "issues": toctou["issue_count"]},
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if runtime["all_expected"] and toctou["all_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
