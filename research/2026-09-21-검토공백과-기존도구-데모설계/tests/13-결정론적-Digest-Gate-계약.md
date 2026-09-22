# 13. 결정론적 digest gate 계약

상태: **EXECUTED / 11개 계약 사례 모두 기대 일치**
실험일: **2026-09-22**

## 목적

LLM의 확률적 행동과 분리해 tool contract와 Skill bundle digest 함수가 무해한 순서 변경, 실제 내용 변경, 잘못된 구조, 파일 추가·수정을 결정론적으로 구분하는지 확인한다.

이 테스트에는 모델, seed, MCP scanner가 없다. 입력 JSON과 임시 Skill 디렉터리에 대해 순수 정책 함수를 실행한다.

## 실행

```powershell
python run_gate_contract.py
```

runner는 최상위 `gate-contract-results.json`을 덮어쓴다. 검증 재실행은 반드시 **새 clone 또는 원본과 분리한 복사본**에서 수행한다.

- runner: [`run_gate_contract.py`](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/run_gate_contract.py)
- 정책: [`gate_policy.py`](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/gate_policy.py)
- 결과: [`gate-contract-results.json`](https://github.com/serendipity-sec/platform/blob/4bd3ca337dd000fa60791207f94025807dff8a0c/experiments/live-agent-security/gate-contract-results.json)

## canonicalization과 정책

tool contract는 도구를 이름순으로 정렬하고 JSON 키를 정렬한 뒤 SHA-256을 계산한다. 중복 도구명과 `tools` 배열 누락은 digest를 만들지 않고 거부한다. Skill manifest는 디렉터리의 모든 파일 상대경로와 content digest를 묶으므로 entrypoint 밖 파일 추가도 바뀐 값으로 나타나야 한다.

## 11개 사례 결과

| 유형 | 사례 | 기대 | 실제 | 결과 |
|---|---|---|---|---|
| tool | identical | ALLOW | ALLOW | PASS |
| tool | tool-order-only | ALLOW | ALLOW | PASS |
| tool | description-change | CHANGE_REQUIRES_REAPPROVAL | 동일 | PASS |
| tool | schema-change | CHANGE_REQUIRES_REAPPROVAL | 동일 | PASS |
| tool | benign-change-before-reapproval | CHANGE_REQUIRES_REAPPROVAL | 동일 | PASS |
| tool | benign-change-after-reapproval | ALLOW | ALLOW | PASS |
| tool | change-without-lock | ALLOW | ALLOW | PASS |
| invalid | duplicate-tool-name | REJECT | ValueError | PASS |
| invalid | missing-tools-array | REJECT | ValueError | PASS |
| Skill | skill-file-added | digest 변경 | 변경 | PASS |
| Skill | skill-entry-edited | digest 변경 | 변경 | PASS |

도구 정상 digest는 `d59931...67bd7`, poisoned digest는 `db1a20...7d3bc`다. 무해한 description 변경도 재승인 전에는 차단되고, 새 변경본을 승인 snapshot으로 갱신한 뒤에는 허용된다. 이것은 내용의 악성 여부를 판단하는 정책이 아니라 승인한 대상과 현재 대상의 동일성을 확인하는 정책이다.

## 판정과 한계

- 기대 판정 일치: **11/11**.
- 모델 실행·scanner 실행·사용자 승인: **NOT_RUN / 해당 없음**.
- 실제 최신 MCP subscription/TTL/authorization context: **NOT_ASSESSED**.

Skill manifest 변경 감지는 서명자 신원이나 악성 여부를 증명하지 않는다. symlink, archive traversal, 대용량 압축, OS별 경로 정규화는 이 2개 Skill mutation 사례에 포함되지 않는다.
