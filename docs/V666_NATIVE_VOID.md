# 명시 native 반환 삭제·void 본문·기존 out 대응 공동 저장

고정 [정보 편집7/8행](V536_I5_6_REMAINING.md)의 여러 직접 소유 함수 편집을 같은
정보 창·한 Save로 결합한다. [원래 유한 잔여](V536_I5_6_RESIDUAL_RECONCILIATION.md)와
[명시 native 반환 변경](V666_NATIVE_RETURNS.md)에 이어 반환 삭제의 기존 void 계약을
연결한다. 기존 상세창의 반환 삭제·호출 출력 대응·C# 본문 직접 검토를 사용한다.
새 UI·문법·권한·변환 정책이나 C# 자동 재작성은 추가하지 않는다.

게시16672b90에서 각 단일 long→void 후보와 원래 실행50은 유효하지만 공동 후보는
void 계약 제한으로 거절된다. 두 함수는 `(long amount, double real, out long count) -> long`을
갖고, 원래 caller는 첫째 반환을 둘째 amount로, 둘째 반환을 자기 long 반환으로 소비한다.
두 함수의 반환을 삭제하고 기존 long 소비를 호환되는 기존 out count로 직접 대응한다.
모든 입력·out ID·타입·역할·수·순서와 기존 out 대응은 유지한다. 새 C# void 선언과 본문은
직접 검토한다. 선택 본문이 count를 같은 관측 helper로 할당하며 반환값은 만들지 않는다.
새 실행42는 첫째 out38을 둘째 입력으로 전달하고 둘째 out42를 반환한다.

원래부터 작성한 같은 임시 Main 원문이 실제 생성된 두 IInvoke의 CLR 반환 타입·반환값·
out 값을 검사한다. 원래 long40/out34, 변경 후 void/null과 out38/34, 공유 caller 실행42를
확인한다. 제품의 원문을 reflection으로 수정하거나 코드 생성을 대체하는 기능은 아니다.

범위는 직접 소유 동기 scalar 함수2~8개, 각 직접 native 구현의 단일 target과 평범한
직접 Blueprint caller다. 기존 scalar 반환을 void로 삭제하며 입력/out 계약은 바꾸지 않는다.
이전 반환과 같은 타입의 기존 out이 있어야 하고 각 caller에서 이전 반환의 대응 out을
직접 선택한다. 입력·기존 out identity와 완전한 C# 선언·본문·원래 해시를 기존 단일 후보
검증으로 먼저 증명한다. 이미 검증한 출력 대응만 원래 graph 복사본에 투영하고 정·역순
동일한 후보를 기존 한 Save/CAS에 결합한다. 자동 변환·새 반환값 추측·연결 삭제는 없다.

기존 native 반환 그룹의 source 범위·helper 읽기·출력 투영·version3 receipt/readGuards와
후속 설명 Save·cold Review·최종 Confirm을 재사용한다.64-member Review·240 source checks·
2048 known source 예산, 원래 C# 원문과 부모/외부 소유권·override 계약·권한·authored layout·
Review/Confirm을 유지한다. 기존 scalar 반환 변경의 지원도 보존한다.

역할 전환·out/입출력 정의 변경과 void에서 값을 새로 만드는 역방향, opaque/private 명시 계획,
선택 native callee 사이 의존성 및 다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다.
직접 native 입력의 역할 변경은 현재 상세창에 동일 핀의 명시 역할 전환이 연결되지 않아,
반환 삭제와 섞어 새 UI 의미를 추측하지 않았다. 기존 전체 C# 본문의 역할 편집 지원과 구별한다.
선택 조합이나 migration을 새 필수로 늘리거나 M11/M12/M4를 구체적 회귀 없이 다시 열지 않는다.
구 Reference reader 제약과 같은 게시 세대 도구 사용을 유지한다. 초기 빈 #app의 과거 원인은
미확정이다. [검증 기록](VALIDATION_V666_NATIVE_VOID.md)은 개발/최종·신규/재사용, LF/CRLF·
UI 수명·경합·새 package/full restore·보관을 구별한다. 실제 Windows/WebView2·물리 기기·IME·
GPU/audio·전체 UI 검사와 Linux native/Chromium 자동화·Windows 교차 패키징은 별개다.

이 명시 native 반환 삭제·void 본문·출력 대응 단위의 [최종 신규 39·재사용0 검증과 보관](VALIDATION_V666_NATIVE_VOID.md)을 마쳤다.
