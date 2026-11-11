# 명시 공개 입력 이름·native 본문과 전달 호출자

고정 [정보 편집7/8행](V536_I5_6_REMAINING.md)의 같은 정보 창·한 Save 흐름이다.
[원래 잔여 대조](V536_I5_6_RESIDUAL_RECONCILIATION.md), [명시 이름·본문 저장](V666_NAMED_BODY_GROUP.md),
[private 호출자](V666_NAMED_NESTED.md)와 [계약 불변 전달 원본](V666_RETAINED_FORWARDING.md)을
기준으로 기존 명시 값 이름 대응을 전달 graph/call에 결합한다. 원래 v666의
`renderFeatureDefinition`/`openOwnFunctionPopover`와 기존 C# 이름 편집·본문 선택·Save를
사용한다. 새 UI·문법·receipt·권한·자동 C# 재작성이나 변환 정책은 추가하지 않는다.

게시 `7b7dd95df26522c95df62f6af7655d0cac9cda1c`에서 원래 프로그램41과 각 단일
이름/본문 후보는 유효하지만, 같은 두 편집의 공동 후보만 전달 문맥 제한으로 거절된다.
기존 depth1/depth2 전달 경로를 포함한 private 호출자에서 공개 amount→leftAmount의
명시 대응과 두 native 본문의 직접 편집을 결합한다. native 매개변수 nativeAmount/
nativeCount와 private 부모의 계약·입력 바인딩은 그대로다. 두 본문을 덧셈에서 뺄셈으로
직접 편집한 뒤 실제 결과는21이다. 이름 변경 자체에 새 실행 의미를 부여하지 않는다.

직접 소유 동기 scalar 함수2~8개, 함수마다 단일 native target과 기존 직접 owned
Blueprint caller를 대상으로 한다. 모든 공개 입력의 위치·타입·역할·수·반환은 유지하고
값 입력 이름만 기존 mapping.args의 위치별 명시 대응으로 바꾼다. ref/out 이름과 실제
native 선언은 유지한다. 원래 전달 graph/call의 입력 저장 위치는 기존 typed graph와
private forwarding 검증이 확인한다. 부모/형제 계약·지역값/exact64·실행선·ID·qualified
C# 원문/record는 보존하고, 필요한 leaf 호출의 signature/argument 이름만 대응한다.

NamedCaller와 최종 caller 문맥 검사 모두 graph/call 전달만 수용한다. code의 storage
또는 implementationContext, wrapper/After, copy provenance와 다른 ABI를 이름 대응으로
인정하지 않는다. 기존 단일 후보를 완전한 원래 관측으로 먼저 검증한 뒤 정·역순 동일
후보와 기존 원자 Save/CAS로 결합한다. 별도 opaque C# 계약 변경은 명시 source 계획이
필요한 원래 잔여이며 이 단위에서 자동 추측하지 않는다. 기존 계약 불변 forwarded/opaque
원본 보존과 ordinary/private·native import의 지원도 유지한다.

기존 version3 readGuards와 저장한 함수/caller source proof를 유지한다. Save 전 원본
변경, 저장 후 후속 설명 Save·cold Review와 Review 이후 원본 변경은 같은 원래 읽기/쓰기
해시로 검증한다. 경합 시 checkpoint·peer·입력을 유지하고 정확한 복원 뒤 새 검토로
진행한다. 기존64-member Review·240 read/write·2048 known source·Tree 예산, override
계약·부모/외부 소유권·권한·authored layout·Review/Confirm·최종 CAS는 유지한다.

[검증 기록](VALIDATION_V666_NAMED_FORWARDING.md)은 게시본 재현, 개발과 최종 신규/재사용,
LF/CRLF·취소/Undo·쓰기 실패/복구·경합·응답 유실·늦은 입력/후속 Save·재시작과 실제 실행,
새 패키지/전체 복원·latest/직전 정상 rollback·증거 및 디스크를 구별한다.
공개 타입/역할·입출력 구조 변경의 명시 대응과 opaque C# 계획, 선택 native callee 사이
의존성 합성·새 import/alias 편집·등록 외부 관측 결합은 같은 고정7/8행 잔여다. 가능한
조합이나 부모/외부 직접 편집·migration을 새 필수로 늘리거나 M11/M12/M4를 다시 열지 않는다.
구 Reference reader 제약과 같은 게시 세대 도구 사용을 유지한다. 초기 빈 #app의 과거
원인은 미확정이다. Linux native/Chromium 자동화·교차 패키징과 실제 Windows/WebView2·
물리 기기·IME·GPU/audio·전체 UI 전수 검증은 별도다.
