# native 본문 공동 저장과 명시 값 입력 이름

고정8행의 같은 정보 창 Save는 여러 함수의 실제 계약·본문 입력을 한 후보로 결합해야 한다.
[기존 잔여](V536_I5_6_REMAINING.md)와 [원래 조작 대조](V536_I5_6_RESIDUAL_RECONCILIATION.md)를 기준으로,
게시 `23c3dbb0`에서 직접 소유 함수 둘의 native 본문 편집과 한 함수의 공개 값 입력 C# 이름 변경을
각각 저장하면 유효하지만 공동 후보만 거절하는 경로를 재현했다. 원래 프로그램 결과40도 확인했다.

이 확장은 직접 소유 동기 scalar 함수2~8개, 함수마다 import 없는 단일 native target과 일반 직접 Blueprint caller를 다룬다. 기존 같은 계약 그룹의 다중 target/import/다른 caller 지원과64-member budget은 유지한다. 모든 공개 입력의
위치·타입·역할·수·반환은 유지하고, 값 입력의 이름만 사용자가 명시한 기존 `mapping.args`로
대응한다. ref/out 이름은 이 확장에서 바꾸지 않는다. 각 target의 실제 native C# 매개변수 선언은
원래와 정확히 같아야 하며, 사용자가 직접 편집한 본문과 선택 공개 계약을 기존 단일 closure로
검증한다. 모든 영향을 받는 target·사용처·공유 caller/import를 원래 관측으로 먼저 검증한 뒤
내부 overlay와 한 Save/CAS에 결합한다. C#·호출 값·타입 변환을 추측해 작성하지 않는다.

실제 예는 공개 `amount`를 명시적으로 `leftAmount`로 바꾸되 native `nativeAmount`와
`nativeCount`는 유지하는 경우다. 공유 caller의 원래 `first` 바인딩은 새 공개 이름에 그대로
대응하고, 기존 실행선·출력 소비자·함수/본문 ID를 유지한다. 두 본문은 사용자가 직접 덧셈에서
뺄셈으로 편집했으며 실행 결과는20이다. 이름 변경 자체를 본문 의미 변경으로 간주하지 않는다.

기존 상세창의 **C# 이름 편집** 모드를 명시적으로 사용한다. 별도 **표시 이름 편집** metadata와
혼동하지 않으며 새 제어·CSS·레이아웃·권한을 추가하지 않는다. 새 이름 결합의 caller는 sync ordinary call/export만 두고 private/code/후처리·지역값/별칭/copy 문맥으로 암묵 확장하지 않는다. 기존 Blueprint/ref/whole 계획은
native body unit이 아닌 경우 원래 dispatcher를 유지한다. override 공개 계약·부모/외부 원본·
copy 관측의 기존 제한을 해제하지 않는다. 지원되지 않는 조합은 입력을 보존하고 거절하며,
가능한 이름/타입/target 조합을 새 필수 작업 목록으로 늘리지 않는다.

## 충돌과 수명 경계

기존 단순 leaf 문맥은 추가 body `readGuards`가 비어 있을 수 있다. `InformationFunctionBodyGuards`
의 `ObservedScope`는 기존 import/다중 target/native·복잡 caller 관측 등의 별도 읽기 범위를 다룬다.
이 확장에서 모든 미편집 헤더의 공백까지 새 raw-byte lease로 묶지 않는다. 실제 편집한 함수·본문·
caller graph는 원래 write CAS로 보호하고 Confirm은 현재 물리 원본을 복사해 다시 검증/컴파일한다.
호환되지 않는 현재 헤더, 편집 대상 파일의 사후 변경과 단순 미편집 공백 변경은 구별한다.
기존 추가 읽기 guard가 필요한 문맥의 정책은 보존한다.

Save 실패·cold·응답 유실/settlement·늦은 입력과 후속 명시 Save·Review 취소/Confirm·최종 CAS는
[최종 검증 기록](VALIDATION_V666_NAMED_BODY_GROUP.md)에 신규/재사용 및 fixture 실패를 구분해 남긴다.
latest/정상 rollback2세대와 증거를 보존하고 main은 사용자 검토/merge 대상으로 유지한다.

## 남은 실제 범위

고정7행의 forwarded/opaque 및 다른 frame 계약·본문 source closure와 고정8행의 위 단위 밖
명시 계약·본문·공유 caller 결합은 기존 잔여다. 이미 지원한 native 본문 그룹·ordinary wrapper/
private·M11/M12/M4를 다시 열지 않는다. 이름 이외의 타입/역할/입출력 구조 변경이나 native
매개변수 선언 변경을 이번 최소 단위의 지원으로 주장하지 않는다.

구 Reference reader의 TYPE 거절·optional 문자열 metadata 호환은 [기존 바이너리 증거](VALIDATION_V666_ARGUMENT_LABELS.md)를
따른다. 같은 게시 세대 reader/authoring/runtime을 사용하며 소급 수정·자동 downgrade/migration은 없다.
초기 간헐적 빈 `#app`의 원인은 미확정이다. 현재 전송/재로드 및 이미 재현된 bootstrap module 실패와
구분하고 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·전체 UI 전수 검증은 완료로 세지 않는다.

이 명시 이름·본문 공동 저장 단위의 [최종 신규 37단계·재사용0 검증과 보관](VALIDATION_V666_NAMED_BODY_GROUP.md)을 마쳤다.
