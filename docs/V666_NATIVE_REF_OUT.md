# 원래 native C# ref→out 전환

고정7/8행의 직접 소유 동기 scalar-return C# 기능·단일 native target·일반 직접 Blueprint
호출자에서 ref를 out으로 전환한다. 이름·타입·수·순서·반환과 원래 C# 본문을 유지하며 기존
C# Script 형식 매개변수 영역을 쓴다. 근거는 원래 v666 C# 매개변수 편집과
[V536 명시 역할/저장소 원칙](V536_I5_6_WHOLE_CONTRACT_SCOPE.md)이다.

공동 단위는2~8개 기능이다. 기존 ref 입력 바인딩은 정확한 원래 표현으로 직접 해제하고,
나머지 입력과 기존 출력은 identity로 유지한다. 새 out은 자동 연결하지 않는다.
호출자 자신의 ref 계약·저장소는 유지한다. 전환한 호출은 그 저장소에 더 이상 쓰지 않으며
새 out 결과는 기존 out 셀/스냅샷 의미를 따른다. 이 효과를 명시 해제와 실제 실행으로 검증한다.
ref를 새로 만들거나 저장소를 추정·복제하지 않는다.

원래 source의 각 기존 단일 후보를 독립 검증한 뒤 내부 overlay에서 공유 caller를 합쳐
한 Save/CAS로 저장한다. public/native 이름은 별개로 보존하고 C#를 자동 재작성하지 않는다.
원래 ref 본문이 할당 전 읽기를 한다면 out 전환은 컴파일에서 거절하며 입력을 보존한다.
한 거래는 한 방향이다. 값/out의 이전 두 방향은 유지하고 새 ref 생성·다른 역할/타입/이름/
수/순서/반환 변경이나 혼합 방향은 이 단위에서 허용하지 않는다.

변경하지 않은 body의 기존 read member·receipt/readGuards를 재사용한다. BOM/CRLF·bytes·
inode·mode·mtime과 후속 정보/기능 설명 Save·cold·Review/Confirm의 원래 source 관측을 유지한다.
새 baseline·소유·권한·저장 문법·migration은 만들지 않는다. 부모/외부 원본과 override는 보호한다.

검증은 실제 CLR ref/out ABI·반환과 원래 caller ref 저장소 효과, 명시 해제 거절, UI 취소·
Undo/Redo·저장 실패/재시도·응답 유실·충돌·늦은 입력·cold·Review/Confirm과 최종 CAS를 포함한다.
LF/CRLF 독립 checkout·새 package·전체 복원을 별도 기록하며 실제 Windows/WebView2·물리 기기·
전체 UI 전수 검증과 구분한다. 구 Reference reader 제약·새 group의 같은 세대 재검토 기준과
과거 간헐 빈 #app 원인 미확정 상태는 유지한다.

잔여는 ref를 새로 요구하는 다른 방향·값 입력 추가/삭제 등의 정의 결합, opaque/private 명시
C# 계획, 선택 native callee 사이 의존성과 다른 원래 import/등록 외부 관측 결합이다.
optional 조합을 새 필수로 늘리거나 M11/M12/M4를 회귀 없이 다시 열지 않는다. main과 보관 증거를 유지한다.

이 ref→out 명시 역할·본문 단위의 [최종 신규 43·재사용0 검증과 보관](VALIDATION_V666_NATIVE_REF_OUT.md)을 마쳤다.
