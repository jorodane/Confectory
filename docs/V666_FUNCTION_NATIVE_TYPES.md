# v666 함수 상세 타입 선택 — 첫 계약

원본 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`dist/app.js::choosePropertyType`는 signature 문맥에서
`project.objects.filter(item=>propertyEntityTypes[item.kind])`를 사용한다.
기존 함수 상세창의 검색·종류별 목록·여러 개 선택을 현재 native 계약에 연결한다.
원본 ZIP SHA256: `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`.
사용자 결정인 정보별 struct, 종류별 enum, 모듈별 interface를 재사용한다.

직접 소유 정보의 **새 함수 첫 계약**에서 지원하는 정보·종류·모듈을 선택하고,
입력·out·반환 및 배열에 기존의 안정적인 generated CLR 이름을 저장한다.
표시명과 namespace/정의 ID로 검색하며, 생성할 수 없는 정의는 이유와 함께 비활성화한다.
이미 연결된 함수의 기본형 계약 변경은 기존의 명시적 구현/호출자 대응 절차를 유지한다.
기존 연결 함수의 모든 nominal ABI 변환 UI를 완료한 단위로 세지 않는다.
함수 카드/상세창의 CSS·크기·배치 및 기본형 선택을 유지한다.

`FunctionNativeTypes`는 현재 소유 namespace와 이미 선언된 직접 dependency만 열거한다.
등록만 된 namespace, 비공개 inline 정의를 선택 대상으로 승격하지 않는다.
지원하는 값 타입 closure와 module의 부모/includes/required function/default header를 확인한다.
본문을 읽거나 provider를 선택/실행하지 않고 객체도 만들지 않는다.
구형 enum의 고정 숫자 계약을 자동 생성하지 않으며 reference/function 필드를
값 snapshot이나 object로 대체하지 않는다. 미지원 async/공개 실행 module 계약도 유지한다.

선택 증거는 타입 shape와 정의 초안/실제 원본의 별도 해시, 실제 등록 manifest를 포함한다.
`function-add.nativeTypes`는 편집 후보/receipt에만 존재한다. `.celem` 문법이나 공개
IInvoke 계약은 추가하지 않는다. 새 nominal 함수 후보에는 정확한 선택 증거가 필요하다. 이전 미확정 nominal 생성 입력은
타입을 다시 선택해야 하며 자동 rebasing하지 않는다. 기존 저장 함수와 기본형 후보는 유지한다.

Save는 선택 증거를 현재 metadata와 비교하고 원자 후보만 checkpoint에 보관한다.
읽기 전용 타입 증거는 receipt에 보존하고 Review에서 다시 확인한다.
Confirm은 동일한 파일 lease 안에서 소유 파일의 기존 read checks와 등록 외부 파일의
absolute read checks를 확인한다. 외부 정의를 쓰기 대상으로 추가하거나 권한을 만들지 않는다.
후속 Save는 이전 타입 증거를 보존한다. 실패/취소/cold/응답 유실/늦은 이름 입력은
기존 입력·receipt 정산 체계를 재사용한다.

저장 문법은 늘리지 않는다. 기존 generated nominal 타입 이름과 v2 enum을 읽지 못하는
이전 parser/compiler/rollback의 제한은 그대로다. 자동 migration이나 C# 원문 재작성은 없다.
살아 있는 reference의 객체 수명·접근 경로, module의 async/공개 실행 계약,
기존 연결 함수의 고급 ABI 전환은 별도 잔여이며 이 단위의 완료 주장에 넣지 않는다.
초기 빈 화면 원인은 미확정이며 실제 Windows/모바일 기기·전체 UI는 검증하지 않았다.
