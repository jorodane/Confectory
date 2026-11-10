# 실제 객체의 정보 구조체 값 읽기·쓰기

고정 정보 편집9행에서 이미 생성되는 정보별 C# struct를 caller-owned 실제 객체의
compound 속성 Read/Set에 연결한다. 원본 v666 ZIP SHA256
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의
`propertyTypeChoiceObjects`/`choosePropertyType`, 기존 single/multiple 계약과
[정보 구조체](V666_INFORMATION_STRUCTS.md)·[중첩 값](V666_INFORMATION_COMPOUND.md)·
[배열 값 ABI](V666_INFORMATION_ARRAYS.md)의 같은 흐름이다. 정보는 struct, 종류는 enum,
모듈은 interface라는 사용자 결정을 유지한다. 화면 배치·문법·권한 정책을 추가하지 않는다.

직전 게시본은 해당 struct를 컴파일하지만 실제 ObjectModel.Create/Access는 compound를
거절한다. 이제 기존 generator가 표현하는 compound 값에 정확한 nominal CLR 타입과
`information-struct-live-value-v1`의 전이 값 타입 구조를 기록한다. 단일은 T, 여러 값은
T[]다. 필드/타입/소유 출처·기존 shape hash와 enum 멤버 숫자 계약을 사용하며 표시명·
아이콘·원문 source를 값 hash에 넣지 않는다. 깊은 필드 변경은 부모 속성 hash에 전파된다.
기존 primitive/reference/enum descriptor와 생성할 수 없는 참조·함수 포함 struct의
미지원 표시는 유지한다. 원문에서 지원하지 않는 필드를 버려 struct를 만들지 않는다.

runtime은 전달받은 값의 CLR 이름·assembly 이름·정확한 public struct 필드 구조와
배열 형태, 중첩 nominal 타입·enum의 타입 구조를 검사한다. 필드 getter·C# 본문·provider를
실행하거나 ID로 객체를 찾지 않는다. 단일 struct는 Set 입력과 Read/Access-write 결과에서
박스를 값 복사하므로 호출자가 보관한 박스나 이전 출력으로 실제 필드 저장소를 바꾸지
않는다. .NET의 [GetObjectValue](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.compilerservices.runtimehelpers.getobjectvalue?view=net-10.0)
값 복사를 사용하고 실제 CLR에서 박스 변경·재호출·이전 출력 보존을 검증한다.

이는 기존 C# struct의 얕은 값 복사다. 내부 배열은 같은 참조이며 여러 값 필드의 T[]도
같은 배열을 저장/반환한다. 배열 원소를 깊이 복제하거나 null 배열을 빈 배열로 바꾸지
않는다. unset 속성의 Read는 계속 오류이며 호출자가 명시한 default(T)의 Set은 기존
C# 기본값이다. 복합 struct 안의 null/NaN/enum 값 등은 이미 허용한 native C# 값 ABI를
유지한다. 선언의 SchemaContracts JSON 데이터 검증을 native 값에 새로 삽입하지 않는다.
최상위 enum 속성의 기존 활성값 검사와 primitive/ref 경로는 그대로다. JSON 데이터의
enum ID/참조/$ref를 이 native 값으로 묵시적으로 변환하지 않는다.

다른 nominal 타입, 같은 이름의 다른 필드 구조, 원시 ID/JSON/object[], 잘못된 vector,
null 값·비vector 배열과 stale 필드 hash는 대입 전에 거절한다. mutable struct field-ref는
추가하지 않으며 기존 general single bool/int/long의 실제 저장소 ref 계약을 유지한다.
인스턴스와 직접 보관한 배열의 변경은 호출자 소유 문맥이다. descriptor/런타임 표현을
새 권한 증명으로 취급하지 않는다. 등록·공개/override 계약·원본 C# bytes는 바꾸지 않는다.

전체 값 closure와 부모 정보 원본을 기존 속성 catalog·본문 후보 읽기 관측에 포함한다.
깊은 자식만 바뀌어도 Save/Review 뒤 최종 CAS는 원래 물리 source proof로 거절한다.
개인 입력·checkpoint·peer 원문을 유지하고 정확 복원과 새 명시 Review를 요구한다.
단일 후보 Save·cold·Undo/Redo·취소·응답 유실·늦은 새 입력과 기존 C# 후속 편집을 같은
경계에서 검사한다. 원본 UI의 검색·값 선택·전체 보기·기존 편집기를 사용한다.

자연적 지원 문맥은 native 정보 입력을 가진 직접 소유 함수와 caller-owned 실제 객체다.
Read→Set→Read의 정확한 값 시점과 이전 출력을 확인하며 별도 인스턴스는 독립적이다.
기존 native 타입 선택·생성 수/필드/읽기 예산과 pack assembly 경계를 유지한다. 이전
runtime은 이 compound 필드를 거절하며 구 reader/과거 DLL을 자동 migration하지 않는다.

살아 있는 정보 reference의 C# 접근 bridge, function 필드와 module async·공개 실행 결과의
contract-only closure는 같은 고정9행 잔여다. reference를 struct 복사로 바꾸거나 구현 ID를
delegate/provider로 조회하지 않는다. 현재 Information DLL/Function contract DLL 순환을
guard 삭제·동일 이름 타입 복제·assembly 병합으로 해결하지 않는다. M11/M12/M4는 실제
회귀 없이 다시 열지 않는다. 이 값 연결에는 새 사용자 정책 결정이 필요하지 않았다.
초기 빈 화면 원인은 미확정이며 실제 기기·전체 UI 완료와 구분한다.

독립 후속 조사에서는 `Information_Example`/`Contracts_Example`이라는 같은 이름의
선행 참조 계약과 실제 타입을 사용해 상호 참조 assembly의 컴파일/CLR 실험을 수행했다.
struct 데이터와 module instance를 담은 async 결과, 실행 분기의 왕복과 동기 호출의
CS0619 거절을 확인했고 런타임 사본에는 선행 stub를 넣지 않았다. 이 실험은 별도 prototype
증거이며 현재 generator·모듈 선택 UI·등록/CAS/기존 이름 전체에 연결한 제품 검증은 아니다.
모듈/함수 필드의 compile closure를 잔여로 유지하며 어려운 구현을 새 사용자 정책 결정으로
돌리지 않는다.

최종 신규/재사용·패키지/전체 복원·보관 결과는 [검증 기록](VALIDATION_V666_LIVE_COMPOUND.md)에서 확정한다.
