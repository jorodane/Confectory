# 명시 native 값 입력 추가와 공유 caller 공동 저장

고정7/8행에서 직접 소유 동기 함수2..8개에 scalar 값 입력을 뒤에 추가하고 직접 일반 Blueprint caller와 한 후보/CAS로 저장한다.
기존 매개변수의 이름·자료형·값 전달·상대 순서와 반환은 유지한다. 새 입력은 scalar 값이며 역할·타입 교체/삭제를 같은 함수에서 추측하지 않는다.
각 구현은 원래 단일 raw native C# target이고 공개 실행 분기·상속/override·copy/opaque/private 문맥은 이 단위에 포함하지 않는다.

기존 함수 상세창에서 입력을 추가하고 새 이름과 타입을 직접 선택한다. caller의 기존 바인딩은 그대로 유지하고 추가 입력마다 JSON 값을 명시한다.
리터럴 타입을 검사하며 새 입력의 기본값이나 기존 바인딩 복제를 추정하지 않는다. 기존 출력 소비자와 caller 자체 ABI·profile·ID·경로는 유지한다.
본문은 기존 C# 창에서 직접 작성하고 저장한다. 원래 native 이름과 타입·순서는 헤더에 유지하고 새 입력만 뒤에 표시한다.
C# 본문을 자동 재작성하지 않는다. 테스트에서는 명시한 새 값5를 사용하는 본문을 직접 선택해 반환34→38, 공유 caller38→46을 검증한다.
선택 전 원문과 모든 비선택 C#은 보호하며, 선택한 본문만 별도 Review/Confirm 뒤 반영한다.

각 single의 원래 계약·native 헤더·선택한 본문·caller를 먼저 독립 검증한 뒤 공유 graph를 합친다.
본문/선언/이름/값/바인딩/hash가 맞지 않거나 명시하지 않은 새 입력이 있으면 전체 거절하고 입력을 유지한다.
후속 설명 Save·cold·Review/Confirm은 원래 receipt/read guards·최종 CAS를 유지한다. 원래 helper/선언·caller graph·native 헤더/본문 변경은 경합으로 거절한다.
원래 native 별칭 nativeAmount/nativeReal은 새 값 step을 추가해도 그대로이며, 선택한 본문은 이 이름을 직접 사용한다.

남은 유한 고정7/8행은 값 입력 삭제/정의·다른 계약 변경 결합, opaque/private 명시 C# 계획,
선택 native callee 사이 의존성과 다른 원래 import/등록 외부 관측 결합이다. optional type/context 조합을 필수로 늘리지 않는다.
이 제한된 추가 단위를 전체 계약 변경 완성으로 표현하지 않는다. M11/M12/M4는 회귀 없이 다시 열지 않는다.
정보별 C# 구조체·종류 enum·모듈 interface, 권한·override 계약·authored layout·기존 예산을 유지한다.
구 Reference reader 제약과 초기 빈 화면 원인 미확정, 실제 기기·전체 UI 전수 검증의 한계를 유지한다.

이 값 입력 추가·본문 단위의 [최종 신규 46·재사용0 검증과 보관](VALIDATION_V666_NATIVE_INPUT_ADDITION.md)을 마쳤다.
