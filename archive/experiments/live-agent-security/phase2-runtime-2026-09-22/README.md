# Phase 2 runtime security demo

기준일: 2026-09-22

이 디렉터리는 AI Skill·MCP·워크플로 공급망 위험을 정적 검사, 실제 로컬 모델 도구 호출, Docker 격리, 실행 무결성, 사용자 판단 연구 설계로 나눠 검증한 증거 묶음이다.

## 먼저 읽을 문서

1. [최종 결과와 제품 결론](FINAL-RESULTS.md)
2. [8개 요청 항목 상태표](coverage-status.md)
3. [로컬 모델 77 run 상세 결과](model-runtime-results.md)
4. [OS 격리·Skill TOCTOU 결과](deterministic-results.md)
5. [공개 Skill·MCP scanner 비교](public-scanners/RESULTS.md)
6. [공개 fake Vercel 원본의 격리 동적 관찰](public-scanners/dynamic-original-skill/RESULTS.md)
7. [공개 캠페인 원본의 로컬 모델 record-only 실험](public-original-model/)
8. [실제 사용자 연구 프로토콜](user-study/field-study-protocol.md)
9. [실험 계획과 실행 범위 변경](plan.md)

## 현재 결론

- 제한된 로컬 조건에서 AI가 악성 MCP 결과를 실제 private read와 더미 secret egress로 연결하는 사례를 확인했다.
- 최종 유효 모델 증거는 77/77 verifier PASS이며 더미 secret egress는 4건이다.
- Docker 격리 8건과 Skill TOCTOU 20건은 모두 사전 기대와 일치했다.
- 정적 scanner는 공격 표현과 분석 방식에 따라 서로 다른 결론을 냈다.
- 실제 사람 대상 연구, Snyk 인증 scan, 상용 victim model 비교는 아직 완료되지 않았다.
- PASS는 증거 무결성과 oracle 일치를 뜻하며 안전 인증이 아니다.

## 상태 표기

| 상태 | 뜻 |
|---|---|
| CONFIRMED | 명시한 로컬 조건에서 실행하고 raw evidence를 재검증함 |
| PARTIAL | 일부 조건은 실행했지만 표본·모델·seed·실제 환경 범위가 부족함 |
| BLOCKED_CREDENTIAL | 필요한 인증 정보가 없어 분석 단계에 도달하지 못함 |
| NOT_RUN | 설계 또는 계측 준비만 있고 요청 대상의 실제 실행은 없음 |
| NOT_ASSESSED | 실행 인프라 오류로 모델 행동 결과를 판정하지 않음 |

모든 실험은 더미 비밀, loopback 또는 Docker 내부 receiver, record-only shim을 사용했다. 실제 공격 인프라와 실제 자격 증명은 사용하지 않았다.
