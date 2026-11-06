# github-pr-alerts — 11/07 수집 요약

## 수집 범위

수집·Slack URL 확인 **2026-11-07 01:00:48 KST**(UTC 11/06 16:00:48). capstone2 공개 채널의 초기 과거 백업 이후 전체 재조회 중 변경 native 응답을 보존했다. 비공개·DM·다른 워크스페이스는 제외했다. 정확한 Slack 편집시각·봇 말줄임/잘린 표 뒤·첨부 본문·외부 전체 이슈/PR/코드·실제 DB/모델/시험·CI는 독립 검증하지 않았다. [raw](../../raw/2026-11-07/C0C8EGWPF33.jsonl). history 고유160개, 70스레드 실제 답글79개 모두 history와 중복(10/11~11/06). 새 TS6개와 기존 #61/#87 설명 갱신이다. docs #61과 platform #61은 서로 다른 PR이다.

## 결정 사항

11/06 [14:41 platform #84](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793943677437419), [14:45 platform #61](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793943919528149), [16:25 platform #87](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793949912796699) 병합 알림을 이전 미병합 시점과 구분한다. 병합은 선언된 정책의 진실·최종 정책 위반 판정·공용 환경/두 호스트·일반 탐지 성능의 독립 검증이 아니다.

## 진행 상황

- [#84 열림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793943474890699)·[ready](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793943475164319)는 OBJECT_OWNERSHIP에 선택적 bindings.version=1.0.0을 추가하고 rule/side/node/pointer/subject 참조, 반대편에만 있는 node-only 대상과 잘못된 참조를 구분한다고 설명한다. 예외에는 명시적 정책·업무 근거가 필요하다고 한다. **선언 주체/효과/예외의 진위나 정책 위반은 판정하지 않는다**고 명시한다. 일반/정적 계획 공통 검증의 모르는 policy/task ID 거부 뒤는 잘렸다.
- [platform #61 기존 TS](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793861888384109)는 참조 검증을 경로 상한 검사 전에, policy 연결을 분석 내용 ID 계산 전에 수행하고 binding 없는 분석 bytes/ID 유지·반대편 부재 메모 중복 방지를 설명한다. 필드·주체 신뢰·효과·예외·최종 정책 위반은 평가하지 않는다는 한계를 유지한다. 기존 통합 검증이 미연결 상태를 가정해 실패해 공개 analyze→정확한 ID 저장/재조회→B 계획 경로로 검증 도구를 바꿨다는 뒤는 말줄임됐다. 코드/시험 성공은 재실행하지 않았다.
- [#87 기존 TS](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793875823201619)는 검토된 카드/profile 임베딩·분석별 벡터 후보로 고정 snapshot/retrieval/plan 생성, 같은 카드/profile 재색인 재사용·과거 plan의 정확한 ID 원본 bytes 복원을 설명한다. 불변 catalog·1024차원 pgvector/HNSW·배치/응답 상한·충돌/무결성/profile 검사, shared-cards 실패를 keyword fallback으로 숨기지 않는다는 보고다. 최신 main a617a22 통합 뒤 발췌는 잘렸다.
- [docs #61 열림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793924489841279)은 이전 예약의 raw18페이지·요약3개·분류 후속 업로드 알림이다. 이번 제품 구현·오늘 수집 성공이나 main 병합으로 세지 않는다.

## 할 일

병합 뒤에도 #89의 과거 실행 증거/현재 소스 결합 문제, 공용 DB 배치·두 호스트 재현과 새 개인 작업 인계를 별도 확인한다. #87의 영수증 갱신 보고만으로 #89 해결을 표시하지 않는다.

## 미해결 질문

#84의 참조 검증과 #61의 영향 경로 연결은 독립 보안 판정이 아니다. #87 저장/검색과 자료원 수집기·카드 초안 생성/검토/승격은 별도다. 출처에 없는 검증 결과·배정·기한·완료를 만들지 않는다.

## 참고 링크

[입력/pipeline 후속](../../../proposals/slack/2026-10-19-고정profile과-입력저장-파이프라인-구현보고.md), [공용 카드 검색 후속](../../../proposals/slack/2026-11-05-B-공용카드-catalog와-벡터검색-제안.md), [역할/인계 안내](../../../meetings/slack/2026-11-06-4개역할-재분배와-인계대기-공지.md).
