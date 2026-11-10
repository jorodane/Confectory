# 종류 enum과 모듈 interface의 C# 연결

사용자는 정보 정의별 C# struct에 이어 종류는 enum, 모듈은 interface라고 확정했다.
[고정 정보 편집9행](V536_I5_6_REMAINING.md)의 타입 생성 흐름을 연결한다. 저장소 v666
ZIP SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의
`Confectory-v666/dist/app.js::propertyEntityTypes`는 Enum과 EnumValue를 구별하고,
`propertyTypeChoiceObjects`/`renderFeatureDefinition`은 정의를 타입으로 선택한다. 기존
`EnumDefinition`/`SchemaContracts`의 항목 ID와 모듈 require/default/includes 계약을 유지한다.
실행 분기의 Result enum과 정보 종류를 합치지 않는다.

종류는 기존 정의 ID의 public C# enum(int)으로 생성한다. `information-enum-int32-v1`은
항목의 고유 ID에서 C# 멤버명을 만들며 표시명이나 행 위치를 정체성으로 사용하지 않는다.
기존 저장값은 여전히 opaque 항목 ID 문자열이다. 별도 `editorEnumNumbers`에 ID→양수
int32 예약표를 저장하고 profile `nominal-members-native-v2`로 명시한다. 0은 기존 미선택
ID `""`이며, ToId/FromId는 정확한 대응만 허용한다. 삭제된 ID/숫자는 활성 enum 변환에서
거절하고 예약표에 남겨 재사용하지 않는다. 이름·아이콘·순서 변경은 번호와 타입 shape를
바꾸지 않는다. 항목 추가/삭제는 생성 enum과 의존 계약을 재검사한다.

기존 v1 정의를 읽거나 빌드한다고 숫자를 임의로 부여하지 않는다. 소유 종류 헤더의
`고정 enum 숫자 계약 준비` 또는 명시 항목 저장이 원래 항목부터 예약하고 새 항목에
다음 번호를 배정한다. 임시 저장과 compiler Review→Confirm은 기존 원자 저장/CAS를
그대로 따른다. 소비자의 선택 ID·원문 C#·정의 ID를 바꾸지 않는다. 읽기 전용 부모/참조/
외부 원본에는 준비 동작을 제공하지 않는다. 잘못된 예약표·중복/0/소수/누락 번호는
자동 복구 없이 거절한다. 활성/과거 ID 합계16384개·숫자표1MiB·int32 한도를 명시 검사한다.

정보 struct의 단일 종류 필드는 정확한 enum 타입을 포함한다. primitive/compound-only
기존 source/shape는 유지하고 enum 포함은 `information-struct-nominal-v1`을 쓴다. 함수의
입력·반환과 pack별 타입 DLL/compiler/link는 같은 nominal closure를 사용한다. 별도
readonly `informationClr` 질의는 schema/enum/module의 타입 source·멤버/메서드·관측
해시를 제공한다. 기존 `informationStruct` 질의는 schema 전용 계약을 유지한다.

모듈은 `module-interface-basic-v1`의 public C# interface로 생성한다. 상속/includes의
require 함수 ID에서 안정적인 메서드명을 만들고 기존 입력·ref/out·반환 계약을 그대로
투영한다. 상속/includes의 요구는 이 interface에 평탄화하며 별도 CLR interface
상속이나 자동 upcast는 만들지 않는다. 첫 범위는 동기 기본형/배열 함수다. default가 실제 요구 함수와 같은 계약의
implementation인지 확인하지만 provider를 선택하거나 실행하지 않는다. 실제 interface
구현은 사용자가 작성한 객체이며, 권한·배정이나 implicit provider 객체를 만들지 않는다.
async/공개 실행 분기/정보 nominal 요구 함수는 현재 profile에서 명시 거절하며 원래
계약을 기본형으로 바꾸거나 메서드를 생략하지 않는다. 필요 없는 조합별 migration을
새 필수 잔여로 늘리지 않고 기존 모듈의 실제 고급 계약 흐름에서 후속으로 다룬다.

같은 계약 C# 본문 후보도 원래 관측한 enum/module/상속 정의를 사용한다. Save 전 원본
변경과 Review 뒤 변경은 원래 read guard와 최종 CAS로 거절한다. 외부 등록·dependency·
소유·override 계약·기존240 read-write/2048 known-unit·64-member Review·선택 타입256/
유효 필드256/모듈 메서드256 예산은 유지한다. 자동 source 재작성·저장값 치환·DLL hot
replacement·권한 변경·저장 데이터 migration은 없다.

**호환성:** legacy v1 종류의 ID 데이터는 계속 읽는다. native 사용은 명시 준비가 필요하다.
직전346b4e9c는 native 연결을 `INFORMATION_CLR_TYPE`으로 거절하며 원문을 바꾸지
않는다. 구 v1 종류 검증도 v2 profile을 허용하지 않는다. 첫 정보
타입 지원 이전 parser는 generated type을 읽지 못한다. 보관본을 수정해 호환되는 것처럼
만들지 않는다. 준비/확정 전에 구 reader 영향을 표시한다. 일반 기본형 프로젝트·기존
primitive/compound struct의 생성 source/hash에는 새 nominal 타입을 강제하지 않는다.

남은 고정9행은 타입 선택 UI의 native 계약 편집 연결, reference의 객체 정체성/실제 접근·
수명, multiple/함수 필드와 고급 Blueprint 값/핀 대응이다. reference를 struct snapshot이나
C# 메모리 ref로 바꾸지 않는다. 모듈의 고급 요구 계약은 위 명시 경계다. M11/M12/M4는
회귀 없이 재개하지 않는다. 초기 빈 화면 원인은 미확정이며 Linux native/Chromium과
교차 패키지/복원 검증을 실제 Windows/WebView2·모바일·GPU/audio·전체 UI 검증과 구분한다.

[신규47단계·재사용0 마감 검증·보관](VALIDATION_V666_NAMED_CLR.md)을 따른다.
