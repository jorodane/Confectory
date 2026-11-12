# 명시 native out 추가·본문 공동 저장

고정 [정보 편집7/8행](V536_I5_6_REMAINING.md)의 출력 추가를 여러 직접 소유 C# 함수의
한 Save에 연결한다. [원래 유한 잔여](V536_I5_6_RESIDUAL_RECONCILIATION.md)와
[out 삭제](V666_NATIVE_OUT_REMOVAL.md)에 이은 출력 정의 편집 단위다. 기존 상세창에서
새 out 이름·타입을 고르고, 원래 호출 계약 대응과 새 C# 선언·본문을 직접 검토한다.
새 UI·문법·권한·C# 자동 재작성이나 기본값·새 소비자 연결은 만들지 않는다.

두 함수의 `(long amount, double real) -> long`에 `out double count`를 추가한다.
새 본문은 `count=real;return calls.StableHelper.Invoke(checked(amount+1));`로 직접 작성한다.
입력 두 개와 long 반환, 첫 반환을 둘째 amount로 사용하는 호출과 최종 반환은 그대로다.
원래 provider의 long34·out 부재와 변경 후 long34/out double1.25를 실제 CLR 계약에서
구별한다. caller는 전후 모두38이다. 새 out은 사용할 수 있으나 원래 소비자에 자동 연결하지 않는다.

지원 경계는 직접 소유 동기 scalar 함수2~8개, 각 직접 native 구현의 단일 target과 일반
직접 Blueprint caller다. 원래 매개변수·반환은 이름·타입·역할·수·순서와 identity 대응을
유지한다. 기존 UI처럼 매개변수 끝에 이름이 중복되지 않는 scalar out만 추가한다.
원래 모든 출력의 대응은 identity이며 이전에 없던 출력의 대응을 지어내지 않는다.
완전한 원래 단일 후보마다 새 out을 직접 할당하는 C# 본문을 먼저 검증한 뒤 정·역순
동일한 공동 후보와 원래 쓰기 해시·한 Save/CAS로 결합한다. 입력·역할·반환 변경이나
삭제/타입 교체를 추가와 혼합해 이 경로로 추정하지 않는다.

후속 설명 Save와 cold Review는 이미 저장한 정확한 선언 hash·원래 receipt/source 아래에서
추가 형태를 인증한다. 기존 읽기 전용 형태 대조를 재사용하며 새 계약/본문 계획을 만들거나
원래 baseline을 재설정하지 않는다. 기존 out 삭제의 실제 ABI·후속 저장·원본 충돌 회귀를
다시 실행한다. 기존 version3 receipt/readGuards·Review/Confirm·최종 CAS, 편집하지 않은
C# bytes와 부모/외부 소유권·override 계약·권한·authored layout을 유지한다.
64-member Review·240 source checks·2048 known source 예산은 그대로다. 동일 임시 Main
원문으로 실제 생성 IInvoke의 매개변수 수·타입·값과 caller를 실행하며 제품 코드 생성이나
원문을 reflection으로 대체하지 않는다.

역할 전환 UI·다른 입출력 정의 결합, opaque/private 명시 C# 계획과 선택 native callee 사이
의존성·다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다. 조합별 migration을
새 필수로 늘리거나 M11/M12/M4를 회귀 없이 다시 열지 않는다. 이전 reader의 새 그룹
재편집/검토 호환은 주장하지 않으며 같은 게시 세대 도구를 사용한다. 과거 간헐 빈 #app의
원인은 미확정이다. [검증 기록](VALIDATION_V666_NATIVE_OUT_ADDITION.md)에 신규/재사용·
LF/CRLF·실패/경합/늦은 입력·새 package/full restore·보관을 구별한다. Linux native/Chromium
자동화·Windows 교차 패키징과 실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI
전수 검증은 별개다.

이 명시 native out 추가·본문 단위의 [최종 신규 41·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUT_ADDITION.md)을 마쳤다.
