# 이미 관측한 함수의 호출 핀 표시명

[직전 일반 루트 호출 표시](V666_CALL_PIN_LABELS.md)를 기존 saved Blueprint의 공통 읽기 경계에 연결한다.
원본 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`featureSignatureFields`는 필드 ID와 표시명을 구별하고 내부 흐름에서도 같은 함수 카드를 사용한다.
게시 `e663dc5b`에서는 동일 소유 callee의 별칭을 이미 읽고도 private 호출 카드가 native 이름만
표시했다. 기존 private·After·owner-bound slot 읽기 화면을 재현 기준으로 삼았다.

`Blueprint.csbody`가 이미 보유한 owned 함수의 관측 `sources[id].text`와 이 view가 사용한
`contracts[id]`가 정확히 같은 경우에만 기존 순수 `functionPinPresentation`을 호출한다.
새 원본·외부 팩을 읽지 않는다. native 위치 ABI 대응·caller 쪽 distinct 검증과 기존
안내를 재사용하며, 표시 metadata는 compiler definition/hash·signature·바인딩·실행에
넣지 않는다. CSS·레이아웃·편집 제어와 저장 권한은 바꾸지 않는다.

이 경계는 저장된 view의 현재 관측을 기준으로 한다. private·After·slot이라는 이유만으로
표시를 막지 않으며, 다른 기존 saved view도 같은 owned/정확한 관측/동일 ABI 검사를 통과해야 한다.
retained copy/override snapshot을 현재 선언으로 간주하거나 새 copy preview의 별도 관측을
생성하지 않는다. 외부 등록 함수의 읽기 권한을 넓히거나 원문과 다른 snapshot을 자동 교체하지 않는다.
비대응 ABI·잘못된/충돌하는 표시명은 기존 native 핀과 안내를 유지한다. 지원하지 않는 계약
편집을 이 표시 연결로 허용하지 않는다. 가능한 context/type 조합을 새 필수 작업 목록으로 만들지 않는다.

반복 진입·root/private 이동·cold 복원에도 native `supplied`/`return`과 원문·정의 hash를 유지한다.
기존 값 편집의 Save·Review 취소·Confirm 및 실제 편집 graph의 최종 CAS를 검증한다.
편집하지 않은 모든 callee 원문까지 새 raw-byte lease를 추가하는 정책은 없다.

## 고정 잔여 대조

[고정7행](V536_ROW7_REMAINING_BOUNDARY.md)의 실제 잔여는 원본 계약 갱신이 forwarded/opaque
source 및 다른 frame 계약·본문에 함께 영향을 주는 경우의 명시 대응과 전체 closure다.
이미 지원한 ordinary private/root/wrapper의 같은 Save와 원래 공개 override 계약 변경 거절은
새 미구현 항목으로 세지 않는다.

[고정8행](V536_I5_6_REMAINING.md)의 실제 잔여는 같은 정보 창에서 여러 함수의 명시 계약·본문을
함께 변경하고 공유 caller/import 및 실제 영향을 받는 모든 source를 한 후보로 결합하는 흐름이다.
`InformationFunctionBodyBatch`의 같은 계약 native 다중 본문/기존 호출자 보존과
`InformationFunctionBatch`의 검증된 계약 조합은 이미 지원한다. body-only guard를 단순히
완화하면 이 잔여가 완료되지 않으며, C# 자동 재작성이나 copy/부모/외부 쓰기를 추가하지 않는다.
이번 단위는 표시 전달이며 7/8행·M11/M12/M4 전체 완료로 합산하지 않는다.

구 Reference reader의 실제 TYPE 거절과 optional 문자열 표시 metadata 호환은 별도다.
[기존 바이너리 증거](VALIDATION_V666_ARGUMENT_LABELS.md)의 SHA를 다시 확인하며, 과거 결과를
새 reader 실행으로 세지 않는다. 구 설치본 소급 수정·자동 downgrade/migration은 없다.
같은 게시 세대의 reader/authoring/runtime을 사용한다.

간헐적 초기 빈 `#app`의 원인은 미확정이다. 현재 전송 정체·reload와 이미 재현한 module
실패 안내는 각 관측 범위로 남긴다. 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·
전체 UI 전수 검증과 구분하고 [최종 검증 기록](VALIDATION_V666_OBSERVED_CALL_LABELS.md)에
신규/재사용·LF/CRLF·새 package/전체 복원 및 실패 근거를 기록한다.
