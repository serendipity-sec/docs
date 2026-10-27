# github-pr-alerts — 10/27 수집 요약

## 수집 범위

수집 **2026-10-27 01:00:47 KST**. capstone2 공개 #github-pr-alerts의 전체 기록·스레드 재조회 중 바뀐 응답을 [raw](../../raw/2026-10-27/C0C8EGWPF33.jsonl)에 보존했다. 초기 과거 백업과 중복 메시지를 포함하며 실제 신규 메시지 날짜는 **10/26**다. 비공개·DM·다른 워크스페이스는 제외했다. 첨부·외부 전체 페이지·코드·실험·CI는 미검증이다.

현재 history/고유 130개, 스레드 54개·답글 60개는 모두 history와 겹친다. 새 TS 22개는 opened 9·merged 13이며 기존 TS의 발췌 변화와 구분했다. 과거 원문 범위는 10/11~26이다.

## 결정 사항

원격 봇 병합 알림: docs [#40 DB 안내](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792947911761289)·[#48 TruffleHog](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792982296057769); platform [#44 분석 상한](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792981839921779)·[#53 비-main 연결 구분](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792981904154149)·[#60 분석 안내](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792981982307489)·[#47 수집 기반](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792982180770849)·[#71 setup-python](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792982229261829)·[#70 TruffleHog](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792982234508439)·[#56 고정 profile](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792983007981819)·[#57 기억 삭제 근거](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792983012950219)·[#77 시각 없는 retry](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792996401528779)·[#76 근거 카드](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792996527823199)·[#72 B 산출물](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792996936538899). platform 11개와 docs 2개로 **13개**다. 병합을 테스트 성공으로 해석하지 않는다.

## 진행 상황

[#69](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792948267983429)는 공개 정적 도구 4개가 두 버전을 구분하지 못했다는 작성자 보고와 사례 전용 임시 Semgrep catalog 제안이다. [#72](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792975645382409)는 A impact_paths·출처/한계를 retrieval/plan에 보존하고 B 원본 bytes를 PG 트랜잭션에 저장·정확한 plan_id로 복원한다는 설명이며 뒤 병합 알림이 있다. [#73](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792981841874599)은 A의 공용 PostgreSQL adapter와 graph_0001·전용 버전 표를 설명하는 PR 열림이다. 이 범위에 #73 병합 알림은 없다.

[#76](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792992540121399)은 source revision·SHA·관측·적용 조건의 팀 작성 카드이며 임시 catalog stub 검색만 확인했다는 제한이다. [#77](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792995308198679)은 시각 없는 복수 격리본의 순서를 추정하지 않고 KNOWLEDGE_SOURCE_REVISION_ORDER_UNKNOWN으로 유지한다는 수정 설명이다. [#83](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793015909534969)은 등록 정적 adapter 제안으로 plan/catalog/handoff·해시를 확인하고 before/after 기록·도구 오류 상태를 구분한다는 설명이다. #69 선행 변경을 포함할 수 있으며 아직 병합 알림이 없다.

## 할 일

#69/#73/#83 검토와 실제 B→C 연결·공용 환경은 별도 확인 사항이다. 새 담당·기한을 만들지 않는다.

## 미해결 질문

기존 [#59 TS](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792375492116969)는 입력 저장/조회, 실제 C plan-bundle 바이트와 해시, manifest·run·관측 해시 후 독립 주문 검증을 설명하도록 바뀌었다. 정확한 편집시각과 뒤 잘린 내용은 미제공이다. 기존 docs #47의 실행 날짜 발췌 변화도 새 PR·main 병합이 아니다. 저자 테스트·동적 Agent 보안·최종 판정을 독립 검증하지 않았다.

## 참고 링크

[C 제안](../../../proposals/slack/2026-10-26-C-정적검사-catalog-제안-알림.md), [B](../../../proposals/slack/2026-10-13-B-첫구현-보고와-경계검토.md), [A](../../../proposals/slack/2026-10-15-이름참조-DATA-관계와-후속검토.md), [profile/pipeline](../../../proposals/slack/2026-10-19-고정profile과-입력저장-파이프라인-구현보고.md), [자료 목록](../../../research/slack/2026-10-19_2026-10-20-기억삭제사례와-A발표자료-공유목록.md).
