# 캡스톤2 Slack 원문과 Codex 요약

Codex가 연결된 Slack 플러그인으로 대화를 읽고 이 저장소에 원문과 한국어 요약을 저장한다.
별도 OpenAI API 키, Slack 봇 토큰, 요약 서버를 사용하지 않는다.
예약 실행은 GitHub Actions가 아니라 사용자의 Codex 앱에서 수행한다.

## 운영 설정

| 항목 | 설정 |
|---|---|
| Slack | `capstone2-cxs4239.slack.com` — 표시 이름 `capstone2`(캡스톤2) |
| 확인한 워크스페이스 ID | `T0C2Y9MNME1` — Slack 도구의 실제 워크스페이스 조회와 채널 읽기로 검증 |
| 조회 계정 | `config.json`의 `slack_connection_link_id`를 모든 Slack 조회의 `link_id`로 지정 |
| 채널 | 연결된 계정에 보이는 공개 채널 전체. 별도 지정 전까지 비공개 채널·DM 제외 |
| 실행 시각 | 매일 새벽 01:00, 한국 시간 |
| 실행 순서 | 원문 수집 → 원문 GitHub 업로드 → Codex 요약 → 요약 GitHub 업로드 |
| 원문 | 채널과 스레드의 모든 페이지를 읽은 뒤 저장 |
| GitHub | 비공개 `serendipity-sec/docs`, `automation/slack-archive` 브랜치 |
| 로컬 작업 폴더 | `C:\Users\andyw\Desktop\serendipity-sec\.publication-work\slack-archive` |

로컬 파일을 사용하는 예약 실행에는 PC와 Codex 앱이 켜져 있어야 한다.
슬립·앱 종료·계정 사용 제한으로 실행이 지연되면 다음 실행에서 보이는 대화를 다시 수집한다.
채널 접근 권한과 Slack의 보존 기간을 넘어서는 대화는 복구할 수 없다.

## 현재 연결 상태

2026-10-07에 두 Slack 계정이 도구의 계정 목록에 노출되고, 계정별 `link_id`를 지정해
캡스톤2와 `whs-agentic-ai`를 각각 조회할 수 있음을 확인했다. 캡스톤2 `공지방`의 실제
메시지 읽기도 성공했다. 브라우저의 선택 상태나 `team_id`만으로 인증 계정을 바꾸지 않는다.
`config.json`의 `workspace_id`는 `T0C2Y9MNME1`, `connection_status`는 `WORKSPACE_VERIFIED`다.
캡스톤2 조회는 모든 Slack 도구 호출에 `slack_connection_link_id`를 명시한다.
두 계정의 기존 연결과 권한은 모두 유지한다.

2026-10-06에 현재 Codex 채팅으로 돌아오는 예약 작업을 매일 한국 시간 새벽 01:00으로 변경했다.
`캡스톤2 Slack 원문·요약 저장`(`2-slack`) 하나에서 원문 수집과 요약을 순서대로 처리한다.
기존 별도 23:00 요약 작업(`2-slack-2`)은 삭제했다.

2026-10-06 14:32:22 KST에 첫 수동 실행을 시도했다. 당시 Slack 도구의 워크스페이스 목록 전체를
조회했으나 `whs-agentic-ai`(`T0BLTQ38GUW`)만 반환했다. 대상 `T0C2Y9MNME1`에 접근할 수
없어 수집을 중단했다. 이 실패한 시도에서는 실제 원문과 요약을 만들지 않았다.

2026-10-07 첫 예약 실행에서는 공개 채널 8개의 접근 가능한 기록을 수집하고 실제 원문
9페이지(본문 73개와 스레드 답글 4개), 요약 8개를 전용 브랜치에 업로드했다.
원문 커밋은 `80d1012`, 요약 커밋은 `f41041d`이며 원격 SHA와 원문·요약 해시를 확인했다.
예약의 실제 시작은 09:14 KST, 수집 기준은 09:15:35 KST였다. 새벽 01:00 예약의 지연 원인은 미확인이다.
첫 백업에는 9월 20일부터 10월 6일까지의 기록이 포함되며, 첨부 본문은 포함하지 않는다.

## 저장 파일

```text
slack/
  config.json
  RUNBOOK.md
  raw/YYYY-MM-DD/C채널ID.jsonl
  summaries/YYYY-MM-DD/C채널ID.md
  state/channels/C채널ID.json
  state/summaries/YYYY-MM-DD/C채널ID.json
scripts/slack_archive.py
```

날짜는 **원문을 수집한 한국 날짜**다. 초기 백업에는 과거 메시지도 포함될 수 있으므로
요약에 실제 메시지 날짜와 수집 범위를 적는다. JSONL은 Slack 플러그인이 반환한 원래
`content`/`structuredContent`와 요청 인수를 보존한다. Slack 서버 전체의 원본 데이터 덤프를 뜻하지 않는다.
파일 메타데이터와 링크는 응답에 있는 범위로 포함하고, 첨부 바이너리 다운로드는 이 자동화의 범위에 포함하지 않는다.

매 수집에서 접근 가능한 채널 기록과 스레드를 다시 읽는다. 이 방식은 오래된 메시지에 붙은
새 답글을 놓치지 않도록 한다. 동일한 응답은 SHA-256으로 중복 저장을 건너뛴다.
수정된 응답은 새 스냅샷으로 남기며 이전 원문을 지우지 않는다.
메시지 삭제와 보존 기간 만료 전후의 완전한 감사 로그는 보장하지 않는다.

요약은 새로 저장되거나 변경된 원문이 있는 날짜·채널에 대해 생성한다.
요약 실패는 원문 저장을 되돌리지 않는다. 원문 해시가 바뀌면 다음 요약 실행에서 다시 처리한다.
예약을 등록했다는 사실과 실제 첫 수집·요약·GitHub 업로드 성공은 각각 확인한다.

## 확인

```powershell
python scripts/slack_archive.py status
python scripts/slack_archive.py summary-plan
python -m unittest discover -s tests -v
```

`live_collection_confirmed`는 실제 원문 페이지가 있을 때만 `true`다.
테스트는 임시 폴더에서 실행하며 가짜 Slack 메시지를 실제 `raw/`에 만들지 않는다.

예약 작업의 자세한 실행 순서는 [RUNBOOK.md](RUNBOOK.md)를 따른다.
공식 기능 조건은 [Codex 예약 실행 문서](https://learn.chatgpt.com/docs/automations?surface=app)를 참고한다.
