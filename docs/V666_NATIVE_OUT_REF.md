# 원래 native C# out→ref와 기존 caller ref 입력

고정7/8행의 명시 역할 전환을 직접 소유 동기 scalar-return 기능2..8개와 직접 일반 Blueprint caller에 결합한다.
각 선택 구현은 원래 단일 raw native C# target이며 공개 실행 분기·상속/override 없는 기존 경계를 유지한다.
이름·자료형·수·순서·반환을 유지하며 out→ref만 한 방향으로 바꾼다. 없어진 out의 자료형은 유지한 반환과 같아야 한다.
기존 C# 원문은 사용자가 선택한 텍스트 그대로 검사하며 자동 재작성하지 않는다.

기존 C# 창에서 out을 ref로 바꾸고 호출 계약 창에서 이미 선언된 caller의 같은 타입 ref 입력을 직접 선택한다.
이번 경로는 caller에 원래부터 존재하는 scalar ref 매개변수만 새 ref 출처로 제공한다.
값 매개변수·리터럴·local/node 결과나 out 스냅샷을 ref 저장소로 추정하지 않고 기본값/임시 셀을 만들지 않는다.
원래 입력과 출력은 직접 대응한다. 기존 out 소비자는 호환 반환값에 명시 대응하고 caller 자체 계약과 graph profile을 유지한다.

읽기 전용 caller sources 목록은 원래 scope signature에서 만들어지며 저장 시 같은 선언·타입·출처를 다시 증명한다.
명시 binding 표현은 기존 정보 타입 선택과 같은 형식이며 권한이나 새 인스턴스를 부여하지 않는다.
caller ref 선언은 원래 read/CAS 원본에 포함한다. 그 선언의 ref를 지우거나 receipt에서 해당 원본을 누락하면 저장/Confirm을 거절한다.
각 single 후보를 원본 기준으로 독립 검증하고 공유 graph를 한 후보로 합친다. 순서를 바꿔도 같은 후보여야 한다.
후속 Save·cold·Review/Confirm에서 원래 receipt/read guards·권한·소유권·authored layout을 보존한다.

실행 예제는 원래 두 `(long amount,out long count)→long` 함수와 caller의 기존 `(long first,ref long second)→long` 계약이다.
원래 C#은 count에 helper 결과를 대입하고 반환한다. 기존 out 소비자는 선택한 반환값에 대응한다.
두 provider의 CLR 매개변수는 전후 long&이고 IsOut만 true→false다. 반사 호출은 반환34·인자34로 같다.
caller 반환은38로 같지만, 기존 second ref 셀은 원래5로 남다가 전환 후38로 바뀐다. 원래 out 셀을 임의로 별칭화한 결과가 아니다.
C# UTF8 BOM·CRLF·bytes·inode·mode·mtime과 caller 자체 ABI를 유지한다.

남은 유한 고정7/8행은 값 입력 추가/삭제 등 정의 변경 결합, opaque/private 명시 C# 계획,
선택 native callee 사이 의존성과 다른 원래 import/등록 외부 관측 결합이다. 기본 역할 방향을 위한 optional type/context 조합을 필수로 늘리지 않는다.
기존 각 단위의 scalar·반환 호환·한 방향·소스 문맥 제한을 전체 계약 변경 완성으로 표현하지 않는다. M11/M12/M4는 회귀 없이 다시 열지 않는다.
정보별 C# 구조체·종류 enum·모듈 interface, override 계약과 기존 예산을 유지한다.
구 Reference reader 제약과 간헐 초기 빈 화면 원인 미확정 상태, 실제 기기·전체 UI 전수 검증의 한계를 유지한다.

이 out→ref 명시 역할·본문 단위의 [최종 신규 46·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUT_REF.md)을 마쳤다.
