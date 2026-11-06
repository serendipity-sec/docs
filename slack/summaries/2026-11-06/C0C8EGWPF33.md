# github-pr-alerts — 11/06 수집 요약

## 수집 범위

수집·Slack URL 확인 **2026-11-06 09:09:04 KST**(UTC 00:09:04). 예약 목표 01:00과 실제 실행을 구분한다. capstone2 공개 채널 전체 재조회이며 초기 과거 백업·겹치는 스냅샷을 포함한다. 비공개·DM·다른 워크스페이스는 제외했다. 봇의 말줄임·잘린 표·첨부 본문·외부 전체 코드/PR·실제 DB/실험·CI는 독립 검증하지 않았다. 기존 TS 설명 변화의 정확한 Slack 편집시각은 미제공이다. [raw](../../raw/2026-11-06/C0C8EGWPF33.jsonl). history 고유154개(페이지 경계의 중복 TS 제외), 69스레드 실제 답글75개 모두 history와 겹친다(10/11~11/05). 새 TS13개다. 기존 #86 설명이 바뀌었고 #58/#59/#47의 URL·발췌 길이 변화는 별도 보존한다.

## 결정 사항

실제 11/05 병합 알림: [docs #58 14:23](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793856187672069), [docs #47 15:21](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793859710730089), [platform #58 15:32](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793860335585209), [platform #59 15:37](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793860664855129), [docs #59 15:47](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793861262374029), [platform #86 17:46](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793868373927549), [platform #88 18:00](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793869224377539). 기존 미병합 시점과 구분하며, 병합을 실제 공용 환경·성능/보안 판정·CI 성공으로 바꾸지 않는다.

## 진행 상황

- [새 #88](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793859255751459)은 B가 C의 등록 StaticScanCatalog로 계획을 만들고 C가 수정 없이 소비해 before/after를 plan_id로 연결한다고 설명한다. support·그래프/변경 참조·같은 side target을 확인하고 설명용 limitations를 선택 결과/전체 analysis_context에 보존한다. PARTIAL/UNKNOWN·대상 불일치·누락/모호함·TRUNCATED를 구분한다는 뒤는 잘렸다. #78의 이전 점검 상태와 이후 병합을 함께 기록한다.
- [#86 기존 TS](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793760731171109)는 다른 계획·실행 결과 혼합과 원시 보고서 변경 거부, 같은 제한 크기 파일 핸들로 읽기/해시 대조, 조회 payload plan ID 대조, 기존 요약 미덮어쓰기·before/after 쌍 요구를 새로 설명한다. DB/코드/실행은 독립 검증하지 않았다.
- [docs #59 열림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793859827795339)은 지도교수 면담의 일정·점수화/신뢰성·서비스 방향·출품 논의 기록 알림이다. 원격에서 받아 읽은 [기존 회의록](../../../meetings/2026-11-05-01-회의록.md)을 연결하며 익명 참석자 1~5를 실명에 대응시키지 않는다. 해당 문서의 계획·교수 제안과 구현·제출 완료를 구분한다.
- [새 platform #61](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793861888384109)과 [ready](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793861888714879)는 #84 위에 쌓은 정책 binding을 A analyze() 영향 경로에 연결하는 제안이다. #58→#59→이후 순서 설명은 말줄임돼 전체를 추정하지 않는다. 이 범위에 #61/#84 병합 알림은 없다.
- [새 #87 알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793875823201619)과 [ready](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793875823446269)는 공용 PG 카드 catalog·profile별 임베딩 색인, 같은 카드/profile 재임베딩 생략, shared-cards의 query embedding·벡터 검색/계획·B 산출물 저장을 설명한다. 실패 시 keyword로 자동 전환하지 않는다고 한다. Slack 관측은 19:50이고 본문 on 필드는 03:22:01Z를 표시한다. #79의 15:16 Draft 설명과 뒤의 ready를 시간별로 구분한다. 이 범위에 #87 merged는 없다.

## 할 일

#61/#87의 검토·병합, #89가 제기한 고정 실행 예제/현재 src 결합 문제, 실제 두 호스트 공용 DB와 재현 증거는 별도 확인한다. 소스 안의 명령은 이 자동화에서 실행하지 않았다.

## 미해결 질문

docs #58의 [병합된 적용 제안](../../../research/2026-11-04-동적검증-판정기준-FlowDelta적용안.md)은 실험 결과가 없다고 명시한다. 근거 부족을 안전으로 세지 않고 정답 라벨/판정기 자격시험·네트워크/관측 환경·팀 채택을 별도로 정해야 한다. 정상 업무 실행과 독립 보안 판정을 합치지 않는다.

## 참고 링크

[공용 카드/벡터 검색 제안](../../../proposals/slack/2026-11-05-B-공용카드-catalog와-벡터검색-제안.md), [결과 저장 후속](../../../proposals/slack/2026-11-04-C-정적결과-저장조회-제안.md), [입력/pipeline](../../../proposals/slack/2026-10-19-고정profile과-입력저장-파이프라인-구현보고.md), [동적 기준 후속](../../../research/slack/2026-11-04-동적검증-판정기준-제안알림.md).
