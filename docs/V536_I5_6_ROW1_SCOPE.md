# I5-6 1행의 마지막 수용 범위

고정 9행의 1행에서 이번에 마감할 사용자 조작만 적는다. 원본 v536 및 기존 엔진 계약으로 결정할 수 있는 미연결 구현이며 사용자에게 새 언어/권한 설계를 요청할 사안은 없다.

| 기존 화면의 조작 | 저장 후보가 해야 할 일 |
|---|---|
| 함수 상세창에서 property 읽기/쓰기/필드 참조의 수신자로 쓰이는 object 입력을 삭제하거나 다른 타입으로 바꾸고, 현재의 다른 object 입력을 선택 | propertyOwner·field·필드 hash·accessor·읽기/쓰기 시점을 보존하고 수신자 값만 명시 대응한다. null/리터럴이나 다른 타입으로 추측하지 않는다. |
| property 쓰기 값에 쓰이는 입력을 삭제/타입 변경하고 대체 값/입력을 선택 | 수신자·필드 계약과 결과/참조 사용처는 유지하고 해당 쓰기 값만 대체한다. |
| 기존 bool branch 또는 실행 enum code 노드의 값 인자가 읽는 입력을 삭제/타입 변경하고 대체를 선택 | C# 본문·helpers·enum 식별자/값·branchOwner·연결·계속 경로를 그대로 두고 값 바인딩만 대체한다. 새 분기/반복 의미를 추가하지 않는다. |
| 기존 소유 call의 bool branch, serial After, execution-enum After 값 인자에서 같은 입력 대응 | callee 서명·typed import·public output/SourceContext·후처리 C#·enum·출력/실행 연결을 그대로 두고 값 인자만 대체한다. 같은 callee의 변경하지 않는 ref/out 인자도 보존한다. |

자기 호출 생성은 기존 `BlueprintCall.Prepare`가 이미 거절한다. 그것을 새 지원 기능으로 추가하지 않는다. callee/ref 역할 변경, 전체 본문 저장소, 등록/상속·복사·중첩 문맥은 기존 4~7행의 별도 항목이며 이번 1행을 계속 늘리는 잔여로 재분류하지 않는다.

완료 조건은 위 네 조작의 실제 엔진·원본 UI 연결과 정상 Save/Undo/취소/충돌/응답 유실/재시작/Review·컴파일 Confirm, 원문·입력 보존이다. property descriptor의 원래 소유 선언/상속·schema 및 고정 accessor/등록 manifest를 읽기 전용 관찰에 묶고, 원본이 바뀌거나 증거가 빠지면 전체 후보를 거절한다. getter 실행이나 provider body 읽기를 통해 계약을 추정하지 않는다.

이 단위 이후에는 3행의 `adaptOutput`, `outputCreates/removeOutputs/outputRoutes`와 caller `remap.outputs`를 명시 후보/CAS로 결합한다. 출력 값 바인딩의 대응과 출력 타입·추가삭제·반환 계약 변경은 구별한다. 기존 9행·레이아웃·권한을 확장하지 않는다.
