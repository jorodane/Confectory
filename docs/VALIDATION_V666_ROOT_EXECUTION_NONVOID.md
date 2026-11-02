# M12: 기존 반환값과 공개 실행 분기

## 원본 요구와 이번 범위

저장소 v666 `dist/app.js:2469–2476`은 returns와 executionOutputs를 구별한다. `dist/blueprint.js:248`은 출력 발행을 결과 분기와 후속 동작보다 앞에 둔다. 이 요구에 맞춰 직접 소유한 동기 ordinary Blueprint 함수의 기존 반환값을 공개 분기와 함께 전달한다. 원본 C#·함수/핀 ID·IO 타입/역할·연결·provider 선택·권한·레이아웃을 재작성하지 않는다.

기존 `IInvoke.Invoke(...) -> T`는 그대로다. 생성 `IExecutionInvoke`의 별도 진입이 기존 인수 뒤의 생성 `out T`로 원래 반환값을 캡처하고 기존 ExecutionResult를 반환한다. 캡처 매개변수 이름은 기존 인수와 충돌하지 않도록 할당한다. Blueprint 호출 노드는 이 값을 기존 return 데이터 포트에 발행한 뒤 공개 분기를 실행한다. tuple/enum으로 사용자 C# 반환문을 바꾸거나 예외를 실패 분기로 치환하지 않는다.

비void 공개 종료점은 `{executionBranch, value}`로 기존 직접 값 연결과 분기 ID를 함께 보존한다. `value:null`은 기존 export-return/미할당 기본값을 사용한다. 공개 계약 전환 후보는 기존 종료점의 데이터 연결을 몰래 변경·누락하면 거절한다. UI 분기 선택·다른 target 선택도 기존 데이터를 보존한다. 새로운 반환 배치는 기존 export/default 의미를 사용한다. void/private 종료점의 기존 저장 형태는 유지한다.

## 검증 경계

검증 결과는 최종 동결 코드 기준으로 아래에 기록한다. 이번 사용자 흐름은 int 반환·ref int·out long/string, 직접 종료점 값과 기존 export-return을 함께 사용한다. native 계약 테스트는 반환 캡처 이름 충돌·일반 Invoke·잘못된 값 선택·None/기본값도 확인한다. 이미 지원된 저장/Review/Confirm·복원/receipt·충돌·쓰기 실패·응답 유실·늦은 입력 검증을 이 데이터 흐름에서 실행한다.

구형 parser/생성기는 비void 공개 실행 계약을 이해하지 못하므로 새 데이터를 과거 버전에서 열 수 있다고 보장하지 않는다. 원본·checkpoint·검증 증거와 최신/정상 롤백을 보존하며 자동 migration을 만들지 않는다.

## 유한한 실제 잔여

1. 같은 데이터·분기 전달을 기존 copy/자식 소유/등록 외부 함수 반환 흐름에 적용하고 원래 소유권·readonly receipt 경계를 확인하기.
2. 공개 계약 변경에서 중첩/private의 실제 호출 위치와 등록 외부 import의 관측을 같은 원자 후보에 결합하기.
3. 여러 직접 소유 ordinary provider의 공개 계약·target 반환·명시 caller 대응을 한 후보에 결합하기.

이 목록은 사용자 흐름별이며 타입·ref/out·문맥의 모든 곱을 새 요구로 만들지 않는다. 부모/참조 원본 직접 쓰기·override 공개 계약 변경은 정상 보호다. 구형 profile 자동 승격·독립 새 계약 복제는 필수 범위가 아니다. M11은 구체적 회귀가 없으면 닫힌 상태다.

M4의 동기 호출자 정책은 2026-11-02에 확정됐다. 호출자가 명시적으로 async로 바뀌기 전에는 호환되지 않는 호출을 오류로 표시하고 거절한다. 자동 blocking/await 삽입/caller 변환은 하지 않는다. 실제 async 저장·호출·완료 실행은 다음 고정 M4 구현이며 이번 동기 M12 완료와 구분한다. 3D 이동은 표시 연출이며 실행 조건이 아니고 3D·권한은 별도 팩이다.
