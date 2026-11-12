# 명시 native 입력 정의·타입 공동 저장

고정7/8행의 입력 정의와 scalar 타입 편집을 같은 함수에서 명시하고, scalar 반환을 유지하는 직접 소유 동기 C# 함수2..8개와 일반 Blueprint 공유 caller를 한 후보/CAS로 저장한다.
각 구현은 원래 단일 raw native target이다. 기존 값 입력을 삭제/추가하면서 남는 이름의 scalar 타입도 바꾼다.
타입을 유지한 입력의 연결과 남는 입력 이름의 상대 순서, 반환·출력 소비자·caller 자체 ABI/profile·노드 ID·실행선은 유지한다.
새 입력은 남는 입력 뒤에 추가한다. 기존 입력의 이름/역할/순서 변경이나 저장소 의미를 묵시적으로 추측하지 않는다.

기존 상세창에서 삭제/추가·타입을 직접 선택한다. 기존 호출 계약 창에서 새 타입과 추가 입력의 JSON 값을 각각 선택하고,
제거하거나 타입을 바꾼 원래 바인딩을 각각 정확히 해제한다. 새 기본값·기존 값 재사용·변환 함수를 생성하지 않는다.
기존 C# 창에 표시된 선언에 맞춰 사용자가 선택한 본문을 직접 저장하고 Review/Confirm 뒤 반영한다.
원래 native 이름을 새 타입으로 추측 변환하거나 원문을 자동 치환하지 않는다. 모든 선언·본문은 원래 해시로 검증한다.

검사는 long amount 삭제, real의 double→string 변경, long step 추가를 같은 함수에서 선택한다.
원래 root 입력/앞 호출 결과와 real 리터럴1.25/2.5를 각각 명시 해제하고, 두 문자열 첫째😀/second 및 새 숫자5/7을 직접 지정한다.
선택한 본문 real.Length+step과 그대로인 helper를 실제 실행해 provider 반환34→13, 공유 caller38→16을 확인한다.
선택 전 원문과 helper/비선택 C# bytes는 보존하며 선택한 본문만 명시 텍스트로 반영한다.

각 함수의 완전한 원래 계약·native 선언/본문·caller 선택을 먼저 독립 검증하고 공유 graph를 합친다.
누락/틀린 해제·새 값/대체 값 누락이나 틀린 타입·암묵적 기존 바인딩 재사용·출력 재대응·stale 원본·잘못된 C#은 전체 거절한다.
원래 version3 receipt/readGuards·후속 정보/함수 설명 Save·cold·Review/Confirm·최종 CAS를 유지한다.
이전 입력 정의 단위에서 수정한 동일 인자 수의 retained-source 인증을 그대로 사용하며 원래 기준 파일·동의를 재구성하지 않는다.

공개 실행 분기·out/ref·override/copy/opaque/private 문맥, 출력/반환 계약의 동시 변경과 선택 native 함수 사이 의존성은 이 단위에 포함하지 않는다.
남은 고정7/8행은 다른 실제 복합 계약/본문 편집, opaque/private C# 명시 계획, 선택 native callee 의존성과 다른 원래 import/등록 외부 관측 결합이다.
가능한 타입/문맥 조합을 새 필수 목록으로 늘리지 않고 M11/M12/M4를 회귀 없이 다시 열지 않는다.
정보별 구조체·종류 enum·모듈 interface, 기존 권한·원본 소유권·authored layout·예산을 유지한다.
같은 게시 세대의 저장·재편집·검토 기준이며 구 Reference reader 제약이나 이전 authoring 세대로의 migration/downgrade를 바꾸지 않는다.
초기 빈 화면 원인은 미확정이다. 실제 Windows/WebView2·물리 기기 및 전체 UI 전수 검증을 자동화 결과와 구분한다.

이 입력 정의·타입·본문 단위의 [최종 신규 46·재사용0 검증과 보관](VALIDATION_V666_NATIVE_INPUT_MIX.md)을 마쳤다.
