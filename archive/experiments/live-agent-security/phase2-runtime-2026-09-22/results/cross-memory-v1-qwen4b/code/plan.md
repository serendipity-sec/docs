# Phase 2 runtime validation plan

Date: 2026-09-22

This directory extends the published experiment without modifying any source file whose hash is part of earlier evidence. Every batch copies its executing code, records hashes, uses a new `LAB_ONLY_` canary, and separates model output from file or receiver effects.

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
- Public malicious Skill text is static input only. Public malicious or vulnerable MCP code is not executed by the model in this phase.
- `COMPLETED` only means that the harness ended. Normal utility and actual effect are separate fields.
- Local open models are not commercial-model evidence. Synthetic study actors are excluded from human results.
- Existing `paper-guided-2026-09-22` code is intentionally untouched because its verifier binds stored runs to source hashes.

## Predeclared dynamic matrices

| Matrix | Cases | Policies | Seeds | Initial model |
|---|---:|---:|---:|---|
| Cross-server permission composition | 3 | 3 | 3 | `qwen3:4b-q4_K_M` |
| Two-session memory poisoning and combination | 4 | 3 | 3 | `qwen3:4b-q4_K_M` |
| Expression twins | 12 | 2 | 3 | each available model batch |
| Bounded adaptive response injection | attack fixed/adaptive plus benign control | 2 | 3 | `qwen3:4b-q4_K_M` |

Static scanner, Docker isolation, Skill TOCTOU, and user-study dry-run records live in their own subdirectories and are not added to the model-run denominator.
