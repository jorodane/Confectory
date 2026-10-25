# I5-6 고정 6행: 전체 본문과 호출자 저장소

아래는 첫 게시 단위의 기록이다. 후속 타입·핀/out 역할·반환 전환의 현재 지원 범위는 [전체 본문 계약 단위](V536_I5_6_WHOLE_CONTRACT_SCOPE.md)에 기록한다.

기준은 저장소 v536과 기존 `BlueprintRootContract.rootBody/inputModes`, 전체 본문 C# 편집창, `implementationContext`/`forwardCallerStorage`의 위치별 native/public 저장소 계약이다. 새로운 C# 변환·임의 저장소·별칭 스냅샷·분기/반복 의미를 만들지 않는다.

첫 완료 단위는 직접 소유한 함수 하나의 import 없는 원래 전체 본문 lift다. 기존 C# 편집창에서 사용자가 직접 작성한 본문과 값↔ref 전달을 선택하고, 보존된 원래 out 인자·반환·native 인자명/타입/순서·공개 핀·래퍼 없는 일반 Blueprint 호출자별 기존 저장소를 같은 후보와 CAS에 넣는다. 여러 target은 모두 같은 native 선언에 동의해야 한다. 원본 record/hash/정의·context·입력의 위치별 저장소·직렬 반환 경로를 재검사한다. 실제 생성기의 본문·멤버·entry를 Roslyn으로 검사하며 코드를 실행하지 않는다. 호출자의 모드 변경은 기존 연결 매핑 화면에서 명시적으로 선택한 exact-typed 저장소만 사용하고, ref에 리터럴·임의 셀을 만들지 않는다.

이 단위의 종료 조건은 기본/독립 정보 창의 실제 편집·저장·Undo/취소·실패·충돌·응답 유실·재시작·Review/Confirm, 원문/out 저장소/이전 입력과 다른 소스 보존, 집중 회귀·clean checkout·Windows 교차 패키지다. 이 첫 단위는 아래 문서의 검증을 마쳤다. 아래 잔여를 전체 6행 완료로 계산하지 않는다.

후속 직접 소유 전체 본문의 타입·핀 수·값/ref/out·반환 편집은 `V536_I5_6_WHOLE_CONTRACT_SCOPE.md`와 `VALIDATION_V536_INFORMATION_WHOLE_CONTRACT.md`에 검증 범위를 분리했다. 전체 본문 caller의 자신의 ABI를 유지한 프로젝트 소유 import·수동 C# 갱신은 `VALIDATION_V536_INFORMATION_CONTEXTS.md`의 후속 단위다.

현재 남은 6행 조작은 추가 callee 노드·locals/별칭, 별도 `forwardCallerStorage`, postCall의 명시 source/helpers 갱신이다. 이들은 현재 단위가 안전하게 거절하며 이를 완료로 계산하지 않는다. 등록/상속/copy 출처와 import receipt는 고정 7행, 중첩 private path는 5행, 공유 caller의 여러 함수는 8행, 고급 타입/표시명은 9행으로 유지한다.

후속 고정 C1/C3/C4의 직접 소유 수용 경계와 현재 잔여는 `V536_I5_6_RETAINED_SCOPE.md` 및 `VALIDATION_V536_INFORMATION_RETAINED.md`로 갱신했다. 이 문서의 이전 미완료 기록과 이후 마감 결과를 구별한다.
