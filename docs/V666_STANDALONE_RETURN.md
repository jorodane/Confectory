# standalone 함수의 고정 반환 핀 표시 이름

원본 `reference/site-ui/Confectory-Editor-Prototype-v666.zip` 안
`Confectory-v666/dist/app.js::functionSignatureFields`, `renderFunctionSignatureEditor`는
필드 ID와 표시 이름을 별도로 유지한다. [정보 카드의 반환 표시명](V666_RETURN_LABEL.md)과
[standalone 인자 표시명](V666_STANDALONE_LABELS.md)의 같은 상세창을 재사용한다.
게시 `ca8123ce`의 실제 standalone 상세창에서 고정 반환 이름칸이 읽기 전용인 것을
재현했다. 새 화면·버튼·CSS·크기를 추가하지 않는다.

직접 소유 standalone 함수의 고정 반환 이름칸을 편집한다. 카드와 상세창은 같은
선택 문자열 metadata `editorReturnName`을 표시한다. 기존 trim·1–60 UTF-16 문자·
control 금지 규칙을 재사용하며, `결과`로 명시 초기화하면 그 metadata만 제거한다.
`void`는 반환 핀을 숨기고 기존 이름은 다음 nonvoid 반환을 위해 보관하는 이미
정해진 정책을 따른다. 잘못된 기존 metadata의 읽기 fallback도 기존 helper와 같으며,
해당 이름을 명시 편집할 때만 바꾼다. 고정 `return` ID, 실제 반환 타입·C#·인자
이름/역할/순서·호출 연결을 바꾸지 않는다. native 서명 변경과 새 표시 편집을 한 번에
제출하면 popup 입력을 보존하고 별도 저장을 안내한다. 자동 C# 치환·계약 대응은 없다.

`function-return-name`은 `{type,text}` 두 필드만 가진 기존 owner transaction의 한
표시 셀이다. 반환 이름·인자 표시명·설명·아이콘을 최대4개로 결합한다. 등록/소유 source,
관측 hash와 전체 후보 검증, checkpoint CAS, 저장 영수증·cold/늦은 입력, 최종
Review/Confirm CAS를 그대로 사용한다. 동일 함수의 이 표시 셀에만 source-only Undo를
연결하며 unit 수/kind/path와 다른 원문이 같은지 확인하는 기존 조건을 유지한다.
다른 ownership 변경의 history 경계는 그대로다. 새 runtime ABI·권한·source migration은 없다.

## 유한 잔여와 호환성

이름 변경은 이 standalone 고정 반환 화면만 연결한다. module/caller/graph의 다른
표시 문맥은 원래 화면의 실제 ID·계약과 대조할 잔여이며, 모든 위치/타입 조합을 새
필수 요구로 추가하지 않는다. 고정7행의 실제 forwarded/opaque 영향 source closure,
고정8행의 여러 함수 명시 계약·본문과 공유 caller closure는
[기존 재대조](V666_BOOTSTRAP_RECOVERY.md) 범위로 유지한다. ordinary private/frame/wrapper,
같은 계약 native 다중 본문·호출 보존과 완료된 M11/M12/M4를 다시 미구현으로 세지 않는다.

표시 metadata를 읽는 구 reader와 새 표시 저장을 보존하는 authoring writer를 구별한다.
구 `Confectory.Reference.*` reader의 `TYPE` 거절은 별도 타입 지원 제한이다.
[보관된 실제 바이너리 비교](VALIDATION_V666_ARGUMENT_LABELS.md)는 이번 신규 실행이 아니다.
같은 게시 세대의 reader/authoring/runtime을 사용하며 원문·ID·profile을 보존한다.
일반 값 치환·profile 삭제·자동 downgrade나 `TYPE`만 보고 구 버전/데이터 손상으로
단정하는 안내를 추가하지 않는다. 구 설치본의 실행 지원을 소급 변경하지 않는다.

과거 간헐적인 빈 `#app`의 원인은 미확정이다. 재현된 의존 module 실패 안내와 이번
최종 코드의 전송 정체/실제3D reload 관찰을 구별한다. 실제 Windows/WebView2·물리 기기·
OS IME·GPU/audio·전체 UI 전수 검증은 별도다. 신규/재사용·실패 시도·패키지/전체 복원은
[검증 기록](VALIDATION_V666_STANDALONE_RETURN.md)에 구분해 남긴다.
