# 정보 기능의 고급 타입과 직접 Blueprint 호출자 입력

고정 [정보 편집9행](V536_I5_6_REMAINING.md), 원본 v666 ZIP의
`dist/app.js::choosePropertyType` signature 문맥과 기존 명시 계약 대응을 잇는다.
원본 ZIP SHA256은 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다.
정보별 struct·종류 enum·모듈 interface라는 사용자 결정을 유지한다.

직접 소유한 일반 동기 정보 기능의 C# 구현과, 직접 소유한 일반 직렬 Blueprint 호출자가
이미 가진 같은 타입의 입력 값을 연결한다. 기존 상세창에서 타입을 선택하고 기존 입력
대응 창에서 `호출자 입력`을 명시 선택한다. 예전 입력 연결의 해제와 C# 구현의 명시 본문
계획도 함께 요구한다. 구조체·enum·interface 배열의 입력을 새 호출 계약에 전달하되 함수/
구현/노드/핀 ID·좌표·실행선·반환 연결과 호출자 자신의 공개 계약은 유지한다. 기존 C#
원문이나 runtime 호출자를 추정하여 변환하지 않는다. 원래 카드/상세창/CSS 배치를 유지한다.

`native-information-function-blueprint-call-v1` scope는 직접 C# 구현과 일반 직접 호출자
헤더/manifest뿐 아니라 실제 Blueprint 원문을 관찰한다. Blueprint 구현 자체, 내부 graph/
copy·opaque C#·후처리·실행 분기·async 호출자는 이 선택 범위로 승격하지 않는다.
상속·부모/외부 원본·require/default/함수 필드와 override 계약은 기존 보호를 유지한다.
등록이나 선택 창의 노출만으로 편집 권한을 만들지 않는다. 기존 C# 전용 scope와 선언 전용
scope의 shape는 바꾸지 않는다. 기존 v2 보호 초안 안에 정확한 source 증거를 보관한다.

명시 입력 계획의 `binding`은 관찰한 호출자 입력 중 정확히 같은 nominal 타입만 가리킨다.
새 객체/접근자·지역값을 만들거나 선언 data/default/$ref를 값 snapshot으로 읽지 않는다.
이름/위치로 타입을 추정하지 않으며 알려지지 않은 입력, 다른 타입, 자기 결과, 임의 JSON
구조체 값은 거절한다. 기존 입력의 해제를 따로 확인하고 다른 연결을 묵시적으로 버리지 않는다.
최종 Blueprint 검증·실제 C# 후보 컴파일과 원래 Review/Confirm·최종 CAS가 계속 권위다.
선택한 원본이 바뀌면 Save/Confirm 전체를 거절하며 입력을 유지한다.

선택 창의 현재 값·본문 계획·정확한 scope는 기존 Undo/Redo·취소·별도 창·재시작 보관과
checkpoint 실패·응답 유실 정산·늦은 입력 보존을 재사용한다. 이미 수락한 같은 mapping을
늦은 이름 Save가 다시 제출하지 않도록 하는 기존 receipt 규칙도 그대로 사용한다.
Confirm 뒤 같은 계약의 C# 본문 편집은 새 타입/source 증거로 수행한다.

이 단위의 마감 조건은 기존 caller 입력의 명시적 nominal 연결과 native 본문 계획을
한 후보로 저장·복원·검토·확정·실행하고, 실패/CAS/유실/늦은 입력과 기존 C# 호출자의
회귀를 최종 코드에서 확인하는 것이다. 고급 Blueprint 전체나 M11/M12/M4를 재개한 완료
주장이 아니다. Blueprint 구현 entry/출력의 고급 ABI 대응은 같은9행의 남은 사용자 흐름이며,
선택적 타입/문맥 조합을 새 필수 행으로 늘리지 않는다.

살아 있는 reference의 caller 제공 객체/접근자 연결과 module async·공개 실행 계약도
독립 잔여다. 후자는 기존 `BlueprintAsync.Result`/`BlueprintExecutionBranches.Result`를 보존하는
계약-only closure와 assembly 의존성 처리가 선행된다. 같은 pack의 계약 DLL→정보 DLL→
계약 DLL 순환을 결과 ABI 복제/생략으로 회피하지 않는다. 동기 호출자는 명시적 async
전환 전 오류라는 확정 정책을 유지한다. 현재 이 입력 연결에 추가 사용자 결정은 필요하지 않다.

구 compiler/reader의 nominal/enum/parser 제한을 유지한다. 직전 sealed authoring 바이너리의
읽기 전용 scope 거절과 새 compiler에서의 실행은 각각 구분한다. 이전 전체 reader 실행이나
자동 migration을 뜻하지 않는다. 실제 Windows/모바일·전체 UI는 미검증이며 초기 빈 화면
원인은 미확정이다. 최신/rollback 패키지와 원본·증거는 기존 관리 규칙에 따라 보존한다.

이 한정 범위의 [최종 신규45단계·재사용0 검증과 보관](VALIDATION_V666_BLUEPRINT_NATIVE_INPUTS.md)을 마쳤다.
