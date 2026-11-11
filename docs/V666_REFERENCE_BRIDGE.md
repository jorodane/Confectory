# 실제 인스턴스의 정보 계약 연결

고정 [정보9행](V536_I5_6_REMAINING.md)의 객체 참조 접근에서 첫 runtime 연결 단위다.
원본 v666 ZIP SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의
`app.js::propertyTypeChoiceObjects`는 정보 값의 순환 포함을 제외하고, `referenceInput`은
참조 대상을 보관한다. 현재 `SchemaContracts.ValidateSingle`의 reference도 적용 정보의
ID/상속을 검사한다. 이를 값 복사나 C# 메모리 ref로 치환하지 않는다. 정보별 C# struct,
종류 enum·모듈 interface라는 사용자 결정과 기존 native 값 ABI를 유지한다.

새 readonly `informationReference` 질의의 `descriptor`는
`information-object-reference-v1`의 정보 ID/상속·원래 필드 ID·타입·cardinality·정확한
기존 필드 hash를 담는다. 기존 ObjectModel descriptor와 같은 필드 생성 경로를 사용한다.
별도 envelope의 observations/bodyReads/runtimeValuesRead/sourceWritten은 검증 관측이며
runtime contract 안에 섞지 않는다. 선언/등록을 읽으며 값·getter·provider body를 읽거나
실행하지 않는다. 등록된 외부 정보도 원래 명시 dependency 없이는 거절한다.

`Confectory.ObjectModel::BindReference(object target,string contract,out string owner) -> object`
는 호출자가 이미 제공한 ObjectModel v1/v2 인스턴스를 그 명시적 정보 계약과 비교한다.
성공하면 **동일한 object handle**과 실제 object/concept owner ID를 반환한다. 이 owner를
기존 checked Read/Set에 명시적으로 전달할 수 있다. 정보의 부모 계약에 해당하는 원래
필드 ID가 보존된 파생 정보도 가능하며, 다른 객체의 추가 schema 필드는 합치거나 버리지
않는다. 같은 정보/부모에서 추가·삭제·타입/계약 변경된 필드가 있으면 거절한다. 다른 origin의
동명 필드를 원래 ID 대신 자동 대응하지 않는다.

바인딩은 타입/필드 선언만 확인한다. 값은 기존 Read/Set에서 검사하며, unset 필드나
비지원 필드를 초기화·정규화하지 않는다. ID/$ref 문자열·JSON·값 snapshot을 인스턴스로
조회/복제하지 않고, getter나 함수 provider도 호출하지 않는다. 원래 receiver·StrongBox
셀·배열·참조·함수 handle과 alias를 유지한다. 반환 handle이 같은 실제 객체를 보유하는
일반 CLR strong-reference/GC 수명이며, 전역 registry·interning·lease·Dispose/소유 이전은
추가하지 않는다. v1도 같은 handle이고 RefCell의 v1 거절은 그대로다.

contract는 호출자가 명시적으로 제공한 **버전 snapshot**이다. 현재 프로젝트 파일이나
인스턴스 ID를 runtime에서 조회하지 않고 기존 alias를 소급 취소하지 않는다. 새 source의
계약과 오래된 인스턴스가 다르면 새 연결은 거절한다. 이 검사나 owner 출력은 권한 토큰이
아니다. 원래 등록·실제 handle·호출 가능한 provider와 source 쓰기/권한 경계는 그대로다.
C# 문자열 안의 schema ID를 추론해 편집기 읽기 권한이나 source dependency를 만들지 않는다.

기존 primitive/enum/compound/function/reference 필드 descriptor와 checked accessor는
바꾸지 않는다. 정보의 native 값 struct 및 interface에 새 참조 필드를 object placeholder로
넣지 않는다. **정보별 typed reference ABI/struct reference 필드와 그 타입 선택 연결은
후속**이며 이번 opaque object bridge의 완료로 합산하지 않는다. 선언 데이터의 구현/객체
ID에서 인스턴스를 생성하는 자동 binding도 없다. 기존 `calls.X`로 사용자가 직접 제공한
함수 handle의 생성/호출 규칙은 원래 binding generator를 따른다.

기존 직접 소유 본문 UI에서 별도 receiver를 명시적으로 연결하고, 반환된 owner로 같은
인스턴스를 수정한 후 값31을 반환한다. 값 struct 입력100과 실제 receiver30을 구분하고,
원래 ref 셀도31로 바뀌는지 확인한다. 이 typed 본문은 이미 관찰한 정보 source·등록 import
receipt와 기존 Save/Review/Confirm/최종 CAS를 사용한다. 모든 임의 C# 문자열에서 정보
source를 자동 추론한다고 주장하지 않는다. 원문·부모/외부 원본·override 계약·UI 배치는
유지한다. M11/M12/M4는 회귀 없이 다시 열지 않는다.

새 질의/API와 pack 함수는 추가 기능이며 기존 프로젝트 저장 형식을 변경하지 않는다.
옛 authoring 도구는 `informationReference`를 지원하지 않으므로 새 질의에는 갱신된 도구가
필요하다. 기존 object/concept descriptor와 필드 hash는 회귀로 비교하며, 새 reference
profile을 옛 reader가 이해하거나 자동 변환한다고 가정하지 않는다.

이 단위는 실제 receiver/owner·alias·반환/out·GC/해제, 거절/복원, 등록 dependency와 기존
metadata 회귀, UI 취소/Undo/실패/cold/응답 유실/늦은 입력, LF/CRLF와 새 패키지 전체
복원으로 마감한다. 결과는 [검증 기록](VALIDATION_V666_REFERENCE_BRIDGE.md)에 구분한다.
실제 Windows·물리 기기·전체 UI는 별도이며 초기 빈 화면의 원인은 미확정이다.

이 한정 범위의 [최종 신규 42단계·재사용 0 검증과 보관](VALIDATION_V666_REFERENCE_BRIDGE.md)을 마쳤다.
