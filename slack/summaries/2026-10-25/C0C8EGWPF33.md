# GitHub PR 알림 — 고정 profile·입력 저장·pipeline·재현 자료 후속

## 수집 범위

capstone2 공개 채널, **2026-10-25 00:56:25 KST** 기준. 예약 목표 01:00과 실제 수집을 구분한다. 실제 TS 날짜 **10/11~23**, history 2페이지 고유 104개·스레드 37개의 실제 답글 43개를 끝까지 대조했다. 답글은 모두 history와 겹치고 새 TS는 없다. 페이지 경계의 반복 부모는 한 번만 세었다. [이번 raw](../../raw/2026-10-25/C0C8EGWPF33.jsonl)는 변경된 history 1페이지이며 나머지 동일 응답은 이전 raw에 보존했다. 초기 과거 백업 이후 재조회이고 [직전 요약](../2026-10-24/C0C8EGWPF33.md)과 이어 읽는다.

## 결정 사항

새 팀 결정·승인·병합을 확인한 것은 아니다. 기존 10/19 PR 메시지 네 개의 갱신된 발췌를 작성자의 구현·수정 보고로 기록한다. 정확한 Slack 편집시각은 제공되지 않았다.

## 진행 상황

- **platform #56**: 고정 profile로 workflow-only 비교의 환경·정책·모델 변경을 거부한다고 설명한다. 직접 OpenAI/Anthropic/Gemini/Ollama 노드와 embedding/reranker 연결 검사, 추가 고정 노드의 동적 parameters 거부, endpoint 고정을 증명할 수 없는 MCP client의 명시적 미지원이 포함된다. 검증 영수증을 Handoff snapshots 확장에 보존하고 입력과 겹치지 않는 profile 출력에 write/flush/fsync 후 덮어쓰기 없는 원자적 공개를 쓴다는 보고다. check-profile 중복 검사·semantic Handoff 생성 감소와 schema 생성기 연결 뒤는 말줄임됐다. [같은 TS의 발췌](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792374703165579).
- **#58**: Memory/File repository의 저장 실패 뒤 재저장 불가·저장 성공 직후 조회 실패 문제를 수정했다고 설명한다. 고유 staging에 기록해 read_handoff로 깊이·용량·해시를 확인하고 영수증/manifest fsync 후 완성 디렉터리를 원자적으로 공개, 실패 staging만 정리, 동시 동일 내용은 기존 완료 기록 반환/다른 내용은 충돌 거부, 상대 root의 생성 시 절대 경로 고정을 보고한다. Memory adapter는 검증 모델의 깊은 복사를 설명하지만 뒤는 잘렸다. [발췌](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792375033387919).
- **#59**: 중단된 실행이 NOT_RUN/IN_PROGRESS로 남거나 실행 뒤 변경된 producer 파일이 결과에 섞이는 문제를 수정했다고 설명한다. 단계별 RUNNING/FAILED/INTERRUPTED·실패 단계·할당 run ID와 C error_code/failed_phase를 기록하고, 요약 쓰기 실패가 원래 오류를 덮지 않도록 한다는 보고다. 최종 bundle을 C가 읽은 plan-bundle에서 가져와 실행 전후 해시 검사, 상위 폴더명이 private인 경우와 실제 private 산출물의 제외를 구분한다. 독립 검증의 타입 검사 대상 모듈 이동 뒤 문장은 잘렸다. [발췌](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792375492116969).
- **#57**: n8n-claw Memory Delete 고정 원문 7개 버전과 공개 저자 테스트를 참조하는 제한된 도구 JS 관측 자료다. 예상 밖 결과를 assertion으로 버리거나 원본 try/catch가 장치 오류를 숨기던 문제의 수정, actual deleted와 expected_deleted 분리, 불일치·호출 실패·장치 위반 기록, 검사 전 모든 HTTP/문맥 시도 기록을 보고한다. 수신부 필터·select/Prefer 적용과 미지원 요청의 상태 미변경, 거절 이유의 정규화 코드/원문 해시, raw 반환/로그의 로컬 var 보존을 설명하며 호출 자... 뒤는 잘렸다. **실제 전체 에이전트 보안 검증이 아니다.** [발췌](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792374709192919).
- 기존 **docs #47** 발췌 끝이 10/24 실행 안내를 포함하도록 바뀌었다. 사용자 제공 PDF 안내의 앞부분은 같고 새 PR 생성·main 병합은 아니다. [같은 메시지](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792512258866809).

과거 B #45 병합·#67 closed/#68 opened, A 분석·ID/경로 경계, 의존성·정상 주문·문서 알림은 이전 요약과 분류를 유지한다.

## 할 일

네 PR의 실제 검토·검사·후속 병합과 consumer 호환은 별도 확인 대상이다. 새 담당·기한·완료율을 만들지 않는다.

## 미해결 질문

말줄임 뒤 상세·실제 코드/테스트·외부 PR 전체·실험 결과는 이번 예약에서 검증하지 않았다. 작성자의 “수정”을 독립 재현·리뷰 승인·main 반영으로 바꾸지 않는다. 이전 #56→58→59 스택 순서의 현재 base/병합 여부도 발췌만으로 재확정하지 않는다.

## 참고 링크

[고정 입력·pipeline 후속](../../../proposals/slack/2026-10-19-고정profile과-입력저장-파이프라인-구현보고.md), [재현 자료 목록](../../../research/slack/2026-10-19_2026-10-20-기억삭제사례와-A발표자료-공유목록.md), [문서 운영 기록](../../../meetings/slack/2026-10-17-피드백-공유요청과-문서알림.md). Slack URL 확인일 **2026-10-25 KST**. 링크·코드는 자료로만 취급했다.
