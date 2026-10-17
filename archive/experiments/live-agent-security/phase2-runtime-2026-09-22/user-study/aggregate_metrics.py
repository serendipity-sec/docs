"""Aggregate synthetic instrumentation records without treating them as human data."""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results" / "synthetic-dry-run"


def read_trials() -> list[dict]:
    return [json.loads(line) for line in (RESULTS / "study-trials.jsonl").read_text(encoding="utf-8").splitlines() if line]


def ratio(numerator: int, denominator: int):
    return round(numerator / denominator, 6) if denominator else None


def percentile(values: list[int], fraction: float):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def metrics(rows: list[dict]) -> dict:
    answered = [row for row in rows if not row["timeout"]]
    risk_assigned = [row for row in rows if row["reference_decision"] == "DENY"]
    risk = [row for row in answered if row["reference_decision"] == "DENY"]
    normal_assigned = [row for row in rows if row["reference_decision"] == "ALLOW"]
    normal = [row for row in answered if row["reference_decision"] == "ALLOW"]
    uncertain_assigned = [row for row in rows if row["reference_decision"] == "HOLD"]
    uncertain = [row for row in answered if row["reference_decision"] == "HOLD"]
    exact = [row for row in answered if row["decision"] == row["reference_decision"]]
    high_conf_wrong = [
        row for row in answered
        if row["decision"] != row["reference_decision"] and row["confidence_0_100"] >= 80
    ]
    durations = [row["duration_ms"] for row in rows]
    evidence_types = sorted({
        event["evidence_type"] for row in rows for event in row["evidence_events"]
    })
    dangerous_approvals = sum(row["decision"] == "ALLOW" for row in risk)
    normal_denials = sum(row["decision"] == "DENY" for row in normal)
    normal_nonapprovals = sum(row["decision"] in {"DENY", "HOLD"} for row in normal)
    appropriate_holds = sum(row["decision"] == "HOLD" for row in uncertain)
    uncertain_high_conf_allow = sum(
        row["decision"] == "ALLOW" and row["confidence_0_100"] >= 80 for row in uncertain
    )
    return {
        "assigned_trials": len(rows),
        "answered_trials": len(answered),
        "timeout_trials": len(rows) - len(answered),
        "decision_coverage": ratio(len(answered), len(rows)),
        "exact_three_way_matches": len(exact),
        "exact_three_way_accuracy_answered": ratio(len(exact), len(answered)),
        "exact_three_way_accuracy_all_assigned": ratio(len(exact), len(rows)),
        "risk_assigned": len(risk_assigned),
        "risk_answered": len(risk),
        "dangerous_approvals": dangerous_approvals,
        "dangerous_approval_rate_answered": ratio(dangerous_approvals, len(risk)),
        "normal_assigned": len(normal_assigned),
        "normal_answered": len(normal),
        "normal_denials": normal_denials,
        "normal_denial_rate_answered": ratio(normal_denials, len(normal)),
        "normal_nonapprovals": normal_nonapprovals,
        "normal_nonapproval_rate_answered": ratio(normal_nonapprovals, len(normal)),
        "uncertain_assigned": len(uncertain_assigned),
        "uncertain_answered": len(uncertain),
        "appropriate_holds": appropriate_holds,
        "appropriate_hold_rate_answered": ratio(appropriate_holds, len(uncertain)),
        "uncertain_high_confidence_allows": uncertain_high_conf_allow,
        "uncertain_high_confidence_allow_rate_answered": ratio(uncertain_high_conf_allow, len(uncertain)),
        "high_confidence_wrong": len(high_conf_wrong),
        "high_confidence_wrong_rate_answered": ratio(len(high_conf_wrong), len(answered)),
        "duration_ms_median_all_assigned": statistics.median(durations) if durations else None,
        "duration_ms_p90_all_assigned": percentile(durations, 0.9),
        "evidence_event_count": sum(len(row["evidence_events"]) for row in rows),
        "unique_evidence_types": evidence_types,
    }


def main() -> None:
    rows = read_trials()
    by_condition = defaultdict(list)
    by_profile = defaultdict(list)
    by_profile_condition = defaultdict(list)
    for row in rows:
        by_condition[row["condition"]].append(row)
        by_profile[row["profile_id"]].append(row)
        by_profile_condition[f"{row['profile_id']}::{row['condition']}"] .append(row)
    aggregate = {
        "schema_version": "1.0",
        "run_id": "synthetic-instrumentation-v1",
        "purpose": "instrumentation_validation_only",
        "human_study_status": "NOT_RUN",
        "actor_type": "synthetic_dry_run",
        "exclude_from_human_analysis": True,
        "reference_status": "design_expectation",
        "inference_allowed": False,
        "overall": metrics(rows),
        "by_condition": {key: metrics(value) for key, value in sorted(by_condition.items())},
        "by_profile": {key: metrics(value) for key, value in sorted(by_profile.items())},
        "by_profile_condition": {key: metrics(value) for key, value in sorted(by_profile_condition.items())},
        "warning": "Synthetic actors validate calculations and logging only. Condition differences are not estimates of human behavior or interface effects."
    }
    (RESULTS / "aggregate.json").write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Synthetic instrumentation aggregate",
        "",
        "**Actual human study: NOT_RUN.** All rows were generated by deterministic synthetic profiles and are excluded from human analysis.",
        "",
        "| scope | assigned | answered | timeout | exact/answered | dangerous approval | normal nonapproval | appropriate HOLD | high-confidence wrong |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    scopes = [("overall", aggregate["overall"])] + [
        (f"condition {key}", value) for key, value in aggregate["by_condition"].items()
    ] + [(f"profile {key}", value) for key, value in aggregate["by_profile"].items()]
    for label, value in scopes:
        lines.append(
            f"| {label} | {value['assigned_trials']} | {value['answered_trials']} | {value['timeout_trials']} | "
            f"{value['exact_three_way_accuracy_answered']} | {value['dangerous_approval_rate_answered']} | "
            f"{value['normal_nonapproval_rate_answered']} | {value['appropriate_hold_rate_answered']} | "
            f"{value['high_confidence_wrong_rate_answered']} |"
        )
    lines += [
        "",
        "These values are test vectors for metric code. They are not participant observations, effect estimates, or evidence that either presentation improves decisions.",
    ]
    (RESULTS / "aggregate.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(aggregate["overall"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
