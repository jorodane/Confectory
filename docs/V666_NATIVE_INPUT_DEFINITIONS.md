# 명시 native 입력 삭제·추가와 공유 caller 공동 저장

고정7/8행의 입력 정의 삭제·추가를 같은 함수에서 명시하고, scalar 반환을 유지하는 직접 소유 동기 native C# 함수2..8개와 일반 Blueprint 공유 caller를 한 후보/CAS로 저장한다.
각 함수는 단일 raw native target이다. 기존 값 입력을 삭제하고 새 scalar 값 입력을 남는 입력 뒤에 추가한다.
남는 입력의 공개/native 이름·타입·값 전달·상대 순서와 반환은 유지한다. 삭제와 이름/타입/역할 변환을 추측해 섞지 않는다.
상세창에서 기존 입력을 삭제하고 새 입력 이름·타입을 직접 선택한다. 호출 계약 창에서는 원래 연결의 정확한 해제와 새 JSON 값을 각각 명시한다.
남는 입력 연결·출력 소비자·caller 자체 ABI/profile·노드 ID·실행선·반환 연결을 유지하며 기존 연결을 새 입력으로 자동 복제하지 않는다.

C# 창은 남는 native 별칭과 새 입력의 선언을 표시한다. 사용자가 명시한 선언·본문을 원래 해시로 검사하고 Review/Confirm 뒤 반영한다.
본문·캐스트·기본값·입력 재배정을 자동으로 생성하지 않는다. 누락된 새 값이나 정확하지 않은 원래 연결 해제는 전체 거절한다.
검사는 long amount를 삭제하고 double real을 유지한 뒤 long step을 추가한다. nativeReal 별칭과 real 값1.25/2.5는 그대로다.
두 호출에 새 step 값5와7을 직접 선택하고 root 입력/앞 호출 결과의 원래 amount 연결을 각각 해제한다.
명시 본문은 provider 반환34→9, 공유 caller38→12를 실제 실행한다. helper와 비선택 C# 원문은 유지한다.

각 함수의 완전한 원래 계약·native 선언/본문·caller 선택을 먼저 독립 검증하고 공유 graph를 합친다.
누락/틀린 해제·새 값 누락/변조·기존 연결 재사용·남는 입력의 타입/이름/역할/순서 변경·출력 재대응·stale 원본은 전체 거절한다.
원래 receipt/version3 readGuards·후속 설명 Save·cold·최종 CAS와 Review/Confirm을 유지한다.
후속 설명 Save 뒤 인자 수가 같은 삭제/추가도 남는 식별자로 인증하며, 누락된 readGuards를 기존 단순 본문 그룹으로 오인해 건너뛰지 않는다. 원래 동의·기준 파일을 다시 추정하지 않는다.
공개 실행 분기·override/copy/opaque/private 문맥, 선택 native 함수 사이 의존성 및 다른 원본 import/등록 외부 결합은 이 단위에 포함하지 않는다.

같은 게시 세대의 저장·재편집·검토 기준이다. 구 Reference reader 제약이나 이전 authoring 세대로의 migration/downgrade는 바꾸지 않는다.
남은 고정7/8행은 기존 명세의 다른 실제 복합 계약/본문 편집, opaque/private C# 명시 계획,
선택 native callee 사이 의존성과 다른 원래 import/등록 외부 관측 결합이다. 가능한 타입·문맥 조합을 새 필수 항목으로 늘리지 않는다.
M11/M12/M4는 구체적 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface, 권한·원본 소유권·authored layout·기존 예산을 유지한다.
초기 빈 화면 원인은 미확정이다. 실제 Windows/WebView2·물리 기기와 전체 UI 전수 검증을 자동화 결과와 구분한다.
