# FlowDelta 데이터베이스 스키마와 단계별 사용 안내

- 기준: platform 입력·파이프라인 계약 0.4.0
- 무결성 보강: 2026-10-27 · [Issue #49](https://github.com/serendipity-sec/docs/issues/49)
- 대상: PostgreSQL 17을 사용하는 후속 공유 저장소 설계
- SQL: [database-schema.sql](database-schema.sql)
- 현재 저장 상태: [current-readiness.md](current-readiness.md)
- 기존 DB·파일 저장 설계: [implementation-design.md](implementation-design.md#10-db와-파일-저장-설계)

## 이 문서의 범위

이 스키마는 FlowDelta가 나중에 여러 구성원의 검증 이력을 공유하는 경우를 위한 참조 설계다. 현재 코드는 파일 묶음을 모듈 간 계약으로 사용하고, 설계 문서의 1차 권고는 로컬 사례와 CLI 사용이다. 이 문서는 DB를 현재 MVP에 도입하기로 결정하지 않는다. 해당 저장소 결정은 [Issue #31](https://github.com/serendipity-sec/docs/issues/31)을 따른다.

DDL은 입력부터 평가 결과까지 필요한 DB 구조를 보여 준다. 워크플로 원문, 정규화 그래프, 상세 분석, 응답, 상태 스냅샷, 이벤트 스트림은 파일 artifact로 보관한다. DB에는 SHA-256, 경로, 크기, 유형과 조회용 속성, 관계를 저장한다. DB 행과 파일 manifest의 참조를 함께 검사해야 한다.

현재 실행 계약은 보안 결과를 null로 둔다. run_checks, check_evidence, comparison_results, result_checks는 독립 판정기를 만든 뒤 적용할 미래 확장이다. card_embeddings도 pgvector 검색을 선택할 때만 활성화한다.

이번 보강은 기존 24개 테이블, UUID 내부 키, 파일 artifact 저장 방식을 유지한다. FK·UNIQUE·CHECK, 게시/불변성 트리거와 조회 인덱스를 추가한다. 전체 원본의 BYTEA 저장이나 실행 report 이력 모델로 전환하지 않는다. 이 SQL은 새 DB에 적용할 참조 DDL이며, 기존 DB를 갱신하는 migration 스크립트가 아니다.

## 작업 흐름과 테이블 쓰기 시점

입력 묶음 → bundles/artifacts → cases/obligations → before/after snapshots → A 분석/analyses → B 검색·계획/retrievals·plans → C 실행/comparison_runs·runs → 증거/run_artifacts·evidence_events → 미래 판정 테이블

id는 DB 내부 UUID이며 외부 JSON의 식별자와 구분한다. 외부 값은 contract_id로 보존한다. created_at과 observed_at은 시간대를 포함한 UTC 시각을 사용한다. JSONB는 계약 payload나 속성 묶음을 보존하며, 이 안의 artifact 경로를 DB FK가 자동 검증하지는 않는다.

### 입력을 받았을 때: bundles, artifacts, cases

1. 먼저 입력 묶음을 읽고 각 파일의 크기와 SHA-256을 확인한다.
2. bundles에 INPUT 유형과 schema 버전, 저장 위치를 등록한다.
3. 파일 하나당 artifacts 행을 등록한다. contract_id와 상대 경로는 그 묶음 안에서 유일해야 한다. `relative_path_key`에는 검증된 `relative_path.casefold()` 값을 넣는다.
4. manifest의 전체 목록·해시·크기와 파일을 대조하고 hash를 기록한 뒤 bundle을 SEALED로 바꾼다. 새 bundle은 OPEN으로만 만들 수 있으며, SEALED/FAILED 상태와 그 artifact 행은 다시 변경하지 않는다.
5. 사례 유효성 검사가 끝나면 cases와 obligations, 양쪽 snapshots를 만든다. 새 입력의 DB 등록은 하나의 트랜잭션으로 커밋하며, 중간 행만 다른 소비자에게 공개하지 않는다.

| 테이블 | 주요 속성의 의미 |
|---|---|
| bundles | kind는 INPUT, MODULE_OUTPUT, RUN_OUTPUT 중 하나다. schema_version은 파일 계약 버전이다. status는 작성 중/고정/실패 상태다. storage_root와 manifest_uri는 파일 위치, manifest_sha256은 파일 목록의 해시다. |
| artifacts | contract_id는 파일 계약에서 온 artifact ID다. relative_path는 묶음 기준 경로, relative_path_key는 Python casefold 결과, storage_uri는 실제 파일 주소다. sha256과 size_bytes는 원본 bytes 기준이다. 파일 크기는 0–8 MiB, media_type은 application/json 또는 text/plain이다. |
| cases | contract_id와 family_id는 입력 JSON의 사례 식별자와 데이터 계열이다. 각 artifact_id는 task, policy, environment, initial state, provenance 등 입력 파일을 가리킨다. changed_axes에는 workflow 및/또는 dependencies를 기록한다. baseline_security_status는 별도 근거가 없으면 UNKNOWN으로 유지한다. |

cases의 입력 참조들은 같은 INPUT bundle 안에 있어야 한다. 이 제약은 잘못된 묶음에서 task를 가져오거나 다른 환경 설정을 섞는 일을 막는다. 의존성 manifest가 없을 수 있으므로 해당 FK만 nullable이다.

`cases.input_bundle_kind`는 INPUT으로 생성되는 제약용 열이며, `(input_bundle_id, input_bundle_kind)` FK가 실제 bundle 유형까지 검사한다. `relative_path_key`는 SQL `lower()`와 같다고 가정하지 않는다. key와 원래 경로의 일치, 예약 이름·경로 이탈·파일/디렉터리 충돌은 입력 검증기가 확인한다.

자격증명 값이나 실사용 비밀을 입력 파일·JSONB에 복사하지 않는다. 자격은 참조 식별자와 별도의 비밀 저장소를 사용한다. 민감한 응답이나 상태 파일은 승인된 보관 위치와 보존 기간을 정한 뒤 저장한다.

### 입력 정규화가 끝났을 때: snapshots, obligations

각 사례에 snapshot 행을 before 하나, after 하나씩 만든다. workflow_artifact_id는 원본 workflow이고 snapshot_artifact_id는 전체 스냅샷 manifest, normalized_artifact_id와 semantics_artifact_id는 입력 단계 산출물이다. 한 case/side는 하나의 불변 snapshot만 가리킨다.

- raw_sha256은 workflow 원본 바이트 해시다.
- structural_sha256은 정규화 구조 해시다.
- semantic_sha256은 선언 설정만 비교한 경우에만 기록한다. 의미 해시 버전과 scope를 같이 기록하고, 미확인 의존성이 있으면 null로 둔다.
- dependency_status는 고정 선언 파일을 모두 읽었는지 표시한다. 완전한 실제 의존성 탐색을 의미하지 않는다.
- dependency_limits는 아직 해석하지 못한 위치와 이유를 보존한다.
- runtime_status와 execution_status는 정적 snapshot 상태와 실제 실행 상태를 구분한다.

`(workflow_artifact_id, raw_sha256)` FK로 등록된 artifact의 해시와 일치시킨다. semantic hash가 있으면 version=`config-v1`, scope=`DECLARED_CONFIGURATION`, dependency_status=`DECLARED_RESOLVED`, 빈 dependency_limits가 필요하다. hash가 없으면 version/scope도 null이다. scope의 명시적인 NOT NULL 검사를 통해 SQL CHECK가 NULL을 통과시키는 경우를 막는다.

obligations는 ComparisonCase의 검증 항목을 한 행씩 보존한다. contract_id는 obligation ID, required는 필수 여부, required_artifact_kinds는 판정에 필요한 자료 종류다. source_policy_rule_id와 source_artifact_id는 규칙의 근거를 찾는 선택 참조다. 분석이나 계획 단계에서 검색에 실패해도 obligation 행을 삭제하거나 생략하지 않는다.

### A가 구조와 변경을 분석할 때: analyses

A가 새로운 분석 결과를 만들면 analyses 행을 추가한다. before_snapshot_id와 after_snapshot_id는 같은 case의 before/after snapshot을 각각 참조해야 한다. 생성 열 before_side/after_side와 복합 FK가 양쪽이 뒤바뀌는 것을 차단한다. analyzer_version과 analyzer_config는 결과를 재현할 코드와 설정이다. analysis_artifact_id는 typed graph, node match, Change, ImpactPath, 미지원 항목, source location이 담긴 JSON 파일을 가리킨다. authorship은 CONTRACT_EXAMPLE, MODULE_OUTPUT 등 산출물의 작성 경계를 기록한다.

동일 ID·동일 원본 bytes의 재저장은 기존 행을 반환한다. 내용이 바뀐 분석에는 새 ID와 artifact를 사용한다. 같은 입력과 코드의 재계산이 같은 ID를 만드는 경우도 있으므로, 실행했다는 이유만으로 새 ID를 강제하지 않는다. 그래프 간선, 변경 목록처럼 큰 자료는 우선 JSON artifact에서 관리한다. DB에서 이를 자주 검색해야 하는 요구가 확인되면 change/path 전용 관계 테이블을 추가한다.

### B가 지식 카드를 검색하고 시험을 만들 때

1. 지식 카드 파일과 출처를 고정해 knowledge_snapshots를 만든다.
2. 각 시나리오 카드를 scenario_cards에 등록한다. 외부 자료는 source artifact, revision, 라이선스와 재사용 상태를 채운다.
3. 각 스냅샷에 포함된 카드를 kb_cards로 연결해 검색에 사용한 KB 구성을 고정한다.
4. 검색을 수행하면 retrievals에 분석 ID, KB ID, 검색 방식, 모델 버전과 질의를 쓴다.
5. 반환된 각 카드는 retrieval_hits에 순위, 점수, 적합성, 이유를 저장한다. 제외 사유는 retrievals.excluded_reasons에 기록한다.
6. template_catalogs와 templates에 실행 가능한 정상 템플릿, 입력 schema, 필수 자료, 허용 효과와 timeout을 버전 단위로 등록한다.
7. B가 plan을 만들면 plans에 normal_input, 선택한 템플릿, 설정과 artifact를 등록한다. plan_obligations에는 사례의 모든 obligation을 BOUND 또는 UNCOVERED로 기록한다.

| 테이블 | 주요 속성의 의미 |
|---|---|
| knowledge_snapshots | manifest_artifact_id와 manifest_sha256으로 카드 집합을 동결한다. embedding_profile에는 사용한 임베딩 설정을 기록한다. |
| scenario_cards | contract_id/version은 카드의 외부 ID와 버전이다. content_sha256은 내용 고정값이다. reuse_status, source_revision, license_identifier는 외부 카드의 사용 근거다. claim_basis는 팀 가설, 작성자 설명, 실행 관측 중 근거 수준이다. |
| kb_cards | knowledge_snapshot_id와 card_id로 카드와 당시 KB를 연결한다. position은 카드 manifest 순서가 필요할 때 쓴다. |
| retrievals | method는 KEYWORD/VECTOR/HYBRID 중 선택한 방법이다. model_version은 벡터/LLM 모델을 쓴 경우 기록한다. query와 excluded_reasons는 검색 입력과 제외 이유다. |
| retrieval_hits | rank는 결과 순위, score는 검색 점수, applicability는 MATCH/PARTIAL/NO_MATCH, reason은 해당 카드가 선택된 근거다. hit 카드는 같은 retrieval의 KB snapshot 안에 있어야 한다. |
| template_catalogs, templates | catalog artifact와 해시가 등록부를 고정한다. template은 task/runtime profile, HTTP 또는 수동 실행 방식, 입력 바인딩, artifact 요구, 허용 효과와 제한 시간을 정의한다. |
| plans | analysis_id, retrieval_id, template_id는 계획의 출처다. normal_input은 실제 실행 입력, attempts_per_side와 timeout_seconds는 시험 반복 수와 제한이다. planner_metadata와 authorship은 생성 방법 및 출처다. |
| plan_obligations | obligation별 binding_status와 required_artifact_kinds를 저장한다. UNCOVERED이면 uncovered_reason이 필수다. |

현재 TestPlan은 하나의 template을 가리킨다. 여러 시험 template을 한 계획에 넣도록 계약이 바뀌면 plan_tests 연결 테이블을 추가한다. 카드 임베딩을 실제 저장할 때는 SQL의 주석 처리된 pgvector 블록을 별도로 활성화한다. 서로 다른 모델 revision이나 차원의 벡터를 한 검색 후보 집합에 섞지 않는다.

KB manifest, 카드 파일, catalog의 해시 필드는 해당 artifact의 원본 bytes 해시와 복합 FK로 일치시킨다. 정규화 JSON의 별도 의미 해시로 대체하지 않는다. 검색 score는 NaN/Infinity를 허용하지 않는다. `retrieval_id IS NULL`은 검색 기록 미공급이며, retrieval 행이 있고 hit가 0건인 검색과 구분한다.

plan_obligations의 UNCOVERED 행은 빈 required_artifact_kinds와 공백이 아닌 uncovered_reason을 가진다. 계약 원본에 개별 사유가 없으면 저장 처리기는 `NOT_SUPPLIED_BY_PRODUCER`처럼 사유 미공급을 명시하며, 추측한 사유를 생산자 진술로 기록하지 않는다. 모든 의무가 정확히 한 번 포함되는지는 저장 처리기의 집합 검사다.

### C가 계획을 실행할 때: jobs, comparison_runs, runs

동기 CLI 실행은 jobs 없이 시작할 수 있다. API가 비동기 worker를 사용할 때만 jobs에 idempotency_key, 상태, lease, heartbeat를 기록한다.

계획을 한 번 실행하는 단위를 comparison_runs로 만든다. attempts_per_side가 2라면 한 comparison_run 아래에 before 2회와 after 2회의 runs를 생성한다. 나중에 같은 계획을 재실행하면 새 comparison_run을 만들어 이전 실행 결과를 보존한다.

각 runs 행에는 실제 실행 side, attempt_number, snapshot, 초기 상태 해시, 런타임 버전/image digest, 단계, 업무 실행 상태, 수집 상태, 정리 상태를 기록한다. execution_status=SUCCEEDED는 업무 요청 실행 결과일 뿐 보안상 통과를 뜻하지 않는다. 컨테이너 정리 실패도 cleanup_status에 별도로 남긴다.

`runs.plan_attempts_per_side`는 선택한 plans.attempts_per_side를 복사한 제약용 열이다. `(plan_id, plan_attempts_per_side)` FK와 attempt_number CHECK가 계획 상한을 넘는 실행 번호를 차단한다. 독립적인 실행 설정으로 수정하지 않는다. 완료 시각이 존재하면 시작 시각보다 앞설 수 없다.

| 테이블 | 주요 속성의 의미 |
|---|---|
| jobs | idempotency_key는 중복 요청을 막는다. status, worker_id, lease_expires_at, heartbeat_at은 비동기 작업 점유와 진행 상태다. CLI에서는 쓰지 않아도 된다. |
| comparison_runs | plan_id와 case_id로 한 차례 전후 비교를 묶는다. job_id는 비동기 요청으로 시작했을 때만 채운다. status는 전체 비교의 진행/부분 완료 상태다. |
| runs | side/attempt_number로 전후 반복 실행을 식별한다. actual_engine_version과 actual_image_digest는 사용한 환경이다. initial_state_sha256으로 시작 상태를 확인한다. phase, execution_status, cleanup_status, collection_status는 각각 단계·업무 실행·정리·증거 수집 상태다. |
| run_artifacts | artifact_kind마다 필요 여부, 수집 상태, 실제 파일 참조를 기록한다. MISSING이면 누락 이유를 적는다. 필요한 자료의 누락을 성공한 수집으로 처리하지 않는다. |
| evidence_events | producer/sequence는 생산자별 이벤트 순서다. observed_at은 관측 시간, ingested_at은 FlowDelta가 받은 시간이다. principal, tenant, resource_id, method, event_outcome은 서비스에서 관찰한 효과다. response_sha256은 응답 무결성 참조다. source_locator로 원본 JSONL의 위치를 찾는다. |

evidence_events.source_kind는 수집기 인증 채널에서 정한 INDEPENDENT_SERVICE 또는 WORKFLOW_LOG 값이다. 워크플로가 보낸 자체 문장을 독립 관측으로 승격하면 안 된다. 이 속성은 현재 0.4.0 EvidenceEvent의 직접 필드가 아니므로, 플랫폼 계약과 DB를 연결할 때는 namespaced extensions 또는 별도 수집 메타데이터로 추가한다.

수집기는 실행 전 기대하는 artifact 종류를 run_artifacts에 PENDING으로 기록하고, 실행 후 실제 파일은 OBSERVED, 받지 못한 자료는 MISSING으로 갱신한다. 상세 이벤트와 응답은 artifact 파일에 남기고 events.jsonl의 순번, 생산자와 시간 정보를 사용한다.

### 독립 판정기를 구현한 뒤: run_checks와 comparison_results

현재 계약은 run outcome을 null로 유지한다. 보안 판정기를 구현한 뒤에만 run_checks를 채운다. run_checks는 개별 실행과 obligation에 대한 PASS, VIOLATION, INCONCLUSIVE, NOT_RUN 판정을 보관한다. check_evidence는 해당 판정이 근거로 사용한 artifact나 event를 연결한다. comparison_results는 before/after 여러 attempts의 결과를 obligation 단위로 집계해 NEW_RISK, EXISTING_RISK, INCREASED_RISK, FIX_VERIFIED, NO_NEW_REGRESSION, INCONCLUSIVE를 기록한다. result_checks는 어떤 개별 판정들이 집계 결과를 만들었는지 남긴다.

판정 입력이나 실행 증거가 빠진 경우 안전으로 간주하지 말고 INCONCLUSIVE로 둔다. 집계 알고리즘을 바꾸면 기존 결과를 갱신하지 말고 evaluator_version을 바꾸어 새 결과를 기록한다.

run_checks.comparison_run_id는 `(run_id, comparison_run_id)` FK로 실행의 비교 회차에 묶인다. result_checks는 양쪽 부모의 `(id, case_id, comparison_run_id, obligation_id, evaluator_version)`을 모두 참조한다. 따라서 같은 case 안의 다른 비교 회차·다른 의무·다른 평가자 버전의 check를 집계에 섞을 수 없다. 이 안은 개별 판정과 집계가 같은 evaluator_version을 사용한다는 정책이다. 서로 다른 판정기와 집계기의 버전을 조합하려면 버전 필드와 호환 규칙을 먼저 별도로 설계한다.

## 삽입 순서 예시

각 테이블의 행은 모듈 결과가 확정될 때 추가한다. 정확한 파일을 먼저 기록해 두면 DB 오류가 나도 산출물에서 인덱스를 다시 만들 수 있다.

| 단계 | 수행 내용 | 작성 테이블 |
|---|---|---|
| 1 | 입력 묶음 생성, manifest/hash 고정 | bundles → artifacts |
| 2 | 전체 입력 계약 검증 후 사례 등록 | cases → obligations |
| 3 | 전후 workflow 정규화와 snapshot 해시 계산 | snapshots |
| 4 | A 분석 artifact 작성과 검증 | analyses |
| 5 | 검색 시 KB/card set 고정 후 결과 저장 | knowledge_snapshots → scenario_cards → kb_cards → retrievals → retrieval_hits |
| 6 | B가 계획을 만들고 obligation 대응 기록 | template_catalogs → templates → plans → plan_obligations |
| 7 | C 실행 요청/전후 반복 실행 생성 | jobs (비동기일 때) → comparison_runs → runs |
| 8 | 자료 수집 결과와 독립 서비스 이벤트 적재 | run_artifacts → evidence_events |
| 9 | 판정기 준비 후 근거에 연결한 평가 기록 | run_checks → check_evidence → comparison_results → result_checks |

DB 행을 만들기 전에 artifact를 임시 파일에 쓰고, 닫고, 해시를 확인한 뒤 최종 경로에 고정한다. 그 다음 artifacts와 도메인 행을 트랜잭션으로 등록한다. DB 등록이 실패해도 고정 파일을 즉시 삭제하지 않는다. 다음 인덱스 복구 과정에서 참조가 없는 파일인지 확인한다.

## 외부 ID와 멱등 저장

이 참조 DB의 한 프로젝트 namespace에서 analyses/retrievals/plans/comparison_runs/runs의 contract_id는 각 테이블 안에서 유일하다. 이에 따라 `get(analysis_id)`, `export(plan_id)`가 한 행을 정한다. 여러 프로젝트를 한 DB에 합칠 때는 project namespace를 키에 명시적으로 포함하는 migration이 필요하다.

cases와 artifacts는 bundle 안에서, obligations는 case 안에서, templates는 catalog 안에서 유일하다. scenario_cards는 `(contract_id, version)`, knowledge_snapshots와 template_catalogs는 `(contract_id, hash)`로 버전을 구분한다. 모든 외부 ID를 무조건 DB 전체 유일성으로 바꾸지는 않는다.

저장 처리기는 다음 순서로 동작한다.

1. 기존 외부 ID가 있으면 연결된 artifact의 hash·크기·원본 bytes와 부모 참조를 확인한다.
2. 동일하면 원래 행을 반환한다. 산출물 원본은 JSONB 재직렬화로 비교하거나 덮어쓰지 않는다.
3. 다르면 충돌로 거부한다. `ON CONFLICT DO UPDATE`로 원본·부모·메타데이터를 교체하지 않는다.
4. 두 writer가 동시에 새 ID를 넣어 UNIQUE 충돌이 나면 해당 트랜잭션을 롤백하고 기존 행을 다시 읽어 위 규칙으로 판정한다.

SEALED bundle의 artifact를 재등록할 때는 INSERT 전에 기존 행을 찾아 비교한다. BEFORE INSERT 트리거는 `ON CONFLICT DO NOTHING`보다 먼저 실행되므로, DO NOTHING만으로 SEALED bundle의 멱등 저장을 구현하지 않는다. runs의 진행 중 상태 갱신은 원본 재저장과 구분한다. 최종 run record를 게시한 뒤의 변경은 아래 저장 처리기 규칙으로 금지한다.

## 게시·불변성·완전성 경계

### DB에서 강제하는 조건

- 새 bundle은 OPEN으로 시작한다. SEALED에는 manifest URI/hash와 sealed_at이 필요하다.
- artifact INSERT/UPDATE/DELETE는 부모 bundle 행을 `FOR UPDATE`로 잠그고 OPEN인지 검사한다. artifact의 id/bundle_id 변경은 금지한다.
- bundle의 SEALED 전이는 같은 부모 행 잠금 아래에서 artifact 1–64건, 메타데이터 크기 합 32 MiB 이하를 검사한다. SEALED/FAILED bundle과 그 artifact 목록은 변경·삭제할 수 없다.
- cases/snapshots/obligations, A/B 불변 산출물과 membership, evidence_events, 미래 판정 기록은 UPDATE/DELETE를 거부한다. 해당 테이블과 bundles/artifacts의 TRUNCATE도 거부한다.
- jobs/comparison_runs/runs/run_artifacts는 기존 실행 수명주기에 따라 갱신할 수 있다. 상태 전이와 최종 게시 후 변경 금지는 저장 처리기의 책임이다.

### 저장 처리기가 보장할 조건

아래 조건은 SQL만으로 보장되지 않는다. 검증된 저장 처리기만 INSERT/UPDATE 권한을 갖도록 구성하며, 임의 클라이언트가 직접 쓰는 운영을 전제로 하지 않는다.

| 대상 | 저장 처리기의 검증 |
|---|---|
| 파일·manifest | 원본 bytes의 hash/size, manifest 전체 파일 목록·참조 일치, 경로 안전성·casefold key·예약 경로·파일/디렉터리 충돌, 계약의 총 크기 제한 |
| case/snapshot | 필수 역할 존재·역할별 파일 구분, 양쪽 snapshot 존재, normalized/semantics와 원본의 대응, 선언된 의존성 및 계약 버전 |
| 불변 부모·자식 | case+obligations+snapshots, KB+카드 membership, catalog+templates, retrieval+hits, plan+전체 의무를 완전한 단위로 한 번에 게시하고 이후 자식만 추가하지 않음 |
| B 계획 | 원본과 열의 일치, case의 모든 의무에 대한 BOUND/UNCOVERED 집합 일치, template/task/profile 적합성, 정상 입력형과 필수 자료 |
| 실행 | plan/case/side/초기 상태/runtime 정보와 run 원본의 일치, 허용된 상태 전이, side별 예정 attempt 전체를 식별 |
| 증거 수집 | plan/template의 필수 kind와 run_artifacts 전체 집합 일치, required/observed/missing과 collection_status 일치, 이벤트 원본 위치·run 연결·인증된 수집 출처 |
| 최종 run 게시 | run 행을 잠근 상태에서 증거를 검증하고 최종 원본 참조와 상태를 함께 확정. 이후 동일 run ID의 원본·관계·증거를 변경하지 않음 |
| 판정 | 채택한 check가 의무에 충분한 근거를 갖는지, 집계 대상 attempt의 누락 처리, evaluator/aggregation 규칙과 원본 일치 |

일반 저장은 READ COMMITTED에서 **부모를 잠금 → 관련 행 읽기·검증 → 삽입/갱신 → 게시 → COMMIT** 순서로 수행한다. bundle은 `SELECT ... FOR UPDATE` 후 artifact를 읽어 manifest와 대조하고, 별도 UPDATE 문으로 SEALED로 전이한다. 여러 부모를 잡으면 UUID 순으로 잠가 순서를 통일한다. 잠금 전에 읽은 결과를 그대로 게시 검증에 사용하지 않는다. REPEATABLE READ/SERIALIZABLE을 채택하면 serialization failure 시 전체 트랜잭션을 다시 수행해야 한다.

bundle 봉인은 파일 목록의 완료만 의미한다. 이것만으로 case/plan의 의무 집합까지 검증됐다고 판단하지 않는다. 불변 행 트리거 역시 나중의 자식 INSERT를 전부 막는 장치는 아니다. run_artifacts/evidence_events를 쓰는 모든 경로도 같은 run 부모 잠금과 최종 게시 상태 검사를 따라야 한다. 여러 독립 writer가 필요해지면 이 프로토콜을 DB 쓰기 함수나 부모별 게시 상태를 이용한 제약으로 확장한다.

행과 자식들을 한 트랜잭션으로 저장하고 검증 실패 시 전체를 롤백한다. 파일은 먼저 고정하므로 DB 실패 시 미참조 파일이 남을 수 있다. 원본 저장소의 파일 자체가 바뀌는 것까지 DB 트리거가 막지는 않으므로 읽기/export에서도 hash와 size를 확인한다. 트리거를 비활성화할 수 있는 소유자·관리자까지 방어하는 불변 저장소로 설명하지 않는다.

이 불변성 정책은 일반 DML 삭제도 막는다. 보존 기간·삭제 요구를 적용할 때는 관계 순서, 권한, 감사 기록과 백업을 포함한 별도의 관리자 유지보수 절차를 정해야 한다.

## 조회 인덱스

PK/UNIQUE가 이미 제공하는 인덱스를 활용하고, 참조하는 FK와 주요 조회 경로에 보조 인덱스를 추가했다.

- family → cases, case → analyses/plans
- analysis/KB → retrievals, KB/card → retrieval_hits
- plan → comparison_runs/runs, snapshot → runs
- run → artifacts/events/checks, check → evidence/result 연결
- artifact → 해당 원본을 참조하는 domain 행

이 인덱스는 조회 경로를 위한 초기안이다. 실제 건수와 실행 계획으로 조정하며, 성능 개선을 측정했다는 의미는 아니다. 전문검색·GIN·partition은 이번 변경에 포함하지 않는다.

## 제약과 구현 경계

- cases의 업무, 정책, 환경, 초기 상태, 출처는 같은 입력 bundle에 있어야 한다.
- snapshot은 case당 before/after 각 하나이며 수정하지 않는다. 새 분석은 새 analyses 행을 만든다.
- semantic hash는 DECLARED_CONFIGURATION 범위다. 전체 행동이 같거나 숨은 의존성까지 발견했다는 증명이 아니다.
- retrieval hit는 검색 당시 KB에 실제 포함된 카드여야 한다. KB manifest와 해시를 고정한다.
- plans의 before/after snapshot과 초기 상태는 연결된 analysis/case와 동일한지 검사한다.
- 각 plan은 case의 모든 obligation에 대응하는 plan_obligations 행을 가져야 한다.
- run attempt은 side별로 별도 ID를 사용하고, 실행마다 독립 초기 상태에서 출발한다.
- 업무 실행 성공, 증거 수집 완료, 보안 판정 완료는 서로 다른 상태로 보존한다.
- 상세 그래프, request/response, 상태 전후, 오류, 이벤트 본문은 파일에 둘 수 있다. DB 컬럼에는 참조, 해시와 조회에 필요한 최소 metadata를 둔다.
- 원본에 자격증명 값이 포함되면 artifact로 복사하지 않는다. 비밀은 외부 secret manager 참조로 관리한다.
- assessment 테이블과 vector 테이블은 해당 기능이 구현되기 전에는 운영 테이블로 취급하지 않는다.

## 적용 전에 확인할 사항

이 DDL은 참조 스키마다. 실제 적용 전에는 다음을 프로젝트에서 확정해야 한다.

1. 여러 사람이 공유하는 서버를 만들지, CLI와 로컬 artifact 중심으로 둘지.
2. 원본 입력과 결과 파일을 어디에 보관하고 누가 열람할지.
3. SQL과 Pydantic 계약에서 enum/version 값을 어디서 관리할지.
4. 위 저장 처리기의 다중 행 검증·잠금·멱등 처리·최종 게시 규칙을 구현하고, 직접 쓰기 권한을 제한할 방법.
5. 비동기 API와 jobs가 현재 캡스톤 범위에 들어가는지.
6. 보안 판정 기준과 평가자 데이터의 접근 경계를 어떻게 둘지.

현재 저장 형태와 런타임 제한은 [current-readiness.md](current-readiness.md), 전체 입력·시험 설계는 [final/README.md](../final/README.md) 및 [platform 입력 계약 0.4.0](https://github.com/serendipity-sec/platform/blob/main/docs/INPUT_CONTRACT_04.md)에서 확인한다.

### 적용 범위와 확인 상태

core, 선택적 job, 이벤트 조회, 미래 판정, vector index는 실제 도입 시 단계별 migration으로 나눈다. SQL의 pgvector 384차원 블록은 예시이며 현재 플랫폼의 기본값이라는 뜻이 아니다. 실제 provider/model/revision/dimensions를 확정하고 맞춘 뒤 활성화한다.

2026-10-27 보강은 참조 SQL과 설명 문서 수정이다. 운영 DB에 적용하지 않았고 DDL 실행·회귀·동시성 테스트를 수행하지 않았다. 실제 migration으로 채택할 때는 기존 데이터의 ID 중복·관계 충돌을 확인하고 신규 필드를 채운 뒤 제약을 검증해야 한다. 특히 봉인/삽입 경쟁과 최종 run 게시 시 증거 쓰기 경쟁은 실제 DB에서 확인해야 한다.

참고한 PostgreSQL 17 공식 문서(확인일: 2026-10-27):

- [Constraints](https://www.postgresql.org/docs/17/ddl-constraints.html): FK·UNIQUE·CHECK와 NULL 처리, FK 참조 측 인덱스.
- [Explicit Locking](https://www.postgresql.org/docs/17/explicit-locking.html): 행 잠금의 충돌과 획득 순서.
- [Overview of Trigger Behavior](https://www.postgresql.org/docs/17/trigger-definition.html): 행/문장 트리거와 INSERT 충돌 처리 시점.
