# M12 native whole-body 공개 실행 진입

기준은 저장소 v666의 공개 함수 실행 분기/반환/직접 call 흐름과 기존 M11의 명시적 whole-body lift 계약이다. 기존 `sync-acyclic-switch-v1` Root에서 native 문맥이 있다는 이유만으로 공개 분기 전체 거래를 거절하던 경계를 연결한다. profile 자동 승격이나 C# 의미 변환은 하지 않는다.

공개 실행 어댑터가 native `public Invoke`와 중복되지 않도록 기존 M11처럼 그래프의 ordinary 진입을 명시적 `IInvoke` 구현에 둔다. 원래 instance `Invoke`, `this`/재귀, `IImports`/scoped import, CLR receiver와 CallerFilePath/CallerMemberName·CRLF 원문 위치는 그대로다. `IExecutionInvoke`는 기존 out과 별도의 비void 반환 캡처를 발행한 뒤 공개 결과 분기를 전달한다. 원문에 결과 enum/tuple/새 인수를 삽입하지 않는다. 예외를 실패 분기로 치환하지 않는다.

import 함수와 그 소유 scope object 헤더를 변경 없는 관측 멤버로 같은 checkpoint/receipt/Review/최종 CAS에 포함한다. 경로·종류·소유 namespace·source proof와 기존 문맥/인수 저장소 검증은 유지한다. object scope가 외부이면 기존 등록·readonly receipt 경계가 필요하며 이번 단위에서 소유 쓰기로 가장하지 않는다.

이번 새 사용자 흐름은 직접 소유된 이미 저장된 branch-capable whole-body Root, 명시 직접 Blueprint caller의 공개 분기 정의/반환/저장/실행이다. M11 완료분·copy 반환 편집을 새 잔여로 다시 세지 않는다. 공개 override IO 변경·비소유 원본 쓰기·구형 profile 자동 migration은 지원 요구가 아니다. 전체 공개 계약 갱신의 copy/자식·등록 import 등 실제 잔여와 종료 조건은 [유한한 마감표](M12_CLOSURE.md)를 따른다. native ordinary IInvoke 소비자와 자체 postCall wrapper는 새 분기 의미로 자동 해석하지 않는다.

검증은 생성 경계의 동기 void/out·비void/out 실제 실행, native 문맥/서명/인수/위치 변조 거절, scope/import/원문 Save 전후 경합, receipt 누락/변조·cold 복원·응답 재조회, 부분 Review/최종 CAS, 반복 이름/순서·명시 caller 연결을 포함한다. UI는 기존 팝오버/배치·Review 취소/Confirm·Undo/Redo·저장 실패·중단/늦은 응답·재시작을 확인한다. 독립 LF/CRLF와 새 패키지·전체 압축 복원본은 최종 동결 코드에서 별도로 실행하며 결과를 아래에 기록한다.

실제 Windows apphost/WebView2·모바일·DPI/IME, 독립 창·프로젝트 왕복과 전체 UI/Space 전달은 이번 교차 패키지 검사로 완료를 주장하지 않는다. 기존 원본·권한·main·과거 산출물은 보존하며 승인된 자체 검사 임시물의 증거 보존 후 수명관리와 최신/롤백 승격만 사용한다.
