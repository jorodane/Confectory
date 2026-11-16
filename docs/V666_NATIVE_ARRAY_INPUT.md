# 선택 C# import 함수의 정보 배열 입력

원본 v666 함수 타입 선택기의 “여러 개”와 [기존 배열 ABI](V666_INFORMATION_ARRAYS.md)를 고정 7/8행의 명시 계약·본문 공동 저장에 연결한다. 유한 단위는 Main→선택 A→선택 B에서 두 scalar 값 입력을 정보별 구조체 일차원 `T[]`로 바꾸는 한 흐름이다. 반환형·공개 입력 이름/순서/값 역할·원래 native 인자 이름·Main ABI·import alias를 유지한다. 네 명시 선택의 세 고유 source를 원래 path/hash/before/after 선언에서 검증하고 공유 A는 한 번만 합친다. 구현·소비 본문과 새 배열 값은 사용자가 직접 작성하며 호출자나 C# 본문을 자동 변환하지 않는다.

기존 원소 CLR 타입 proof와 함수별 원본 source scope를 사용한다. 새 array proof·receipt flag·schema 문법·권한은 없다. 배열 cardinality는 공개/native 선언으로 따로 검증한다. 바뀐 입력의 기존 binding은 명시 null mapping으로 해제하고 직접 작성한 C#에서 새 값을 전달한다. 바뀌지 않은 입력은 원래 identity mapping을 유지한다. 직접 소유 동기 함수의 scalar 반환과 입력 수·이름·순서·역할은 보존하고, 기존 단일 nominal 입력과 값/배열 반환도 유지한다.

C# 편집기는 정보 값의 단일/일차원 배열로 입력 타입을 바꿀 때 기존 native 이름을 유지한 선언을 표시한다. 보관된 readonly 인자 draft가 그 선언을 덮지 않는다. 값/ref/out·추가/삭제·rename 및 caller coupling의 기존 판정과 v666 DOM/CSS는 유지한다. 새 참조 carrier를 만들거나 ID에서 객체를 조회하지 않는다.

실제 배열 본문은 Main이 두 struct 원소를 명시 생성하고 A가 같은 배열 alias로 첫 값을71로 바꾼 뒤 B에 전달한다. B의 scalar 반환은73이며 Main은 원래 배열의 첫 값71·둘째 값1·순서/길이를 확인한다. 기존 단일 struct 입력의 같은 편집기 경로는 Main의 원래 값40이 유지되고 결과73인지 회귀로 구분한다. 이는 기존 C# 배열 별칭과 struct 값 복사 의미이며 새 깊은 복사·초기화 정책이 아니다. 등록 외부 원소로의 변환도 명시 C#으로 작성하고 외부 source·등록 proof는 readonly 관측으로 보존한다.

종료 기준은 온전한 게시 패키지에서 원래70·새 계획 거절·Save 전 인자 이름 유실 재현, 순서 독립 후보·원소 proof/배열 선언 변조·상충 본문·잘못된 C# 거절, 원래 입력 선택기의 여러 개·취소/Undo/Redo·정상/역순 재개방·cold·실패/재시도·응답 유실·늦은 입력·프로젝트 전환, 후속 표시 Save·Review 후 Main/A/원소 정의 충돌의 최종 CAS, 소유/등록 원소 및 LF/CRLF·새 패키지/전체 ZIP 복원이다. 이미 검증한 이전 source를 다시 빌드하는 대신 그 온전한 패키지를 해시/모드와 함께 추출해 기준 흐름을 새로 검사한다.

참조 배열·입력/반환 혼합과 다른 기존 opaque 문맥은 별도 잔여다. jagged 배열이나 추가 타입/문맥 조합을 새 필수 행으로 늘리지 않는다. 이번 지원 경계를 영구 금지 정책으로 확정하지 않는다. override 공개 계약·외부 쓰기 금지, 정보별 struct·종류 enum·모듈 interface, 명시 async 전환 전 sync caller 오류, 원본 바이트·Review/Confirm/CAS와 예산을 유지한다. 이전 pending guard 수용은 같은 패키지에서 별도로 측정하고 자동 migration/downgrade하지 않는다. 실제 기기·전체 UI는 미검증이며 초기 빈 화면 원인은 미확정이다.
