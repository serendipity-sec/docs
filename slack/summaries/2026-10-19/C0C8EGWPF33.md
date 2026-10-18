# GitHub PR 알림 — A 경로 상한과 B 저장·임베딩·수집

## 수집 범위

- capstone2 공개 채널, **2026-10-19 00:56:45 KST** 기준. 실제 Slack 날짜 **10/11~10/18**의 과거 재조회다.
- history 73개·스레드 28개의 실제 답글 29개를 모두 확인했다. 답글 29개는 history에도 있어 고유 **73개**, 이전 대비 새 **11개**다. history와 새 스레드 4개의 원래 응답 5페이지를 저장했다.
- [이번 raw](../../raw/2026-10-19/C0C8EGWPF33.jsonl), [이전 요약](../2026-10-18/C0C8EGWPF33.md). 알림 발췌·말줄임을 보존했으며 외부 PR 코드·첨부·플랫폼 테스트를 직접 확인하거나 실행하지 않았다. 10/19는 Slack 확인일이다.

## 결정 사항

- PR 작성·ready for review는 승인·병합·실제 CI 통과와 다르다. 새 platform 알림에 병합 이벤트는 없다.
- #38·40은 10/18에 읽은 opened 형태 알림이지만 원문 내부 생성일은 각각 **10/17 14:29:42Z·14:38:53Z**다. 10/18 신규 생성 PR로 단정하지 않는다. #45의 내부 생성일은 10/18 04:34:14Z다.

## 진행 상황

| PR | 보이는 설명·상태 | Slack 근거 |
|---|---|---|
| docs #42 | 이전 Slack 동기화의 01:16 작성·병합 알림 2개. 새 기능 구현 2건을 뜻하지 않음 | [작성](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792253762958689), [병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792253808407399) |
| platform #42 | 끊긴 참조 before 경로 보존·표시 전용 변경 제외. #35 위 stacked PR, #36 연결 | [02:23](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792257825325329) |
| platform #44 | 노드 100/300·대표 경로 20의 개발 기본 상한과 도달 표시. #42 위 stacked PR, #43 연결 | [02:46](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792259187177229) |
| platform #45 | qwen3-embedding:0.6b용 공급자 중립 계약·제한된 Ollama 어댑터, query/document 규칙, 모델 digest·profile, 응답 검증·L2 정규화, localhost Compose와 smoke 명령. 작성·검토 준비 알림 2개 | [13:40](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792298431613589) |
| platform #47 | 제한된 SourceAdapter 수집과 원본 revision·정규화 JSON·오류 격리·다음 cursor의 단일 PostgreSQL transaction. #40 기반, #46 연결 | [13:58](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792299513889189) |
| platform #40 | PostgreSQL 17.8·pgvector 0.8.1 로컬 컨테이너, 계정 분리·Alembic·원본 revision·고정 digest. #38 기반. 작성 표시·검토 준비 알림 2개 | [16:10](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792307435595879) |
| platform #38 | 로딩·검색·계획 구성·출력 분리, 검색 한 번, 고정 결과의 fingerprint/snapshot/card/rank 검증. 작성 표시·검토 준비 알림 2개 | [16:10](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792307443819659) |

- #38 설명의 전체 pytest 223 passed·2 skipped, B 27 passed·1 skipped, Ruff/mypy와 #45의 pytest/Ruff/mypy 47 source files는 **작성자가 보고한 결과**다. 이번 수집의 독립 재실행·검증 결과가 아니다.
- #45는 PG 저장·CVE/card 색인·생성형 LLM 선택을 별도 예정 작업으로 구분한다. #40의 실제 Docker 검증 설명은 중간에 잘렸고 #47의 mock/PG 테스트 보고도 전체 수집 완료의 증거가 아니다.

## 할 일

- A는 설명된 순서 #34→35→42→44와 참조 위치 반례 #52를 검토한다. B는 #38→40→47 의존 관계와 앱 DML/마이그레이션 계정·원본 rollback·cursor 재개를 검토한다. 알림 속 순서를 실제 병합 명령으로 실행하지 않는다.
- 모델 digest·입력 규칙·데이터 취급·라이선스와 검색/계획 연결을 확인할 필요가 있다. 구체 담당 수락·새 기한은 추정하지 않는다.

## 미해결 질문

- 신규 platform PR들의 현재 원격 승인·CI·병합 상태와 완전한 본문은 이 Slack 수집만으로 미확인이다. 기존 공식 회의록의 결정과 개별 PR의 구현 설명을 합쳐 완료 선언하지 않는다.

## 참고 링크

- [A 후속](../../../proposals/slack/2026-10-15-이름참조-DATA-관계와-후속검토.md), [B 후속](../../../proposals/slack/2026-10-13-B-첫구현-보고와-경계검토.md)
