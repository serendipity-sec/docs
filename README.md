# FlowDelta · 최종 설계와 프로젝트 기록

AI 워크플로우의 업데이트가 만든 결합 취약점을 변경 그래프, 취약 시나리오 검색, 변경 전후 실행 증거로 검사하는 프로젝트다.
2026년 10월 3일 사용자가 확정한 설계와 HTML을 **`final/`의 최종본**으로 지정한다. 4명·8~10주를 기준으로 하며, 일정·규모·성능은 계획이고 실행 성과가 아니다.

## 최종본

| 파일 | 내용 |
|---|---|
| [아키텍처 HTML](final/architecture.html) | 단계별 역할, 변경 전·후·수정 후 설명용 예시. 다운로드 후 브라우저로 열 수 있음 |
| [상세 설계서](final/README.md) | 목표·범위·위협 모델·그래프·RAG·실행 검증·보고서 |
| [실행 계획과 논문 평가](final/execution-plan.md) | 4인 역할, 10주 일정, 데이터셋·비교군·지표·비용 |
| [공통 데이터 계약](final/contracts.example.json) | 구성·변경·시험·증거·결과를 연결하는 제안 형식. NOT_RUN 예시 |
| [최종 설계의 조사 근거](final/research-evidence.md) | 공유 설계 5개와 선행 연구·공식 문서의 반영 관계 |

최종이라는 표시는 설계 결정에 대한 것이다. 구현 완료, 탐지 성능 달성, 신규 취약점 발견을 뜻하지 않는다.
HTML은 외부 라이브러리 없이 동작하며 실제 보안 검사를 실행하지 않는다.

## 과거 자료의 분류

| 폴더 | 분류 |
|---|---|
| [archive/proposals](archive/proposals/) | 과거 설계·아이디어·발표 제안 |
| [archive/research](archive/research/) | 자료조사·선행 연구·기존 도구 비교·실험 해설 |
| [archive/experiments](archive/experiments/) | 과거 실험 코드·입력·실행 기록·원본 증거 |
| [archive/notion](archive/notion/) | 이전 Notion 구성·CSV·가져오기 자료 |
| [archive/meetings](archive/meetings/) | 기존 회의록과 당시 템플릿 |
| [archive/deliverables](archive/deliverables/) | 이전 제출 폴더 구조. 빈 폴더가 제출 완료를 뜻하지 않음 |
| [archive/course](archive/course/) | 강의 참고 자료 |
| [분류 전 저장소 소개](archive/repository-overview.md) | 이전 프로젝트 방향·일정·팀 안내의 원문 |
| [팀 온보딩 자료](archive/팀-온보딩.md) | 기존 GitHub 협업 안내 |

[과거 자료 읽는 법](archive/README.md)과 [파일 이동·해시 기록](archive/classification-manifest.json)을 함께 본다.
원본 실험과 자료는 내용을 고치지 않고 보존했으며, 과거 결과를 새 설계의 검증 결과로 인용하지 않는다.

구현 저장소는 [serendipity-sec/platform](https://github.com/serendipity-sec/platform)이다. 그 저장소의 이전 설명은 이번 문서 분류 작업에서 변경하지 않았다.
