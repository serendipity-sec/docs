# 워크플로우 보안 회귀 프로젝트의 조사 근거

개정일: 2026-10-09, Asia/Seoul. 기존 출처 확인일은 10월 3일이며, 아래 추가 조사에 10월 8일·9일의 확인 범위를 따로 적었다. 공식 문서·원저자 논문·공식 저장소를 우선 확인했다. 도구 실행과 논문 실험의 재현은 이번 조사에서 수행하지 않았다. 최신 README의 기능 표시는 실제 성능이나 모든 버전의 동작을 입증하지 않는다.

## 사용자가 제공한 설계안

Notion 커넥터에서 5건 모두 접근 오류가 발생했으나 로그인된 브라우저에서 각 페이지를 열어 접힌 본문을 펼쳐 읽었다. 아래는 본문 기반 통합이며 첨부 HTML 파일을 별도로 다운로드·실행한 결과가 아니다.

| 문서 | 핵심 내용 | 반영 |
|---|---|---|
| [AI 워크플로우의 배포 환경 및 의존성 변경에 따른 보안 회귀 분석](https://app.notion.com/p/AI-3ecc2d6e153780c7a6d5c3338dd4abc3) | n8n, 환경·의존성, 필드와 판단 영향, 변경 중심 평가 | 공통 그래프와 스냅샷 |
| [환경·의존성 변경을 고려한 AI 워크플로우 보안 회귀 분석](https://app.notion.com/p/AI-3ecc2d6e1537807db675ca541ec4d8c8) | 기존 도구 비교, 승인 가정의 무효화, 무관한 IF, 미확인 처리 | 연구 범위와 비교군 |
| [재개 가능한 AI 워크플로우의 업데이트에 따른 승인–실행 일치성 분석](https://app.notion.com/p/AI-3ecc2d6e1537800f849ac1439b4bfcbb) | LangGraph 체크포인트·재개와 승인 값의 관계 | P3에 기본 계약만 반영, 버전 전환 재개는 후속 |
| [MCP·Skills 공급망의 보안 경계 위반 검증 및 취약점 발굴 프레임워크](https://app.notion.com/p/MCP-Skills-3ecc2d6e15378067ad2ac3720aca897a) | 코드·변경에서 후보 발견, 독립 관측, 수정 재검증 | 실험실·oracle·문제 분류 |
| [MCP·Skill 워크플로우의 배포 구성과 사용자 정책을 연결하여, 동일 구성을 서로 다른 권한 환경에서 검증하는 보안 테스트 도구](https://app.notion.com/p/MCP-Skill-3ecc2d6e153780f3bdfaf48c89ab064f) | 제한·과권한 환경, P1·P2, 모의 수신과 자원 변경 | 필수 동적 대조 |

이 문서들은 과거 제안이며, 최신 사용자 결정인 변경 그래프·시나리오 RAG·실행 검증과 4명·8~10주 조건을 우선한다. 과거 문서에 적힌 예상 정확도나 사례 수를 실적 또는 새 계획의 필수 수치로 가져오지 않았다.

## 핵심 주장별 사실 확인

| 주장 | 판정 | 확인한 근거와 제한 |
|---|---|---|
| 워크플로우 업데이트에는 검사가 없다 | 부정확 | n8n 리뷰·보안 감사, OWASP 회귀 하네스, Promptfoo CI 테스트가 존재한다 |
| 개별 워크플로우 리뷰 밖의 실행 구성이 바뀔 수 있다 | 특정 제품에서 확인 | n8n 공식 리뷰 문서가 설정·자격증명·변수·테이블·하위 workflow를 제외한다 |
| 여러 구성요소 결합으로 새로운 위험이 생길 수 있다 | 사례·연구 근거 있음 | TFA와 SCR-Bench가 다룬다. 실제 생태계에서의 발생률은 별도 문제다 |
| 그래프 기반 분석은 새롭다 | 성립하지 않음 | Agentic Radar, Agentproof, AgentFlow 등 선행 구현·연구가 있다 |
| 정적 후보를 실행으로 확인하는 결합은 새롭다 | 성립하지 않음 | VIPER-MCP 등 유사 분석·검증 접근이 있다 |
| 변경 조건을 이용한 검색·시험 선택이 더 효율적이다 | 연구 가설 | 같은 모델·시간·호출 예산의 비교 실험 필요 |
| 팀이 신규 CVE를 반드시 발견할 수 있다 | 근거 없음 | 발견·인정·발급은 보장할 수 없으며 필수 완료 조건에서 제외 |
| 8~10주에 논문 채택까지 가능하다 | 보장 불가 | 기간 내 목표는 완성된 연구 아티팩트·실험·초안이다 |

권하는 문제 서술은 “AI 워크플로우의 노드·연결뿐 아니라 환경·의존성·보호 조건의 변경까지 포함하여 보안 회귀를 검증할 필요가 있다”이다. “대부분의 기업은 업데이트를 검사하지 않는다”와 같은 시장 빈도는 인터뷰나 표본 조사 없이 쓰지 않는다.

## 가까운 도구와 연구

아래의 추가 비교 항목은 확인할 연구 질문이다. 조사에서 특정 기능을 찾지 못했다는 이유만으로 해당 도구가 그 기능을 절대 제공하지 않는다고 단정하지 않는다.

| 대상과 1차 출처 | 확인한 기능 또는 연구 | FlowDelta에서 필요한 추가 비교 |
|---|---|---|
| [n8n Workflow Reviews](https://docs.n8n.io/build/manage-workflows/workflow-reviews) | 노드·연결의 특정 버전 검토와 visual diff. 문서상 Enterprise Preview이며 리뷰 밖 의존성이 명시됨 | 환경·하위 참조를 포함했을 때 어떤 판정이 추가되는가 |
| [n8n Security Audit](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/run-security-audits) | 자격증명 사용, SQL 표현식, 파일 시스템, 위험 노드, 인스턴스 검사 | 전체 기능이 아닌 공통 지원 항목에서 비교 |
| [FlowGuard](https://github.com/MohibShaikh/FlowGuard) | n8n 구성의 규칙 기반 위험 검사. 공개 규칙과 결과 예시 제공 | 조건 의미·하위 구성·환경 분석의 추가 가치. 실제 버전 고정 실행 필요 |
| [Agentic Radar](https://github.com/splx-ai/agentic-radar) | 워크플로우 그래프, 도구·MCP 탐지, 취약점 매핑. 현재 README의 runtime test 설명은 OpenAI Agents 대상 | n8n 정적 구조 추출 재사용 가능성과 동일 범위의 정확도 |
| [Invariant Toxic Flow Analysis](https://invariantlabs.ai/blog/toxic-flow-analysis) | 신뢰되지 않은 입력·민감 자원·도구 능력의 위험한 조합 분석 | 변경 전후 구분과 시험 예산에 따른 확인율 |
| [Snyk Agent Scan](https://github.com/snyk/agent-scan) | 에이전트·MCP·Skill 검사. README가 v0.5와 v0.6 이후 기능 설명을 구분 | TFA의 과거 기능을 최신 CLI에 그대로 있다고 가정하지 않고 버전별 실행 |
| [Agentproof](https://arxiv.org/abs/2603.20356) | 2026년 3월 프리프린트. 여러 프레임워크의 그래프 추출과 구조·시간적 정책 검증, witness 생성 | 그래프 구조가 같고 권한·인자·설명만 달라진 변경을 구분하는가 |
| [AgentFlow](https://arxiv.org/html/2607.01640v1) | 2026년 7월 프리프린트. agent·prompt·model·capability 등을 표현하는 ADG와 보안 분석. 본문은 코드 기반 agent program에 범위를 둠 | low-code 변경 의미와 시나리오 선택에 추가 기여가 있는가 |
| [OWASP Agent Security Regression Harness](https://github.com/OWASP/Agent-Security-Regression-Harness) | 초기 Incubator 단계의 실행 시나리오·assertion·trace 기반 회귀 하네스 | 사용자가 시험을 지정하는 방식과 변경에서 자동 선택·구체화하는 방식 비교 |
| [Promptfoo MCP Security Testing](https://www.promptfoo.dev/docs/red-team/mcp-security-testing/) | MCP 직접 호출·도구 오염·agent 경유 시험과 CI 예시 | 동일 대상·예산에서 일반 시험과 변경 관련 시험의 효율 비교 |
| [SCR-Bench](https://arxiv.org/abs/2606.15242) | 2026년 6월 프리프린트. 스킬 결합 경로와 후속 상태 변화의 위험 평가 | 결합 평가 자체를 기여로 삼지 않고 버전 쌍·환경·검색 기반 선택의 효과 평가 |
| [AgentDojo](https://arxiv.org/abs/2406.13352) | 도구를 사용하는 agent의 공격·방어와 정상 작업을 평가하는 환경 | 정상 업무·공격을 함께 평가하는 원칙 참고. n8n 변경 정답셋으로 직접 대체 불가 |
| [CaMeL](https://arxiv.org/abs/2503.18813) | 제어·데이터 흐름 분리와 capability 기반 정책 강제 | 방어를 새로 발명하는 주장이 아닌, 배치된 통제의 모델링과 시험 |
| [VIPER-MCP](https://arxiv.org/abs/2605.21392) | 2026년 프리프린트. MCP 구현의 taint 분석과 동적 확인 결합 | 일반적인 정적·동적 결합 대신 버전 전후 시험 선택·정책 회귀에 초점 |

최소 외부 비교는 아래 10월 8일 조사에서 추가한 n8n-ai-agent-security-lab의 공통 범위를 우선 확인하고, FlowGuard 또는 n8n Audit의 정적 검사, OWASP 하네스 또는 Promptfoo의 동적 검사를 보완 비교한다. Agentic Radar는 그래프 추출 비교 또는 재사용 후보로 둔다. 많은 제품을 얕게 실행하기보다 고정 버전·정확한 설정·공통 범위에서 비교한다. 접근권한·라이선스·호환성 때문에 실행하지 못한 도구는 NOT_RUN으로 표시한다.

## 입력과 판정 구조를 뒷받침하는 자료

* [MCP Tools 명세 2026년 7월 28일 판](https://modelcontextprotocol.io/specification/2026-07-28/server/tools): 도구 목록은 요청의 권한에 따라 달라질 수 있고 변경 알림·캐싱을 다룬다. 같은 이름의 도구라도 서버 식별자·권한 문맥·스냅샷 시점을 기록해야 한다는 설계 근거다. 명세가 있다는 사실은 개별 구현이 이를 준수한다는 증명이 아니다.
* [Agent Skills 명세](https://agentskills.io/specification): 본문과 참조 자료를 사용하는 구조, 구현별 지원이 다른 `allowed-tools` 필드를 확인했다. 파일 트리와 호스트 계약을 함께 기록하되 선언을 실효 권한으로 해석하지 않는다.
* [OSV API](https://google.github.io/osv.dev/api/)와 [OSV 스키마](https://ossf.github.io/osv-schema/): 패키지·버전·커밋 및 취약점 별칭을 구조화해 다룰 기반이다. CVE 적용 여부를 문장 유사도만으로 결정하지 않는다.
* [Invariant의 Tool Poisoning 원발견 보고](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks): 설치 이후 descriptor 변경과 다른 서버 도구에 대한 영향 사례를 설명한다. 호출된 도구뿐 아니라 모델 문맥에 노출된 설명도 영향 그래프에 포함하는 이유다.
* [Same Name, Different Server](https://arxiv.org/abs/2609.14119): 2026년 9월 프리프린트가 MCP 메타데이터·endpoint의 변경을 조사한다. 저자의 표본·스캐너·실험 결과이며 이번 프로젝트에서 재현한 통계가 아니다. 변경 관측을 취약성의 자동 증거로 삼지 않는다.

실제 취약 공지의 예로 [n8n GHSA-2vff-hj5x-8gq7](https://github.com/n8n-io/n8n/security/advisories/GHSA-2vff-hj5x-8gq7)은 공개 webhook 입력이 내부 데이터 복사 과정을 거쳐 후속 action의 필드로 사용될 때의 confused-deputy 위험을 설명하며 CVE-2026-54306으로 연결된다. 이 자료는 제품·영향 버전뿐 아니라 workflow 구성 조건도 보존해야 함을 보여준다. 해당 취약점을 이번 작업에서 재현했거나 새로 발견한 것은 아니다. 여러 릴리스 계열의 수정 버전은 공식 구조화 데이터와 비교해 처리하고, 공지의 버전 문자열을 단순 비교하지 않는다.

## 로컬 자산과 재사용의 경계

10월 3일 조사 때 로컬 설계 브랜치에서 확인한 과거 자산이다. 현재 핵심 설계만 공유 main에 반영하며, 과거 실험을 재실행하거나 그 결과를 새 성능으로 인용하지 않는다. 아래 링크는 조사 대상이 있던 고정 커밋으로 연결한다.

[기존 실험 요약](https://github.com/serendipity-sec/docs/blob/42837ce75aa5c55f994bfa035df9221cb3af334c/archive/research/2026-09-21-검토공백과-기존도구-데모설계/README.md)과 [실험 코드](https://github.com/serendipity-sec/docs/blob/42837ce75aa5c55f994bfa035df9221cb3af334c/archive/experiments/live-agent-security/README.md)에서 다음 자산을 확인했다.

| 자산 | 재사용 후보 | 새 프로젝트에서 다시 확인할 것 |
|---|---|---|
| lab_mcp_server.py와 fixtures | 합성 문서·도구 응답·모의 외부 효과 | 실제 n8n 경로와의 연결, fixture 의미 |
| run_lab.py와 실행 기록 구조 | 모델 설정·실행 ID·반복 실행 | 모델 버전·환경 초기화·불변 trace |
| verify_evidence.py와 gate 관련 코드 | 증거 존재·상태 구분 | 새 oracle의 독립성·변환 데이터 판정 |
| 기존 스캐너 비교 기록 | baseline 구성과 실패 경험 | 현재 선택한 버전에서 새 실행 |

과거 문서에는 유출 oracle의 누락과 판정 정정, 모의 승인, 프로토콜 적합성·OS 격리의 한계가 명시돼 있다. 따라서 코드를 읽었다는 사실만으로 새 실험의 판정기를 검증했다고 하지 않는다. 첫 주에 작은 정상·위반·차단·관측 실패 사례로 다시 자격을 확인한다.

## 추가 조사가 필요한 항목

첫 주에는 8~12개 관련 도구·연구에 대해 버전·공개 코드·지원 대상·변경 처리·시나리오 자동 선택·독립 효과 관측을 표로 고정한다. 저장소 코드까지 확인한 사실과 README만 확인한 사실을 구분한다. “미기재”는 “미지원”과 다르다.

실무자 3~5명에게 최근 workflow 변경에서 무엇을 검토했고 무엇을 재실행했는지 물어본다. 이는 탐색적 사용자 조사이며 시장 전체 비율을 추정하는 설문이 아니다. 공개 변경 사례는 부모·하위 의존성·권한 변경을 포함해 가능한 범위에서 10쌍을 조사한다. 조건을 충족하는 사례가 적으면 그 수를 그대로 보고한다.

프리프린트의 성능·신규성 주장은 저자의 주장으로 취급한다. 가장 가까운 방법이 같은 문제를 이미 해결한다면 그 부분의 최초성 주장을 철회하고 변경 벤치마크나 n8n 어댑터·시험 선택의 실증 개선으로 기여를 좁힌다.

## 10월 8일 추가 평가에서 반영한 근거

| 1차 출처 | 확인한 범위 | 설계 반영과 한계 |
|---|---|---|
| [n8n-ai-agent-security-lab](https://github.com/0xCD4/n8n-ai-agent-security-lab) 및 [rehearsal 문서](https://github.com/0xCD4/n8n-ai-agent-security-lab/blob/main/docs/release-rehearsal-cli.md) | 공개 README·CLI 문서의 그래프·하위 workflow·baseline/candidate 비교·제한된 실행 검증 | 가장 가까운 외부 비교군. 문서상 rehearsal은 Webhook 2.1·Set 3.4·HTTP 4.2 등의 제한된 조건을 다루며 AI·동적 목적지·하위 호출 등과 구분한다. 직접 실행 성능은 미확인 |
| [Testing Agentic Workflows with Structural Coverage Criteria](https://arxiv.org/html/2605.26521v1) | 그래프에서 검증 항목을 만들고 실행 witness와 대응하는 연구 구조 | 필수 검증 항목–근거 대응표를 명시. 구조 coverage를 모든 보안 정책의 증명으로 확장하지 않음 |
| [Mutation Testing for Multi-Agent Systems](https://www.researchgate.net/publication/410035906_Mutation_Testing_for_Multi-Agent_Systems) | 저자가 공개한 원본·변형 비교와 관련 검증 항목 평가 방식 | 변경 기반 시험 선택의 선행 아이디어. 직접 관련된 항목만 검사할 경우 공유 상태·비국소 영향 누락을 고려. 심사 상태·자체 재현 미확인 |
| [n8n workflow tool 공식 문서](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolworkflow) | sub-node 표현식에서 첫 item을 참조하는 동작 설명 | 일반 노드와 sub-node를 같은 값 전파 규칙으로 취급하지 않고 배치 의미 계약을 시험 |

그래프+변경 비교+실행 검증이라는 조합만으로 최초성을 주장하지 않는다. 환경·의존성 정보의 추가 가치와 RAG 선택의 효과를 각각 검증하며, 정답은 스캐너 경고와 독립적으로 작성한다. 설명 자료를 읽은 결과와 코드 검토·실제 실행 결과를 구분한다.

## 10월 9일 입력·데이터 조사에서 반영한 근거

[입력·데이터 상세 3절](input-and-data.md#3-실제로-확인한-자료)에 원문 URL, 공식 JSON API, 확인 항목과 사용 한계를 모았다. n8n 템플릿 14550은 nodes 배열 18개, 18499는 60개를 확인했으며 설명용 노드도 포함한다. τ 저장소 retail/tasks.json의 114개는 업무 요청 수다. 이 수치를 실행 지원 수·독립 workflow 수·확정 취약점 수로 사용하지 않는다.

공개 템플릿은 실제 작성된 업무 예시이고, τ의 정책·DB는 연구용 환경이다. starter kit의 실제 commit은 변경 이력 근거이며 보안 정답은 아니다. 모든 조건을 갖춘 완성된 n8n 회귀 데이터셋은 이번 조사에서 확보하지 못했다. 따라서 원본·정책·상태·환경·정답을 출처별로 구성하고 변환 내용을 공개해야 한다.

새 후보를 데이터셋에 편입할 때는 URL만 보관하지 않고 실제 수집 파일·commit·해시·이용 조건을 함께 기록한다. 이번 문서에 후보를 기재한 사실만으로 원본 수집·재배포 검토·실행·라벨링이 끝난 것으로 보지 않는다.
