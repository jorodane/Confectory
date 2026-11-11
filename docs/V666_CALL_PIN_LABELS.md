# Blueprint 호출 카드의 읽기 전용 핀 표시명

원본 `reference/site-ui/Confectory-Editor-Prototype-v666.zip` 안
`Confectory-v666/dist/app.js::featureSignatureFields`와 함수 노드 표시는 필드 ID와
표시 이름을 구분한다. 정보·standalone 정의에 저장한 인자/반환 표시명을 현재
Blueprint 호출 카드에도 보여주는 한정 연결이다. 게시 `2ed5ff01`의 실제 엔진/UI에서
별칭이 있는 함수를 호출해도 호출 카드는 native 이름만 보여주는 것을 재현했다.

직접 소유한 일반 동기 루트 구현의 기존 ordinary `next` 호출을 다룬다. 현재 view가
이미 읽은 직접 소유 함수의 선언만 사용하며 새 파일·외부 등록 접근을 추가하지 않는다.
slot/copy/private frame·상속 구현·async·공개 실행/후처리 wrapper에는 새 표시를
암묵 적용하지 않는다. 다른 표시 문맥은 기존 명세에 비추어 연결할 잔여다.

기존 native 위치 ABI의 인자 수·타입·역할·반환이 같은 경우에만 callee의 native 이름에
연결된 명시 표시명을 같은 위치의 caller 핀 ID에 투영한다. callee의 `amount`와 caller의
`supplied`가 달라도 실제 ID는 `supplied`이며 표시만 별칭을 사용한다. 별칭이 없으면
기존 caller 이름을 유지한다. 반환 표시는 기존 `editorReturnName`/`결과` 정책이다.
서명 대응을 새로 저장하거나 C# 이름·순서·입출력·연결·실행 계약을 바꾸지 않는다.

`functionPinPresentation`은 전달받은 관측 선언과 호출 서명만 읽는 순수 metadata
작업이다. view의 선택 `pinPresentation` 필드가 표시를 전달한다. compiler Core의
node definition/outputs/계약·정의 hash와 generator에는 이 필드를 넣지 않는다.
callee source는 기존 Read/관측 revision/hash에 이미 포함되며 save/Review/Confirm의
기존 source proof와 실제 반영 파일의 최종 CAS를 유지한다. 일반 Confirm이 현재 물리
원본을 복사해 컴파일하는 기존 동작은 유지하며, 편집하지 않은 모든 source의 공백 변경까지
새 raw-byte guard로 묶었다고 주장하지 않는다. 다른 함수의 미저장 브라우저 입력을 읽어
암묵 저장하거나 표시의 근거로 사용하지 않는다.

잘못된 인자 표시 metadata·다른 서명·caller native 이름과 충돌하는 별칭을 정상 표시로 추측하지 않는다.
callee에서 유효한 별칭도 caller의 다른 이름과 충돌하면 기존 입출력 쪽별 distinct 규칙으로 거절한다. 순수 조회는
`invalid-labels`/`ambiguous-labels`/`signature-mismatch`로 구별하며 view는 원래 핀을 유지하고 기존 카드의
`title` 안내를 사용한다. 원문·profile·ID를 지우거나 자동 복구하지 않는다. JS에서는
JSON의 자체 키만 조회한다. native 이름 `constructor` 등과 JS 기본 속성을 혼동하지 않는다.
CSS·카드 크기·새 편집 제어를 추가하지 않는다.

## 기존 유한 잔여

이 단위는 표시 전달이며 고정7/8행의 계약·본문 결합을 완료로 세지 않는다.
[고정7행](V536_ROW7_REMAINING_BOUNDARY.md)의 실제 forwarded/opaque 영향 source와
다른 frame 계획 결합, [고정8행](V536_I5_6_REMAINING.md)의 여러 함수 명시 계약·본문 및
공유 caller closure는 기존 잔여다. 이미 지원하는 ordinary private/frame/wrapper,
같은 계약 native 다중 본문·caller 보존과 완료된 M11/M12/M4를 다시 열지 않는다.
가능한 이름/타입/target 조합 전부를 새 필수 요구로 늘리지 않는다.

구 reader의 새 `Confectory.Reference.*` TYPE 거절과 optional 문자열 metadata 호환은
별도다. [구 바이너리의 보관 근거](VALIDATION_V666_ARGUMENT_LABELS.md)를 사용하며 같은
게시 세대의 reader/authoring/runtime을 사용한다. 이 view projection으로 구 설치본을
소급 수정하거나 TYPE만으로 버전/손상을 단정·자동 downgrade하지 않는다.
과거 간헐적 빈 `#app` 원인은 미확정이다. 새 전송 정체 관찰과 재현된 module 실패
안내를 그 원인 확정으로 합산하지 않는다. 실제 Windows/WebView2·물리 기기·OS IME·
GPU/audio·전체 UI 전수 검증은 별도이며 최종 신규/재사용·패키지/전체 복원과 실패 기록은
[전용 검증](VALIDATION_V666_CALL_PIN_LABELS.md)에 남긴다.

이 호출 핀 표시 단위의 [최종 신규 36단계·재사용0 검증과 보관](VALIDATION_V666_CALL_PIN_LABELS.md)을 마쳤다.

[이미 관측한 함수 호출 표시](V666_OBSERVED_CALL_LABELS.md)는 saved Blueprint의 공통 읽기 경계에서 정확한 owned 함수 관측과 기존 위치 ABI를 사용한다. private·After·slot을 표시만의 금지 조건으로 삼지 않으며 snapshot/외부 읽기/계약 편집 권한은 확장하지 않는다. 고정7/8행의 실제 계약·본문 closure와 기기·전체 UI 잔여는 별도다.
