# 명시 native 값 입력 삭제와 공유 caller 공동 저장

고정7/8행의 기존 입력 정의 변경·본문 편집 흐름을 직접 소유 동기 native C# 함수2..8개와 일반 Blueprint 공유 caller의 한 후보/CAS에 연결한다.
원래 단일 raw native target에서 scalar 값 입력을 삭제한다. 남는 매개변수의 공개/native 이름·타입·값 전달·상대 순서와 반환을 유지한다.
함수 상세창에서 입력을 삭제하고, 호출 계약 창에서 삭제한 입력의 원래 연결을 각각 명시적으로 해제한다.
남는 입력 연결과 출력 소비자·caller 자체 ABI·profile·노드 ID·실행선·반환 연결은 유지한다. 연결이나 새 값을 자동으로 추정하지 않는다.

C# 창은 남는 원래 native 매개변수를 표시하고, 사용자가 직접 선택한 본문만 별도 Review/Confirm 뒤 반영한다.
본문을 자동 재작성하지 않는다. 삭제한 변수를 계속 사용하는 C#은 compiler 검토에서 거절한다.
검사는 첫 long amount 입력을 삭제하고 남는 double nativeReal 별칭을 유지한다. 호출자 root 입력과 앞 호출 결과 연결을 각각 정확히 해제한다.
명시 본문이 남는 실수 값으로 계산해 실제 provider 반환34→9, 공유 caller38→10으로 실행된다. helper와 비선택 C# 원문은 보존한다.

각 함수의 완전한 원래 계약·본문·caller 선택을 먼저 독립 검증하고 공유 graph를 합친다.
누락/틀린 해제·남는 입력 재배정·출력 재대응·매개변수 타입/이름/역할/순서 변경이나 stale 원본은 전체 거절하고 입력을 보존한다.
원래 receipt/version3 readGuards·후속 설명 Save·cold·최종 CAS와 Review/Confirm을 유지한다.
공개 실행 분기·override/copy/opaque/private 문맥 및 선택 native 함수 사이 의존성 결합은 이 단위에 포함하지 않는다.

같은 세대의 저장·재편집·검토를 검증한다. 구 Reference reader 제약이나 이전 authoring 세대로의 자동 migration/downgrade는 바꾸지 않는다.
남은 고정7/8행은 아직 거절되는 다른 명시 계약/본문 공동 편집, opaque/private C# 명시 계획,
선택 native callee 사이 의존성과 다른 원래 import/등록 외부 관측 결합이다. 선택 가능한 모든 타입·문맥 조합을 필수로 추가하지 않는다.
M11/M12/M4는 구체적 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface, 권한·원본 소유권·authored layout·기존 예산을 유지한다.
초기 빈 화면 원인은 미확정이다. 실제 Windows/WebView2·물리 기기 및 전체 UI 전수 검증과 자동화 결과를 구분한다.

이 값 입력 삭제·본문 단위의 [최종 신규 46·재사용0 검증과 보관](VALIDATION_V666_NATIVE_INPUT_REMOVAL.md)을 마쳤다.
