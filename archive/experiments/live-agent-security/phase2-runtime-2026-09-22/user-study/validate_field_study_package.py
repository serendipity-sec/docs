"""Read-only checks for the empty human field-study package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
DOCS_ROOT = BASE.parents[3]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    required_docs = [
        "field-study-protocol.md",
        "participant-instructions.md",
        "consent-template.md",
        "facilitator-checklist.md",
    ]
    required_json = [
        "human-run-manifest.template.json",
        "human-trial.template.json",
        "schema/human-run-manifest.schema.json",
        "schema/human-study-trial.schema.json",
    ]
    checks: list[tuple[str, bool]] = []
    for name in required_docs + required_json:
        checks.append((f"required file exists: {name}", (BASE / name).is_file()))

    run = load(BASE / "human-run-manifest.template.json")
    trial = load(BASE / "human-trial.template.json")
    run_schema = load(BASE / "schema" / "human-run-manifest.schema.json")
    trial_schema = load(BASE / "schema" / "human-study-trial.schema.json")

    checks += [
        ("human run status is NOT_RUN", run["status"] == "NOT_RUN"),
        ("human run has no study id", run["study_id"] is None),
        ("human run excludes synthetic data", run["synthetic_data_included"] is False),
        ("human run contains no human files", run["human_data_files"] == []),
        ("recruitment is NOT_RUN", run["recruitment"]["status"] == "NOT_RUN"),
        ("collection is NOT_RUN", run["data_collection"]["status"] == "NOT_RUN"),
        ("analysis is NOT_RUN", run["analysis"]["status"] == "NOT_RUN"),
        ("all recruitment counts are null", all(run["recruitment"][key] is None for key in ("target_count", "invited_count", "screened_count", "consented_count"))),
        ("all collection counts are null", all(run["data_collection"][key] is None for key in ("started_sessions", "completed_sessions", "withdrawn_sessions", "technical_failure_sessions"))),
        ("all analysis result fields are null", all(value is None for key, value in run["analysis"].items() if key != "status")),
        ("trial template status is NOT_RUN", trial["collection_status"] == "NOT_RUN"),
        ("trial template has no participant id", trial["participant_id"] is None),
        ("trial template has no decision", trial["decision"] is None),
        ("trial template has no confidence", trial["confidence_0_100"] is None),
        ("run schema is draft 2020-12", run_schema["$schema"].endswith("2020-12/schema")),
        ("trial schema is draft 2020-12", trial_schema["$schema"].endswith("2020-12/schema")),
        ("run schema required fields match template", set(run_schema["required"]) == set(run)),
        ("trial schema required fields match template", set(trial_schema["required"]) == set(trial)),
    ]

    for name in required_docs:
        text = (BASE / name).read_text(encoding="utf-8")
        checks.append((f"document states NOT_RUN: {name}", "NOT_RUN" in text))

    source = DOCS_ROOT / run["reference_set"]["source_cases_path"]
    checks.append(("source cases exist", source.is_file()))
    checks.append(("source cases hash matches template", sha(source) == run["reference_set"]["source_cases_sha256"]))

    failures = [name for name, passed in checks if not passed]
    report = {
        "status": "PASS" if not failures else "FAIL",
        "human_study_status": "NOT_RUN",
        "checks": len(checks),
        "failed": len(failures),
        "failures": failures,
        "note": "This validates empty templates only. No recruitment, consent, response collection, or human analysis occurred."
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
