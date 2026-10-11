# 결정론적 런타임 격리·Skill TOCTOU 데모 결과

실행일: **2026-09-22 (Asia/Seoul)**  
범위: 합성 파일, 고정 Python fixture, 로컬 Docker Desktop, 외부 인터넷 없는 전용 네트워크  
상태: 런타임 격리 8건과 Skill 실행 무결성 20건 완료, 독립 재검증 문제 0건

이 실험은 기존 `paper-guided-2026-09-22`의 저장 코드와 결과를 수정하지 않고 새 디렉터리에서 실행했다. 모든 비밀은 run별 `LAB_ONLY_<uuid>` 가짜 값이며 실제 자격 증명이나 공개 악성 패키지를 사용하지 않았다.

## 실행 환경과 증거

- Docker Desktop 4.83.0의 Linux Engine 29.6.2
- 고정 이미지: `python@sha256:4c47124a8391cb7a9f571164147d154777cf012a4ece5f86097130d7a4478111`
- collector와 공격 서버가 연결되는 조건도 `docker network create --internal`로 만든 외부 라우팅 없는 run별 네트워크만 사용
- 각 run에 Docker create 명령, container inspect, stdout/stderr, 실제 파일, collector receipt, 결과 JSON을 보존
- 실행 코드는 각 batch의 `code/`에 복사하고 SHA-256 manifest를 저장
- `verify_deterministic.py`가 결과 요약이 아니라 실제 파일·receipt·Docker inspect·코드 snapshot을 다시 읽어 판정

최종 실행 전 Docker Desktop lifecycle 지연 때문에 TOCTOU 개발 실행 두 번을 중단했다. 첫 실행은 hardened container 생성, 두 번째 실행은 attach 시작이 각각 30초 제한을 넘었다. 공격 판정과 예상 결과는 바꾸지 않고 container create/start 제한만 90초로 늘린 뒤 batch 디렉터리를 새로 만들어 전체 20건을 다시 실행했다. 중단 실행은 최종 분모에 포함하지 않는다.

## 1. 실제 파일·네트워크 격리 8건

사전 가설은 정상 archive 업무는 네 조건에서 모두 유지되고, sleeper 공격은 제공받은 capability만 사용할 수 있다는 것이었다.

| 서버 동작 | Docker 조건 | private 읽기 시도 | 실제 private 읽기 | 전송 시도 | canary 실제 수신 | 정상 archive |
|---|---|---:|---:|---:|---:|---:|
| 정상 | broad container | 0 | 0 | 0 | 0 | PASS |
| 정상 | network none | 0 | 0 | 0 | 0 | PASS |
| 정상 | private mount 제외 | 0 | 0 | 0 | 0 | PASS |
| 정상 | hardened | 0 | 0 | 0 | 0 | PASS |
| sleeper | broad container | 1 | **1** | 1 | **1** | PASS |
| sleeper | network none | 1 | **1** | 1 | **0** | PASS |
| sleeper | private mount 제외 | 1 | **0** | 0 | **0** | PASS |
| sleeper | hardened | 1 | **0** | 0 | **0** | PASS |

관찰 결과는 8/8건에서 사전 기대와 일치했다.

- 넓은 조건에서는 sleeper가 `/lab/private/session.txt`를 실제로 읽었고 같은 run의 canary가 collector receipt에 도착했다.
- 같은 private mount를 유지하고 `--network none`만 적용하면 파일 읽기는 그대로 성공했지만 HTTP 전송은 실패했다. 네트워크 격리는 이미 허용된 파일 읽기를 취소하지 않는다.
- private 디렉터리를 컨테이너에 마운트하지 않으면 읽기 단계에서 `FileNotFoundError`가 발생했고 전송할 값도 얻지 못했다.
- hardened 조건은 private mount 제외와 network none에 더해 non-root 사용자, read-only rootfs, `cap-drop ALL`, `no-new-privileges`, 메모리·CPU·process 제한을 실제 Docker inspect에서 확인했다.
- 네 조건 모두 공개 프로젝트 파일을 읽어 archive를 쓰는 정상 업무는 성공했다.

저장 결과: `results/runtime-isolation-v1/summary.json`, 실행별 `runs/<run-id>/`, 재검증 `results/runtime-isolation-v1/verification.json`.

## 2. Skill 검사 후 변경·자기수정·복사 실행 20건

각 패키지는 `SKILL.md`와 `helper.py`의 full-tree manifest를 먼저 만들었다. 이후 고정된 barrier 지점에서 파일을 바꾸거나 helper가 실행 중 새 코드를 만들었다. 공격 효과는 모델의 답변이 아니라 `attack-marker.txt`의 실제 생성으로 판정했다.

표의 `EFFECT`는 바뀌거나 새로 생성된 코드가 실제 실행돼 marker를 만든 경우, `SAFE`는 marker가 없는 경우, `HOLD`는 실행 전에 digest 불일치로 보류된 경우다.

| 사례 | 설치 시 1회 검사 | 실행 직전 재해시 | sealed read-only snapshot | sealed + child-process 제한 |
|---|---|---|---|---|
| 정상 helper | SAFE, 정상 업무 | SAFE, 정상 업무 | SAFE, 정상 업무 | SAFE, 정상 업무 |
| 검사 뒤 helper 교체 | **EFFECT**, 정상 업무 | **HOLD**, 업무 미실행 | SAFE, 정상 업무 | SAFE, 정상 업무 |
| 재해시 뒤 open 전에 교체 | **EFFECT**, 정상 업무 | **EFFECT**, 정상 업무 | SAFE, 정상 업무 | SAFE, 정상 업무 |
| 첫 실행에서 자기수정, 두 번째 실행 | **EFFECT**, 정상 업무 | SAFE, 첫 실행 후 두 번째 보류 | SAFE, 정상 업무 | SAFE, 정상 업무 |
| writable output에 복사 후 child 실행 | **EFFECT**, 정상 업무 | **EFFECT**, 정상 업무 | **EFFECT**, 정상 업무 | SAFE, 정상 업무 |

20/20건이 사전 기대와 일치했고, 공격 marker는 7건에서 실제 생성됐다. 정상 결과는 19/20건에서 생성됐다. 남은 1건은 검사 뒤 교체를 실행 직전 재해시가 발견해 helper 실행 자체를 보류한 사례다.

직접 확인한 경계는 다음과 같다.

1. 설치 시 한 번 계산한 digest는 검사 후 파일 교체와 자기수정을 막지 못했다.
2. 실행 직전 재해시는 이미 바뀐 파일과 두 번째 자기수정 실행을 찾았지만, 재해시와 실제 open 사이에 교체하면 바뀐 코드를 실행했다. 경로의 시점별 해시만으로 TOCTOU가 닫히지 않았다.
3. 검증한 바이트를 별도 snapshot으로 복사해 read-only mount에서 실행하면 원본 경로의 교체와 패키지 자기수정은 실제 실행 바이트에 영향을 주지 못했다. 자기수정 시도는 컨테이너에서 `Read-only file system` 오류로 기록됐다.
4. immutable package만으로는 helper가 writable output에 새 payload를 만들고 Python child process로 실행하는 동작을 막지 못했다. `sealed-snapshot`에서 child는 exit 0으로 marker를 만들었다.
5. `sealed+runtime`에서 `--pids-limit 1`을 적용한 이번 직접 child-process fixture는 `BlockingIOError: [Errno 11] Resource temporarily unavailable`로 차단됐고 helper의 정상 결과는 유지됐다.

마지막 결과는 일반적인 임의 코드 실행 방지가 완성됐다는 뜻이 아니다. `pids-limit 1`은 정상적인 child process도 막는 거친 실험 통제이며, interpreter 우회·동일 process 내 악성 동작·커널 취약점·실제 Skill 런타임 전체를 다루지 않는다.

저장 결과: `results/skill-toctou-v1/summary.json`, 실행별 `runs/<run-id>/`, 재검증 `results/skill-toctou-v1/verification.json`.

## 독립 재검증

`verify_deterministic.py`가 다음을 별도로 다시 계산했다.

- runtime-isolation 8개 조합의 누락·중복 여부
- private 파일의 실제 SHA-256과 probe 기록의 일치
- canary가 실제 collector receipt에 포함됐는지
- 정상 archive의 정확한 내용
- private mount 포함 여부, network mode, read-only rootfs, 사용자, capability, process 제한
- TOCTOU 20개 조합의 누락·중복 여부
- 승인 manifest와 최종 original/sealed tree digest
- 실제 marker와 정상 산출물
- read-only 자기수정 오류와 child-process 결과
- 실행 당시 코드 snapshot과 run별 `input_hashes`

결과는 runtime-isolation **8건/문제 0건**, Skill TOCTOU **20건/문제 0건**이다.

이 결과가 지지하는 제품 요구사항은 검사 결과만 저장하는 것이 아니라, 검증한 정확한 바이트를 실행 대상으로 고정하고, 서버·Skill별 파일 mount와 네트워크 capability를 분리하며, 실행 중 새 코드 생성·child process·실제 egress를 별도 runtime 정책과 receipt로 확인해야 한다는 것이다.
