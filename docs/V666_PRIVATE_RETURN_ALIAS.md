# Scalar 반환 편집기의 원래 C# 별칭 보존

고정 v666 [정보7/8행](V536_I5_6_REMAINING.md)의 [private 본문·scalar 반환 공동 저장](V666_PRIVATE_SCALAR_RETURN.md)에서 남긴 native 별칭 UI 경로다. 직접 소유한 일반 C# 구현에서 공개 인자명과 원래 C# 인자명이 다르면, 반환 타입을 선택한 뒤에도 읽기 전용 헤더가 원래 C# 인자명·타입·역할·수를 유지한다. 본문과 반환값은 사용자가 직접 작성한다. 자동 이름 변경·본문 변환·호출자 전환은 하지 않는다.

유한 범위는 기존 scalar 입력/out 정의를 유지하고, 기존 반환과 같은 타입의 out이 있는 함수의 non-void scalar 반환 변경이다. 이전 반환 소비자는 호환 out에 직접 대응한다. private 본문/helpers 편집과 한 정보 창·한 Save·한 Review/Confirm에 결합한다. 원래 native 별칭 `nativeAmount/nativeCount`와 공개 `amount/count`를 구분하며, 실제 caller40→20, native double 반환25.5·기존 long out25를 확인한다. 다른 역할·void·입출력 구조·private ABI·opaque/import 확장은 별도 잔여다.

이미 저장한 명시 서명의 인자명은 유지한다. 새 읽기 전용 편집 초안은 기존 `parameters` 필드에 표시한 인자 문맥을 보관해 재진입 시 유지한다. 그 표식이 없는 이전 초안을 새 별칭으로 추측해 해석하지 않는다. 원문 hash가 다르면 초안을 보존하고 재진입을 거절한다. 본문을 바꾸지 않은 Code Save는 기존 CRLF 문자열을 유지한다. 새 schema·receipt 필드·migration·권한은 없다.

제품 변경은 기존 `feature-authoring.js`의 서명 선택·초안 문맥·원문 문자열 보존과 해당 WebBundle의 정규화 크기/hash뿐이다. backend·workspace version1·receipt version3·nativeBodyContexts·전체 읽기 관측·최종 CAS·원본 권한·authored layout은 유지한다. 구 패키지 UI의 실패 재현과 구 backend의 유효한 명시 계획 수용은 구분해 기록한다.

검증은 native 엔진/컴파일러와 Chromium 자동화의 저장·Undo/Redo·cold 복원·실패/재시도·응답 유실·늦은 입력·Review 뒤 경합·LF/CRLF·새 패키지/전체 복원으로 구분한다. 이전 초안/명시 별칭/원문 CRLF의 독립 렌더러 검사는 모의 metadata 검사로 별도 표시한다. Windows/WebView2·물리 기기·전체 UI를 완료로 주장하지 않는다. 초기 빈 화면 원인은 미확정이며 구 Reference reader 제약도 유지한다.
