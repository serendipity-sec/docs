# 사전조사 실험 코드와 원본 증거

상세 문서와 재현 코드·원본 증거를 **docs 저장소 한 곳**에 보관한다.

- [테스트별 상세 문서 42개](../research/2026-09-21-검토공백과-기존도구-데모설계/tests/README.md)
- [실험 코드·입력·원본 결과](live-agent-security/README.md)
- [저장 증거 재검증 명령](live-agent-security/publication-guide.md)
- [바이트 단위 이관 검증](live-agent-security-import.json)

명령은 이 저장소의 루트인 `docs/`에서 실행한다. 기존 기록의 `platform` 경로는 당시 실행 위치이며 현재 필수 경로가 아니다. 해시에 포함된 원본 코드·계획·결과·실행 경로는 변경하지 않고 그대로 보존했다. `.gitattributes`는 증거 경로의 줄바꿈 변환을 금지한다.

설치 런타임과 모델 가중치는 포함하지 않는다. 결과 검토는 저장된 기록만으로 가능하며, 동적 재실행에는 별도 환경과 새 batch가 필요하다.
