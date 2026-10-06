# 캡스톤2 Slack 원문과 Codex 요약

Codex가 연결된 Slack 플러그인으로 대화를 읽고 이 저장소에 원문과 한국어 요약을 저장한다.
별도 OpenAI API 키, Slack 봇 토큰, 요약 서버를 사용하지 않는다.
예약 실행은 GitHub Actions가 아니라 사용자의 Codex 앱에서 수행한다.

## 운영 설정

| 항목 | 설정 |
|---|---|
| Slack | `capstone2-cxs4239.slack.com` — 표시 이름 `capstone2`(캡스톤2) |
| 확인한 워크스페이스 ID | `T0C2Y9MNME1` — 브라우저 URL로 확인, 플러그인 연결은 별도 검증 |
| 채널 | 공개 채널 전체. 별도 지정 전까지 비공개 채널·DM 제외 |
| 원문 | 매시간, 채널과 스레드의 모든 페이지를 읽은 뒤 저장 |
| 요약 | 매일 23:00, 한국 시간 |
| GitHub | 비공개 `serendipity-sec/docs`, `automation/slack-archive` 브랜치 |
| 로컬 작업 폴더 | `C:\Users\andyw\Desktop\serendipity-sec\.publication-work\slack-archive` |

로컬 파일을 사용하는 예약 실행에는 PC와 Codex 앱이 켜져 있어야 한다.
슬립·앱 종료·계정 사용 제한으로 실행이 지연되면 다음 실행에서 보이는 대화를 다시 수집한다.
채널 접근 권한과 Slack의 보존 기간을 넘어서는 대화는 복구할 수 없다.

## 현재 연결 상태

초기 확인에서 Slack 플러그인은 `whs-agentic-ai`만 반환했고, 캡스톤2 채널 조회는
`channel_not_found`로 실패했다. 사용자가 OAuth 권한을 승인한 뒤 ChatGPT의 Slack 플러그인
화면에 `캡스톤2` 연결이 추가되고 선택된 것을 확인했다. 현재 채팅의 Slack 도구는 아직
이전 워크스페이스를 반환하므로 첫 실제 수집은 미확인이다.
`config.json`의 `workspace_id`는 플러그인에서 정확한 워크스페이스를 확인하기 전까지 `null`이다.
실제 원문이 저장되기 전에는 수집 성공으로 보고하지 않는다. 실제 첫 수집 후 이 상태 설명을 갱신한다.

2026-10-06에 현재 Codex 채팅으로 돌아오는 예약 작업을 등록했다.
`캡스톤2 Slack 원문 저장`(`2-slack`)은 매시간, `캡스톤2 Slack 일일 요약`(`2-slack-2`)은
매일 한국 시간 23:00에 실행하도록 설정했다. 첫 실제 수집·요약·원격 업로드는 아직 미확인이다.

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
