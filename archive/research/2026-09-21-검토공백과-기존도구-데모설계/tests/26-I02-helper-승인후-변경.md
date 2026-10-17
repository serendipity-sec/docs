# I02-helper-edited — SKILL.md가 같아도 helper 변경을 보류하는가

실험일: 2026-09-22. 상태: **결정론적 로컬 계약 1건 실행, 기대 판정 일치**. 모델·MCP 호출·네트워크 전송 없이 패키지 검증만 수행했다.

## 목적과 입력 변경

정상 버전 3을 서명한 뒤 scripts/render.py를 `return 'changed:' + text` 구현으로 교체한다. SKILL.md와 manifest는 그대로 둔다.

정상 목적은 공개 프로젝트 자료를 읽어 사실에 맞는 요약을 만드는 Skill을 승인하는 것이다. 이 테스트는 그 업무를 실제 AI로 수행하지 않고, 승인 대상 패키지의 동일성·발행자·버전·toy 안전 정책을 검사한다.

## 비교 구조와 사전 정답

사전 기대 결정은 `HOLD_INTEGRITY`이고 실제 결정도 `HOLD_INTEGRITY`였다. 사례별 반복 seed는 없으며 전체 8종 매트릭스에서 한 번씩 결정론적으로 확인했다.

검증 순서와 기준:

1. manifest를 정렬 key·공백 없는 JSON으로 canonicalize하고 Ed25519 서명을 검증한다.
2. 실제 전체 파일 집합의 추가·삭제·수정을 서명 manifest와 비교한다.
3. 별도 entrypoint-only 비교를 대조 지표로 계산한다. 이것만으로 최종 허용하지 않는다.
4. host의 신뢰 공개키와 발행자를 비교하고 최소 버전 3을 적용한다.
5. `private/session.txt` 또는 `send_report` 문구가 있는지 toy safety gate를 적용한다.
6. integrity·authenticity·freshness·safety가 모두 통과할 때만 ALLOW한다.

manifest.json, manifest.sig, signer-public-key.hex, approval.json은 파일 집합의 제어 메타데이터로 제외한다. 이 제외가 모든 형태의 package closure를 검증한다는 뜻은 아니다.

## 입력 파일과 고정 근거

| manifest 파일 | 승인된 SHA-256 | 실제 SHA-256 또는 상태 |
|---|---|---|
| [SKILL.md](../../../experiments/live-agent-security/paper-guided-2026-09-22/skill-integrity-fixtures/I02-helper-edited/SKILL.md) | `f885cff7f9e059f89d7691e941d70da7c80314d423cdbaebf573206fc94f2d4d` | `f885cff7f9e059f89d7691e941d70da7c80314d423cdbaebf573206fc94f2d4d` |
| [references/schema.md](../../../experiments/live-agent-security/paper-guided-2026-09-22/skill-integrity-fixtures/I02-helper-edited/references/schema.md) | `15e60b0cd335d8981d9aefa26d85296c41075377e032f606fc3b049c23fa6fa1` | `15e60b0cd335d8981d9aefa26d85296c41075377e032f606fc3b049c23fa6fa1` |
| [scripts/render.py](../../../experiments/live-agent-security/paper-guided-2026-09-22/skill-integrity-fixtures/I02-helper-edited/scripts/render.py) | `89d650cf07b68526059914bbcc2a8dce435e449d7f1c5de81252bc3a3d6dde8c` | `bd62fa228202bf6066c3f65b22e3e8cb027da992c2146414e68601b4dd1cdcce` |

canonical manifest SHA-256: `405141b0d5e0378e15b8098129694f8807fcfa37005add48e677fae3992ef71b`.

[manifest](../../../experiments/live-agent-security/paper-guided-2026-09-22/skill-integrity-fixtures/I02-helper-edited/manifest.json) · [signature](../../../experiments/live-agent-security/paper-guided-2026-09-22/skill-integrity-fixtures/I02-helper-edited/manifest.sig) · [signer public key](../../../experiments/live-agent-security/paper-guided-2026-09-22/skill-integrity-fixtures/I02-helper-edited/signer-public-key.hex) · [실험 승인 기록](../../../experiments/live-agent-security/paper-guided-2026-09-22/skill-integrity-fixtures/I02-helper-edited/approval.json)

## 실행 방법

Python 3.12와 cryptography 50.0.1을 사용했다. Ed25519 키는 코드에 고정한 lab 문자열의 SHA-256에서 유도한 공개 실험용 키다. 실제 서비스의 키 생성·보관 방식으로 사용하면 안 된다.

**새 clone에서** docs 루트를 작업 디렉터리로 다음을 실행한다. 이 스크립트는 자기 소유 fixture 디렉터리 8개를 삭제·재생성하고 결과도 다시 쓰므로, 보존 중인 원본 디렉터리에서는 실행하지 않는다.

```powershell
python experiments/live-agent-security/paper-guided-2026-09-22/run_skill_integrity.py
```

실행기 SHA-256: `ee60ccb03f572d4180943348a951f6c5bd6eb171324abffa68b40b4a3eabc65d`. 코드: [run_skill_integrity.py](../../../experiments/live-agent-security/paper-guided-2026-09-22/run_skill_integrity.py). 특정 case만 생성하는 CLI는 없으므로 8건 전체를 실행하고 아래 case_id로 결과를 찾는다.

## 실제 관측값

| 필드 | 값 |
|---|---|
| `entrypoint_digest_match` | `true` |
| `signature_valid` | `true` |
| `full_tree_match` | `false` |
| `signer_trusted` | `true` |
| `version` | `3` |
| `minimum_version` | `3` |
| `version_current` | `true` |
| `security_scan_pass` | `true` |
| `integrity_pass` | `false` |
| `authenticity_pass` | `true` |
| `decision` | `"HOLD_INTEGRITY"` |
| `expected_match` | `true` |

변경·누락·추가와 toy finding:

```json
{
  "changed_files": [
    "scripts/render.py"
  ],
  "missing_files": [],
  "added_files": [],
  "security_scan_hits": []
}
```

## 해석과 제한

entrypoint만 비교하면 통과하지만 실제 scripts/render.py hash가 manifest와 달라 full-tree는 실패했다. 진입 문서가 그대로여도 실행에 영향을 주는 파일을 승인 범위에 포함해야 한다.

이는 상용 scanner 탐지율이나 악성 Skill의 AI 실행 재현이 아니다. safety gate는 두 리터럴을 찾는 축소 규칙이며 문구를 바꾼 공격·정상 설명 인용·다른 언어를 제대로 분류하는지 평가하지 않았다. 무결성 통과가 무취약성을 뜻하지 않는다.

approval.json 자체의 신뢰 저장소·전자서명, 서명 key 폐기, timestamp, SemVer 해석, 경로 대소문자 충돌·symlink, 검사와 사용 사이의 경쟁 상태는 이 8건에 포함되지 않는다. 파일을 읽는 시점의 단순 집합 비교를 실제 OS sandbox나 전체 공급망 인증으로 확대하지 않는다.

## 결과 검토와 원본

[8건 원본 결과](../../../experiments/live-agent-security/paper-guided-2026-09-22/results/skill-integrity/results.json) · [전체 비교표](../../../experiments/live-agent-security/paper-guided-2026-09-22/results/skill-integrity/results.md) · [해당 패키지](../../../experiments/live-agent-security/paper-guided-2026-09-22/skill-integrity-fixtures/I02-helper-edited)

문서화 과정에서는 원본을 재생성하지 않고 inspect_package를 저장된 8개 패키지에 적용했다. 신뢰 공개키 SHA-256과 실행기 SHA-256을 먼저 대조하고, 재계산 필드 전체가 원래 JSON과 일치함을 확인했다. 기록은 [무결성 재검토 JSON](skill-integrity-recheck.json)에 있다.

설계 맥락은 [논문 기반 추가 실험](../07-논문기반-변형유출과-sleeper-추가실험.md)과 [공통 상세 색인](README.md)을 참고한다. 논문 원문의 수치나 구현을 재현했다고 주장하지 않는다.
