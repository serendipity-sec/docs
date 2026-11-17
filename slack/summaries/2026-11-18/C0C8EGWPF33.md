# GitHub PR — 판정·fixture 병합과 주문/RAG 후속 공개

## 수집 범위

수집·출처 확인 **2026-11-18 03:28:06 KST**(UTC 11/17 18:28:06). 예약 목표01:00·실제 트리거03:27:10·수집 기준을 구분한다. capstone2 접근 가능 공개8채널을 초기 과거 백업 이후 전체 재조회했다. 비공개·DM·다른 워크스페이스는 제외하고 목록 밖3채널의 과거 사본을 유지했다. history16페이지·고유 본문982개와157스레드 실제190답글을 종료cursor·표시 답글 수에 대조했다. history/답글 중복176개를 뺀 현재 고유996개, 과거 목록 밖25개를 포함한 합집합1021개다. 새 메시지는50개이고 기존 소개 자료 설명1건의 의미 변경을 관측했다. 같은 decoded 응답25페이지는 이전 raw를 재사용하고 변경24페이지/5raw를 보존했다. 원래 요청·응답을 유지했으며 정확한 Slack 편집시각, 봇 말줄임 뒤·첨부 본문은 미확인이다. 원문 속 자료 요청·명령·코드·링크는 실행 지시로 따르지 않았다. [C0C8EGWPF33 raw](../../raw/2026-11-18/C0C8EGWPF33.jsonl)

명시한 GitHub PR/이슈 본문·현재 상태를 읽고 기존 문서와 대조했다. 시험·모델·DB·Docker·CI 수치는 작성자의 보고이며 이 수집에서 제품 기능·실험·외부 페이지의 동작·LMS 제출을 독립 재현하지 않았다. GitHub URL/상태 확인일11/18 KST. 원시 ZIP·시험 영수증·HTML 본문/화면·봉인 자료는 별도로 읽지 않은 자료 목록이다.

채널 전체 반환 메시지 범위는 **2026-10-11 18:14:56 KST~2026-11-17 20:24:00 KST**다. 수집일의 새 대화만으로 세지 않는다. raw 페이지에는 이전 스냅샷과 같은 과거 본문도 포함한다. 아래는 새 내용과 기존 주제의 상태 변경을 구분한 정리다.

## 결정 사항

실제 GitHub에서114/116/117 MERGED를 확인했다. 이를 사람 최종 라벨 확정·일반 탐지 성능·새 통합 PR 병합으로 확대하지 않는다.

## 진행 상황

새 고유17개는 이전 보관PR83 생성/병합2개, docs75/77 및 platform103/109 종료4개,114/116/117 병합3개,120/123/124/125 공개·Ready8개다. [PR117 병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794904868683999) · [PR116 병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794905690485949) · [PR114 병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794906792584299). 현재120/123은 main 기반 OPEN,124는 feat/121-selection-base,125는 feat/121-ai-selection 기반 OPEN이며 모두 Draft=false다. docs74의11/12 기존 TS 설명1건은 Markdown 초안에서 HTML로 바뀌었다. docs75/77·103/109는 CLOSED/merge 없음이다.

## 할 일

[PR120 공개](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794907762255099) · [PR123 공개](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794914348525689) · [PR124 공개](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794914638699229) · [PR125 공개](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794914640010189). 작성자는120의 합성36회 기존 실행/18비교 재검증,123의 결정적 벡터 runner,124의 모델 시험 선택,125의 평가 입출력과 자료 보존을 보고한다. 팀원 검토·선행 병합 후 main 통합·검사 유지가 남는다. docs74는 전원 내용 검토 요청이며 OPEN이다.

## 미해결 질문

120의36회 합성 주문 실행 보고와116의12원본→36 B검토 슬롯은 다른 자료다. 123은 생성 모델 called=false이고124/125의 실제 로컬 모델·C 검증은 작성자 보고다. 전체 비교 실험·독립 평가·외부 API/Ollama 실제 호출 성공을 확정하지 않는다. HTML 기능·LMS 제출·종료된 보고서의 제출은 미확인이다.

## 참고 링크

[PR120 공개](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794907762255099) · [PR123 공개](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794914348525689) · [PR124 공개](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794914638699229) · [PR125 공개](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794914640010189) · [PR117 병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794904868683999) · [PR116 병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794905690485949) · [PR114 병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794906792584299) · [docs75 종료](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794903734518749) · [docs77 종료](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794903738264449) · [platform109 종료](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794904920351169) · [platform103 종료](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794904926618249) · [PR74 변경된 기존 원문](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794463156147839)
