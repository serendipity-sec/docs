# 2026-11-17 github-pr-alerts 요약

## 수집 범위

수집·출처 확인 **2026-11-17 01:02:59 KST**(UTC 11/16 16:02:59). 예약 목표01:00·트리거01:02:27·실제 수집 기준을 구분한다. capstone2 접근 가능 공개8채널의 초기 과거 백업 이후 전체 재조회다. 비공개·DM·다른 워크스페이스는 제외했고 목록 밖3채널의 사본을 유지했다. 같은 decoded 응답은 기존 raw에 보존했다. 실제 요청 인수/원래 도구 응답과 이전 메시지·요약·분류를 대조하고 새 메시지·의미 있는 변경 및 명시한 GitHub PR 본문을 읽었다. 봇 말줄임 뒤·첨부 본문·정확한 Slack 편집시각은 미확인이다. 제품 코드·DB·모델·실험·CI를 이번 수집에서 실행하거나 독립 검증하지 않았으며 PR 본문의 시험/성공 수치는 작성자 보고로 구분한다. history220개/3페이지·91스레드103답글(모두 history 중복), 고유220개다. 새TS4개와 기존PR116/117 발췌2변경을 history3/thread1페이지에 보존했다. [raw](../../raw/2026-11-17/C0C8EGWPF33.jsonl)

이 raw의 실제 메시지 날짜는 **2026-10-11~2026-11-16 KST**이며 수집 날짜와 다르다.

## 결정 사항

새 제품 채택·담당 수락·최종 라벨 확정은 없다. PR116은 개발용 AI 보조 B 검토 패키지v2라고 명시하고 사람의 독립 라벨링·최종 정답·제품 호환성 승인을 미완료로 남긴다.

## 진행 상황

[PR116 기존 TS](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794468920335249)는 원래11/12 메시지이며 이번에는 정책·판정 계약 보완 제목/설명으로 바뀌었다. 전체 PR 본문은 별도 차단 표시, replay 범위, 원본 COMPLETED와 판정 SUCCEEDED의 구분을 설명한다. 고정 연구 정책에서 관리자 삭제를 허용하되 제품 입력에 그 문맥을 전달할 수 없는 호환성 문제를 남긴다. 36슬롯은12개 원본 관측을 직접/동일성 적용한 것으로 독립 표본/실행36개가 아니다. 상위 라벨8/25/3은 유지되고 위반 없음25개가 비관측22·차단3으로 나뉜다는 **작성자 보고**다.

[PR117 기존 TS](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794469578801879)도 원래11/12 메시지다. 반환 없는 타인 조회의 오탐·도구 미호출의 위반 없음·주체/이벤트 연결·다른 실행 자료 혼입 문제의 설명을 갱신했다. 현재 PR 본문은 고정 합성 관측 JSON2개의 회귀 검증을 추가했으며 이번 보완은 새 Docker/n8n 실행이 아니라고 구분한다. PR114/116/117은 모두 OPEN, 각각868e7873/6bdbad9d/921fba90 head이며 main 반영으로 쓰지 않는다.

[09:17:09 platform118](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794788229190149)와 [09:17:58 docs82](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794788278374819)는 Dependabot의 trufflehog3.99.8→3.99.9 제안이다. 둘 다 OPEN이며 release notes의 SECURITY 문구는 봇의 인용이다. 외부 릴리스 원문/도구 기능/우리 저장소의 취약 영향은 별도 검증하지 않았다.

[01:00:41 PR81 생성](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794758441260969)·[01:01:28 병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794758488114909)은 전날 보관 자동화다. GitHub MERGED/head0ee17ee0a01b2d9722f783e1864f1a07e1d4004e/merge4b8818db8055c852e16ecc9917a6e10cb5a89604를 대조했다. 본문의300파일/state140·CI/Notion 설명은 전날 결과이며 오늘 새 검증으로 재사용하지 않는다.

## 할 일

PR116이 연결한 TEAM_DECISIONS는 독립 B 배정·AI 사전 노출·관측 재사용·정책/범위 승인·관리자 지원·A공개/최종 동결을 **팀이 결정해야 할 목록**이다. 파일 이름만으로 결정 완료로 해석하지 않는다. PR117 본문은 팀원 승인 후 병합을 기다리고 원본103/109 정리는 실제 병합 뒤라고 한다. 이 예약은 해당 PR을 승인·병합하거나 원문 명령을 실행하지 않는다.

## 미해결 질문

관리자 허용 정책·선택 JS replay와 제품 어댑터 호환성, 독립 라벨러/블라인드 자격, 실제 서버 인증·전체 workflow·모델/DB 관측은 미완료/범위 밖이다. PR117의 NOT_FOUND는 명시적 거절 BLOCKED와 구분되며 정상 업무 성공·안전의 증명으로 바꾸지 않는다.

## 참고 링크

[platform114](https://github.com/serendipity-sec/platform/pull/114) · [116](https://github.com/serendipity-sec/platform/pull/116) · [117](https://github.com/serendipity-sec/platform/pull/117) · [118](https://github.com/serendipity-sec/platform/pull/118) · [docs82](https://github.com/serendipity-sec/docs/pull/82) · [후보/실행 보고](../../../proposals/slack/2026-11-12-주문소유권-평가fixture와-판정연결-후보.md) · [B검토 자료](../../../research/slack/2026-11-04-동적검증-판정기준-제안알림.md). GitHub 본문/상태·URL 확인일11/17 KST. 외부 기능·시험/성능·제출은 독립 미검증이다.
