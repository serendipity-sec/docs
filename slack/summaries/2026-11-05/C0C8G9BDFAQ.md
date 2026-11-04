# github-push-alerts — 11/05 수집 요약

## 수집 범위

수집·Slack URL 확인 **2026-11-05 01:02:36 KST**(UTC 11/04 16:02:36, 예약 목표 01:00과 구분). capstone2 공개 채널의 초기 과거 백업 이후 전체 재조회 중 변경 native 응답을 보존했다. 비공개·DM·다른 워크스페이스는 제외했다. 봇 말줄임 뒤·정확한 편집시각·첨부 본문·외부 전체 코드/PR·실험/CI는 독립 검증하지 않았다. [raw](../../raw/2026-11-05/C0C8G9BDFAQ.jsonl). 전체3페이지·고유269개(10/11~11/04), 스레드 없음. 새TS15개는 실제11/04다.

## 결정 사항

main push 알림은 [platform 86a57e4f/#85](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793743140994379), [docs 83fe4956/#51](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793743265017199), [platform 54445d1d/#73](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793744191476609), [platform f6e2aedb/#83](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793744928549689)다. 병합 반영 관측이며 전체 기능·성능·운영 배포 검증이 아니다.

## 진행 상황

- docs/docs/81-knowledge-evidence [1fd804d0](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793743192687949)는 역사적 scan evidence URL 고정 제목이다. docs main5커밋에는 기존4개와 merge가 함께 있어 새 기능5개로 세지 않는다.
- [analysis-database 9개](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793744053549289), [static-adapter 5개](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793744766309059), [pipeline-runner 20개](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793745149936929)는 이전 main/브랜치 이력과 merge가 겹친 잘린 묶음이다. 합계34개 신규 구현으로 더하거나 말줄임을 복원하지 않는다.
- result-repo의 [a85f14b2](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793756638453929)·[28a8e470](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793757911552469)·[8a91be0a](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793759817064579)·[7c625c37](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793760193821869)는 PG 저장/조회·CLI·요약·저장 전 확인 제목이다. 실제 기능/DB/해시·회귀는 독립 검증하지 않았다.
- docs/junseo [781d98db](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793761994967199)는 동적 판정 기준 적용 제안 제목이다.
- [7841f3c2](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793722543830269)·[d89ed534](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1793722693848179)는 이전 예약 yusang 업로드로 새 제품 기능·이번 수집·main 반영이 아니다.

## 할 일

병합 범위 이후의 실제 통합·운영 서비스·독립 보안 판정과 미병합 제안은 별도 확인한다. 새 담당·기한·완료를 만들지 않는다.

## 미해결 질문

#83의 보수적 WARNING 한계·#86 저장 계약·#58 실험 미수행·#59 추가 반례 보고를 전체 성공으로 합치지 않는다.

## 참고 링크

[PR 요약](C0C8EGWPF33.md), [카드/자료 근거](../../../research/slack/2026-10-29-CVE-자료원과-카드근거-정리알림.md), [결과 저장 제안](../../../proposals/slack/2026-11-04-C-정적결과-저장조회-제안.md), [동적 판정 기준](../../../research/slack/2026-11-04-동적검증-판정기준-제안알림.md).
