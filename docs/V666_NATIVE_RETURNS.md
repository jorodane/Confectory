# 명시 native 반환·본문·기존 출력 대응 공동 저장

고정 [정보 편집7/8행](V536_I5_6_REMAINING.md)의 여러 직접 소유 함수 편집을 같은
정보 창·한 Save로 결합한다. [원래 유한 잔여](V536_I5_6_RESIDUAL_RECONCILIATION.md)와
[명시 native 입력 교체](V666_NATIVE_INPUTS.md)에 이어 실제 scalar 반환 타입 변경을
연결한다. 기존 상세창 반환 타입 선택·호출 계약의 출력 대응·C# 본문 직접 검토를
사용한다. 새 UI·문법·권한·변환 정책이나 C# 자동 재작성은 추가하지 않는다.

게시157ab629에서 두 단일 후보와 원래 실행50은 유효하지만 공동 후보만 거절된다.
두 함수는 `(long amount, double real, out long count) -> long`을 갖고, 원래 caller는
첫째 반환을 둘째 amount로, 둘째 반환을 자기 long 반환으로 소비한다. 두 함수의 반환을
각각 double로 선택하고, 기존 long 소비는 호환되는 기존 out count로 명시 대응한다.
모든 값 입력·out ID·타입·역할·수·순서는 유지한다. 새 선언에 맞춘 C# 본문은 사용자가
직접 편집한다. 새 본문의 double 반환은 real이며 count는 같은 관측 helper를 사용한다.
새 실제 실행42는 첫째 out38을 둘째 입력으로 전달하고 둘째 out42를 반환한다.

runtime 검증용 임시 Main은 원래부터 작성한 같은 C# 원문을 유지하며, 실제 생성된 두
provider의 IInvoke 반환 타입·반환값·out 값을 확인한다. 원래 long40/out34, 변경 후
각 double1.25와 out38/34를 확인하고 실제 공유 caller도 실행한다. 제품의 원본을
reflection으로 수정하거나 코드 생성을 대체하는 기능은 아니다.

범위는 직접 소유 동기 scalar 함수2~8개, 각 직접 native 구현의 단일 target과 기존
평범한 직접 Blueprint caller다. void/ref·다른 입력 변경·out 정의 변경은 이 경로에
포함하지 않는다. 이전 반환과 호환되는 기존 out이 있어야 하며, 각 caller에서 모든 입력과
기존 out의 identity를 유지하고 이전 반환의 대응 out을 직접 선택한다. 전체 C# 선언·본문,
원래 source hash와 출력 선택은 기존 단일 후보 검증으로 먼저 증명한다. 기존 shared-caller
projection은 이미 증명한 앞선 출력 대응만 원래 graph 복사본에 반영한다. 그 외 입력·
C# source·선·ID를 추측해 바꾸지 않고 정·역순 동일한 후보를 원래 해시로 한 CAS에 결합한다.

입력 교체와 같은 직접 소유 source 검사를 재사용하며, 기존 helper 선언·본문·별칭과
읽기 원본은 읽기 전용이다. 기존 version3 receipt/readGuards는 native 선언·본문·caller와
원래 의존성을 보관한다. 후속 정보/함수 설명 Save·cold Review·최종 Confirm도 같은 원래
해시를 확인한다.64-member Review·240 source checks·2048 known source 예산, override
계약·부모/외부 소유권·권한·authored layout·Review/Confirm을 유지한다.

역할·out/void·입출력 정의 변경과 opaque/private C# 명시 계획, 선택 native callee 사이
의존성 및 다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다. 선택 조합이나
migration을 새 필수 목록으로 늘리지 않고 M11/M12/M4를 구체적 회귀 없이 다시 열지 않는다.
구 Reference reader 제약과 같은 게시 세대 도구 사용을 유지한다. 초기 빈 #app의 과거
원인은 미확정이다. [검증 기록](VALIDATION_V666_NATIVE_RETURNS.md)은 개발/최종·신규/재사용과
LF/CRLF·UI 수명·경합·새 package/full restore·보관을 구별한다. Linux native/Chromium 자동화와
Windows 교차 패키징은 실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 검사와 별개다.

이 명시 native 반환·본문·출력 대응 단위의 [최종 신규 39·재사용0 검증과 보관](VALIDATION_V666_NATIVE_RETURNS.md)을 마쳤다.
