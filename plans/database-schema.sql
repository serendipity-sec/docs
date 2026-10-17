-- FlowDelta PostgreSQL schema proposal
-- Aligned with the platform input and pipeline contracts 0.4.0.
-- Reference schema for possible future shared persistence; it does not mean
-- PostgreSQL is part of the current local-first MVP.
-- Store large immutable source/output files in an artifact store. Store paths,
-- hashes, sizes, and queryable metadata in these tables.
-- Apply through ordered Alembic migrations if implementation is approved.

-- 1. Bundles and immutable artifacts

CREATE TABLE bundles (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    kind                text NOT NULL
                        CHECK (kind IN ('INPUT', 'MODULE_OUTPUT', 'RUN_OUTPUT')),
    schema_version      text NOT NULL,
    status              text NOT NULL DEFAULT 'OPEN'
                        CHECK (status IN ('OPEN', 'SEALED', 'FAILED')),
    storage_root        text NOT NULL,
    manifest_uri        text,
    manifest_sha256     varchar(64)
                        CHECK (manifest_sha256 IS NULL
                               OR manifest_sha256 ~ '^[0-9a-f]{64}$'),
    created_at          timestamptz NOT NULL DEFAULT now(),
    sealed_at           timestamptz,
    CHECK ((status = 'SEALED') = (sealed_at IS NOT NULL))
);

CREATE TABLE artifacts (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    bundle_id           uuid NOT NULL REFERENCES bundles(id),
    contract_id         text NOT NULL,
    relative_path       text NOT NULL,
    storage_uri         text NOT NULL,
    sha256              varchar(64) NOT NULL
                        CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    size_bytes          bigint NOT NULL CHECK (size_bytes >= 0),
    media_type          text NOT NULL,
    kind                text NOT NULL CHECK (kind IN ('source', 'generated')),
    created_at          timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, bundle_id),
    UNIQUE (bundle_id, contract_id)
);

CREATE UNIQUE INDEX artifacts_bundle_path_ci
    ON artifacts (bundle_id, lower(relative_path));


-- 2. Input case, fixed comparison context, and snapshots

CREATE TABLE cases (
    id                              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    input_bundle_id                 uuid NOT NULL REFERENCES bundles(id),
    contract_id                     text NOT NULL,
    family_id                       text NOT NULL,
    case_artifact_id                uuid NOT NULL,
    task_artifact_id                uuid NOT NULL,
    policy_artifact_id              uuid NOT NULL,
    environment_artifact_id         uuid NOT NULL,
    initial_state_artifact_id       uuid NOT NULL,
    provenance_artifact_id          uuid NOT NULL,
    dependency_manifest_artifact_id uuid,
    changed_axes                    text[] NOT NULL
                                    CHECK (
                                        cardinality(changed_axes) BETWEEN 1 AND 2
                                        AND changed_axes <@ ARRAY[
                                            'workflow',
                                            'dependencies'
                                        ]::text[]
                                    ),
    baseline_security_status        text NOT NULL DEFAULT 'UNKNOWN'
                                    CHECK (baseline_security_status = 'UNKNOWN'),
    schema_version                  text NOT NULL,
    created_at                      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (input_bundle_id, contract_id),
    UNIQUE (id, input_bundle_id),
    UNIQUE (id, initial_state_artifact_id),
    FOREIGN KEY (case_artifact_id, input_bundle_id)
        REFERENCES artifacts (id, bundle_id),
    FOREIGN KEY (task_artifact_id, input_bundle_id)
        REFERENCES artifacts (id, bundle_id),
    FOREIGN KEY (policy_artifact_id, input_bundle_id)
        REFERENCES artifacts (id, bundle_id),
    FOREIGN KEY (environment_artifact_id, input_bundle_id)
        REFERENCES artifacts (id, bundle_id),
    FOREIGN KEY (initial_state_artifact_id, input_bundle_id)
        REFERENCES artifacts (id, bundle_id),
    FOREIGN KEY (provenance_artifact_id, input_bundle_id)
        REFERENCES artifacts (id, bundle_id),
    FOREIGN KEY (dependency_manifest_artifact_id, input_bundle_id)
        REFERENCES artifacts (id, bundle_id)
);

CREATE TABLE snapshots (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id                 uuid NOT NULL REFERENCES cases(id),
    contract_id             text NOT NULL,
    side                    text NOT NULL CHECK (side IN ('before', 'after')),
    workflow_artifact_id    uuid NOT NULL REFERENCES artifacts(id),
    snapshot_artifact_id    uuid NOT NULL REFERENCES artifacts(id),
    normalized_artifact_id  uuid NOT NULL REFERENCES artifacts(id),
    semantics_artifact_id   uuid NOT NULL REFERENCES artifacts(id),
    raw_sha256              varchar(64) NOT NULL
                            CHECK (raw_sha256 ~ '^[0-9a-f]{64}$'),
    structural_sha256       varchar(64) NOT NULL
                            CHECK (structural_sha256 ~ '^[0-9a-f]{64}$'),
    semantic_sha256         varchar(64)
                            CHECK (semantic_sha256 IS NULL
                                   OR semantic_sha256 ~ '^[0-9a-f]{64}$'),
    semantic_hash_version   text,
    semantic_hash_scope     text,
    dependency_status       text NOT NULL
                            CHECK (dependency_status IN (
                                'UNRESOLVED',
                                'DECLARED_RESOLVED'
                            )),
    dependency_limits       jsonb NOT NULL DEFAULT '[]'::jsonb
                            CHECK (jsonb_typeof(dependency_limits) = 'array'),
    runtime_status          text NOT NULL DEFAULT 'NOT_VALIDATED',
    execution_status        text NOT NULL DEFAULT 'NOT_RUN',
    created_at              timestamptz NOT NULL DEFAULT now(),
    UNIQUE (case_id, side),
    UNIQUE (id, case_id),
    UNIQUE (id, case_id, side),
    CHECK (
        (
            semantic_sha256 IS NULL
            AND semantic_hash_version IS NULL
            AND semantic_hash_scope IS NULL
        )
        OR
        (
            semantic_sha256 IS NOT NULL
            AND semantic_hash_version IS NOT NULL
            AND semantic_hash_scope = 'DECLARED_CONFIGURATION'
            AND dependency_status = 'DECLARED_RESOLVED'
            AND dependency_limits = '[]'::jsonb
        )
    )
);

CREATE TABLE obligations (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id                 uuid NOT NULL REFERENCES cases(id),
    contract_id             text NOT NULL,
    required                boolean NOT NULL,
    description             text NOT NULL,
    required_artifact_kinds jsonb NOT NULL DEFAULT '[]'::jsonb
                            CHECK (jsonb_typeof(required_artifact_kinds) = 'array'),
    source_policy_rule_id   text,
    source_artifact_id      uuid REFERENCES artifacts(id),
    UNIQUE (case_id, contract_id),
    UNIQUE (id, case_id)
);


-- 3. A: immutable analysis record; detailed graph/change data stays in artifact

CREATE TABLE analyses (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id                 uuid NOT NULL REFERENCES cases(id),
    contract_id             text NOT NULL,
    before_snapshot_id      uuid NOT NULL,
    after_snapshot_id       uuid NOT NULL,
    analysis_artifact_id    uuid NOT NULL REFERENCES artifacts(id),
    analyzer_version        text NOT NULL,
    analyzer_config         jsonb NOT NULL DEFAULT '{}'::jsonb,
    authorship              jsonb NOT NULL,
    limitations             jsonb NOT NULL DEFAULT '[]'::jsonb
                            CHECK (jsonb_typeof(limitations) = 'array'),
    created_at              timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, case_id),
    UNIQUE (id, case_id, before_snapshot_id, after_snapshot_id),
    FOREIGN KEY (before_snapshot_id, case_id)
        REFERENCES snapshots (id, case_id),
    FOREIGN KEY (after_snapshot_id, case_id)
        REFERENCES snapshots (id, case_id),
    CHECK (before_snapshot_id <> after_snapshot_id)
);


-- 4. B: frozen knowledge, retrieval trace, and versioned execution templates

CREATE TABLE knowledge_snapshots (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id             text NOT NULL,
    manifest_artifact_id    uuid NOT NULL REFERENCES artifacts(id),
    manifest_sha256         varchar(64) NOT NULL
                            CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    embedding_profile       jsonb,
    created_at              timestamptz NOT NULL DEFAULT now(),
    UNIQUE (contract_id, manifest_sha256)
);

CREATE TABLE scenario_cards (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id             text NOT NULL,
    version                 text NOT NULL,
    card_artifact_id        uuid NOT NULL REFERENCES artifacts(id),
    source_artifact_id      uuid REFERENCES artifacts(id),
    content_sha256          varchar(64) NOT NULL
                            CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    title                   text NOT NULL,
    summary                 text NOT NULL,
    source                  text NOT NULL,
    source_revision         text,
    reuse_status            text NOT NULL
                            CHECK (reuse_status IN (
                                'TEAM_AUTHORED',
                                'LICENSED_PUBLIC',
                                'CONSENTED'
                            )),
    license_identifier      text,
    claim_basis             text NOT NULL
                            CHECK (claim_basis IN (
                                'TEAM_HYPOTHESIS',
                                'AUTHOR_DESCRIPTION',
                                'EXPERIMENTALLY_OBSERVED'
                            )),
    authorship              jsonb NOT NULL,
    runtime_profile         text NOT NULL,
    node_types              jsonb NOT NULL DEFAULT '[]'::jsonb
                            CHECK (jsonb_typeof(node_types) = 'array'),
    template_contract_id    text NOT NULL,
    template_version        text NOT NULL,
    required_artifact_kinds jsonb NOT NULL DEFAULT '[]'::jsonb
                            CHECK (jsonb_typeof(required_artifact_kinds) = 'array'),
    UNIQUE (contract_id, version),
    CHECK (
        reuse_status = 'TEAM_AUTHORED'
        OR (
            source_artifact_id IS NOT NULL
            AND source_revision IS NOT NULL
            AND license_identifier IS NOT NULL
        )
    )
);

CREATE TABLE kb_cards (
    knowledge_snapshot_id   uuid NOT NULL REFERENCES knowledge_snapshots(id),
    card_id                 uuid NOT NULL REFERENCES scenario_cards(id),
    position                integer NOT NULL CHECK (position >= 0),
    PRIMARY KEY (knowledge_snapshot_id, card_id),
    UNIQUE (knowledge_snapshot_id, position)
);

CREATE TABLE retrievals (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id             text NOT NULL,
    analysis_id             uuid NOT NULL REFERENCES analyses(id),
    knowledge_snapshot_id   uuid NOT NULL REFERENCES knowledge_snapshots(id),
    retrieval_artifact_id   uuid NOT NULL REFERENCES artifacts(id),
    method                  text NOT NULL
                            CHECK (method IN ('KEYWORD', 'VECTOR', 'HYBRID')),
    model_version           text,
    query                   jsonb NOT NULL,
    excluded_reasons        jsonb NOT NULL DEFAULT '{}'::jsonb,
    authorship              jsonb NOT NULL,
    created_at              timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, analysis_id),
    UNIQUE (id, knowledge_snapshot_id)
);

CREATE TABLE retrieval_hits (
    retrieval_id            uuid NOT NULL,
    knowledge_snapshot_id   uuid NOT NULL,
    card_id                 uuid NOT NULL REFERENCES scenario_cards(id),
    rank                    integer NOT NULL CHECK (rank >= 1),
    score                   double precision NOT NULL,
    applicability           text NOT NULL
                            CHECK (applicability IN ('MATCH', 'PARTIAL', 'NO_MATCH')),
    reason                  text NOT NULL,
    PRIMARY KEY (retrieval_id, card_id),
    UNIQUE (retrieval_id, rank),
    FOREIGN KEY (retrieval_id, knowledge_snapshot_id)
        REFERENCES retrievals (id, knowledge_snapshot_id),
    FOREIGN KEY (knowledge_snapshot_id, card_id)
        REFERENCES kb_cards (knowledge_snapshot_id, card_id)
);

CREATE TABLE template_catalogs (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id             text NOT NULL,
    catalog_artifact_id     uuid NOT NULL REFERENCES artifacts(id),
    content_sha256          varchar(64) NOT NULL
                            CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    authorship              jsonb NOT NULL,
    created_at              timestamptz NOT NULL DEFAULT now(),
    UNIQUE (contract_id, content_sha256)
);

CREATE TABLE templates (
    id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    catalog_id                  uuid NOT NULL REFERENCES template_catalogs(id),
    contract_id                 text NOT NULL,
    version                     text NOT NULL,
    task_contract_id            text NOT NULL,
    runtime_profile             text NOT NULL,
    mode                        text NOT NULL
                                CHECK (mode IN (
                                    'NORMAL_BUSINESS_REQUEST',
                                    'NORMAL_MANUAL_WORKFLOW'
                                )),
    method                      text
                                CHECK (method IS NULL OR method IN ('GET', 'POST')),
    webhook_path                text,
    materialized_input_bindings jsonb NOT NULL DEFAULT '[]'::jsonb,
    input_fields                jsonb NOT NULL,
    required_artifact_kinds     jsonb NOT NULL DEFAULT '[]'::jsonb,
    allowed_effects             jsonb NOT NULL DEFAULT '[]'::jsonb,
    timeout_seconds             integer NOT NULL
                                CHECK (timeout_seconds BETWEEN 1 AND 300),
    UNIQUE (catalog_id, contract_id, version),
    CHECK (
        (
            mode = 'NORMAL_MANUAL_WORKFLOW'
            AND method IS NULL
            AND webhook_path IS NULL
        )
        OR
        (
            mode = 'NORMAL_BUSINESS_REQUEST'
            AND method IS NOT NULL
            AND webhook_path IS NOT NULL
        )
    )
);

CREATE TABLE plans (
    id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id                     uuid NOT NULL REFERENCES cases(id),
    contract_id                 text NOT NULL,
    analysis_id                 uuid NOT NULL,
    retrieval_id                uuid,
    before_snapshot_id          uuid NOT NULL,
    after_snapshot_id           uuid NOT NULL,
    template_id                 uuid NOT NULL REFERENCES templates(id),
    plan_artifact_id            uuid NOT NULL REFERENCES artifacts(id),
    initial_state_artifact_id   uuid NOT NULL REFERENCES artifacts(id),
    normal_input                jsonb NOT NULL,
    planner_metadata            jsonb NOT NULL DEFAULT '{}'::jsonb,
    attempts_per_side           integer NOT NULL
                                CHECK (attempts_per_side BETWEEN 1 AND 10),
    timeout_seconds             integer NOT NULL
                                CHECK (timeout_seconds BETWEEN 1 AND 300),
    authorship                  jsonb NOT NULL,
    created_at                  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, case_id),
    FOREIGN KEY (
        analysis_id,
        case_id,
        before_snapshot_id,
        after_snapshot_id
    ) REFERENCES analyses (
        id,
        case_id,
        before_snapshot_id,
        after_snapshot_id
    ),
    FOREIGN KEY (retrieval_id, analysis_id)
        REFERENCES retrievals (id, analysis_id),
    FOREIGN KEY (case_id, initial_state_artifact_id)
        REFERENCES cases (id, initial_state_artifact_id)
);

CREATE TABLE plan_obligations (
    plan_id                 uuid NOT NULL,
    case_id                 uuid NOT NULL,
    obligation_id           uuid NOT NULL,
    binding_status          text NOT NULL
                            CHECK (binding_status IN ('BOUND', 'UNCOVERED')),
    required_artifact_kinds jsonb NOT NULL DEFAULT '[]'::jsonb,
    uncovered_reason        text,
    PRIMARY KEY (plan_id, obligation_id),
    FOREIGN KEY (plan_id, case_id)
        REFERENCES plans (id, case_id),
    FOREIGN KEY (obligation_id, case_id)
        REFERENCES obligations (id, case_id),
    CHECK (
        binding_status <> 'UNCOVERED'
        OR uncovered_reason IS NOT NULL
    )
);


-- 5. C: optional async job, paired execution group, individual attempts, evidence

CREATE TABLE jobs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id             uuid NOT NULL REFERENCES plans(id),
    request_artifact_id uuid REFERENCES artifacts(id),
    idempotency_key     text NOT NULL UNIQUE,
    status              text NOT NULL
                        CHECK (status IN (
                            'QUEUED',
                            'CLAIMED',
                            'RUNNING',
                            'SUCCEEDED',
                            'FAILED',
                            'CANCELLED'
                        )),
    worker_id           text,
    lease_expires_at    timestamptz,
    heartbeat_at        timestamptz,
    requested_at        timestamptz NOT NULL DEFAULT now(),
    finished_at         timestamptz,
    error_code          text,
    UNIQUE (id, plan_id)
);

CREATE TABLE comparison_runs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id         text NOT NULL,
    plan_id             uuid NOT NULL,
    case_id             uuid NOT NULL,
    job_id              uuid,
    status              text NOT NULL
                        CHECK (status IN (
                            'QUEUED',
                            'RUNNING',
                            'FINISHED',
                            'PARTIAL',
                            'FAILED',
                            'CANCELLED'
                        )),
    created_at          timestamptz NOT NULL DEFAULT now(),
    started_at          timestamptz,
    finished_at         timestamptz,
    UNIQUE (id, case_id),
    UNIQUE (id, plan_id, case_id),
    UNIQUE (job_id),
    FOREIGN KEY (plan_id, case_id)
        REFERENCES plans (id, case_id),
    FOREIGN KEY (job_id, plan_id)
        REFERENCES jobs (id, plan_id)
);

CREATE TABLE runs (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id             text NOT NULL,
    comparison_run_id       uuid NOT NULL,
    plan_id                 uuid NOT NULL,
    case_id                 uuid NOT NULL,
    snapshot_id             uuid NOT NULL,
    side                    text NOT NULL CHECK (side IN ('before', 'after')),
    attempt_number          integer NOT NULL CHECK (attempt_number >= 1),
    run_record_artifact_id  uuid REFERENCES artifacts(id),
    runtime_profile         text NOT NULL,
    actual_engine_version   text,
    actual_image_digest     text,
    initial_state_sha256    varchar(64) NOT NULL
                            CHECK (initial_state_sha256 ~ '^[0-9a-f]{64}$'),
    phase                   text NOT NULL
                            CHECK (phase IN (
                                'QUEUED',
                                'PREPARING',
                                'READY',
                                'RUNNING',
                                'COLLECTING',
                                'FINALIZING',
                                'FINISHED'
                            )),
    execution_status        text NOT NULL
                            CHECK (execution_status IN (
                                'NOT_RUN',
                                'SUCCEEDED',
                                'FAILED',
                                'TIMED_OUT',
                                'CANCELLED',
                                'INTERRUPTED'
                            )),
    cleanup_status          text NOT NULL
                            CHECK (cleanup_status IN ('PENDING', 'COMPLETE', 'FAILED')),
    collection_status       text NOT NULL
                            CHECK (collection_status IN (
                                'NOT_STARTED',
                                'PARTIAL',
                                'COMPLETE'
                            )),
    started_at              timestamptz,
    finished_at             timestamptz,
    error_code              text,
    error_details           jsonb,
    usage                   jsonb,
    authorship              jsonb NOT NULL,
    UNIQUE (comparison_run_id, side, attempt_number),
    UNIQUE (id, case_id),
    UNIQUE (id, comparison_run_id),
    FOREIGN KEY (comparison_run_id, plan_id, case_id)
        REFERENCES comparison_runs (id, plan_id, case_id),
    FOREIGN KEY (snapshot_id, case_id, side)
        REFERENCES snapshots (id, case_id, side),
    CHECK (
        execution_status <> 'SUCCEEDED'
        OR (
            actual_engine_version IS NOT NULL
            AND actual_image_digest IS NOT NULL
            AND started_at IS NOT NULL
        )
    ),
    CHECK (phase <> 'FINISHED' OR finished_at IS NOT NULL)
);

CREATE TABLE run_artifacts (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              uuid NOT NULL REFERENCES runs(id),
    artifact_id         uuid REFERENCES artifacts(id),
    artifact_kind       text NOT NULL,
    required            boolean NOT NULL,
    collection_state    text NOT NULL
                        CHECK (collection_state IN ('PENDING', 'OBSERVED', 'MISSING')),
    missing_reason      text,
    collected_at        timestamptz,
    UNIQUE (run_id, artifact_kind),
    UNIQUE (id, run_id),
    CHECK (
        (collection_state = 'OBSERVED' AND artifact_id IS NOT NULL)
        OR
        (collection_state IN ('PENDING', 'MISSING') AND artifact_id IS NULL)
    ),
    CHECK (
        collection_state <> 'MISSING'
        OR missing_reason IS NOT NULL
    )
);

CREATE TABLE evidence_events (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              uuid NOT NULL REFERENCES runs(id),
    source_artifact_id  uuid NOT NULL REFERENCES artifacts(id),
    producer            text NOT NULL,
    source_kind         text NOT NULL
                        CHECK (source_kind IN (
                            'INDEPENDENT_SERVICE',
                            'WORKFLOW_LOG'
                        )),
    sequence            integer NOT NULL CHECK (sequence > 0),
    observed_at         timestamptz NOT NULL,
    ingested_at         timestamptz NOT NULL DEFAULT now(),
    event_type          text NOT NULL,
    principal           text NOT NULL,
    tenant              text NOT NULL,
    resource_id         text NOT NULL,
    method              text
                        CHECK (method IS NULL OR method IN (
                            'GET', 'POST', 'PUT', 'PATCH',
                            'DELETE', 'HEAD', 'OPTIONS'
                        )),
    event_outcome       text NOT NULL,
    response_sha256     varchar(64) NOT NULL
                        CHECK (response_sha256 ~ '^[0-9a-f]{64}$'),
    attempt_number      integer NOT NULL DEFAULT 1 CHECK (attempt_number >= 1),
    execution_id        text,
    node_id             text,
    node_run_index      integer CHECK (node_run_index IS NULL OR node_run_index >= 0),
    item_index          integer CHECK (item_index IS NULL OR item_index >= 0),
    attributes          jsonb NOT NULL DEFAULT '{}'::jsonb,
    source_locator      jsonb NOT NULL,
    UNIQUE (run_id, producer, sequence),
    UNIQUE (id, run_id)
);


-- 6. Future extension: independent security evaluation.
-- The current 0.4.0 ExecutionRun contract keeps security outcome null.

CREATE TABLE run_checks (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              uuid NOT NULL,
    case_id             uuid NOT NULL,
    obligation_id       uuid NOT NULL,
    evaluator_version   text NOT NULL,
    verdict             text NOT NULL
                        CHECK (verdict IN (
                            'PASS',
                            'VIOLATION',
                            'INCONCLUSIVE',
                            'NOT_RUN'
                        )),
    reason              text NOT NULL,
    details_artifact_id uuid REFERENCES artifacts(id),
    created_at          timestamptz NOT NULL DEFAULT now(),
    UNIQUE (run_id, obligation_id, evaluator_version),
    UNIQUE (id, run_id),
    UNIQUE (id, case_id),
    FOREIGN KEY (run_id, case_id)
        REFERENCES runs (id, case_id),
    FOREIGN KEY (obligation_id, case_id)
        REFERENCES obligations (id, case_id)
);

CREATE TABLE check_evidence (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_check_id        uuid NOT NULL,
    run_id              uuid NOT NULL,
    run_artifact_id     uuid,
    evidence_event_id   uuid,
    evidence_role       text NOT NULL,
    FOREIGN KEY (run_check_id, run_id)
        REFERENCES run_checks (id, run_id),
    FOREIGN KEY (run_artifact_id, run_id)
        REFERENCES run_artifacts (id, run_id),
    FOREIGN KEY (evidence_event_id, run_id)
        REFERENCES evidence_events (id, run_id),
    CHECK (
        run_artifact_id IS NOT NULL
        OR evidence_event_id IS NOT NULL
    )
);

CREATE TABLE comparison_results (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    comparison_run_id       uuid NOT NULL,
    case_id                 uuid NOT NULL,
    obligation_id           uuid NOT NULL,
    evaluator_version       text NOT NULL,
    classification          text NOT NULL
                            CHECK (classification IN (
                                'NEW_RISK',
                                'EXISTING_RISK',
                                'INCREASED_RISK',
                                'FIX_VERIFIED',
                                'NO_NEW_REGRESSION',
                                'INCONCLUSIVE'
                            )),
    aggregation_method      text NOT NULL,
    reason                  text NOT NULL,
    created_at              timestamptz NOT NULL DEFAULT now(),
    UNIQUE (comparison_run_id, obligation_id, evaluator_version),
    UNIQUE (id, case_id),
    FOREIGN KEY (comparison_run_id, case_id)
        REFERENCES comparison_runs (id, case_id),
    FOREIGN KEY (obligation_id, case_id)
        REFERENCES obligations (id, case_id)
);

CREATE TABLE result_checks (
    comparison_result_id    uuid NOT NULL,
    run_check_id            uuid NOT NULL,
    case_id                 uuid NOT NULL,
    PRIMARY KEY (comparison_result_id, run_check_id),
    FOREIGN KEY (comparison_result_id, case_id)
        REFERENCES comparison_results (id, case_id),
    FOREIGN KEY (run_check_id, case_id)
        REFERENCES run_checks (id, case_id)
);


-- Optional, when pgvector is installed and embedding retrieval is implemented:
-- CREATE EXTENSION IF NOT EXISTS vector;
--
-- CREATE TABLE card_embeddings (
--     knowledge_snapshot_id uuid NOT NULL,
--     card_id               uuid NOT NULL,
--     chunk_id              text NOT NULL,
--     chunk_sha256          varchar(64) NOT NULL
--                           CHECK (chunk_sha256 ~ '^[0-9a-f]{64}$'),
--     model_name            text NOT NULL,
--     model_revision        text NOT NULL,
--     dimensions            integer NOT NULL CHECK (dimensions = 384),
--     embedding             vector(384) NOT NULL,
--     created_at            timestamptz NOT NULL DEFAULT now(),
--     PRIMARY KEY (
--         knowledge_snapshot_id,
--         card_id,
--         chunk_id,
--         model_revision
--     ),
--     FOREIGN KEY (knowledge_snapshot_id, card_id)
--         REFERENCES kb_cards (knowledge_snapshot_id, card_id)
-- );
