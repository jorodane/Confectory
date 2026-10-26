# v536 공유 호출자의 명시 매개변수 순서

기준은 저장소 `196c605` v536 원본이다. 정보 상세창의 정렬 제어를 새로 만들지
않는다. 원본 `blueprintParseCSharpRegions`는 기존 C# 인자명으로 핀 ID를 찾아
`scriptParameterOrder`를 바꾼다. 실제 원본 렌더에서 `amount-pin`/`total-pin`을
같은 타입·역할·본문으로 이동하는 것을 확인했다. 원본 데모 검사는 실제 엔진
검증과 구분한다. 첨부 ZIP과 저장소 레퍼런스의 동일성은 미확인이다.

이번 지원 단위는 직접 소유한 정확한 whole-body code/return lift 2~8개다.
기존 C# 편집 영역에서 `(long nativeAmount, ref long nativeTotal)`을
`(ref long nativeTotal, long nativeAmount)`로 적으면 공개 핀
`amount`/`count`가 기존 ID·타입·역할을 유지하며 이동한다. native 별칭과 공개
핀 이름은 별개다. 명시 호출 검토에서 각 원래 바인딩을 확인하며 공유 caller의
호출 서명·typed import·callee native/public 계약·whole receipt를 한 후보/CAS로
검증한다. 각 원래 후보를 먼저 증명하고 역순 합성 결과도 대조한다.

변경 전 두 단일 후보는 유효하지만 그룹은 거절했고, 실제 C# 화면은 이동한
ref를 위치별 역할 변경으로 잘못 해석했다. 이제 기존 native 이름·타입·역할이
정확한 순열일 때만 원래 공개 핀을 따라 이동한다. 이름/타입/역할 변경이나
다른 계약 변경이 섞인 순서는 추측하지 않으며 입력을 보존하고 거절한다. 이미 선택한 같은 순열은 본문에 재진입해 다시 저장할 수 있고, 기존 원래 핀 집합을 재확인한다.
사용자 C# 원문 자동 재작성, 연결 삭제·다른 셀 선택·출력 재선택은 없다.

전체 요청의 원래 hash/CAS와 기존 단일 계약/whole-body/컴파일 검사는 유지한다.
함수 선언·native header/context·typed import만 같은 순서로 갱신하며 caller의
입력 저장소·첫 호출 반환→둘째 호출 입력·최종 반환·실행 경로와 출력 ID를
보존한다. 기존 반환 writer는 기존 whole-body 경로의 명시 `return: null`
정규화를 사용한다. 원래 본문과 별도 원문 파일·정확한 64비트 값·설명·부모·
외부 원본을 유지하며 자동 확정하지 않는다. HTML/CSS·모달·기존 버튼은 변경하지
않고 `feature-authoring.js`의 저장 어댑터와 `element-functions.js`의 기존 검토창 진입 조건 및 두 리소스의 고정 해시만 갱신한다. 순서만 바뀌면 검토를 건너뛰던 조건을 실제 화면에서 재현하고 수정했다.

검증 결과는 [집중 근거](evidence/v536-information-shared-order/focused-verification.json)에
기록한다. 초기 검사 준비 중 미완성 report를 읽은 오류, 반환 writer 정규화의
검사 예상값 누락, JS 리소스 고정 크기 미갱신으로 인한 기동 거절은 실패 근거를
보존한 뒤 각각 준비 순서·정확한 예상 graph·정상 manifest 갱신으로 해결했다.
재진입한 같은 순열을 잘못 거절하던 오류도 실제 화면에서 재현하여 수정했다. 순열 후 ref 입력/출력에 중복되는 arg0 대신 의도한 값 입력 arg1을 선택하여 거절/Undo 재시도를 확인한다. 기능/CAS/컴파일 검사를 약화하지 않는다.

8행 전체 완료는 아니다. 이번 정확한 순열과 다른 역할·입력/출력 재선택·타입/
정의 변경의 혼합 및 일반 retained/native/mixed·중첩/private·whole caller/
postCall·복사/상속/등록 문맥의 여러 closure 결합은 현재 별도 경계를 유지한다.
7행의 원계약 유지 copy 편집·배정 잔여와 9행 고급 타입/표시명도 별도다.
오버라이드의 원계약 구조 변경은 정상 금지이며 독립 계약 복제/새 ID는 필수
범위에서 제외한다. I6/B2·A4~A6·M4/M11/M12, 전체 UI, 실제 Windows/WebView2·
모바일 기기 실행과 Library 전달은 미완료다. 새 이미지/협의/렌더 backend는
이번 UI 복원 범위 밖이며 구현하지 않는다.

집중 12흐름·32확인, 영향 9흐름·25확인이 통과했다. 기본/독립 창의 C# 잘못된 혼합 순서 거절/입력 보존·취소/재열기·명시 호출 대응·Undo/Redo·미저장 cold·저장 cold·Review 취소/Confirm, checkpoint 실패 전체 미적용/재시도·응답 유실 뒤 settled 결과 조회와 중복 방지·실제 peer 경합·프로젝트 전환/오래된 창 차단을 확인했다. 마지막 함수의 잘못된 계획/본문·receipt·컴파일·다른 문맥은 첫 함수까지 미적용이며 원본·정확64 값·반환 경로를 보존한다. 초기 실패 5건의 원인과 통과한 재검증은 근거에 별도로 기록했고 미해결 실패는 없다. 원본 렌더/실제 C#·호출 검토창 스크린샷과 원문 fixture를 보존했다.
