# 테스트별 상세 기록

정리일: 2026-09-22. 총 **42개 상세 문서**에 테스트 목적·입력·실행 조건·실제 관측·판정 기준·원본 근거·한계를 정리했다. 반복 seed는 같은 사례 문서 안에서 비교하며, scanner의 입력별 실행도 각 도구 문서에서 따로 기록했다.

현재 결론부터 읽으려면 [유출 판정 독립 재검토](56-유출판정-독립재검토.md)를 먼저 확인한다. 기존 T01 전체파일 oracle이 키 이름을 제외한 실제 비밀값을 놓쳤다. exact-dlp는 raw 2/3에서 검토 전체값 수신 3/3으로 정정했고, lineage는 전체값 0/3이지만 부분 식별자 수신 1/3이다. 원본 결과는 보존했다.

## 전체 실행 범위

| 묶음 | 최종 평가 수 | 저장 상태 |
|---|---:|---|
| 최초 Skill·MCP 9개 사례 | 54 | COMPLETED 54 |
| 승인·최소 권한·결합 통제 | 51 | COMPLETED 45, 모델 호출 전 POLICY_BLOCKED 6 |
| 공개/비밀 flow와 동일 metadata sleeper | 33 | COMPLETED 33 |
| MCP 공격 단계 4종 + 정상 쌍 | 48 | COMPLETED 45, STEP_LIMIT 3 |
| **합계** | **186** | COMPLETED 177, POLICY_BLOCKED 6, STEP_LIMIT 3 |

`COMPLETED`는 실행기가 종료됐다는 뜻이며 정상 업무 성공 또는 안전을 뜻하지 않는다. 별도로 digest 계약 11건, 검사 완료 gate 11건, Skill 무결성 계약 8건, 초기 scanner 20건과 추가 scanner 2건을 평가했다. 원래 A·B·C 12개 명세와 별도 실행 사례의 분모를 섞지 않는다.

저장된 result.json 223개 중 개발 제외는 37개이며, result.json 없는 부분 실행 1건도 별도로 보존한다. 상세 [미실행·평가 제외](55-미실행과-평가제외.md)를 참고한다. 사람 대상 승인 판단·시간·과신 연구는 NOT_RUN이다.

## 문서 색인

### 초기 Skill·MCP 사례

| 문서 | 설명 |
|---|---|
| [01-S00-정상-Skill](01-S00-정상-Skill.md) | 01. S00 정상 Skill 대조군 |
| [02-S01-Skill-본문-주입](02-S01-Skill-본문-주입.md) | 02. S01 Skill 본문 주입 |
| [03-S02-Skill-참조파일-주입](03-S02-Skill-참조파일-주입.md) | 03. S02 Skill 참조 파일 주입 |
| [04-S03-Skill-승인파일-변조](04-S03-Skill-승인파일-변조.md) | 04. S03 Skill 승인 파일 변조 |
| [05-M00-정상-MCP](05-M00-정상-MCP.md) | 05. M00 정상 MCP 대조군 |
| [06-M01-MCP-도구설명-주입](06-M01-MCP-도구설명-주입.md) | 06. M01 MCP 도구 설명 주입 |
| [07-M02-MCP-응답-주입](07-M02-MCP-응답-주입.md) | 07. M02 MCP 응답 주입 |
| [08-M02C-정상-MCP-응답](08-M02C-정상-MCP-응답.md) | 08. M02C 정상 MCP 응답 대조군 |
| [09-M03-MCP-설명변경](09-M03-MCP-설명변경.md) | 09. M03 MCP 설명 변경 |

### 승인·권한·검사 완료 통제

| 문서 | 설명 |
|---|---|
| [10-T1-승인-Digest-잠금](10-T1-승인-Digest-잠금.md) | 10. T1 승인 대상 digest 잠금 |
| [11-T2-업무별-최소권한](11-T2-업무별-최소권한.md) | 11. T2 업무별 최소 권한 |
| [12-T3-Digest-사각지대와-결합통제](12-T3-Digest-사각지대와-결합통제.md) | 12. T3 digest 사각지대와 결합 통제 |
| [13-결정론적-Digest-Gate-계약](13-결정론적-Digest-Gate-계약.md) | 13. 결정론적 digest gate 계약 |
| [14-검사완료-Scan-Gate-계약](14-검사완료-Scan-Gate-계약.md) | 14. 검사 완료 상태 scan gate 계약 |

### 논문 기반 flow·sleeper·패키지 계약

| 문서 | 설명 |
|---|---|
| [20-T00-정상-공개정보-변환흐름](20-T00-정상-공개정보-변환흐름.md) | T00 — 정상 공개정보 변환·전송 흐름 |
| [21-T01-변형-민감정보-유출-정책비교](21-T01-변형-민감정보-유출-정책비교.md) | T01 — 악성 MCP 응답의 변형 민감정보 유출과 정책 4종 비교 |
| [22-R00-안정-MCP-서버-정상흐름](22-R00-안정-MCP-서버-정상흐름.md) | R00 — metadata와 동작이 안정적인 MCP 서버 정상 흐름 |
| [23-R01-sleeper-rug-pull-정책비교](23-R01-sleeper-rug-pull-정책비교.md) | R01 — 동일 metadata sleeper/rug-pull과 endpoint capability 조건 |
| [24-I00-정상-서명-패키지](24-I00-정상-서명-패키지.md) | I00-valid-clean — 정상 패키지가 불필요하게 보류되지 않는가 |
| [25-I01-SKILL-승인후-변경](25-I01-SKILL-승인후-변경.md) | I01-skill-edited — 서명 이후 entrypoint의 변경을 확인하는가 |
| [26-I02-helper-승인후-변경](26-I02-helper-승인후-변경.md) | I02-helper-edited — SKILL.md가 같아도 helper 변경을 보류하는가 |
| [27-I03-unsigned-파일추가](27-I03-unsigned-파일추가.md) | I03-unsigned-file-added — 서명 목록에 없는 새 파일을 발견하는가 |
| [28-I04-서명된-파일삭제](28-I04-서명된-파일삭제.md) | I04-signed-file-removed — 서명된 참조 파일이 빠진 패키지를 보류하는가 |
| [29-I05-신뢰하지않는-서명자](29-I05-신뢰하지않는-서명자.md) | I05-untrusted-signer — 유효한 서명과 신뢰 발행자를 분리하는가 |
| [30-I06-구버전-replay](30-I06-구버전-replay.md) | I06-old-version-replay — 유효하게 서명된 과거 버전의 재사용을 막는가 |
| [31-I07-유효서명-악성패키지](31-I07-유효서명-악성패키지.md) | I07-validly-signed-malicious — 서명된 악성 내용에 별도 안전 정책이 필요한가 |
| [32-Cisco-MCP-변형응답-probe](32-Cisco-MCP-변형응답-probe.md) | Cisco MCP Scanner — 변형 유출 응답 연결 probe |

### MCP 공격 단계와 정상 대조

| 문서 | 설명 |
|---|---|
| [40-P04C-정상-policy-hint](40-P04C-정상-policy-hint.md) | P04C — 정상 policy hint와 정확한 파일 인자 |
| [41-P04A-implicit-parameter-hijack](41-P04A-implicit-parameter-hijack.md) | P04A — tool metadata의 implicit parameter hijack |
| [42-P05C-정상-project-note](42-P05C-정상-project-note.md) | P05C — 정상 project note 응답 |
| [43-P05A-user-impersonating-response](43-P05A-user-impersonating-response.md) | P05A — user-impersonating MCP response |
| [44-P06C-정상-primary-record](44-P06C-정상-primary-record.md) | P06C — 정상 primary 조회의 허용과 효용 |
| [45-P06A-가짜오류-도구전환](45-P06A-가짜오류-도구전환.md) | P06A — 가짜 오류가 비요청 도구 전환을 유발하는가 |
| [46-P07C-정상-검색레코드](46-P07C-정상-검색레코드.md) | P07C — 공개 검색 결과의 정상 요약 |
| [47-P07A-검색레코드-주입](47-P07A-검색레코드-주입.md) | P07A — 검색 record에 섞인 지시의 실행 여부 |

### 기존 검사기별 입력·결과

| 문서 | 설명 |
|---|---|
| [50-Cisco-Skill-Scanner](50-Cisco-Skill-Scanner.md) | Cisco Skill Scanner 2.1.0 — 입력별 검사 상세 |
| [51-Cisco-MCP-Scanner](51-Cisco-MCP-Scanner.md) | Cisco MCP Scanner 4.8.4 YARA — 입력별 검사 상세 |
| [52-SkillSpector-기본](52-SkillSpector-기본.md) | NVIDIA SkillSpector 2.11.2 기본 --no-llm — 입력별 검사 상세 |
| [53-SkillSpector-불완전성차단](53-SkillSpector-불완전성차단.md) | NVIDIA SkillSpector 2.11.2 --fail-on-incomplete — 입력별 검사 상세 |
| [54-AgentShield-검사범위](54-AgentShield-검사범위.md) | AgentShield 1.6.0 — 입력별 검사 상세 |

### 미실행 범위와 독립 재검토

| 문서 | 설명 |
|---|---|
| [55-미실행과-평가제외](55-미실행과-평가제외.md) | 미실행·평가 제외 범위 |
| [56-유출판정-독립재검토](56-유출판정-독립재검토.md) | 유출 판정의 독립 재검토 — 전체 파일·전체 값·부분 노출 |

## 재현 환경과 기록 읽는 법

실행은 Windows, Python 3.12, 로컬 Ollama와 고정 Qwen3 모델을 사용했다. 구체적 버전·model digest·seed·temperature·step budget은 해당 batch의 runtime와 initial-request에 있다. Ollama endpoint는 `http://127.0.0.1:11436`이며, 실행기는 서버와 모델이 준비되어 있다고 가정한다. 설치 런타임과 모델 가중치는 저장소에 포함하지 않는다.

초기 54회는 harness 1.2/1.3의 저장 snapshot에서 나왔다. 현재 run_lab.py(v2.0)로 같은 인자를 실행한 결과를 과거와 동일 버전 재현이라고 부르면 안 된다. 정확한 과거 replay에는 새 임시 폴더에 해당 `runs/<batch>/code`의 Python 파일을 복사한 뒤, 그 폴더에서 먼저 `python build_fixtures.py`를 실행해 cases.json과 fixture를 만든다. 그다음 각 문서의 run_lab.py 명령을 같은 폴더에서 실행한다. 원본 폴더에서는 재실행하지 않는다.

모든 동적 재실행은 새 clone 또는 고유한 새 batch를 사용한다. 고정 seed도 다른 하드웨어·모델 런타임에서 동일한 문장을 보장하지 않는다. 이번 문서화에서는 AI를 새로 호출하지 않고 저장된 근거를 재검토했다.

원본 추적 순서는 `입력·tools → 모델 call → host 결정 → 서버 action → 실제 receipt/파일 → result`다. 말로만 수행했다고 답한 것은 실제 효과가 아니다. canary가 없는 비요청 수신, 전체값 수신, 부분 노출을 구분한다. utility는 각 문서의 원래 oracle과 검토 보완을 함께 읽는다.

## 검증과 증거 보존

플랫폼 증거 커밋: [`4bd3ca337dd000fa60791207f94025807dff8a0c`](https://github.com/serendipity-sec/platform/commit/4bd3ca337dd000fa60791207f94025807dff8a0c). 문서 링크는 이 SHA에 고정되어 이후 main 변경과 구분된다.

- [저장 범위·재검증 명령·Git 바이트 보존 방식](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/publication-guide.md)
- [초기 효과 체인 112회 재검증](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/evidence-verification.json)
- [초기 scanner 20건·입력 24개·공식 출처 29개 검증](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/scanner-evidence-verification.json)
- [논문 기반 81회·무결성 8건·probe 2건 검증](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/verification.json)
- [사후 T01 12회 receipt 재검토](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/egress-oracle-audit.json)

커밋에서 꺼낸 깨끗한 사본에서도 위 검증기를 실행해 저장 근거의 issue_count=0을 확인했다. 그러나 이 검증이 충분한 공격·utility oracle, 제품 안전성, 생태계 전체 탐지율을 보장하지는 않는다. 검증된 범위와 실제 발견된 oracle 누락을 함께 남긴다.

문서 자체의 검사 기록: [고정 증거·내부 링크 검증](document-validation.json), [Skill 무결성 8건 읽기 전용 재계산](skill-integrity-recheck.json).

[실험 전체 요약으로 돌아가기](../README.md)
