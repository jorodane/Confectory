# Private 본문과 원래 호출 대상의 명시 scalar 반환 변경

고정 v666 [정보7/8행](V536_I5_6_REMAINING.md)의 한 정보 창·한 Save에서 private C# 본문/helpers와 그 구현이 원래 호출하는 다른 소유 함수의 scalar 반환·C# 본문 변경을 결합하는 유한 단위다. [선택 callee 이름 대응](V666_PRIVATE_CALLEE_RENAME.md)에 기존 [scalar 반환/호환 out 선택](V666_PRIVATE_SCALAR_RETURN.md)을 연결한다.

호출 대상의 long 반환을 double로 명시 선택한다. 기존 long 입력과 long out 및 nativeAmount/nativeCount를 유지하고, private 구현의 원래 ordinary call과 공유 caller 각각의 이전 long 반환 소비자는 호환되는 원래 long out(count)을 명시 선택한다. 나머지 입력/출력 identity·바인딩·경로·배치·정확한64비트 locals와 private/frame/code ABI를 보존한다. typed import의 반환 계약과 해당 call 서명·명시 출력 대응만 기존 단독 closure로 갱신한다. 사용자가 작성한 두 C# 본문/helpers 외 C#·형변환·저장소·호출을 추론하지 않는다.

직전 온전한 package에서 원래 실행45와 두 단독 계획이 유효하고 결합 후보 거절을 먼저 측정한다. 별도 실제 UI에서는 scoped caller로 범용 native 전환이 불가할 때 기존 scalar 반환 헤더가 공개 이름으로 바뀌는 결함을 재현하고 trusted Save 거절·입력/원본 보존을 확인한다. 이 경우 기존 scalar 반환 조건만 허용해 native 별칭을 보존하며 범용 native 역할·타입 전환의 available과 권한은 유지한다. 종료 기준은 원래 두 caller의 출력 대응, 정·역순 동일 후보·실제 실행15 및 직접 native double25.5/out25, 저장 후 private/callee 본문 재편집·cold에서 최초 source/flow/import·반환 대응·물리 읽기 버전 보존이다.

각 원래 계획을 같은 원래 snapshot에서 독립 검증해 결합한다. unchanged 관측은 한 검증된 명시 변경과 결합하고 서로 다른 변경 결과는 거절한다. 현재 편집 receipt는 이미 원래 계획으로 재생 검증한 pending graph의 같은 노드와 일치해야 하며, 캡처한 최초 whole/source hash는 바꾸지 않는다. 단독 Contracts/Graphs·assembled compiler·version3 nativeBodyContexts·전체 원본 readGuards·Review/Confirm·최종 CAS를 유지한다.

기존 UI의 반환 선택·두 명시 caller 출력 대응·구현 선택·취소/Undo·실패/재시도·응답 유실·늦은 입력·창/프로젝트 경계, 실제 원본 경합과 fresh Confirm을 검사한다. LF/CRLF·새 package/전체 ZIP 복원과 완료한 선택 callee 이름 대응 및 기존 역할/struct/whole/retained/helper 회귀를 구분한다. 구 guard의 새 pending 거절과 구 CLI의 확정 일반 source 실행을 따로 측정한다. schema/workspace version1·receipt version3와 기존 예산·권한·소유권·authored layout을 유지한다.

정보별 C# struct·종류 enum·모듈 interface, 명시 async 전환 전 sync caller 오류를 유지한다. 다른 callee 입력 타입·역할·반환 구조, private ABI·retained/opaque import·외부 관측은 별도 잔여다. 가능한 조합으로 필수 매트릭스를 늘리지 않는다. 구 Reference reader·Windows/WebView2/물리 기기·전체 UI는 별도이며 초기 빈 화면 원인은 미확정이다. 원본·latest/rollback·증거·main을 보존한다.

이 유한 흐름은 [최종 신규48·재사용0 검증](VALIDATION_V666_PRIVATE_CALLEE_RETURN.md)을 마쳤다.
