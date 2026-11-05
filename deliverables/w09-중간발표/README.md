# FlowDelta 중간발표

[발표 PDF 열기](FlowDelta_중간발표.pdf)

사용자가 제공한 18쪽 PDF 원본을 2026-10-23에 저장소에 추가했다. 표지의 발표 자료 기준일은 2026-10-22이며, PDF 내용과 바이트는 수정하지 않았다.

| 항목 | 값 |
|---|---|
| 파일 | `FlowDelta_중간발표.pdf` |
| 페이지 | 18쪽, 16:9 |
| 크기 | 24,978,911 bytes |
| SHA-256 | `cebe1ac76fd8ecaf9b3d11991c0e12781434fd44c3d481ea9cb1aa34867540b3` |
| 확인 | 18쪽 렌더링 확인, 사용자 제공 원본과 복사본 SHA-256 일치 |

## 자료 구성

- 1~7쪽: FlowDelta 소개, n8n과 AI 에이전트, workflow JSON과 실행 환경.
- 8~10쪽: 공개 보안 사례와 변경 후 보호 조건을 확인해야 하는 이유.
- 11~15쪽: 프로젝트 목적, 전체 구조, A 변경 분석 / B 근거 검색·시험 계획 / C 실행·관측.
- 16~18쪽: 현재 확인 범위, 첫 평가 계획, 비교 대상, 화면·API·DB 설계.

## 진행 상태를 읽는 기준

발표 자료에는 구현한 기능과 앞으로 구현·평가할 설계가 함께 있다. 정상 주문 조회의 A/B/C 통합 실행, n8n-claw 도구 코드의 부분 재현, 전체 Agent 보안 검증을 구분한다. 전체 Agent 보안 검증·RAG 비교 평가와 제품 화면/API는 자료에 표시한 후속 계획이다.

발표 파일의 저장소 업로드와 과목 LMS 제출·발표 완료는 별개다. 이 문서는 저장소에 보관한 파일과 무결성만 기록한다. 최신 구현 상태는 [platform](https://github.com/serendipity-sec/platform), [열린 PR](https://github.com/serendipity-sec/platform/pulls), [담당별 이슈](https://github.com/serendipity-sec/platform/issues)를 확인한다.

## 관련 자료

- [A 모듈 중간 진행 보고](../w08-중간진행보고/A-그래프분석.md)
- [A의 n8n-claw 분석 그림](A-n8n-claw-분석.html)
- [2026-10-15 주간 보고와 제작 방법](../weekly/2026-10-15/README.md)
