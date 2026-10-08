# AI 도구 6종이 제공하는 서비스

확인일: 2026-10-07 KST. 목적: FlowDelta와의 기능 비교에 앞서 각 제품의 서비스 성격, 입력, 사용 흐름, 결과, 오픈소스/상용 구분을 설명한다.

제공된 6개 URL을 직접 요청했다. Snyk GitHub 페이지는 HTTP 200, 나머지 5개 사이트는 네트워크 프록시의 CONNECT 403으로 열리지 않았다. Promptfoo·Giskard·LangSmith·n8n은 공식 GitHub에 공개된 해당 문서와 인접 서비스 설명 원본을 읽었다. Cisco는 지정된 Explorer 블로그를 읽지 못했고, 대신 공식 AI Defense SDK·CLI·조직 소개를 확인했다. **SDK의 전체 플랫폼 기능을 Explorer Edition 제공 범위로 해석하지 않는다.** 제품 설치, 계정 로그인, 실제 공격·평가·차단은 실행하지 않았다. 최신 저장소 문서는 설치 릴리스와 다를 수 있다.

## Promptfoo

**서비스 성격:** LLM 애플리케이션을 위한 품질 평가·보안 공격 시험 도구다. 일반 평가와 red teaming이라는 두 주요 사용 흐름이 있고, 오픈소스 CLI/라이브러리와 기업용 플랫폼으로 제공된다.

일반 평가는 사용자가 여러 prompt/model/provider와 시험 입력·기준 답·assertion을 정의하면 조합별로 실행하고 결과를 나란히 비교한다. 사용 목적은 프롬프트 수정 후 정확도가 떨어졌는지, 모델 교체가 비용·품질에 어떤 영향을 주는지, 출력 형식과 업무 규칙을 지키는지 확인하는 것이다. caching·concurrency·web viewer·CI/CD 연동도 제공한다.

red teaming은 대상 애플리케이션의 목적과 연결 방법을 설정하고, 공격 plugin과 strategy를 선택하는 흐름이다. plugin은 특정 위험의 공격 입력을 만들고 strategy는 그 입력에 공격 방식을 적용한다. 공식 빠른 시작은 생성된 시험을 `redteam.yaml`에 저장하고 target에 실행한 뒤 위험 보고서를 보는 절차를 설명한다. 보안 범위에는 prompt injection, jailbreak, RAG poisoning, 정보 노출, 권한 위반, 다중 턴 공격 등이 있다. 사용자 지정 조직 정책도 시험에 사용할 수 있다.

대상 연결은 HTTP endpoint·모델 provider·custom code·browser 등의 adapter를 활용한다. MCP provider는 도구 호출을 지원하고, 지원 chat provider의 실제 MCP 호출은 `metadata.toolCalls`에 기록한다. OpenTelemetry tracing은 도구 실행과 guardrail·오류 등 span을 trajectory로 정규화해 grader와 공격 전략에 제공할 수 있다. 도구 사용·인수·순서 등 결정적 assertion도 있어 최종 응답 문장만 검사하는 도구로 보면 안 된다.

**입력:** prompts, test cases, target/provider 설정, 공격 범주·전략, 조직 정책, 선택적 trace.

**결과:** 조합별 응답·평가 결과, 위험 분류별 보고서, 실행 trace와 호출 기록, JSON/HTML/JUnit 등의 결과 export와 CI 판정.

**제공 형태:** Community는 로컬 CLI/라이브러리다. Enterprise는 hosted SaaS, Enterprise On-Prem은 자체 인프라와 dedicated runner를 제공한다. 기업용 문서는 팀/RBAC, target/plugin 구성 관리, reporting·remediation, SIEM/issue tracker 통합, 조직별 공유와 전문 지원을 설명한다. 문서 비교표는 Community의 red teaming·remediation·sharing·API를 제한적 제공으로 표시하지만 구체 수량은 이번에 확인한 문서에 없다. 로컬 실행과 원격 모델·공격 생성기 호출은 별개다.

**사용 예:** 고객 상담 에이전트에 공격 입력을 보내 개인정보 조회·금지 도구 호출 여부를 검사하고, 모델이나 prompt 수정 후 같은 시험을 반복한다. 실제 수신처에 데이터가 도착했는지 독립 확인하는 환경은 별도로 연결해야 한다.

출처: [제품 소개](https://github.com/promptfoo/promptfoo/blob/main/site/docs/intro.md), [빠른 시작](https://github.com/promptfoo/promptfoo/blob/main/site/docs/red-team/quickstart.md), [에이전트 시험](https://github.com/promptfoo/promptfoo/blob/main/site/docs/red-team/llm-agents.md), [기업용 서비스](https://github.com/promptfoo/promptfoo/blob/main/site/docs/enterprise/index.md).

## Giskard

**서비스 성격:** 에이전트·LLM/RAG의 품질, 안전성, 업무 실패를 시험하는 Python 라이브러리와 기업용 팀 평가 플랫폼이다. 현재 공식 문서는 OSS와 Hub를 구분한다.

OSS v3는 `giskard-checks`와 `giskard-scan` 중심이다. target을 callable로 연결하고, Scenario에 메시지/대화와 Check를 배치하고, 여러 Scenario를 Suite로 실행한다. Check는 문자열·regex·semantic similarity·LLM judge 등으로 답변이나 trace를 평가한다. `vulnerability_scan`은 에이전트 설명에서 공격 시나리오를 생성하고, `quality_scan`은 지식 자료를 사용하는 RAG 품질 실패를 평가한다. scan은 기본 설치에 포함되지 않아 별도 extra가 필요하다. LLM 생성기와 judge를 사용하는 기능은 provider 접근·키·비용이 필요하다. README는 v3와 더 이상 적극 유지되지 않는 v2를 구분한다.

**Hub**는 프로젝트·에이전트·dataset·knowledge base·scan·evaluation을 함께 관리하는 상용 작업 공간이다. UI에서 대상 API, 인증 header, 지원 언어, agent 설명을 등록한다. Chat 또는 custom JSON 기반 Structured agent를 연결하고, 문서를 knowledge base로 가져와 시험 생성에 활용할 수 있다.

Hub의 업무 순서는 **scan → scenario/dataset 생성 → 사람의 annotation과 check 검토 → evaluation 실행 → 결과 검토·비교 → 수정·재시험**이다. 코드 작성자뿐 아니라 업무 담당자가 실패 분류와 정답·판정 기준 검토에 참여할 수 있다. 예약 평가, 지속적 red teaming, alert, 데이터셋 중앙 관리·versioning, 사용자/RBAC, SSO·2FA·audit 기능을 문서가 설명한다. SDK는 이 흐름을 Python/CI에서 자동화한다.

**입력:** 대상 agent API/callable, 설명·언어, 시험 대화, checks, 지식 자료, dataset.

**결과:** 취약/업무 실패 사례, scenario별 check 결과, 평가 지표, 비교 기록, 검토·annotation와 실패 후속 task.

**제공 형태:** OSS는 개발자·연구자의 programmatic/local workflow, Hub는 UI·SDK를 제공하는 enterprise 플랫폼이다. Hub 문서는 on-premise 문의 경로를 제공하지만 모든 고객에게 동일한 배포 옵션·가격을 제공한다고 확인한 것은 아니다. 공식 비교표는 tool/function calling tests와 지속적 red teaming을 Hub의 제공 항목으로 구분한다. OSS의 custom target/trace Check 확장 가능성과 Hub의 내장 제품 기능을 동일시하지 않는다. 비교표의 “외부 의존성 없음”이라는 일반 설명도 실제 LLM provider 요청이 없는 것으로 해석하지 않는다.

**사용 예:** 기업 문서를 바탕으로 시험 질문을 생성하고, 잘못된 답변·근거 부족·업무 규칙 위반을 사람이 검토해 regression dataset으로 유지한다. 보안 공격 입력도 같은 품질 관리 흐름으로 재실행한다.

출처: [문서 홈 원본](https://github.com/Giskard-AI/giskard-docs/blob/main/src/content/docs/index.mdx), [Hub UI](https://github.com/Giskard-AI/giskard-docs/blob/main/src/content/docs/hub/ui/index.mdx), [Hub SDK](https://github.com/Giskard-AI/giskard-docs/blob/main/src/content/docs/hub/sdk/index.mdx), [OSS/Hub 비교](https://github.com/Giskard-AI/giskard-docs/blob/main/src/content/docs/start/comparison.mdx), [OSS README](https://github.com/Giskard-AI/giskard-oss/blob/main/README.md).

## Cisco AI Defense

**확인 범위:** 제공된 링크는 Agent Validation Explorer Edition 소개 블로그지만 본문을 읽지 못했다. 아래는 Cisco가 공개한 SDK·CLI에서 확인한 **전체 AI Defense 플랫폼의 통합 기능**이다. Explorer의 실제 공격 인터페이스, 무료 제한, 지원 대상, 독립 관측 방식은 미확인이다.

Cisco AI Defense는 운영 중 AI 애플리케이션의 보안·privacy·safety 검사와 중앙 정책 관리까지 제공하는 enterprise 보안 플랫폼이다. 공식 Python SDK는 다음 서비스를 연결한다.

- **Chat Inspection:** prompt·response·대화 검사.
- **HTTP Inspection:** HTTP 요청과 응답 검사.
- **MCP Inspection:** tool-call, resource-read, response 등 JSON-RPC 메시지의 위험 검사. PII/PCI/PHI 같은 데이터 노출에 관한 검사도 설명한다.
- **Agent Runtime SDK:** 지원 LLM/MCP client를 patch해 상호작용을 검사. API mode는 검사를 거쳐 provider를 호출하고, Gateway mode는 트래픽을 AI Defense gateway로 전달한다. `monitor`는 기록, `enforce`는 차단, `off`는 검사 비활성이라는 모드 예시가 있다.
- **Validation API:** 등록된 application 등에 validation job을 시작·조회하는 API. SDK 예시만으로 Explorer의 실험실·agent 공격 범위를 알 수는 없다.
- **Model/MCP Scan:** model 파일·repository와 MCP server를 검사하는 API.
- **Management API:** application·connection·policy·event 관리. AI BOM 관련 API도 공개 SDK에 포함된다.

공개 CLI는 model-scan·mcp-scan·ai-bom, machine-readable 결과와 정책 기준 CI exit code를 설명한다. 공개 조직 소개는 MCP/Skill/A2A scanner 같은 커뮤니티 도구를 기업용 플랫폼을 보완하는 별도 프로젝트로 구분한다.

**입력:** API가 검사할 메시지·요청/응답, 등록 application/server/model, 정책·검사 설정.

**결과:** 검사 decision·관련 이벤트, scan 결과, 관리 API 결과. 설정과 SDK 통합에 따라 운영 중 호출을 차단할 수 있다. 공개 SDK를 받을 수 있다는 사실이 backend 서비스·Explorer 전체의 무료 사용을 뜻하지 않는다. SDK 예시는 inspection/management API key를 요구한다.

**사용 예:** 운영 에이전트의 LLM/MCP 상호작용에 위험 검사를 넣고, 조직 정책에 따라 관측하거나 차단하며 event를 중앙에서 관리한다. 출시 전 공격 시험과 운영 중 guardrail은 다른 기능이므로 나누어 봐야 한다.

출처: [공식 SDK](https://github.com/cisco-ai-defense/ai-defense-python-sdk/blob/main/README.md), [공식 CLI](https://github.com/cisco-ai-defense/ai-defense-cli/blob/main/README.md), [공개 조직 소개](https://github.com/cisco-ai-defense/.github/blob/main/profile/README.md). [지정된 Explorer 블로그 — 접근 실패](https://blogs.cisco.com/ai/agent-validation-explorer-edition).

## Snyk Agent Scan

**서비스 성격:** 머신·프로젝트에 설치된 agent/MCP/Skill을 발견하고 위험한 구성·설명·파일 내용을 검사하는 CLI다. 일반 agent endpoint에 공격 대화를 보내 업무 전체를 평가하는 도구와 입력 단위가 다르다.

지원 agent의 구성 경로를 탐색해 MCP와 Skill을 찾는다. 문서는 Claude, Cursor, VS Code, Gemini CLI, Codex 등 여러 구성의 OS/scope별 탐색 범위를 구분한다. MCP에서는 서버와 연결해 tool descriptions/prompts/resources 등을 수집하고, Skill에서는 manifest·지시문·관련 파일을 분석한다.

현재 0.6+ risk 문서의 MCP 항목은 도구 설명의 주입 지시, 공격자가 제공할 수 있는 외부 content, private data 접근, destructive capability다. Skill 항목은 숨은 주입 지시, 의심 download URL, 악성 코드, credential 취급, secret, 금융 접근, third-party content, 검증 불가능한 remote dependency, system service 수정, SKILL.md 누락이다. 결과에는 risk score·근거와 해당 도구/파일 위치 등이 들어간다. 서버 기동 실패 같은 운영 오류는 보안 위험과 별도 code로 구분한다.

**입력:** 로컬 agent 설정 경로, MCP configuration, SKILL.md/Skill 디렉터리, 서버에서 발견한 entity 정보.

**결과:** 발견한 component inventory, 위험 indicator·score·근거, affected tools/파일 위치, JSON 결과, CI 실패 여부.

**제공 형태:** 공개 Python CLI(`uvx`)·standalone binary와 Snyk의 분석 backend/enterprise 연계다. 최신 Quick Start는 Snyk 가입과 `SNYK_TOKEN`을 요구한다. README는 분석에 필요한 agent/MCP/Skill 정보를 API로 보낸다고 설명하므로 완전한 offline scanner로 보면 안 된다. CLI 결과 구조는 experimental이며 0.5.x와 0.6+의 형식이 다르다. enterprise Evo의 지원 계약과 공개 CLI 출력 안정성도 구분한다.

검사 과정에서 stdio MCP 서버의 command를 기동하거나 remote MCP에 연결할 수 있다. 따라서 파일을 읽기만 하는 검사로 가정하면 안 된다. 그렇다고 업무 전체에서 실제 기밀이 유출됐다는 증거가 생기는 것은 아니다. 예를 들어 private-data와 destructive-capability indicator는 능력의 위험이며 특정 공격 실행 성공률은 아니다.

**사용 예:** 외부 MCP/Skill 도입 전에 설치 구성과 지시문·접근 능력을 조사하고 위험 근거를 검토한다. 변경 후 같은 구성을 다시 scan하거나 CI에서 gate로 사용한다.

출처: [공식 README](https://github.com/snyk/agent-scan), [risk reference](https://github.com/snyk/agent-scan/blob/main/docs/risks.md).

## LangSmith

**서비스 성격:** AI 애플리케이션의 개발·운영을 위한 관측, 평가, prompt 관리 플랫폼이다. 제공된 링크는 그중 **실험 결과 비교 화면**의 설명이다. 별도의 LangSmith Deployment 서비스도 있다.

**Observability**는 실행 trace를 받아 LLM 호출·retrieval·tool·오류 등 내부 실행을 조사하고, 운영 지표·dashboard·alert·feedback을 관리한다. 공식 문서는 LangChain 이외의 여러 framework/provider도 연동한다고 설명한다. 실제 사용자 실행에서 발견한 실패를 dataset에 추가해 이후 평가에 재사용할 수 있다.

**Evaluation**은 input/reference output을 담은 dataset, code·LLM judge·human·pairwise evaluator, agent의 특정 version을 실행한 experiment로 구성된다. offline evaluation은 출시 전 비교·regression, online evaluation은 운영 trace/thread의 품질 검사에 쓰인다. 반복·동시성·cache도 실행 설정에 포함된다.

제공된 **Compare experiment results** 페이지는 동일 dataset에서 두 개 이상 experiment를 선택하고 metric별 regression/improvement를 강조하는 UI를 설명한다. input/output/metadata/feedback 등을 filter하고, 두 실험의 text·JSON/YAML output diff를 보고, 동일 example의 trace를 나란히 연다. 출력 diff는 배포 설정 전체의 보안 graph diff와 다르다.

**Prompt engineering**은 template을 commit·tag로 versioning하고 Playground에서 prompt/model/tool/schema를 바꾸며 비교하는 기능이다. SDK로 지정 prompt version을 애플리케이션에서 가져올 수 있다.

**Deployment**는 agent workload의 durable execution·streaming·scaling을 위한 별도 runtime 서비스다. 공식 문서는 Cloud·Hybrid·self-hosted 등의 배포 topology를 구분한다. 관측/평가 플랫폼을 쓰는 것과 agent를 이 서비스에 hosting하는 것은 별도 선택이다.

**입력:** 실행 trace, dataset/examples, reference outputs, evaluator, prompt template/model 설정, 선택적으로 배포할 agent.

**결과:** 실행 조사 화면, 품질·latency 등 지표, feedback score, experiment 비교, versioned prompts, 선택적 hosted runtime.

**제공 형태:** 플랫폼의 Cloud·BYOC·Self-hosted. 확인한 platform 문서는 BYOC/Self-hosted를 Enterprise 제공으로 설명한다. agent hosting의 조건은 별도 Deployment 계약에 따른다. 계정/API key·trace 저장 위치·retention·plan을 확인해야 한다. 정확한 요금·quota는 이번에 읽은 가격 문서가 실제 가격 페이지로 연결만 하므로 확정하지 않았다.

**사용 예:** prompt v1/v2를 같은 질문 집합에 실행하고 어떤 질문의 정확도가 떨어졌는지 확인한 뒤 trace를 열어 retrieval이나 tool 선택의 변화를 조사한다. 외부 수신/상태 oracle의 결과도 custom evaluator에 넣을 수 있지만 관측기를 자동 구축해 주는 것으로 확인되지는 않았다.

출처: [지정된 비교 페이지의 원본](https://github.com/langchain-ai/docs/blob/main/src/langsmith/compare-experiment-results.mdx), [관측](https://github.com/langchain-ai/docs/blob/main/src/langsmith/observability.mdx), [평가](https://github.com/langchain-ai/docs/blob/main/src/langsmith/evaluation.mdx), [prompt](https://github.com/langchain-ai/docs/blob/main/src/langsmith/prompt-engineering-concepts.mdx), [platform](https://github.com/langchain-ai/docs/blob/main/src/langsmith/platform-setup.mdx), [deployment](https://github.com/langchain-ai/docs/blob/main/src/langsmith/deployment.mdx).

## n8n Evaluations

**서비스 성격:** n8n AI workflow를 dataset으로 반복 실행해 결과와 품질을 비교하는 **n8n 내장 기능**이다. 별도 보안 스캐너 서비스나 독립 agent hosting 제품이 아니다. 제공된 링크는 평가를 왜 하는지와 light/metric-based 구분을 설명하는 개요다.

시험 자료는 data table 또는 Google Sheets 등으로 준비하고, Evaluation Trigger를 업무 흐름에 연결한다. Set Outputs로 결과를 dataset에 기록한다. **Light evaluation**은 작은 사례 집합을 실행해 사람이 input·expected/actual output을 비교하며 반복 개발하는 흐름이다. **Metric-based evaluation**은 scoring logic을 추가해 run별·case별 지표와 이전 결과를 비교한다.

내장 metric은 AI 기반 correctness/helpfulness, string similarity, categorization, Tools Used다. 계산한 custom metric도 등록할 수 있다. 공식 문서는 AI Agent의 Return intermediate steps를 켜면 `intermediateSteps`로 실제 수행한 도구 정보를 후속 metric에서 참고할 수 있다고 설명한다. 실패한 운영 입력을 dataset에 추가하고 regression test로 재실행하는 흐름을 제공한다. LLM 결과/judge의 변동을 줄이려면 같은 dataset row를 반복해 평가하는 방법도 안내한다.

**입력:** n8n workflow, dataset input/reference outputs, evaluation trigger 연결, metric logic.

**결과:** 사례별 workflow output, numeric metric, run 요약·이전 run 비교, 해당 execution으로 drill-down.

**제공 형태:** n8n Cloud/self-hosted 안의 plan별 기능이다. 확인한 문서는 light evaluation을 Cloud 모든 plan과 self-hosted Registered Community/Business/Enterprise에 제공한다고 설명한다. metric-based는 Cloud Pro/Enterprise와 self-hosted Enterprise, Registered Community/Starter에는 한 workflow 사용을 설명한다. 문서의 concurrency 표에는 다른 tier도 있어 실제 버전·계정의 entitlement 확인이 필요하다. workflow마다 evaluation trigger는 하나이며 여러 부분을 별도로 평가하려면 sub-workflow로 나눌 수 있다고 안내한다.

**사용 예:** 고객 문의 분류 workflow의 model/prompt를 바꾼 뒤 동일 문의 집합에서 분류 정확도와 사용 도구를 비교한다. 기밀 수신/쓰기 여부 같은 외부 효과는 별도 observer와 metric 연결이 필요하다. evaluation trigger로 workflow 중간에 진입한 결과를 실제 webhook 인증·진입 통제 검증으로 일반화하지 않는다.

출처: [개요](https://github.com/n8n-io/n8n-docs/blob/main/docs/build/integrate-ai/test-and-improve-ai-workflows/understand-why-to-test.md), [light](https://github.com/n8n-io/n8n-docs/blob/main/docs/build/integrate-ai/test-and-improve-ai-workflows/run-quick-evaluations.md), [metrics](https://github.com/n8n-io/n8n-docs/blob/main/docs/build/integrate-ai/test-and-improve-ai-workflows/use-metrics-to-measure-quality.md), [tool data와 common issues](https://github.com/n8n-io/n8n-docs/blob/main/docs/build/integrate-ai/test-and-improve-ai-workflows/fix-common-issues.md).

## 서로 어떤 서비스 계층에 있는가

| 도구 | 주된 가치 | 주로 투입하는 것 | 받는 핵심 결과 |
|---|---|---|---|
| Promptfoo | 개발·보안 시험 실행 | target + test/plugin/strategy | 평가·위험·실행 결과 |
| Giskard OSS/Hub | 품질·안전·업무 실패 시험과 팀 관리 | agent + scenarios/checks/knowledge | 실패 사례·dataset·평가 이력 |
| Cisco AI Defense | 보안 검증·운영 검사·정책 관리 | application·traffic·policy·scan target | 검사/정책 결과·보안 event·선택적 차단 |
| Snyk Agent Scan | agent 구성요소 inventory와 위험 분석 | MCP config·Skill·설치 구성 | 구성요소별 위험 근거 |
| LangSmith | 관측·평가·prompt 관리와 선택적 deployment | traces·datasets·evaluators·prompts | 비교·진단·feedback·운영 지표 |
| n8n Evaluations | n8n workflow의 내장 반복 평가 | workflow·dataset·metrics | output·metric·run 비교 |

여섯 제품을 모두 같은 “취약점 스캐너”로 분류하면 서비스를 잘못 이해하게 된다. 상시 운영 차단, 출시 전 공격 시험, 구성 위험 분석, 품질 평가·관측은 구분해야 한다. Cisco Explorer의 지정 페이지를 직접 파악하려면 `blogs.cisco.com` 접근이 필요하며 무료 제공 범위와 독립 관측 방식은 확인 과제로 남았다.
