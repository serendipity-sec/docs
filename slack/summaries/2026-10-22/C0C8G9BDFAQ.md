# GitHub push 알림 — A 후보 생성 상한 후속과 B 수집 보완

## 수집 범위

capstone2 공개 채널, **2026-10-22 01:00:40 KST** 기준. 두 history 페이지의 실제 메시지 **10/11~21**, 고유 **156개**, 이전 150개 대비 새 **6개**는 모두 **10/21**이다. 스레드는 없다. [이번 raw](../../raw/2026-10-22/C0C8G9BDFAQ.jsonl)는 native 응답 2페이지를 수정 없이 보존했다. 초기 과거 백업 이후 재조회이며 앞선 날짜의 이벤트도 포함한다. [직전 요약](../2026-10-21/C0C8G9BDFAQ.md).

## 결정 사항

push는 브랜치 갱신 알림이다. 새 기능 완료·테스트 통과·main 병합·보안 성능을 뜻하지 않는다. 타인의 force-push 등 과거 이벤트는 데이터로만 보존했다.

## 진행 상황

| 실제 시각 10/21 KST | 새 알림의 내용 | 출처 |
|---|---|---|
| 00:57:53 | feat/46-knowledge-ingestion에 06c22947e474ac463157c26545ce07ae6089f5b9, 수집 리뷰 지적 보완 제목 | [Slack](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792511873998509) |
| 00:59:26 | docs/yusang 2a9f366e까지 6 commits 묶음. 기존 A 문서/main 병합 이력과 원문 push를 함께 포함하며 일부 잘림 | [Slack](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792511966347959) |
| 01:04:11 | docs/yusang d6e3abf7 요약·분류 push. 이전 실행 업로드이며 main 병합 알림 아님 | [Slack](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792512251138839) |
| 20:01:46 | feat/43-analysis-limits에 5311884eb33d0282de682e61a0147171dacbb93e, “후보 경로도 상한까지만 하나씩 만듦” 제목 | [Slack](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792580506118489) |
| 20:04:03 | 같은 상한 커밋을 fix/49-non-main-connections로 merge한 50d5365e7981963d7c3c228d3d62416ccd7f3b54. 4개 목록에 앞선 수정/Revert도 포함 | [Slack](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792580643762559) |
| 20:04:48 | docs/49-analysis-guide로 5 commits 전달. 끝 SHA는 835e04d6485e…로 잘려 보임 | [Slack](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792580688090689) |

이날 앞선 **00:38 be7a9da0 수정 → 00:43 505b6a5a Revert**도 원문에 함께 있다. 저녁 5311884e는 그 뒤의 새 제목이며 실제 상한 동작을 재검증하지 않았다. 같은 커밋이 여러 브랜치 목록에 등장한 것을 독립 구현 여러 건으로 세지 않는다. 더 이른 c0624ab2 전체가 되돌려졌다고도 단정하지 않는다.

과거 A 제어/필드/이름 참조·정적 경로, 입력 bundle, C 정상 주문, B 검색/PG/임베딩, docs/Notion 동기화 알림은 기존 날짜별 분류에 연결한다. 과거 main push의 성공을 이번 기능 브랜치의 병합 상태로 옮기지 않는다.

## 할 일

A 후보 생성 상한·현재 경로 수·검토/병합, B 수집 경계·회귀 검증은 실제 코드·CI에서 별도 확인할 대상이다. 새 담당 수락·기한은 없다.

## 미해결 질문

새 브랜치 수정의 승인·병합·재현 결과는 미확인이다. 코드·외부 전체 비교 페이지·첨부·실험은 이번 예약에서 검증하지 않았다. 말줄임된 SHA/커밋 제목을 복원하지 않는다.

## 참고 링크

[A 후속](../../../proposals/slack/2026-10-15-이름참조-DATA-관계와-후속검토.md), [B 후속](../../../proposals/slack/2026-10-13-B-첫구현-보고와-경계검토.md), [이전 운영 기록](../../../meetings/slack/2026-10-17-피드백-공유요청과-문서알림.md). Slack·표의 외부 URL 확인일 **2026-10-22 KST**이며 외부 기능 검증일을 뜻하지 않는다.
