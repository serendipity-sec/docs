"""Generate deterministic synthetic trials to test study instrumentation only."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent
DOCS_ROOT = BASE.parents[3]
RUN_ID = "synthetic-instrumentation-v1"
OUTPUT = BASE / "results" / "synthetic-dry-run"
FIXTURE_CLOCK = datetime(2026, 9, 22, 0, 0, 0, tzinfo=timezone.utc)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def presentation(case: dict, condition: str) -> dict:
    common = {
        "case_id": case["id"],
        "family": case["family"],
        "changed_variable": case["changed_variable"],
        "precondition": case["precondition"],
        "planned_oracle": case["planned_oracle"],
    }
    if condition == "B0":
        return {"format": "raw_evidence_bundle", "materials": common}
    return {
        "format": "linked_evidence_view",
        "policy": "P1",
        "version_binding": {"case_id": case["id"], "changed_variable": case["changed_variable"]},
        "permission_and_scan_state": {
            "precondition": case["precondition"],
            "evidence_requirements": case["planned_oracle"],
        },
    }


def source_evidence(case: dict, policy_summary: str) -> dict:
    return {
        "policy_id": "P1",
        "policy_summary": policy_summary,
        "case": {
            key: case[key]
            for key in (
                "id", "family", "variant", "changed_variable", "precondition",
                "expected_reason", "planned_oracle"
            )
        },
    }


def decide(profile: dict, reference: str, trial_index: int):
    rule = profile["decision_rule"]
    if rule == "exact_reference":
        return reference, ["matched_design_expectation"], [], False
    if rule == "always_allow":
        return "ALLOW", ["trusted_summary_badge"], [], False
    if rule == "always_hold":
        return "HOLD", ["insufficient_certainty"], ["independent_review"], False
    if rule == "exact_reference_except_every_fourth_trial_timeout":
        if trial_index % 4 == 0:
            return None, [], ["more_review_time"], True
        return reference, ["matched_design_expectation"], [], False
    raise ValueError(f"Unknown decision rule: {rule}")


def evidence_events(profile: dict, condition: str) -> list[dict]:
    strategy = profile["evidence_strategy"]
    if strategy == "inspect_summary_badge_only":
        return [{"event": "open_evidence", "evidence_type": "summary_badge"}]
    if strategy == "request_more_evidence_without_resolution":
        return [{"event": "open_evidence", "evidence_type": "evidence_completeness"}]
    if condition == "B0":
        return [
            {"event": "open_evidence", "evidence_type": "raw_precondition"},
            {"event": "open_evidence", "evidence_type": "raw_oracle_requirements"},
        ]
    return [
        {"event": "open_evidence", "evidence_type": "linked_policy"},
        {"event": "open_evidence", "evidence_type": "linked_change_and_state"},
    ]


def main() -> None:
    manifest = load_json(BASE / "case-manifest.json")
    assignments = load_json(BASE / "assignments.json")
    profiles_doc = load_json(BASE / "synthetic-profiles.json")
    profiles = {row["profile_id"]: row for row in profiles_doc["profiles"]}

    source_path = DOCS_ROOT / manifest["source"]["path_from_docs_root"]
    actual_source_sha = file_sha256(source_path)
    if actual_source_sha != manifest["source"]["sha256"]:
        raise RuntimeError(f"Source cases hash changed: {actual_source_sha}")
    source = load_json(source_path)
    for field, expected in (
        ("execution_status", manifest["source"]["required_execution_status"]),
        ("fixture_files_created", manifest["source"]["required_fixture_files_created"]),
        ("reference_decisions_reviewed", manifest["source"]["required_reference_decisions_reviewed"]),
    ):
        if source.get(field) != expected:
            raise RuntimeError(f"Unexpected source state {field}={source.get(field)!r}")

    cases = {case["id"]: case for case in source["cases"]}
    expected_ids = set(manifest["case_sets"]["A"] + manifest["case_sets"]["B"])
    if set(cases) != expected_ids:
        raise RuntimeError("Case manifest does not cover exactly the source cases")

    records = []
    for actor_offset, actor in enumerate(assignments["actors"]):
        profile = profiles[actor["profile_id"]]
        sequence = assignments["sequences"][actor["sequence_id"]]
        cursor = FIXTURE_CLOCK + timedelta(hours=actor_offset * 2)
        for trial_index, assigned in enumerate(sequence, start=1):
            case = cases[assigned["case_id"]]
            condition = assigned["condition"]
            decision, reasons, requested, timed_out = decide(
                profile, case["expected_decision"], trial_index
            )
            duration_ms = (
                int(profile["timeout_duration_ms"])
                if timed_out
                else int(profile["duration_ms"]) + trial_index * 100
            )
            first_evidence = cursor + timedelta(milliseconds=750)
            submitted = None if timed_out else cursor + timedelta(milliseconds=duration_ms)
            raw_evidence = source_evidence(case, source["policy_summary"])
            record = {
                "schema_version": "1.0",
                "run_id": RUN_ID,
                "actor_type": "synthetic_dry_run",
                "actor_id": actor["actor_id"],
                "profile_id": actor["profile_id"],
                "sequence_id": actor["sequence_id"],
                "trial_id": f"{actor['actor_id']}-{trial_index:02d}-{case['id']}",
                "trial_index": trial_index,
                "source_case_id": case["id"],
                "case_family": case["family"],
                "condition": condition,
                "reference_status": "design_expectation",
                "reference_decision": case["expected_decision"],
                "source_evidence_sha256": digest(raw_evidence),
                "presented_snapshot_sha256": digest(presentation(case, condition)),
                "decision": decision,
                "reason_codes": reasons,
                "requested_evidence": requested,
                "confidence_0_100": None if timed_out else int(profile["confidence"]),
                "evidence_events": evidence_events(profile, condition),
                "timing_origin": "synthetic_fixture",
                "started_at": iso(cursor),
                "first_evidence_at": iso(first_evidence),
                "submitted_at": iso(submitted),
                "duration_ms": duration_ms,
                "timeout": timed_out,
                "exclude_from_human_analysis": True,
            }
            records.append(record)
            cursor += timedelta(milliseconds=duration_ms + 1000)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    trials_path = OUTPUT / "study-trials.jsonl"
    trials_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records),
        encoding="utf-8",
    )
    run_manifest = {
        "schema_version": "1.0",
        "run_id": RUN_ID,
        "purpose": "instrumentation_validation_only",
        "human_study_status": "NOT_RUN",
        "actor_type": "synthetic_dry_run",
        "exclude_from_human_analysis": True,
        "reference_status": "design_expectation",
        "source_cases_path": manifest["source"]["path_from_docs_root"],
        "source_cases_sha256": actual_source_sha,
        "fixture_clock_origin": iso(FIXTURE_CLOCK),
        "actors": len(assignments["actors"]),
        "profiles": len(profiles),
        "trial_records": len(records),
        "trials_sha256": file_sha256(trials_path),
        "warning": "No real participant took part. These records cannot support claims about user accuracy, time, trust, or overconfidence."
    }
    (OUTPUT / "run-manifest.json").write_text(
        json.dumps(run_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(run_manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
