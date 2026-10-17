# FlowDelta 아키텍처와 기존 도구 비교

확인일: **2026-10-07 KST**. 비교 기준: 사용자가 첨부한 `architecture.html`의 **2026-10-03 제안 설계**. 이 HTML은 구조 설명이며 실제 검사 결과가 아니다. 저장소의 과거 Slack 논의안보다 첨부 설계를 우선했다.

**핵심 판단**

FlowDelta의 공격 생성·보안 시험·회귀 비교·실행 기록·그래프는 각각 기존 도구와 겹친다. 가장 설득력 있는 연구 대상은 **보안 관련 구성 변경으로 시험을 선택하고, 동일 조건의 전후 실행에서 실제 효과를 독립 관측해, 변경부터 판정까지 연결하는 절차**다. 이것도 최초라는 주장은 아직 뒷받침되지 않는다. 특히 Promptfoo는 도구 실행·궤적 기반 판정을 이미 지원하며, 사용자 표에 기술된 Cisco의 독립 관측 기능과 공개 `n8n-ai-agent-security-lab`의 변경 검토는 직접 비교해야 한다.

이번 조사는 공개 공식 저장소의 문서 원본과 첨부 설계를 읽은 **문헌·아키텍처 비교**다. 도구 설치, 공격 실행, 속도·탐지율 측정, 상용 계정 검증은 하지 않았다. 따라서 아래의 “지원”은 읽은 문서가 설명하는 지원이며 실제 재현 결과가 아니다. 공식 사이트는 프록시 403으로 열리지 않아 가능한 경우 공식 GitHub 원본으로 대체했다. Cisco 원문은 확보하지 못했다. 출처 ID·커밋·SHA-256은 [출처 기록](2026-10-07-FlowDelta-도구비교-sources.json)에 보관한다. `main` 문서에는 미출시 변경이 포함될 수 있어 설치할 릴리스의 기능과 별도로 확인해야 한다.

## 1. 현재 아키텍처를 어떻게 해석했는가

| 단계 | 첨부 설계의 입력·처리·출력 | 비교에서 중요한 점 |
|---|---|---|
| ① Snapshot | 워크플로·하위 참조·MCP 도구 설명·Skill·권한·모델 설정을 전후 묶음으로 고정. 버전·해시·출처·미확인 설정 기록 | 단순 프롬프트 버전 비교보다 넓다. 파일 해시만으로 실제 계정 권한이나 배포 상태까지 확인되지는 않는다 |
| ② Graph + Diff | 데이터·권한·모델 영향·승인·필터 관계를 구성하고 새 경로, 권한 확대, 수신자 변경, 보호 조건 삭제, 하위 참조 변경 추적 | 일반 실행 순서도나 JSON 텍스트 diff보다 보안 의미를 해석해야 한다 |
| ③ Retrieval | 사람 검토한 카드에서 키워드·벡터 검색 후 제품·버전·입력 통제권·권한·방어 조건으로 필터링 | 유사 문서 검색과 취약점 적용 판단을 분리한다. 검색 결과가 없어도 정책 위반 후보 유지 |
| ④ Test Plan | LLM이 등록된 템플릿의 입력 위치·파라미터 제안. 별도 검증기가 노드 ID·조건·도구·관측 기준 검증 | LLM이 임의 코드·판정 기준을 만들거나 바꾸지 못하는 구조 |
| ⑤ Isolated Run | 폐기 가능한 VM, n8n, 모의 MCP, 합성 자료, 격리 수신처로 전후 실행. 매번 초기화. 고정 호출 재생과 실제 모델 실행 구분 | 상태·시험 조건을 통제해야 변경 효과를 비교할 수 있다 |
| ⑥ Evidence | 대상이 수정할 수 없는 수신 기록·문서 쓰기 이벤트·자원 상태로 판정. 수정본과 정상 업무 재시험 | 모델 답변·도구 시도·실제 외부 효과를 구분한다 |

증거 연결은 `Snapshot → ChangeSet → Hypothesis → TestPlan → Run → Evidence → Finding`이다. 구현 선택은 Python 분석 코어·n8n 어댑터·PostgreSQL/pgvector, 격리 실행, 독립 증거 영역이다. 이는 제안된 구조이지 배포된 기능 목록은 아니다.

8주 필수 범위는 **n8n 한 플랫폼, 변경 분석, 시나리오 검색, 기밀 전송·무단 쓰기, 독립 증거, 전후 비교 보고서**다. 모델 교차 평가·지식 웹사이트·LangGraph·다중 프레임워크·넓은 승인 분석은 후속 범위로 읽었다.

## 2. 사용자 표에서 보완해야 할 부분

| 도구 | 확인한 내용 | 비교할 때 보완할 점 |
|---|---|---|
| Promptfoo | 에이전트 보안 시험, MCP 호출, 간접 주입, 실행 궤적·도구 인수/순서 assertion, CI 회귀 [P1–P5] | 출력만 보는 스캐너로 축소하면 안 된다. trace-aware grading과 결정적 assertion까지 비교해야 한다 |
| Giskard | 최신 공식 README는 v3의 다중 턴 에이전트·Scenario/Check/Suite·취약점 생성·trace 평가를 설명 [G1] | v2 Scan/RAGET/Hub와 v3를 섞지 않는다. README는 v2가 더 이상 적극 유지되지 않는다고 설명한다 |
| Cisco AI Defense | 사용자가 제시한 표의 공격 시험·지속 상태·독립 관측 설명 | 원문 접근 실패로 기능·Explorer 범위·가격·지원 인터페이스 미검증. 이 행을 검증된 제품 사실로 인용하지 않는다 |
| Snyk Agent Scan | MCP·Skill 탐색·분석, Snyk API 토큰 요구, 분석용 구성 정보 전송, MCP 서버 기동 가능 [S1] | “오픈소스 CLI”가 “완전 로컬·오프라인 분석”을 뜻하지 않는다. CLI 출력은 실험적이고 버전별 구조가 바뀐다 |
| LangSmith | 동일 dataset의 실험 비교, 지표별 회귀, 출력 diff, 실행 trace 나란히 보기, code/LLM/human/pairwise evaluator [L1–L2] | 단순 로그 뷰어가 아니다. 사용자 정의 보안 판정 결과도 평가 플랫폼에 연결할 수 있다 |
| n8n Evaluations | dataset 반복 실행·결과/지표 비교·custom metric·intermediateSteps 조회 [N1–N4] | 정상 품질 평가 외에 보안 시험 데이터를 넣을 수 있다. 외부 효과의 독립 관측은 별도 설계해야 한다 |

## 3. 아키텍처 기준 비교표

“확인”은 공식 원본에서 확인한 기능, “연동”은 API/확장 지점이 있어 FlowDelta 쪽 구현으로 연결 가능한 부분, “미확인”은 이번 문서 범위에서 확인하지 못한 부분이다. 미확인은 기능 부재를 뜻하지 않는다. FlowDelta 열은 설계 목표다.

| 비교 기준 | FlowDelta 설계 | Promptfoo | Giskard v3 | Cisco | Snyk Agent Scan | LangSmith | n8n Evaluations |
|---|---|---|---|---|---|---|---|
| 비교 단위 | 구성·권한·도구·정책을 포함한 전후 스냅샷 | target/provider·시험 구성 | target·scenario·suite | 원문 미확인 | 발견한 agent/MCP/Skill 구성 | dataset·example·experiment·run | workflow·dataset·test run |
| 보안 의미의 구성 graph diff | 핵심 | 기본 기능 미확인; 별도 분석 연동 | 기본 기능 미확인; 별도 분석 연동 | 미확인 | 구성/능력 위험 분석과 중첩; 전후 n8n graph diff 미확인 | 실행 trace와 구별; 구성 graph diff 미확인 | workflow 존재; 보안 graph diff 미확인 |
| 변경 조건으로 시험 선택 | 핵심 | test/plugin 선택 연동; 동일 자동화 미확인 | generator/suite 선택 연동 | 미확인 | 위험 결과를 선택 입력으로 연동 | metadata/dataset/evaluator 연동 | dataset 선택 로직 연동 |
| 공격·시험 생성 | 카드+등록 템플릿+LLM | red-team plugin/strategy 확인 | vulnerability_scan/generator 확인 | 사용자 표의 기능; 미검증 | 구성·자연어 내용의 위험 분석 확인 | dataset·evaluator 기반; 전용 공격 생성은 읽은 문서에서 미확인 | dataset 기반; 전용 공격 생성 미확인 |
| 간접 입력·MCP | 입력 위치와 시험 조건 지정 | 간접 주입 plugin·MCP provider 확인 | target adapter/custom scenario로 연결 | 사용자 표의 기능; 미검증 | MCP 설명·prompts/resources·Skill 검사 확인 | 해당 실행을 instrument/평가하면 연결 | n8n AI 도구와 workflow 데이터로 연결 |
| 실행 과정 평가 | 도구 기록+독립 이벤트 | OTEL trajectory·toolCalls·assertion 확인 | trace 기반 Check 확인 | 사용자 표의 기능; 미검증 | 서버 탐색/접속과 업무 전체 공격 실행은 구별 | trace·code evaluator 확인 | intermediateSteps·custom metric 확인 |
| 수신/상태의 독립 판정 | 핵심, 대상과 권한 분리 | custom provider/assertion으로 연동 가능; 자체 설치는 필요 | custom target/check로 연동 가능; 자체 설치는 필요 | 사용자 표에 직접 중첩; 원문 미확인 | 실제 기밀 수신/상태 변화 oracle 미확인 | 외부 관측 결과를 code evaluator/feedback으로 연동 | 외부 관측 결과를 metric으로 연동 |
| 전후 동일 시험·회귀 | 핵심 | CI eval/redteam 실행 확인 | suite/scenario 재실행 확인 | 미확인 | 스캔 재실행 가능; 업무 효과 회귀와 구별 | 동일 dataset 실험 비교 확인 | 반복 평가·이전 run 지표 비교 확인 |
| 격리·상태 초기화 | 폐기 VM·매 실행 초기화 | 대상 실험실 별도 구축 | 대상 실험실 별도 구축 | Explorer 실험실 조건 미확인 | README가 untrusted MCP 스캔의 sandbox 권고 | 대상 실험실 별도 구축 | n8n instance·credentials·상태 격리 별도 구축 |

표의 기능 수를 합산해 우열 점수를 만들지 않는다. Snyk의 구성 분석, Promptfoo/Giskard의 시험 엔진, LangSmith/n8n의 평가 운영은 서로 다른 층위다.

## 4. 도구별 상세 판단

**Promptfoo — 가장 먼저 실제 기준선으로 삼을 보안 시험 엔진**

공식 에이전트 가이드는 권한 상승, context poisoning·exfiltration, memory poisoning, 다단계 공격, 도구/API 조작을 다룬다. black-box·component·trace-based testing을 구분하고, OpenTelemetry span을 실행 궤적으로 정규화해 grader와 공격 피드백에 사용한다 [P1]. 간접 주입 plugin은 RAG 문서·이메일·프로필 같은 비신뢰 template variable에 payload를 넣는다 [P3]. 실제 n8n 검색 결과나 MCP 도구 반환값에 주입하려면 그 위치를 target adapter가 정확히 노출해야 한다. template variable 시험이 모든 실제 도구 반환값 교체를 자동 제공하는 것은 아니다.

MCP provider는 직접 도구를 호출할 수 있다. 또한 지원 chat provider가 모델 대신 수행한 MCP 호출을 `metadata.toolCalls`에 담아 도구 이름·인수·출력·오류를 assertion에 사용한다 [P2]. trace assertion은 도구 사용·인수·순서 등을 검사한다 [P4]. 따라서 FlowDelta의 “LLM의 성공 선언을 믿지 않고 도구 기록을 본다”는 부분만으로는 차별화되지 않는다.

남는 비교 대상은 **어떤 구성 변경이 어떤 정책 위반 경로를 만들었기에 이 시험을 골랐는가**, 그리고 **호출 기록과 실제 수신/쓰기 결과가 일치하는가**다. Promptfoo가 외부 oracle을 호출하도록 확장하면 후자도 구현할 수 있다. 제안은 공격 전략·평가 형식·CI를 재사용하고, graph diff·조건 선택·격리 환경·수신/상태 oracle을 FlowDelta에서 책임지는 것이다. 공개 LICENSE는 MIT [P6]. 로컬 CLI라도 모델·공격 생성기·판정기·대상 서비스 비용과 데이터 전달은 provider 설정에 따라 달라진다. 상용 플랜의 정확한 범위·가격은 이번 조사에서 확인하지 않았다.

**Giskard — 시나리오 계약과 평가 엔진을 재사용할 대안**

최신 README의 v3는 Python 3.12+, `giskard-checks`, `giskard-scan` 중심이다. `Target`은 sync/async callable이고 출력에 trace를 포함할 수 있다. `Scenario`는 interactions+checks, `Suite`는 시나리오 묶음이다. string/regex·semantic similarity·LLM-as-judge와 다중 턴 에이전트 평가를 설명한다. `vulnerability_scan`은 agent 설명을 받아 공격 suite를 생성하고 custom ScenarioGenerator 확장도 제공한다 [G1].

FlowDelta의 TestPlan을 Scenario/Suite로 변환하고 독립 이벤트를 custom Check로 평가할 수 있다. 다만 snapshot·graph diff·변경 조건 필터·n8n 상태 초기화·관측 권한 분리까지 자동으로 완성되는 것은 확인하지 못했다. “Giskard는 RAG만 평가한다”거나 “단일 응답만 검사한다”는 비교는 최신 원본과 맞지 않는다.

Python 코어와 맞는 장점이 있지만, 작은 프로젝트에서 Promptfoo와 Giskard를 동시에 완전 통합하면 adapter·결과 정규화 작업이 늘어난다. 첫 실행 엔진은 하나를 택하고 다른 엔진은 제한된 비교 실험으로 사용하는 편이 타당하다. provider 기반 생성·LLM judge에는 해당 API 접근과 비용이 필요하다. README의 telemetry는 선택적 집계 분석이며 prompts/outputs는 전송하지 않는다고 설명하지만, 이는 LLM provider로 보내는 평가 요청과 별개다. 공개 LICENSE는 Apache-2.0 [G2]. v2의 Hub/RAGET 설명을 v3에 그대로 붙이지 않는다.

**Cisco AI Defense — 독립 판정의 차별화 주장에 가장 중요한 확인 대상**

사용자 표에는 실제 에이전트 공격 시험, 도구·간접 입력·지속 상태 검사, 독립 관측을 통한 성공 확인이 적혀 있다. 이 설명이 원문과 일치한다면 FlowDelta의 ⑤–⑥과 매우 가깝다. 그러므로 **“기존 제품은 답변만 보고 우리는 독립 oracle을 쓴다”는 주장은 성립하지 않을 수 있다.**

다만 이번 환경에서 제공된 Cisco URL은 프록시 403으로 열리지 않았다. 다음은 확인 과제이며 기능 부재로 처리하지 않는다: Explorer가 임의의 자체 n8n/MCP 대상에 연결 가능한지, 지속 상태 초기화와 버전 비교가 어떤 범위인지, 독립 관측기의 권한·결과 형식·export/API·시험 제한이 무엇인지, 변경 그래프가 시험 선택의 입력인지, 무료와 상용의 차이가 무엇인지. 사용자 표의 “무료 Explorer”를 무제한·범용·로컬 사용 가능으로 확대 해석하지 않는다. 원문 및 실제 계정 검증 전에는 Cisco 대비 탐지 우위·독창성을 결론 내리지 않는다.

**Snyk Agent Scan — Snapshot/구성 위험 계층과 직접 중첩**

공식 README는 설치된 agent harness·MCP·Skill을 탐색하고 prompt injection, 민감정보 처리, 악성 자연어·코드 등 위험을 분석한다고 설명한다. 현재 설명은 0.5.x의 issue-code 출력과 0.6+의 risk-based 출력을 구분하며, CLI JSON/위험 이름/점수/필드가 실험적이라고 명시한다 [S1]. FlowDelta는 이를 내부 표준 Finding으로 바꾸는 adapter와 버전 고정이 필요하다.

이 도구는 순수 파일 정적 분석이라고 보기 어렵다. 도구 설명 수집을 위해 stdio MCP 설정의 명령을 실행하거나 remote MCP에 연결할 수 있고, 분석에 필요한 component 정보를 Agent Scan API로 보낸다. 현재 Quick Start는 `SNYK_TOKEN`을 요구한다. 공개 CLI LICENSE는 Apache-2.0 [S2]지만 서비스 의존성과 별개다.

FlowDelta는 발견한 구성과 위험 후보를 ①–③에 받아 **전후 구성의 결합 조건**을 분석할 수 있다. 예를 들어 “기밀 조회 능력”과 “제약 없는 전송 능력”은 위험 후보이지 실제 유출 증거가 아니다. Snyk 탐지 결과를 그대로 ⑥의 공격 성공으로 승격해서는 안 된다. untrusted MCP 서버 기동은 분석·제어 영역이 아니라 격리 영역에서 수행하는 것이 첨부 설계의 신뢰 경계와 맞는다.

**LangSmith — 결과 비교와 실행 추적에서 이미 강한 대체 기능**

공식 비교 문서는 동일 dataset에서 두 개 이상의 experiment를 선택해 feedback key별 regression/improvement를 보고, 두 실험의 JSON/YAML/text output diff와 trace를 나란히 확인한다고 설명한다 [L1]. 평가 문서는 curated dataset·code/LLM/human/pairwise evaluator·반복 횟수·동시성·캐싱을 포함한다 [L2].

“업데이트 전후 평가 결과를 표로 보여준다”는 FlowDelta 기능은 크게 겹친다. 다만 실행 trace를 비교하는 것과 **배포 전 구성의 데이터·권한·보호 조건 graph diff**는 서로 다른 분석이다. FlowDelta의 Snapshot/ChangeSet/Hypothesis ID를 experiment/run metadata에 넣고 독립 oracle 결과를 feedback으로 연결하면 보고 UI를 재사용할 수 있다.

custom code evaluator가 외부 관측 서비스를 조회하게 할 수 있으므로 LangSmith가 실제 효과 판정을 원천적으로 못한다고 말하면 안 된다. 차이는 그 관측기·권한 분리·증거 결합을 누가 구축하느냐다. 계정/API key와 trace 저장 정책·플랜을 확인해야 하며, 합성 기밀이라도 실험 입력·출력·trace의 외부 저장 범위를 결정해야 한다. 정확한 현행 요금과 self-hosting 제공 조건은 이번 원본에서 확인하지 않았다.

**n8n Evaluations — 1차 플랫폼에 이미 있는 평가 기능**

공식 문서는 dataset을 workflow에 반복 투입해 결과를 저장하고 metric을 비교하는 흐름을 제공한다 [N1]. metric-based evaluation은 correctness/helpfulness·문자열 유사도·분류·Tools Used·custom metric을 설명한다 [N3]. AI Agent의 `Return intermediate steps`를 켜면 `intermediateSteps`로 실행 도구 정보를 평가할 수 있다 [N4]. 따라서 “도구 실행을 평가하지 않는다”는 비교도 부정확하다.

반면 Tools Used나 intermediateSteps는 금지된 수신처의 실제 수신을 자동 증명하지 않는다. custom metric을 외부 oracle 결과로 만들면 보안 평가가 가능하지만, metric 계산이 시험 workflow 내부에 있다는 사실만으로 독립성이 성립하지 않는다. 별도 서비스와 읽기 전용 결과 계약이 필요하다.

평가 trigger를 삽입하고 workflow 내부에 metric 로직을 넣는 방식은 시험 대상 export 자체를 바꿀 수 있다. 두 버전의 업무 경로를 똑같이 instrument했는지, webhook 인증·승인·진입 제어를 평가 trigger가 우회하지 않는지 확인해야 한다. trigger 뒤부터 실행한 평가는 실제 webhook 진입 통제 전체의 검증과 다르다.

확인한 문서에서 light evaluation은 Cloud 모든 플랜과 self-hosted Registered Community/Business/Enterprise, metric-based는 Cloud Pro/Enterprise와 self-hosted Enterprise를 설명하고 Registered Community·Starter는 한 workflow 사용을 허용한다 [N2–N3]. 같은 metric 문서의 동시성 표에는 self-hosted Business도 등장하므로, 모든 플랜 차이를 이 표 하나로 확정하지 말고 사용하는 n8n 버전·라이선스에서 기능 노출을 확인해야 한다. 8주 구현을 유료 평가 기능에 필수 의존시키기보다 외부 runner와 독립 oracle로 구성하고 내장 평가는 정상 업무 비교에 선택적으로 활용할 수 있다.

## 5. 추가해야 할 직접 비교 대상: n8n-ai-agent-security-lab

이 저장소는 팀 자료에 이미 언급되어 있고, 확인한 최신 README에는 정적 경로 audit, exposure graph, 여러 workflow의 trust-boundary map, baseline/candidate change review, staging regression gate, fingerprint와 연결된 receipt, 제한된 local action rehearsal가 있다 [X1]. FlowDelta의 graph·변경·실행·증거 연결과 상당히 겹친다. 6개 도구만 비교하고 이 대상을 제외하면 직접적인 선행 구현을 놓칠 수 있다.

문서가 밝힌 한계도 구체적이다. local rehearsal는 literal Webhook/Set 및 credential-free HTTP Request의 제한된 비순환 경로를 대상으로 하고, 합성 요청을 로컬 capture service로 보낸다. 포함된 runtime staging fixture에는 AI node가 없으며 prompt-injection marker 시험은 승인 제어를 검사하고 실제 모델의 주입 저항을 검증하지 않는다. generic gate의 receipt는 선택된 local candidate fingerprint를 기록하지만 원격 n8n 배포 내용을 독립적으로 읽어 attestation하지 않는다 [X1]. README의 통과 수치와 점수는 저자 주장으로 읽었고 재현하지 않았다.

따라서 비교할 질문은 **실제 모델이 간접 입력을 읽고 MCP/Skill과 결합된 도구를 선택하는 경우에도, 변경 조건으로 시험을 골라 독립 수신/쓰기 결과를 증명하는가**다. FlowDelta가 이 확장을 실제로 구현·검증해야 차이를 주장할 수 있다. 그래프·receipt·diff 자체를 신규 기능이라고 내세우는 것은 피한다.

## 6. 첨부 예시를 모든 도구에 공통으로 적용하면

동일 업무는 “외부 문의를 요약해 내부 담당자에게 전달”이다. 기준 구성은 공개 FAQ 읽기+내부 수신자 고정, 후보 구성은 기밀 검색 추가+수신자를 모델이 선택, 수정 구성은 기밀 조회 유지+전송 도구에서 내부 수신자 목록 강제다.

| 대상 | 이 예시를 어떻게 시험하는가 | 별도로 준비할 부분 |
|---|---|---|
| Promptfoo | 외부 문의/검색 결과의 간접 주입, agent target 실행, toolCalls/trajectory assertion, 같은 fixture 재실행 | n8n 두 버전·권한 환경, graph diff, 시험 선택, 합성 비밀 수신 oracle |
| Giskard | target adapter, 다중 턴 Scenario/Suite, injection generator/custom Check | 같은 실험실·변경 분석·독립 효과 관측 |
| Cisco | 사용자 표대로라면 공격 시험과 독립 관측을 직접 비교할 후보 | 원문 확보 후 n8n adapter·버전 비교·oracle 범위 검증 |
| Snyk | 도구 설명·Skill·구성에서 기밀 접근/전송/주입 위험 조사 | 실제 업무 실행과 금지 수신처에 도착했는지 검증 |
| LangSmith | 동일 dataset의 baseline/candidate/fixed experiment, trace/feedback 비교 | 공격 fixture, 구성 변화 해석, 독립 결과를 feedback으로 연결 |
| n8n Evaluations | 동일 dataset 실행, intermediateSteps/custom metric, 정상 업무 비교 | 실제 진입 경로 보존, 버전 격리, 외부 수신/쓰기 oracle |
| FlowDelta | 두 변경을 경로·조건으로 분석→카드 검색→검증된 계획→전후 실행→독립 수신/상태 판정→수정본 재시험 | 첨부 설계의 각 부분을 구현하고 통합 재현해야 함 |

기밀 접근 추가와 수신자 제약 제거가 동시에 바뀌면, baseline/candidate 둘만으로 어느 변경이 원인인지 분리하기 어렵다. **기준 / 조회 능력만 추가 / 수신자만 자유화 / 두 변경 동시 적용 / 도구 수준 allowlist 수정**의 5개 구성을 시험하면 결합 효과를 조사할 수 있다. 기밀 조회만 추가한 구성도 내부 수신자 권한이 적절한지는 별도 정책 문제이므로 “전체 안전”으로 처리하지 않는다.

## 7. 차별화할 수 있는 주장과 피해야 할 주장

| 주장 | 판단 | 필요한 증거 |
|---|---|---|
| 공격 문장을 자동 생성한다 | 이미 중첩 | Promptfoo/Giskard 대비 추가 효용을 측정해야 함 |
| 실행 기록을 보므로 기존 도구보다 정확하다 | 현재 근거 부족 | Promptfoo trace-aware/결정적 assertion과 같은 관측 조건에서 비교 |
| 독립 oracle이 새롭다 | 신규성 미확립 | Cisco 원문 확인, 선행 구현 조사, 외부 oracle을 연결한 기존 엔진과 비교 |
| workflow graph/diff를 제공한다 | 선행 구현과 중첩 | 보안 의미 분석 정확도와 시험 선택 개선을 측정 |
| RAG로 알려진 취약점을 찾는다 | 기능 자체의 차별성 약함 | 조건 필터가 잘못된 적용을 얼마나 줄이는지 측정 |
| 변경으로 영향받는 정책 경로를 찾아, 같은 예산에서 유효한 시험을 우선한다 | 유망한 연구 가설 | 전체 시험/무작위/키워드/조건 선택 기준선과 비용·탐지율 비교 |
| 실제 효과·관측 실패·실험실 차단을 구분하고 정확한 후보에 증거를 연결한다 | 유효한 시스템 목표 | 의도적 관측 장애·후보 해시 불일치·지연 효과·차단 주체 시험 |
| 모든 워크플로/Skill/MCP가 안전함을 증명한다 | 설계도 그렇게 주장하지 않음 | 시험 범위 밖 안전성을 일반화하지 않는다 |

추천 소개 문장: **“FlowDelta는 n8n 에이전트의 구성 변경이 기밀 전송과 무단 쓰기 정책에 미치는 영향을 분석하고, 관련 시험을 선택해 전후 실행의 독립 효과 증거와 연결하는 보안 회귀 검증 연구 시스템이다.”** 지원 엔진·표현식·관측 범위를 함께 명시한다.

## 8. 현재 설계에서 구체화해야 할 계약

**Snapshot은 선언과 실제 관측을 구분해야 한다.** export의 credential reference는 실제 계정 권한을 증명하지 못한다. 도구 설명에 “read-only”라고 적혀 있어도 서버가 다른 동작을 할 수 있다. 각 capability/guard에 `declared`, `observed`, `unknown`에 해당하는 상태와 출처를 두고, 미확인 설정을 “권한 없음”으로 축약하지 않는다. candidate fingerprint뿐 아니라 실행 환경·effective policy·모델·도구 버전·knowledge card revision까지 Run과 결합한다. 가능한 범위에서 실제 로드된 후보의 식별 정보를 확인하고, 모의 환경으로 대체한 부분은 따로 표시한다.

**Graph 추출은 지원 범위를 제한해야 한다.** n8n expression·Code node·조건 분기·동적 sub-workflow·외부 MCP의 실제 권한을 모두 정적으로 해석하기는 어렵다. source/sink/control/권한 확대와 관련된 작은 node 집합을 먼저 지원하고, 동적 해석이 필요한 edge는 unknown으로 남긴다. 객체 노드 ID가 바뀌었지만 의미는 같은 경우와, ID는 같지만 의미가 바뀐 경우를 구분할 매칭 규칙도 필요하다. 제어가 존재한다는 것뿐 아니라 실행되는 경로에서 그 제어가 실제 효과보다 앞서 강제되는지 확인해야 한다.

**카드는 적용 근거와 시험 조건을 가진다.** 카드에는 공식 출처·영향 버전·공격자가 통제할 입력·필요 capability·guard 조건·지원 template·판정 유형을 둔다. vector similarity는 후보 검색이고 CVE 적용 확인은 별도 조건 판단이다. 일반 공격 패턴을 CVE 재현으로 표시하지 않는다. 정책에서 직접 만든 시험을 지식 카드 검색의 fallback으로 유지한다.

**TestPlan은 타입이 있는 제한된 데이터여야 한다.** `entry_point`, `node_id`, `scenario_id/version`, `template_id/version`, `policy_id`, `fixture_id`, `oracle_id`, `budget`, 전후 환경 조건을 검증한다. 카드·Skill·도구 설명도 비신뢰 자료이므로 그 안의 명령을 planner의 권한으로 승격하지 않는다. LLM은 등록된 공격 템플릿의 허용 파라미터만 선택하고, 대상·관측기 endpoint·판정 정의를 바꾸지 못하게 한다.

**독립성은 별도 프로세스 이름만으로 보장되지 않는다.** target/LLM이 observer 저장소·판정 규칙·Run ID 대응표를 수정할 수 없어야 한다. canary는 run마다 다르고 보호 문서에만 있어야 하며, attacker 입력에 같은 canary를 미리 넣으면 반사 출력도 유출로 오인한다. 문서 쓰기는 tool log가 아닌 target resource의 전후 상태와 쓰기 event로 확인하고, 정당한 업무 변경과 금지된 변경을 나눈다. 수신 기록에는 role·수신자·Run ID·시간·내용 검증 결과를 연결하고 replay·다른 run의 지연 이벤트를 배제한다.

**결과를 한 pass/fail로 압축하지 않는다.** 첨부 설계는 위반·대상 통제 차단·시도·미관측·판단 불가·미실행을 구분한다. 구현에서는 `execution_status`, `observation_status`, `policy_outcome`, `blocking_actor`를 독립 축으로 두는 방식을 권한다. 이름 자체보다 구분이 중요하다. tool error·timeout·실험실 firewall 차단을 대상 방어 성공으로 세지 않고, 시험이 끝나도 지연 작업의 완료·관측 범위를 보고해야 한다.

**비교의 인과 해석을 제한한다.** reset된 memory·문서·queue·credentials, 동일 test fixture·모델 설정·실행 예산, 반복 횟수·모델 버전을 기록한다. LLM은 같은 입력이어도 달라질 수 있고 seed만으로 결정성을 보장할 수 없다. 고정 tool-call replay는 실행 제어 검증이고 실제 agent 실행은 모델의 경로 선택 검증이다. 둘의 결과를 합쳐 “주입 성공률”로 보고하지 않는다. “후보에서만 관측된 회귀”와 “특정 변경이 유일 원인임을 입증”도 구분한다.

## 9. 실제 비교 실험의 추천 설계

**주 비교는 엔진 경쟁보다 시험 선택 방식 비교가 되어야 한다.** 동일 runner·모델·fixture·oracle을 공유하고 다음을 비교한다.

| 기준선 | 역할 | 공정한 비교 조건 |
|---|---|---|
| 전체 등록 시험 | 제한된 시험 집합에서의 경험적 비교 기준 | 같은 유효 oracle과 반복 조건; 모든 공격의 완전한 ground truth라고 부르지 않음 |
| 고정 시험 또는 무작위 선택 | 동일 예산에서 단순 선택 대비 효과 | 공격 수뿐 아니라 모델 호출·시간·token 예산도 맞춤 |
| 키워드/벡터 검색만 사용 | RAG 자체의 기여를 분리 | 같은 카드·generator·실행 엔진 |
| graph diff + 조건 필터 | FlowDelta 선택 로직의 기여 | graph/필터 유무만 바꾸는 ablation |
| Promptfoo 기본 grader/trace assertion + 공통 독립 oracle | 판정 방식과 증거 수준 비교 | 도구를 일부러 출력 전용으로 제한하지 않음 |
| 제한된 n8n-ai-agent-security-lab 적용 | 직접 선행 구현과의 범위 비교 | 지원하는 subset을 명시; AI node 미지원은 성능 실패와 구분 |

Giskard는 동일한 소수 fixture로 adapter 가능성과 결과 호환성을 비교할 수 있다. LangSmith/n8n은 보안 탐지 엔진과 같은 순위표에 넣기보다 실험 운영·보고·정상 업무 평가 비용을 비교한다. Cisco는 접근과 원문 확인 후 가능한 대상/시험 범위에 맞춰 포함하고, 미실행을 실패로 점수화하지 않는다.

필수 평가 항목은 다음과 같다.

- **변경 탐지 정확도:** node/edge/capability/guard 변경의 수작업 기준 정답과 비교. 의미 변화 없는 순서·ID 수정도 포함.
- **선택 recall과 효율:** 전체 등록 시험에서 관측한 위반 중 선택 시험이 얼마나 다시 발견했는지, 발견까지 비용·시간·실행 수. 기밀 전송·무단 쓰기를 따로 보고.
- **조건 필터의 오류:** 적용 불가 버전·입력 통제권 없음·권한 없음·미지원 oracle 등을 정확히 제외했는지. 미확인 때문에 누락한 위험도 별도 집계.
- **판정 정확도:** 실제 수신, 전송 시도만 있음, tool의 허위 성공 응답, observer 장애, timeout, 실험실 차단, 후보 해시 불일치, 지연 event를 미리 구성해 판정 확인.
- **정상 업무 유지:** 내부 수신자 전달·허용된 읽기·정당한 쓰기 성공률과 지연. 모두 차단하는 수정이 좋은 보안으로 보이지 않게 함.
- **변경 결합 효과:** 앞의 5개 구성에 같은 시험을 적용해 조회 권한과 전송 자유화의 결합을 조사.
- **반복 불확실성:** 각 구성/공격별 실행 수·위반 수·rate와 신뢰구간, unknown/error/unsupported 비율. 평균 점수만으로 희소한 실제 위반을 숨기지 않음.
- **증거 완전성:** 모든 Finding에서 정확한 snapshot/card/template/run/evidence로 되짚을 수 있는지. 해시가 provenance를 연결하는 것과 증거 저장소가 변조 불가능한 것은 별도 검증.

처음에는 작은 고정 fixture로 pilot을 수행해 비용과 변동성을 측정하고 반복 수를 정한다. 반복·공격 예산을 사전에 정해 유리한 결과가 나올 때까지 실행 횟수를 늘리지 않는다. CVE 재현 여부와 일반 정책 위반은 별도 label로 남긴다.

## 10. 4명·8–10주에 맞는 구현 우선순위

**①–② 담당:** 지원 node와 expression 범위, Snapshot/ChangeSet 계약, capability/control graph, 변경 매칭과 unknown 처리. 처음부터 모든 n8n node나 모든 프레임워크를 분석하지 않는다.

**③–④ 담당:** 소수의 사람 검토 카드, 구조화 조건 필터, 등록 template와 Plan validator. pgvector·키워드 검색은 구현 수단이며 RAG UI 확장은 필수 검증 이후로 둔다. 카드와 planner가 실제 실행/판정 권한을 가지지 않게 한다.

**⑤–⑥ 담당:** reset되는 n8n 실험실·모의 MCP·합성 fixture·독립 receiver/resource observer, read-only 결과 계약. 가장 먼저 “기준/후보/수정본 + 정상 대조”의 작은 세로 흐름을 완성해 graph/검색에서 만든 계획이 실제 증거까지 연결되는지 확인한다.

**평가·보고 담당:** 5개 구성과 실패 fixture, 공통 oracle, 선택 기준선·ablation, 사례별 실행 결과·비용·한계 보고. 예쁜 그래프보다 모든 Finding의 증거 연결과 실제 정상 업무 유지가 먼저다.

초기 통합 후보는 **Promptfoo 한 엔진 + FlowDelta의 변경 선택·격리·독립 oracle**이다. Python 코어와 Scenario 계약이 더 잘 맞는다면 Giskard로 대체할 수 있다. 두 엔진·LangSmith·Snyk·n8n 내장 평가를 모두 필수 의존성으로 넣는 것은 범위를 키운다. Snyk은 선택적인 구성 위험 공급자, LangSmith는 선택적인 결과 운영 UI, n8n Evaluations는 정상 업무 대조를 돕는 선택 기능으로 두는 편이 현재 범위에 맞는다.

이 추천은 성능 검증 결론이 아니다. 최신 공개 문서의 확장 지점과 첨부 설계의 구현 범위를 바탕으로 한 선택이다. Cisco의 Explorer 조건 확인과 `n8n-ai-agent-security-lab`의 직접 비교 없이 신규성 결론을 확정하지 않는다.

## 출처

아래 링크는 읽은 공식 문서/README에 대응한다. 고정 커밋 URL·파일 해시는 동봉한 JSON 기록을 따른다. 첨부 HTML이 연결한 `README.md`, `execution-plan.md`, `research-evidence.md`는 첨부에 포함되지 않아 읽지 못했다. 이번 비교는 HTML에 드러난 구조에 한정한다.

- **P1:** [Promptfoo 에이전트 보안 시험](https://www.promptfoo.dev/docs/red-team/agents/) / [공식 원본](https://github.com/promptfoo/promptfoo/blob/main/site/docs/red-team/llm-agents.md)
- **P2:** [MCP provider 공식 원본](https://github.com/promptfoo/promptfoo/blob/main/site/docs/providers/mcp.md)
- **P3:** [간접 prompt injection 공식 원본](https://github.com/promptfoo/promptfoo/blob/main/site/docs/red-team/plugins/indirect-prompt-injection.md)
- **P4:** [tracing 공식 원본](https://github.com/promptfoo/promptfoo/blob/main/site/docs/tracing.md)
- **P5:** [CI/CD 공식 원본](https://github.com/promptfoo/promptfoo/blob/main/site/docs/integrations/ci-cd.md)
- **P6:** [Promptfoo LICENSE](https://github.com/promptfoo/promptfoo/blob/main/LICENSE)
- **G1:** [Giskard 공식 README](https://github.com/Giskard-AI/giskard/blob/main/README.md)
- **G2:** [Giskard LICENSE](https://github.com/Giskard-AI/giskard/blob/main/LICENSE)
- **C1:** [Cisco 제공 링크 — 원문 접근 실패](https://blogs.cisco.com/ai/agent-validation-explorer-edition). 본문 기능 설명은 사용자 표 기반이며 독립 검증되지 않았다.
- **S1:** [Snyk Agent Scan 공식 README](https://github.com/snyk/agent-scan/blob/main/README.md)
- **S2:** [Snyk Agent Scan LICENSE](https://github.com/snyk/agent-scan/blob/main/LICENSE)
- **L1:** [LangSmith 실험 비교 공식 원본](https://github.com/langchain-ai/docs/blob/main/src/langsmith/compare-experiment-results.mdx)
- **L2:** [LangSmith 평가 공식 원본](https://github.com/langchain-ai/docs/blob/main/src/langsmith/evaluation.mdx)
- **N1:** [n8n 평가 개요 공식 원본](https://github.com/n8n-io/n8n-docs/blob/main/docs/build/integrate-ai/test-and-improve-ai-workflows/understand-why-to-test.md)
- **N2:** [n8n light evaluation 공식 원본](https://github.com/n8n-io/n8n-docs/blob/main/docs/build/integrate-ai/test-and-improve-ai-workflows/run-quick-evaluations.md)
- **N3:** [n8n metric evaluation 공식 원본](https://github.com/n8n-io/n8n-docs/blob/main/docs/build/integrate-ai/test-and-improve-ai-workflows/use-metrics-to-measure-quality.md)
- **N4:** [n8n 평가의 tool data·반복·trigger 주의사항](https://github.com/n8n-io/n8n-docs/blob/main/docs/build/integrate-ai/test-and-improve-ai-workflows/fix-common-issues.md)
- **X1:** [n8n-ai-agent-security-lab README](https://github.com/0xCD4/n8n-ai-agent-security-lab/blob/main/README.md). 도구 저자의 설명을 읽었으며 통과 수치와 점수는 재현하지 않았다.
