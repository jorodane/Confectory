# 선택 callee ref→out과 private C# 본문 공동 저장

기존 고정7/8행의 직접 소유 동기 scalar C# 함수에서, 선택한 native callee의 원래 ref 하나를 out으로 바꾸는 명시 계획을 private 본문·보조 함수 편집과 함께 저장한다. 근거는 [원래 ref→out 계약](V666_NATIVE_REF_OUT.md), [private callee ref→값 단위](V666_PRIVATE_CALLEE_REF_VALUE.md), 원래 매개변수 영역 편집이다.

callee의 이름·자료형·수·순서·반환과 native 별칭을 유지한다. 기존 ordinary root call과 공유 caller 각각에서 원래 ref 입력 표현을 정확히 선택해 해제하며, 다른 입력과 기존 반환은 identity로 유지한다. 새 out은 자동 연결하지 않는다. caller 자신의 ref 계약·저장소 및 private 노드의 값 ABI는 유지한다. C# 본문과 보조 함수는 사용자가 명시한 텍스트로만 바꾼다. 할당 전 out 읽기는 기존 compiler에서 거절한다.

각 단일 계획을 원래 source에서 독립 검증하고 변경 callee와 그 원래 호출 관측을 내부 overlay로 결합한다. 저장 순서와 무관한 후보를 기존 한 Save·Review/Confirm·최종 CAS로 처리한다. mapping·caller·원래 입력 해제·source·native 별칭 증거의 누락/변조, 다른 역할/반환/타입 변경은 이 단위에서 거절한다. 권한·소유·external access·저장 문법·receipt 필드를 추가하지 않는다.

UI는 기존 C# Script 매개변수 영역과 호출 계약 갱신 선택을 사용한다. 거절된 입력을 bodyDrafts에 보존하고, 취소·Undo/Redo·첫 Save 전 재진입에서 명시 계획과 별칭을 유지한다. 원래 private frame, 경로, routes, 배치와 편집하지 않은 파일의 bytes·mtime을 보존한다.

검증 fixture는 원래115/ref40에서 명시 편집 후13/ref5로 실행된다. private 직접 호출19/ref5와 callee 직접 호출24/out6을 CLR에서 따로 확인한다. 원래 caller ref5가 새 out6으로 덮이지 않아야 한다. LF/CRLF·실패/재시도·응답 유실·충돌·늦은 입력·cold restore·새 package·전체 복원은 최종 검증 기록에 구분한다.

이전 게시본은 이 새 공동 계획을 거절한다. 이미 Confirm한 일반 source와 checkpoint 읽기 호환성은 별도 확인하며 자동 migration을 의미하지 않는다. 구 Reference reader 제약, 과거 초기 빈 화면 원인 미확정 상태와 실제 Windows/WebView2·물리 기기·전체 UI 미검증 한계는 유지한다.

잔여는 다른 callee 역할·반환·고급 ABI와 retained/opaque 및 외부 원본 관측의 명시 결합이다. optional 조합을 새 필수 범위로 늘리지 않고 기존 완료 단위·main·원본·보관 증거를 보존한다.
