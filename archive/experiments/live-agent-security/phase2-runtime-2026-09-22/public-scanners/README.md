# 공개 Skill·MCP 스캐너 실측

이 폴더는 공개된 악성·취약 데모의 **고정 원문을 실행하지 않고 정적으로만 검사**한 증거를 보관한다. 실험 결과는 `results/`, 입력과 저장소 커밋·해시는 `provenance.json`에 기록한다.

## 안전 경계

- `toxicskills-goof`의 Skill 파일은 검역 저장소에서 직접 읽지만 이 폴더로 복사하거나 에이전트에 설치하지 않는다.
- Cisco Skill Scanner와 SkillSpector는 정적 파일 분석만 수행한다.
- Cisco MCP Scanner에는 서버 설정이나 실행 명령 대신 고정 JSON만 제공한다.
- 공개 MCP 서버의 JavaScript를 실행하지 않는다.
- 로컬에서 부재한 관련 파일은 원인을 단정하지 않고 `AV_BLOCKED_OR_REMOVED`로 기록하며 복구·우회하지 않는다.
- Snyk Agent Scan에는 MCP 설정을 주지 않고 단일 `SKILL.md`만 전달한다. 토큰이 없는 상태에서 `BLOCKED_CREDENTIAL`을 확인하는 데 그친다.
- SkillSpector `codex_cli` 조건은 도구·MCP가 제거된 read-only/ephemeral CLI transport를 사용하며, 공개 Vercel 데모 텍스트만 전송한다.

## 입력 출처

- Snyk Labs ToxicSkills demo: <https://github.com/snyk-labs/toxicskills-goof>
- Appsecco Vulnerable MCP Servers Lab: <https://github.com/appsecco/vulnerable-mcp-servers-lab>

Appsecco에서 가져온 짧은 도구·리소스 텍스트는 MIT 라이선스에 따라 `inputs/mcp/`에 고정했고 라이선스 전문을 함께 보관한다. ToxicSkills 저장소에는 루트 라이선스가 보이지 않아 원문을 복사하지 않고 경로·커밋·해시만 기록한다.

## 실행 조건

```powershell
python run_public_scanners.py manifest
python run_public_scanners.py static
python run_public_scanners.py ollama
python run_public_scanners.py codex
python run_public_scanners.py snyk
```

`ollama` 조건은 `127.0.0.1:11437`의 `qwen3:1.7b-q4_K_M`, `qwen3:4b-q4_K_M`만 대상으로 했다. 1.7B는 4회의 의미 분석 호출이 모두 공유 런타임 제한으로 실패했고, 4B는 다른 실험에 공유 런타임을 반환하기 위해 중단했다. 두 결과 모두 탐지 비교에서 제외한다.

## 확인된 결과

- Cisco Skill Scanner 2.1.0은 fake Vercel 두 변형을 `is_safe=true`로 판정했다. testing-guidelines의 숨은 문자와 snyk-skill의 taint flow는 `CRITICAL`로 탐지했다.
- SkillSpector 2.11.2 `--no-llm`은 fake Vercel의 외부 전송을 찾았지만 Agents 변형은 `SAFE`, Gemini 변형은 `LOW`/`CAUTION`이었다.
- Cisco MCP Scanner 4.8.4 YARA는 고정된 Appsecco 간접 프롬프트 주입·악성 응답·RCE 메타데이터·typosquatting 메타데이터 8개 항목을 모두 `SAFE`로 판정했다.
- SkillSpector `codex_cli`는 공개 fake Vercel Gemini 파일만 분석해 의미 분석 4/4회를 완료했고, 점수 100 `CRITICAL`, `DO_NOT_INSTALL`, finding 7개를 냈다. 공개 텍스트 외의 프로젝트 자료나 비밀은 전달하지 않았다.
- Snyk Agent Scan 0.6.4는 전용 환경에 설치했지만 `SNYK_TOKEN`이 없어 `BLOCKED_CREDENTIAL`이었다. 0.6.4 소스에서 토큰 검사가 HTTP 요청 반복문보다 먼저 수행됨을 확인했으므로 보안 분석 결과는 없다.

상세 비교와 해석 범위는 [RESULTS.md](RESULTS.md), fake Vercel 원문의 정확한 위치와 향후 격리 재현 판단은 [DYNAMIC-REPRODUCTION.md](DYNAMIC-REPRODUCTION.md), 기계 판독 결과는 `summary.json`, 증거 검증은 `verification.json`을 참조한다.
