# AI 워크플로 프레임워크 생태계 지형

조사일 2026-09-19 · 조사자 김민우

> **왜 이 조사가 필요한가**: 제안서는 검사 대상을 "AI 워크플로 구성요소"라고 부르지만,
> 그 생태계 전체가 어떻게 생겼는지는 정리된 적이 없다. 범위를 정하려면 먼저
> **무엇이 있는지**와 **우리가 건드리는 것이 그중 어디인지**를 알아야 한다.
>
> 결론부터: 생태계는 **12개 계층**으로 나뉘고, 우리 검사 대상은 그중 **4개 계층**이다.
> 그 4개는 공통점이 있다 — **에이전트가 "읽는" 것**이지 에이전트를 "돌리는" 것이 아니다.

---

## 전체 지형 한눈에

```
                      ┌─────────────────────────────────────────┐
  사람이 쓰는 것       │ ① 실행 호스트 (코딩 에이전트 CLI·IDE)      │
                      ├─────────────────────────────────────────┤
  ★ 에이전트가        │ ② 지침·컨텍스트   AGENTS.md · SKILL.md   │ ← 검사 대상
     읽는 것          │ ③ 도구 연결 프로토콜   MCP · A2A · ACP    │ ← 검사 대상
                      │ ⑥ 메타 프레임워크   SuperClaude · BMAD    │ ← 검사 대상
                      │ ⑪ 레지스트리·마켓   skills.sh · ClawHub  │ ← 유통 경로
                      ├─────────────────────────────────────────┤
                      │ ④ 에이전트 프레임워크 (코드)              │
  개발자가 조립       │ ⑤ 노코드·로우코드 워크플로 빌더            │
                      ├─────────────────────────────────────────┤
                      │ ⑦ 실행 격리·샌드박스                     │
  인프라              │ ⑧ 내구 실행·오케스트레이션                │
                      │ ⑨ 관측·평가                             │
                      │ ⑩ 가드레일·정책                          │
                      │ ⑫ 보안 검사 도구                         │
                      └─────────────────────────────────────────┘
```

---

## ① 실행 호스트 — 코딩 에이전트 CLI·IDE

에이전트가 실제로 돌아가는 곳. 지침 파일을 읽고 도구를 호출하는 주체다.

| 제품 | 형태 | 규모 |
|---|---|---|
| **GitHub Copilot** | IDE 확장 | 시장점유율 **42%**, 사용자 2,000만+ |
| **Claude Code** | CLI + 데스크톱 + 웹 + IDE 확장 | 점유율 **28%**, NPS +58, 선호도 **46%**(1위) |
| **Cursor** (Anysphere) | IDE | 활성 사용자 **500만+**, ARR $2B, 기업가치 $10B+ |
| **Cline** | 오픈소스 | H1 2026까지 설치 **100만+** |
| **Codex** (OpenAI) | CLI + 클라우드 | — |
| Aider · Gemini CLI · Windsurf · opencode | CLI·IDE | 롱테일 |

**관찰**: 한 개발자가 하루에 Copilot으로 "쓰고", Cursor에서 "개발하고", Claude Code를
"꺼내 쓴다". **단일 도구 환경이 아니다** — 같은 지침 파일이 여러 호스트에서 읽힌다.
이게 ②계층에서 크로스툴 표준(AGENTS.md)이 뜬 이유다.

---

## ② 지침·컨텍스트 계층 ★ 검사 대상

에이전트가 **작업 지침으로 읽는** 마크다운. 코드가 아니다.

| 형식 | 소유 | 규모·상태 |
|---|---|---|
| **AGENTS.md** | 크로스툴 | **저장소 60,000개+** 채택. 정식 관리 주체가 **Linux Foundation으로 이관** |
| **CLAUDE.md** | Claude Code | AGENTS.md를 명시적 import로 처리 |
| **.cursorrules** | Cursor | |
| **Agent Skills (SKILL.md)** | 오픈 표준 | 2025-12 `agentskills.io`로 표준화. **약 40개 플랫폼 지원** (OpenAI Codex, GitHub Copilot, Snowflake Cortex Code 등) |

**Agent Skills 구조** — 폴더 하나에 `SKILL.md`(YAML 프런트매터 + 마크다운 본문)와
선택적 `scripts/` · `references/` · `assets/`.

**Progressive disclosure (3단계 로딩)** — 컨텍스트 비용을 통제하는 모델:

| 단계 | 내용 | 로딩 시점 |
|---|---|---|
| Level 1 | 메타데이터(name, description) | 설치된 모든 스킬에 대해 **항상** |
| Level 2 | SKILL.md 본문 | 작업이 해당 스킬을 **유발했을 때** |
| Level 3 | 동봉 파일 | 본문이 **참조했을 때** |

> **보안적으로 중요**: Level 3는 참조될 때만 읽힌다. 즉 **첫 마크다운 파일만 검사하면
> 뒤에서 읽히는 문서나 보조 코드가 빠진다.** 제안서가 지적한 BMAD 사례가 정확히 이것이다.

**우리와의 관계**: 이 계층이 프로젝트의 1차 검사 대상이다. **패키지가 아니라 마크다운**이라
lockfile·semver·레지스트리 무결성 검사가 원천적으로 적용되지 않는다.

---

## ③ 도구 연결 프로토콜 ★ 검사 대상

에이전트와 외부 도구·다른 에이전트를 잇는 규약.

| 프로토콜 | 주체 | 역할 | 상태 |
|---|---|---|---|
| **MCP** | Anthropic → LF | 에이전트 ↔ **도구** | 월 SDK 다운로드 **9,700만**(2026-03). Anthropic·OpenAI·Google·Microsoft·AWS·Cursor·JetBrains **전부 네이티브 지원** |
| **A2A** | Google → LF | 에이전트 ↔ **에이전트**. Agent Card로 상호 발견·위임 | v1.0.1(2026-05)에서 확장 메커니즘 추가 |
| **ACP** | — | REST·async 우선 기업 메시징. 멀티파트 MIME, **오프라인 발견**(에어갭) | |
| **ANP** | — | 에이전트 네트워크 | |
| **AGNTCY** | Cisco → LF | OASF(스키마) + SLIM(메시징). A2A·MCP의 **대체가 아니라 기반 인프라** | |

**통합 움직임** — 2025년 12월 Linux Foundation이 **Agentic AI Foundation(AAIF)** 을 출범시켜
MCP·A2A와 관련 인프라를 중립 재단 아래 모았다.

> MCP는 "에이전트가 도구에 접근하는 법"을 풀었지만 "한 에이전트가 다른 에이전트에게
> 일을 넘기는 법"은 남겼다. 그 자리를 A2A가 채운다.

**주의** — 연구 논문 *"Governance Gaps in Agent Interoperability Protocols:
What MCP, A2A, and ACP Cannot Express"* 가 지적하듯, **이 프로토콜들은 거버넌스를
표현하지 못한다.** 누가 무엇을 해도 되는지는 프로토콜 밖의 문제다. 우리 프로젝트가
서 있는 자리이기도 하다.

---

## ④ 에이전트 프레임워크 — 코드로 짜는 것

2026년에 오케스트레이션 스타일이 **4가지로 정리**됐다.

| 스타일 | 대표 | 특징 |
|---|---|---|
| **그래프 기반** | **LangGraph**, Microsoft Agent Framework | 상태 기반 프로덕션 워크플로의 기본값. 감사 추적·결정론적 제어·사람 승인 단계가 필요한 규제 환경에 강함. 체크포인팅·스트리밍·LangSmith 연동 |
| **역할 기반** | **CrewAI**, Agno | 아이디어 → 멀티에이전트 프로토타입 최단 경로. LangGraph보다 배포 **40% 빠름**. 단 팀이 나중에 성장해 벗어나는 경우가 많음 |
| **핸드오프 기반** | **OpenAI Agents SDK** | GPT 중심 에이전트의 최소 마찰 선택지. 샌드박스 도구·서브에이전트 |
| **계층 기반** | **Google ADK** | Gemini 최적화. 다른 모델도 지원. 가장 최신 |

그 외: **AutoGen**(대화 중심 합의 구조라 느림) → **AG2**(이벤트 기반·비동기로 계승),
**Claude Agent SDK**, **Strands**, **Pydantic AI**, **smolagents**.

모델 중립: LangGraph · CrewAI · AutoGen · smolagents.
모델 종속이지만 셋업 최단: OpenAI Agents SDK.

---

## ⑤ 노코드·로우코드 워크플로 빌더

**2026년의 가장 큰 변화가 일어난 계층.** 단순 워크플로 빌더에서 **완전한 에이전틱
플랫폼**으로 바뀌었다 — 자율 에이전트, 멀티모델 오케스트레이션, human-in-the-loop 제어,
그리고 **MCP 채택**.

| 제품 | 정체 | 강점 |
|---|---|---|
| **n8n** | **워크플로 엔진** | GitHub **182,000+ stars**, 7년 개발. AI가 큰 워크플로의 일부일 때. 재시도·분기·스케줄·실행 로그 |
| **Dify** | **LLM 앱 플랫폼** | 데이터셋·프롬프트·앱 배포를 한 곳에. RAG + 에이전트 + 모니터링 올인원 |
| **Flowise** | **LangChainJS 캔버스** | 벡터스토어·모델·도구를 한 화면에서 연결하고 바로 테스트 |
| **Langflow** | **Python LangChain GUI** | 팀이 Python 기반일 때. MCP **클라이언트·서버 양방향** 네이티브 |
| **Activepieces** | 자동화 | **MCP 서버 280개+** 로 선두 |
| StackAI · Make · Zapier | 상용 | |

> MCP가 **"AI 통합의 USB-C"** 가 됐다. 이 플랫폼들이 이제 도구를 MCP 서버로 내보내고
> MCP 클라이언트로 소비한다. **③계층이 ⑤계층을 관통한다.**

---

## ⑥ 메타 프레임워크 — 방법론 번들 ★ 검사 대상

개별 스킬이 아니라 **작업 방식 전체를 묶어 배포**하는 것.

| 이름 | 구성 |
|---|---|
| **SuperClaude** | `commands` · `agents` · `modes` · `mcp` · `skills` 디렉터리. 명령이 참조하는 지침과 MCP 도구를 **함께 확인해야** 함 |
| **BMAD** | `SKILL.md` 외에 `workflow.md`, 단계별 문서, 참고자료, 검토 프롬프트. **첫 마크다운만 검사하면 뒤에서 읽는 문서가 빠짐** |
| Anthropic PDF 스킬 | `SKILL.md` + `forms.md` + `reference.md` + `scripts/`. 스킬 하나도 문서와 실행 코드의 결합 배포 단위가 될 수 있음 |

**우리와의 관계**: 이 계층이 **검사 범위 산정의 난이도**를 결정한다. 배포 단위 하나가
여러 파일·여러 종류를 품고 있어서, "무엇을 검사했고 무엇을 못 했는지"를 명시하지 않으면
검사 결과 자체가 오해를 만든다.

---

## ⑦ 실행 격리 — 샌드박스

에이전트가 **생성한 코드**를 격리 실행하는 계층. 우리 프로젝트가 **의도적으로 안 하는** 영역.

| 제공자 | 격리 기술 | 특징 |
|---|---|---|
| **E2B** | **Firecracker microVM** | 샌드박스마다 자체 Linux 커널. 부팅 약 **150ms**. 컨테이너 격리가 남기는 교차 탈출을 막음. 보안 격리·SDK 편의성 1위 |
| **Modal** | **gVisor** (유저스페이스 커널) | 시스템콜을 호스트 커널 도달 전에 가로챔. 콜드스타트 1초 미만. **GPU 접근이 쉬움** |
| **Daytona** | | |
| **GKE Agent Sandbox** · **Amazon Bedrock AgentCore Runtime** | 클라우드 네이티브 | |
| Cloudflare Sandbox · Vercel Sandbox | 엣지 | |

---

## ⑧ 내구 실행 — 오케스트레이션 런타임

에이전트를 **장시간 살아 있는 워크플로**로 다루는 계층.

**Temporal** — 에이전트를 Temporal Workflow로 돌리면 상태가 자동 영속되고, 크래시나
서버 재시작 후 **중단 지점에서 재개**되며, 입력을 기다리는 동안 **컴퓨트를 0으로** 쓴다.
에이전트 수명주기를 프로세스가 아니라 Temporal이 관리한다. **Sandbox Orchestration
Harness** 로 실행 중인 에이전트를 다른 샌드박스 제공자로 **포크**할 수도 있다.

OpenAI도 자체 블로그에서 샌드박스 에이전트의 핵심 역량으로 durable execution을 꼽았다.

그 외: **Inngest**, **Restate**.

---

## ⑨ 관측·평가

LLM 트레이스를 1급 객체로 다루는 계층. 에이전트·리트리버·도구에 걸친 중첩 스팬을
수집하고 프로덕션 트래픽에 평가 점수를 붙인다.

| 제품 | 성격 |
|---|---|
| **Langfuse** | **오픈소스·자체호스팅.** 트레이싱 + 평가 + 비용 분석 통합. 종합 1순위 |
| **LangSmith** | LangChain/LangGraph **최심 통합**. 독점, 볼륨 기반 과금 |
| **Arize Phoenix** | **OpenTelemetry 네이티브**, OpenInference 시맨틱 규약. 오픈소스 |
| **Braintrix**(Braintrust) | 비기술 이해관계자와 빠른 프로토타이핑. 자체호스팅 불가 |
| **Helicone** | 드롭인 프록시. 설치 최단 |
| **Datadog LLM Observability** · **Honeycomb** | 기존 관측 스택 보유 기업 |

---

## ⑩ 가드레일·정책

사용자 ↔ LLM ↔ 시스템 사이에 앉는 **런타임 보안·품질 계층**. 입력(프롬프트),
출력(응답), 그리고 점점 **그 사이의 행위**(도구 호출·파라미터·권한)까지 검사해
허용 / 플래그 / 차단을 집행한다.

**4개 계열**:

| 계열 | 예 |
|---|---|
| 오픈소스 조립형 | **NVIDIA NeMo Guardrails** (Colang 이벤트 모델링 언어), **Guardrails AI**, **LLM Guard** |
| 클라우드 네이티브 필터 | **Amazon Bedrock Guardrails**, **Azure AI Content Safety** |
| 보안 스위트 흡수형 | 2024~2026 사이 대형 벤더에 인수·통합된 것들 |

**다층 방어 예시(7계층)** — NeMo 입력 레일 → 조직별 명령 정책 → 정적 위협 시그니처
매칭 → LLM 안전 판정자 → **사람 승인 게이트** → 샌드박스 파드 실행 → 출력 비밀정보 삭제.

> 우리 프로젝트는 이 계층이 **아니다.** 가드레일은 런타임에 행위를 막고,
> 우리는 도입 전에 근거를 보여 준다. 발표에서 헷갈리면 "그거 NeMo 쓰면 되지 않냐"는
> 질문을 받는다.

---

## ⑪ 레지스트리·마켓플레이스 ★ 유통 경로

| 레지스트리 | 대상 | 규모 |
|---|---|---|
| **MCP Registry** (공식) | MCP 서버 | 서버 **9,652개** / 서버-버전 레코드 **28,959개** (2026-05) |
| **skills.sh** (Vercel) | Agent Skills | **가장 활발한 레지스트리.** Anthropic·GitHub·OpenAI·커뮤니티 스킬 호스팅. 69,000개+ |
| **ClawHub** | OpenClaw 스킬 | 2,857개 → **10,700개+** (2026년 중 급성장) |
| GitHub 직접 | 전부 | 레지스트리 없이 `git clone`·zip 배포 |

> **이 계층이 공급망 사고가 실제로 발생한 곳이다.** ClawHavoc(악성 스킬 341→1,184개),
> postmark-mcp 백도어, Oura MCP 복제본 전부 여기서 나왔다.
> 자세한 내용은 [실제사례와_통계.md](실제사례와_통계.md).

---

## ⑫ 보안 검사 도구

별도 조사 완료 — [선행조사_생태계와_기존연구.md](선행조사_생태계와_기존연구.md) 참고.

요약: NVIDIA **SkillSpector**(Apache-2.0) · **AgentShield**(MIT) · Snyk **agent-scan** ·
Cisco **Skill/MCP Scanner·DefenseClaw** · **MCP-Scan**(피닝) · **skillfence**(런타임).

---

## 우리 프로젝트가 서 있는 자리

### 검사 대상 = "에이전트가 읽는 것"

12개 계층 중 우리가 건드리는 건 ②③⑥⑪이다. 공통점이 명확하다:

| | 우리 검사 대상 (②③⑥⑪) | 나머지 계층 |
|---|---|---|
| 정체 | 에이전트가 **읽는** 것 | 에이전트를 **돌리는** 것 |
| 형태 | 마크다운·설정·메타데이터 | 코드·인프라·서비스 |
| 배포 | git clone · zip · 복붙 | 패키지 매니저 · 컨테이너 |
| 기존 방어 | lockfile·semver·무결성 검사 **원천 미적용** | 성숙한 공급망 보안 존재 |

**이 표 한 장이 "그냥 npm 공급망 문제 아니냐"에 대한 답이다.**

### 이 계층이 사라지지 않는다는 근거

범위를 여기로 좁혀도 되는지 판단할 때 쓸 수 있는 신호:

- AGENTS.md — 저장소 **60,000개+**, 관리 주체가 **Linux Foundation으로 이관**
- Agent Skills — 2025-12 오픈 표준화, **약 40개 플랫폼** 지원
- MCP — 월 SDK 다운로드 **9,700만**, **모든 주요 제공자**가 네이티브 지원
- AAIF(2025-12) 출범으로 MCP·A2A가 중립 재단 아래 통합

**표준화되고 있다는 건 대상이 안정된다는 뜻이고, 검사 도구를 만들 가치가 있다는 뜻이다.**
반대로 아직 표준이 없었다면 학기 중에 형식이 바뀌어 버릴 위험이 있었다.

### 헷갈리면 안 되는 인접 계층

| 계층 | 왜 우리가 아닌가 |
|---|---|
| ⑩ 가드레일 | **런타임에 행위를 차단**한다. 우리는 도입 전 근거 제시 |
| ⑦ 샌드박스 | **실행**이 전제. 우리는 정적으로만 읽음 |
| ⑨ 관측 | **실행 후** 트레이스 수집. 우리는 실행 전 |
| ④⑤ 프레임워크·빌더 | 만드는 도구. 우리는 **가져온 것을 검사** |

---

## 확인하지 못한 것

- 각 계층의 **한국 시장 사용률** — 국내 통계를 찾지 못했다
- ⑤계층 제품들이 스킬·MCP를 **어떤 형식으로 내보내는지** 실제 확인 필요
  (우리 검사 대상 형식과 호환되는지가 범위 확장 가능성을 결정)
- 시장점유율 수치(Copilot 42%, Claude Code 28%, Cursor 5M)는 **출처마다 측정 기준이 다르다.**
  사용자 수·설치 수·선호도를 섞어 인용하면 안 된다
- A2A·ACP·ANP의 **실제 프로덕션 채택률** — 사양은 공개됐으나 사용 통계는 확인 못 함

---

## 참고 자료

확인일 2026-09-19.

**프레임워크**
- [The best AI agent frameworks in 2026 — LangChain](https://www.langchain.com/resources/ai-agent-frameworks)
- [AI Agent Frameworks Compared (2026) — Agentmelt](https://agentmelt.com/blog/ai-agent-frameworks-compared-2026/)
- [2026 AI Agent Framework Showdown — QubitTool](https://qubittool.com/blog/ai-agent-framework-comparison-2026)

**노코드·로우코드**
- [n8n vs Flowise vs Langflow — Hugging Face Blog](https://huggingface.co/blog/daya-shankar/n8n-vs-flowise-vs-langflow-enterprises)
- [Top 7 Open-Source AI Low/No-Code Tools in 2026](https://htdocs.dev/posts/top-7-open-source-ai-lowno-code-tools-in-2026-a-comprehensive-analysis-of-leading-platforms/)
- [Flowise vs Dify vs n8n — Jahanzaib](https://www.jahanzaib.ai/blog/flowise-vs-dify-vs-n8n-ai-agents)

**프로토콜**
- [Agent Interoperability Protocols: MCP, A2A, OSI Explained (2026) — Atlan](https://atlan.com/know/agent-interoperability-protocols/)
- [Top AI Agent Protocols in 2026 — GetStream](https://getstream.io/blog/ai-agent-protocols/)
- [A Survey of Agent Interoperability Protocols (MCP/ACP/A2A/ANP)](https://arxiv.org/html/2505.02279v1)
- [Governance Gaps in Agent Interoperability Protocols](https://arxiv.org/pdf/2606.31498)

**지침 계층**
- [Standardize project context with AGENTS.md and Agent Skills — Red Hat Developer](https://developers.redhat.com/articles/2026/07/27/standardize-project-context-agentsmd-and-agent-skills)
- [Agent Skills Explained: SKILL.md Format and Adoption (2026) — Atlan](https://atlan.com/know/ai-agent/ai-agent-skills/what-are-agent-skills/)
- [The Agent Skills Open Standard — Adoption and the Governance Gap](https://anomity.ai/blog/agent-skills-open-standard-adoption-governance/)
- [AGENTS.md Spec (2026) — Morph](https://www.morphllm.com/agents-md-guide)

**코딩 에이전트**
- [Every AI Coding CLI in 2026: The Complete Map (30+ Tools)](https://dev.to/soulentheo/every-ai-coding-cli-in-2026-the-complete-map-30-tools-compared-4gob)
- [AI Coding Agent Market Share 2026](https://andrew.ooo/answers/ai-coding-agent-market-share-cursor-claude-code-copilot-july-2026/)
- [Agentic Coding Tools: The Q2 2026 Landscape — Zylos](https://zylos.ai/research/2026-06-25-agentic-coding-tools-q2-2026-landscape/)

**샌드박스·런타임**
- [Best Code Execution Sandboxes for AI Agents in 2026 — Modal](https://modal.com/resources/best-code-execution-sandboxes-ai-agents)
- [Temporal Sandbox Orchestration Harness](https://temporal.io/blog/temporal-sandbox-orchestration-harness-the-missing-layer-for-running-agents)
- [Daytona vs E2B in 2026 — Northflank](https://northflank.com/blog/daytona-vs-e2b-ai-code-execution-sandboxes)

**관측·가드레일**
- [Top LLM Observability and Evaluation Platforms in 2026 — MarkTechPost](https://www.marktechpost.com/2026/08/09/top-llm-observability-and-evaluation-platforms-in-2026-langfuse-langsmith-braintrust-arize-and-more-compared/)
- [Best 9 AI guardrails in 2026 — Giskard](https://www.giskard.ai/knowledge/ai-guardrails-comparison-2026)
- [AI Agent Guardrails in Production: 7 Layers (2026)](https://www.aurorasre.ai/blog/ai-agent-guardrails)
