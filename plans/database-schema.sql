-- FlowDelta PostgreSQL schema proposal
-- Aligned with the platform input and pipeline contracts 0.4.0.
-- Reference schema for possible future shared persistence; it does not mean
-- PostgreSQL is part of the current local-first MVP.
-- Store large immutable source/output files in an artifact store. Store paths,
-- hashes, sizes, and queryable metadata in these tables.
-- Apply through ordered Alembic migrations if implementation is approved.
-- This remains a reference DDL, not an upgrade script for an existing database.
-- File bytes, manifest equality and aggregate completeness are importer checks;
-- see database-schema.md for transaction and publication boundaries.

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
    CHECK ((status = 'SEALED') = (sealed_at IS NOT NULL)),
    CHECK (status <> 'SEALED' OR (
        manifest_uri IS NOT NULL AND length(btrim(manifest_uri)) > 0
        AND manifest_sha256 IS NOT NULL
    )),
    UNIQUE (id, kind)
);

CREATE TABLE artifacts (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    bundle_id           uuid NOT NULL REFERENCES bundles(id),
    contract_id         text NOT NULL,
    relative_path       text NOT NULL CHECK (length(relative_path) BETWEEN 1 AND 512),
    -- The validated importer supplies Python str.casefold(); SQL lower() differs.
    relative_path_key   text NOT NULL CHECK (length(relative_path_key) > 0),
    storage_uri         text NOT NULL,
    sha256              varchar(64) NOT NULL
                        CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    size_bytes          bigint NOT NULL CHECK (size_bytes BETWEEN 0 AND 8388608),
    media_type          text NOT NULL CHECK (media_type IN ('application/json', 'text/plain')),
    kind                text NOT NULL CHECK (kind IN ('source', 'generated')),
    created_at          timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, bundle_id),
    UNIQUE (id, sha256),
    UNIQUE (bundle_id, contract_id)
);

CREATE UNIQUE INDEX artifacts_bundle_path_ci
    ON artifacts (bundle_id, relative_path_key);


-- 2. Input case, fixed comparison context, and snapshots

CREATE TABLE cases (
    id                              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    input_bundle_id                 uuid NOT NULL REFERENCES bundles(id),
    input_bundle_kind               text GENERATED ALWAYS AS ('INPUT'::text) STORED,
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
                                        changed_axes IN (
                                            ARRAY['workflow'], ARRAY['dependencies'],
                                            ARRAY['workflow', 'dependencies'],
                                            ARRAY['dependencies', 'workflow']
                                        )
                                    ),
    baseline_security_status        text NOT NULL DEFAULT 'UNKNOWN'
                                    CHECK (baseline_security_status = 'UNKNOWN'),
    schema_version                  text NOT NULL,
    created_at                      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (input_bundle_id, contract_id),
    UNIQUE (id, input_bundle_id),
    UNIQUE (id, initial_state_artifact_id),
    FOREIGN KEY (input_bundle_id, input_bundle_kind)
        REFERENCES bundles (id, kind),
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
    runtime_status          text NOT NULL DEFAULT 'NOT_VALIDATED'
                            CHECK (runtime_status = 'NOT_VALIDATED'),
    execution_status        text NOT NULL DEFAULT 'NOT_RUN'
                            CHECK (execution_status = 'NOT_RUN'),
    created_at              timestamptz NOT NULL DEFAULT now(),
    UNIQUE (case_id, side),
    UNIQUE (id, case_id),
    UNIQUE (id, case_id, side),
    FOREIGN KEY (workflow_artifact_id, raw_sha256)
        REFERENCES artifacts (id, sha256),
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
            AND semantic_hash_version = 'config-v1'
            AND semantic_hash_scope IS NOT NULL
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
    contract_id             text NOT NULL UNIQUE CHECK (length(btrim(contract_id)) > 0),
    before_snapshot_id      uuid NOT NULL,
    after_snapshot_id       uuid NOT NULL,
    before_side             text GENERATED ALWAYS AS ('before'::text) STORED,
    after_side              text GENERATED ALWAYS AS ('after'::text) STORED,
    analysis_artifact_id    uuid NOT NULL REFERENCES artifacts(id),
    analyzer_version        text NOT NULL,
    analyzer_config         jsonb NOT NULL DEFAULT '{}'::jsonb
                            CHECK (jsonb_typeof(analyzer_config) = 'object'),
    authorship              jsonb NOT NULL,
    limitations             jsonb NOT NULL DEFAULT '[]'::jsonb
                            CHECK (jsonb_typeof(limitations) = 'array'),
    created_at              timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, case_id),
    UNIQUE (id, case_id, before_snapshot_id, after_snapshot_id),
    FOREIGN KEY (before_snapshot_id, case_id, before_side)
        REFERENCES snapshots (id, case_id, side),
    FOREIGN KEY (after_snapshot_id, case_id, after_side)
        REFERENCES snapshots (id, case_id, side),
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
    UNIQUE (contract_id, manifest_sha256),
    FOREIGN KEY (manifest_artifact_id, manifest_sha256)
        REFERENCES artifacts (id, sha256)
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
    FOREIGN KEY (card_artifact_id, content_sha256)
        REFERENCES artifacts (id, sha256),
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
    contract_id             text NOT NULL UNIQUE CHECK (length(btrim(contract_id)) > 0),
    analysis_id             uuid NOT NULL REFERENCES analyses(id),
    knowledge_snapshot_id   uuid NOT NULL REFERENCES knowledge_snapshots(id),
    retrieval_artifact_id   uuid NOT NULL REFERENCES artifacts(id),
    method                  text NOT NULL
                            CHECK (method IN ('KEYWORD', 'VECTOR', 'HYBRID')),
    model_version           text,
    query                   jsonb NOT NULL CHECK (jsonb_typeof(query) = 'object'),
    excluded_reasons        jsonb NOT NULL DEFAULT '{}'::jsonb
                            CHECK (jsonb_typeof(excluded_reasons) = 'object'),
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
    score                   double precision NOT NULL
                            CHECK (score > '-Infinity'::double precision
                                   AND score < 'Infinity'::double precision),
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
    UNIQUE (contract_id, content_sha256),
    FOREIGN KEY (catalog_artifact_id, content_sha256)
        REFERENCES artifacts (id, sha256)
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
    materialized_input_bindings jsonb NOT NULL DEFAULT '[]'::jsonb
                                CHECK (jsonb_typeof(materialized_input_bindings) = 'array'),
    input_fields                jsonb NOT NULL CHECK (jsonb_typeof(input_fields) = 'array'),
    required_artifact_kinds     jsonb NOT NULL DEFAULT '[]'::jsonb
                                CHECK (jsonb_typeof(required_artifact_kinds) = 'array'),
    allowed_effects             jsonb NOT NULL DEFAULT '[]'::jsonb
                                CHECK (jsonb_typeof(allowed_effects) = 'array'),
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
            AND materialized_input_bindings = '[]'::jsonb
        )
    )
);

CREATE TABLE plans (
    id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id                     uuid NOT NULL REFERENCES cases(id),
    contract_id                 text NOT NULL UNIQUE CHECK (length(btrim(contract_id)) > 0),
    analysis_id                 uuid NOT NULL,
    retrieval_id                uuid,
    before_snapshot_id          uuid NOT NULL,
    after_snapshot_id           uuid NOT NULL,
    template_id                 uuid NOT NULL REFERENCES templates(id),
    plan_artifact_id            uuid NOT NULL REFERENCES artifacts(id),
    initial_state_artifact_id   uuid NOT NULL REFERENCES artifacts(id),
    normal_input                jsonb NOT NULL CHECK (jsonb_typeof(normal_input) = 'object'),
    planner_metadata            jsonb NOT NULL DEFAULT '{}'::jsonb
                                CHECK (jsonb_typeof(planner_metadata) = 'object'),
    attempts_per_side           integer NOT NULL
                                CHECK (attempts_per_side BETWEEN 1 AND 10),
    timeout_seconds             integer NOT NULL
                                CHECK (timeout_seconds BETWEEN 1 AND 300),
    authorship                  jsonb NOT NULL,
    created_at                  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, case_id),
    UNIQUE (id, attempts_per_side),
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
    required_artifact_kinds jsonb NOT NULL DEFAULT '[]'::jsonb
                            CHECK (jsonb_typeof(required_artifact_kinds) = 'array'),
    uncovered_reason        text,
    PRIMARY KEY (plan_id, obligation_id),
    FOREIGN KEY (plan_id, case_id)
        REFERENCES plans (id, case_id),
    FOREIGN KEY (obligation_id, case_id)
        REFERENCES obligations (id, case_id),
    CHECK (
        binding_status <> 'UNCOVERED'
        OR (uncovered_reason IS NOT NULL AND length(btrim(uncovered_reason)) > 0
            AND required_artifact_kinds = '[]'::jsonb)
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
    contract_id         text NOT NULL UNIQUE CHECK (length(btrim(contract_id)) > 0),
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
    contract_id             text NOT NULL UNIQUE CHECK (length(btrim(contract_id)) > 0),
    comparison_run_id       uuid NOT NULL,
    plan_id                 uuid NOT NULL,
    case_id                 uuid NOT NULL,
    snapshot_id             uuid NOT NULL,
    side                    text NOT NULL CHECK (side IN ('before', 'after')),
    -- Constraint witness: must equal the selected plan's limit, never independent config.
    plan_attempts_per_side  integer NOT NULL,
    attempt_number          integer NOT NULL
                            CHECK (attempt_number BETWEEN 1 AND plan_attempts_per_side),
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
    FOREIGN KEY (plan_id, plan_attempts_per_side)
        REFERENCES plans (id, attempts_per_side),
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
    CHECK (phase <> 'FINISHED' OR finished_at IS NOT NULL),
    CHECK (started_at IS NULL OR finished_at IS NULL OR finished_at >= started_at)
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
    comparison_run_id   uuid NOT NULL,
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
    UNIQUE (id, case_id, comparison_run_id, obligation_id, evaluator_version),
    FOREIGN KEY (run_id, comparison_run_id)
        REFERENCES runs (id, comparison_run_id),
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
    UNIQUE (id, case_id, comparison_run_id, obligation_id, evaluator_version),
    FOREIGN KEY (comparison_run_id, case_id)
        REFERENCES comparison_runs (id, case_id),
    FOREIGN KEY (obligation_id, case_id)
        REFERENCES obligations (id, case_id)
);

CREATE TABLE result_checks (
    comparison_result_id    uuid NOT NULL,
    run_check_id            uuid NOT NULL,
    case_id                 uuid NOT NULL,
    comparison_run_id       uuid NOT NULL,
    obligation_id           uuid NOT NULL,
    evaluator_version       text NOT NULL,
    PRIMARY KEY (comparison_result_id, run_check_id),
    FOREIGN KEY (comparison_result_id, case_id, comparison_run_id, obligation_id, evaluator_version)
        REFERENCES comparison_results (id, case_id, comparison_run_id, obligation_id, evaluator_version),
    FOREIGN KEY (run_check_id, case_id, comparison_run_id, obligation_id, evaluator_version)
        REFERENCES run_checks (id, case_id, comparison_run_id, obligation_id, evaluator_version)
);


-- 7. Publication guards. All related tables/functions belong to one schema.
-- Normal importer transactions use READ COMMITTED and lock the bundle BEFORE
-- reading its entries. A file's actual bytes and the manifest are still checked
-- outside SQL; these triggers serialize metadata writes against sealing.

CREATE FUNCTION guard_artifact_bundle() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE
    target_bundle uuid;
    bundle_status text;
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF NEW.id IS DISTINCT FROM OLD.id OR NEW.bundle_id IS DISTINCT FROM OLD.bundle_id THEN
            RAISE EXCEPTION 'artifact identity and bundle cannot change' USING ERRCODE = '23514';
        END IF;
    END IF;
    IF TG_OP = 'DELETE' THEN
        target_bundle := OLD.bundle_id;
    ELSE
        target_bundle := NEW.bundle_id;
    END IF;
    EXECUTE format('SELECT status FROM %I.bundles WHERE id = $1 FOR UPDATE', TG_TABLE_SCHEMA)
        INTO bundle_status USING target_bundle;
    IF bundle_status IS NULL THEN
        RAISE EXCEPTION 'artifact bundle does not exist' USING ERRCODE = '23503';
    END IF;
    IF bundle_status <> 'OPEN' THEN
        RAISE EXCEPTION 'artifact writes require an OPEN bundle' USING ERRCODE = '55000';
    END IF;
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER artifacts_open_bundle
BEFORE INSERT OR UPDATE OR DELETE ON artifacts
FOR EACH ROW EXECUTE FUNCTION guard_artifact_bundle();

CREATE FUNCTION guard_bundle_publication() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE
    artifact_count bigint;
    artifact_bytes numeric;
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.status <> 'OPEN' THEN
            RAISE EXCEPTION 'new bundles must start OPEN' USING ERRCODE = '23514';
        END IF;
        RETURN NEW;
    END IF;
    IF OLD.status <> 'OPEN' THEN
        RAISE EXCEPTION 'SEALED/FAILED bundle metadata is immutable' USING ERRCODE = '55000';
    END IF;
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    IF NEW.id IS DISTINCT FROM OLD.id THEN
        RAISE EXCEPTION 'bundle identity cannot change' USING ERRCODE = '23514';
    END IF;
    IF NEW.status = 'SEALED' THEN
        -- The UPDATE owns the same bundle row lock used by artifact writes.
        EXECUTE format('SELECT count(*), coalesce(sum(size_bytes), 0) FROM %I.artifacts WHERE bundle_id = $1',
                       TG_TABLE_SCHEMA)
            INTO artifact_count, artifact_bytes USING NEW.id;
        IF artifact_count NOT BETWEEN 1 AND 64 OR artifact_bytes > 33554432 THEN
            RAISE EXCEPTION 'bundle artifact count/bytes exceed contract limits' USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER bundles_publication
BEFORE INSERT OR UPDATE OR DELETE ON bundles
FOR EACH ROW EXECUTE FUNCTION guard_bundle_publication();

-- Immutable facts are inserted with all children in one validated transaction.
-- These guards freeze existing rows; late child INSERTs and set completeness
-- require the importer protocol described in database-schema.md.
-- Jobs, comparison_runs, runs and run_artifacts retain their mutable lifecycle.
CREATE FUNCTION reject_immutable_fact_change() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
    RAISE EXCEPTION 'immutable fact in %.%; preserve the original identity/content',
        TG_TABLE_SCHEMA, TG_TABLE_NAME USING ERRCODE = '55000';
END;
$$;

DO $$
DECLARE
    fact_table text;
    target_schema text := current_schema();
BEGIN
    FOREACH fact_table IN ARRAY ARRAY[
        'cases', 'snapshots', 'obligations', 'analyses', 'knowledge_snapshots',
        'scenario_cards', 'kb_cards', 'retrievals', 'retrieval_hits',
        'template_catalogs', 'templates', 'plans', 'plan_obligations',
        'evidence_events', 'run_checks', 'check_evidence', 'comparison_results', 'result_checks'
    ] LOOP
        EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE ON %I.%I '
            'FOR EACH ROW EXECUTE FUNCTION %I.reject_immutable_fact_change()',
            target_schema, fact_table, target_schema);
    END LOOP;
    FOREACH fact_table IN ARRAY ARRAY[
        'bundles', 'artifacts', 'cases', 'snapshots', 'obligations', 'analyses',
        'knowledge_snapshots', 'scenario_cards', 'kb_cards', 'retrievals', 'retrieval_hits',
        'template_catalogs', 'templates', 'plans', 'plan_obligations',
        'evidence_events', 'run_checks', 'check_evidence', 'comparison_results', 'result_checks'
    ] LOOP
        EXECUTE format('CREATE TRIGGER immutable_truncate BEFORE TRUNCATE ON %I.%I '
            'FOR EACH STATEMENT EXECUTE FUNCTION %I.reject_immutable_fact_change()',
            target_schema, fact_table, target_schema);
    END LOOP;
END;
$$;


-- 8. FK/reproduction access paths. PK/UNIQUE indexes already cover leading keys
-- such as bundle_id on artifacts and run_id on run_artifacts/evidence_events.
CREATE INDEX cases_case_artifact_idx ON cases (case_artifact_id);
CREATE INDEX cases_task_artifact_idx ON cases (task_artifact_id);
CREATE INDEX cases_policy_artifact_idx ON cases (policy_artifact_id);
CREATE INDEX cases_environment_artifact_idx ON cases (environment_artifact_id);
CREATE INDEX cases_initial_state_artifact_idx ON cases (initial_state_artifact_id);
CREATE INDEX cases_provenance_artifact_idx ON cases (provenance_artifact_id);
CREATE INDEX cases_dependency_artifact_idx ON cases (dependency_manifest_artifact_id);
CREATE INDEX cases_family_idx ON cases (family_id, created_at, id);
CREATE INDEX snapshots_workflow_idx ON snapshots (workflow_artifact_id, raw_sha256);
CREATE INDEX snapshots_document_idx ON snapshots (snapshot_artifact_id);
CREATE INDEX snapshots_normalized_idx ON snapshots (normalized_artifact_id);
CREATE INDEX snapshots_semantics_idx ON snapshots (semantics_artifact_id);
CREATE INDEX obligations_source_idx ON obligations (source_artifact_id);
CREATE INDEX analyses_case_idx ON analyses (case_id, created_at, id);
CREATE INDEX analyses_before_idx ON analyses (before_snapshot_id, case_id, before_side);
CREATE INDEX analyses_after_idx ON analyses (after_snapshot_id, case_id, after_side);
CREATE INDEX analyses_artifact_idx ON analyses (analysis_artifact_id);
CREATE INDEX knowledge_manifest_idx ON knowledge_snapshots (manifest_artifact_id, manifest_sha256);
CREATE INDEX scenario_cards_artifact_idx ON scenario_cards (card_artifact_id, content_sha256);
CREATE INDEX scenario_cards_source_idx ON scenario_cards (source_artifact_id);
CREATE INDEX kb_cards_card_idx ON kb_cards (card_id);
CREATE INDEX retrievals_analysis_idx ON retrievals (analysis_id);
CREATE INDEX retrievals_knowledge_idx ON retrievals (knowledge_snapshot_id);
CREATE INDEX retrievals_artifact_idx ON retrievals (retrieval_artifact_id);
CREATE INDEX retrieval_hits_card_idx ON retrieval_hits (card_id);
CREATE INDEX retrieval_hits_member_idx ON retrieval_hits (knowledge_snapshot_id, card_id);
CREATE INDEX catalogs_artifact_idx ON template_catalogs (catalog_artifact_id, content_sha256);
CREATE INDEX plans_case_idx ON plans (case_id, created_at, id);
CREATE INDEX plans_analysis_idx ON plans (analysis_id, case_id, before_snapshot_id, after_snapshot_id);
CREATE INDEX plans_retrieval_idx ON plans (retrieval_id, analysis_id);
CREATE INDEX plans_template_idx ON plans (template_id);
CREATE INDEX plans_artifact_idx ON plans (plan_artifact_id);
CREATE INDEX plans_initial_state_idx ON plans (initial_state_artifact_id);
CREATE INDEX plan_obligations_obligation_idx ON plan_obligations (obligation_id, case_id);
CREATE INDEX jobs_plan_idx ON jobs (plan_id);
CREATE INDEX jobs_request_idx ON jobs (request_artifact_id);
CREATE INDEX comparison_runs_plan_idx ON comparison_runs (plan_id, case_id);
CREATE INDEX runs_plan_idx ON runs (plan_id, plan_attempts_per_side);
CREATE INDEX runs_snapshot_idx ON runs (snapshot_id, case_id, side);
CREATE INDEX runs_artifact_idx ON runs (run_record_artifact_id);
CREATE INDEX run_artifacts_artifact_idx ON run_artifacts (artifact_id);
CREATE INDEX evidence_events_source_idx ON evidence_events (source_artifact_id);
CREATE INDEX run_checks_obligation_idx ON run_checks (obligation_id, case_id);
CREATE INDEX run_checks_details_idx ON run_checks (details_artifact_id);
CREATE INDEX check_evidence_check_idx ON check_evidence (run_check_id, run_id);
CREATE INDEX check_evidence_artifact_idx ON check_evidence (run_artifact_id, run_id);
CREATE INDEX check_evidence_event_idx ON check_evidence (evidence_event_id, run_id);
CREATE INDEX comparison_results_obligation_idx ON comparison_results (obligation_id, case_id);
CREATE INDEX result_checks_check_idx
    ON result_checks (run_check_id, case_id, comparison_run_id, obligation_id, evaluator_version);


-- Optional, when pgvector is installed and embedding retrieval is implemented:
-- This block illustrates a 384-dimensional profile, not the platform default.
-- Select and validate the actual model/revision/dimensions before activation.
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
