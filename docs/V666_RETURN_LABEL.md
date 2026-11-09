# 정보 함수 반환 핀의 표시명

고정 [정보 편집9행](V536_I5_6_REMAINING.md)의 표시명/native 식별자 분리 중,
직접 소유 정보 함수의 고정 반환 슬롯 한 곳을 연결한다. v666 ZIP
`Confectory-v666/dist/app.js::renderFunctionSignatureEditor`는 출력의 이름 입력을
노출하고 `openOwnFunctionPopover`는 필드 ID와 이름을 별도로 저장한다.
게시 eb1492e8의 실제 상세창에서는 `결과` 입력이 readonly이고, 표시명만 제출한
native 후보도 거절된다. 기존 두 native 함수의 원래 실행 결과는46이다.

같은 원래 이름칸에서 한글·공백·기호를 편집하고 기존 Save→Review→Confirm으로
정보 함수 카드의 반환 이름을 저장한다. 새 UI나 배치는 추가하지 않는다.
`editorReturnName`은 선택적 function 표시 metadata이며 기존 `return` ID,
함수 signature·인자 이름·순서·타입·C# 원문·caller 바인딩과 구별한다.
일반 인자/out 이름 편집은 기존 실행 계약의 의미를 유지한다.
공통 standalone 기능 상세창은 이 정보 전용 opt-in을 받지 않으므로 기존 동작을 유지한다.

입력은 trim 후1–60 UTF-16 문자·control 문자 없음으로 제한한다. `결과`로
되돌리면 선택 metadata를 제거한다. 이 키가 없는 구 선언/요청은 기존 기본 표시를
유지한다. 키가 있어도 명시하지 않은 기존 편집에서는 보존한다. 반환이 void이면
슬롯을 새로 만들지 않고 metadata는 다음 반환의 표시로만 남는다. 새 표시 metadata는
기존 value 문법을 사용하고 C# 생성·함수 ABI·override 계약·권한을 바꾸지 않는다.
구 reader의 모든 checkpoint 교환을 검증한 것으로 보지는 않는다.

기존 직접 소유 판정과 function hash, exact-key, 원자 후보/CAS, 공동 Undo,
Review/Confirm과 최종 source lease를 재사용한다. receipt는 제출한 표시명과 저장된
함수 hash를 확인하고, 응답 이후의 새 표시 입력을 과거 텍스트로 덮어쓰지 않는다.
부모·외부·참조 원본 쓰기나 새 권한·계약복제·자동 소스 재작성은 추가하지 않는다.

9행의 입력/out 표시명 분리와 정보·참조·외부 타입의 실행 통합은 별도 기존 잔여다.
현재 Core generator는 C# 타입 표기를 그대로 사용하고 schema는 자료 계약이므로,
단지 타입 선택창에 정보를 나열해 실행 지원으로 간주하지 않는다. 고급 핀의 공통
값/참조 CLR 표현과 schema별 생성 타입 중 선택은 사용자 답변 대기 중이다.
7/8행의 실제 closure·저장 편집 잔여도 전체 완료로 처리하지 않는다. 신원/그룹
backend와 종류 CLR/사용 중 삭제 정책, 실제 기기/전체 UI 검증을 구분한다.
M11/M12/M4는 회귀 근거 없이 다시 열지 않는다. 초기 빈 화면 원인은 미확정이다.

최종 runtime `dcf4cf7b82a3d6f84515a4b921dfb17dcce62c94`의 신규36단계·재사용0을 [확정 검증·보관 기록](VALIDATION_V666_RETURN_LABEL.md)으로 마감했다.
