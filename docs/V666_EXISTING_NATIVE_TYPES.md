# v666 기존 정보 기능의 native 타입 전환

고정 수용 목록 9행의 함수 상세 타입 선택을 이어간다. 원본 v666 ZIP의
`dist/app.js::choosePropertyType` signature 문맥과 `renderFeatureDefinition`을 근거로,
기존 상세창의 검색·타입 선택·배열 표시를 재사용한다. 원본 ZIP SHA256은
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다.
정보별 struct·종류별 enum·모듈별 interface라는 사용자 결정을 유지한다.

이번 지원 범위는 **구현·호출·요구 계약이 없는 직접 소유 정보 기능**의 동기 일반
입력/out/반환 타입 전환이다. 기본형과 지원되는 nominal 타입·배열 사이를 선택한다.
원래 함수 ID와 소유 파일을 유지하고 기존 값·본문·연결을 자동 변환하지 않는다.
연결된 함수의 기본형/기존 명시적 대응 절차는 유지하며, 연결된 nominal 전환과
상속·비소유 원본·async/공개 실행 계약까지 지원했다고 세지 않는다.

`FunctionNativeEdits`는 소유 namespace와 이미 선언된 직접 dependency의 공개 선언,
그 선언이 참조하는 header closure 및 manifest를 관찰한다. implementation/function,
parent, import, require/default/provide, function field, 다른 소유자의 contain이 선택
기능을 사용하면 전환을 거절한다. 등록만 된 namespace를 새로 권한 범위에 넣지 않는다.
현재 receipt 예산 안에서 최대 200개 header를 관찰하며 초과 시 입력을 보존해 거절한다.
선택한 값 타입은 기존 `FunctionNativeTypes` shape/source 증거를 그대로 사용한다.

`native-function-edit` 입력은 function-edit 후보에 `nativeTypes`를 전달하며,
`$function:<ID>` 증거가 사용처 부재와 모든 관찰 원본/manifest를 묶는다.
Save 직전과 Review에서 사용처를 다시 확인하고 Confirm의 같은 파일 lease 안에서
관찰 버전을 확인한다. 중간에 소비자가 생기면 원자 후보 전체를 거절한다.
전환이 저장됐어도 Review/Confirm 전에는 첫 구현 작성을 막아 관찰 조건을 유지한다.
사용처 없는 선언 변경이므로 저장할 값이나 C# 본문을 폐기할 필요가 없다.

보호 초안은 기존 v2/profile을 사용한다. 이전 UI는 알 수 없는
`native-function-edit` 입력을 저장하지 못하며, 이전 타입 검증기는 알 수 없는
`$function:` 선택을 Review에서 거절한다. 구 reader를 실제 실행한 결과로 주장하지
않으며 구 parser/compiler의 generated nominal/enum 제한도 유지한다. 자동 migration은 없다.

Confirm 전 후속 Save와 늦은 입력은 살아 있는 원자 그룹의 읽기 증거를 상속한다.
Confirm이 그룹을 수락한 뒤에는 이전 receipt를 새 변경의 기준으로 재사용하지 않는다.
종전에는 같은 세션의 새 이름 Save가 확정 전 manifest 해시 때문에 거절되는 결함이
있었으며, 재현 후 활성 atomicEditGroup이 있을 때만 증거를 상속하도록 수정했다.

살아 있는 참조 접근은 `RuntimeObjectContracts`의 설명과 실제 runtime 객체/접근자 연결을
구분해야 한다. 선언 data/default를 runtime 객체 snapshot으로 쓰지 않는다. 모듈 async와
공개 실행 요구는 `ModuleInterfaces`의 동기 제한, `BlueprintAsync`/`BlueprintExecutionBranches`
결과 계약 및 호출자 연결을 함께 확장해야 하는 후속 범위다. 표현 방식에 대한 사용자
결정을 다시 묻거나 implicit blocking/caller 자동 변환을 도입하지 않는다.

실제 Windows/모바일 기기 및 전체 UI는 미검증이다. 초기 빈 화면의 원인은 미확정이다.
