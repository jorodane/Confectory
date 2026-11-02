# M12 데이터 ABI와 M4의 유한한 경계

기준은 저장소 v666 ZIP과 원계약/C# 보존 합의다. 새 copy 첫 Save와 별개의 남은 실행 계약을 사용자 동작별로 묶으며 타입·역할·문맥의 곱을 작업 목록으로 만들지 않는다.

| 흐름 | 원본으로 확정된 요구 | 현재 경계/다음 구현 |
|---|---|---|
| M12 데이터와 분기 동시 반환 | 입출력 ID/타입/역할과 ordinary Invoke/C# 원문을 유지한다. 데이터 발행 뒤 결과 분기와 다음 동작을 실행한다. | 동기 void의 typed out·복수 out·ref를 기존 by-reference 전달에 연결한다. ordinary 비void 반환은 별도 결과 데이터 경로가 필요하며 아직 잔여다. [지원·검증](VALIDATION_V666_ROOT_EXECUTION_DATA_VOID.md). |
| M12 복합 호출 계약 갱신 | 영향받는 caller/target 전부의 명시 대응·한 후보/CAS·원본 보존이 필요하다. | 다른 직접 소유 함수 import를 함께 쓰는 ordinary caller는 추가 헤더의 readonly 관측과 같은 거래에 연결한다. 중첩/private·등록 외부 import receipt·여러 provider의 공개 계약 변경은 완전한 closure의 실제 잔여다. [범위·검증](VALIDATION_V666_ROOT_EXECUTION_COMPOUND_OWNED.md). 새 자동 선택 정책을 만들지 않는다. |
| M4 비동기 실행 | await → 출력 발행 → 완료 → 결과 분기 → 다음 동작. ref 입력은 거절하며 본문 await/내부 async가 남았으면 동기 전환을 거절한다. | 실제 async 저장·실행·호출 어댑터가 남아 있다. 표시만 async로 바꾸거나 Task를 무시하고 다음 동작으로 진행하지 않는다. |

## 원본이 정한 것과 내부 표현

`dist/app.js:2469–2476`은 inputs/outputs/parameters/returns/executionOutputs를 구현보다 우선한다. `dist/blueprint.js:248`의 실행 계획은 `publish-outputs`를 완료/결과 분기보다 앞에 둔다. None과 기존 branch ID는 정보 EnumValue와 구별하며 예외를 임의의 실패 분기로 치환하지 않는다.

동기 M12의 다른 CLR 데이터 전달을 위한 별도 결과 인터페이스/생성 어댑터 표현은 원래 Invoke·노드 출력 정체성·저장소 alias·실행 순서를 보존하는 구현 선택이다. 동기 void의 여러 typed out/ref는 기존 메서드 인수로 전달하므로 새 공개 결과 구조가 필요하지 않다. 원래 반환 값을 버리거나 공개 C# 본문을 tuple/enum 반환으로 재작성하는 선택은 허용되지 않는다. 과거 구현의 int out 제한을 언어 자체의 영구 제한으로 규정하지 않는다. 정보 종류(Enum/EnumValue)의 CLR 표현 결정은 별도 잔여이며, 그 결정을 기다릴 필요 없는 기존 CLR 데이터 경로는 독립적으로 진행한다.

비void에는 기존 private wrapper의 `native-return-out-v1`과 같은 별도 반환 캡처를 재사용할 수 있다. 현재 일반 Root의 직접 exit 값과 명시 export-return은 서로 다른 저장 형태이므로, 원래 값 연결을 보존하는 후보/표시 연결까지 필요하다. 단순히 반환형 검사만 제거하면 값 또는 분기 의미를 잃는다. 어댑터 내부 모양 자체를 새 사용자 정책 결정으로 확대하지 않는다.

## M4에서 따로 대조해야 할 호환성

원본 `blueprint.js:113–128`은 실행 중 async 의존성을 상위 graph에 전파하고 ref 입력을 막는다. `171–176`은 async 결과에 Branch와 출력들을 함께 담는 Task 결과 모델을 제시한다. 이 데이터/완료 순서는 미정이 아니다.

반면 현재 Confectory의 기존 동기 IInvoke 소비자가 async provider를 호출할 때의 호환 경계는 프로토타입의 Execute 예제만으로 확정되지 않는다. 동기 blocking bridge는 기존 반환 시점은 유지하지만 사용자 SynchronizationContext의 교착/블로킹 위험이 있고, 명시 async 진입만 허용하려면 미대응 동기 caller의 전환을 원자적으로 거절/안내해야 한다. 자동 Task.Run이나 C# await 삽입은 원문과 호출 문맥을 바꾸므로 임의 채택하지 않는다. 실제 M4 어댑터/소비자 대조 때 기존 계약으로 해결되는 범위와 사용자 결정이 필요한 경계를 구분한다. 이 점은 현재 copy 구현이나 동기 M12 데이터 전달을 막지 않는다.

현재 생성 계약/실제 binding/entry는 IInvoke를 동기로 호출하며 별도 IAsyncInvoke가 없다(`Generation.cs`의 ContractSource/FinalSource). 2026-11-02에 미전환 동기 호출자가 있으면 전환 전체 거절(권장)과 동기 차단 브리지의 실제 호환 선택을 사용자에게 질문했다. 답변 전에는 그 정책에 의존하는 M4 전환을 구현하지 않으며 독립 M12를 계속한다.

원본 async toggle의 void return 재작성 예제(`blueprint.js:128`)를 사용자 C# 원문에 자동 적용하지 않는다. 원문 보존 합의가 우선하며 별도 생성 어댑터로 의미를 보존할 수 있는 범위를 확인한다. 취소/예외를 새 성공·실패 정책으로 바꾸거나 별도 권한/실행 스케줄을 만드는 것은 이 요구에 포함되지 않는다. 3D 표시 팩의 이동/도착은 async 작업 시작 조건이 아니며 권한 팩과 기존 실행 검증을 우회하지 않는다.
