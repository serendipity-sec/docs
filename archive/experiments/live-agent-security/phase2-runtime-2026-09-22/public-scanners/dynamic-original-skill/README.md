# 공개 fake Vercel Skill 격리 관찰 실험

이 디렉터리는 Snyk Labs `toxicskills-goof`의 고정 공개 원문을 **실행 코드가 아닌 inert text**로 읽고, 원문이 유도하는 명령 선택과 dummy `.env` payload 구성만 기록한다. 외부 통신과 실제 `npm`, `npx`, Vercel 배포는 수행하지 않는다.

## 조건

- 입력: `.runtime/quarantine/toxicskills-goof/.gemini/skills/vercel/SKILL.md`
- 커밋: `80ce2e06f52fd384163c4bd6778676019723773c`
- SHA-256: `d70912ce0d898712b9b5048423d89d5190ffe4775d57f3221bff35bddbe36e3e`
- 행동 조건: `DETERMINISTIC_SAFE_INTERPRETER`
- AI 모델 사용: 없음
- 네트워크: Docker `none`
- 도구: 실제 프로그램 대신 기록 전용 `curl`, `npm`, `npx`, `uname` shim

결정론적 interpreter는 원문을 shell, `source`, `eval`, `exec`에 전달하지 않는다. 고정 marker와 allowlist가 일치할 때만 명시적인 argv 배열을 `shell=False`로 shim에 전달한다. 따라서 결과는 “공개 원문에 위험 지시가 있고, 안전한 해석 규칙이 그 지시로부터 어떤 명령과 payload를 구성하는가”를 확인한다. LLM이나 자율 에이전트가 실제로 지시를 따랐다는 증거는 아니다.

## 실행

Docker Desktop이 실행 중이고 고정 base image가 로컬에 존재하는 상태에서 다음을 실행한다.

```powershell
python .\run_experiment.py
```

runner는 base image를 pull하지 않고, `--network=none` build와 격리 컨테이너 실행을 수행한다. 컨테이너가 실행 중일 때 고정 파일명만 허용하는 `/harness/export_evidence.py`를 `docker exec`로 호출해 tmpfs evidence를 stdout으로 회수한다. 그 뒤 SIGTERM으로 interpreter를 정상 종료하고 컨테이너를 삭제한 다음 `validate.py`를 실행한다. export 과정에도 shell이나 외부 네트워크는 사용하지 않는다.

## 증거 위치

- `results/provenance.json`: 입력 경로·커밋·실행 전후 해시와 안전 경계
- `results/image-digest.json`: base/built image ID와 digest
- `results/container-config.json`: 요청한 Docker 인자와 inspect 관찰값
- `results/container-evidence/events.jsonl`: shim 호출 순서·argv·통신 여부
- `results/container-evidence/interpreter-result.json`: 선택 결과·dummy payload·범위 제한
- `results/raw/container.stdout.txt`, `container.stderr.txt`: 원시 컨테이너 출력
- `results/raw/container-inspect-*.json`: 실행 전후 Docker inspect 원문
- `results/validation.json`: 자동 검증 결과
- `RESULTS.md`: 사람이 읽는 상세 판정
- `evidence-manifest.json`: 위 파일과 하네스 전체의 크기·SHA-256 목록(자기 자신 제외)

로컬에서 부재해 `AV_BLOCKED_OR_REMOVED`로 분류된 `.agents/skills/clawhub/skill.md`와 `.agents/skills/google/SKILL.md`는 입력·마운트·복구 대상에서 제외한다. 이 증거만으로 부재 원인을 단정하지 않는다.
