# 공개 루트 실행 분기 M12

기준은 저장소의 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`이다. `dist/blueprint.js`의 `renderContractPanel`(969행), branch-exit 선택/이름 처리(718–739행), 실행 의미(248행)를 따른다. 함수의 공개 분기 ID, 캔버스의 반환 위치, 호출자의 실행 포트를 연결한다. 정보의 `Enum/EnumValue`와 개별 코드의 private `Result`는 별개다.

## 이번 지원 경계

직접 소유한 동기 `void` 함수, 값 입력과 선택적인 **정수 `out int` 하나**, 이미 저장된 직접 소유 Blueprint target 전부와 명시 선택한 직접 Blueprint 호출자들을 다룬다. 같은 그래프의 반복 호출과 여러 호출자/target을 하나의 계약 변경에 포함한다. Blueprint 호출자가 없어도 분기를 정의할 수 있으며 기존 C# `IInvoke` 소비자는 유지한다. 모든 Root는 기존 `sync-acyclic-switch-v1`이어야 한다. 루트의 C# 원문, 노드 ID·핀·입력 값과 화면 위치를 보존한다. 함수의 공개 입력/ordinary 출력 계약을 변경하지 않는다. 원본 부모/외부/참조, override 입출력 계약 및 권한을 확장하지 않는다.

기존 분기 사이드바에서 추가/이름/삭제, 반환 카드 배치/기존 ID 선택과 실행선 연결을 사용한다. 함께 갱신할 호출자는 자동으로 고르지 않는다. 현재 영향받는 호출 위치 전부를 직접 선택해야 하며 누락/중복은 거절한다. 다른 target의 반환도 공개 ID 또는 `None`으로 명시 대응한다. 물리 파일을 공유하는 target은 모호한 초안 소유권을 피하기 위해 현재 거절하며, 이를 영구 UX 정책이나 필수 마이그레이션으로 확정하지 않는다. 삭제 전에 반환 카드와 호출자의 연결을 명시적으로 해제해야 한다. 호출자의 기존 다음 줄은 유지한다. 분기 줄은 기존 노드 실행 규칙에 따라 실행한 뒤 다음 줄로 돌아가며, 함수 반환 카드는 해당 함수에서 즉시 반환한다. 미연결 일반 종료는 `None`이며 성공/실패를 추정하지 않는다. 불완전 반환 선택이나 삭제된 ID는 거절한다.

## 저장 및 실행 계약

공개 함수의 `blueprintExecutionBranches` metadata는 schema 1과 `{id,name,value}` 목록을 저장한다. 표시명은 C# 식별자로 사용하지 않는다. ID에서 만든 enum 멤버와 명시적 양수 값을 사용하며 0은 분기 선택 없음이다. 이름/배치 순서를 바꾸어도 ID/값을 유지한다. 마지막 명시 분기를 해제해 목록이 비어도 이미 선언된 실행 인터페이스는 `None`만 반환하는 계약으로 유지한다. 원래 `void Invoke`를 제거하거나 재작성하지 않는다. 기존 `IInvoke.Invoke(...) -> void`는 유지한다. 선택한 분기 결과는 별도의 `IExecutionInvoke.InvokeExecution(...) -> ExecutionResult`로 전달한다. 원래 호출은 한 번 실행한다. 코드 생성의 어댑터가 결과를 전달하거나 버리며 사용자 C# 본문을 재작성하지 않는다. catalog는 분기와 실행 인터페이스를 별도로 노출한다.

루트 schema 2 / `executionExitMode`와 정확한 함수 계약 hash, 호출자의 `publicExecution` receipt를 함께 검증한다. 각 반환 위치는 공개 분기 ID 하나를 참조한다. 기존 M11 private 종료점의 완전성/coverage 검증은 바꾸지 않는다. 공개 계약과 대응 없는 새 caller 분기나 낡은 receipt는 거절한다.

정수 출력은 기존 export 카드와 데이터 연결을 유지한다. 기존 `IInvoke(..., out int)`와 선택적 `IExecutionInvoke.InvokeExecution(..., out int)`가 같은 out 매개변수를 전달하며, 결과 enum은 별도 반환한다. 호출은 한 번만 일어나고 out 값을 발행한 뒤 호출자가 결과 분기를 실행하며 다음 줄로 이어진다. C# 본문에 매개변수를 추가하거나 결과 tuple로 재작성하지 않는다. 출력 미배정/예외의 기존 컴파일 경고·기본값·저장소 규칙은 유지하고 새 성공/실패나 출력 값을 추정하지 않는다. 다른 out 타입·복수 out·ref 입력·비void 반환은 이번 지원 경계 밖이다.

루트 함수·구현·그래프와 호출자 함수·구현·그래프 및 원래 C# record가 하나의 `rootContractGroup`이다. 전체 후보를 준비한 뒤 체크포인트 CAS로 저장하고 전체 그룹을 Review→Confirm한다. 바꾸지 않는 원문과 헤더도 체크포인트 저장 및 최종 파일 commit lease의 읽기 전용 hash 검사에 포함한다. Confirm 이후에는 그룹 크기로 의미를 추정하지 않고 공통 그룹 검증을 통과한 전체 멤버의 기준본을 갱신한다. 호출자가 없는 작은 그룹도 같은 검증을 사용하여 재시작 후 재편집에서 낡은 기준본을 남기지 않는다. 일부 Review, 외부 변경, 쓰기 실패는 전체 미적용하며 원본과 편집 입력을 보존한다. 응답이 유실되면 기존 attempt/receipt로 저장 결과를 조회한다.

## 별도 잔여와 호환성

이 단위는 모든 공개 함수 형태의 M12 완료를 뜻하지 않는다. same-contract copy/자식 소유 본문의 기존 공개 분기 반환과 다른 원래 호출 문맥은 다음 잔여다. 이번 계약 편집은 일반 switch-profile Root와 직접 호출만 지원한다. 중첩/private 호출, 다른 callee import가 섞인 호출자, 여러 provider의 계약 변경은 아직 원자 결합 경계 밖이며 정상 금지 정책으로 확정하지 않는다. 정수 out 하나 밖의 ordinary 값 출력·ref/out 결합은 별도 원래 지원 경계로 남긴다. 계약이 바뀌는 override나 독립 새 계약 복제는 구현 대상이 아니다. 구형 profile을 자동 승격하지 않는다. M4 async 전환·완료 순서는 이번에 구현하지 않는다.

새 metadata/루트 schema 2를 이해하지 못하는 과거 실행 패키지로 새 자료를 열 수 있다고 보장하지 않는다. 최신/롤백 패키지와 전체 SHA manifest·복원 증거를 보관하며, 이전 패키지의 원래 데이터는 보존한다. 교차 패키지·Linux hosted UI 검사는 실제 Windows/WebView2·모바일 실행이나 전체 UI 및 Space/Library 전달 검증과 구별한다.
