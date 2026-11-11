# 정보 struct의 함수 필드

정보 `field ... single/multiple function <함수 ID>`는 기존 선언 데이터에서 해당 함수의
구현 ID를 보관하고 원래 함수 계약과 일치하는지 검사한다(`SchemaContracts.cs`). 이번
native 생성은 그 동일 함수의 C# 호출 계약을 필드 타입으로 사용한다. ID를 provider로
찾거나 등록·로딩·실행하지 않는다. 호출자가 이미 가진 실제 함수 객체만 명시적으로
대입한다. 선언 데이터/기본값의 구현 ID를 native 객체로 자동 변환하지 않는다.

`information-struct-functions-v1`은 기존 `Generation.ImportInterface`를 재사용한다.
일반/공개 분기 동기 함수는 원래 `IInvoke`, async 함수는 원래 `IAsyncInvoke`다. 공개
실행 결과는 기존 import처럼 명시적 `IExecutionInvoke` view로 호출한다. 별도 delegate
서명·복제 DTO·분기 enum·default provider를 만들지 않는다. async 필드의 native Invoke는
기존 Obsolete(error=true) 계약으로 오류를 낸다. 자동 대기나 caller 전환은 없다.

필드의 native ID·이름/출처·단일/배열 구분과 함수 ID를 보존한다. 함수가 다른데 매개변수
타입이 같아도 다른 nominal interface이며 암시적 대입은 거절된다. struct를 복사하면
함수 객체의 reference는 그대로다. 함수 배열은 기존 C# 배열 reference를 유지한다.
상태 있는 같은 provider를 호출하며 GC의 일반 strong reference 수명을 따른다. 생성기가
registry에 객체를 붙잡거나 소유/Dispose/lease/취소 정책을 추가하지 않는다. 기본 함수
필드와 배열은 C#의 null이며 자동 기본 구현은 없다. native C# null을 선언 JSON 규칙으로
정규화하지 않는다.

함수 필드는 inline 정보 값이 아니라 interface reference다. 값 필드의 배치를 생성한 뒤
그 함수 서명의 nominal 타입을 관찰하므로 자기 정보 struct를 입력·출력으로 쓰는 callback도
지원한다. 실제 compound 값 필드의 순환은 기존 Structural cycle 거절을 유지한다. 함수
reference의 shape는 함수의 원래 생성 계약·signature 타입명·async completion ID를
포함한다. 함수 메서드가 사용하는 정보 타입의 배치 자체를 필드에 복제하지 않는다.
그 타입의 모든 source를 별도로 읽고, 전체 정보/함수 source를 기존 2단계 DLL 컴파일
키에 넣어 깊은 타입 변경을 무효화한다. source guard도 전체 closure를 관찰한다.

[모듈 계약에서 검증한 컴파일 방식](V666_MODULE_FLOW.md)을 재사용한다. 동일 assembly/
namespace/type 이름의 임시 nominal 선언으로 실제 함수 계약을 먼저 컴파일하고 실제
정보 DLL을 생성한다. 링크·catalog에는 실제 DLL만 전달한다. 구현의 선택·권한·override
계약·원래 C# bytes는 바꾸지 않는다. 등록 외부 함수와 그 서명 타입은 각 원래 source의
명시 dependency를 검사한다. 역방향 접근을 추정하지 않는다. 기본형/compound/enum/
ordinary module의 기존 source/profile/hash를 유지한다.

기존 같은 계약 본문 편집은 관찰된 함수 선언을 원래 Roslyn 후보에 포함한다. 타입
선택 증거에도 해당 함수 source/manifest를 넣어 이름/서명/분기/completion 변경을 Save
전·Review 뒤 최종 CAS에서 검사한다. 원래 Review/Confirm·원자 checkpoint·취소·Undo/
Redo·재시작·늦은 입력·응답 유실 복구를 재사용한다. 새 UI 배치/권한은 만들지 않는다.

이 단위의 종료 기준은 같은/등록 분리 pack의 실제 함수 handle·배열·상태·GC 유지,
원래 반환/out/분기/async 결과, 자기 타입 callback 및 암시적 오배정/동기 호출/inline 순환
거절, 저장 수명·원문 CAS, LF/CRLF와 새 패키지 전체 복원 검사다. 검증 결과는
[마감 기록](VALIDATION_V666_FUNCTION_FIELDS.md)에 구분한다.

살아 있는 객체의 reference는 실제 객체 핸들 의미이고 정보 struct는 값 의미다. 둘을
snapshot 복사로 합치지 않는다. ObjectModel live 함수 속성 및 함수가 들어 있는 compound
값의 직접 Read/Set은 별도 accessor/binding 계약까지 준비되기 전 종전 unsupported
표현을 그대로 유지한다. 직전 게시 패키지의 descriptor를 실제 질의하여 golden으로
보존하고, 새 native 함수 필드 지원이 이를 잘못 지원 가능으로 표시하지 않는지 검사한다.
참조 bridge/수명·reference 필드와 선언 구현 ID→실제 함수 handle의 명시적 live 연결은
같은 고정9행의 유한 잔여다. 임의 provider 선택/ID 조회/자동 migration을 완료 조건에 넣지
않는다. 실제 Windows·물리 기기·전체 UI는 별도이며 초기 빈 화면 원인은 미확정이다.

이 한정 범위의 [최종 신규 24단계·동등 재사용 14단계·총 38단계 검증과 보관](VALIDATION_V666_FUNCTION_FIELDS.md)을 마쳤다.
