# GitHub PR 알림 — 고정 입력·A 인계·B 병합·공유 자료

## 수집 범위

- capstone2 공개 채널, **2026-10-20 02:28:51 KST** 기준 전체 재조회. 실제 Slack 날짜는 **10/11~20**, 새 알림은 **10/19~20**다. 초기 과거 백업과 재조회 중복을 새 작업으로 합산하지 않는다.
- history 91개·스레드 32개의 실제 답글 37개를 모두 확인했다. 답글은 전부 history와 겹쳐 고유 **91개**, 이전 대비 새 **18개**다. 변경된 native 응답 8페이지를 [이번 raw](../../raw/2026-10-20/C0C8EGWPF33.jsonl)에 저장했다. [이전 요약](../2026-10-19/C0C8EGWPF33.md).
- 발췌와 말줄임을 보존했다. 외부 PR 코드·첨부 본문·플랫폼 테스트는 직접 열람/실행하지 않았다. 아래 확인일 10/20는 Slack 확인일이다.

## 결정 사항

- 작성·ready for review·닫힘·재열림·병합을 구분한다. 알림 속 검증·성능 주장은 작성자 보고이며 이번 예약의 독립 검증 결과가 아니다.
- platform #40은 **10/20 01:55:18 closed → 01:56:19 reopened → 02:12:30 merged**다. 중간 closed를 최종 종료 상태로 남기지 않는다. [닫힘](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792428918716839), [재열림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792428979371709), [병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792429950529559)

## 진행 상황

| 범위 | 새 알림과 보이는 설명 | 근거 |
|---|---|---|
| docs #43 | 10/19 이전 동기화 작성·병합 2개. 새 기능 2건이 아님 | [작성](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792339764463899), [병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792339819356979) |
| platform #53 | 10/19 작성. ai_tool·ai_languageModel 부착 연결을 main 실행 순서/항목 필드 흐름과 구분. #44 위 stacked PR | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792350177964249) |
| #54 | 10/19 작성. 정확한 analysis ID 저장·조회 인터페이스와 파일·메모리 구현. 공용 DB adapter는 공통 migration 틀 뒤 별도 연결 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792350724449299) |
| #55 | actions/upload-artifact 4.6.2→7.0.2 작성·10/20 병합 2개. 릴리스 노트 발췌는 외부 실행 검증이 아님 | [작성](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792369255564409), [병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792428910827889) |
| #56 | 고정 FixedComparisonProfile로 기준 workflow·업무·정책·초기 상태·환경·의존성·모델 설정 변경을 거부한다는 작성 설명. freeze/check/profile-snapshot CLI | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792374703165579) |
| #57 | n8n-claw 기억 삭제 사례의 고정 URL 8파일·해시 수집기·네트워크 없는 재현기·정제 영수증 공유. 원본 재배포 제한은 작성자의 라이선스 관측 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792374709192919) |
| #58 | profile 해시+case ID namespace의 InputRepository, 다른 내용의 같은 ID 충돌 거부, bytes·참조 해시 보존. #56 기반 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792375033387919) |
| #59 | 명시 case/profile/catalog/cards로 입력→A→B→선택적 등록 C→bundle 연결. 기본 PREPARE/C NOT_RUN, --execute에도 기존 C 검사 유지. #56→58→59 스택 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792375492116969) |
| #34·35 | 10/19 필드 흐름·고정 하위 workflow 그래프, 정적 영향 경로 각각 병합 알림 2개 | [#34](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792380569372779), [#35](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792381105128109) |
| #60 | 10/19 analysis.json 소비자 안내 작성, 코드 변경 없음. truncated→changes→impact_paths→support/limitations 순서, 경로 없음이 안전을 뜻하지 않는다고 설명. #53 기반 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792394502140049) |
| docs #44 | 10/20 A 중간보고 초안·n8n-claw 분석 PNG/HTML 자료 작성. 본문은 10/23 보고·10/30 발표 용도와 보고서 담당 미정을 명시 | [알림](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792426205163209) |
| platform #38·40 | 10/20 검색/계획 분리와 PG 저장/migration 병합. #40 상태 전환 3개는 위 시간순으로 보존 | [#38 병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792428916024649), [#40 병합](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1792429950529559) |

- 같은 TS의 기존 #35·38·40·42·45 설명도 현재 발췌로 보존했다. #42는 #34·35 병합 후 main 기반으로 바꿨다는 설명과 Closes #52가 추가됐고, #45는 실제 Docker Ollama smoke에서 1024차원 문서·질의 벡터를 확인했다는 한국어 보고다. 정확한 편집 시각은 알 수 없으며 새 PR 생성으로 세지 않는다.
- 자료 초안·이미지 공유는 공식 보고서 제출·발표 완료가 아니다. 생성형 LLM 선정·공용 서버 배포·임의 워크플로 C 실행·최종 보안 판정을 완료했다고 해석하지 않는다.

## 할 일

- 알림에 명시된 stacked PR의 선행 병합 후 main 재정렬·CI 재확인, A/B 소비자 경계와 정확한 ID 계약을 검토한다. 이 예약이 그 플랫폼 PR을 병합하거나 코드를 실행하지는 않는다.
- 기억 삭제 사례·발표 자료는 [자료 목록](../../../research/slack/2026-10-19_2026-10-20-기억삭제사례와-A발표자료-공유목록.md)에 연결한다. 실제 파일·원본 라이선스·재현 결과는 별도 확인이 필요하다.

## 미해결 질문

- 새 작성 PR들의 승인·모든 CI·최종 원격 상태, 담당 수락·보고서 통합 담당, 생략된 상세는 미확인이다. 이 Slack 알림에서 확인되지 않은 최종 합의·제출 상태는 변경하지 않는다.

## 참고 링크

- [고정 입력·파이프라인 설명](../../../proposals/slack/2026-10-19-고정profile과-입력저장-파이프라인-구현보고.md), [A 후속](../../../proposals/slack/2026-10-15-이름참조-DATA-관계와-후속검토.md), [B 후속](../../../proposals/slack/2026-10-13-B-첫구현-보고와-경계검토.md)
