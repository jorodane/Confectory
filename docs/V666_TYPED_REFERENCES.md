# 정보별 native 참조 struct와 타입 선택

고정 [정보9행](V536_I5_6_REMAINING.md)의 typed reference ABI·reference 필드·타입 선택을
연결한다. 사용자는 정보 정의마다 C# struct, 종류는 enum, 모듈은 interface로 결정했다.
원본 v666 ZIP `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의
정보 값/참조 구분과 기존 `SchemaContracts`·[실제 인스턴스 bridge](V666_REFERENCE_BRIDGE.md)를
따른다. 기존 값 struct 이름과 원본 C#을 바꾸거나 객체 ID를 실제 객체로 조회하지 않는다.

`Confectory.Reference.<pack symbol>.<information symbol>`은 정보별 **readonly struct**다.
`information-reference-struct-v1`의 public readonly `Target`/`Owner`는 원래 실제 handle과
object/concept owner를 보유한다. owner는 접근 주소이며 새 권한을 부여하는 토큰이 아니다. private 생성자와 명시적 `Bind(target,contract)`를 사용한다.
이 factory는 기존 ObjectModel v1/v2 bridge와 같은 bounded 선언/hash·schema 계보·필드
검사를 생성된 contract 안에서 수행한다. 해당 정보 ID의 `information-object-reference-v1`
계약만 허용하며 값·getter·provider를 읽거나 실행하지 않는다. readonly 질의
`informationReferenceType`은 이 타입·shape·C# source와 원래 source 관측을 반환한다.
기존 `informationReference`의 runtime descriptor/envelope와 의미는 그대로다.

복사한 참조 struct도 같은 객체를 보유한다. CLR strong reference와 GC 수명이고 전역
registry·lease·Dispose·소유 이전·alias retargeting은 없다. C# `default`는 `IsBound=false`인
unbound carrier이며 인스턴스를 만들지 않는다. 정보 값과 참조, 서로 다른 정보 ID 사이에
암묵적 변환을 만들지 않는다. 부모 정보로의 참조 view도 실제 handle을 그 부모 계약에
명시적으로 Bind한다. source 변경은 기존 alias를 소급 취소하지 않고 새로운 binding에서
명시한 버전 snapshot을 검사한다. ID/$ref/JSON/snapshot으로 native handle을 만들지 않는다.

정보 값 struct의 reference 필드는 해당 정보의 참조 struct, multiple은 그 배열이다.
`information-struct-references-v1`은 원래 field ID/이름/출처를 유지한다. 자기 자신 또는
서로 참조하는 필드는 값의 inline 재귀 포함이 아니다. compound의 실제 값 순환과 원래
정보 선언 검증은 계속 거절한다. 배열은 원래 C# 배열 reference를 보존하며 value struct의
일반 필드는 값 복사를 유지한다. default carrier/배열을 살아 있는 객체나 editor 기본값으로
정규화하지 않는다. 정보 값과 같은 정보 참조를 함께 쓰는 계약도 별도 source와 같은 pack
Information DLL에 연결하고 후보 compiler와 실제 module/function 계약에서 같은 타입을 쓴다.
등록된 두 pack의 상호 참조는 기존 임시 nominal 선언→실제 DLL 연결을 사용한다. 최종
링크에는 실제 DLL만 넣고 값 포함의 순환은 계속 거절한다. 양방향 pack dependency도 원래
선언이 필요하다. C# `ref`/`out` 전달 역할과 정보의 객체 reference 의미를 혼동하지 않는다.

기존 ObjectModel의 reference 속성은 object/object[] ABI 그대로이며 typed carrier로
묵시적으로 변환하지 않는다. `Target`/`Owner`로 기존 checked Read/Set을 명시적으로
호출한다. 기존 live compound accessor에서 reference를 담은 native 값의 거절도 유지한다.
그 profile과 descriptor/hash를 자동 승격하거나 새 data migration 요건을 만들지 않는다.
참조 인자를 가진 함수 handle은 새 nominal readonly carrier 모양을 검사하며 provider를
생성·선택하지 않는다. 기존 일반/enum/compound/function descriptor는 같은 계약을 유지한다.

원래 상세창·타입 popup에서 정보 값과 **정보 참조**를 별도로 고른다. 정보 reference 배열도
기존 여러 개 선택을 사용한다. 원래 catalogue 행의 ID/값 타입을 유지하고 reference 선택을
별도 member로 내보내므로 기존 값 선택을 참조 선택으로 바꾸지 않는다. 새/기존 함수,
관찰된 Blueprint/C# frame은 기존 명시적 계약 대응과 source proof를 사용한다. 기존
namespace 등록/dependency·비공개 정보 제한과 256정의/선택 타입·64개 계약/240읽기 등의
예산을 유지하며 parent/외부 source 쓰기 권한은 추가하지 않는다. Save·Review·최종 CAS와
중단/취소/재시작/늦은 입력의 원자 저장은 원래 경계를 사용한다. source 문자열의 정보 ID를
추측해 권한을 만들거나 원문 C#·연결·override 계약을 자동 재작성하지 않는다.

새 reference 타입 이름을 구 parser는 읽지 못하고 새 field profile/타입 선택도 구 authoring
도구의 지원 범위가 아니다. 기존 기본형·값 타입 이름·descriptor/hash·저장 format은 유지한다.
같은 보호 초안 v2의 native proof marker를 사용하며 새 타입을 모르는 구 도구가 거절하는
경계를 없애지 않는다. schema 변경 후 기존 DLL/instance/저장 data를 자동 migration하지
않는다. 지원 범위는 이미 생성된 ObjectModel 실제 handle이다. custom 객체/ID 해석이나
외부 access grant를 추가하지 않는다. 실제 Windows·기기·전체 UI와 초기 빈 화면 원인은
별도이며 결과는 [검증 기록](VALIDATION_V666_TYPED_REFERENCES.md)에 구분한다.

첫 Confirm 전 본문 없는 생성 함수의 이름 후속 저장에서는 빈 original을 native 본문
원문으로 파싱하지 않는다. 정확한 missing baseline·같은 계약·본문 없는 원래 생성 그룹만
해당하며 native type proof/read scope는 그대로 보존한다. 본문 포함 그룹·계약 변경·기준선
변조를 그 경로로 통과시키지 않고 초안도 원문으로 승격하지 않는다.
