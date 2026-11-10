# v666 C# 구현·호출자가 있는 정보 기능의 타입 전환

[고정 정보 편집9행](V536_I5_6_REMAINING.md), 원본 v666 ZIP의
`dist/app.js::choosePropertyType` signature 문맥과 기존 C# 명시 대응 절차를 잇는다.
원본 ZIP SHA256은 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다.
정보 struct·종류 enum·모듈 interface라는 확정된 결정을 유지한다.

지원하는 다음 경계는 직접 소유 정보의 일반 동기 함수와 직접 소유 일반 C# 구현·직접 C#
호출자다. 기존 `owner_Function_ID`와 소유 locator, 인자/출력 대응, 모든 영향 target의 원문
해시 및 명시 본문 계획을 재사용한다. 지원 nominal 타입·배열의 입력/out/반환을 선택하고,
원래 C# 편집기의 구현 선택 목록에서 각 영향을 받는 본문을 직접 작성한다. 구현이나 호출자
계획이 빠지거나 코드가 맞지 않으면 전체 Save를 거절한다. 원문을 추정해 고치지 않는다.

`FunctionNativeEdits`는 기존 header 관찰/receipt 예산 안에서 전환 가능성을 확인한다.
기존 선언 전용 profile은 유지하고 C# 연결에는 `native-information-function-abi-v1` shape를
쓴다. 관찰한 직접 구현/호출자 ID와 모든 원래 header/manifest가 같은 보호 초안의
`$function:<ID>` 증거에 들어간다. 상속/부모·비소유 원본, Blueprint·private copy, module
require/default·function field, async/공개 실행 계약까지 전환 범위를 확장하지 않는다.
해당 원본과 이전 기본형 대응 절차는 유지한다. source/header가 공유되면 기존 전체 소유
검증이 계속 권위가 있으며, 단지 선택 창에 노출됐다는 이유로 쓰기 권한을 만들지 않는다.

신규 선택의 등록 외부 타입도 실제 후보 컴파일에 필요하다. 검증된 nativeTypes 선택 증거의
정확한 공개 header만 기존 C# 후보의 읽기 전용 타입 사전에 더한다. `InformationDefinitions`의
정확한 선택 검증 뒤에만 이 경로로 전달하며, 구 batch 호출은 기존 기본값 경로를 유지한다.
원래 등록/dependency 밖의 선언을 추정하지 않는다. 외부 header는 소유 선언 쓰기 반복에
들어가지 않고, 원래 source hash·읽기 observations 및 최종 file lease로 보호된다.

Save는 함수·구현·호출자의 header와 명시 C#을 한 후보로 검사하고 checkpoint에만 보관한다.
Review/Confirm은 원래 전체 컴파일과 원자 CAS를 유지한다. 바꾸는 C#의 원본은 기존 쓰기
대상의 baseline으로 보호하며, 변경하지 않는 타입/원본은 읽기 guard로 보호한다. 컴파일러의
nullable 경고를 오류로 취급하는 기존 규칙도 유지한다. Save의 정적 검증 성공은 최종 실행
컴파일 성공이나 원본 반영을 뜻하지 않는다.

늦은 이름 입력이 수락된 타입/본문 계획과 같은 상태라면 receipt 정산 뒤 그 이미 수락한
mapping만 제거하고 새 이름을 보존한다. 변한 서명이나 다른 본문 계획은 제거하지 않는다.
따라서 후속 Save가 과거 본문 hash를 다시 제출하지 않으면서도 새 입력을 잃지 않는다.
취소·Undo/Redo·재시작·쓰기 실패·응답 유실은 기존 보존 체계를 재사용한다.
확정 후 같은 계약의 C#을 다시 작성할 때도 기존 계약에 선언된 nominal 타입을 새로
관찰해 보호 증거를 붙인다. 다른 타입을 임의 선택하지 않으며, 변경하지 않는 호출자 원문은
읽기 전용으로 유지한다.

새 `.celem` 문법이나 공개 override 계약은 만들지 않는다. 보호 초안은 기존 v2/profile이다.
이전 게시본은 연결된 함수의 새 scope를 거절한다. 구 parser/compiler/보관본의 nominal/enum
제한을 유지하며, 이전 전체 reader 바이너리를 실제 실행한 완료 주장이나 자동 migration은 없다.

모듈 async/실행 요구는 `ModuleInterfaces`의 기존 동기 제한을 단순 해제할 수 없다.
기존 `BlueprintAsync.Result`와 `BlueprintExecutionBranches.Result`는 함수 계약 DLL에 있고,
정보 DLL의 모듈이 이를 참조하면 같은 pack의 함수 계약→정보 타입→함수 계약 순환이 가능하다.
계약만 선택하는 closure와 산출물 의존성까지 해결해야 하며 결과형을 복제하거나 기존 C#을
자동 변환하지 않는다. 이는 다음 구현 의존성이며 이번에 새로운 표현 정책으로 확정하지 않았다.
동기 호출자는 명시적 async 전환 전 오류라는 확정 규칙을 유지한다.

살아 있는 참조는 `RuntimeObjectContracts`의 설명과 실제 caller 제공 객체/접근자 연결을
구분한다. 선언 data/default나 객체 ID로 값 snapshot을 만들지 않았다. 고급 Blueprint ABI,
살아 있는 참조 접근과 module async/공개 실행 요구는 같은 유한9행의 잔여다.
M11/M12/M4를 새 회귀 없이 다시 열거나 선택적 조합을 필수로 늘리지 않는다.
기존 CSS/카드/상세창 배치를 유지한다. 실제 Windows/모바일·전체 UI는 미검증이며 초기 빈
화면 원인은 미확정이다.

[최종 검증·보관 기록](VALIDATION_V666_CONNECTED_NATIVE_TYPES.md)을 확인한다.

[후속 직접 Blueprint 호출자 입력 연결](V666_BLUEPRINT_NATIVE_INPUTS.md)의 한정 범위와 보호를 확인한다.
