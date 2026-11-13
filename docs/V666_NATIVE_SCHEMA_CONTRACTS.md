# 기존 scalar 속성과 native 계약·본문의 한 저장

고정8행의 같은 정보 창에서 기존 속성 타입 선택과 여러 함수 계약·본문 편집을 한 Save로 결합한다.
게시 `aaf9ef53`에서 직접 소유한 scalar 필드 편집과 이미 지원한 native ABI/body/caller 그룹은
각각 유효했지만 결합은 거절됐다. 원래 타입 선택창과 함수/C#·호출 대응 창에서 같은 거절과
다섯 입력·원문·checkpoint 보존을 관측했다. 새 UI나 자동 C# 치환은 추가하지 않는다.

이번 경계는 직접 소유한 기존 단일 scalar 필드 하나의 명시 타입 선택과 함수2..8개의
기존 명시 native 계약·본문 계획이다. 소유 정보의 설명·아이콘은 각각 하나까지 유지하며 전체는 최대11행이다.
기존 `nativeType` 형식과 현재 타입 선택창의 scalar `definition`/`sources:null` 형식을 모두 분류한다.
분류 중에만 필드 행을 분리하고, 완전한 원래 선언은 InformationDefinitions의 원래
schema ID/hash·필드 계약·기본값/사용처·참조 검증과 동일한 후보·checkpoint CAS에 남긴다.
현재 타입 목록 조회가 추가로 관측한 기존 등록 파일도 관측 증거에서 제거하지 않는다.

일반 scalar는 bool/int/long/float/double/string의 기존 타입을 사용한다. 필드 ID·개수·순서와
기본값 JSON 원문을 자동 변환하지 않는다. 명시 선택과 기존 데이터/사용처가 충돌하면 전체 거절한다.
새 필드·삭제·중첩/array/reference/compound 정의·외부 schema 쓰기·새 source proof는 이 분류로 허용하지 않는다.
공개 override·부모/팩 원본·C# 원문 소유권·권한·authored layout·Review/Confirm·최종 CAS를 유지한다.

검사는 기존 Scale 필드의 long→double과 명시 native out/반환·본문·공유 caller를 함께 저장한다.
Scale의 기본값7과 다른 Power 필드의 정확한64비트 기본값, 다른 필드/참조와 비선택 C#을 보존한다.
계약을 바꾸지 않는 본문 그룹과 입력 ABI 그룹도 같은 분류/원본 읽기 범위를 확인한다.
그룹에 속성 편집을 넣기 전후의 native/caller 변경 bytes가 같고, 행 순서에 무관한 한 후보여야 한다.
stale/foreign/중첩/중복·지원 밖 정의·부적합 기본값과 불완전한 ABI 계획은 전체 거절한다.
같은 계약에서 본문 변경을 생략하여 원문을 유지하는 기존 경로는 불완전한 ABI 전환으로 취급하지 않는다.

실제 Linux 엔진·Chromium의 취소·Undo/Redo·실패/재시도·응답 유실·cold·Review/Confirm,
원본 경합·늦은 입력·후속 저장·새 패키지/전체 복원을 별도 기록한다.
새 문법·receipt 버전·정보별 struct/종류 enum/모듈 interface 정책이나 자동 migration을 추가하지 않는다.
같은 게시 세대의 저장·재편집 기준이며 이전 authoring 세대의 조합 receipt 호환/downgrade를 보장하지 않는다.
구 Reference reader 제약과 초기 빈 화면 원인 미확정, 실제 기기·전체 UI 미검증은 구별한다.
기존 속성 타입 Undo 뒤 포커스가 BODY로 이동해 연속 Redo가 소유 창에 전달되지 않는 경계도 관측했다.
이번 단위는 원래 속성 버튼을 명시한 Undo/Redo의 입력 보존을 검사하며 자동 포커스 복원은 별도 잔여다.

이 원래 조작의 정상/거절·입력/원문 보존·실제 저장/실행 증거를 이번 단위의 종료 기준으로 삼는다.
남은 다른 복합 계약·속성 생성/삭제 및 구조 편집, opaque/private 명시 C# 계획,
선택 native 의존성과 기존 import/등록 외부 원본의 closure는 같은 고정7/8행에 유지한다.
타입·문맥의 가능한 모든 조합을 새 필수 항목으로 늘리지 않으며 M11/M12/M4는 회귀 없이 다시 열지 않는다.

이 scalar 속성·native 계약 공동 저장 단위의 [최종 신규 50·재사용0 검증과 보관](VALIDATION_V666_NATIVE_SCHEMA_CONTRACTS.md)을 마쳤다.
