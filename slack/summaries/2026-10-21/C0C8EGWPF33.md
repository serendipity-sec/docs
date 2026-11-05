# GitHub PR 알림 — A 경계 병합·사례 재현·ID 후속

## 수집 범위

capstone2 공개 채널, **2026-10-21 00:57:44 KST** 기준. 실제 메시지 **10/11~20**, 새 알림 **10/20**이다. history 99개·스레드 36개의 실제 답글 41개를 끝까지 읽었다. 답글 모두 history와 겹쳐 고유 **99개**, 이전 대비 새 **8개**다. 원래 응답 5페이지를 [이번 raw](../../raw/2026-10-21/C0C8EGWPF33.jsonl)에 보존했다. [이전 요약](../2026-10-20/C0C8EGWPF33.md).

초기 과거 백업 이후 재조회이며 발췌·말줄임을 유지했다. 외부 platform PR 전체·코드·실행/CI·첨부 그림/HTML은 미검증이다. 원격에서 받은 현재 docs의 A 보고 Markdown은 읽었으며 작성자 보고와 독립 검증을 구분한다. URL·로컬 문서 대조일 10/21.

## 결정 사항

PR 작성·병합·작성자 테스트 보고·제출 완료는 서로 다르다. 개인의 CI 관련 질문은 검사 예외에 대한 최종 합의가 아니다.

## 진행 상황

| 범위 | 새 알림의 내용 | Slack 근거 |
|---|---|---|
| docs #45 | 이전 예약 동기화 작성·병합 2개 | [작성](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792431366779279), [병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792431405050919) |
| docs #44 | A 보고 초안·그림 02:57 병합 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792432620381639) |
| platform #42 | 끊긴 이름 참조 영향 경로·표시 변경 제외 05:00 병합 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792440020273599) |
| platform #64 | n8n-claw 두 비교 쌍의 A 분석 재현 절차 작성. 고정 URL·해시·크기의 원본 4개로 var에 case bundle 생성, src 변경 없음. Handoff를 기다리지 말고 #57 자료를 가공해 analysis.json/재현 명령을 B에 인계하라는 #49 요청 참조 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792441230046229) |
| docs #46 | A 보고 10/20 기준 갱신 작성·병합 2개. #64·상한 생성 단계·저장 루트 링크·리뷰 현황과 미지원 사유 정정 설명 | [작성](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792441475190929), [병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792443194826659) |
| platform #65 | 결과가 달라도 같은 analysis_id가 나오는 문제를 결과 내용 해시로 고친다는 작성 설명. snapshot ID+producer만 사용하던 규칙의 충돌 사례를 제시 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792443839627859) |

- #65의 사례는 같은 n8n-claw 기능 추가 쌍을 main(영향 경로 27개)과 상한 포함 A 스택(20개)에서 분석하면 둘 다 `analysis-06277a39151c0499`였다는 **작성자 보고**다. 변경·재현·병합을 직접 검증하지 않았다.
- 같은 TS의 기존 PR #60 설명에는 Closes #63가 추가됐다. 원래 메시지 날짜는 10/19이고 정확한 수정 시각은 미확인이다. 새 PR 생성으로 세지 않는다.
- docs #46 알림은 #42·44 링크를 docs 저장소 URL로 렌더링한다. platform 기능 번호와 docs 번호를 구분하고 원문 링크를 몰래 고치지 않는다. platform #42 병합은 위 별도 알림으로 확인한다.
- 현재 [A 보고](../../../deliverables/w08-중간진행보고/A-그래프분석.md)의 그래프 테스트 99개·저장소 21개·팀 리뷰 결함 6건/리뷰 9건은 문서 작성자의 집계다. support UNKNOWN·미지원 설정/AI 연결·정책 binding·DB adapter의 한계와 리뷰 중 상태를 함께 읽는다. 이번 수집의 실행 결과로 바꾸지 않는다.

## 할 일

정확한 분석 ID와 불변 저장소 연결, #64의 B 소비, workflow 설정/AI 연결의 지원 경계와 상한 표시를 확인한다. 새 담당 수락·완료율·기한은 정하지 않는다.

## 미해결 질문

#64·65의 최종 승인/검사/병합, 실제 B 인계 소비·보안 판정·제출 완료는 미확인이다. 보고서에서 수정했다고 적은 상한도 이후 push·되돌리기 이벤트와 시점을 구분해야 한다.

## 참고 링크

[A 후속](../../../proposals/slack/2026-10-15-이름참조-DATA-관계와-후속검토.md), [자료·보고 목록](../../../research/slack/2026-10-19_2026-10-20-기억삭제사례와-A발표자료-공유목록.md), [운영 질문](../../../meetings/slack/2026-10-20-Actions와-병합기준-질문.md).
