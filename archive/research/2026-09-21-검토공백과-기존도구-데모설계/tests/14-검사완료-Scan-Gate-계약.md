# 14. 검사 완료 상태 scan gate 계약

상태: **EXECUTED / 실제 5 + synthetic 6, 11/11 기대 일치**
실험일: **2026-09-22**

## 목적

검사기가 낮은 위험 점수나 정상처럼 보이는 출력만 반환해도 실제 처리 범위가 불완전하거나 결과를 현재 입력에 결합할 수 없으면 활성화를 보류하는 fail-closed 계약을 검증한다.

정책 결과는 다음 세 가지다.

- `ALLOW`: 완료·파싱 가능·보고서 참조 존재·현재 입력 SHA-256 일치·분석 범위 완전·위험 finding 없음.
- `DENY`: 신뢰할 수 있는 완료 결과에서 위험 finding 확인.
- `HOLD`: timeout, 손상·절단된 출력, 누락 참조, stale digest, 불완전 분석, 0 files 등 승인 근거 부족.

`DENY`와 `HOLD`는 이유가 다르지만 둘 다 활성화를 막는다.

## 실행과 재현 주의

```powershell
python run_scan_gate_contract.py
```

runner는 저장된 실제 scanner 산출물과 synthetic envelope를 읽고 `scan-gate-results.json`·`.md`를 다시 쓴다. 원본 보존을 위해 **새 clone 또는 분리된 복사본에서만 실행**한다.

- runner: [`run_scan_gate_contract.py`](../../../experiments/live-agent-security/run_scan_gate_contract.py)
- 정책: [`scan_gate_policy.py`](../../../experiments/live-agent-security/scan_gate_policy.py)
- 구조화 결과: [`scan-gate-results.json`](../../../experiments/live-agent-security/scan-gate-results.json)
- 설명 결과: [`scan-gate-results.md`](../../../experiments/live-agent-security/scan-gate-results.md)

## 실제 저장 산출물 5개

| 사례 | 입력·상태 | 기대/실제 | 근거 |
|---|---|---|---|
| Cisco MCP M00 | 5/5 completed SAFE, 입력 digest 현재 일치 | ALLOW | complete clean bound scan |
| Cisco MCP M01 | HIGH `PROMPT INJECTION` | DENY | confirmed security finding |
| SkillSpector S00 default | score 0이나 `is_complete=false`, partial, unresolved reference | HOLD | incomplete analysis |
| SkillSpector S00 strict | 같은 partial + exit 1 | HOLD | incomplete + nonzero exit |
| AgentShield S00 | A/100이나 `filesScanned=0`, adapter match 0 | HOLD | zero files assessed |

실제 사례는 기존 execution metadata에 기록된 scanner 입력 경로·SHA-256을 현재 파일과 다시 비교하고, scanner report 자체도 이번 계약 실행 시 SHA-256·bytes로 snapshot했다.

## synthetic 6개

| 사례 | 주입한 결함 | 기대/실제 |
|---|---|---|
| SYNTHETIC_TIMEOUT | transport timeout | HOLD |
| SYNTHETIC_MALFORMED | JSON 파싱 불가 | HOLD |
| SYNTHETIC_TRUNCATED | 잘린 report 표시와 bytes | HOLD |
| SYNTHETIC_MISSING_REF | report reference 빈 값 | HOLD |
| SYNTHETIC_STALE_DIGEST | scanned와 current input digest 불일치 | HOLD |
| SYNTHETIC_CLEAN | 완료·정상·결합된 Cisco형 report | ALLOW |

synthetic 사례는 실제 scanner 실행이 아니라 adapter contract의 오류 경로를 결정론적으로 자극한 입력이다. 실제 도구의 timeout 빈도나 오류율로 해석하지 않는다.

## 결과

- 전체: **11개**.
- 실제 저장 증거: **5개**.
- synthetic: **6개**.
- 기대 판정 일치: **11/11**.
- 결과 분포: **ALLOW 2 / DENY 1 / HOLD 8**.

정책 파일 SHA-256은 `17b79f...f41c7`, runner는 `760f5e...33f0`이며 전체 값과 source manifest는 결과 JSON에 있다.

## 해석 경계

이 계약은 scanner의 탐지 정확도를 새로 측정하지 않는다. 위험 finding이 있는 완료 결과, clean 완료 결과, 불완전하거나 결합이 깨진 결과를 activation decision으로 정규화하는 작은 정책 시험이다. ALLOW 2/11을 생태계 안전률로, HOLD 8/11을 실제 제품 장애율로 해석하면 안 된다.
