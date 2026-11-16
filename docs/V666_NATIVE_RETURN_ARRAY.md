# 선택 C# import 함수의 정보 배열 반환

원본 v666 타입 선택기의 “여러 개”와 [기존 함수 타입 선택](V666_FUNCTION_NATIVE_TYPES.md), [배열 ABI](V666_INFORMATION_ARRAYS.md)를 고정 7/8행의 명시 계약·본문 공동 저장에 연결한다. 다음 유한 단위는 Main→선택 A→선택 B에서 두 scalar 반환을 정보별 구조체의 일차원 `T[]`로 바꾸는 한 흐름이다. 공개 입력·native 인자 별칭·값 역할·Main ABI·원래 import alias는 유지하고 두 구현과 Main의 본문을 사용자가 직접 작성한다. 네 명시 선택의 세 고유 source를 같은 원래 경로/hash/선언에서 인증하며 공유 A는 한 번만 반영한다. 기존 구조체 단일 반환과 입력 전환은 보존한다.

기존 `SignatureTypes`는 배열 원소의 CLR 타입을 선택 증거 key로 사용한다. 새 array proof나 schema/profile/receipt 필드는 만들지 않는다. 공개/native 선언과 본문·함수별 source proof는 `T[]` cardinality를 별도로 보존한다. 원소 proof를 배열 이름의 key로 위장하거나 캡처 선언의 배열 여부를 바꾸면 거절한다. C# 편집기는 배열 반환에도 원래 native 입력 이름을 표시하며 readonly 인자 draft가 이를 덮지 않는다.

배열의 값·순서·별칭은 기존 C# 배열 의미를 따른다. 타입 선택 자체는 배열·객체·provider를 만들거나 본문을 변환하지 않는다. 실제 검증 본문은 두 원소를 명시 생성하고 같은 배열 alias를 통해 첫 struct를 수정한다. 원래70·편집73, 두 번째 원소의 값·순서 보존을 실행 기준으로 둔다. 이미 등록된 외부 원소 정의는 원래 readonly 타입/등록 증거와 관측만 사용하고 외부 write를 추가하지 않는다.

종료 기준은 이전 planner의 거절 및 인자 별칭 UI 재현, 순서 독립 후보·원소 증거/배열 선언 변조·상충 source·잘못된 C# 거절, 타입 선택기 “여러 개”·취소/Undo/Redo·정상/역순 재개방·cold·실패/재시도·응답 유실·늦은 입력·프로젝트 전환, 후속 표시 Save와 Review 후 Main/A/원소 정의 충돌의 최종 CAS, 소유/등록 원소 반환, LF/CRLF 및 새 패키지/전체 ZIP 복원이다. 기존 단일 반환·입력·공유 source 증거·scalar 반환의 회귀는 구분한다. 타입/문맥별 무한 조합을 새 요구로 늘리지 않는다.

이번 전환 지원은 scalar→정보 값의 단일/일차원 배열 반환과 그대로인 scalar 값 입력이다. 참조 배열·배열 입력 전환·입력/반환 혼합 등 기존 잔여는 유지한다. jagged 배열이나 추가 역할·문맥 조합을 이번 단위로 지원하거나 새 필수 항목으로 만들지 않는다. 이번 지원 경계를 영구 금지 정책으로 확정하지 않는다. 실제 확인하지 않은 enum/interface 반환 조합 전체를 완료로 세지 않는다. 정보별 struct·종류 enum·모듈 interface, 명시 async 전환 전 sync caller 오류, override 공개 계약 금지·권한·원본 바이트·v666 배치·Review/Confirm/CAS를 유지한다. 구 reader의 새 pending 수용은 이전 패키지에서 별도 측정하고 자동 migration/downgrade하지 않는다. 실제 기기·전체 UI와 초기 빈 화면 원인은 별도 미검증/미확정으로 유지한다.

이 단위는 [신규47·재사용0 최종 검증](VALIDATION_V666_NATIVE_RETURN_ARRAY.md)을 마쳤다.
