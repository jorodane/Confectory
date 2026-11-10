# 정보 함수 계약 변경과 기존 C# 노드 보존

고정 [정보 편집9행](V536_I5_6_REMAINING.md)의 고급 함수 핀 선택을 기존 일반 C# 노드가
있는 직접 소유 Blueprint 구현에도 연결한다. 원본 v666 `dist/app.js::choosePropertyType`와
기존 명시 input/output remap 계약을 따른다. 원본 ZIP SHA256은
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다.
정보별 struct·종류 enum·모듈 interface라는 사용자 결정과 원래 카드/상세창 배치를 유지한다.

일반 동기 root의 직렬 code/call/export 구현에서 **C# 노드 자체의 서명·본문·helpers·import
계약이 같은 경우** 함수의 입력과 반환 타입을 명시적으로 변경할 수 있다. 상세 타입 선택 뒤
사용 중인 노드 입력과 writer/exit를 원래 연결 선택창에서 정확한 타입의 값으로 다시 연결한다.
삭제한 입력을 자동 지우거나 새 literal·형변환·실행선을 추정하지 않는다. 영향받은 일반 C#
호출자는 기존 chooser에서 본문 계획을 명시 작성한다. 모든 계획을 한 후보/Review/CAS에 묶는다.

노드 정의/import hash가 달라지면 기존 source record에 새 hash를 묵시적으로 붙여 통과시키지
않는다. 기존 definition hash와 실제 C# 컴파일을 검사하며, 수락한 일반 노드 record는 JSON
공백·줄바꿈·Unicode·source·helpers까지 원래 bytes를 유지한다. 최종 Confirm에서도 그 파일을
다시 쓰지 않는다. edited function을 code import로 호출하는 문맥은 source 대응이 필요하므로
이 보존 범위로 승격하지 않는다. private/whole-body/context/wrapper·async/공개 분기는 별도다.

`native-information-function-retained-code-v1`은 기존 header/manifest/graph 증거에 정확한
일반 C# record ID·path·source hash를 포함한다. 기존 scope들의 shape와 보호 초안 v2는
유지한다. 읽기 증거는 Save·cold 복원·Review·최종 CAS까지 유지하며 의미가 같은 comment나
공백만 바뀌어도 오래된 증거로 저장하지 않는다. 원래 ID·좌표·entry·핀 역할·외부 연결·원본
소유·override 계약·권한과 취소/Undo/Redo·checkpoint 실패·응답 유실·늦은 입력 보호를 재사용한다.

종료 기준은 위 고정 코드 계약의 입력 재연결과 writer/exit 선택을 원래 UI에서 저장·복원·
컴파일·실행하고 bytes/실패/CAS 회귀를 확인하는 것이다. 노드 C# 서명 자체 변경과 private/
whole-body의 명시 native 대응은 같은9행의 후속이며 가능한 타입/문맥 조합을 새 필수 목록으로
늘리지 않는다. M11/M12/M4를 새 회귀 없이 다시 열지 않는다.

살아 있는 reference의 실제 객체/접근자 연결·수명은 아직 선언 ID/$ref와 별개다. 선언 data나
객체 ID를 runtime 값 snapshot으로 바꾸지 않는다. 모듈은 현재 ordinary synchronous 요구
메서드를 투영하며 async/공개 실행 결과의 계약-only closure와 DLL 순환 처리는 남는다.
그 실행 계약을 생략하거나 기존 C#을 동기 대기로 바꾸지 않는다. 명시 async 전환 전 동기
호출자 오류라는 확정 정책을 유지한다. multiple/함수 필드 native 생성도 같은 고정 잔여다.
이번 보존 경로에 추가 사용자 결정은 필요하지 않다.

구 parser/enum reader의 비호환과 이전 authoring scope의 명시 거절은 유지한다. 이전 전체
workspace reader 실행/자동 migration이나 실제 Windows/모바일·전체 UI 완료를 뜻하지 않는다.
초기 빈 화면 원인은 미확정이며 원본·latest/rollback·증거의 기존 보관/정리 규칙을 유지한다.

이 한정 범위의 [최종 신규45단계·재사용0 검증과 보관](VALIDATION_V666_RETAINED_NATIVE_CODE.md)을 마쳤다.
