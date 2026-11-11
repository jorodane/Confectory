# 호출자가 제공한 실제 함수의 live 속성 접근

고정 [정보9행](V536_I5_6_REMAINING.md)의 함수 필드 생성 다음 단위다. 원래
`SchemaContracts.cs`의 `case "function"`은 선언 데이터의 구현 ID를 해당 함수 계약으로
검사한다. [native 함수 필드](V666_FUNCTION_FIELDS.md)는 원래 IInvoke/IAsyncInvoke를
사용한다. 이번 연결은 호출자가 이미 보유한 그 실제 interface 객체를 기존 ObjectModel
Create/Read/Set에 명시적으로 전달한다. 선언 ID를 provider로 해석하거나 구현을 선택하지
않는다. 정보별 struct·종류 enum·모듈 interface라는 사용자 결정을 유지한다.

`function-interface-live-v1` descriptor는 함수 ID, 원래 interface/assembly 이름, 정확한
매개변수 이름·타입·값/ref/out 역할·반환과 nominal signature 타입의 shape/source,
async의 원래 Task 결과 DTO·완료/실행 enum 계약을 담는다. 동기 공개 분기 함수는 기존
native IInvoke, async는 IAsyncInvoke다. 실제 객체에 원래 공개 실행 view가 있으면 같은
객체에서 명시적으로 사용한다. 별도 delegate, 결과 DTO 또는 분기 번호를 만들지 않는다.

함수 속성의 기존 CLR 경계는 `object`, 여러 값은 `object[]`다. 새 함수 핀 문법이나
ObjectModel 공개 메서드 서명을 만들지 않는다. 기존 property/property-set 노드도 그
경계를 사용한다. Read→Set→Read와 반복 실행은 같은 handle과 이전 출력을 보존한다.
단일 함수·배열은 원래 reference를 유지하고 일반 CLR strong reference/GC 수명을 따른다.
배열 alias를 통해 나중에 잘못된 함수가 들어오면 다음 Read가 거절한다. 함수 저장은
provider 메서드·property getter를 실행하지 않는다. 호출은 작성자가 명시한 C#에서만 한다.

Set은 기존 explicit owner·field hash를 요구한다. 다른 함수, 잘못된 메서드 계약,
구현 ID 문자열, null/잘못된 배열은 기존 값을 바꾸기 전에 거절한다. 미설정 필드 Read와
함수의 mutable ref cell도 거절하며 기본 provider를 만들지 않는다. 기존 native struct
내부의 nullable 함수 필드 규칙은 바꾸지 않는다. async는 원래 InvokeAsync와 결과 타입을
검사하며 동기 caller를 자동 대기·전환하지 않는다.

metadata는 기존 등록과 dependency로 선언만 읽는다. 함수 메서드가 사용하는 정보/종류/
모듈의 전이 source와 모듈 include/require/default 선언까지 관찰하며 구현 body나 provider
인스턴스를 읽지 않는다. property plan의 입력 변경 후보도 그 전체 source proof를 저장하고
Save 전 및 Review 후 최종 CAS에서 다시 확인한다. 일반 property 계약 후보에서 관측이
최종 lease로 전달되지 않던 결함도 수정했다. `propertySourceScope/propertySourceReads`를
원래 receipt에 보존하고, 같은 등록과 함수/graph에서 다시 유도한 경로·원래 hash만 허용한다.
소유 경로는 기존 readGuards에, 등록 외부 경로는 기존 CommitPlan의 읽기 검사에 전달한다.
누락/변조 receipt는 새 기준으로 재해석하지 않는다. 외부 locator는 읽기 권한을 추가하지
않고, 원문 C#·override 계약·소유권·원래 UI 배치와 Review/Confirm을 유지한다.

새 accessor는 `nativeFunction` 없는 옛 function descriptor를 계속 거절한다. 옛 accessor는
새 function descriptor도 지원하지 않는다. `object` ABI가 같다는 이유로 구 runtime의 실행
호환성을 주장하지 않는다. 기존 primitive/reference/enum/compound descriptor와 실행은
그대로다. 함수가 들어 있는 compound의 직접 live Read/Set은 기존 unsupported 경계를
유지한다. 자동 migration이나 provider/lease/Dispose 정책을 추가하지 않는다.

이번 단위의 종료 기준은 실제 함수/배열의 동일성·상태·GC·원래 출력/out/공개 분기/Task,
기존 property 노드 실행, 거절 경계와 source CAS, 기존 본문 UI의 취소/Undo/실패/재시작/
응답 유실/늦은 입력, 최종 LF/CRLF 및 새 패키지 전체 복원이다. 결과는
[전용 검증 기록](VALIDATION_V666_LIVE_FUNCTIONS.md)에 구분한다.

객체 참조 bridge/수명과 struct의 reference 필드, 선언 구현 ID와 실제 함수 handle을 잇는
명시적 인스턴스 binding은 같은 고정9행의 유한 잔여다. 임의 provider 조회·직접 부모/외부
쓰기·자동 migration을 필수 요구로 늘리지 않는다. M11/M12/M4의 완료 범위는 유지한다.
실제 Windows·물리 기기·전체 UI는 별도이며 초기 빈 화면의 원인은 미확정이다.
