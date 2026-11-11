# Blueprint 계약과 native 본문의 같은 Save

고정8행의 원래 조작은 같은 정보 창에서 실제 편집한 여러 함수의 계약·본문을 공유 caller와
함께 저장하는 흐름이다. [잔여 대조](V536_I5_6_REMAINING.md)와 [원래 조작 표](V536_I5_6_RESIDUAL_RECONCILIATION.md)를
기준으로, 게시74694344에서 한 ordinary Blueprint 함수의 값 입력 C# 이름 변경과 다른
native 함수의 직접 본문 편집은 각각 유효하지만 공동 후보만 거절하는 것을 재현했다.
[직전 native 이름·본문 결합](V666_NAMED_BODY_GROUP.md)을 다시 구현한 것이 아니라,
서로 다른 기존 편집 경로를 같은 후보에 결합하는 한정 단위다.

지원은 직접 소유 동기 scalar 함수2~8개에서 적어도 한 import 없는 단일 ordinary Blueprint
구현의 공개 값 입력 이름과, 다른 함수의 import 없는 단일 native 본문을 함께 편집하는 경우다.
이름 편집은 기존 before/args 명시 대응과 위치별 타입·역할·수·반환을 유지한다. native 쪽은
공개/native 선언을 그대로 두고 사용자가 직접 작성한 텍스트만 선택한다. 공유 caller는 기존
직접 소유 sync call/export graph로 제한하고 private/code/whole/copy/후처리·지역값/별칭 및
외부 쓰기를 암묵 허용하지 않는다. 같은 계약 native 그룹과 기존 Blueprint/ref dispatcher는 유지한다.
기존64-member/target/source budget과 소유권·override 계약·Review/Confirm·최종 CAS를 보존한다.

`InformationFunctionMixedBodies`는 전체 원래 관측에서 기존 native body closure와 Blueprint
계약 closure를 각각 검증한 뒤 기존 내부 overlay/merge에 전달한다. 역순으로 준비해도 같은
후보·원래 hash여야 하며 중간 결과는 저장하지 않는다. 자동 C# 재작성·타입 변환·값/출력 추측·
새 ID/권한을 추가하지 않는다. UI는 기존 상세창의 명시 **C# 이름 편집**과 native 본문 편집을 사용한다.
표시 이름 metadata와 C# 계약 이름을 혼동하거나 새 제어·레이아웃을 추가하지 않는다.

예는 Blueprint 공개 amount→leftAmount에 기존 입력을 대응하면서 다른 native 본문을 덧셈에서
뺄셈으로 직접 편집하는 경우다. Blueprint C# 기록의 원문·native code 핀 선언과 반환/소비자,
함수·본문·노드 ID·기존 실행선을 유지한다. root/header·공유 caller의 이름 대응과 기존 정의 hash는
필요한 부분만 갱신한다. 원래 실행40, 공동 편집 실행30을 실제 프로그램으로 확인한다.

기존 단순 leaf 문맥의 추가 body readGuards가 비어 있을 수 있다는 정책을 유지한다. 실제
편집한 함수·구현/header·graph·native 본문은 원래 write CAS로 보호하고 Confirm은 현재 물리
원본을 복사해 검증/컴파일한다. 모든 미편집 원본 공백까지 새 raw-byte lease로 묶지 않는다.
추가 읽기 guard가 필요한 기존 문맥을 이번 혼합 경로에 자동 포함하지 않는다. 본문 계획 전체를
제거하면 기존의 유효한 이름 편집 경로로 돌아가며, 남겨진 계획의 필수 필드 누락과 구별한다.

[최종 검증](VALIDATION_V666_MIXED_FUNCTION_BODIES.md)은 정/역순·원래 hash·명시 대응·거절,
실제 UI 취소/Undo/cold·쓰기 실패·source 충돌·응답 유실·늦은 입력과 후속 Save·Review/Confirm,
저장된 caller의 읽기 전용 표시 전달과 실제 실행을 신규/재사용·fixture 실패와 구분해 기록한다.

## 같은 유한 잔여

고정7행의 forwarded/opaque 및 다른 frame 계약·본문 closure와 고정8행의 이 단위 밖 명시
계약/본문·공유 caller/import 결합은 기존 잔여다. native 선언·타입/역할/입출력 구조 변경,
복합 문맥을 이번 단위의 지원으로 세지 않는다. 가능한 조합별 새 필수 목록으로 늘리거나
이미 완료한 M11/M12/M4·ordinary private/wrapper·같은 계약 native 저장을 다시 열지 않는다.

구 Reference TYPE 거절·optional 문자열 metadata 호환은 [기존 바이너리 증거](VALIDATION_V666_ARGUMENT_LABELS.md)를
따른다. 같은 게시 세대의 reader/authoring/runtime을 사용하고 소급 수정·자동 downgrade/migration은 없다.
초기 간헐 빈 #app 원인은 미확정이며 전송/재로드 관찰과 이미 재현한 module 실패와 구분한다.
실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·전체 UI 전수 검증은 별도다.

이 Blueprint 계약·native 본문 혼합 저장 단위의 [최종 신규 37단계·재사용0 검증과 보관](VALIDATION_V666_MIXED_FUNCTION_BODIES.md)을 마쳤다.
