# 정보 구조체의 단일 복합 값 필드

고정 [정보 편집9행](V536_I5_6_REMAINING.md)과 [정보별 구조체 기반](V666_INFORMATION_STRUCTS.md)의
같은 타입 생성 흐름을 확장한다. 저장소 v666 ZIP SHA256
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의
`app.js::propertyTypeChoiceObjects`는 Info 값의 순환 포함을 제외하며,
`applyPropertyMultiplicity`는 값을 구조 복사한다. 현재 `SchemaContracts.ValidateSingle`의
compound는 대상 정보의 필드 값을 재귀 검증한다. 이 근거에 따라 **단일 복합 값 필드**는
대상 정보의 별도 C# struct를 값 필드로 포함한다. 참조/$ref나 종류를 같은 값으로 바꾸지 않는다.

`information-struct-compound-v1`은 기존 정보 ID별 CLR 이름을 유지하고 단일 compound
필드의 CLR 타입을 정확한 자식 정보 타입으로 생성한다. 직접 사용한 정보부터 자식의 전체
값 closure를 선택하며, 상속 필드와 공통 자식도 같은 nominal 정체성을 유지한다. 자식
shape hash를 상위 shape에 포함하여 깊은 자식의 필드 변경이 상위 정보·함수/구현·링크
산출물에 전파된다. 표시명/아이콘만 바꾸면 값 shape는 같다. 기존 primitive-only
`information-struct-v1`의 필드 descriptor·shape hash·생성 source는 그대로다.

타입 DLL은 기존 pack별 assembly 이름과 경계를 유지한다. 다른 pack의 자식은 실제
선언된 dependency와 등록 원본만 읽으며, 생성 DLL/ref의 전체 전이 참조를 compiler와
링크에 전달한다. 같은 타입 assembly의 다른 선택된 타입이 필요한 참조도 포함한다.
자식의 nominal ID를 바꿨을 때 기존 C# initializer를 자동 변환하지 않는다. 원래 C#은
컴파일 오류로 거절하고 사용자가 명시한 대응 코드만 검사한다. 부모·외부 정의나 등록,
배정·권한·원본 C#·public override 계약을 쓰기 대상으로 추가하지 않는다.

직접 소유 같은 계약 본문의 Roslyn 후보도 같은 전체 struct closure를 사용한다. 모든
필요한 정보/부모가 기존 관측 선언에 있어야 하며, 누락된 원본을 추정하지 않는다. 부모의
같은 이름 필드 계약 변경은 기존 Registry와 같은 규칙으로 거절한다. 기존64부모 제한을
순환 검증으로 바꾸어 알려진 선언/읽기 예산 내에서 추적하며, 새 깊이별 제한은 넣지 않는다.
원래240 read-write/2048 known-unit·64-member Review·타입256/유효 필드256 예산은 유지한다.
단일 정보 함수 저장의 기존 source scope/version3 receipt를 그대로 사용한다. 자식만
변경되고 Root 타입명·Root 선언이 같아도 Save/Review→Confirm의 원래 읽기 해시/CAS로
거절한다. cold·Undo/Redo·취소·실패/재시도에서 원문과 입력을 유지한다.

값 포함 순환은 기존 구조 계약과 C# struct 제약에 따라 거절한다. 선택된 pack 타입 DLL
사이에 순환 참조가 필요한 경우도 `INFORMATION_CLR_PACK_CYCLE`로 거절한다. 자동으로
pack을 합치거나 assembly/타입 정체성을 바꾸지 않는다. 이 경계를 새 필수 migration이나
조합별 끝없는 잔여로 늘리지 않는다. multiple/배열 필드, reference의 객체 정체성·접근,
function·종류 필드와 타입 선택 UI/고급 Blueprint 대응은 동일한 고정9행 후속이다.

종류는 현재 `EnumDefinition`의 opaque member ID이며 `SchemaContracts`도 ID 문자열을
검증한다. 이름/순서/int 위치로 선택을 치환하지 않는다. 사용자는 종류는 C# enum, 모듈은 C# interface라고 확정했다. 표현 선택은 답변 대기가 아니다.
항목 ID에 대응하는 숫자는 이름/행 순서 변경에도 유지해야 하며 후속에서 기존 저장 계약과
연결한다. 이 compound checkpoint는 enum/interface를 구현한 것으로 세지 않는다.
참조는 기존 객체 ID/$ref의 살아 있는 객체를 뜻하므로 값 snapshot이나 C# 메모리 ref로
자동 치환하지 않는다. 필요한 접근/수명 정책은 기존 runtime 문맥과 별도로 대조한다.

**구 reader 영향:** compound schema/저장 데이터 문법은 바꾸지 않았다. 직전116ccecd의
Info v1 parser는 기존 generated type 이름을 읽지만 복합 struct 생성을
`INFORMATION_CLR_FIELD`로 거절한다. 이 실제 게시본 기준 거절과 원문 불변을 재현했다.
첫 struct 지원 이전 parser는 generated type을 `TYPE`으로 거절한다. 기존 보관본을 고치거나
필드를 버려 열리게 하지 않는다. 새 소스 전체의 compiler 재검증과 새 산출물만 사용하며
구 DLL hot replacement·저장 데이터/서명 자동 migration·모든 구 reader 교환은 지원하지 않는다.

[신규44단계·재사용0의 마감 기록](VALIDATION_V666_INFORMATION_COMPOUND.md)을 따른다. 타입 선택 UI는 이 단위에서 수정하지 않는다.
M11/M12/M4는 새 회귀 없이 재개하지 않는다. 초기 빈 화면의 원인은 미확정이며 Linux
native/Chromium·교차 패키지와 실제 Windows/WebView2·모바일·물리 GPU/audio/IME·전체
UI/사용자 프로젝트 검증을 구분한다.
