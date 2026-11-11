# 명시 native out 삭제·본문·소비자 공동 저장

고정 [정보 편집7/8행](V536_I5_6_REMAINING.md)의 출력 삭제를 여러 직접 소유 C# 함수의
한 Save에 연결한다. [원래 유한 잔여](V536_I5_6_RESIDUAL_RECONCILIATION.md)와
[out 타입 변경](V666_NATIVE_OUTPUTS.md)에 이은 출력 정의 편집 단위다. 기존 상세창에서
out을 삭제하고, 원래 소비자의 호환 출력 대응과 새 C# 선언·본문을 직접 검토한다.
새 UI·문법·권한·C# 자동 재작성이나 암묵 출력 삭제는 추가하지 않는다.

두 함수의 `(long amount, double real, out long count) -> long`에서 count를 삭제한다.
기존 count를 쓰던 둘째 호출의 amount와 caller의 반환은 명시 선택한 기존 long return으로
대응한다. 새 본문은 `return calls.StableHelper.Invoke(checked(amount+1));`로 직접 작성한다.
원래 provider의 long40/out long34와 변경 후 long34·out 매개변수 부재를 실제 CLR 계약에서
구별한다. caller는 전후 모두38이다. 입력·반환 타입·남은 핀 ID·순서·실행선과 원본은 유지한다.

지원 경계는 직접 소유 동기 scalar 함수2~8개, 각 직접 native 구현의 단일 target과 일반
직접 Blueprint caller다. 삭제한 out은 기존 반환과 호환되는 같은 타입이어야 하며, 원래
args에서 null로 삭제를 명시한다. 모든 원래 출력의 대응을 검토하고 삭제한 out의 소비자는
유지된 호환 return을 직접 선택한다. 남은 입력/out은 이름·타입·역할·순서와 identity 대응을
유지한다. 모든 완전한 원래 단일 후보를 먼저 검증한 뒤 정·역순 동일한 공동 후보와 원래
쓰기 해시·기존 출력 투영·한 Save/CAS로 결합한다. 새 핀·기본값·저장소를 추측하지 않는다.

후속 설명 Save와 cold Review는 이미 저장한 정확한 선언 hash·원래 receipt/source를
확인한 뒤 삭제 형태만 인증한다. 이 읽기용 형태 대조는 새 계약·본문 계획을 만들거나
원래 baseline을 재설정하지 않는다. 기존 같은 수의 이름/타입/반환 변화 대조는 유지하며
그 외 입력 삭제·순서/역할 변경·새 out·혼합 구조 변경을 이 경로로 받아들이지 않는다.

기존 version3 receipt/readGuards·Review/Confirm·최종 CAS, 편집하지 않은 C# bytes와
부모/외부 소유권·override 계약·권한·authored layout을 유지한다.64-member Review·240 source
checks·2048 known source 예산은 그대로다. 동일 임시 Main 원문으로 실제 생성 IInvoke의
매개변수 수·타입·값과 caller를 실행하며 제품 코드 생성/원문을 reflection으로 대체하지 않는다.

역할 전환 UI·out 추가/다른 입출력 정의 변경, opaque/private 명시 C# 계획과 선택 native
callee 사이 의존성·다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다.
조합별 migration을 새 필수로 늘리거나 M11/M12/M4를 회귀 없이 다시 열지 않는다.
이전 reader의 새 그룹 재편집/검토 호환은 주장하지 않으며 같은 게시 세대 도구를 사용한다.
과거 간헐 빈 #app의 원인은 미확정이다. [검증 기록](VALIDATION_V666_NATIVE_OUT_REMOVAL.md)에
신규/재사용·LF/CRLF·실패/경합/늦은 입력·새 package/full restore·보관을 구별한다.
Linux native/Chromium 자동화·Windows 교차 패키징과 실제 Windows/WebView2·물리 기기·
IME·GPU/audio·전체 UI 전수 검증은 별개다.

이 명시 native out 삭제·본문 단위의 [최종 신규 41·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUT_REMOVAL.md)을 마쳤다.
