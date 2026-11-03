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

## 기존 공개 계약을 유지하는 copy 본문 반환

정보(schema)에 단독 배정되어 저장된 same-contract copy의 일반 switch-profile Root는 기존 공개 분기 ID/None을 반환 카드에서 선택·배치·연결할 수 있도록 연결했다. 이 첫 단위는 직접 소유 함수 계약과 저장된 소유 copy를 마감했다. 이후 추가한 새 copy·자식 소유 본문·등록 외부 함수의 현재 상태는 아래 항목과 유한한 M12 대조표를 기준으로 한다. 본문 반환 지원을 공개 원계약 편집 권한으로 확대하지 않는다.

분기 정의의 이름·추가·삭제는 읽기 전용이며 함수 선언, IO/값/핀, caller의 receipt/연결과 donor/복사 C# record·provenance를 바꾸지 않는다. 편집 계획은 반환/실행선/시작점만 받는다. 공개 정의 변경 거래와 본문 반환 선택 거래를 구별한다.

본문에서 관측한 소스를 완전한 atomic 그룹과 저장 receipt에 보존한다. 저장/복원/Review에서 동일 소유 배정·owner hash·공개 계약·source proof를 확인하며 최종 파일 CAS에 변경하지 않는 원문도 포함한다. Review 뒤 함수 원문이 바뀌어도 부분 Confirm하지 않는다. 공개 루트 Confirm은 지속 checkpoint와 모든 멤버가 완전히 정착한 뒤에만 해당 거래의 live metadata를 종료한다. 이 메타데이터가 다음 copy를 미확정 provider로 오인해 막지 않도록 하며, 활성/불완전 거래는 보존한다. 지원 경계 밖의 외부 함수는 소유 함수로 바꾸지 않는다. 최종 동결 코드의 신규 LF23·CRLF19·새 패키지/전체 복원/실패 수명관리6, 총48단계가 통과했다. [지원 범위와 검증/보관](VALIDATION_V666_ROOT_EXECUTION_COPY.md).

## 새 정보 copy의 미리보기와 첫 저장

직접 소유 정보(schema)에서 같은 소유 공개 함수를 구현할 새 copy를 명시 선택하면, 미리보기에도 기존 공개 분기/None 반환 카드를 표시한다. 정의 이름·추가·삭제는 읽기 전용이다. 기존 switch Root·값 입력·선택적 int out 하나의 범위를 사용하며 첫 Save가 copy 생성·등록·정보 배정·반환 계획을 하나의 후보에 저장한다. 원래 C#·함수 계약/ID·호출 연결·donor와 부모/외부 원본은 바꾸지 않는다. 다른 소유 문맥이나 등록 외부 함수의 반환 편집까지 완료했다는 뜻이 아니다.

sealed 선택의 기존 관측 원문을 원자 그룹과 첫 Save 영수증에 보존하고 checkpoint·복원·Review·최종 파일 CAS에서 검증한다. 아직 Confirm하지 않은 copy를 후속 편집할 때도 최초 출처·배정·원문 baseline은 유지하고, 최신의 소유자 연결 author 영수증으로 본문 변경을 검증한다. 새 hash를 자동 추정하지 않으며 그룹/영수증/원문 검사 누락이나 변조를 거절한다. 독립 창은 서버가 연결한 같은 정보 소유자에서 정확한 반환 계획만 전달하며 공개 계약 편집·다른 소유자·surface 위조는 허용하지 않는다.

첫 Save의 응답이 유실되면 기존 receipt를 조회한다. 성공이 확인된 입력을 재생성하지 않으며 늦게 들어온 새 반환 입력은 별도 명시 Save로 적용한다. 명시 취소는 자기 copy 선택과 입력만 제거하고 원본 파일을 유지한다. 원래 UI·Review→Confirm·Undo/Redo와 프로젝트 경계는 공통 처리로 보존한다. 최종 **신규 LF24·CRLF20·새 패키지/전체 복원/실패 수명관리6, 총50단계**를 통과했다. [검증·증거와 보관 경계](VALIDATION_V666_ROOT_EXECUTION_COPY_CREATING.md).

보강 전의 미확정 공개 copy checkpoint에 원래 관측 그룹/읽기 영수증이 없으면 최신 버전은 이를 추정해 자동 승격하지 않는다. 원본 checkpoint를 보존하고 복원을 거절하는 호환성 경계이며, 자동 삭제/마이그레이션을 새 필수 기능으로 추가하지 않는다. 공개 문법이나 기존 IInvoke/실행 결과 인터페이스는 이번 단위에서 바꾸지 않는다.

## 별도 잔여와 호환성

이 단위는 모든 공개 함수 형태의 M12 완료를 뜻하지 않는다. 자식이 직접 선언한 ordinary 본문, 등록 외부 함수의 ordinary provider와 저장 copy 반환은 아래 후속 단위에서 연결했다. 외부 함수의 새 copy 첫 Save·다른 데이터 ABI·복합 호출은 아래 유한한 대조표의 실제 잔여다. 이번 계약 편집은 일반 switch-profile Root와 직접 호출만 지원한다. 중첩/private 호출, 다른 callee import가 섞인 호출자, 여러 provider의 계약 변경은 아직 원자 결합 경계 밖이며 정상 금지 정책으로 확정하지 않는다. 정수 out 하나 밖의 ordinary 값 출력·ref/out 결합은 별도 원래 지원 경계로 남긴다. 계약이 바뀌는 override나 독립 새 계약 복제는 구현 대상이 아니다. 구형 profile을 자동 승격하지 않는다. M4 async 전환·완료 순서는 이번에 구현하지 않는다.

새 metadata/루트 schema 2를 이해하지 못하는 과거 실행 패키지로 새 자료를 열 수 있다고 보장하지 않는다. 최신/롤백 패키지와 전체 SHA manifest·복원 증거를 보관하며, 이전 패키지의 원래 데이터는 보존한다. 교차 패키지·Linux hosted UI 검사는 실제 Windows/WebView2·모바일 실행이나 전체 UI 및 Space/Library 전달 검증과 구별한다.


## 자식 소유 본문의 기존 분기 반환

자식 implementation이 직접 선언한 ordinary `sync-acyclic-switch-v1` Blueprint target(code/export, native context·call·중첩 없는 Root)은 원래 공개 분기와 None을 반환·배치·연결한다. 부모 유무만으로 실행을 거절하던 엔진 경계를 제거하고, opaque 유효 target의 기존 거절은 유지한다. 상속받기만 한 Blueprint의 실행은 선언 소유자의 node source를 사용하며 자식 locator를 통한 부모 본문 쓰기는 허용하지 않는다.

이 경로는 직접 소유 함수의 기존 동기 void/값 입력/선택적인 int out 하나 계약을 유지한다. 공개 분기 정의·입출력·부모 및 C# record·node ID/인수/데이터 연결은 바꾸지 않는다. 반환의 entry/edges/exits만 하나의 checkpoint/Review 그룹으로 저장한다. 원본 노드와 헤더의 관측 receipt를 복원·Review와 최종 파일 CAS에 재검증한다.

이미 등록된 외부 부모는 기존 M11 ancestry 관측 계약을 읽기 전용으로 재사용한다. 최초 화면의 dependency hash를 입력 및 Save 시도 journal에 보존하고, 변경된 부모를 새 관측으로 묵시적으로 대체하지 않는다. Save·응답 복구·Review·Confirm과 최종 lease에서 외부 헤더/manifest 관측을 확인한다. 외부 부모의 본문이나 권한을 쓰거나 새 접근권한을 만들지 않는다.

부모 계약을 바꾸는 override·부모/참조 원본 직접 편집은 정상 거절이다. 등록 외부 **함수**의 ordinary provider와 저장 copy 반환은 아래 후속 단위에서 다룬다. 다른 원래 출력/호출 문맥과 M4는 이 경로 완료로 표시하지 않는다. 구형 profile의 자동 변환은 새 필수 요구가 아니다. 검증 결과는 [자식 소유 반환 검증](VALIDATION_V666_ROOT_EXECUTION_OVERRIDE.md)에 기록한다.


## 등록 외부 함수의 로컬 provider 반환

기존 ProjectPack의 직접 의존성으로 등록된 공개 함수도 정보(schema)에 명시 배정된 로컬 소유 provider의 ordinary Root(code/export)에서 기존 공개 분기/None을 반환한다. 함수의 ID·입출력·분기 정의와 provider 배정은 바꾸지 않는다. 외부 함수는 편집 source/원자 그룹에 추가하지 않고 기존 callable 계약의 함수·팩 manifest 헤더 관측만 재사용한다. local 프로젝트/구현 등록이 실제 파일과 일치하는지 먼저 확인하여 등록 철회 뒤 옛 manifest로 새 읽기를 진행하지 않는다.

외부 헤더의 text hash와 원시 파일 hash를 함께 보존한다. 최초 관측과 local 원문 closure를 Save 시도/복원/Review에 묶고, Confirm의 마지막 source lease에 외부 typed read를 결합한다. 본문·계정·외부 권한을 새로 읽거나 변경하지 않는다. 기존 switch C# 카드는 backend가 반환 편집을 허용한 경우에만 표시를 연결하며, 이 조건으로 C# 계약 편집을 새로 허용하지 않는다.

이번 검증 경계는 직접 등록된 동기 void·값 입력·선택적인 정수 out 하나, schema의 단독 명시 배정과 기존 공통 팝오버/Review 경로다. 외부 함수 공개 계약 변경은 readonly 보호이며, 외부 함수의 저장 public same-contract copy는 아래 후속 단위에서 연결했다. 새 copy 첫 Save·나머지 기존 데이터/호출 문맥은 완료로 표시하지 않는다. [등록 함수 반환 검증](VALIDATION_V666_ROOT_EXECUTION_REGISTERED.md).


## 저장된 등록 외부 함수 copy의 기존 분기 반환

직접 등록된 외부 함수를 구현하는 **저장된 로컬 same-contract copy**도 정보(schema)의 기존 단독 명시 배정에서 공개 분기 ID/None 반환을 선택·배치·연결한다. 등록 함수 계약과 donor는 readonly이며 외부 함수는 쓰기 source나 Review 그룹에 넣지 않는다. 기존 copy ABI binding·provenance, 원래 implementation/target·핀·C#와 caller 연결을 유지한다. 기존 함수의 동기 void·값 입력·선택적인 정수 out 하나와 switch-profile Root를 사용한다.

기존 등록 함수의 두 헤더 관측을 원래 저장된 copy 선언에 연결한다. 첫 dependency hash와 author 저장 receipt를 checkpoint/복구·반복 Save·Review·최종 typed read CAS까지 보존한다. 현재 프로젝트/구현 등록을 먼저 확인한 뒤 기존 registry로만 외부 경로를 재도출한다. 누락·변조·낡은 receipt, 명시 배정/관측 source 불일치, Review 이후 외부 변경은 입력을 보존하며 전체 거절한다. Confirm이 정착한 뒤의 재편집은 완료된 거래의 receipt를 새 거래로 잘못 재사용하지 않는다.

이 단위는 이미 저장된 copy의 반환 흐름이다. 등록 외부 함수의 **새 copy 미리보기/첫 Save**는 아래 별도 생성 수명 단위에서 연결한다. 새 접근권한, 외부 공개 계약 편집, 자동 provider 선택이나 독립 새 계약 복제는 추가하지 않는다. [검증·보관 기록](VALIDATION_V666_ROOT_EXECUTION_REGISTERED_COPY.md).

## 유한한 M12 대조표

원본 `dist/blueprint.js:969–976`은 readonly 정의에서도 기존 분기 반환 배치를 제공하며, `dist/app.js:2469–2476`은 원본 입출력/실행 분기를 구현보다 우선한다. 이 근거로 본문 반환 편집과 공개 계약 변경을 구분한다. 아래는 사용자 흐름별 경계이며 타입/역할/중첩 조합의 곱을 새 필수 항목으로 만들지 않는다.

| 사용자 흐름 | 현재 상태와 다음 경계 |
|---|---|
| 직접 소유 함수에 공개 분기를 정의하고 관련 Blueprint target·직접 호출자에 명시 대응 | 동기 void·값 입력·선택적 int out 하나, 복수 호출자/target은 지원·검증했다. |
| 기존 분기를 copy·자식 소유 본문에서 반환 | 소유 함수의 저장/새 copy, 자식이 직접 선언한 ordinary target, 등록 외부 함수의 ordinary provider와 저장 copy를 지원한다. **외부 함수 새 copy의 미리보기/첫 저장**도 아래 단위로 연결했다. 다음 실제 경계는 데이터 ABI와 복합 호출의 명시 대응이다. |
| 원래 데이터 입출력과 공개 분기를 함께 전달 | 동기 void의 기존 typed out·복수 out·ref를 원래 by-reference 전달과 공개 분기에 연결한다. ordinary 비void의 값과 실행 분기는 직접 소유 ordinary Root에서 원래 Invoke 반환형·생성 out 캡처·종료점 데이터 보존으로 연결한다. [지원 경계](VALIDATION_V666_ROOT_EXECUTION_NONVOID.md). 원문 재작성 없이 ordinary Invoke·저장소 alias·출력 발행 순서를 보존한다. [지원·검증](VALIDATION_V666_ROOT_EXECUTION_DATA_VOID.md). |
| 기존 복합 그래프/호출 문맥에서 공개 계약을 갱신 | 다른 직접 소유 함수를 호출하는 ordinary 본문·caller는 추가 헤더를 readonly 관측 멤버로 같은 그룹에 결합한다. [본문 import 검증](VALIDATION_V666_ROOT_EXECUTION_PROVIDER_IMPORT.md). 중첩/private·등록 외부 import receipt·여러 provider의 공개 계약 변경을 포함한 완전한 명시 대응은 실제 잔여다. [지원·검증](VALIDATION_V666_ROOT_EXECUTION_COMPOUND_OWNED.md). 단일 본문 반환의 타입 조합으로 별도 무한 목록을 만들지 않는다. |
| 비동기 완료와 분기 실행 | 별도 고정 M4다. 원본의 await→출력 발행→완료→결과 분기→다음 동작 순서를 유지해야 하며 이번 M12 반환 변경으로 완료되지 않는다. |

부모/참조 원본 쓰기·override 입출력/분기 정의 변경은 정상 보호다. 구형 profile 자동 승격·별도 핀 ID 재설계·독립 계약 복제는 필수 잔여가 아니다. 다른 출력 ABI나 복합 호출의 현재 안전 거절은 영구 UX 정책으로 확정하지 않는다. M11은 새 회귀 증거가 없으면 완료 상태를 유지한다.


## 등록 외부 함수 새 copy의 첫 저장

직접 소유 정보(schema)의 기존 구현 선택에서 등록 외부 함수의 donor와 target을 명시 선택하면, 새 copy의 미리보기에서도 공개 분기 ID/None 반환을 편집한다. 생성·ProjectPack 등록·정보 배정·반환 계획은 기존 첫 Save 후보/CAS/Review 그룹 하나다. 입력/출력·원래 C#·donor·부모/외부 원본·공개 함수 정의는 바꾸지 않는다. 지원 범위는 앞선 단위와 같은 동기 void·값 입력·선택적인 int out 하나, 기존 execution-exit switch Root다. 원본에 없는 자동 target/계약 복제·구형 profile 자동 변환은 추가하지 않는다.

선택 시 관측한 donor/함수/등록 원문을 최소 origin과 첫 Save 영수증의 해시에 보존한다. 외부 함수는 writable source가 아니다. 이후 미확정 copy의 본문 Save도 최초 origin·owner·provenance와 별도 author receipt를 유지한다. 복원은 구조·관측 해시를 확인하고, Save/Review/Confirm은 기존 registry/선택된 donor 관측으로 경로를 다시 도출한다. 저장된 경로를 임의 파일 읽기로 사용하지 않으며 최종 typed read lease가 원시 관측을 확인한다. Confirm 뒤 일반 saved-copy 편집은 완료된 생성 관측을 새 donor 의존성으로 재사용하지 않는다.

보강 전 미확정 외부 public-copy checkpoint에 이 origin/최초 관측 해시가 없으면 이를 추정해 승격하지 않는다. 원본 checkpoint와 입력을 보존하는 호환성 경계다. [첫 저장 검증·보관 기록](VALIDATION_V666_ROOT_EXECUTION_REGISTERED_CREATING.md).

확정으로 전체 그룹이 깨끗해진 뒤 남는 완료 author receipt는 새 반환 거래가 아니다. 활성 그룹 없이 원문과 같은 Root만 종료 상태로 처리하며, 수정된 Root의 그룹 누락은 계속 거절한다. 같은 세션의 후속 Save와 확정 뒤 donor 원문 변경을 확인해 생성 관측이 다시 활성화되지 않도록 한다.


## 동기 void의 여러 typed out과 ref 저장소

기존 공개 실행 결과 인터페이스와 생성 어댑터는 원래 value/ref/out 인수를 그대로 전달한다. 정수 out 하나만 허용하던 수용 경계를 동기 void의 기존 typed out·복수 out·ref로 넓힌다. C# 원문·ordinary Invoke·공개 매개변수/핀 ID/타입·값 연결·ref 저장소의 정체성을 변경하지 않는다. 기존 profile의 정확한 타입·쓰기 가능한 ref 저장소와 None/미할당 출력 기본값 검증을 재사용하며 암묵적 참조 변환을 허용하지 않는다.

직접 소유 함수의 분기 정의·target 반환·명시한 직접 호출자의 원자 후보와 Review/Confirm을 검증한다. readonly 부모/외부 계약 보호나 override 입출력 계약을 완화하는 변경이 아니다. ordinary 비void의 값 반환, 복합 호출 closure와 M4는 별도 실제 잔여다. [검증과 보관](VALIDATION_V666_ROOT_EXECUTION_DATA_VOID.md).


## 기존 반환값과 공개 분기의 별도 전달

직접 소유 동기 ordinary Root의 반환값은 기존 IInvoke 반환형을 유지하며 생성 실행 진입의 별도 out 캡처로 전달한다. 직접 종료점 값과 export-return/default를 구별해 보존하고 값 발행 후 분기/후속 동작을 실행한다. [검증 범위와 유한한 잔여](VALIDATION_V666_ROOT_EXECUTION_NONVOID.md). M4의 동기 caller는 사용자가 명시적으로 async로 전환하기 전까지 호환되지 않는 호출을 오류로 거절한다는 정책이 확정됐으며 실제 async 구현은 별도 잔여다.


## copy·자식 소유·등록 외부의 기존 데이터 반환

ordinary switch-profile의 기존 공개 분기/None 반환에 비void 직접 종료점 값·export-return/default와 typed out/ref를 보존한다. 저장/새 same-contract copy, 직접 선언한 자식 target, 이미 등록된 외부 함수의 로컬 provider·저장/새 copy를 연결한다. 함수/override IO·분기 정의와 부모/외부 원본은 readonly다. [지원 경계·검증·유한한 다음 흐름](VALIDATION_V666_PUBLIC_RETURN_DATA.md).


## 여러 직접 소유 ordinary provider의 계약 갱신

같은 공개 함수를 구현하는 직접 소유 ordinary Blueprint provider들의 모든 target과 실제 직접 caller를 기존 명시 대응 후보/CAS/Review 그룹으로 결합한다. 다른 provider의 import도 readonly 관측에 포함하며 실행 provider 선택·기존 scoped 배정을 바꾸지 않는다. opaque/override/비소유 원본과 공유 물리 그래프 보호는 유지한다. [지원과 검증 경계](VALIDATION_V666_ROOT_EXECUTION_PROVIDERS.md).


## 소유 private frame의 실제 호출 위치

기존 ordinary switch-profile private caller의 전체 경로와 local 실행선을 공개 분기 계약 후보에 연결한다. 모든 C# leaf를 qualified source ID로 관측하고 기존 body target/sourceOwner와 부모 continuation·형제·권한을 유지한다. profile/전달 계약 자동 변환은 하지 않는다. [지원/검증 경계](VALIDATION_V666_ROOT_EXECUTION_NESTED.md).
