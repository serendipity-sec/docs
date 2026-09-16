#!/usr/bin/env bash
# GitHub Organization 초기 세팅
#
# 사전 준비 (사람이 직접 해야 하는 두 가지):
#   1) gh auth login -h github.com -s admin:org,repo,workflow
#   2) https://github.com/account/organizations/new  에서 Free 플랜으로 org 생성
#
# 그 다음:  bash setup-github.sh
set -euo pipefail

# ─────────────────────────────────────────────────────────────
# 여기만 고치면 됩니다
ORG="serendipity-sec"

# 조직에 초대할 팀원 GitHub ID (@ 없이). 본인 ID는 넣지 마세요.
# 웹에서 이미 초대했다면 비워 두면 됩니다. 이미 있는 멤버는 건너뜁니다.
MEMBERS=(
  "uptime-zero"
)

# 지도교수님 ID (외부 협력자로 초대. 모르면 비워 두세요)
PROFESSOR_ID=""
# ─────────────────────────────────────────────────────────────

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say() { printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }
ok()  { printf '  \033[32m✔\033[0m %s\n' "$*"; }
warn(){ printf '  \033[33m!\033[0m %s\n' "$*"; }

say "인증 확인"
# gh auth status 는 오래된 keyring 항목 때문에 실패할 수 있으므로
# 실제 API 호출로 확인합니다.
WHOAMI="$(gh api user --jq .login 2>/dev/null)" || {
  echo "gh 로그인이 안 돼 있습니다. 먼저 실행하세요:"
  echo "  gh auth login -h github.com -s admin:org,repo,workflow"
  exit 1
}
SCOPES="$(gh api -i user 2>/dev/null | grep -i '^x-oauth-scopes:' || true)"
case "$SCOPES" in
  *admin:org*) : ;;
  *) echo "admin:org 스코프가 없어 조직/팀 설정을 할 수 없습니다. 실행하세요:"
     echo "  gh auth refresh -h github.com -s admin:org,repo,workflow"
     exit 1 ;;
esac
ok "로그인: $WHOAMI"

say "조직 확인: $ORG"
gh api "orgs/$ORG" --jq .login >/dev/null 2>&1 || {
  echo "조직 '$ORG' 을 찾을 수 없습니다."
  echo "https://github.com/account/organizations/new 에서 Free 플랜으로 먼저 만드세요."
  exit 1
}
ok "조직 확인됨"

# ── 저장소 생성 + push ────────────────────────────────────────
for REPO in platform docs; do
  say "저장소: $ORG/$REPO"
  if gh repo view "$ORG/$REPO" >/dev/null 2>&1; then
    warn "이미 존재합니다. 생성을 건너뜁니다."
  else
    gh repo create "$ORG/$REPO" --private \
      --description "$([ "$REPO" = platform ] \
        && echo 'AI 워크플로 구성요소의 공급망 보안 검사 및 공유 플랫폼' \
        || echo '팀 serendipity 문서 저장소 — 회의록·제출물·조사 자료')"
    ok "생성됨"
  fi

  cd "$ROOT/$REPO"
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/$ORG/$REPO.git"
  git push -u origin main
  ok "push 완료 → https://github.com/$ORG/$REPO"
  cd "$ROOT"
done

# ── 라벨 ─────────────────────────────────────────────────────
say "라벨 정리 (platform)"
# GitHub 기본 라벨 중 안 쓰는 것 제거
for L in "good first issue" "help wanted" "invalid" "question" "wontfix" "duplicate"; do
  gh label delete "$L" --repo "$ORG/platform" --yes 2>/dev/null || true
done

add_label() { gh label create "$1" --color "$2" --description "$3" \
                --repo "$ORG/platform" --force >/dev/null; ok "$1"; }

add_label "task"          "0e8a16" "구현·문서·설정 작업"
add_label "bug"           "d73a4a" "동작이 예상과 다름"
add_label "research"      "1d76db" "기술 선택·선행 도구 비교·근거 수집"
add_label "security"      "b60205" "이 플랫폼 자체의 보안 이슈"
add_label "area:scanner"  "5319e7" "규칙·스킬·MCP 정적 검사 엔진"
add_label "area:graph"    "5319e7" "관계 그래프·시각화"
add_label "area:backend"  "5319e7" "API·저장·검사 파이프라인"
add_label "area:frontend" "5319e7" "화면·검토 흐름"
add_label "area:infra"    "5319e7" "CI/CD·배포·개발 환경"
add_label "area:eval"     "5319e7" "평가 데이터셋·성능 측정"
add_label "P0"            "b60205" "이번 주에 끝내야 함"
add_label "P1"            "fbca04" "이번 스프린트"
add_label "P2"            "c2e0c6" "여유 있을 때"
add_label "blocked"       "000000" "다른 작업이나 결정을 기다리는 중"
add_label "needs-review"  "fbca04" "리뷰 대기"

# ── 팀 ───────────────────────────────────────────────────────
say "팀 생성: @$ORG/dev"
gh api "orgs/$ORG/teams" -f name="dev" \
  -f description="캡스톤 개발팀" -f privacy="closed" >/dev/null 2>&1 \
  && ok "생성됨" || warn "이미 있거나 생성 실패 (계속 진행)"

for M in "${MEMBERS[@]:-}"; do
  [ -z "$M" ] && continue
  if gh api "users/$M" >/dev/null 2>&1; then
    gh api --method PUT "orgs/$ORG/memberships/$M" -f role=member >/dev/null
    gh api --method PUT "orgs/$ORG/teams/dev/memberships/$M" -f role=member >/dev/null 2>&1 || true
    ok "초대/확인: $M → @$ORG/dev"
  else
    warn "GitHub 사용자를 찾을 수 없습니다: $M"
  fi
done

for REPO in platform docs; do
  gh api --method PUT "orgs/$ORG/teams/dev/repos/$ORG/$REPO" \
    -f permission=push >/dev/null 2>&1 && ok "@$ORG/dev → $REPO (write)" || true
done

if [ -n "$PROFESSOR_ID" ]; then
  for REPO in platform docs; do
    gh api --method PUT "repos/$ORG/$REPO/collaborators/$PROFESSOR_ID" \
      -f permission=pull >/dev/null && ok "교수님 초대: $PROFESSOR_ID → $REPO (read)"
  done
fi

# ── 조직 기본 권한 ───────────────────────────────────────────
say "조직 기본 저장소 권한"
gh api --method PATCH "orgs/$ORG" -f default_repository_permission=write >/dev/null
ok "멤버 기본 권한 = write (팀 배정 전에도 push 가능)"

# ── 저장소 설정 ──────────────────────────────────────────────
say "저장소 설정"
for REPO in platform docs; do
  gh api --method PATCH "repos/$ORG/$REPO" \
    -F has_issues=true -F has_wiki=false -F has_projects=true \
    -F allow_squash_merge=true -F allow_merge_commit=false \
    -F allow_rebase_merge=false -F delete_branch_on_merge=true \
    -F allow_auto_merge=true >/dev/null
  ok "$REPO — squash merge만 허용, 머지 후 브랜치 자동 삭제"
done

say "완료"
echo "  https://github.com/$ORG/platform"
echo "  https://github.com/$ORG/docs"
echo
echo "남은 수동 작업:"
echo "  - 무료 org의 private 저장소는 브랜치 보호 규칙을 쓸 수 없습니다."
echo "    GitHub Student Developer Pack(education.github.com/pack)을 신청하면 열립니다."
echo "    그동안은 CONTRIBUTING.md의 '리뷰어 1명 승인 후 머지' 규칙을 수동으로 지킵니다."
echo "  - Projects 보드를 만들어 주차 단위로 이슈를 관리하세요."
