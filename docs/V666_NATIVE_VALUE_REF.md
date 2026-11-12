# 원래 native C# 값→ref와 공유 caller 공동 저장

고정7/8행의 명시 역할 전환을 직접 소유 동기 scalar-return 기능2..8개와 직접 일반 Blueprint caller에 결합한다.
각 선택 구현은 기존 단일 raw native C# target이며 공개 실행 분기·상속/override 없는 경계를 유지한다.
매개변수의 원래 이름·자료형·수·순서·반환을 유지하며 값→ref만 한 방향으로 바꾼다.
C# 본문은 사용자가 선택한 원문을 검사하며 자동 재작성하지 않는다. 기존 로컬 helper는 읽기 의존성으로 보존한다.

기존 C# 창에서 값 매개변수에 ref를 명시하고 호출 계약 창에서 원래 입력 바인딩과 출력을 identity로 선택한다.
같은 타입의 실제 기존 바인딩이어야 하며, 리터럴을 ref로 바꾸거나 임시/기본 저장소를 생성하지 않는다.
예제는 caller의 기존 ref second 셀을 두 callee의 count에 연결한 채 값→ref로 전환한다.
caller 자체의 long/ref long→long 계약과 graph profile·바인딩·ID·경로를 유지한다.
provider 반환은38로 같고 반사 호출 인자 셀은5→38로 바뀐다. 공유 caller 반환은46→79, 원래 caller 셀은5→79다.
명시한 쓰기 전달 추가의 결과이며 원래 프로그램 결과 보존을 주장하지 않는다.

모든 기존 single 계획을 원본 기준으로 각각 증명한 뒤 공유 graph를 합쳐 한 Save/CAS로 보관한다.
같은 출력 목록이어도 명시한 출력 identity를 포함한다. 후속 Save·Review/Confirm·cold의 원래 receipt/read guards를 유지한다.
저장 실패·응답 유실·경합 때 입력과 checkpoint를 보존하며 C# UTF8 BOM·CRLF·bytes·inode·mode·mtime을 유지한다.
새 ref로 변경할 원래 바인딩이 constant인 경우는 실제 원래 value 실행의 유효성을 확인한 뒤 후보를 거절한다.
허용된 방향을 오류로 기대하던 기존 UI 입력은 실제 이름 변경 거절 사례로 바꾸며 기존 양방향과 ref→out UI를 회귀 검사한다.

남은 유한 고정7/8행은 out→ref, 값 입력 추가/삭제 등의 정의 결합, opaque/private 명시 C# 계획,
선택 native callee 의존성과 다른 원래 import/등록 외부 관측 결합이다. optional type/context 조합을 필수로 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface 설계와 권한·override 계약은 유지한다.
구 Reference reader 제약과 간헐 초기 빈 #app 원인 미확정 상태를 유지한다. 실제 기기와 전체 UI 전수 검증은 별도 잔여다.
