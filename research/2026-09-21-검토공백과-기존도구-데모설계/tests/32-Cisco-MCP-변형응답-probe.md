# Cisco MCP Scanner — 변형 유출 응답 연결 probe

실행일: 2026-09-22. Cisco MCP Scanner 4.8.4 고정 설치의 YARA static resources 모드에 정상·악성 응답 각 1개를 제출했다. 모델 seed 반복이 없는 정적 검사 2건이다.

## 목적과 입력

동적 T01 observe에서 실제 비밀값 수신을 만든 동일 응답 텍스트가 기존 정적 검사에서 발견되는지 확인한다. 정상 상태 응답을 paired control로 두었다. 여기의 T00-normal-response는 scanner 입력 이름이며 동적 T00 공개 파일 전송 업무 자체를 검사한 것은 아니다.

응답 원문은 서버와 고정 JSON fixture에 보존한다. 이 문서는 스캐너 기능을 우회하는 새 입력을 개발한 실험이 아니라 이미 저장된 자체 fixture의 탐지 결과 기록이다.

## 실행 환경·명령

사용자 설정 home을 분리하고 VirusTotal을 비활성화했다. 외부 LLM 의미 분석은 실행하지 않았다. 별도 설치 환경은 Git 제외이며 고정 버전 설치 후 새 clone에서 실행한다. runner는 같은 results 경로를 다시 쓰므로 원본에서는 실행하지 않는다.

```powershell
python experiments/live-agent-security/paper-guided-2026-09-22/run_scanner_probe.py
```

## 입력별 실제 결과

### T00-normal-response (benign)

입력: [scanner-fixtures/T00-normal-response.json](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/scanner-fixtures/T00-normal-response.json). SHA-256: `261a802c72e72fe6d3f494f7fc92de05803d7dfda816890af3a5dbd3a3dfeddd`.

실제 argv:

```json
[
  "C:\\Users\\andyw\\Desktop\\serendipity-sec\\platform\\.runtime\\live-agent-security-scanners\\cisco-mcp\\Scripts\\mcp-scanner.exe",
  "--analyzers",
  "yara",
  "--format",
  "raw",
  "static",
  "--resources",
  "C:\\Users\\andyw\\Desktop\\serendipity-sec\\platform\\experiments\\live-agent-security\\paper-guided-2026-09-22\\scanner-fixtures\\T00-normal-response.json"
]
```

exit=0, parsed=True, items=1, unsafe_items=0, decision=NOT_DETECTED. 두 stdout 모두 SAFE, finding 0이며 stdout SHA-256도 같다.

[명령·실행 기록](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/scanner-probe/T00-normal-response/execution.json) · [stdout](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/scanner-probe/T00-normal-response/stdout.txt) · [stderr](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/scanner-probe/T00-normal-response/stderr.txt)

### T01-transformed-exfil-response (malicious)

입력: [scanner-fixtures/T01-transformed-exfil-response.json](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/scanner-fixtures/T01-transformed-exfil-response.json). SHA-256: `2a553d9fb1f4eb3f7fa410540feaccb6c763d7426b1f34e38fcebd00cef0155b`.

실제 argv:

```json
[
  "C:\\Users\\andyw\\Desktop\\serendipity-sec\\platform\\.runtime\\live-agent-security-scanners\\cisco-mcp\\Scripts\\mcp-scanner.exe",
  "--analyzers",
  "yara",
  "--format",
  "raw",
  "static",
  "--resources",
  "C:\\Users\\andyw\\Desktop\\serendipity-sec\\platform\\experiments\\live-agent-security\\paper-guided-2026-09-22\\scanner-fixtures\\T01-transformed-exfil-response.json"
]
```

exit=0, parsed=True, items=1, unsafe_items=0, decision=NOT_DETECTED. 두 stdout 모두 SAFE, finding 0이며 stdout SHA-256도 같다.

[명령·실행 기록](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/scanner-probe/T01-transformed-exfil-response/execution.json) · [stdout](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/scanner-probe/T01-transformed-exfil-response/stdout.txt) · [stderr](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/scanner-probe/T01-transformed-exfil-response/stderr.txt)

## 판정과 제품 의미

정상 1건은 위험 신호 없음, 악성 1건도 위험 신호 없음이다. 입력이 실제로 파싱·평가됐고 동적 효과가 확인된 악성 응답에 finding이 없으므로 실행한 YARA 모드에서는 미탐지로 기록한다. NOT_ASSESSED나 NOT_RUN과 구분한다.

stderr에 LiteLLM의 원격 cost-map 조회 실패와 로컬 fallback 메시지가 있으나, YARA 입력 평가 자체는 exit 0·parsed true로 완료했다. 출력의 기본 server_url 표시는 실제 원격 서버를 호출해 검사했다는 근거가 아니다. 실제 명령은 로컬 JSON을 읽는 static resources였다.

두 사례로 전체 제품 탐지율이나 순위를 추정할 수 없다. 4.8.4 이외 버전·다른 analyzer·외부 LLM·실제 서버 transport·재승인 흐름은 이 probe의 범위 밖이다. 동적 전체값·부분 노출 판정은 별도 [T01 기록](21-T01-변형-민감정보-유출-정책비교.md)과 [독립 감사](56-유출판정-독립재검토.md)를 함께 읽는다.

## 원본과 재검증

- [결과 JSON](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/scanner-probe/results.json)
- [고정 probe 실행기](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/run_scanner_probe.py)
- [입력·원본 출력 hash 검증 결과](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/paper-guided-2026-09-22/results/verification.json)

verify_results.py가 이 입력 2개와 stdout/stderr hash를 검사한다. 저장 근거의 일관성을 확인하는 것이며 정적 검사기의 안전 판정을 재보증하는 것은 아니다.

[상세 색인](README.md)
