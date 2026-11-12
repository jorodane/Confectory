# 원래 native C# out→값 전환

고정7/8행의 직접 소유 동기 scalar-return C# 기능과 일반 직접 Blueprint 호출자에서
out을 값 입력으로 전환한다. 기존 C# Script 형식 매개변수 영역을 사용하며 이름·타입·수·
순서·반환과 원래 C# 본문은 유지한다. 근거는 원래 v666 형식 매개변수 편집과
[V536 whole-contract 명시 역할 원칙](V536_I5_6_WHOLE_CONTRACT_SCOPE.md)이다.

공동 단위는2~8개 기능·구현별 단일 native target·공유 직접 caller다. 변환한 out은
현재 scalar 반환과 같은 타입이어야 하며, 원래 소비자를 그 반환에 직접 대응한다.
기존 값 입력과 남은 out은 identity로 유지한다. 새 값 입력은 기존 호출 계약 창에서
리터럴을 직접 지정한다. 기존 바인딩을 두 입력에 중복 재사용하지 않는 원래 규칙은
그대로다. 새 값·출력 대응을 추측하거나 기본값·ref 저장소를 만들지 않는다.

원래 source에서 각 기존 단일 후보를 먼저 독립 검증하고 내부 overlay에서 caller를
합쳐 한 Save/CAS로 저장한다. 값→out의 기존 명시 해제와 출력 identity 계획도 유지한다.
한 거래는 한 방향이며 ref·다른 타입/이름/수/순서/반환 변경·혼합 방향은 이 단위 밖이다.
public/native 이름은 별개로 보존하고 C# 본문을 자동 재작성하지 않는다.

변경하지 않은 body의 기존 read member와 receipt/readGuards를 재사용한다. BOM/CRLF·
본문 bytes·inode·mode·mtime을 보존하며 후속 설명/기능 메타데이터 저장·cold·Review/Confirm도
원래 source를 관측한다. 새 baseline·소유·권한·저장 문법·migration은 만들지 않는다.

검증은 실제 CLR out/값 ABI·반환/caller 실행, 명시 계획 거절, UI 취소·Undo/Redo·저장 실패/
재시도·응답 유실·충돌·늦은 입력·cold·Review/Confirm과 원래 source CAS를 포함한다.
LF/CRLF 독립 checkout·새 package·전체 복원을 별도 기록하며 실제 Windows/WebView2·
물리 기기·전체 UI 전수 검증과 구분한다. 구 Reference reader 제약과 새 group의 동일 세대
재검토 기준은 유지하고 과거 간헐 빈 #app 원인은 미확정으로 남긴다.

잔여는 다른 ref 역할·값 입력 추가/삭제 등의 정의 결합, opaque/private 명시 C# 계획,
선택 native callee 사이 의존성과 다른 원래 import/등록 외부 관측 결합이다. optional 조합을
새 필수로 늘리거나 M11/M12/M4를 회귀 없이 다시 열지 않는다. main과 원본/보관 증거를 유지한다.

이 out→값 명시 역할·본문 단위의 [최종 신규 43·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUT_VALUE.md)을 마쳤다.
