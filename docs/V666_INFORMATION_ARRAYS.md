# 정보 구조체의 여러 값 필드

고정9행의 정보별 C# struct 생성에서 기존 `multiple` 값 필드를 연결한다.
원본 v666 `dist/app.js`의 `choosePropertyType`은 정보 필드에 “여러 개”를 선택하며,
`propertyTypeSummary`가 그 선택을 표시한다. 원본 ZIP SHA256은
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`다.
기존 `SchemaContracts`의 single/multiple 계약과 native 함수의 `T[]` 표현에 따라
primitive·중첩 정보·종류 값 필드를 각각 `T[]`로 생성한다. 정보는 struct, 종류는 enum,
모듈은 interface라는 사용자 결정을 유지한다. 새 문법·배치·권한 정책은 추가하지 않는다.

단일 값만 가진 기존 정의의 생성 원문·shape hash·profile은 그대로다. 직접 여러 값
필드를 가진 정의는 `information-struct-arrays-v1`을 사용하며, 원소 정의의 shape가
바뀌면 기존 의존성 key로 해당 정보·모듈·함수 산출물을 무효화한다. 모듈은 이미 지원하는
동기 메서드의 정보 입출력을 통해 이 구조체를 사용할 수 있다. 외부 원소는 기존 등록과
명시 dependency가 필요하고, 다른 nominal 원소 타입으로 바꾸면 C# 초기화도 사용자가
명시적으로 수정해야 한다. 생성기가 기존 본문을 고치거나 값을 잘라내지 않는다.

배열 필드는 일반 C# 배열의 기본값과 참조 대입 규칙을 따른다. 초기화하지 않은 필드는
null이고 struct 대입이 배열 원소를 깊이 복제하지 않는다. 빈 배열 자동 생성, 객체 ID
조회, provider 선택, 순환 구조 자동 변환은 수행하지 않는다. reference/함수 필드는
기존 별도 계약 경계로 남아 있으며, struct 값 필드로 대체하지 않는다. 기존 구조적 순환
검사와 생성 개수·필드·source 관측 예산도 유지한다.

실제 본문 편집 UI로 검증하면서 별도의 영수증 결합 결함을 재현했다. 본문 Save가
native 타입/사용처의 등록 의존성을 read guard로 보존했는데 Review의 본문 guard가 그
범위를 합치지 않아 유효한 저장 후보를 거절했다. 이제 기존 native 타입 영수증을 현재
등록·소스에 대해 다시 검증한 뒤 프로젝트 안의 해당 읽기 경로를 기대 목록에 합친다.
임의 추가 경로를 신뢰하지 않으며, 원래 hash를 새 hash로 갱신하지 않는다. 외부 접근권한,
쓰기 대상, 원자 그룹, 최종 CAS 및 명시 Review/Confirm의 의미는 그대로다.
늦은 이름·설명 입력의 후속 Save도 원래 본문/타입의 읽기 증거를 유지한다. 기존 함수
입출력 계약과 같은 표시 편집만 이 보존 경로로 인정하고, ABI mapping을 추론하지 않는다.

종료 기준은 배열 descriptor·C# 실행·의존성 key·타입 변경 거절, 원래 460px 본문 UI의
편집·취소·Undo/Redo·Save·cold·Review/Confirm, 저장 실패·응답 유실·늦은 입력과
등록 proof의 누락/변조/동시 변경 거절이다. 최종 LF/CRLF·새 패키지/전체 복원 결과는
[검증 기록](VALIDATION_V666_INFORMATION_ARRAYS.md)에서 개발 재현과 구별한다.

이전 reader는 `multiple` 문법을 읽을 수 있지만 이전 native generator는 이 값 ABI를
생성하지 못한다. nominal/enum 구 parser 비호환, 과거 rollback이 새 계약을 읽거나
실행하지 못하는 제한과 자동 migration 없음은 유지한다. 기존 원본·latest/rollback·증거를
보존하며 되돌리기 위해 현재 데이터를 구형 형식으로 덮어쓰지 않는다.

같은9행의 다른 실제 ABI closure, 살아 있는 참조 객체/접근자·수명, 함수 필드 native 생성,
모듈 async·공개 실행 결과의 계약-only closure와 DLL 순환은 남아 있다. 모듈의 일반
동기 interface에 배열 값이 통과했다는 사실을 이 잔여의 완료로 합산하지 않는다. 이 단위에
새 사용자 정책 결정은 없다. M11/M12/M4는 회귀 증거 없이 다시 열지 않는다. 실제 기기·전체
UI는 미검증이며 초기 빈 화면 원인은 미확정이다.

이 한정 범위의 [최종 신규46단계·재사용0 검증과 보관](VALIDATION_V666_INFORMATION_ARRAYS.md)을 마쳤다.
