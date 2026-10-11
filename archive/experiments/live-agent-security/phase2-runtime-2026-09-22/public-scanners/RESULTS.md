# 공개 Skill·MCP 스캐너 실측 결과

검증 상태: **PASS**. 공개 Skill 또는 MCP 서버 코드는 실행하지 않았다.

## 핵심 결과

- Cisco Skill Scanner 2.1.0은 fake Vercel 두 변형을 모두 `is_safe=true`, 최대 `INFO`로 판정했다. Gemini 변형에는 `.env`와 호스트 정보를 외부 paste 서비스로 보내라는 명시적 명령이 있지만 위협 finding은 없었다.
- Cisco Skill Scanner는 testing-guidelines의 Unicode/ASCII smuggling과 snyk-skill의 taint flow는 각각 `CRITICAL`로 잡았다. 즉 규칙 기반 탐지는 공격 표현에 따라 크게 달라졌다.
- SkillSpector 2.11.2 `--no-llm`은 fake Vercel Gemini에서 외부 전송 `E1`과 unpinned `npx` 위험 `RP1`을 찾았지만 총점 13 `LOW`, 권고 `CAUTION`이었다. Agents 변형은 `E1`이 있어도 권고가 `SAFE`였다.
- Cisco MCP Scanner 4.8.4 YARA는 Appsecco의 명시적 간접 프롬프트 주입 문서 3개, 악성 도구 응답 1개를 포함한 모든 항목을 `SAFE`로 판정했다. 이 결과는 YARA 정적 모드에만 적용된다.
- SkillSpector `codex_cli`는 동일 fake Vercel Gemini 파일에서 의미 분석 4/4회를 완료하고 7개 finding, 점수 100 `CRITICAL`, `DO_NOT_INSTALL`을 냈다. 파일 coverage는 100.0%였다.
- Codex 조건의 전체 completeness는 `partial`다. 원인은 의미 분석 실패가 아니라 14행의 경로처럼 보이는 문구를 해석할 때 생긴 `reference_unresolved` 한 건이다.
- Ollama 1.7B는 813.125초 후 exit 0이었지만 LLM 호출 4회가 모두 실패했고 coverage 0.0%, `partial`였다. 정적 finding만 포함하므로 의미 분석 비교에서 제외했다. 4B는 공유 런타임을 반환하기 위해 중단했다.
- Snyk Agent Scan 0.6.4은 토큰 없는 격리 환경에서 `BLOCKED_CREDENTIAL`이었다. 고정된 0.6.4 소스는 `SNYK_TOKEN`이 없으면 HTTP 요청 반복문 전에 예외를 발생시키므로 실제 보안 분석 결과는 없다.

## Skill 정적 비교

| 입력 | Cisco is_safe / 최대 심각도 | SkillSpector 점수·심각도 / 권고 | coverage / completeness |
|---|---:|---:|---:|
| TS-CLAWHUB | True / INFO | 61 HIGH / DO_NOT_INSTALL | 100.0% / partial |
| TS-SNYK-SKILL | False / CRITICAL | 33 MEDIUM / CAUTION | 100.0% / complete |
| TS-TESTING-GUIDELINES | False / CRITICAL | 30 MEDIUM / CAUTION | 100.0% / complete |
| TS-VERCEL-AGENTS | True / INFO | 6 LOW / SAFE | 100.0% / complete |
| TS-VERCEL-GEMINI | True / INFO | 13 LOW / CAUTION | 100.0% / partial |

## MCP YARA 결과

| 입력 | 항목 수 | SAFE | unsafe | 위협명 |
|---|---:|---:|---:|---|
| MCP-INDIRECT-INJECTION | 4 | 4 | 0 | none |
| MCP-MALICIOUS-TOOLS | 1 | 1 | 0 | none |
| MCP-RCE-METADATA | 1 | 1 | 0 | none |
| MCP-TYPOSQUAT-METADATA | 2 | 2 | 0 | none |

## 해석 경계

- 이 표본 묶음은 작은 목적 표본이며 시장 전체 탐지율을 뜻하지 않는다.
- ToxicSkills 저장소는 위험 데모라는 저장소 수준 경고를 제공하지만 모든 개별 파일의 악성 ground truth를 독립적으로 확정하지는 않았다. fake Vercel, hidden testing 지시, env hook처럼 행위가 명시적인 사례를 중심으로 해석한다.
- MCP RCE와 typosquatting 입력은 서버 소스의 위험이 도구 설명에 충분히 노출되지 않는 경우를 보여준다. YARA의 `SAFE`는 서버 구현이 안전하다는 뜻이 아니다.
- Codex CLI 결과는 한 번의 고정 입력 실행이다. 여러 상용 모델의 일반 성능이나 반복 안정성을 증명하지 않는다.
- 공개 원문을 AI 에이전트에 설치하거나 실제 MCP 서버로 실행하지 않았으므로 실제 피해 발생 가능성은 별도 격리 실행 실험의 영역이다.

## 증거 위치

- `provenance.json`: 저장소 커밋, 입력 경로·해시, 스캐너 바이너리 해시
- `results/`: 명령, 종료 코드, stdout, stderr, 원시 JSON 보고서
- `summary.json`: 위 결과의 기계 판독 요약
- `verification.json`: 안전 경계와 완전성 검증
- `evidence-manifest.json`: 보존 파일의 SHA-256
