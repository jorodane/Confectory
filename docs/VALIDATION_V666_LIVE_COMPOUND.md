# 실제 객체 compound 값 접근 검증

[지원 경계](V666_LIVE_COMPOUND.md)의 제품·검사를 고정한 뒤 `live-compound` 전용
suite로 최종 검증한다. 현재 결과는 실행 후 확정한다. 개발 재현을 최종 통과나 실제
Windows/모바일·전체 UI 수용으로 합산하지 않는다.

게시본 `2406f7ccd14d36399594a15d48b4f6aef47a09f8`에서 실제 native struct ABI는
컴파일되지만 live compound 생성이 거절됨을 CLR로 재현했다. 원본과 선언 data는 바꾸지
않았다. 기존 primitive/reference/enum descriptor와 참조를 포함해 native 값으로 생성할 수
없는 필드의 미지원 descriptor를 golden으로 보관했다. golden 입력과 실행 증거 재사용을
구분한다.

새 native 검사는 전이 값/enum 구조·타입 출처, 실제 Blueprint Read→Set→Read, 반복 호출과
독립 상속 인스턴스를 확인한다. caller 박스·Read 결과 박스·Access-write 결과의 변경이
실제 필드를 바꾸지 않으며 struct 내부 배열과 T[]는 같은 참조를 보존한다. 기존 native
default/null/NaN/enum 값은 정규화하지 않는다. raw ID/object[], 외부 nominal 타입,
같은 이름의 위조 필드 구조, 잘못된 배열·stale hash·mutable ref를 거절하고 유효한 저장소를
보존한다. 표시 변경은 값 계약을 유지하며 깊은 필드 변경은 pinned graph를 거절한다.
정확 복원은 원래 산출물과 실행을 회복한다. 등록된 중첩 타입 locator만 있는 경우의
명시 dependency 거절과 허용된 dependency의 별도 nominal assembly/원문 관측도 확인한다.
이 metadata 검사와 등록 외부 struct의 모든 runtime/UI 조합 완료를 구분한다.

UI는 원래 속성 검색·모바일 값 선택·native 입력·기존 전체 보기와 실제 compiler/engine을
사용한다. 새 읽기·가져오기·receiver·소비 연결·실행 attachment의 한 후보 Save, cold,
기존 C# 후속 편집/취소·저장 실패·Review/Confirm, 깊은 자식 원본의 Save 전·Review 뒤
충돌, 응답/영수증 유실과 늦은 입력을 검사한다. 기존 enum 경로도 같은 driver에서 검사한다.

최종 계획은 독립 LF16·CRLF15·관리 IPC1·새 패키지/전체 ZIP 복원/실패 수명10의42단계다.
기존 enum native/UI·primitive/ref runtime·authoring·정보 배열 회귀를 포함한다. 공개 SDK와
기존 NuGet seed만 사용하고 살아 있는 AI 계정·유료 호출·새 외부 접근을 사용하지 않는다.
최종 SHA·신규/동등 재사용·실패·증거·latest/rollback·정리·공간은 실제 실행 뒤 확정한다.
