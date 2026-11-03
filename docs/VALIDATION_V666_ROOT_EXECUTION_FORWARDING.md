# M12 기존 private 실행 경계 안의 공개 호출 갱신

원본 v666 `dist/blueprint.js:135`는 call의 실행 포트를 참조 정의에서 가져오며 `:248`은 분기 반환과 부모의 연속 실행을 구별한다. 기존 M11은 소유 private graph의 `executionSource`·`executionEnum`·종료점 선택을 이미 저장한다. 이번 흐름은 그 프레임의 기존 실행 분기 안에서 호출한 함수의 공개 분기를 갱신하는 것이다. 새 계약 복제·profile 자동 migration·원문 변환을 추가하지 않는다.

후보는 기존 switch-profile frame과 분기 소유 관계를 보존한다. `executionExitMode` 또는 `branchOwner`가 있다는 이유만으로 호출 전체를 일괄 거절하지 않고, 기존 전체 `Definitions`/`SwitchFlow` 검증을 후보 전후에 적용한다. private source·서명·enum·분기 소유자·종료점 coverage가 맞지 않으면 계속 거절한다. 피호출자의 공개 분기를 바깥 selector의 enum으로 대체하지 않으며 부모/참조 원본·override 계약·권한은 변경하지 않는다. 모든 실제 호출은 계속 명시 대응하고 같은 checkpoint/Review→Confirm/최종 CAS를 사용한다.

집중 fixture의 기존 private selector는 `done=17`과 out 저장소를 갖는다. 그 분기 안에서 callee를 호출한 뒤 private 반환·부모 분기·부모 다음 줄을 실행한다. callee의 성공만 기존 private 반환 카드에 연결하면 그 프레임의 다음 줄만 건너뛰며 원래 `17`·출력 `10`·부모 실행을 유지해야 한다. 실패/None의 미연결 분기는 원래 다음 줄을 계속한다. 잘못된 source/enum/서명/owner/coverage·다른 frame 경로·낡은 증거와 Save/Review 뒤 원문 경합을 거절하고, 원문 C#·형제 frame·readonly mode·재시작/응답 유실·늦은 입력·Undo/취소/저장 실패를 확인한다. 실제 UI와 독립 LF/CRLF·새 패키지/전체 복원 결과는 최종 동결 뒤 아래에 기록한다.

원본 `blueprint.js:1504–1512`의 wrapper는 원본의 핀·분기·공개 출력이 바뀌면 계약 갱신을 요구한다. 이 정상 거절을 자동 wrapper 갱신의 미구현으로 세지 않는다. `:1514–1519`의 명시적 OriginalResult 매핑은 별도 기존 wrapper 흐름이며, 기존 ordinary IInvoke/NoBranch adapter를 실제 공개 결과라고 바꾸어 해석하지 않는다. copy/자식 전체 정의 갱신과 등록 import의 실제 잔여는 [유한한 M12 표](M12_CLOSURE.md)를 따른다. M11은 구체적 회귀 없이 유지하며 M4의 명시 async caller 규칙은 별개다.

레이아웃·CSS/HTML·원본 C#·공개 IO·권한을 보존한다. 검사는 승인된 실행별 임시물 수명관리와 최신/롤백 보관을 사용하며 과거 자료를 추가 삭제하지 않는다. 교차 패키지/복원 검사는 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달 완료가 아니다.
