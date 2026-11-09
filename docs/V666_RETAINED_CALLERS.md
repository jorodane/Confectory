# 여러 C# 본문 저장과 기존 일반 호출자

고정 [정보 편집8행](V536_I5_6_REMAINING.md)의 한 정보 창·한 Save에서,
직접 소유 함수 여러 개의 같은 계약 C# 본문을 바꿀 때 기존 일반 Blueprint 호출자의
계산 코드와 지역값을 보존한다. 원본 v666 ZIP `app.js`의 `renderFeatureDefinition`,
`openOwnFunctionPopover`와 `blueprint.js`의 기존 일반 code/call 흐름을 기준으로 한다.
새 화면·제어·권한이나 가능한 문맥 조합별 새 필수 항목을 만들지 않는다.

게시 cba44307에서 각 본문 편집과 원래 프로그램41은 유효했지만, 기존 호출자에
일반 code와 locals가 있으면 공동 후보만 거절됐다. 최초 구현 후보에서는 caller
코드 기록의 JSON 의미가 같아도 재직렬화해 쓰기 대상에 넣는 추가 결함을 발견했다.
그 후보는 Confirm하지 않았다. 변경 없는 코드 기록은 원래 바이트를 유지해,
수정하지 않은 코드 파일·graph·local ID·연결·정확64 값이 새 쓰기 대상이 되지 않는다.

지원 경계는 기존 직접 소유 단일 native target의 같은 계약 본문2–8개와,
기존 직접 소유 일반 code/call/export next 호출자다. 호출자의 기존 locals/aliases는
보존한다. 원래 source-ready/assemble·노드 hash·타입 검증은 그대로 수행한다.
copy/private/forwardCallerStorage/implementationContext/postCall/실행 분기 조작은
이번 경계에서 기존대로 거절하며 자동 의미 변환이나 C# 소스 재작성은 없다.
callee 공개/native/override 계약·인자 ID/타입·권한·UI 배치를 바꾸지 않는다.

추가 callee import나 native caller가 없는 leaf에서도 이 보존된 일반 caller를
기존 version3 readGuards에 연결한다. 원래 source snapshot 전체의 알려진 owned
경로/해시와 기존240개 예산을 사용한다. cold Review는 원래 알려진 소유 header를
먼저 읽고, 그 import가 가리키는 기존 caller graph ID만 읽는다. 경로를 추측하거나
새 외부 접근을 만들지 않는다. 저장 후 caller가 단순 graph로 바뀌어도 이미 저장한
읽기 증거를 빈 legacy receipt로 재해석하지 않는다. 후속 owner 설명/아이콘 Save도
원래 같은 그룹과 읽기 해시를 보존한다. checkpoint CAS·Review·최종 source lease는
기존 경계를 유지하고, 과거 leaf/단순 Blueprint caller의 빈 guard 호환은 남긴다.

추가로 본문만 저장하는 동안 처음 입력한 설명이 cold 뒤 이전 revision에 남아
후속 Save를 막는 결함을 재현했다. 명시 저장의 settled receipt를 확인한 뒤 소유
선언의 text hash가 그대로인 새 설명에만 기존 description proof를 연결한다.
소유 선언 해시가 달라지면 기존 거절을 유지하며 새 텍스트를 덮어쓰지 않는다.

고급 정보·참조 핀의 공통 값/참조 타입과 정보별 생성 C# 타입 선택은 답변 대기다.
이 단위는 그 결정을 사용하지 않는다. 일반 입력/out 표시명과 7/8행의 다른 실제
closure·고급 타입 실행 통합을 완료로 세지 않는다. M11/M12/M4를 다시 열거나
외부/부모 원본 편집·새 권한·자동 copy/migration 요구를 추가하지 않는다.
초기 빈 화면 원인은 미확정이며 실제 기기와 전체 UI는 별도 검증이다.

최종 runtime `7938a4f01e6331cd980e4397fbba66fc3ffc0ea8`의 신규34단계·동등 재사용7, 유효41단계를 [확정 검증·보관 기록](VALIDATION_V666_RETAINED_CALLERS.md)으로 마감했다.

첫 동결본의 최종 검사에서31개를 통과한 뒤 충돌 UI의 경고 관측이 시간 초과됐다.
기존 코드에서 Save pointerdown과 release 사이에 peer 갱신을 넣으면 버튼이 제거·
재생성돼 release가 저장을 발행하지 않는 경로를 고정 재현했다. 같은 프로젝트·같은
요소·같은 종류의 갱신에만 기존 action 버튼을 유지하고 현재 handler를 다시 연결한다.
프로젝트/요소 변경에서는 기존처럼 버튼을 교체해 이전 gesture를 새 대상으로 옮기지 않는다.
수정 후 같은 눌림/갱신/release는 현재 Save를 실행하고 stale 입력을 거절했다.
입력·체크포인트·peer를 유지하며 새 저장 권한을 만들지 않는다. 이 경로의 재현/수정과
과거 모든 간헐 현상·초기 빈 화면의 원인 판단은 구별한다.

native backend·자료 adapter·SDK/NuGet·독립 EOL과 실행 명령이 같은7개 사실만
봉인 증거와 대조해 재사용한다. UI·실패·미실행·빌드·패키지는 모두 새로 검사한다.
