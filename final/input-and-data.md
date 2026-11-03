# FlowDelta 입력 고정 범위와 현실적인 데이터 구성안

기존 본문 기준일: **2026-10-09, Asia/Seoul**. §10의 CVE 자료원·카드 기준 및 후보 확인일: **2026-10-29**. 지원 버전·사례 선정·정답 라벨은 각 절의 근거와 상태를 따른다. [전체 아키텍처](README.md)와 [실행·평가 계획](execution-plan.md)을 함께 사용한다.

## 현재 방향

**연구 평가를 우선하는, 지원 범위가 명확한 오픈소스 도구를 만든다.** 분석 프로그램은 여러 입력을 받도록 만들고, 평가할 때는 미리 정한 사례와 조건을 고정한다. 하나의 비교쌍에서는 업무·정책·초기 데이터를 동일하게 두고, 데이터셋 전체에서는 여러 업무 요청·워크플로우 계열·환경을 다룬다.

공개 코드, 재현 가능한 평가 묶음, 사용자 입력 형식을 함께 제공할 수 있다. 초기에 모든 n8n 노드·모든 정책·운영 SaaS 연결을 지원해야 오픈소스가 되는 것은 아니다. 연구를 한다고 업무와 워크플로우를 하나로 영구 고정할 필요도 없다.

여기서 ‘기존 n8n/수정된 n8n’은 먼저 워크플로우와 그 의존성의 이전·이후 구성으로 해석한다. n8n 엔진 자체의 버전 변경은 별도 비교 유형으로 둔다.

## 1. 어디에서 무엇을 고정할 것인가

| 입력 | 한 비교쌍 안에서 | 데이터셋·다른 사용 사례 사이에서 |
|---|---|---|
| 업무 목적과 정상 완료 조건 | 동일하게 유지 | 여러 업무·요청으로 다양화 |
| 평가 정책 | 동일 정책으로 양쪽을 판정 | 같은 지원 정책 형식 안에서 허용 자원·주체·목적지 등을 다르게 설정 |
| 초기 데이터·계정·상태 | 동등한 별도 초기 상태에서 시작 | 서로 다른 업무 사례를 구성 |
| 기존 워크플로우 | 그 사례의 기준본으로 고정 | 서로 다른 공개 원본·독립 계열 사용 |
| 수정 워크플로우 | 비교하려는 변경을 포함 | 실제 변경, 검토한 정상 변경, 통제된 평가 사례 등을 구분 |
| 하위 의존성·권한·환경 | 비교 대상인 변화만 달리하고 나머지는 통제 | 별도 환경 변화·의존성 변화 사례로 다양화 |
| n8n·모델·분석기 버전과 실행 예산 | 해당 비교의 조건을 고정하고 기록 | 다른 버전·모델 일반화는 분리된 실험으로 수행 |

상태를 고정한다는 것은 두 버전이 같은 변경 가능한 DB를 공유한다는 뜻이 아니다. 같은 초기 내용에서 각각 시작하고 실행의 잔여 상태를 다음 사례로 넘기지 않는다는 뜻이다. 모델의 출력까지 동일해진다고 보장할 수는 없으므로 반복과 불확실성을 기록한다.

워크플로우만 바꾸는 비교, 부모 워크플로우를 유지하고 하위 의존성을 바꾸는 비교, 같은 워크플로우에서 환경을 바꾸는 비교를 구별한다. 동시에 여러 요소가 달라진 실제 이력은 변경 묶음의 영향으로 먼저 보고하고 단일 변경의 인과 효과로 단정하지 않는다.

업무나 정책 자체가 달라졌다면 요구사항 변경이다. 기존 정책에서 금지됐던 일을 새 정책에서 허용했다는 이유만으로 자동으로 보안 회귀라고 분류하지 않는다. 공통으로 유지된 요구사항에 대한 비교와 변경된 요구사항에 대한 적합성 판단을 구별한다.

## 2. 업무·정책·구현을 분리한다

업무는 ‘무엇을 해야 하는가’, 정책은 ‘누가 어떤 조건에서 어디까지 할 수 있는가’, 워크플로우는 ‘그 일을 어떤 절차로 하는가’다. 초기 데이터는 그 업무를 수행할 때의 고객·주문·문서 등의 시작 상태다.

예시 업무는 ‘인증된 고객에게 본인 주문의 배송 상태를 안내한다’다. 이 사례의 완료 조건은 올바른 주문 상태를 응답하는 것이다. 정책에는 다른 고객의 정보 제공 금지, 조회 요청 중 보호 주문의 변경 금지, 필요한 상담 기록 추가 허용 등을 명시할 수 있다. 이는 설명용 정책 예시이며, 실제 도입 시 운영자의 업무 규칙을 확인해야 한다.

‘읽기 업무’라도 감사 로그·상담 기록 등 승인된 부수 기록은 생길 수 있다. 모든 쓰기를 금지하면 정상 동작도 위반으로 잘못 분류한다. 보호 대상과 허용 부수 효과를 구체화해야 한다.

정책은 워크플로우의 현재 행동만 보고 역으로 정하지 않는다. 현재 행동을 기준으로 허용 범위를 만들면 현재의 잘못된 동작도 정당화할 수 있다. 정책의 출처를 운영자 확인, 공개 benchmark, 연구자 정의로 나누고 원문과 대응시킨다. 자동 추출한 정책 후보는 사람 검토를 거친다.

MVP에서 고정할 것은 P1·P2와 같은 정책의 지원 형식이다. 허용 고객·문서·수신자·테넌트와 같은 값은 사례별 입력으로 둔다. 자연어 정책을 제한 없이 해석하는 기능은 별도 과제다.

정책과 정상 완료 조건은 분석기에 필요한 입력이다. 숨겨야 할 평가 정답은 최종 위반 라벨·정답 경로·최종 평가의 예상 관측 결과 등이다. 업무용 문서 검색 지식과 분석기의 보안 사례 검색 지식도 구분해야 한다.

## 3. 실제로 확인한 자료

자료의 존재·문서·일부 JSON 구조를 읽기 전용으로 확인했다. 워크플로우를 import·activate·execute하지 않았고, 실제 배포 실적이나 보안 상태를 인증하지 않았다.

| 자료 | 확보할 수 있는 것 | 이번 확인 | 사용 위치와 한계 |
|---|---|---|---|
| [n8n 주문 고객지원 템플릿 14550](https://n8n.io/workflows/14550-handle-e-commerce-support-on-telegram-with-gemini-and-google-sheets/) | 주문 조회·주문 취소·상담 티켓의 공개 업무 구조와 JSON | 공식 API에서 JSON nodes 18개 확인. 설명용 Sticky Note 포함 | 업무·도구·상태의 관계를 분석할 후보. 실제 기업 운영 기록이나 검증된 안전 기준본은 아님 |
| [n8n 티켓 라우팅 템플릿 18499](https://n8n.io/workflows/18499-route-and-respond-to-support-tickets-with-google-sheets-slack-and-gemini/) | 요청 검증·분류·주문/정책 조회·Slack 이관·로그 기록 | 공식 API에서 JSON nodes 60개 확인. 설명용 노드 포함 | 현실적인 복합 흐름을 확인할 후보. 현재 지원 후보 밖의 동작이 있어 즉시 실행 평가용으로 확정할 수 없음 |
| [현재 τ-bench 저장소](https://github.com/sierra-research/tau2-bench) | 업무 요청, 정책, 초기 상태·DB, 평가 기준 | retail/tasks.json 114개 확인. policy.md·db.json·split_tasks.json 존재 확인 | 재현 가능한 업무 맥락 구성에 적합. 실제 회사 운영 DB가 아닌 연구용 환경이며 n8n 원본도 아님 |
| [n8n 공식 AI starter kit](https://github.com/n8n-io/self-hosted-ai-starter-kit) | 공식 예제 JSON과 환경 구성, Git 변경 이력 | 한 예제 파일의 실제 노드 버전 변경 커밋 확인 | 실제 변경쌍 확보 방식을 확인할 수 있음. 이것만으로 보안 회귀의 정답이 있지는 않음 |
| [n8n 공식 test-workflows](https://github.com/n8n-io/test-workflows) | 노드 동작을 검증하는 workflow 자료 | 저장소의 공개 목적과 파일 목록 확인 | 의미 해석기의 정확성 확인에 유용. 실제 운영 업무 평가셋과 구별 |

공식 API 정적 확인 경로는 [14550](https://api.n8n.io/api/templates/workflows/14550), [18499](https://api.n8n.io/api/templates/workflows/18499)다. 노드 수는 API 응답의 nodes 배열 길이이며 실행되는 노드 수나 지원 가능한 동작 수가 아니다. 원본 응답을 파일로 저장하거나 실행하지 않았다.

14550에는 AI Agent·Gemini·메모리·Code·Google Sheets Tool·Telegram 등이 있고, 18499에는 Code·Sheets·Slack·분류/추출·오류/예약 트리거 등의 동작이 있다. 따라서 실제 후보를 먼저 확인하고 지원 범위를 결정해야 한다. 모든 외부 노드를 임의 HTTP 노드로 바꾼 뒤 원본과 동일하다고 주장하면 안 된다.

τ-bench는 구 저장소가 현재 저장소의 수정된 과제를 사용하라고 안내한다. 현재 저장소는 τ³-bench를 안내하지만 URL은 tau2-bench다. 고정한 커밋·과제 버전을 사용해야 한다. retail 자료는 [정책](https://github.com/sierra-research/tau2-bench/blob/main/data/tau2/domains/retail/policy.md), [업무](https://github.com/sierra-research/tau2-bench/blob/main/data/tau2/domains/retail/tasks.json), [초기 DB](https://github.com/sierra-research/tau2-bench/blob/main/data/tau2/domains/retail/db.json)에서 확인할 수 있다. 정책은 본인 업무 범위와 상태 변경 전 확인 등의 규칙을 명시한다. MIT 표시는 저장소에서 확인했다.

τ 자료를 n8n으로 옮기면 ‘τ 기반 n8n 변환 사례’다. 원 benchmark 그대로의 평가라고 표현하지 않는다. 참고 동작 목록이 항상 유일한 정답 호출 순서는 아니며, 기본 평가는 DB 최종 상태 등을 사용한다. 정상 업무 점수를 모든 보안 정책 준수의 증거로 대체해서는 안 된다. [평가 명세](https://github.com/sierra-research/tau2-bench/blob/main/docs/evaluation.md)

확인한 실제 변경은 starter kit의 [9ccbaf42](https://github.com/n8n-io/self-hosted-ai-starter-kit/commit/9ccbaf42e007369453acaec60b9808cf8e6cdb44)다. Basic LLM Chain의 typeVersion 변경이며 작성일은 2025-09-01이다. 정상 변경 후보로 검토할 수 있지만 이번에 안전성 라벨을 확정한 것은 아니다.

반대로 [다른 고객지원 공개 저장소](https://github.com/ibam28/customer-support-ai-automation-n8n)는 전체 커밋 수와 달리 workflows 경로에서 확인된 이력이 최초 추가 1개였다. 저장소에 커밋이 여러 개 있다는 사실만으로 해당 업무의 전후 변경 데이터가 확보됐다고 볼 수 없다.

보조 자료로 [AgentDojo](https://github.com/ethz-spylab/agentdojo)는 업무 환경과 평가 구조를 참고할 수 있다. n8n 실제 운영 이력 데이터로 취급하지 않는다. [n8n 100-template study](https://github.com/0xCD4/n8n-ai-agent-security-lab/blob/main/research/template-study/README.md)는 공개 템플릿 표집·출처·해시 관리의 참고 사례이며 정적 경고를 확정 취약점 라벨로 사용하지 않는다. [10,803개 공개 템플릿을 분석한 연구](https://arxiv.org/html/2609.13136v1)는 업무·구조 분포 참고 자료다. 그 전체 corpus의 다운로드 가능성은 이번에 확인하지 않았다.

이번 확인 범위에서는 ‘실제 운영 워크플로우의 전후 구성 + 당시 정책 + 업무 입력/초기 상태 + 권한 + 보안 정답’을 모두 갖춘 완성된 n8n 회귀 데이터셋은 확보하지 못했다. 필요한 구성요소를 출처를 보존하며 결합하는 작업이 필요하다.

## 4. 현실성을 확보하는 방법

서로 다른 출처를 섞어 하나의 ‘실제 데이터’ 점수로 발표하지 않고 다음 집합을 나누어 관리한다.

| 집합 | 내용 | 입증하는 것 |
|---|---|---|
| 공개 원본과 실제 변경 이력 | 작성자가 공개한 workflow·commit·문서 | 현실적인 구성과 변경에서의 적용 가능성·분석 범위·수작업 부담 |
| 공개 업무에서 가져온 통제 평가 | 출처가 있는 업무 구조에 정책·초기 상태·독립 판정을 명시한 정상/위반/판단불가 사례 | 알려진 조건에서의 판정 정확성과 재현성 |
| 운영자 제공 사례 | 동의를 얻은 전후 구성·업무 요청·정책·환경 사실 | 실제 운영 맥락에서의 외부 타당성 |

연구자가 만든 변경은 연구자 생성으로 표시한다. 공개 템플릿은 공개 원본이라고 표시한다. 실제 운영 이력은 운영자 확인이나 이에 준하는 근거가 있을 때 표시한다. 안전성이 미확인인 공개 기준본은 ‘안전’ 라벨을 자동 부여하지 않는다. 기존 위험이 양쪽에 있는 경우도 별도 결과다.

업무 현실성은 실제 사람의 이름이나 운영 비밀번호를 보유하는 것에서 나오지 않는다. 입력 필드·분기·조회 관계·권한·상태 전이·기대 결과가 현실을 반영하는지가 중요하다. 익명화할 때도 동일 사용자의 연결과 다른 테넌트의 구별 등 분석에 필요한 관계는 유지해야 한다.

협력 운영자가 있다면 정상 업무 요청 예시, 이전/이후 JSON과 하위 구성, 정책 근거, 역할·권한 설명, 정상 완료 증거를 받는 것이 유용하다. n8n은 workflow version을 JSON으로 다운로드할 수 있다. 다만 설정 변경이 workflow history에 남지 않을 수 있으므로 환경·설정은 별도 기록이 필요하다. [n8n history](https://docs.n8n.io/build/manage-workflows/view-change-history.md)

공유 JSON에는 credential 이름·ID나 직접 입력된 인증 헤더 등이 포함될 수 있다. 외부 공유 전 검토가 필요하다. [공식 export 설명](https://docs.n8n.io/build/manage-workflows/export-and-import.md) 공개 데이터 재배포 시에는 출처별 이용 조건·원저자를 기록하고, 재배포 범위를 확인한 원본 또는 직접 만든 대체 데이터를 제공한다.

반복 가능한 실험 환경과 소수의 실제 서비스 시험 환경을 구분할 수 있다. 전자는 비용·초기화·관측을 통제하고, 후자는 모의 서비스와 실제 서비스 의미가 얼마나 다른지 확인한다. 대체한 인증·오류·재시도·비동기 동작을 명시한다. 일부 서비스에 연결됐다는 사실만으로 원래 운영 환경과 동등하다고 판단하지 않는다.

## 5. 입력과 평가 정답의 묶음

논리적으로 한 사례에는 다음이 필요하다. 아래는 파일 형식의 구현 확정안이 아닌 책임 구분이다.

| 구성 | 책임 |
|---|---|
| 이전 구성·이후 구성 | 부모 workflow, 의존성, 환경의 비교 대상을 고정 |
| 업무 설명·정상 완료 조건 | 달성해야 할 정상 결과를 정의 |
| 정책 | 주체·자원·목적지·허용 부수 효과를 정의 |
| 초기 데이터·환경 사실 | 반복 가능한 시작 상태와 사실의 출처·확인 수준을 기록 |
| 실행 조건 | n8n·모델·분석기 버전, 예산, 초기화 조건을 고정 |
| 출처·변환 기록 | 원본 URL/commit/hash, 작성자, 이용 조건, 원본에서 바꾼 부분을 기록 |
| 평가 정답·근거 | 연구 평가자가 관리하며, 최종 라벨과 판정 증거를 분리 보관 |

실제 서비스 사용자에게까지 정답 라벨을 작성하라고 요구하지 않는다. 사용자는 대상과 의도·정책을 제공하고 도구가 지원 범위와 필요한 확인을 설명한다. 정답 묶음은 연구 평가에서 도구의 성능을 측정하기 위한 별도 자산이다. 실행 환경 자료가 부족하면 정적 결과와 미확인 항목까지 제공하고 동적 확인 완료로 표시하지 않는다.

## 6. 오픈소스로 제공할 범위

하나의 공통 분석 코어를 사용한다. 연구에서는 고정된 평가 묶음을 넣고, 다른 사용자는 지원 형식에 맞는 자기 업무 묶음을 넣는다. 사례 이름·노드 ID·정답을 프로그램에 하드코딩하지 않는다.

처음 공개할 가치가 있는 범위는 지원 입력 형식, 제한된 n8n 의미 계약, 정책 템플릿, 출처가 명확한 예제, 정적 분석 결과와 미지원 안내, 검토된 격리 검증용 연결, 증거 보고서와 재현 설명이다. 운영 SaaS의 전자동 연결이나 임의 코드 전체 지원은 별도 확장이다.

연구 평가의 주장은 고정한 범위에 한정한다. 재사용성은 다른 사람이 새로운 지원 사례를 넣을 때 핵심 코드를 바꿔야 하는지, 얼마나 수동 환경 정의가 필요한지, 미지원 이유가 이해되는지로 확인한다. 코드 공개만으로 사용성이 검증되지는 않는다.

114개의 τ 업무를 하나의 n8n workflow에 연결해도 독립 workflow 114개가 생기는 것은 아니다. 업무 요청 수와 workflow 계열 수를 별도로 집계한다. 같은 원본·fork·템플릿 파생물·변경쌍은 같은 평가 분할에 두고, 최종 계열의 정답이 보안 RAG에 들어가지 않게 한다.

## 7. 다음 진행 순서

1. 연구 질문과 함께 공개 업무 후보를 먼저 확인한다. 고객지원·주문조회처럼 설명·데이터·정책을 연결하기 쉬운 한 업무 영역부터 시작할 수 있다.
2. 후보별 실제 node/operation, 하위 의존성, 초기 데이터 요구, 정상 완료 조건을 기록한다. 현재 12개 동작 후보가 적절한지 이 자료로 조정한다.
3. 원본 의미를 유지해 지원 가능한 작은 사례 두 개에서 분석과 정상 업무 확인을 연결한다. 원본을 바꿨다면 변환 범위를 공개한다.
4. 업무·정책·초기 상태를 고정한 비교 규칙과 검증 항목–근거 대응표를 확정한다. 실제 변화와 연구자가 만든 통제 사례를 분리한다.
5. 초기 실행 비용·관측 신뢰성·수동 작업량을 확인한 후 독립 계열과 반복 수를 정한다. 큰 공개 목록의 개수를 평가 규모로 대신하지 않는다.
6. 계열 분할과 버전을 고정하고 비교 실험을 수행한다. 동일한 코어와 입력 형식을 재사용할 수 있도록 공개 후보 산출물을 정리한다.

이 순서는 기존 권고에 ‘실제 후보 자료를 먼저 살펴 지원 범위를 정한다’를 앞당긴 것이다. 지금 확보한 것은 후보 원문·정책·정상 업무 데이터와 일부 변경 이력의 존재 근거다. 실행 가능한 평가 묶음, 보안 정답, 실험 결과까지 확보한 상태는 아니다.

## 8. 팀원이 작성할 사례 묶음의 구체적인 내용

파일명은 제안이며 제품 구현은 아직 없다. 입력은 공통 코어가 해석하는 선언형 자료로 관리한다.

```text
case/
  case.json                 # 비교 유형, 계열 ID, 아래 자료의 참조
  before/manifest.json      # 이전 workflow·하위 구성의 경로와 실제 해시
  after/manifest.json       # 이후 workflow·하위 구성의 경로와 실제 해시
  task.json                 # 요청, 주체, 정상 완료 조건, 허용 부수 효과
  policy.json               # 보호 자원·수신자·테넌트·허용 동작과 출처
  initial-state/            # 독립 실행마다 복원할 합성·비식별 데이터
  environment.json          # 비밀이 아닌 권한 사실, 근거와 확인 수준
  runtime.json              # 엔진·노드·모델·분석기·관측기·KB 버전과 예산
  provenance.json           # 원본·수집일·commit·license·변환 기록
evaluation-private/
  labels.json               # 평가자용 라벨과 독립 정답 근거; 분석기 입력에서 제외
```

같은 사례 폴더에 정답 파일을 놓고 분석기에게 통째로 읽히지 않는다. 분석기는 명시적으로 허용된 입력 참조만 읽는다. 공개할 재현 정답은 최종 평가 동결·실행이 끝난 뒤 출처별 공개 범위를 검토한다. 예시 JSON의 미해결 참조는 실제 파일·해시가 없는 설계 자리표시자다.

### 정책을 작성하는 순서

1. 운영자 요구사항 또는 공개 benchmark의 정책 원문·버전을 정한다. 근거가 없으면 연구자 정의임을 표시한다.
2. 업무 주체, 조회 가능한 자원, 전송 가능한 수신자, 변경 가능한 자원·필드, 허용 부수 기록을 표로 쓴다.
3. 이를 MVP가 지원하는 P1·P2의 구조화 필드로 매핑한다. 지원하지 못하는 규칙은 삭제하지 않고 미지원으로 남긴다.
4. 사례 작성자와 다른 검토자가 정상 완료 조건 및 예외를 검토한다. 분석 결과를 본 뒤 유리하게 정책을 바꾸지 않는다.
5. 정책·업무·관측기 버전을 고정한다. 해석이 달라져 수정하면 새 평가 버전을 만든다.

P1에는 데이터의 출처·민감도뿐 아니라 허용된 주체·테넌트·수신자 관계가 필요하다. 본인 주문 정보를 본인에게 안내하는 정상 동작과 다른 고객의 주문 정보를 전달하는 동작을 같은 ‘외부 전송’으로 묶으면 안 된다. P2는 보호 주문·문서의 변경과 허용된 감사 기록을 구분한다. 주문 취소처럼 상태 변경 자체가 정상 업무인 사례를 읽기 업무로 라벨링하지 않는다. 복잡한 취소·재승인 절차는 P3 지원이 확정되기 전 확장 후보로 남긴다.

### 후보를 평가 사례로 채택하는 기준

| 점검 | 필요한 기록 | 충족하지 못한 경우 |
|---|---|---|
| 출처 | 원본 URL·파일 경로·commit/수집 시점·실제 해시·작성자·이용 조건 | 후보 목록에만 두고 재배포·실행셋 편입 보류 |
| 실제 의미 | node type·typeVersion·operation·표현식·하위 참조·배치·오류 경로 | 미지원 부분과 영향 경로를 표시 |
| 정상 업무 | 입력·초기 상태·독립 완료 확인·허용 부수 효과 | 탐지 성능 평가 사례로 채택하지 않음 |
| 정책과 권한 | 출처가 있는 규칙·환경 사실·관측 수준 | 해당 판정을 미확인 처리 |
| 비교 가능성 | 이전·이후 확보, 변경 축, 같은 기준으로 비교할 수 있는 부분 | 단일 구성 연구 또는 요구사항 변경으로 별도 분류 |
| 독립 정답 | 두 검토자, 불일치 조정, 필요한 실행 증거 | 라벨 미확인 유지; 스캐너 경고로 대체하지 않음 |
| 재현성 | 초기화·관측기 확인·버전 고정·다른 팀원의 실행 | 재현 완료로 표시하지 않음 |

가능한 한 원본을 유지한다. 실행기를 위해 노드를 대체했다면 원본 노드와 대체 동작의 매핑, 보존한 의미, 생략한 인증·실패·배치 동작, 새 해시를 기록한다. 원본 그대로/설정만 대체/동작 변환/연구자 작성이라는 이식 수준을 별도 필드로 둔다. 정적 분석 가능한 공개 원본 수와 실제 실행 가능한 사례 수를 분리한다.

### 시작할 업무 후보와 선택 이유

첫 후보 영역은 고객지원으로 좁힌다. 14550의 주문 조회는 주체–주문 관계와 정상 응답을 정의하기 쉽고, 18499의 문의 분류·내부 이관은 수신자·채널·로그의 허용 범위를 확인하기 좋다. 두 템플릿은 **적격성 조사 후보**이며 그 전체를 즉시 지원한다고 결정한 것이 아니다. 두 독립 원본에서 지원 가능한 업무를 선택하고, 축소·변환했다면 그 사실을 명시한다.

τ 업무·정책·초기 DB는 별도의 변환 사례 구성에 활용할 수 있다. n8n 템플릿의 자체 업무 규칙과 τ의 규칙을 근거 없이 혼합하지 않는다. 둘을 결합할 경우 어떤 부분을 가져왔고 어떤 규칙을 팀이 추가했는지 남긴다. 공식 starter kit의 실제 변경은 실제 이력 집합의 별도 후보로 관리한다.

## 9. 외부 사용과 연구 실행의 연결

| 사용 모드 | 사용자가 제공하는 것 | 가능한 결과 |
|---|---|---|
| 정적 검토 | 전후 구성, 업무·정책, 확보한 환경 사실 | 변경·경로 후보, 지원 범위, 추가로 필요한 근거 |
| 격리 실행 검증 | 위 자료 + 초기 데이터·지원 실행 어댑터·독립 관측 구성 | 관측한 효과와 정상 업무 결과, 실패·미판정 이유 |
| 연구 평가 | 같은 공개 입력 형식 + 평가자가 별도 관리하는 라벨·분할·예산 | 기준선 비교, 불확실성·비용·coverage·한계 |

외부 사용자는 사례별 값과 자료를 바꿀 수 있다. 새 노드 동작이나 새 정책 언어를 지원하려면 어댑터·계약을 추가해야 하며 이는 단순 입력 교체와 다르다. 재사용성 검증에서는 기존 지원 범위의 새 사례를 다른 팀원이 핵심 코드 수정 없이 연결하는지, 설정 시간과 수동 필드 수가 얼마나 필요한지 기록한다.

공개 준비물은 코어 소스·설치 안내·지원/미지원 표·입력 스키마·정책 템플릿·재배포 가능한 예제·결과 형식·평가 재현 자료다. 실제 공개 라이선스 선택, 외부 사례의 배포 가능 범위, 배포 버전은 출시 전에 별도 확정한다. 이번 문서 개정은 제품 출시나 데이터셋 배포 실적이 아니다.

## 10. CVE 자료원 선택과 ScenarioCard 초안 기준

이 기준은 워크플로우 엔진, 실행 환경, advisory 자료원에 종속되지 않는다. ScenarioCard는 한 사례의 주장, 적용 범위, 출처와 근거를 연결하는 구조화 문서다. 기술별 사례는 아래의 적용 예시처럼 이 공통 기준에 맞춰 기록한다.

### CVE ID 발견과 적용성 판정은 분리한다

먼저 CVE·GHSA·OSV 등 식별자를 찾는다. 발견된 ID와 이를 확인한 자료원·확인일을 기록한다. 확인 범위 안에서 ID를 찾지 못했다면 `NOT_IDENTIFIED`와 함께 조회한 자료원·범위·기준일을 남긴다. `NOT_IDENTIFIED`는 적용성 결과가 아니며, CVE가 존재하지 않는다는 증명도 아니다.

각 advisory와 평가 대상 runtime 환경의 조합에 대해 적용성을 별도로 판정한다.

| 적용성 상태 | 의미 |
|---|---|
| `APPLICABLE` | advisory의 package/product identity, 영향 버전 범위, 설정·환경 조건이 모두 평가 대상과 일치한다. |
| `NOT_APPLICABLE` | 평가 대상의 정확한 버전 또는 조건이 advisory의 영향 범위 밖임을 근거로 확인했다. |
| `UNKNOWN` | package/product identity, 실제 포함 버전, 빌드·배포 연결 또는 advisory 조건 중 하나 이상을 확인하지 못했다. |

적용성은 advisory와 환경별로 기록한다. ID를 발견했어도 `UNKNOWN`일 수 있고, 조회 범위에 ID가 없더라도 환경이 안전하다는 결론을 내리지 않는다. 전역 NVD/OSV/GHSA feed 수집은 사례별 조사나 초안 작성의 선행 조건이 아니다.

### Runtime identity와 자료원

평가 대상 runtime에 실제 포함된 정확한 ecosystem/package 이름과 버전, 또는 정확한 product 이름과 버전을 기록한다. package나 product의 identity를 모르면 적용성을 확정하지 않는다. OSV에서 source commit으로 조회하는 경우에도 해당 commit이 advisory의 package/repository에 속한다는 사실과 그 commit의 소스가 평가 중인 built/deployed runtime에 포함됐다는 연결 근거가 모두 필요하다. Workflow commit, 변경 가능한 image tag, node `typeVersion` 하나만으로는 runtime identity나 적용성을 입증할 수 없다.

자료원은 주장 종류와 identity에 맞춰 선택한다.

1. **Workflow·구성 동작과 수정 이력:** 정확한 upstream 저장소, commit, 파일 hash를 기록한다. 작성자 설명, 발견·수정 이력, 정적 분석, 제한 replay는 각기 다른 근거로 구분하며 workflow 권한 결함을 package CVE로 바꾸지 않는다.
2. **Dependency 취약점:** 실제 runtime에서 확인한 ecosystem, package 이름, 버전 또는 commit과 OSV의 affected range를 대조한다. advisory의 package가 해당 runtime에 포함됐는지 확인한다.
3. **제품·플랫폼 취약점:** vendor/product/version과 영향을 받는 설정·조건을 확인한 뒤 NVD CVE/CPE와 upstream advisory/release를 대조한다. CPE 일치만으로 환경 적용성을 확정하지 않는다.
4. **Repository advisory:** 대상 저장소 또는 package identity가 일치하는지 확인하고 GitHub Advisory의 affected/patched range와 사례의 조건을 대조한다. 필요하면 OSV/NVD와 연결하되 같은 advisory를 별도 취약점으로 세지 않는다.

### Claim 근거 참조

각 `claims[]` 주장은 근거를 직접 가리키는 `evidence_refs`를 가져야 한다. 참조는 (a) immutable artifact의 경로·SHA-256·selector를 직접 포함하거나, (b) `evidence_key`가 그 카드 자신의 evidence map 안에서만 하나의 immutable artifact 경로와 SHA-256으로 해석되고 selector가 그 artifact의 내용을 가리켜야 한다. 다른 카드나 전역 map의 키로 해석하면 안 된다. Selector는 결과 내부의 중첩 record를 가리킬 수 있으며, 그 record를 포함하는 상위 실행 record의 version·source hash·status와 coverage도 함께 검증할 수 있다. 파일 전체의 경로·hash만으로는 어느 내용이 주장을 지지하는지 알 수 없다.

소스 코드에 관한 주장은 정확한 code location(JSON Pointer 또는 줄 위치)을 포함하고, 가능한 경우 그 위치의 code hash도 포함한다. 고정된 source bytes를 확인할 수 없다면 selector를 추정하지 말고 그 제한을 기록한다. 예를 들어, zero-finding 주장은 존재하지 않는 finding 항목을 가리킬 수 없다. 해당 주장은 대상이 분석 coverage에 포함됐는지 확인하고, 분석이 성공했으며 해당 run의 findings가 빈 배열인 상위 summary record를 가리켜야 한다. 미래 #82 초안 검증은 알 수 없는 `evidence_key`, artifact hash 불일치, 근거가 되지 않는 selector를 거부해야 한다.

ScenarioCard 0.4.0의 generic `extensions`는 이런 참조 해석·의미 검증을 강제하지 않는다. claim-evidence의 semantic validation은 #82 범위이며 이 문서 기준만으로 구현됐다고 간주하지 않는다.

### 기술 중립적인 evidence layer

사례에 관련된 layer만 선택한다. 각 layer에는 status, 범위와 설정, 도구·버전, artifact reference, coverage와 제한을 기록한다. 실행하지 않은 layer는 `NOT_RUN`으로 남긴다. 한 layer의 결과를 상위 layer나 실제 환경의 결과로 일반화하지 않는다.

| Layer | 기록할 관측 범위 |
|---|---|
| Source inspection | 고정된 source/configuration, 파일 hash, 주장에 필요한 code location |
| Static analysis | 입력 범위, 분석기·규칙·설정 버전, 처리한 항목, 누락·미지원 항목과 결과 |
| Bounded/component replay | 실행한 component, fixture·환경 설정, case별 결과, timeout·coverage 등 제한 |
| Integrated workflow/system execution | 고정된 workflow/system 구성과 의존성, 실행 조건, 실제 통합 경로의 결과와 누락된 경로 |
| Backing-service effects | 실제 DB·queue·file store 등 서비스 identity와 권한, 시작 상태, 독립 관측한 효과와 초기화 방법 |

Layer는 사례에 따라 선택 사항이다. 합성 수신부에서 관찰한 변경은 bounded/component replay의 증거이며 실제 backing-service effect로 기록하지 않는다. 분석 결과, finding 부재, 테스트 통과는 각각의 관측 범위 안에서만 설명한다.

### 결정적 추출과 템플릿 초안

초안 생성은 고정된 입력에서 다음 사실 필드를 결정적으로 추출한다.

| 입력 | 추출 필드 |
|---|---|
| Source manifest | URL, path, revision, 원본 bytes 기준 SHA-256, size, license·consent·references-only 등 reuse terms |
| Advisory record | 확인된 ID, ecosystem, package/product 이름과 version, advisory의 affected range·patched range, 출처에 명시된 조건 |
| Evidence artifact | artifact path와 SHA-256, 해당 주장을 뒷받침하는 selector, 도구·버전과 rule·버전 |

제목·요약·적용성·영향·제한은 이렇게 확인된 필드와 근거가 뒷받침하는 `claims[]`에서 결정적 템플릿으로 만든다. 제목은 확인된 대상과 claim을 요약하고, 요약은 지원되는 claim만 모으며, 적용성은 별도 적용성 판정값을 사용한다. 영향은 관측된 효과만 설명하고, 제한은 `NOT_RUN`, 미지원 coverage와 미확인 사실에서 채운다. 근거가 없는 값은 `UNKNOWN`으로 남긴다. CVE, 영향, 권한을 새로 추론하거나 지어내지 않는다. 초안 생성 v1은 외부 LLM을 사용하지 않는다.

### 초안 검토와 활성 카드 승격

초안은 source revision/hash와 이용 조건, runtime identity와 advisory 조건, claim별 근거, 필요한 권한, 관측 layer, coverage, 미확인 사항을 보존한다. 사람 검토자는 CVE 발견 범위, 적용성, 보안 의미와 각 주장이 evidence boundary를 넘지 않는지 확인한다. 활성 `cards/`로 승격하기 전에 ScenarioCard 0.4.0 구조 검증과 별도의 semantic evidence-reference 검증을 모두 통과하고, 검토자가 명시적으로 승인을 기록해야 한다. `TEAM_AUTHORED`는 작성 주체를 설명할 뿐 검토 승인이나 활성 상태를 뜻하지 않는다.

### 구현 상태 메모: #80, #82, #78

- **#82:** 위 기준을 draft 생성·검증에 적용하는 구현 범위다. 현재 `load_cards(directory)`는 0.4.0 구조, 중복 `(card_id, version)`, 제공된 `source_ref`를 검증하지만 `extensions.flowdelta.case_evidence` 안의 claim reference를 해석하거나 검토 상태를 검사하지 않는다. #82는 같은 카드의 evidence map 안에서 키를 해석하고 hash·selector의 실제 지원 내용을 확인해 실패 시 draft 승격을 막아야 한다. Draft는 활성 카드 디렉터리 바깥에 두며, 첫 버전은 외부 LLM 없이 manifest와 관측에서 사실 필드를 채우고 출처가 뒷받침하는 결정적 초안을 만든다.
- **#80:** 사례별 수집 경로가 필요해질 때 제한된 자료원 adapter와 원본 hash·재개 처리를 다룬다. 전체 feed mirror, 무관 CVE, embedding/index는 이 기준이나 사례별 수집의 선행 조건이 아니다.
- **#78:** B plan과 C 정적 검사 연결은 별도 통합 범위다. 아래 사례 카드의 template ID·상태를 임의 변경하거나 독립 실험 결과를 B 생성 C-plan 실행 결과로 표현하지 않는다.

### 적용 예시: n8n-claw Memory Delete와 n8n starter kit

2026-10-29에 확인한 후보로 공통 규칙을 적용한 예다. starter-kit 후보를 두 번째 확정 취약 사례로 간주하지 않는다.

| 사례 | CVE ID 발견 | Advisory·runtime 적용성 | 확인 근거와 경계 |
|---|---|---|---|
| n8n-claw Memory Delete — feature-add `63a7f2e`, first-fix `4d1b1b7 → eb6d7bc` | 고정 workflow revisions와 제한 replay 자료에서 `NOT_IDENTIFIED` (2026-10-29). 검토한 [upstream revisions](https://github.com/serendipity-sec/platform/blob/main/experiments/n8n-claw-memory/sources.json)와 [`observations.json`](https://github.com/serendipity-sec/platform/blob/main/experiments/n8n-claw-memory/evidence/observations.json) (SHA-256 `88039348d8963431af9a229a17c46812ddb920534c70d1d7dcc80b0bb73d6ae7`)을 가리킨다. 이는 전체 advisory feed 검색 결과가 아니다. | `UNKNOWN`. workflow commit과 파일 hash는 있지만 평가 runtime에 실제 포함된 package/product와 버전, source commit에서 built/deployed runtime으로의 연결이 없다. Workflow 권한 검사 누락을 CVE로 바꾸지 않는다. | 카드의 주장은 특정 workflow와 제한된 JavaScript replay에 한정한다. caller 인증, 실제 배포, DB 권한, 전체 n8n+LLM 동작은 확인하지 않았다. |
| n8n self-hosted AI starter kit Demo workflow, commit [`9ccbaf42`](https://github.com/n8n-io/self-hosted-ai-starter-kit/commit/9ccbaf42e007369453acaec60b9808cf8e6cdb44), workflow file SHA-256 `e4e3112000b61db5fed114b026b000912b90ff832f163c3e7cc0d839bb1b7bad` | `CVE-2025-56265` / `GHSA-v2x8-97xq-8xrr` ID가 [OSV](https://osv.dev/vulnerability/GHSA-v2x8-97xq-8xrr)와 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-56265)에 있다. ID 발견은 이 후보의 적용성을 증명하지 않는다. | `UNKNOWN`. Advisory는 `@n8n/n8n-nodes-langchain <1.107.0`에 대해 게시되고 `1.107.0`에서 수정됐다. 이 후보의 `Chat Trigger` node가 같은 package 계열이라는 것만으로는 runtime version을 확인할 수 없다. | [고정 workflow](https://github.com/n8n-io/self-hosted-ai-starter-kit/blob/9ccbaf42e007369453acaec60b9808cf8e6cdb44/n8n/demo-data/workflows/srOnR8PAY3u4RSwb.json)는 Basic LLM Chain `typeVersion`이 `1.3 → 1.7`로 바뀐 이력이다. 같은 commit의 [`docker-compose.yml`](https://github.com/n8n-io/self-hosted-ai-starter-kit/blob/9ccbaf42e007369453acaec60b9808cf8e6cdb44/docker-compose.yml)는 mutable `n8nio/n8n:latest`를 사용한다. 이 commit, tag, `typeVersion`은 package version이나 배포 image digest를 증명하지 않는다. [upstream fix PR](https://github.com/n8n-io/n8n/pull/18148)와 [1.107.0 release](https://github.com/n8n-io/n8n/releases/tag/n8n%401.107.0)도 대조했다. |

두 n8n-claw 카드 `memory-delete-owner-check-gap.json`과 `memory-delete-owner-check-first-fix.json`은 기존 `cve: NOT_IDENTIFIED`를 유지하고 별도 `cve_applicability.status=UNKNOWN`을 기록한다. [PR #76](https://github.com/serendipity-sec/platform/pull/76)에서 검토·승인된 활성 카드다. 카드의 source evidence는 commit/path/file hash를 고정하지만 upstream source bytes가 이 checkout에 없어 코드 pointer를 독립 확인할 수 없다. 확인할 수 없는 pointer는 추가하지 않았고 이 한계를 남긴다.

두 카드는 [Semgrep tool-fit report](https://github.com/serendipity-sec/platform/blob/86a57e4f52f6c482c5b2a627d170e1837832ce79/experiments/n8n-claw-c/evidence/semgrep-summary-0.4.0.json) (SHA-256 `afa1ea124fc82d6742f33c0408fd4728e6be49aa01765cd3f21605c42c89fd60`)를 별도 static-analysis evidence로 둔다. Semgrep `1.181.0`, rule `flowdelta.n8n.agent-tool-write-without-ownership-check@0.4.0`의 `feature` 결과는 Memory Delete와 Memory Update finding을 기록했고, `first-fix` 결과는 해당 rule의 finding이 없다. `toolWorkflow`와 Telegram 등 일부 node type은 `TARGET_TYPE_NOT_SUPPORTED`이며 report의 `security_outcome`은 null이다. Finding 부재는 안전성 증명이 아니고, 이 실행은 B가 생성한 C plan의 결과가 아니다.

카드의 evidence layer 대응은 source inspection = pinned workflow file 주장, static analysis = 위 Semgrep report, bounded/component replay = 합성 수신부에 대한 선택 JavaScript 실행으로 각각 제한한다. 전체 workflow·LLM 실행과 실제 backing-service effect인 database 실행은 `NOT_RUN`이다. C 측 catalog에는 `static-agent-tool-ownership@0.1.0`이 따로 등록됐지만 카드는 기존 `n8n-claw-memory-static-scan@0.1.0-proposed`와 `template_status=PROPOSED_NOT_REGISTERED`를 유지한다. Template 연결과 B→C 실행 경계는 #78에서 다룬다.
