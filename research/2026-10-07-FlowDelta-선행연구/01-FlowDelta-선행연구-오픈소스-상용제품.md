# FlowDelta 아키텍처와 닮은 선행연구·오픈소스·상용 제품

Oct 7, 2026 · @준서

## FlowDelta 구조 (이 문서의 기준)

FlowDelta는 **업데이트된 스킬·워크플로를 로컬 서버에서 실제로 돌려, 이전 버전과 비교해 새로 생긴 행위·취약점을 찾는 방식**으로 정리했습니다. 학계 용어로는 **차분 동적 분석(differential dynamic analysis)** 또는 \*\*행위 기준선 비교(behavioral baselining)\*\*에 해당합니다.

&#91;embedded content: FlowDelta 이해도 · 두 버전 실행 → 행위 diff → 판정\]

아래 자료는 이 그림의 네 단계(① 버전 고정 ② 로컬 실행·기록 ③ 행위 diff ④ 판정·증거) 중 어디가 겹치는지로 표시했습니다.

## 한눈에 보기

결론: **"두 버전을 같은 조건에서 실행해 행위 차이를 본다"는 방식은 일반 소프트웨어 테스트·CI 보안·특허에는 이미 있지만, 스킬·n8n 워크플로를 대상으로 공개된 연구·도구는 이번 조사에서 찾지 못했습니다.** 스킬 동적 분석 연구(USENIX '26, SkillDetonate 등)는 모두 **한 버전만** 검사합니다. 그래서 FlowDelta의 빈칸은 분명하지만, 설계는 기존 것을 많이 빌려올 수 있습니다.

| FlowDelta 단계 | 가장 닮은 것 | 유형 · 신뢰도 | 빌려올 점 |
| --- | --- | --- | --- |
| ① 버전 고정 | [mcp-scan 도구 고정(tool pinning)](https://invariantlabs.ai/blog/introducing-mcp-scan), skillwarden | 오픈소스 | 해시로 "검사한 버전"을 고정하고 바뀌면 재검사 |
| ② 로컬 실행·기록 | [OpenSSF package-analysis](https://github.com/ossf/package-analysis), [USENIX '26 스킬 샌드박스](https://arxiv.org/html/2602.06547v4) | 오픈소스 / 동료심사 | 일회용 샌드박스 + 파일·네트워크·명령 기록 + 미끼 자격증명 |
| ③ 행위 diff | [Diffy](https://github.com/opendiffy/diffy) | 오픈소스 (Twitter 출신) | **이전 버전을 2번 돌려 "원래 흔들리는 정도(노이즈)"를 먼저 재고**, 그보다 큰 차이만 신호로 봄 |
| ③ 행위 diff (보안) | [Harden-Runner 기준선(baseline)](https://github.com/step-security/harden-runner) | 오픈소스 + 상용 | 과거 실행에서 본 적 없는 외부 연결만 경고 |
| ④ 판정·증거 | [Spectra Assure 패키지 diff](https://docs.secure.software/cli/guides/package-diff) | 상용 | 두 버전을 **같은 엔진·같은 설정**으로 검사한 뒤 비교 |

**FlowDelta 설계에 바로 영향을 주는 시사점 3개**

1. **노이즈 측정이 필수다.** LLM 에이전트는 같은 입력에도 매번 다르게 움직입니다. Diffy처럼 v1을 여러 번 돌려 "원래 차이"를 재지 않으면, 정상 업데이트도 전부 위험 후보로 뜹니다.
2. **환경을 고정해야 한다.** Harden-Runner는 2025-04에 GitHub 자체 도메인 변경 때문에 여러 고객에게 "새 연결" 경고를 냈습니다([사례](https://www.stepsecurity.io/blog/harden-runner-detects-new-traffic-to-release-assets-githubusercontent-com-across-multiple-customers)). 스킬·워크플로가 아니라 **환경이 바뀐 것도 차이로 잡힙니다.**
3. **코드 diff와 행위 diff를 연결해야 판정이 선다.** 행위 차이만으로는 "왜"를 설명하지 못하고, 코드 diff만으로는 실제로 실행되는지 모릅니다. 두 결과를 연결하는 부분이 FlowDelta의 기여 지점입니다.

## 선행연구

**"두 버전을 실행해 비교"하는 연구는 보안 분야에선 드물고, 대부분 "한 버전만 실행"하거나 "두 버전을 코드로만 비교"합니다.** FlowDelta는 이 둘을 합친 자리에 있습니다. 아래는 그 기준으로 나눈 표입니다.

**A. 두 버전의 "행위"를 비교 — FlowDelta와 가장 가까움**

| 연구 | 신뢰도 | 무엇을 하나 | FlowDelta와의 관계 |
| --- | --- | --- | --- |
| [LifecycleGuard — *Agent Skill Security: Threat Models, Attacks, Defenses, and Evaluation*](https://promptfoo.dev/lm-security-db/vuln/lifecycle-poisoning-of-reusable-agent-skills-fc8f356e) (arXiv 2607.13987) | 프리프린트 · **2차 출처로만 확인** | 스킬 업데이트를 **매번 새로 들어오는 스킬처럼 다시 심사**하고 행위 변화를 검토. 지속 검증이 없으면 악성 업데이트를 100% 받아들였고, 방어 시 악성 업데이트 92.5% 탐지 | 스킬 대상으로 "업데이트 = 재심사 + 행위 변화 검토"를 주장한 유일한 자료. 원문 확인 결과 실행 없이 지시문 벡터 거리만 비교(오탐률 37%). |
| [BeCoV — Kessel, *Co-Versioning Run-time Behavior alongside Code*](https://arxiv.org/abs/2604.16933) | 동료심사 (FSE 2026) | 커밋마다 실행 관찰값(입출력 등)을 "행위 보관소"에 쌓아 버전 간 **의미 diff** | 보안 연구는 아님. **증거 저장소를 버전별로 쌓는 설계** 참고용 |
| [특허: 버전 간 행위 변화로 공급망 공격 탐지](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12223045) (US 12223045) | 특허 (출원인 미확인) | 각 버전을 샌드박스에서 실행 → 활동을 벡터화·군집 → 버전 간 비교해 **설명되지 않는 새 행위**를 경고 | 구조가 FlowDelta와 거의 같음. 이미 특허가 있다는 점은 발표 때 "선행기술 확인"으로 언급 가능 |

**B. 두 버전을 "코드"로 비교 (실행 안 함)**

| 연구 | 신뢰도 | 무엇을 하나 | FlowDelta와의 관계 |
| --- | --- | --- | --- |
| [Garrett et al., *Detecting Suspicious Package Updates*](https://www.cs.cmu.edu/~ckaestne/pdf/icsenier19.pdf) | 동료심사 (ICSE 2019 NIER) | 이전 버전 대비 새로 쓰기 시작한 네트워크·파일·프로세스·eval·install 스크립트 등 8개 특징을 **정적으로** 뽑아 군집 밖 업데이트를 표시. 2,288건에서 검토량 89% 감소, eslint-scope 공격 탐지 | FlowDelta의 **코드 diff 쪽 기준선**. 저자도 예비 평가라고 밝힘 |
| [Vu et al., *LastPyMile*](https://2021.esec-fse.org/details/fse-2021-papers/61/LastPyMile-Identifying-the-Discrepancy-between-Sources-and-Packages) | 동료심사 (ESEC/FSE 2021) | 소스 저장소와 배포 패키지의 차이만 추출 | 비교 축이 "버전 간"이 아닌 "원본 ↔ 배포물" |

**C. 한 버전을 "실행" — 실행·기록 단계 참고용**

| 연구 | 신뢰도 | 실행 환경 | 버전 비교 여부 |
| --- | --- | --- | --- |
| [Liu et al., USENIX Security '26](https://arxiv.org/html/2602.06547v4) | 동료심사 | Docker 60초, tcpdump·strace·auditd, 미끼 자격증명, 3\~5회 반복 | 없음 (단일 버전) |
| [OSCAR](https://arxiv.org/abs/2409.09356v1) | 동료심사 (ASE 2024 산업 트랙) | 샌드박스 완전 실행 + 함수 퍼징 + API 후킹. 오탐률 npm 34.63% → 2.57% | 없음 |
| [SkillVetBench (Hossain et al.)](https://arxiv.org/abs/2606.00925) | 프리프린트 | Docker 샌드박스에서 LLM 에이전트로 스킬 실행, 게이트웨이 로그 26만 줄 이상 | 버전 변화는 **체계적으로 다루지 않음** |
| [SkillDetonate (Ji et al.)](https://arxiv.org/abs/2607.02357) | 프리프린트 | 실제 에이전트 + FUSE 미끼 + eBPF 추적 | 없음 |

**읽는 법:** C의 연구들이 "한 번 실행해 나쁜 행위가 있나"를 묻는다면, FlowDelta는 "**v1에 없던 행위가 v2에 생겼나**"를 묻습니다. 이 질문은 정상 스킬이 원래 하던 위험해 보이는 행위(예: 정당한 외부 API 호출)를 걸러 주므로, 단일 버전 검사의 고질적인 오탐 문제를 줄일 수 있다는 것이 FlowDelta의 논리가 됩니다(우리 가설, 검증 전).

## 오픈소스·프로젝트

**행위 diff 엔진으로는 Diffy, 실행·기록 인프라로는 OpenSSF package-analysis가 가장 참고할 만합니다.** 스킬·n8n 쪽에는 버전 고정이나 화면 diff만 있고, "실행해서 비교"하는 도구는 없었습니다.

| 이름 | 단계 | 무엇을 하나 | 라이선스 · 상태 | FlowDelta에 주는 것 |
| --- | --- | --- | --- | --- |
| [Diffy](https://github.com/opendiffy/diffy) | ③ | 같은 요청을 **새 버전 1개 + 기존 버전 2개**에 동시에 보내고, "기존끼리 차이(노이즈)"보다 큰 "기존↔새 차이"만 보고 | CC BY-NC-ND 4.0 · 스타 1.5k+ | **노이즈 상쇄 설계의 원형.** 비상업 라이선스라 코드 재사용보다 **아이디어 차용** 권장 |
| [BehaviorDiff](https://github.com/abheeshtroy/BehaviorDiff) | ②③ | 두 버전을 컨테이너로 나란히 띄워 같은 시나리오 실행 → HTTP 응답·DB 변화·외부 호출 비교, 여러 번 돌려 비결정성 제거 | MIT · 스타 0, v0.1.0 (개인 프로젝트) | 구조가 FlowDelta와 매우 닮음. 신뢰도 낮아 **설계 참고만** |
| [OpenSSF package-analysis](https://github.com/ossf/package-analysis) | ② | 큐 → gVisor 샌드박스 워커 → 파일·네트워크(DNS 포함)·명령 기록 → BigQuery | Apache-2.0 · 스타 915 | 실행·기록 단계의 참고 구현. 버전 비교 기능은 없음 |
| [Harden-Runner](https://github.com/step-security/harden-runner) | ②③ | CI 러너의 네트워크·파일·프로세스 감시, 과거 실행으로 **기준선**을 만들고 새 외부 연결을 경고 | Apache-2.0 (공개 저장소 무료) | "이전에 없던 연결" 판정의 실전 사례. 환경 변화로 인한 오경보 사례도 있음 |
| [mcp-scan (Invariant → Snyk agent-scan)](https://invariantlabs.ai/blog/introducing-mcp-scan) | ① | MCP 도구 설명을 해시로 고정(tool pinning)하고 바뀌면 경고 | Apache-2.0 | "검사한 버전" 고정 방식. 바뀐 **내용이 위험한지**는 판단하지 않음 |
| [skillwarden](https://github.com/coltonbearden/skillwarden) | ① | 설치된 스킬을 고정·해시 검증, 원본 변경 감지, 감사 결과가 바뀌면 CI 실패 | 미확인 (개인) | 스킬판 버전 고정. 실행 비교는 없음 |
| [install-then-update-trap-detector](https://getclawkit.com/skills/official-andyxinweiminicloud-install-then-update-trap-detector) | ①③ | 감사받은 버전과 현재 버전의 차이에서 권한 확장·새 엔드포인트·행위 변화를 표시 (스킬 형태) | 미확인 · 커뮤니티 스킬 | 아이디어가 FlowDelta와 같음. 단 **스킬로 만든 검사기는 그 자체가 공격 벡터**가 될 수 있음 |
| [n8n 워크플로 diff](https://docs.n8n.io/administer/use-source-control-and-environments/compare-versions) | ③ (코드) | 버전 간 추가·수정·삭제된 노드와 연결, JSON 설정 차이를 화면에 표시 | n8n 내장 (Business·Enterprise 플랜) | **n8n 쪽 코드 diff 입력으로 바로 활용 가능.** 보안 분석 기능은 문서에 없음 |

## 상용 제품

**버전 비교 보안 제품은 패키지·바이너리·CI 대상으로 이미 상용화돼 있고, 스킬 동적 분석 제품(SandyClaw)은 버전 비교를 하지 않습니다.**

| 제품 | 회사 | 비교 방식 | 실행 여부 | FlowDelta에 주는 것 |
| --- | --- | --- | --- | --- |
| [Spectra Assure 패키지 diff](https://docs.secure.software/cli/guides/package-diff) | ReversingLabs | 두 버전을 같은 엔진·설정으로 스캔한 뒤 행위·파일 내용·품질 이슈·태그 변화를 보고. 변조 여부 판단용 | 정적 분석만 (실행 안 함) | **"동일 조건 검사 후 비교"** 절차 |
| [StepSecurity (Harden-Runner 기업판)](https://github.com/step-security/harden-runner) | StepSecurity | 과거 실행 기준선 대비 새 외부 연결 탐지 | 실제 실행 감시 | 행위 기준선 운영 방식, 오경보 처리 |
| [Socket for GitHub](https://docs.socket.dev/docs/socket-for-github) | Socket | PR에서 새로 추가·변경된 의존성만 골라 설치 스크립트·네트워크·셸·환경변수 경고 | 정적 분석만 | "변경분만 리뷰어에게 근거와 함께" 보여 주는 화면 |
| [Semgrep diff-aware 스캔](https://docs.semgrep.dev/deployment/customize-ci-jobs) | Semgrep | 기준 브랜치 이후 **새로 생긴 발견만** 보고 | 정적 | "기존 위험은 빼고 새 위험만" 보고 규칙 |
| [SandyClaw](https://permiso.io/blog/introducing-sandyclaw-dynamic-sandbox-ai-agent-skills) | Permiso | 버전 비교 없음 (단일 스킬 실행) | 실제 에이전트로 실행, TLS 복호화, 행위 전부 기록 | 스킬 실행·기록 단계의 상용 기준. 2026-04 출시, 성능은 비공개 |

## 단계별로 빌릴 것과 FlowDelta만의 빈칸

**①②는 거의 빌려 쓰고, 힘은 ③ 노이즈를 뺀 행위 diff와 ④ 행위↔코드 연결에 써야 합니다.**

| 단계 | 빌려올 것 | FlowDelta가 새로 해야 할 것 |
| --- | --- | --- |
| ① 버전 고정 | mcp-scan·skillwarden의 해시 고정, n8n 워크플로 diff(JSON) | 스킬 폴더 전체 + 외부 참조 URL 내용까지 함께 고정 |
| ② 로컬 실행·기록 | package-analysis의 큐-샌드박스-저장 구조, USENIX '26의 미끼 자격증명·반복 실행 | **두 버전에 같은 입력·같은 환경**을 주는 실행 시나리오 (스킬: 같은 사용자 요청, n8n: 같은 트리거 데이터) |
| ③ 행위 diff | Diffy의 노이즈 상쇄(v1 2회 + v2 1회), Harden-Runner의 "처음 보는 연결" 판정 | LLM 비결정성을 견디는 비교 단위 정의 (예: 연결한 도메인 집합, 읽은 민감 경로 집합, 실행한 명령 종류) |
| ④ 판정·증거 | Spectra Assure의 동일 조건 비교, Semgrep의 "새 발견만" 보고 | **행위 차이를 바뀐 파일·줄·노드에 연결**해 "이 변경이 이 행위를 만들었다"는 근거 제시 |

**연구 공백 (캡스톤 규모로 할 수 있는 순)**

1. **스킬·n8n 대상 두 버전 실행 비교 자체.** 이번 조사에서 공개 연구·도구를 찾지 못했습니다. 가장 가까운 LifecycleGuard도 원문을 확인해 보니 지시문만 비교하고 실행하지 않았습니다.
2. **노이즈 상쇄의 효과 측정.** 같은 표본에서 "v2 단독 검사" vs "v1 대비 차이만 검사"의 오탐률을 비교하면, FlowDelta의 핵심 주장을 수치로 보여 줄 수 있습니다.
3. **정상 업데이트 vs 악성 업데이트 쌍 데이터셋.** 기존 스킬 벤치마크(MaliciousSkillBench 등)는 단일 버전이라, 버전 쌍을 직접 만들어야 합니다. Garrett의 8개 특징이 쌍을 설계할 때 체크리스트가 됩니다.

**한계로 미리 말해 둘 것:** 실행하지 않은 경로(조건부·지연 트리거)는 두 버전 모두에서 안 보입니다. USENIX '26에서도 미확정 후보의 93.2%가 60초 안에 발현되지 않았습니다.

## 출처와 미확인 범위

**동료심사**

- Garrett, Ferreira, Jia, Sunshine, Kästner, [*Detecting Suspicious Package Updates*](https://www.cs.cmu.edu/~ckaestne/pdf/icsenier19.pdf), ICSE 2019 NIER
- Kessel, [*Treating Run-time Execution History as a First-Class Citizen* (BeCoV)](https://arxiv.org/abs/2604.16933), FSE 2026
- Vu et al., [*LastPyMile*](https://2021.esec-fse.org/details/fse-2021-papers/61/LastPyMile-Identifying-the-Discrepancy-between-Sources-and-Packages), ESEC/FSE 2021
- Liu et al., [*"Do Not Mention This to the User"*](https://arxiv.org/html/2602.06547v4), USENIX Security 2026
- [OSCAR](https://arxiv.org/abs/2409.09356v1), ASE 2024 산업 트랙

**프리프린트·2차 출처**

- LifecycleGuard (arXiv 2607.13987): [promptfoo 취약점 DB 요약](https://promptfoo.dev/lm-security-db/vuln/lifecycle-poisoning-of-reusable-agent-skills-fc8f356e)으로만 확인
- Hossain et al., [SkillVetBench](https://arxiv.org/abs/2606.00925) · Ji et al., [SkillDetonate](https://arxiv.org/abs/2607.02357)

**오픈소스·공식 문서·기업 자료·특허**

- [Diffy](https://github.com/opendiffy/diffy) · [BehaviorDiff](https://github.com/abheeshtroy/BehaviorDiff) · [OpenSSF package-analysis](https://github.com/ossf/package-analysis) · [Harden-Runner](https://github.com/step-security/harden-runner) · [Harden-Runner 오경보 사례](https://www.stepsecurity.io/blog/harden-runner-detects-new-traffic-to-release-assets-githubusercontent-com-across-multiple-customers) · [mcp-scan 소개](https://invariantlabs.ai/blog/introducing-mcp-scan) · [skillwarden](https://github.com/coltonbearden/skillwarden) · [install-then-update-trap-detector](https://getclawkit.com/skills/official-andyxinweiminicloud-install-then-update-trap-detector) · [n8n 버전 비교 문서](https://docs.n8n.io/administer/use-source-control-and-environments/compare-versions)
- [Spectra Assure 패키지 diff](https://docs.secure.software/cli/guides/package-diff) · [Socket for GitHub](https://docs.socket.dev/docs/socket-for-github) · [Semgrep CI 문서](https://docs.semgrep.dev/deployment/customize-ci-jobs) · [Permiso SandyClaw](https://permiso.io/blog/introducing-sandyclaw-dynamic-sandbox-ai-agent-skills)
- [US 12223045 특허 문서](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12223045)

**미확인·조사하지 못한 것**

- **LifecycleGuard (해결, 2026-10-07):** [원문](https://arxiv.org/html/2607.13987v1)을 확인했습니다. Badhe & Tiwari(Google)의 연구이며, 스킬을 **실행하지 않고** 이전·새 지시문의 벡터 거리와 출처만 비교합니다. 악성 업데이트 탐지율은 92.5%지만 \*\*오탐률이 37.0%\*\*입니다. 앞서 적은 "100% → 23%"는 별도의 런타임 실험 수치였습니다. → FlowDelta의 실행 비교 차별점은 유지됩니다.
- **US 12223045 특허 (해결):** Trend Micro가 출원했고 현재 권리자는 VicOne입니다. 2022-08-24 출원, 2025-02-11 등록 ([Google Patents](https://patents.google.com/patent/US12223045B1/en)).
- **Spectra Assure·Socket (해결):** 둘 다 **정적 분석만** 합니다 ([Spectra Assure](https://docs.secure.software/concepts/spectra-assure-analysis), [Socket](https://docs.socket.dev/docs/socket-for-github)).
- **Ohm et al., ARES 2020 (부분 해결):** 설치 중 아티팩트를 동적으로 관찰하는 방식으로 확인됐지만([Amalfi 논문의 설명](https://arxiv.org/pdf/2202.13953)), 버전 비교 여부는 본문 접근이 막혀 여전히 미확인입니다.
- **새로 찾은 자료:** [diff-CodeQL (SCORED '23)](https://www.plai.ifi.lmu.de/publications/scored23-diff-codeql.pdf)은 두 버전의 CodeQL 결과 차이만 보고해 악성 업데이트 9건을 모두 잡았고 오탐률은 1.4%였습니다. Amalfi도 버전 간 변화 특징을 쓰는 것으로 확인됐습니다.
- **FlowDelta 팀 확정 설계:** 문헌으로 확인할 수 없어 다음 팀 회의 안건으로 남깁니다.
- 세부 내용은 GitHub `docs/junseo/research/`의 추가 조사 문서에 정리했습니다.
