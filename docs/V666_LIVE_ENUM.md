# 실제 객체의 종류 값 읽기·쓰기

고정 정보 편집9행에서 이미 생성되는 C# enum을 호출자가 제공한 실제 객체의 속성
Read/Set에 연결한다. 원본 v666 ZIP
`reference/site-ui/Confectory-Editor-Prototype-v666.zip`의 SHA256은
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이며,
`dist/app.js::choosePropertyType`의 종류 선택과 기존 `SchemaContracts`의 enum 멤버 ID
계약을 따른다. C# 표현은 사용자가 확정한 enum이다. 실행 시점과 이전 출력 보존은
[기존 속성 Set 계약](BLUEPRINT_PROPERTY_SET.md)을 유지한다.

`RuntimeObjectContracts`는 숫자 매핑이 확정된 enum 필드에 정확한 CLR 이름과 기존 pack
타입 assembly 이름, enum shape와 활성 멤버의 ID/숫자/CLR 이름을 추가한다. single은
해당 enum, multiple은 해당 enum 배열이다. 멤버 표시명·순서가 바뀌어도 이 값 계약은
변하지 않는다. 항목·숫자 계약이 바뀌면 필드 hash도 바뀌어 기존 node의 명시 재검토가
필요하다. 기존 primitive/reference descriptor와 숫자 매핑 없는 종류의 미지원 표시는
그대로이며, 조회 중 숫자를 부여하거나 원문을 저장하지 않는다.

ObjectModel의 checked Access는 원래 Instance/v1·v2 표현과 owner lineage·필드 ID/hash를
유지한다. enum 값은 CLR 타입의 이름·assembly 이름·int32 기반·전체 멤버 이름/숫자와
실제 값을 확인한다. 숫자·ID 문자열·다른 nominal enum·정의되지 않은 값·null을 변환하지
않는다. 배열은 정확한 CLR vector와 모든 원소를 대입 전에 검증하며 원래 참조를 그대로
저장/반환한다. 이미 반환된 배열을 새 필드 배열로 교체하지 않는다. 호출자가 공유 배열을
직접 잘못 변경하면 다음 Read가 거절하며 데이터를 자동 복구하거나 새 배열로 치환하지
않는다. enum의0은 기존 native enum 계약의 명시적인 Unselected 값이다.

인스턴스는 호출자가 기존 Create 또는 자신의 명시적 adapter로 제공한다. descriptor와
object[] 표현은 기존 caller-owned 값 계약이며 별도 권한을 부여하는 증명이 아니다.
선언의 data/$ref/implementation ID를 runtime 객체·provider·delegate로 자동 조회하거나
생성하지 않는다. unset을 선언 기본값으로 채우지 않는다. 다른 실제 객체는 독립 저장소를
유지하고, Read 노드에 도달할 때 현재 값을 한 번 읽는다. 앞선 enum 출력은 뒤의 Set과
다음 호출 후에도 보존한다. constrained enum에 무제한 mutable ref cell은 제공하지 않으며
기존 general single bool/int/long ref 계약을 유지한다.

본문 후보 검증의 property 의존성 loader도 enum 선언을 같은 읽기 범위에 포함한다.
새 권한이나 쓰기 대상은 추가하지 않는다. 원래 schema/enum/함수/구현/graph/record와
등록 증거, 한 후보 저장·Review/Confirm·최종 source CAS를 그대로 사용한다. enum의
표시명이나 주석만 바뀌어도 저장 때의 물리 source proof와 다르면 입력을 유지하며 거절한다.
정확 복원과 새 명시 Review 후에만 확인한다. 기존 public/override 계약과 authored UI의
배치·컨트롤은 바꾸지 않는다.

검증하는 자연적 문맥은 enum 입력/반환을 가진 직접 소유 함수와 caller-owned 실제
객체다. 원래 속성 검색·receiver/값 선택·모바일 UI에서 새 enum Read를 연결한다. 검사
fixture가 숫자 출력 보관을 위해 쓰는 enum→long 변환은 명시적인 C# 본문이다. 제품이
자동 변환하지 않는다. 기존 지역값 초기화는 기본형 상수만 허용하므로 enum 초기화 문법,
임의 기본값·숨은 저장소를 이 단위에서 만들지 않는다.

이전 runtime은 enum 필드를 거절한다. 저장된 멤버 ID/숫자 예약과 새 node/descriptor를
이전 보관본에 맞춰 바꾸지 않는다. nominal/enum의 구 parser·reader 제한, 자동 migration
없음과 현재 데이터 보호를 유지한다. source 복원·재검토·실제 실행 및 수명 검사는
[검증 기록](VALIDATION_V666_LIVE_ENUM.md)에 개발/최종·신규/재사용을 구별한다.

살아 있는 정보 참조의 나머지 타입/접근 연결, compound/function 필드와 모듈 async·공개
실행 결과는 기존 잔여다. `SchemaContracts`의 함수 필드는 구현 참조이며 이를 임의의
C# delegate로 바꿀 근거는 없다. module async·함수 필드는 기존 public FunctionResult/
ExecutionResult/IInvoke 타입의 contract-only closure를 필요로 한다. 현재 pack별
information DLL과 function contract DLL 사이의 의존성을 guard 삭제나 중복 타입 생성으로
해결하지 않는다. assembly 병합·새 provider 선택·소스 재작성 정책은 도입하지 않았다.
기존 동기 호출자의 명시 async 전환 전 오류 규칙과 M11/M12/M4 완료 경계도 유지한다.
이번 enum Read/Set에 새 사용자 정책 결정은 필요하지 않았다. 실제 기기·전체 UI와 초기
빈 화면의 원인은 별도이며 검증한 사실만 기록한다.

이 한정 범위의 [최종42단계(신규26·재사용16) 검증과 보관](VALIDATION_V666_LIVE_ENUM.md)을 마쳤다.
