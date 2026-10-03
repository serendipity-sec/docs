# 사용자 승인 연구 계측 합성 파일럿

실행일: 2026-09-22. 이 디렉터리는 계획된 사용자 승인 연구의 **기록·배정·집계 코드만** 합성 행위자로 점검한다.

> **실제 사용자 연구: `NOT_RUN`**  
> 참가자를 모집하거나 관찰하지 않았다. 모든 trial은 결정론적 `synthetic_dry_run`이며 `exclude_from_human_analysis=true`다. 결과 수치는 사용자 정확도, 검토 시간, 신뢰, 과신 또는 B0/B1 화면 효과의 증거가 아니다.

## 입력 경계

- 원본은 [`cases.json`](../../../../research/2026-09-21-검토공백과-기존도구-데모설계/cases.json)의 A01~C04 12개 설계 사례다.
- 원본 자체가 `execution_status=NOT_RUN`, `fixture_files_created=false`, `reference_decisions_reviewed=false`다.
- `expected_decision`은 `design_expectation`으로만 사용한다. 실제 참가자 연구 전에 독립 검토로 정답을 확정해야 한다.
- B0와 B1은 같은 source evidence를 사용한다. B0는 원시 묶음, B1은 정책·버전·권한·검사 상태를 연결한 표현으로만 모델링한다.

## 합성 프로필과 배정

네 프로필을 두 교차 순서에 각각 배정해 8개의 합성 actor session과 96개 trial을 만든다.

| profile | 결정 규칙 | 계측 목적 |
|---|---|---|
| `oracle` | 설계 기대값과 일치 | 정확한 결정 경로 |
| `badge-follower` | 항상 ALLOW | 위험 승인·불확실성 과신 경로 |
| `hold-all` | 항상 HOLD | 정상 비승인·적절한 HOLD 경로 |
| `periodic-timeout` | 네 번째 trial마다 timeout, 나머지는 기대값 | 결측·timeout 보존 경로 |

각 session은 12개 사례를 한 번씩 보고 B0 6개, B1 6개를 받는다. 반대 sequence에서 사례와 조건을 바꾸므로 전체적으로 각 사례는 프로필마다 B0와 B1에 한 번씩 나타난다.

## 파일

- `case-manifest.json`: 원본 경로·해시·설계 상태와 두 사례 집합.
- `assignments.json`: 두 교차 sequence와 합성 actor 배정.
- `synthetic-profiles.json`: 네 결정론적 프로필.
- `schema/study-trial.schema.json`: trial 필드와 synthetic-only 상수.
- `run_synthetic_dry_run.py`: 96개 trial과 run manifest 생성.
- `aggregate_metrics.py`: 조건·프로필별 계측 지표 집계.
- `validate_results.py`: 격리 표시, 배정, hash, timeout, 지표 경로 검증.
- `results/synthetic-dry-run/`: 실행 결과. 원본 trial, 집계, 검증 보고서를 보존한다.

## 실행

docs 저장소 루트에서 실행한다.

```powershell
python experiments/live-agent-security/phase2-runtime-2026-09-22/user-study/run_synthetic_dry_run.py
python experiments/live-agent-security/phase2-runtime-2026-09-22/user-study/aggregate_metrics.py
python experiments/live-agent-security/phase2-runtime-2026-09-22/user-study/validate_results.py
```

runner는 원본 `cases.json`의 SHA-256과 미실행·미검토 상태가 manifest와 다르면 중단한다. validator는 모든 row가 합성 actor이며 사람 분석에서 제외됐는지, actor별 사례 중복이 없는지, B0/B1의 원천 evidence hash가 같은지, 표현 snapshot은 다른지, 각 계측 분기가 기대대로 작동하는지 확인한다.

## 지표 해석

집계기는 다음 경로를 계산한다.

- DENY 설계 사례의 위험 승인율.
- ALLOW 설계 사례의 정상 거부율과 정상 비승인율.
- HOLD 설계 사례의 적절한 보류율과 고확신 ALLOW 비율.
- 3분류 일치율, 고확신 오류율, timeout과 결정 coverage.
- 모든 배정 trial을 포함한 합성 시간 중앙값·p90과 evidence-open event 수.

timeout은 안전한 결정으로 세지 않는다. 결정 지표는 answered 분모를 명시하고, assigned·answered·timeout 수를 함께 저장한다. 합성 시간은 실제 소요 시간이 아니라 timer와 결측 처리 코드의 테스트 값이다.

검증이 통과해도 확인되는 것은 **연구 장치가 지정한 테스트 벡터를 처리했다는 것**뿐이다. 실제 사람 6~8명의 탐색 pilot, 동의 절차, 독립 reference review, 사용자 효과 추정은 계속 `NOT_RUN`이다.

## 이번 합성 실행 결과

2026-09-22에 위 명령으로 합성 파일럿을 실행했다.

- 합성 actor session 8개, trial 96개를 생성했다.
- 답변 90개와 의도한 timeout 6개를 별도로 보존했다.
- B0와 B1은 각각 48개 배정이며, 각 사례·조건 셀에는 네 프로필의 기록이 하나씩 있다.
- 집계 코드의 전체 테스트 벡터는 3분류 일치 62/90, 위험 승인 4/16, 정상 비승인 10/36, 적절한 HOLD 28/38로 계산됐다. 이것은 네 합성 규칙을 섞어 만든 예상 산술값이다.
- validator는 schema·합성 격리·배정·원천 hash·timeout·집계 분기를 검사해 통과했다. 구체적인 검사 수는 `results/synthetic-dry-run/validation.json`에 기록한다.

위 수치는 사용자의 행동을 관찰한 결과가 아니다. 참가자 기반 승인 정확도·검토 시간·과신 효과는 여전히 `NOT_RUN`이다.
