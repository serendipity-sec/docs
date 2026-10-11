# Phase 2 runtime validation plan

Date: 2026-09-22

This directory extends the published experiment without modifying any source file whose hash is part of earlier evidence. Every final model batch has an immutable contract binding its complete expected matrix, selected model digest, runtime, source snapshot, per-run input, and a new `LAB_ONLY_` canary. Model output, file effects, and receiver receipts are separate evidence.

## Questions

1. Can a model combine permissions exposed by separate MCP servers?
2. Can untrusted memory written in one session affect a later session?
3. Do language and format changes alter attack behavior?
4. Does a bounded adaptive attacker improve over repeating one failed payload?
5. Do OS file and network restrictions, and execution-time integrity controls, block actual effects while preserving the intended task?
6. Can the proposed user-study instrumentation calculate metrics without treating synthetic actors as people?

## Safety and interpretation

- All secrets are run-specific dummy values and every receiver is loopback or a Docker-internal test endpoint.
- Models receive fixed tools only. They receive no shell, arbitrary URL, environment-variable, cloud, browser, GitHub, or user-home capability.
- Defender-blocked public files are not bypassed. The readable public fake Vercel Skill receives a separate no-network Docker attempted-behavior test with dummy data and recording shims; it cannot prove external exfiltration.
- `COMPLETED` only means that the harness ended. Normal utility and actual effect are separate fields.
- Local open models are not commercial-model evidence. No commercial victim-model API credential is available, so that arm is `NOT_RUN`. The authenticated Codex CLI scanner arm is scanner evidence, not victim-agent evidence.
- Synthetic study actors are excluded from human results. Real participant recruitment, consent, and measurements remain `NOT_RUN`.
- The `exact-value-lineage` policy follows exact returned values and one canonical public fragment. Paraphrase, encoding, or partial-secret transformations can lose the label; its name and conclusions retain that limitation.
- Model MCP fixtures use separate process namespaces, per-role fixture roots, and expose the collector port only to the report role. This is configured-capability separation, not an OS sandbox. The Docker isolation matrix tests the OS boundary.
- Existing `paper-guided-2026-09-22` code is intentionally untouched because its verifier binds stored runs to source hashes.

## Predeclared dynamic matrices

| Matrix | Cases | Policies | Seeds | Initial model |
|---|---:|---:|---:|---|
| Cross-server permission composition | 3 | 3 | 3 | `qwen3:4b-q4_K_M` |
| Two-session memory poisoning and combination | 4 | 3 | 3 | `qwen3:4b-q4_K_M` |
| Expression twins, primary | 12 | 2 | 3 | `qwen3:4b-q4_K_M` |
| Expression twins, secondary-size/family checks | 12 | 2 | 1 each | `qwen3:1.7b-q4_K_M`, `qwen3:8b-q4_K_M`, `llama3.2:3b` |
| Feedback-conditioned bounded response injection | attack fixed/adaptive plus benign control | 2 | 3 | `qwen3:4b-q4_K_M` |

The secondary batches are breadth checks, not equal-power estimates: one seed cannot establish model-level rates or repeatability. The primary batch uses three fixed seeds. `broad`/`all-exposed`, `exact-value-lineage`, and `intent-lock` are host-policy fixtures rather than claims about a production policy engine.

## Resource amendment after the contracted smoke batch

The nine-run `contract-smoke-v2` measured about 20 minutes on this host because Ollama used CPU inference. Completing the original primary three-seed plan plus four full model matrices would require several hours and would mix thermal/runtime drift into a single interactive run. After seeing the smoke results, the execution matrix was reduced for compute reasons; this is an outcome-aware protocol amendment and must not be presented as a preregistered rate study.

The completed-demo target is therefore:

- all 21 cross-server and memory case-policy cells at seed 47, combining the contracted smoke batch with a complementary batch;
- all 24 expression twin-policy cells at seed 47 for Qwen 4B;
- the same E00 English, E01 Korean, and E02 JSON attack/benign twins under the broad host policy at seed 47 for Qwen 1.7B, Qwen 8B, and Llama 3.2 3B;
- all fixed, feedback-adaptive, and benign-control episodes at seed 47 for Qwen 4B.

These are execution demos and paired breadth checks. They do not estimate population rates, seed stability, or a model-family ranking. The unexecuted seeds 59 and 71 remain `NOT_RUN_RESOURCE_LIMIT`, not negative results.

Static scanner, Docker isolation, Skill TOCTOU, and user-study dry-run records live in their own subdirectories and are not added to the model-run denominator.
