# 최종 결과에서 제외

- 상태: NOT_ASSESSED
- 모델: Llama 3.2 3B
- 계획 run: 6
- 완료 run: 0
- 관찰: 6/6 HTTP 500
- verifier: FAIL, issues 12

이 배치는 실행 인프라 오류로 완료된 모델 행동 증거가 없다. 효과 0이나 utility 0을 안전 결과로 계산하지 않는다. 최종 유효 집계는 같은 모델의 별도 v2 배치를 사용한다. 배치 증거 자체가 직접 확인하는 범위는 HTTP 500, completed 0, raw verification 0까지다.
