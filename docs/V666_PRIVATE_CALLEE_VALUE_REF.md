# 선택 callee 값→ref와 private C# 본문 공동 저장

고정7/8행의 직접 소유 동기 scalar C# 함수에서 선택 callee의 원래 값 입력 하나를 ref로 바꾸는 명시 계획을 private 본문·보조 함수 편집과 함께 저장한다. 근거는 [기존 값→ref 저장소 계약](V666_NATIVE_VALUE_REF.md)과 [선택 callee ref→out의 원래 source 결합](V666_PRIVATE_CALLEE_REF_OUT.md)이다.

두 원래 호출자에 이미 존재하는 같은 타입의 ref 저장소를 사용자가 각각 직접 선택해야 한다. 기존 amount·count 입력과 반환은 identity로 유지하고 해제는 없다. ref에 리터럴·새 임시 셀·기본 저장소를 만들지 않는다. caller 자신의 ref 계약과 private 노드의 값 ABI, native 이름·자료형·수·순서·반환은 유지한다. C# 본문과 보조 함수는 사용자가 명시한 텍스트만 적용한다.

각 계획을 원래 source에서 독립 검증한 뒤 변경 callee와 그 원래 호출 관측을 한 overlay에서 결합한다. 순서와 무관한 한 후보를 기존 한 Save·Review/Confirm·최종 CAS로 처리한다. caller·저장소·source·native 별칭 증거 누락/변조와 다른 역할·타입·반환 변경을 거절한다. 단독 Contracts/Graphs/NativeRoles와 assembled C#가 권위이며 권한·소유·저장 문법·receipt 필드를 추가하지 않는다.

기존 C# Script 매개변수 영역과 호출 계약 갱신 창을 사용한다. 첫 owner Save 전 재진입과 readonly draft 복원에서 수동 ref 계획과 별칭을 유지한다. 거절된 입력은 bodyDrafts에 남기고 취소·Undo/Redo·cold·실패/재시도·응답 유실·늦은 입력·후속 Save를 확인한다. parent/private ABI·경로·배치·정확한 local과 선택 밖 source bytes/mtime는 유지한다.

fixture의 원래115/ref5는 명시 편집 후56/ref19가 된다. private 직접 호출37/ref12와 callee 직접 호출42/ref12를 CLR에서 별도로 확인한다. 이는 사용자가 선택한 ref 쓰기의 결과이며 원래 실행 결과 보존을 주장하지 않는다. 원래 값 호출에 리터럴5가 있는 프로그램도 실제115/ref5 실행이 유효함을 확인한 뒤 새 ref 후보를 거절해야 한다.

LF/CRLF 격리 checkout·실제 엔진/Chromium·새 package·전체 ZIP 복원을 구분해 기록한다. 모의 renderer는 실제 엔진/CLR 증거와 구분한다. 이전 guard의 새 pending 거절과 Confirm된 일반 source의 이전 CLI 빌드/실행 호환성은 별도 확인하며 자동 migration/downgrade를 의미하지 않는다.

이 단위는 private 노드 자체 ABI 변경을 완료하지 않는다. 다른 callee 역할/고급 ABI·retained/opaque 및 외부 관측 결합, 구 Reference reader 일반 호환성·실제 Windows/WebView2·물리 기기·전체 UI는 잔여다. 과거 초기 빈 화면과 이전60초 result timeout 원인은 미확정으로 유지한다. 원본·latest/rollback·기존 증거와 정리 범위를 보존하고 main은 사용자 검토에 남긴다.

[Private 본문·선택 callee 값→ref](V666_PRIVATE_CALLEE_VALUE_REF.md)는 [최종 신규48·재사용0 검증](VALIDATION_V666_PRIVATE_CALLEE_VALUE_REF.md)으로 두 caller의 기존 ref 저장소 명시 선택·리터럴/새 셀 거절·원래 ABI와 한 Save/읽기/CAS 흐름을 마쳤다. private 노드 자체 ABI·retained/opaque·다른 역할/고급 ABI와 reader/기기/전체 UI는 잔여다.
