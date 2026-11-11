# 명시 native void→반환 추가·본문 공동 저장

고정 [정보 편집7/8행](V536_I5_6_REMAINING.md)의 여러 직접 소유 함수 편집을 같은
정보 창·한 Save로 결합한다. [원래 유한 잔여](V536_I5_6_RESIDUAL_RECONCILIATION.md)와
[명시 native 반환 삭제](V666_NATIVE_VOID.md)에 이어 void 함수에 scalar 반환을 추가한다.
기존 상세창 출력 추가·반환 타입 선택·호출 계약 확인·C# 본문 직접 검토를 사용한다.
새 UI·문법·권한·자동 변환이나 C# 재작성은 추가하지 않는다.

두 함수는 `(long amount, double real, out long count) -> void`를 갖는다. 원래 caller는
첫째 count를 둘째 amount로, 둘째 count를 자기 long 반환으로 소비한다. 반환을 long으로
직접 추가하고 새 선언·본문을 검토한다. 기존 입력·out ID·타입·역할·수·순서와 모든 기존
소비는 유지한다. 새 반환을 기존 소비에 자동 연결하거나 가상의 이전 return 선택을 만들지 않는다.
선택 본문은 기존 count 할당을 유지하며 amount+10을 반환한다. 원래와 새 caller 실행은
모두38이며 실제 생성된 provider는 원래 void/null·out34, 변경 후 long40·out34를 확인한다.

범위는 직접 소유 동기 scalar 함수2~8개, 각 직접 native 구현의 단일 target과 평범한 직접
Blueprint caller다. 입력/out 계약과 기존 바인딩을 그대로 유지하고 이전 계약에 실제 존재한
출력만 명시 identity로 대응한다. 새 반환값은 C# 본문이 직접 작성하며 기존 단일 후보의
완전한 original source 검증을 먼저 통과한다. 정·역순 동일한 후보를 기존 한 Save/CAS에
결합하고 이전 반환에 의존하는 scalar 변경·반환 삭제의 호환 out 대응 규칙도 유지한다.

기존 source 범위·helper 읽기·출력 투영·version3 receipt/readGuards, 후속 설명 Save·cold
Review·최종 Confirm을 재사용한다.64-member Review·240 source checks·2048 known source
예산, 편집하지 않은 C# bytes와 부모/외부 소유권·override 계약·권한·authored layout·
Review/Confirm을 유지한다. 실제 반환 ABI/값은 같은 임시 Main 원문에서 생성된 IInvoke를
호출해 확인한다. 제품 원문을 reflection으로 수정하거나 코드 생성을 대체하는 기능은 아니다.

역할 전환 UI·out/입출력 정의 변경, opaque/private 명시 계획과 선택 native callee 사이 의존성,
다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다. 선택 조합이나 migration을
새 필수로 늘리지 않고 M11/M12/M4를 구체적 회귀 없이 다시 열지 않는다. 구 Reference reader
제약과 같은 게시 세대 도구 사용을 유지한다. 초기 빈 #app의 과거 원인은 미확정이다.
[검증 기록](VALIDATION_V666_NATIVE_RETURN_CREATE.md)은 개발/최종·신규/재사용, LF/CRLF·UI
수명·경합·새 package/full restore·보관을 구별한다. 실제 Windows/WebView2·물리 기기·IME·
GPU/audio·전체 UI 검사와 Linux native/Chromium 자동화·Windows 교차 패키징은 별개다.

이 명시 native void→반환 추가 단위의 [최종 신규 39·재사용0 검증과 보관](VALIDATION_V666_NATIVE_RETURN_CREATE.md)을 마쳤다.
