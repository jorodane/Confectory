# Scalar 속성 구조와 native 계약·본문의 공동 저장

고정7/8행에서 같은 정보 창의 속성 생성·삭제·값/이름/아이콘 편집과 명시 native 계약·본문 계획을 한 Save로 결합한다.
게시 aeb65b9의 직접 소유 scalar 속성 묶음과 native ABI/body/caller 묶음은 각각 유효하지만 결합은 거절된다.
이 거절의 재현과 최종 검증 결과는 별도 검증 문서에 기록한다.

분류 경계는 기존 단일 general bool/int/long/float/double/string 속성의 schema-field/name/icon/remove,
root data/unset와 sources:null인 typed-definition/legacy info-definition이다.
전체 선언의 기존64행 제한을 사용하고 native 함수 계획은2..8개, 소유 정보 설명·아이콘은 각각 하나까지다.
분류에서만 owner 행을 분리한다. InformationDefinitions의 원래 schema ID/hash·필드 계약·이름/아이콘·기본값·사용처,
중복/겹침·원본 관측과 출처 제한, 기존 함수/본문/호출 대응 검증 및 후보·checkpoint CAS는 유지한다.
필드 삭제와 다른 같은 필드 편집을 결합하거나 부적합 기본값을 자동 변환하지 않는다.

새 필드는 사용자가 명시 생성한 ID·이름·타입·기본값만 반영한다. 지운 필드는 해당 정의와 지역 표시/기본값만 제거한다.
다른 필드·참조·외부/부모 원본·비선택 C#은 보존한다. 기존 타입 선택창·C# 및 호출 대응 창을 사용하며 새 UI를 추가하지 않는다.
계약을 바꾸지 않는 명시 본문 그룹에도 같은 분류를 적용한다. owner 행을 넣기 전후 native/caller 후보 bytes는 같아야 한다.
저장한 그룹의 기존 후속 정보/함수 표시 편집에도 readGuards를 유지하며 최종 Review 뒤 원본 경합은 Confirm 전체 거절이어야 한다.

검사의 한 원래 조작은 Scale long→double(기본값7 보존), Gauge의 정확한64비트 기본값·이름·아이콘 편집,
Retired의 명시 삭제와 새 scalar 생성, 두 함수의 명시 out/return·native 본문·공유 caller 대응이다.
기존 Power와 Tree/Peer, 선택 밖 C#·등록 관측·소유권을 유지한다.
정상 저장·실행, stale/foreign/중복/겹침·범위 밖 계획 거절과 취소/Undo/Redo·실패/재시도·응답 유실·cold·경합·늦은 입력,
LF/CRLF와 새 package/전체 복원에서 해당 조작을 검증하면 이번 단위를 닫는다. 타입과 문맥의 모든 조합을 새 필수 항목으로 늘리지 않는다.

정보별 struct·종류 enum·모듈 interface, 공개 override 계약과 authored layout·권한·Review/Confirm·최종 CAS를 유지한다.
새 문법·receipt 버전·migration·새 grant/credential·과금은 없다. 저장 후 새 속성 구조/값까지 다시 결합하는 경계는 이번 최초 공동 Save 지원과 구별하며, 캡처 밖 후속 편집의 기존 입력 보존 거절을 완화하지 않는다. 같은 authoring 세대의 조합이며 구 reader downgrade를 보장하지 않는다.
Reference 구 reader 제약과 초기 빈 화면 원인 미확정, 실제 Windows/WebView2·물리 기기·전체 UI 전수 미검증은 구별한다.

남은 원래 고정7/8행의 다른 복합/중첩/array/reference 속성 구조, opaque/private 명시 C# 계획,
선택 native callee와 기존 import/등록 외부 원본 결합은 각각 별도 의존성·검증 경계로 유지한다.
외부 쓰기나 출처 증거를 추정하지 않으며 M11/M12/M4를 회귀 없이 다시 열지 않는다.

이 scalar 속성 구조·native 계약 공동 저장 단위의 [최종 신규 41·재사용0 검증과 보관](VALIDATION_V666_SCALAR_OWNER_CONTRACTS.md)을 마쳤다.

[정보 소유 영역의 거절된 Undo와 브라우저 입력 기록 분리](V666_OWNER_HISTORY.md)는 버튼에 전달된 키가 다른 scalar 입력의 native history로 흐르는 재현 결함을 다룬다. 함수·속성·헤더의 기존 snapshot/소유권/저장 보호와 텍스트 자체 Undo·전역 Ctrl+Y 정책을 유지한다. 다른 편집기·초기 빈 화면·실제 기기 및 고정7/8행 잔여는 구별한다.

[기존 typed 값과 native 계약·본문 공동 저장](V666_TYPED_VALUES_CONTRACTS.md)은 복합·목록·참조·함수·종류 기본값의 기존 편집을 같은 명시 native 후보와 결합하는 단위다. 필드 정의/구조 전환과 opaque/private·외부 write closure 잔여를 구별하며 원래 typed 검증·읽기 관측·Review/Confirm·CAS를 유지한다.
