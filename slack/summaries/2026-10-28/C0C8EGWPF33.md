# github-pr-alerts — 10/28 수집 요약

## 수집 범위

수집·Slack URL 확인 **2026-10-28 01:24:48 KST**. capstone2 공개 채널의 초기 과거 백업 이후 전체 재조회 중 변경된 native 응답을 [raw](../../raw/2026-10-28/C0C8EGWPF33.jsonl)에 보존했다. 실제 새 메시지는 **10/27**이다. DM·비공개·다른 워크스페이스는 제외했다. 첨부 본문·외부 전체 PR/코드·기능·CI는 독립 검증하지 않았고 말줄임 뒤를 추정하지 않는다.

history 페이지 경계의 같은 TS를 제거한 고유 131개다. 스레드 54개의 답글 60개는 모두 history와 겹친다. 새 TS 1개이며 과거 10/11~27 내용을 포함한다.

## 결정 사항

새 병합 알림은 없다.

## 진행 상황

[10/27 02:00 docs PR #50 열림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793034058854689)은 plans/database-schema.sql·.md를 함께 보강했다는 작성자 설명이다. 기존 24개 테이블·UUID 내부 키·파일 artifact/PG metadata 구조는 유지한다.

INPUT bundle 유형, A 전후 방향, artifact 해시 일치를 복합 FK로 보장하고 analysis/retrieval/plan/comparison/run의 외부 ID 유일성·멱등/충돌 규칙, attempt 상한·유한 score·semantic hash NULL 조건·JSON 형태 제약을 추가했다고 한다. 미래 result_checks의 case/comparison_run/obligation/evaluator 연결 뒤는 잘려 복원하지 않았다.

## 할 일

실제 SQL·기능·통합 검증과 리뷰/병합은 별도 확인 사항이다. 새 담당·기한은 없다.

## 미해결 질문

Closes #49는 설명 표기이며 실제 이슈 종료가 아니다. #40 참조와 #31 공유 서비스 결정 범위를 유지한다. 이 수집에 #50 merged는 없으며 공용 DB 운영·최종 판정 구현 완료도 미확인이다.

## 참고 링크

[보강안](../../../proposals/slack/2026-10-27-DB-스키마-무결성-보강안.md), [docs #50](https://github.com/serendipity-sec/docs/pull/50), [기존 DB 안내](../../../plans/database-schema.md).
