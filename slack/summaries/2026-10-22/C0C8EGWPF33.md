# GitHub PR 알림 — 이전 docs PR과 B 수집 검토 보완 설명

## 수집 범위

capstone2 공개 채널, **2026-10-22 01:00:40 KST** 기준. 실제 메시지 **10/11~21**, 새 메시지 날짜는 **10/21**이다. history 100개·스레드 36개의 실제 답글 41개를 끝까지 읽고 수를 맞췄다. 답글 41개가 history에도 있어 고유 **100개**, 이전 대비 새 **1개**다. [이번 raw](../../raw/2026-10-22/C0C8EGWPF33.jsonl)는 변경된 history 1페이지다. 초기 과거 백업 이후 재조회이며 동일한 답글은 기존 raw에 보존했다. [직전 요약](../2026-10-21/C0C8EGWPF33.md).

## 결정 사항

새 팀 합의·새 platform 병합 알림은 없다. 과거 #34·35·42·38·40 등의 병합 이벤트와 새 수정 보고를 날짜별로 구분한다. 테스트 통과·ready for review·Closes는 독립 검증·병합과 같지 않다.

## 진행 상황

- **10/21 01:04** docs **#47** 열림은 이전 예약의 원문·요약·분류 업로드 알림이다. 이번 실행 성공·새 제품 기능·main 병합 증거로 세지 않는다. [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792512258866809)
- platform **#47**의 **기존 10/18 TS** 설명이 달라졌다. 수집 정지·격리 재처리·동시 실행·cursor 비교·실패 상태를 고쳤다는 작성자 보고, NUL/짝 없는 surrogate 격리와 원본 보존·제한된 재처리, #40 병합 뒤 main 기반이라는 설명을 담는다. 검토 대상으로 record/JSONB 유니코드 경계, sync_failure 원본 보존 migration, retry_quarantined_records()를 명시한다. 마지막 advisory 항목은 잘렸다. [같은 메시지 현재 발췌](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792299513889189). 정확한 편집 시각·구현 성공은 추정하지 않는다.
- 기존 A #64 분석 재현/인계, #65 결과 해시 ID 수정, 입력 #56→58→59 스택, #57 기억 삭제 자료, A/DB/임베딩 보고는 이전 문서에 이어 읽는다. 기본 파이프라인 PREPARE/C NOT_RUN, 그림/자료 목록과 실제 보안 판정의 차이를 유지한다. 과거 docs 링크 #42/#44와 platform 동일 번호를 혼동해 바꾸지 않는다.

## 할 일

B #47의 격리·재처리·동시 실행·cursor 경계와 #66 stale revision 보고의 실제 해결·회귀 검증을 확인할 필요가 있다. 담당·기한·승인을 새로 추정하지 않는다.

## 미해결 질문

docs #47과 platform #47은 다른 저장소의 PR이다. 이 Slack 수집에는 docs #47 병합 알림이 없다. 외부 전체 PR·코드·플랫폼 CI·기능과 말줄임 뒤 본문은 미검증이다. 수정 보고를 실제 소스별 전체 수집 성공으로 확대하지 않는다.

## 참고 링크

[docs #47](https://github.com/serendipity-sec/docs/pull/47), [platform #47](https://github.com/serendipity-sec/platform/pull/47), [B 후속](../../../proposals/slack/2026-10-13-B-첫구현-보고와-경계검토.md), [문서 알림 기록](../../../meetings/slack/2026-10-17-피드백-공유요청과-문서알림.md). 외부 URL은 Slack에서 확인한 링크이며 확인일 **2026-10-22 KST**다.
