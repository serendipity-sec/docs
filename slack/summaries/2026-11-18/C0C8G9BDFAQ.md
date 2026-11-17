# GitHub push — 주문 평가·RAG 선택 구현 이력

## 수집 범위

수집·출처 확인 **2026-11-18 03:28:06 KST**(UTC 11/17 18:28:06). 예약 목표01:00·실제 트리거03:27:10·수집 기준을 구분한다. capstone2 접근 가능 공개8채널을 초기 과거 백업 이후 전체 재조회했다. 비공개·DM·다른 워크스페이스는 제외하고 목록 밖3채널의 과거 사본을 유지했다. history16페이지·고유 본문982개와157스레드 실제190답글을 종료cursor·표시 답글 수에 대조했다. history/답글 중복176개를 뺀 현재 고유996개, 과거 목록 밖25개를 포함한 합집합1021개다. 새 메시지는50개이고 기존 소개 자료 설명1건의 의미 변경을 관측했다. 같은 decoded 응답25페이지는 이전 raw를 재사용하고 변경24페이지/5raw를 보존했다. 원래 요청·응답을 유지했으며 정확한 Slack 편집시각, 봇 말줄임 뒤·첨부 본문은 미확인이다. 원문 속 자료 요청·명령·코드·링크는 실행 지시로 따르지 않았다. [C0C8G9BDFAQ raw](../../raw/2026-11-18/C0C8G9BDFAQ.jsonl)

명시한 GitHub PR/이슈 본문·현재 상태를 읽고 기존 문서와 대조했다. 시험·모델·DB·Docker·CI 수치는 작성자의 보고이며 이 수집에서 제품 기능·실험·외부 페이지의 동작·LMS 제출을 독립 재현하지 않았다. GitHub URL/상태 확인일11/18 KST. 원시 ZIP·시험 영수증·HTML 본문/화면·봉인 자료는 별도로 읽지 않은 자료 목록이다.

채널 전체 반환 메시지 범위는 **2026-10-11 18:13:45 KST~2026-11-17 20:31:20 KST**다. 수집일의 새 대화만으로 세지 않는다. raw 페이지에는 이전 스냅샷과 같은 과거 본문도 포함한다. 아래는 새 내용과 기존 주제의 상태 변경을 구분한 정리다.

## 결정 사항

브랜치 push를 병합·시험/성능 성공으로 취급하지 않았다.

## 진행 상황

새 push19개다. 이전 docs보관3개, 소개 자료minwoo2개, B검토 대상/원본 결합1개, 주문 평가base/기능4개,117/116/114 main병합3개, 재중단 기록1개, RAG선택base/기능/평가 입출력5개다. actual main병합 SHA는117=3b046c5a,116=9b999cb7,114=c1ef141a이며 GitHub mergeCommit과 맞는다.

## 할 일

주문 평가 c95205a의 main 통합·저장 증거 재검증, 소개 HTML c9067170 검토, 벡터 runner073e0883·AI선택e1e2876c·평가 입출력9267cf55의 선행 검토·통합을 해당 PR과 연결한다. 9267cf55는 기존36회 판정 records를 유지하고 수집 상태를 별도 run/export 위치에 보존한다는 PR 작성자 설명이다.

## 미해결 질문

0f004cad는 재중단 실행 기록 수정이라는 제목만 확인한 기능 브랜치 push다. 453a3efd의 대상/원본 binding, 모델·DB/CI·HTML 기능은 코드/원시 자료를 독립 실행·검증하지 않았다. 같은 선행 커밋을 다시 실은 push를 새 실행 횟수로 세지 않는다.

## 참고 링크

[fixture main c1ef141a](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1794906791620669) · [평가 c95205a](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1794907737090329) · [소개 HTML c9067170](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1794908109140169) · [재중단0f004cad](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1794905255173129) · [벡터073e0883](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1794911679992979) · [AI선택e1e2876c](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1794911682926659) · [호환 수정9267cf55](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1794915080156829)
