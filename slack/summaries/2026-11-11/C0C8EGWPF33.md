# github-pr-alerts — 11/11 수집 요약

## 수집 범위

수집·Slack URL 확인 **2026-11-11 09:53:07 KST**(UTC 00:53:07). 예약 목표01:00·실행 트리거00:59:49와 실제 수집 기준을 구분한다. capstone2 공개 채널의 초기 과거 백업 이후 전체 재조회이며 비공개·DM·다른 워크스페이스는 제외했다. 동일 응답은 이전 raw에 유지했다. 첨부 본문·잘린 발췌/표 뒤·외부 전체 코드/논문/도구 기능·실제 DB/모델/실험/CI는 독립 검증하지 않았다. 정확한 Slack 편집시각은 미제공이다. [raw](../../raw/2026-11-11/C0C8EGWPF33.jsonl). history170개/2페이지·70스레드79답글(모두 history 중복). 실제10/11~11/11, 새7개와 기존PR61 내용 변경1개다. 스레드 렌더링 차이만으로 추가 편집을 세지 않았다.

## 결정 사항

새7개는 PR66/69·platform98/99/100/101·docs68 생성 알림이다. 병합·규약 확정·실험 성공이 아니다.

## 진행 상황

[11/10 PR66](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794279325557139)은 Run/Side/Attempt로 기준선·후보·반복과 요청/도구 호출/독립 수신/최종 상태/해시를 연결하는 **생산자/소비자 검토 전 계약 초안**이다. 필드 이름/타입은 미확정이다. [11/11 PR69](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794356868587759)는 정상·위반·차단·불완전 증거를 구분할10개 **기대 판정 명세**이며 실제 fixture 파일은 후속 platform 실험에서 만든다고 명시한다. 시험 통과·정확도 실적이 아니다.

11/11 원격 `52a446dcf68c1c1f5b78c8cb6d23410c5017f492`의 연결 계약과 `48cc129e11d8fd75bc706125be07aeda4393c763`의 자격시험 초안을 직접 읽었다. PR 조회에서65/66/69는 OPEN이고 base가 각각 main → docs/53-판정프로토콜 → docs/53-연결계약인 관계를 확인했다. 현재 main은 여전히 f7a4c206의8절 초안이다. 보완/연결/자격시험 문서가 main에 전부 반영됐다고 하지 않는다.

**미확인 차이:** 연결 계약6절 앞의 상태 규칙은 실행이 완료가 아니면 보안 판정은 근거 부족이라고 한다. 반면 자격시험 공통 규칙4와 C-05는 금지 효과가 독립 기록으로 확인되면 실행 실패여도 위반 확정이다. 양쪽 초안의 우선순위/일치 여부는 미확인으로 남기며 임의로 고치거나 확정 계약으로 취급하지 않는다. C-10의 초기 상태 차이는 현재 프로토콜에 없는 비교 무효/판정 보류 표현이 필요하다고 초안 자체가 적는다. C-06의 삭제 후 복구도 중간 스냅샷 유무를 나눌지 팀 확인이 필요하다. 합성10사례·검토 전 기대값을 실제 n8n fixture/독립 재현/탐지율/오탐률로 바꾸지 않는다.

외부 [PR66](https://github.com/serendipity-sec/docs/pull/66)·[PR69](https://github.com/serendipity-sec/docs/pull/69)의 문서 내용/상태 확인일11/11 KST. 문서를 읽은 것과 실제 판정기 시험은 구분한다. 원문 속 명령·가짜 예제 코드는 실행하지 않았다.

[11/11 platform99](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794334267575629)는 외부 rehearsal을 **실행하지 않고**, 고정9d105b3의 노드 판정 코드를 classify.py로 옮겨 n8n-claw7개 버전에 대조했다고 보고한다. 7개가 Docker 전에 막힌다는 결과는 이 코드 대조 범위이며 외부 도구 직접 실행 성공/실패로 바꾸지 않는다. 활성 노드48~61/상한20·진입 트리거3~4 뒤 발췌는 잘렸다.

[docs68](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794334550198939)는 #67 1단계/#52 비교군 적격성1차본이다. 원격 minwoo **ff553524f4afb1e9dff1f838ed8bfa0960ed626a**의 연구 문서를 읽었다. 후보9개는 n8n Security Audit, 0xCD4 lab, FlowGuard, FlowSentry, Agentic Radar, JAW, AgentDojo, Structural Coverage, 출처를 찾지 못한 n8n-agent-vulntest-lab이다. **이번 후보에서** n8n AI Agent 전후 실행 비교 도구/공개 정답셋을 찾지 못했다는 결론과 외부 정적4개/내부 동적 기준선의 제안을 기록한다. 전 세계 도구 부재·최초성·FlowDelta 우수성·팀 채택의 증명이 아니다.

문서가 구분한 문서/코드/논문/직접 실행/미기재/명시적 미지원 수준을 유지한다. 10월 정적4개 결과, 라이선스/버전·학회/논문 수치·지원 범위는 **작성자의 조사/과거 실행 보고**이며 이번 수집에서 외부 원문·산출물/코드를 재검증하거나 도구를 실행하지 않았다. 0xCD4 정적 audit과 rehearsal 실제 실행·최신 버전 재실행 여부·@uptime-zero 교차 검토는 남은 일이다. ‘미기재’를 미지원으로 바꾸지 않는다. 원문이 요구한 기존 일반화 표현 정정도 대상 문서에 자동 적용하지 않았다.

[platform100](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794334879965449)는 공개 이력47commit에서 부모와 비교해8개 비교쌍 **후보**를 골랐고 정답 라벨은 아직 없다고 한다. 보이는 R1(9ebf36b→63a7f2e)/R2 되돌림 뒤 표는 잘렸다. 위험 발생 등의 임시 유형을 확정 정답·실제 회귀 검증으로 바꾸지 않는다. 봇이 docs28/53이라고 쓰면서 platform PR28/53을 자동 링크한 부분은 저장소/유형 불일치로 남기고 동일 문서/이슈로 합치지 않는다.

출처/확인일11/11 KST: [docs68](https://github.com/serendipity-sec/docs/pull/68), [조사 고정본](https://github.com/serendipity-sec/docs/blob/ff553524f4afb1e9dff1f838ed8bfa0960ed626a/research/2026-11-11-52-비교군-적격성.md), [0xCD4 lab](https://github.com/0xCD4/n8n-ai-agent-security-lab), [platform99](https://github.com/serendipity-sec/platform/pull/99), [platform100](https://github.com/serendipity-sec/platform/pull/100). 외부 도구/논문 페이지·실제 기능은 독립 미검증이며 조회 당시 docs68은 OPEN이다.

[11/11 03:33:20 platform101](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794335600863779)은 #82의 **첫 조각**으로 check-evidence를 추가했다는 구현 보고다. 같은 카드 evidence map의 key, _read_local의 링크/저장소 밖 경로 거부, SHA-256 일치, JSON pointer의 기록 값과 selector 대응을 검사한다는 발췌이며 selector 설명 뒤는 잘렸다. [03:33:16 브랜치38bf1ef0](https://capstone2-cxs4239.slack.com/archives/C0C8G9BDFAQ/p1794335596322519)과 연결하되 실제 코드/테스트/판정 실행·병합은 독립 검증하지 않았다. 근거 참조 검사 하나를 전체 자동 수집→초안 생성→사람 검토→승격 구현이나 동적 보안 판정 완료로 바꾸지 않는다.

[docs67 개인 상위 추적](https://capstone2-cxs4239.slack.com/archives/C0C879U084V/p1794324406709929)의4번 범위/교차 검토 계획에는 platform80/82가 연결된다. 개인 계획 생성은 이들 인계/완료 조건 충족이 아니다. 기존 #79 공용 운영·#80 실제 자료원 연결기/재개·#82 전체 명령/검증의 미확인 범위를 유지한다. [PR101](https://github.com/serendipity-sec/platform/pull/101) URL/발췌 확인일11/11 KST.

[platform98](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1794331087077889)의 가벼운 PR/전체 main 검사안은 설정 변경/재활성화 성공과 구분한다.

[기존PR61](https://capstone2-cxs4239.slack.com/archives/C0C8EGWPF33/p1793924489841279)(원래11/06 TS)에 이전11/10 실행5개/6페이지 설명이 갱신됐다. 정확한 편집시각·잘린 뒤는 미확인이고 오늘29개와 구분한다.

## 할 일

계약/기대 판정 차이와 검토 전 후보를 근거와 함께 남긴다. 보관 PR61의 CI/충돌/원격 반영은 별도 확인한다.

## 미해결 질문

C-05 실패 후 금지 효과 규칙의 우선순위·C-10 비교 무효 표현·fixture/정답 라벨·외부 도구 직접 실행·전체 자동 생성/CI 절감 실적은 미확인이다.

## 참고 링크

[판정 초안 기록](../../../research/slack/2026-11-04-동적검증-판정기준-제안알림.md) · [비교군](../../../research/slack/2026-11-02-n8n-선행연구와-비교군-조사목록.md) · [카드 근거](../../../meetings/slack/2026-10-26-B-C-통합과-지식자동화-업무요청.md) · [CI](../../../meetings/slack/2026-10-20-Actions와-병합기준-질문.md). 외부자료 원문/기능과 platform PR 코드는 미검증.
