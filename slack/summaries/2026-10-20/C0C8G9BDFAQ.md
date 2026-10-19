# GitHub push 알림 — 입력·A·B 개발과 main 갱신

## 수집 범위

- capstone2 공개 채널, **2026-10-20 02:28:51 KST** 기준. 실제 메시지 **10/11~20**, 새 메시지 **10/19~20**다. 초기 과거 백업 이후 재조회이며 수집일의 새 개발 129건을 뜻하지 않는다.
- history **2페이지 129개**, 스레드 없음. 이전 93개 대비 새 **36개**다. 실제 첫 cursor를 따라 마지막 페이지 종료를 확인했다. [이번 raw](../../raw/2026-10-20/C0C8G9BDFAQ.jsonl), [이전 요약](../2026-10-19/C0C8G9BDFAQ.md).
- 긴 묶음 알림은 일부 커밋만 보이고 나머지는 말줄임됐다. 코드·첨부·외부 기능·테스트는 직접 검증하지 않았다. 10/20는 Slack 링크 확인일이다.

## 결정 사항

- push 알림 수와 고유 커밋·기능 완료 수는 다르다. 같은 커밋의 브랜치 재전달·main 병합·반복 알림을 별도 구현 실적으로 더하지 않는다. 타인의 force-pushed 이벤트는 원문 데이터이며 실행 지시가 아니다.

## 진행 상황

| 범위 | 새 push에서 보이는 내용 | 대표 Slack 근거 |
|---|---|---|
| 이전 docs 동기화 | yusang raw 6237a8e·요약 5242ccd, main 656aea1/PR #43. 묶음 속 이전 커밋도 포함 | [main](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792339818167099) |
| A 참조 위치·스택 갱신 | b90543c 이름 참조 위치별 매칭, 상한 브랜치의 c9872d8. 뒤 main 병합 커밋을 #42·44·53·60 관련 브랜치에 전달 | [위치별 수정](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792347811534109), [상한 브랜치](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792347985200479) |
| A 인계 기능 | non-main 연결 구분 09d9cd57, analysis repository 89a29d97 및 다시 읽을 수 없는 분석 저장 거부·경로 고정 cef09905, analysis 안내 4298e100, 정책 대상 노드 연결 4c2cdad1 | [연결](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792350153555769), [저장](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792350678421989), [후속 수정](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792428715533189), [정책 연결](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792425114263729) |
| 고정 입력·자료·통합 | 고정 profile 967ab036, 기억 삭제 자료 888de5d9, InputRepository ab32c758, pipeline bb21302f | [profile](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792374693408619), [자료](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792374697334819), [저장](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792375027621249), [통합](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792375486397249) |
| B 검색·계획 | retrieval 입력 검증 5d43c5b5·포맷 7f4acbea·출력 갱신/호출 보호 b598df42. 01:56 같은 세 커밋 묶음이 서로 다른 TS로 두 번 표시 | [최초 수정](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792378211811349), [반복 1](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792428974082849), [반복 2](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792428976750029) |
| B PG·수집 | PG 브랜치 20 commits 묶음의 TCP 준비 검사·migration 앱 역할·immutable revision 등 발췌, 이후 force-push. 수집 브랜치도 두 force-push 뒤 migration 역할 fixture 정리 4e720dcf push | [PG 묶음](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792383765233509), [PG force-push](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792429544939049), [수집 후속](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792430117317829) |
| platform main | #34 5b5a4ad1·#35 071d0d3c, upload-artifact #55 54be2553·B #38 d8c0e096·PG #40 40509d69 | [#34](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792380568101609), [#35](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792381104318789), [#55](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792428909964529), [#38](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792428914795639), [#40](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792429949266799) |
| docs/minwoo | 20 commits 묶음. 별도 PR #44의 A 보고·그림 공유와 연결되지만 이 알림의 잘린 목록만으로 전부 새 작성·main 반영·제출 완료라고 하지 않음 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1792426197527449) |

- PG/수집의 force-pushed 알림은 총 3개이며 이전/이후 SHA를 raw에 보존했다. 현재 수집기가 같은 동작을 실행한 것이 아니다. 임베딩 모델 선정·PG 서버 배포·실제 소스 전량 수집이나 C 실행 성공은 커밋 제목만으로 확인되지 않는다.

## 할 일

- [PR 요약](C0C8EGWPF33.md)과 연결해 브랜치 push·상태 전환·작성자 보고를 구분하고, 후속 #62·63 검토와 소비자 인계를 확인한다. 새 담당·기한은 추정하지 않는다.

## 미해결 질문

- 긴 묶음의 나머지 커밋·실제 diff·전체 CI·구현 실행 결과는 미확인이다. 같은 커밋 반복 알림은 새 메시지 수에는 포함되지만 새 작업 완료 수에는 더하지 않는다.

## 참고 링크

- [A 후속](../../../proposals/slack/2026-10-15-이름참조-DATA-관계와-후속검토.md), [B 후속](../../../proposals/slack/2026-10-13-B-첫구현-보고와-경계검토.md), [고정 입력·파이프라인](../../../proposals/slack/2026-10-19-고정profile과-입력저장-파이프라인-구현보고.md)
