# 공개 입력 이름·native 본문 저장과 기존 로컬 import

고정 [정보 편집8행](V536_I5_6_REMAINING.md)의 같은 정보 창·한 Save 흐름이다.
[잔여 대조](V536_I5_6_RESIDUAL_RECONCILIATION.md), [기존 native import 보존](V666_NATIVE_BODY_IMPORTS.md),
[명시 이름·본문 저장](V666_NAMED_BODY_GROUP.md)과 [기존 private caller](V666_NAMED_NESTED.md)를
기준으로 공개 값 입력 C# 이름과 직접 native 본문을 함께 저장한다. 원래 v666
`app.js::renderFeatureDefinition`/`openOwnFunctionPopover`의 화면을 사용한다.
새 import 편집기·레이아웃·권한·문법은 추가하지 않는다.

게시20a2a4e1에서 기존 로컬 helper를 호출하는 native 함수 두 개의 단일 이름/본문 후보와
실제 프로그램46은 유효하지만 공동 후보만 import 일괄 제한으로 거절됨을 재현했다.
직접 소유 동기 scalar 함수2~8개, 단일 native target과 기존 위치별 타입·역할·수·반환,
native 선언을 유지한다. 공개 값 입력의 C# 이름은 기존 before/args 명시 대응만 사용하고
본문은 사용자가 직접 작성한 텍스트를 선택한다. 표시 이름과 C# 식별자를 혼동하지 않는다.

기존 직접 로컬 import는 같은 namespace의 부모 없는 실제 소유 함수와 원래 typed 계약이
일치해야 한다. 이미 읽은 helper 선언·구현·본문·별칭과 그 의미는 그대로 유지하고,
helper를 쓰기 후보나 선택된 함수로 끌어들이지 않는다. 각 원래 명시 후보를 검증한 뒤
기존 overlay/merge와 한 CAS로 결합하며 정·역순 후보와 원래 hash는 같아야 한다.
네이티브 parameter나 import alias를 추측해 C# 원문을 재작성하지 않는다.

직접 편집하는 두 본문의 덧셈을 뺄셈으로 바꾼 예의 실제 실행은26이다. 원래 helper의
`value+3`·CRLF/한글·emoji 원문과 호출 alias, native 선언·함수/본문/노드 ID·기존 caller의
값/실행선·출력 소비자는 보존한다. helper source가 없어지거나 계약/소유권 관측이
일치하지 않으면 전체 거절하고 입력을 남긴다.

기존 version3 readGuards가 이미 관측한 owned source를 읽기 체크와 최종 source lease로
유지한다. helper는 새 쓰기 대상이 아니다. Save 전 변경, Save 후 cold Review 전 변경,
Review 뒤 helper 선언·구현·본문과 편집 graph 변경을 거절해야 한다. 원문을 복구한 뒤
명시적으로 다시 검토할 수 있으며, 후속 owner 설명 Save도 같은 guard와 group을 유지한다.
이미 구현한 cold header 조회 순서·64-member Review·240 read/write·2048 known source
예산과 override·권한·Review/Confirm·최종 CAS를 변경하지 않는다.

추가 대조에서 공개 입력 이름을 저장한 뒤 함수 설명을 편집하면 필요한 native guard를
선택하지 않던 결함을 확인했다. 함수의 현재 draft·경로·hash가 저장한 source proof와
정확히 같고, 이미 캡처한 값 이름 계약일 때만 후속 metadata 편집으로 인정한다. 상세창의
동일 계약 identity map도 그대로 검사한다. 새 계약·재선택·본문 계획을 설명으로 오인하지
않고, 변경/누락된 source proof는 거절한다. 필요한 guard 여부는 원래 소스 관측에서
판단하므로 guard를 지우거나 비워서 후속 Save/Review를 통과할 수 없다. 기존 단순 leaf의
추가 관측이 필요 없는 빈 guard 의미는 유지한다. 카드 설명·상세창·후속 owner 설명 Save는
새 live 기준으로 재배정하지 않고 같은 원래 읽기 scope를 유지해야 한다.

과거 `--imports-boundary`의 실제 로컬 import fixture는 이 지원의 positive 회귀로 갱신한다.
이전 거절이 영구적인 사용자 정책은 아니었다. 기존 leaf/private 이름·본문, 같은 계약
native import와 ref dispatcher 및 Blueprint/native 혼합 경로를 유지한다. 선택한 native
callee 사이의 별도 의존성 합성, 새 import/alias 편집, 직접 외부 import의 관측 결합,
forwarded/opaque·다른 원래 source closure는 기존7/8행의 유한 잔여다. 부모/외부 원문
직접 쓰기 거절은 정상 보호이며 새 migration/독립 계약 복제 요구로 늘리지 않는다.
가능한 조합을 새 필수 목록으로 늘리거나 닫힌 M11/M12/M4를 다시 열지 않는다.

[최종 검증](VALIDATION_V666_NAMED_IMPORTS.md)에 재현·개발 실패/수정과 신규/재사용,
LF/CRLF·취소/Undo/cold·쓰기 실패/복구·source 경합·응답 유실·늦은 입력과 후속 Save,
Review/Confirm·실행·새 패키지/전체 복원·latest/rollback/증거와 디스크를 구분한다.
구 Reference TYPE 거절과 optional 문자열 metadata의 기존 바이너리 증거를 유지하며,
같은 게시 세대 reader/authoring/runtime을 사용한다. 자동 migration/downgrade는 없다.
과거 간헐 빈 #app 원인은 미확정이다. 전송/재로드 관찰과 재현한 module 실패를 원인
확정으로 세지 않는다. 실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 전수
검증은 Linux native/Chromium 자동화와 교차 패키징과 별도다.

이 공개 이름·native 본문과 로컬 import 단위의 [최종 신규 28·재사용 10·총 38단계 검증과 보관](VALIDATION_V666_NAMED_IMPORTS.md)을 마쳤다.
