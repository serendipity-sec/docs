#!/usr/bin/env python3
"""serendipity-sec 팀 현황 수집기.

gh CLI로 docs·platform 저장소의 활동을 모아 JSON 하나로 출력한다.
읽기 전용이며 GitHub에 아무것도 쓰지 않는다.

    python collect.py              # 최근 7일
    python collect.py --days 14
    python collect.py --since 2026-09-28
"""
import argparse
import csv
import io
import json
import re
import subprocess
import sys
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import quote

ORG = "serendipity-sec"
REPOS = ["docs", "platform"]
KST = timezone(timedelta(hours=9))

# GitHub ID → 이름 (2026-10-06 팀 확인)
MEMBERS = {
    "vmaca123": "김민우",
    "yangyu0330": "양유상",
    "bear300811": "장준서",
    "uptime-zero": "박용준",
}

SEMESTER_START = date(2026, 8, 31)  # 1주차 월요일 (docs/notion/02_주차계획.csv)
FIRST_MEETING = date(2026, 9, 15)
# 고정 회의: 목 14시 오프라인, 토 20시 온라인. 회의록 기한은 회의 후 24시간
MEETING_TIMES = {3: time(14), 5: time(20)}

DELIVERABLES_CSV = "notion/01_제출물.csv"
# 승인 1명 이상이 필요한 저장소. docs는 사람별 브랜치에서 승인 없이 바로 머지한다
REVIEW_REQUIRED = {"platform"}
REVIEW_WAIT_DAYS = 2
ISSUE_LINK_RE = re.compile(r"\b(close[sd]?|fix(e[sd])?|resolve[sd]?|refs?)\s*:?\s*#\d+", re.I)

errors = []


class GhError(Exception):
    pass


def gh(path, raw=False):
    cmd = ["gh", "api", path]
    if raw:
        cmd += ["-H", "Accept: application/vnd.github.raw"]
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8")
    if r.returncode != 0:
        raise GhError(f"{path}: {r.stderr.strip()[:200]}")
    return r.stdout if raw else json.loads(r.stdout or "null")


def gh_list(path):
    sep = "&" if "?" in path else "?"
    items, page = [], 1
    while True:
        batch = gh(f"{path}{sep}per_page=100&page={page}")
        items += batch
        if len(batch) < 100:
            return items
        page += 1


def safe(fn, default):
    try:
        return fn()
    except GhError as e:
        errors.append(str(e))
        return default


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def kst(dt):
    return dt.astimezone(KST).strftime("%m-%d %H:%M") if dt else None


def name(login):
    return MEMBERS.get(login, login) if login else None


def new_person(login):
    return {
        "login": login, "name": name(login),
        "commits": 0, "prs_opened": 0, "prs_merged": 0, "reviews_given": 0,
        "issues_opened": 0, "issues_closed": 0, "comments": 0,
        "last_activity": None, "did": [],
    }


def collect_repo(repo, since, now, people, flags):
    base = f"repos/{ORG}/{repo}"
    since_iso = since.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def person(login):
        if login not in people:
            people[login] = new_person(login)
        return people[login]

    def did(login, kind, text, when):
        person(login)["did"].append({"repo": repo, "kind": kind, "text": text, "at": kst(when)})

    # 커밋: 모든 브랜치, SHA 기준 중복 제거
    branches = [b["name"] for b in safe(lambda: gh_list(f"{base}/branches"), [])]
    commits = {}
    for br in branches:
        for c in safe(lambda: gh_list(f"{base}/commits?sha={quote(br, safe='')}&since={since_iso}"), []):
            entry = commits.setdefault(c["sha"], {"c": c, "branches": []})
            entry["branches"].append(br)

    unlinked, direct_pushes = [], []
    for sha, entry in commits.items():
        c = entry["c"]
        login = (c.get("author") or {}).get("login")
        when = ts(c["commit"]["author"]["date"])
        subject = c["commit"]["message"].splitlines()[0]
        if not login:
            unlinked.append({"sha": sha[:7], "author_name": c["commit"]["author"]["name"], "subject": subject})
            continue
        person(login)["commits"] += 1
        did(login, "commit", f"[{','.join(entry['branches'])}] {subject}", when)
        if "main" in entry["branches"] and len(c.get("parents", [])) < 2:
            pulls = safe(lambda: gh(f"{base}/commits/{sha}/pulls"), None)
            if pulls == []:
                direct_pushes.append({"sha": sha[:7], "by": name(login), "subject": subject, "at": kst(when)})

    if unlinked:
        flags.append({"severity": 2, "type": "unlinked_commits", "repo": repo, "items": unlinked,
                      "why": "GitHub 계정과 연결 안 된 커밋은 기여도 집계에서 빠짐 (팀-온보딩.md 2번)"})
    if direct_pushes:
        flags.append({"severity": 3, "type": "direct_push_to_main", "repo": repo, "items": direct_pushes,
                      "why": "규칙상 main 직접 push 금지. Free 플랜 private 저장소라 브랜치 보호가 꺼져 있음"})

    # PR
    open_prs, unapproved = [], []
    for pr in safe(lambda: gh_list(f"{base}/pulls?state=all&sort=updated&direction=desc"), []):
        updated = ts(pr["updated_at"])
        if pr["state"] != "open" and updated < since:
            continue
        author = pr["user"]["login"]
        created, merged = ts(pr["created_at"]), ts(pr.get("merged_at"))
        title = f"#{pr['number']} {pr['title']}"
        if created >= since:
            person(author)["prs_opened"] += 1
            did(author, "pr_opened", title, created)
        if merged and merged >= since:
            person(author)["prs_merged"] += 1
            did(author, "pr_merged", title, merged)

        reviews = safe(lambda: gh_list(f"{base}/pulls/{pr['number']}/reviews"), [])
        for rv in reviews:
            rv_login = (rv.get("user") or {}).get("login")
            rv_at = ts(rv.get("submitted_at"))
            if rv_login and rv_at and rv_at >= since and rv_login != author:
                person(rv_login)["reviews_given"] += 1
                did(rv_login, "review", f"{rv['state']} on {title}", rv_at)

        approved = any(rv["state"] == "APPROVED" and (rv.get("user") or {}).get("login") != author for rv in reviews)
        if (merged and merged >= since and repo in REVIEW_REQUIRED
                and not approved and not author.endswith("[bot]")):
            unapproved.append({"number": pr["number"], "title": pr["title"], "author": name(author), "at": kst(merged)})

        if pr["state"] == "open" and repo not in REVIEW_REQUIRED:
            open_prs.append({"number": pr["number"], "title": pr["title"], "author": name(author),
                             "age_days": (now - created).days, "draft": pr.get("draft", False),
                             "review_states": ["승인 불필요"], "url": pr["html_url"]})
        elif pr["state"] == "open":
            age = (now - created).days
            reviewed = any((rv.get("user") or {}).get("login") != author for rv in reviews)
            linked = bool(ISSUE_LINK_RE.search(pr.get("body") or ""))
            item = {
                "number": pr["number"], "title": pr["title"], "author": name(author),
                "age_days": age, "draft": pr.get("draft", False),
                "assignees": [name(a["login"]) for a in pr.get("assignees", [])],
                "requested_reviewers": [name(r["login"]) for r in pr.get("requested_reviewers", [])],
                "review_states": sorted({rv["state"] for rv in reviews if (rv.get("user") or {}).get("login") != author}),
                "linked_issue": linked, "url": pr["html_url"],
            }
            open_prs.append(item)
            if not reviewed and not item["draft"] and age >= REVIEW_WAIT_DAYS:
                flags.append({"severity": 3, "type": "pr_waiting_review", "repo": repo,
                              "items": [{"number": pr["number"], "title": pr["title"], "author": name(author), "age_days": age}],
                              "why": f"{age}일째 리뷰 없음. 승인 1명 있어야 머지 가능"})
            if not linked:
                flags.append({"severity": 1, "type": "pr_without_issue", "repo": repo,
                              "items": [{"number": pr["number"], "title": pr["title"]}],
                              "why": "PR 본문에 Closes #N 없음. 머지해도 이슈가 자동으로 안 닫힘"})
    if unapproved:
        flags.append({"severity": 2, "type": "merged_without_approval", "repo": repo, "items": unapproved,
                      "why": "승인 1명 이상 받고 머지하는 규칙. Free 플랜이라 GitHub가 막지 못함"})

    # 이슈 (PR 제외, 자동 생성 주간 현황 제외)
    open_issues = []
    for it in safe(lambda: gh_list(f"{base}/issues?state=all&sort=updated&direction=desc"), []):
        if "pull_request" in it or any(lb["name"] == "weekly-report" for lb in it.get("labels", [])):
            continue
        opener, created, closed = it["user"]["login"], ts(it["created_at"]), ts(it.get("closed_at"))
        title = f"#{it['number']} {it['title']}"
        if created >= since:
            person(opener)["issues_opened"] += 1
            did(opener, "issue_opened", title, created)
        if closed and closed >= since:
            closer = (safe(lambda: gh(f"{base}/issues/{it['number']}"), {}).get("closed_by") or {}).get("login")
            if closer:
                person(closer)["issues_closed"] += 1
                did(closer, "issue_closed", title, closed)
        if it["state"] == "open":
            open_issues.append({
                "number": it["number"], "title": it["title"], "opener": name(opener),
                "assignees": [name(a["login"]) for a in it.get("assignees", [])],
                "labels": [lb["name"] for lb in it.get("labels", [])],
                "milestone": (it.get("milestone") or {}).get("title"),
                "age_days": (now - created).days, "url": it["html_url"],
            })

    # 댓글 (이슈 + PR)
    for cm in safe(lambda: gh_list(f"{base}/issues/comments?since={since_iso}"), []):
        login = (cm.get("user") or {}).get("login")
        if login and ts(cm["created_at"]) >= since:
            person(login)["comments"] += 1

    # 마지막 활동 (이벤트 API, 최근 90일)
    for ev in safe(lambda: gh_list(f"{base}/events"), []):
        login, at = ev["actor"]["login"], ts(ev["created_at"])
        p = person(login)
        if not p["last_activity"] or at > p["last_activity"]:
            p["last_activity"] = at

    # CI
    # 워크플로·브랜치별 가장 최근 실행만 본다. 이미 다시 성공한 실패는 경고하지 않는다
    runs = safe(lambda: gh(f"{base}/actions/runs?per_page=50"), {}).get("workflow_runs", [])
    latest = {}
    for r in runs:  # API는 최신순
        latest.setdefault((r["name"], r["head_branch"]), r)
    failed = [{"workflow": r["name"], "branch": r["head_branch"], "at": kst(ts(r["created_at"])), "url": r["html_url"]}
              for r in latest.values() if r.get("conclusion") == "failure" and ts(r["created_at"]) >= since]
    if failed:
        flags.append({"severity": 2, "type": "ci_failed", "repo": repo, "items": failed, "why": "워크플로 실패"})

    return {"branches": branches, "commits_in_window": len(commits),
            "open_prs": open_prs, "open_issues": open_issues,
            "workflows_seen": sorted({r["name"] for r in runs})}


def collect_deliverables(today, flags):
    text = safe(lambda: gh(f"repos/{ORG}/docs/contents/{quote(DELIVERABLES_CSV)}", raw=True), "")
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        due = date.fromisoformat(row["마감일"])
        path = row["GitHub 경로"].strip()
        files = None
        if path.startswith("docs/") and path != "docs/":
            sub = path[len("docs/"):].rstrip("/")
            listing = safe(lambda: gh(f"repos/{ORG}/docs/contents/{quote(sub)}"), [])
            files = [f["name"] for f in listing if f["name"] != ".gitkeep"] if isinstance(listing, list) else []
        d = {"name": row["산출물"], "week": row["주차"], "due": row["마감일"], "d_day": (due - today).days,
             "owner": row["담당"] or None, "points": row["관련 배점"], "csv_status": row["상태"],
             "path": path, "files_in_github": files}
        out.append(d)
        if 0 <= d["d_day"] <= 7 and not d["owner"]:
            flags.append({"severity": 3, "type": "deadline_no_owner", "items": [d],
                          "why": f"마감 D-{d['d_day']}인데 담당자 없음"})
        if d["d_day"] < 0 and files == []:
            flags.append({"severity": 2, "type": "past_due_not_in_github", "items": [d],
                          "why": "마감 지났는데 GitHub 제출 폴더가 비어 있음 (LMS로만 냈다면 사본 커밋 필요)"})
    return out


def collect_meetings(now, flags):
    listing = safe(lambda: gh(f"repos/{ORG}/docs/contents/meetings"), [])
    have = set()
    for f in listing if isinstance(listing, list) else []:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", f["name"])
        if m:
            have.add(date.fromisoformat(m.group(1)))
    expected, d = [FIRST_MEETING], FIRST_MEETING + timedelta(days=1)
    while d <= now.date():
        if d.weekday() in MEETING_TIMES:
            expected.append(d)
        d += timedelta(days=1)
    missing = []
    for d in expected:
        t = MEETING_TIMES.get(d.weekday(), time(0))
        due = datetime.combine(d, t, KST) + timedelta(hours=24)
        if due < now and d not in have:
            missing.append(f"{d.isoformat()}({'월화수목금토일'[d.weekday()]})")
    if missing:
        flags.append({"severity": 2, "type": "minutes_missing", "items": missing,
                      "why": "고정 회의일 기준 회의록 미커밋 (회의가 실제로 열렸는지 확인 필요). 출석 10점 근거"})
    return {"committed_dates": sorted(x.isoformat() for x in have), "missing": missing}


FLAG_TITLES = {
    "deadline_no_owner": "마감 임박인데 담당자 없음",
    "pr_waiting_review": "리뷰 대기 PR",
    "direct_push_to_main": "main 직접 push",
    "past_due_not_in_github": "마감 지난 제출물이 GitHub에 없음",
    "minutes_missing": "회의록 미커밋",
    "unlinked_commits": "계정 연결 안 된 커밋",
    "ci_failed": "워크플로 실패",
    "pr_without_issue": "이슈 연결 없는 PR",
    "merged_without_approval": "승인 없이 머지된 PR",
    "no_activity_in_window": "기간 내 GitHub 활동 없음",
}


def fmt_item(it):
    if isinstance(it, str):
        return it
    parts = []
    if "number" in it:
        parts.append(f"#{it['number']}")
    if "sha" in it:
        parts.append(f"`{it['sha']}`")
    for k in ("name", "title", "subject", "workflow"):
        if it.get(k):
            parts.append(it[k])
    who = it.get("by") or it.get("author") or it.get("author_name")
    if who:
        parts.append(f"({who})")
    if "age_days" in it:
        parts.append(f"{it['age_days']}일째")
    if "due" in it:
        dd = it["d_day"]
        parts.append(f"마감 {it['due']} ({f'D-{dd}' if dd >= 0 else f'D+{-dd}'})")
    if it.get("at"):
        parts.append(it["at"])
    return " ".join(parts)


def render_md(r, max_did=15):
    upcoming = [d for d in r["deliverables"] if d["d_day"] >= 0][:3]
    lines = [
        f"# 주간 현황 — {r['semester_week']}주차 ({r['generated_at'][:10]})",
        "",
        f"집계 기간 {r['window']['since']} ~ {r['window']['until']} KST · {r['semester_week']}주차 / 15주",
        "",
        "## 다가오는 마감",
        "",
        "| 산출물 | 마감 | D-day | 담당 | GitHub 제출 파일 |",
        "|---|---|---|---|---|",
    ]
    for d in upcoming:
        files = "—" if d["files_in_github"] is None else (f"{len(d['files_in_github'])}개" if d["files_in_github"] else "없음")
        lines.append(f"| {d['name']} | {d['due']} | D-{d['d_day']} | {d['owner'] or '**미정**'} | {files} |")

    lines += ["", "## 사람별 활동", "",
              "| 이름 | 커밋 | PR 열림/머지 | 리뷰 | 이슈 열림/닫음 | 댓글 | 마지막 활동 |",
              "|---|---|---|---|---|---|---|"]
    for p in r["people"]:
        lines.append(f"| {p['name']} | {p['commits']} | {p['prs_opened']}/{p['prs_merged']} | {p['reviews_given']} "
                     f"| {p['issues_opened']}/{p['issues_closed']} | {p['comments']} | {p['last_activity'] or '—'} |")
    lines += ["", "<details><summary>사람별 상세</summary>", ""]
    for p in r["people"]:
        if not p["did"]:
            continue
        lines.append(f"**{p['name']}**")
        lines += [f"- {x['at']} `{x['repo']}` {x['kind']}: {x['text']}" for x in p["did"][:max_did]]
        if len(p["did"]) > max_did:
            lines.append(f"- … 외 {len(p['did']) - max_did}건")
        lines.append("")
    lines += ["</details>", ""]

    open_prs = [(repo, pr) for repo, v in r["repos"].items() for pr in v["open_prs"]]
    open_issues = [(repo, it) for repo, v in r["repos"].items() for it in v["open_issues"]]
    lines += ["## 열린 PR", ""]
    lines += [f"- {repo}#{pr['number']} {pr['title']} · {pr['author']} · {pr['age_days']}일째 · "
              f"{'초안' if pr['draft'] else (', '.join(pr['review_states']) or '리뷰 없음')}"
              for repo, pr in open_prs] or ["- 없음"]
    lines += ["", "## 열린 이슈", ""]
    lines += [f"- {repo}#{it['number']} {it['title']} · 담당 {', '.join(it['assignees']) or '없음'} · {it['age_days']}일째"
              for repo, it in open_issues] or ["- 없음"]

    lines += ["", "## 확인 필요", ""]
    for f in r["flags"] or []:
        items = f["items"] if isinstance(f["items"], list) else [f["items"]]
        repo = f" ({f['repo']})" if f.get("repo") else ""
        lines.append(f"- **{FLAG_TITLES.get(f['type'], f['type'])}{repo}** — {f['why']}")
        lines += [f"  - {fmt_item(it)}" for it in items[:5]]
        if len(items) > 5:
            lines.append(f"  - … 외 {len(items) - 5}건")
    if not r["flags"]:
        lines.append("- 없음")
    if r["errors"]:
        lines += ["", "## 수집 오류", ""] + [f"- `{e}`" for e in r["errors"]]
    lines += ["", "---", "노션·Discord·오프라인 작업은 집계되지 않습니다. 생성: `.github/scripts/team_status.py`"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--since", help="YYYY-MM-DD (KST)")
    ap.add_argument("--md", action="store_true", help="JSON 대신 Markdown 보고서 출력 (첫 줄이 제목)")
    args = ap.parse_args()

    now = datetime.now(KST)
    since = (datetime.combine(date.fromisoformat(args.since), time(0), KST) if args.since
             else now - timedelta(days=args.days))

    flags = []
    people = {m: new_person(m) for m in
              [u["login"] for u in safe(lambda: gh_list(f"orgs/{ORG}/members"), [])] or list(MEMBERS)}

    repos = {r: collect_repo(r, since, now, people, flags) for r in REPOS}

    for p in people.values():
        if p["last_activity"]:
            p["days_since_last_activity"] = (now - p["last_activity"]).days
            p["last_activity"] = kst(p["last_activity"])
        p["did"].sort(key=lambda x: x["at"] or "", reverse=True)
        p["active_in_window"] = any(p[k] for k in
                                    ("commits", "prs_opened", "prs_merged", "reviews_given",
                                     "issues_opened", "issues_closed", "comments"))
    idle = [p["name"] for p in people.values() if not p["active_in_window"]]
    if idle:
        flags.append({"severity": 1, "type": "no_activity_in_window", "items": idle,
                      "why": "기간 내 GitHub 활동 없음 (노션·오프라인 작업은 여기 안 잡힘)"})

    result = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M KST"),
        "window": {"since": kst(since), "until": kst(now)},
        "semester_week": (now.date() - SEMESTER_START).days // 7 + 1,
        "deliverables": collect_deliverables(now.date(), flags),
        "meetings": collect_meetings(now, flags),
        "people": sorted(people.values(), key=lambda p: -(p["commits"] + p["prs_opened"] + p["reviews_given"])),
        "repos": repos,
        "flags": sorted(flags, key=lambda f: -f["severity"]),
        "errors": errors,
    }
    sys.stdout.reconfigure(encoding="utf-8")
    if args.md:
        sys.stdout.write(render_md(result))
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
