# github-pr-alerts — 11/05 수집 요약

## 수집 범위

수집·Slack URL 확인 **2026-11-05 01:02:36 KST**(UTC 11/04 16:02:36, 예약 목표 01:00과 구분). capstone2 공개 채널의 초기 과거 백업 이후 전체 재조회 중 변경 native 응답을 보존했다. 비공개·DM·다른 워크스페이스는 제외했다. 봇 말줄임 뒤·정확한 편집시각·첨부 본문·외부 전체 코드/PR·실험/CI는 독립 검증하지 않았다. [raw](../../raw/2026-11-05/C0C8EGWPF33.jsonl). history 고유141개(10/11~11/04), 60개 스레드 답글66개 모두 history와 중복. 새 TS 6개와 기존 TS 발췌 변화5개다.

## 결정 사항

실제 11/04의 병합 알림: [06:59 #85](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793743142210769), [07:01 docs #51](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793743266301909), [07:16 #73](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793744192318169), [07:28 #83](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793744929837139). 원격 반영 알림이며 실험·운영 배포 성공과 구분한다.

## 진행 상황

- [#83 기존 TS](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793015909534969)의 개정 설명은 plan/catalog/handoff·obligation을 검증하고 같은 규칙 bytes로 전후를 검사한다고 한다. **규칙0.6.0은 인증된 요청자/역할 출처가 없는 계약에서 임의 노드 출력·모델 fallback·admin 변수명·owner 비교로 경고를 억제하지 않는다**고 보고한다. 모델 입력이 고정 DELETE/PATCH/PUT URL에 도달하면 권한 검토 WARNING을 남기며 정상 guard도 경고할 수 있고 첫 보완 전후 안전성을 구분하지 못한다는 한계를 보존한다. 코드·경고 정확성은 재검증하지 않았다.
- [#73 기존 TS](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792981841874599)는 같은 ID 저장도 기존 payload SHA-256·문서 형식·analysis ID를 검증하고 다른 유효 바이트는 ANALYSIS_ID_CONFLICT로 거부한다고 보고한다. 기존 행 미덮어쓰기·공용 case/snapshot 외래키 후속 범위를 구분한다.
- [#59 기존 TS](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792375492116969)는 events.json의 run_id/collection_status와 FINISHED/종료 시각을 검증하고 해시를 다시 맞춰도 다른 run·미완료 수집·종료 전 기록을 NORMAL_BUSINESS_CHECK_FAILED로 거부한다는 설명이다. 추가 반례6개를 수정 전 실패/수정 후 통과했다는 **작성자 보고**이며 독립 실행 검증은 아니다.
- [11:52 새 #86](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793760731171109)은 정적 결과 PG 저장/조회·해시 대조·CLI·SUMMARY.md 생성 보고다. [12:13 새 docs #58](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793762002453209)은 오라클4유형·관찰 지표·위험 확정/위험 없음/근거 부족·환경 기록의 적용 제안이며 **실험 결과가 없고 팀 결정은 체크리스트**라고 명시한다.
- docs #51의 같은TS에 reviewer 표기가 추가됐으나 승인 결과로 쓰지 않는다. docs #47의 같은TS에는 11/04 추가 제목이 보이며 PDF 메타데이터·당시 검증 설명은 동일하다. 정확한 편집시각·말줄임 뒤는 미확인이다.

## 할 일

#86·#58의 실제 검토/병합·공용 운영환경·정적/동적 결과와 독립 판정의 정확성은 별도 확인한다. 새 담당·기한·팀 합의를 추정하지 않는다.

## 미해결 질문

#83의 SUCCEEDED·병합·정적 WARNING은 전체 Agent 보안 판정이 아니다. #86/#58/#59/#47 새 merged 알림은 이 범위에 없다.

## 참고 링크

[C 후속](../../../proposals/slack/2026-10-26-C-정적검사-catalog-제안-알림.md), [결과 저장 제안](../../../proposals/slack/2026-11-04-C-정적결과-저장조회-제안.md), [동적 기준 제안](../../../research/slack/2026-11-04-동적검증-판정기준-제안알림.md), [pipeline/DB 후속](../../../proposals/slack/2026-10-19-고정profile과-입력저장-파이프라인-구현보고.md), [자료 근거](../../../research/slack/2026-10-29-CVE-자료원과-카드근거-정리알림.md).
