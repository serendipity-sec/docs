# 동적 검증 판정 기준 정리 (FlowDelta 적용안)

Nov 4, 2026 · @준서

## 요약

공신력 있는 연구들의 동적 판정은 한 줄로 요약됩니다. 실행 결과를 \*\*미리 정한 판정 기준(오라클)\*\*에 대어 보고, **관찰된 증거**가 있을 때만 확정합니다.

- **기준은 실행 전에 고정한다.** 결과를 보고 기준을 바꾸면 평가가 무너진다 (NIST SATE, Klees et al.).
- **패턴이 아니라 일어난 일로 판정한다.** 미끼 자격증명이 실제로 외부로 나갔는지, 환경 상태가 실제로 바뀌었는지를 본다 (USENIX Security '26 악성 스킬 연구, AgentDojo).
- **판정은 두 단계다.** 지표에 걸리면 후보, 증거(패킷 캡처·syscall 로그)를 사람이 보고 확정한다.
- **결과는 세 갈래로 둔다.** 위험 확정 / 위험 없음 / 근거 부족(실행 안 됨·시간 초과). 근거 부족을 "안전"으로 세지 않는다 (팀 문서 05-평가설계 4.2절).
- **한계를 함께 적는다.** 동적 분석은 실행 중에 드러난 것만 본다. 지연 실행, 샌드박스 감지, 조건부 실행은 놓친다.

이 문서는 근거 정리와 적용안이다. 아래 기준으로 실험한 결과는 아직 없다.

## 판정 기준(오라클)의 네 가지 유형

오라클은 "이 결과가 나오면 위험"이라고 판단하는 기준입니다. 공신력 있는 연구에서는 아래 네 가지를 씁니다. 하나만 쓰기보다 섞어 쓰는 경우가 많습니다.

| 유형 | 무엇으로 판정하나 | 쉬운 예시 | 근거 |
| --- | --- | --- | --- |
| 행동 지표 | 실행 중 파일 접근·네트워크 연결·실행 명령이 미리 정한 위험 행동과 맞는지 | 설치만 했는데 모르는 IP로 연결함 | [OpenSSF Package Analysis](https://pkg.go.dev/github.com/ossf/package-analysis), [Duan et al. NDSS 2021](https://ndss-symposium.org/ndss-paper/towards-measuring-supply-chain-attacks-on-package-managers-for-interpreted-languages) |
| 미끼(허니토큰) | 정상 작업에서는 쓸 일이 없는 가짜 자격증명을 읽거나 보냈는지 | 가짜 `AWS_SECRET_KEY` 값이 외부 요청에 들어감 | [Liu et al., USENIX Security '26](https://arxiv.org/abs/2602.06547v1), SkillDetonate(팀 조사문서 \[P5\]) |
| 상태 확인 | 실행이 끝난 뒤 환경 상태를 검사하는 결정적 함수 | 실행 후 외부 수신함에 사용자 메일이 도착해 있음 | [AgentDojo, NeurIPS 2024](https://arxiv.org/html/2406.13352v3) |
| 차등 비교 | 이전 버전에는 없던 행동이 새 버전에서 생겼는지 | v1은 안 부르던 도메인을 v2가 부름 | [OpenSSF Package Analysis](https://securityaffairs.com/130831/security/package-analysis-project.html) |

- **행동 지표.** OpenSSF는 패키지를 샌드박스(gVisor)에서 설치·import·실행하며 세 가지를 봅니다. 어떤 파일에 접근하는지, 어디로 연결하는지, 어떤 명령을 실행하는지입니다.
- **미끼.** 악성 스킬 연구는 패턴만으로는 확정하지 않았습니다. 미끼 자격증명이 실제로 전송된 것처럼 행동이 관찰된 157개만 악성으로 확정했습니다.
- **상태 확인.** AgentDojo는 LLM에게 판정을 맡기지 않고 환경 상태로 판정합니다. LLM 판정기 자체가 프롬프트 인젝션에 속을 수 있기 때문입니다.
- **차등 비교.** OpenSSF는 패키지 행동이 시간에 따라 어떻게 바뀌는지 추적합니다. 예전엔 안전하던 소프트웨어가 수상하게 바뀌는 시점을 잡기 위해서입니다. FlowDelta의 전후 비교와 가장 가까운 공개 사례입니다.

## 관찰 지표 목록

아래 지표는 참고 연구들이 실제로 쓴 위험 행동을 모은 것입니다. MITRE ATT&CK은 공격 기법에 번호를 붙여 둔 공개 분류표입니다. 보고서에 기법 ID를 붙이면 "우리가 임의로 정한 기준이 아니다"라는 근거가 됩니다.

| 관찰 지표 | 관찰 방법 | 후보 조건 | 확정 조건 | ATT&CK |
| --- | --- | --- | --- | --- |
| 자격증명 수집 | auditd·inotify로 `~/.ssh`, `~/.aws`, `.env` 감시 + 미끼 키 | 미끼 파일·환경변수 읽기 | 읽은 미끼 값이 외부로 전송됨 | [T1552](https://attack.mitre.org/techniques/T1552/) |
| 외부 전송(유출) | tcpdump 또는 프록시 로그 | 허용 목록 밖 목적지로 송신 | 송신 내용에 미끼·사용자 데이터 포함 | [T1041](https://attack.mitre.org/techniques/T1041/), [T1567](https://attack.mitre.org/techniques/T1567/) |
| 문서에 없는 도메인 접속 | DNS·연결 로그 | 설명·설정에 없는 호스트 | 증거 검토에서 정당한 용도가 없음 | [T1071](https://attack.mitre.org/techniques/T1071/) |
| 외부 코드 내려받아 실행 | 네트워크 + execve 추적(strace) | 실행 중 파일 다운로드 | 내려받은 파일이 실행됨 | [T1105](https://attack.mitre.org/techniques/T1105/), [T1059](https://attack.mitre.org/techniques/T1059/) |
| 예상 밖 명령 실행 | execve 추적 | 셸·인터프리터 실행 | 목적과 무관한 명령(리버스 셸 등) | [T1059](https://attack.mitre.org/techniques/T1059/) |
| 지속성 확보 | 파일 감사 | cron·시작 스크립트 쓰기 | 등록된 항목이 외부 연결·재실행을 수행 | [T1053](https://attack.mitre.org/techniques/T1053/) |
| 권한 상승 | syscall·감사 로그 | sudo·setuid 시도 | 실제로 권한이 올라감 | [T1548](https://attack.mitre.org/techniques/T1548/) |
| 트래픽 가로채기 | 프록시 설정·연결 로그 | 프록시 주소 설정 | 요청이 외부 프록시를 거쳐 나감 | [T1090](https://attack.mitre.org/techniques/T1090/) |

관찰 방법(auditd, tcpdump, strace, 미끼 키)은 [Liu et al. USENIX Security '26](https://arxiv.org/abs/2602.06547v1)의 구성을 따랐습니다. "후보 조건 / 확정 조건" 구분은 이 연구가 패턴만으로는 확정하지 않은 원칙을 지표별로 풀어 쓴 것입니다. ATT&CK 매핑은 이 문서에서 붙인 것이므로 팀 검토가 필요합니다.

## 판정 단계와 채점

판정은 자동 지표로 후보를 고르고, 증거를 사람이 보고 확정하는 순서로 진행합니다.

1. **기준 고정 (실행 전).** 지표, 허용 목록, 시간 제한, 입력을 문서로 고정한다. 결과를 본 뒤 바꾸지 않는다.
2. **실행과 수집.** 동일한 환경에서 여러 번(참고 연구는 입력을 바꿔 3\~5회) 실행하고 네트워크·syscall·파일 이벤트를 모두 저장한다.
3. **자동 매칭 → 후보.** 관찰 지표의 "후보 조건"에 걸리면 후보로 표시한다.
4. **증거 검토 → 확정.** 두 사람이 독립적으로 판단한다. 의견이 갈리면 패킷 캡처 같은 추가 증거를 본다. 참고 연구는 1\~3점 척도에서 "개연성 있음" 이상일 때만 확정했다.
5. **세 갈래 판정.** 위험 확정 / 위험 없음 / 근거 부족. 실행 실패·시간 초과·경로 미도달은 근거 부족이다 (팀 문서 `docs/research/2026-09-20-프로젝트-사전검증/05-보안효과와-사용자판단-평가설계.md` 4.2절).
6. **채점.** 도구 결과를 보지 않고 만든 정답 라벨과 비교해 TP·FP·TN·FN을 센다.

| 지표 | 계산 | 뜻 |
| --- | --- | --- |
| 탐지율(TPR, 재현율) | TP / (TP + FN) | 진짜 위험 중 몇 %를 잡았나 |
| 오탐률(FPR) | FP / (FP + TN) | 정상 중 몇 %를 잘못 걸었나 |
| 정밀도 | TP / (TP + FP) | 걸린 것 중 몇 %가 진짜인가 |
| Youden 지수 | TPR − FPR | OWASP Benchmark 점수 방식. 무작위 찍기 = 0, 완벽 = 1 |
| 근거 부족 비율 | 근거 부족 / 전체 | 정상으로 세지 않고 따로 공개 |

근거: 채점 방식은 [OWASP Benchmark](https://owasp.org/www-project-benchmark/), 독립 라벨링과 2인 검토는 [Liu et al. 2601.10338](https://arxiv.org/abs/2601.10338)과 [2602.06547](https://arxiv.org/abs/2602.06547v1), 기준 사전 고정과 반복 실행은 [Klees et al. CCS 2018](https://arxiv.org/pdf/1808.09700)에서 가져왔습니다.

## 환경 구성과 기록 요건, 알려진 한계

결과를 다른 사람이 재현하려면 환경을 빠짐없이 기록해야 합니다. 실제 취약점 368건을 재현해 본 USENIX Security 2018 연구에서는 보고서 정보만으로 54.9%만 재현됐습니다 ([Mu et al.](https://usenix.org/node/217570)).

| 항목 | 참고 연구 설정 (2602.06547) | 우리가 기록할 것 |
| --- | --- | --- |
| 격리 | Docker, Ubuntu 22.04, Python 3.10, Node.js 18 | 이미지 태그·digest, 대상 버전(예: n8n 버전) |
| 자원·시간 | 메모리 2GB, 60초 제한 | 제한값, 시간 초과 여부 |
| 네트워크 | bridge 네트워크 + tcpdump | 차단/허용 정책, 허용 목록 |
| 감시 | strace, auditd, inotify | 도구·버전, 원본 로그 보관 위치 |
| 미끼 | `AWS_*`, `API_*`, `SECRET_*`, `TOKEN_*` 형태의 가짜 키 | 미끼 값과 위치 |
| 입력 | 문서화된 진입점 + 합성 입력, 3\~5회 | 입력 목록, 반복 횟수 |

**알려진 한계 (보고서에 함께 적을 것)**

- **시간·조건 트리거.** 60초 안에 안 드러나는 지연·날짜·환경 조건 실행은 놓친다. 참고 연구는 확정 157개를 하한선이라고 밝혔다.
- **샌드박스 감지.** 컨테이너임을 알아채면 행동을 숨길 수 있다.
- **실행 경로 미도달.** 합성 입력이 위험 코드까지 도달하지 못할 수 있다. NDSS 2021 MalOSS도 동적 분석의 낮은 커버리지를 한계로 적었다 ([Duan et al.](https://arxiv.org/pdf/2002.01139)).
- **환경 차이.** Docker 안 행동과 실제 런타임(에이전트·n8n 서버) 행동은 다를 수 있다.
- **네트워크 정책 딜레마.** 완전 차단하면 연결 시도만 보이고, 열면 위험하다 (팀 조사문서 `claude/skill-scanners-and-methods.md` 1절 ⑧).
- **정답의 순환.** 같은 사람이 패턴·라벨·검토를 모두 맡으면 편향이 생긴다. 라벨은 도구 결과를 보지 않고 만든다 ([Arp et al. USENIX Security 2022](https://usenix.org/conference/usenixsecurity22/presentation/arp)의 라벨 오류·표본 편향 경고).

## FlowDelta 적용안 (팀 확인 필요)

제안의 핵심은 이전 버전과 새 버전을 같은 환경·같은 입력으로 돌리고, "차등 비교 + 미끼 + 관찰 지표"로 새로 생긴 위험만 판정하는 것입니다. 아래는 이 문서의 제안이며 팀 결정이 아닙니다.

**팀 문서에 이미 정해진 것** (`docs/meetings/2026-10-17-01-회의록.md`)

- 환경은 고정하고, 변동 입력은 업데이트된 n8n 워크플로로 둔다 (3절).
- C 단계는 기존 오픈소스 n8n 검사 도구를 써도 되며, 해당 취약점을 잡을 수 있는지 먼저 확인한다 (결정사항).
- 정적 검사가 우선이고, 동적 샌드박스는 여유가 있을 때 진행한다 (결정사항).
- 취약점은 정책과 결합해 터지므로 정책 설정이 필요하다는 의견이 있었으나 범위는 미정이다 (3절).

**제안: 동적 판정 절차**

1. **기준선 실행.** 이전 버전 워크플로를 고정 환경에서 돌려 접속 도메인·읽은 파일·실행 명령 목록을 기준선으로 저장한다.
2. **새 버전 실행.** 같은 환경·같은 입력·같은 미끼로 새 버전을 돌린다.
3. **차등 목록 만들기.** 새 버전에만 나타난 행동을 뽑는다.
4. **지표 대조.** 차등 목록을 "관찰 지표 목록"의 후보·확정 조건에 대어 본다.
5. **세 갈래 판정.** 새 위험 확정 / 새 위험 없음 / 근거 부족.

**팀에서 정해야 할 것**

- [ ] n8n에서 무엇을 관찰 단위로 볼지 (노드별 HTTP 목적지, 컨테이너 syscall 등)
- [ ] 네트워크를 차단할지, 허용 목록 프록시로 열지
- [ ] 실행 계약 0.4.0과 결과 DB 필드에 세 갈래 판정·증거 경로를 어떻게 담을지 (이 문서는 계약 문서를 확인하지 않았음)
- [ ] 정답 라벨을 누가, 도구 결과를 보기 전에 만들지

## 출처

| 출처 | 종류 | 이 문서에서 쓴 내용 |
| --- | --- | --- |
| [Liu et al., Malicious Agent Skills in the Wild (USENIX Security '26, arXiv 2602.06547)](https://arxiv.org/abs/2602.06547v1) | 논문 | 샌드박스 구성, 미끼, 확정 기준, 한계 |
| [Liu et al., Agent Skills in the Wild (arXiv 2601.10338)](https://arxiv.org/abs/2601.10338) | 프리프린트 | 독립 라벨링, 2인 검토 |
| [Debenedetti et al., AgentDojo (NeurIPS 2024)](https://arxiv.org/html/2406.13352v3) | 논문 | 환경 상태 기반 판정 |
| [OpenSSF Package Analysis](https://pkg.go.dev/github.com/ossf/package-analysis) | 공식 도구 문서 | 파일·연결·명령 관찰 |
| [OpenSSF 발표 보도 (Security Affairs)](https://securityaffairs.com/130831/security/package-analysis-project.html) | 보도(2차) | 행동 변화 추적 |
| [Duan et al., MalOSS (NDSS 2021)](https://arxiv.org/pdf/2002.01139) | 논문 | 동적 분석 한계 |
| [Mu et al. (USENIX Security 2018)](https://usenix.org/node/217570) | 논문 | 환경 기록과 재현성 |
| [Klees et al., Evaluating Fuzz Testing (CCS 2018)](https://arxiv.org/pdf/1808.09700) | 논문 | 기준 사전 고정, 반복 실행 |
| [Arp et al., Dos and Don'ts (USENIX Security 2022)](https://usenix.org/conference/usenixsecurity22/presentation/arp) | 논문 | 라벨 오류·표본 편향 |
| [OWASP Benchmark](https://owasp.org/www-project-benchmark/) | 공식 프로젝트 | TP/FP/TN/FN, Youden 지수 |
| [MITRE ATT&CK](https://attack.mitre.org/) | 공식 분류표 | 관찰 지표 매핑 |
| 팀 문서: `docs/meetings/2026-10-17-01-회의록.md`, `docs/research/2026-09-20-프로젝트-사전검증/05-보안효과와-사용자판단-평가설계.md`, `claude/skill-scanners-and-methods.md` | 내부 | 현재 결정·세 갈래 판정·SkillDetonate 요약 |

SkillDetonate(arXiv 2607.02357)는 이번에 원문을 열지 못했고, 팀 조사문서 요약만 참고했습니다.
