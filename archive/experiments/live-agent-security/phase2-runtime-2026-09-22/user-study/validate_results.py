"""Validate dry-run trial isolation, counterbalancing, and aggregate calculations."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results" / "synthetic-dry-run"
VALID_DECISIONS = {"ALLOW", "DENY", "HOLD"}
REQUIRED = {
    "schema_version", "run_id", "actor_type", "actor_id", "profile_id", "sequence_id",
    "trial_id", "trial_index", "source_case_id", "case_family", "condition",
    "reference_status", "reference_decision", "source_evidence_sha256",
    "presented_snapshot_sha256", "decision", "reason_codes", "requested_evidence",
    "confidence_0_100", "evidence_events", "timing_origin", "started_at",
    "first_evidence_at", "submitted_at", "duration_ms", "timeout",
    "exclude_from_human_analysis"
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, message: str, checks: list[dict]) -> None:
    checks.append({"check": message, "passed": bool(condition)})
    if not condition:
        raise AssertionError(message)


def main() -> None:
    assignments = load_json(BASE / "assignments.json")
    schema = load_json(BASE / "schema" / "study-trial.schema.json")
    manifest = load_json(RESULTS / "run-manifest.json")
    aggregate = load_json(RESULTS / "aggregate.json")
    trials_path = RESULTS / "study-trials.jsonl"
    rows = [json.loads(line) for line in trials_path.read_text(encoding="utf-8").splitlines() if line]
    checks: list[dict] = []

    check(set(schema["required"]) == REQUIRED, "JSON Schema requires the validator field set", checks)
    check(set(schema["properties"]) == REQUIRED, "JSON Schema defines only the validator field set", checks)
    check(schema["properties"]["actor_type"].get("const") == "synthetic_dry_run", "JSON Schema fixes the synthetic actor type", checks)
    check(schema["properties"]["exclude_from_human_analysis"].get("const") is True, "JSON Schema excludes every row from human analysis", checks)
    check(len(rows) == 96, "exactly 96 synthetic trial records", checks)
    check(manifest["trials_sha256"] == sha256(trials_path), "trial file hash matches run manifest", checks)
    check(all(set(row) == REQUIRED for row in rows), "every row has the exact required field set", checks)
    check(all(row["actor_type"] == "synthetic_dry_run" for row in rows), "all actors are synthetic", checks)
    check(all(row["exclude_from_human_analysis"] is True for row in rows), "all rows are excluded from human analysis", checks)
    check(all(row["reference_status"] == "design_expectation" for row in rows), "all references are unreviewed design expectations", checks)
    check(all(row["condition"] in {"B0", "B1"} for row in rows), "conditions are B0 or B1", checks)
    check(all(row["reference_decision"] in VALID_DECISIONS for row in rows), "reference decisions use three states", checks)

    for row in rows:
        check(len(row["source_evidence_sha256"]) == 64, f"source hash length: {row['trial_id']}", checks)
        check(len(row["presented_snapshot_sha256"]) == 64, f"presentation hash length: {row['trial_id']}", checks)
        if row["timeout"]:
            check(row["decision"] is None, f"timeout has no decision: {row['trial_id']}", checks)
            check(row["confidence_0_100"] is None, f"timeout has no confidence: {row['trial_id']}", checks)
            check(row["submitted_at"] is None, f"timeout has no submission time: {row['trial_id']}", checks)
        else:
            check(row["decision"] in VALID_DECISIONS, f"answered decision is valid: {row['trial_id']}", checks)
            check(isinstance(row["confidence_0_100"], int) and 0 <= row["confidence_0_100"] <= 100, f"answered confidence is valid: {row['trial_id']}", checks)
            check(row["submitted_at"] is not None, f"answered trial has submission time: {row['trial_id']}", checks)

    assignment_by_actor = {actor["actor_id"]: actor for actor in assignments["actors"]}
    rows_by_actor = defaultdict(list)
    for row in rows:
        rows_by_actor[row["actor_id"]].append(row)
    check(set(rows_by_actor) == set(assignment_by_actor), "all and only assigned actors are present", checks)
    for actor_id, actor_rows in rows_by_actor.items():
        actor_rows.sort(key=lambda row: row["trial_index"])
        expected = assignments["sequences"][assignment_by_actor[actor_id]["sequence_id"]]
        check(len(actor_rows) == 12, f"actor has 12 trials: {actor_id}", checks)
        check(len({row["source_case_id"] for row in actor_rows}) == 12, f"actor sees each case once: {actor_id}", checks)
        check(Counter(row["condition"] for row in actor_rows) == Counter({"B0": 6, "B1": 6}), f"actor has balanced conditions: {actor_id}", checks)
        observed = [(row["source_case_id"], row["condition"]) for row in actor_rows]
        planned = [(row["case_id"], row["condition"]) for row in expected]
        check(observed == planned, f"actor follows assignment sequence: {actor_id}", checks)

    by_case_condition = defaultdict(list)
    for row in rows:
        by_case_condition[(row["source_case_id"], row["condition"])].append(row)
    check(all(len(value) == 4 for value in by_case_condition.values()), "each case-condition cell has four profile records", checks)
    for case_id in sorted({row["source_case_id"] for row in rows}):
        b0 = by_case_condition[(case_id, "B0")]
        b1 = by_case_condition[(case_id, "B1")]
        check(len({row["source_evidence_sha256"] for row in b0 + b1}) == 1, f"B0 and B1 share source evidence: {case_id}", checks)
        check({row["presented_snapshot_sha256"] for row in b0}.isdisjoint({row["presented_snapshot_sha256"] for row in b1}), f"B0 and B1 presentations differ: {case_id}", checks)

    timeouts = [row for row in rows if row["timeout"]]
    check(len(timeouts) == 6, "periodic timeout profile produces six timeouts", checks)
    check(aggregate["human_study_status"] == "NOT_RUN", "aggregate keeps human study NOT_RUN", checks)
    check(aggregate["inference_allowed"] is False, "aggregate forbids effect inference", checks)
    check(aggregate["overall"]["assigned_trials"] == 96, "aggregate assigned count is 96", checks)
    check(aggregate["overall"]["answered_trials"] == 90, "aggregate answered count is 90", checks)
    check(aggregate["overall"]["timeout_trials"] == 6, "aggregate timeout count is 6", checks)
    check(aggregate["by_profile"]["oracle"]["exact_three_way_accuracy_answered"] == 1.0, "oracle exercises perfect-accuracy path", checks)
    check(aggregate["by_profile"]["badge-follower"]["dangerous_approval_rate_answered"] == 1.0, "badge follower exercises dangerous-approval path", checks)
    check(aggregate["by_profile"]["hold-all"]["normal_nonapproval_rate_answered"] == 1.0, "hold-all exercises normal-nonapproval path", checks)
    check(aggregate["by_profile"]["hold-all"]["appropriate_hold_rate_answered"] == 1.0, "hold-all exercises uncertainty-HOLD path", checks)
    check(aggregate["by_condition"]["B0"]["assigned_trials"] == aggregate["by_condition"]["B1"]["assigned_trials"] == 48, "conditions have equal assigned counts", checks)

    report = {
        "schema_version": "1.0",
        "run_id": "synthetic-instrumentation-v1",
        "status": "PASS",
        "human_study_status": "NOT_RUN",
        "actor_type": "synthetic_dry_run",
        "exclude_from_human_analysis": True,
        "records_checked": len(rows),
        "checks_passed": len(checks),
        "checks_failed": 0,
        "checks": checks,
        "warning": "Validation success means the synthetic logging and metric paths behaved as specified. It is not a user-study result."
    }
    (RESULTS / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: report[key] for key in ("status", "records_checked", "checks_passed", "checks_failed", "human_study_status")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
