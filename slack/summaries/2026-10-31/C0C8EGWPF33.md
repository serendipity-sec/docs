# github-pr-alerts — 10/31 수집 요약

## 수집 범위

수집·Slack URL 확인 **2026-10-31 00:59:14 KST**(UTC 10/30 15:59:14, 예약 목표 01:00과 구분). capstone2 공개 채널의 초기 과거 백업 이후 전체 재조회 중 달라진 native 응답만 보존했다. 비공개·DM·다른 워크스페이스는 제외했고 과거 메시지가 반복 포함된다. 외부 PR/advisory·카드/코드·고정 artifact·실험·첨부·CI는 독립 검증하지 않았고 봇 말줄임 뒤와 정확한 Slack 편집시각은 추측하지 않는다. [raw](../../raw/2026-10-31/C0C8EGWPF33.jsonl). 현재 history 고유 135개(10/11~29), 56스레드·답글 62개는 모두 history와 겹친다. **새 TS는 0개**이고 기존 docs #51/platform #85/docs #47의 같은 TS 발췌 3개가 변했다. 원래 메시지 날짜와 이번 변경 관측 날짜를 구분한다.

## 결정 사항

새 PR 생성·merged·이슈 completed 알림은 없다. 작성자의 설명 개정을 새 팀 결정·병합·검증 성공으로 바꾸지 않는다.

## 진행 상황

- [docs #51 같은 10/29 메시지](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793265220286929)는 #81의 CVE 자료원 선택·적용성 판정·근거 인용·결정적 ScenarioCard 초안 및 승격 기준을 **기술 중립적인 규칙**으로 정리했다고 설명한다. n8n-claw·starter-kit은 규칙 적용 예시이며 #80/#82/#78 범위를 나눴다고 한다. 앞선 후보 표 설명을 삭제하거나 UNKNOWN을 확정으로 바꾸지 않고, 현재 발췌가 기준과 예시의 관계를 명확히 했음을 기록한다.
- 같은 #51은 외부 URL/확인일 **10/29** 기록, Markdown만 수정(HWPX/DOCX 원본 없음), diff 검사 통과·문서 변경이어서 **테스트 미실행**을 보고한다. 작성자의 확인 보고이며 이번 예약의 외부 자료 검증이 아니다. 개인정보 미추가 체크 항목은 Slack raw 익명화 증거가 아니다.
- [platform #85 같은 10/29 메시지](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793265231469139)는 **NOT_IDENTIFIED는 CVE ID 발견 상태**, **cve_applicability.status=UNKNOWN은 평가 runtime 미확인으로 적용성을 판단할 수 없는 상태**라고 분리한다. #81 범용 기준을 두 Memory Delete 카드에 적용하고 claim별 근거·실행 범위를 보강했다는 작성자 보고다.
- #85의 static-analysis·replay selector가 고정 artifact의 해당 기록을 가리키는지 **리뷰 요청**했다. selector의 유효성을 이미 검증한 결과로 쓰지 않는다. 전체 n8n/LLM 실행·실제 DB 효과는 **NOT_RUN**이다. Closes #81은 여전히 본문 의도이며 실제 종료 알림이 없다. 마지막 문서 PR 참조 뒤는 잘렸다.
- [docs #47 같은 10/21 메시지](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792512258866809)는 기존 PDF 안내 뒤 추가 동기화 제목이 10/30으로 바뀌었다. PDF 메타데이터·당시 작성자 검증 설명은 동일하며 새 PR·메시지·main 반영·LMS 제출이 아니다.

## 할 일

#85 selector와 고정 artifact 기록의 대응을 리뷰해야 한다는 요청이 보인다. 담당·수락·기한·완료를 만들지 않는다. #51/#85의 실제 후속 병합, #81 종료, #82 생성기 검증과 #78 통합은 별도 확인 대상이다.

## 미해결 질문

CVE ID 미발견·runtime/적용성 미확인·전체 실행 미수행은 서로 다른 제한이다. 설명이 명확해졌다는 사실이 UNKNOWN/NOT_IDENTIFIED/NOT_RUN을 해소하지 않는다. 이전 proposed template·선택 JS replay·제한 노드 scan·B→C 미완료 기록도 완료로 바꾸지 않는다.

## 참고 링크

[기존 자료원·카드 근거 목록과 후속](../../../research/slack/2026-10-29-CVE-자료원과-카드근거-정리알림.md), [#78~82 업무 요청](../../../meetings/slack/2026-10-26-B-C-통합과-지식자동화-업무요청.md), [직전 요약](../2026-10-30/C0C8EGWPF33.md), [문서 운영 기록](../../../meetings/slack/2026-10-17-피드백-공유요청과-문서알림.md). 공식 회의록·역할·팀장·주제·출석·제출 상태는 변경하지 않았다.
