# M4 · 소유 whole-body 함수의 명시적 비동기 전환

저장소 v666 `blueprint.js`의 기능 heading 전환과 완료 흐름을 기존 native whole-body의 소유 Root에 연결한다. 이미 명시적으로 Blueprint로 전환·확정한 직접 소유 함수와 모든 소유 target이 대상이다. 원문 C# target은 기존 명시 전환이 선행하며 자동 복제·재작성하지 않는다.

기존 `Invoke`는 같은 생성 클래스의 같은 서명·이름으로 유지한다. 함수의 Task 진입과 원래 native 호출을 분리하므로 `this`, 직접 `this.Invoke` 재귀, `calls`와 scoped import, 타입 정체성, 원래 소스 파일/멤버 위치, CRLF literal을 유지한다. native 반환은 기존 export를 따르고 out은 이름이 다른 구현 매개변수도 서명 위치에 따라 공개 출력에 전달한 뒤 호출자 완료/후속 동작으로 진행한다. ref는 기존 async 계약에서 거절한다.

원래 native `Invoke` 자체는 동기 메서드다. 본문을 자동으로 async로 고치거나 별도 스레드에서 실행하지 않는다. 함수 전체의 명시적 Task 어댑터만 추가한다. native 노드의 개별 async 버튼은 계속 비활성화하고 API도 같은 변경을 거절한다. 실제 await 코드 작성은 이미 지원하는 ordinary async 동작의 명시 편집을 사용한다. 기존 import가 새 async 함수의 동기 호출 계약을 사용하면 컴파일/편집 오류를 표시하며 자동 대기·호출자 전환을 하지 않는다.

원래 팝오버·레이아웃과 코드 팝업을 재사용한다. Save는 모든 소유 target/본문·실제 호출자·provider/scoped import 관측을 기존 원자 후보에 묶고, 원본 쓰기는 완전한 Review→Confirm과 최종 CAS 뒤에만 수행한다. 입력 미리보기·Undo/Redo·취소·실패·응답 유실·늦은 입력·cold 복원을 기존 수명 규칙으로 처리한다. 부모/참조/외부 원본 편집·override 입출력 변경·구형 profile 자동 migration은 지원 대상에 추가하지 않는다.

이번 흐름의 종료 조건은 native/void 반환과 out의 실제 실행, 원문/instance 문맥 보존, 함수와 호출자 명시 전환·sync 복귀·재활성화, Review/CAS 및 UI 실패/복원, 독립 LF/CRLF와 새 패키지/전체 복원 통과다. 새/직접 소유 내부 본문 전환은 다음 유한한 M4 흐름이다. M11/M12 및 완료한 일반 완료/속성/Set을 조합별 잔여로 다시 열지 않는다. V1 검증 잔여·V2–V9와 팩/backend/종류 결정·실제 기기/전체 UI/Space 전달은 별도다.

완료 계약을 가진 피호출자를 다시 async로 바꿀 때, 동기 caller가 남아 있다는 이유로 후보 저장 자체가 막히던 결함을 수정했다. 전환 후보 전용 Describe는 나머지 구조·원문을 계속 검사하면서 `pendingAsyncCallers`를 명시한다. 일반 화면 Describe와 Assemble/실행은 같은 호출을 계속 오류로 거절한다. 동기 caller의 flag나 원문을 자동 변경하지 않으며 Review는 diff·소유 범위 검토를 유지하며, 명시 전환 후에만 Confirm의 후보 컴파일·실행이 성공한다.
