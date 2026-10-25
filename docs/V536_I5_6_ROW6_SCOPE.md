# I5-6 고정 6행: 전체 본문과 호출자 저장소

기준은 저장소 v536과 기존 `BlueprintRootContract.rootBody/inputModes`, 전체 본문 C# 편집창, `implementationContext`/`forwardCallerStorage`의 위치별 native/public 저장소 계약이다. 새로운 C# 변환·임의 저장소·별칭 스냅샷·분기/반복 의미를 만들지 않는다.

첫 완료 단위는 직접 소유한 함수 하나의 import 없는 원래 전체 본문 lift다. 기존 C# 편집창에서 사용자가 직접 작성한 본문과 값↔ref 전달을 선택하고, 보존된 원래 out 인자·반환·native 인자명/타입/순서·공개 핀·래퍼 없는 일반 Blueprint 호출자별 기존 저장소를 같은 후보와 CAS에 넣는다. 여러 target은 모두 같은 native 선언에 동의해야 한다. 원본 record/hash/정의·context·입력의 위치별 저장소·직렬 반환 경로를 재검사한다. 실제 생성기의 본문·멤버·entry를 Roslyn으로 검사하며 코드를 실행하지 않는다. 호출자의 모드 변경은 기존 연결 매핑 화면에서 명시적으로 선택한 exact-typed 저장소만 사용하고, ref에 리터럴·임의 셀을 만들지 않는다.

이 단위의 종료 조건은 기본/독립 정보 창의 실제 편집·저장·Undo/취소·실패·충돌·응답 유실·재시작·Review/Confirm, 원문/out 저장소/이전 입력과 다른 소스 보존, 집중 회귀·clean checkout·Windows 교차 패키지다. 이 첫 단위는 아래 문서의 검증을 마쳤다. 아래 잔여를 전체 6행 완료로 계산하지 않는다.

남은 6행 조작은 전체 본문의 이름·타입·핀 수·out 역할·반환 변경과 추가 본문/alias가 있는 forwardCallerStorage, whole-body 호출자와 postCall 래퍼가 있는 호출 문맥이다. 이들은 기존 native/public/호출자 저장소 식별성과 명시적 출력·반환 대응을 함께 검증해야 하며 현재 단위가 안전하게 거절한다. 등록/상속/copy 출처와 import receipt는 고정 7행, 중첩 private path는 5행, 공유 caller의 여러 함수는 8행, 고급 타입/표시명은 9행으로 유지한다.

원본 레이아웃·권한·명시적 Review/Confirm은 유지한다. 실제 Windows/모바일 실행과 Library 전달은 미검증이며 사용자 계정/유료 AI/사용자 프로젝트 Run은 수행하지 않는다.
