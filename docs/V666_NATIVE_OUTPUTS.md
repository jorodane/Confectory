# 명시 native out 타입·본문·소비자 공동 저장

고정 [정보 편집7/8행](V536_I5_6_REMAINING.md)의 기존 출력 타입 편집을 여러 직접 소유
C# 함수의 한 Save에 연결한다. [원래 유한 잔여](V536_I5_6_RESIDUAL_RECONCILIATION.md)와
[반환 추가](V666_NATIVE_RETURN_CREATE.md)에 이은 출력 편집 단위다. 기존 상세창에서
out 타입을 고르고, 호출 계약의 기존 출력 대응과 C# 선언·본문을 직접 검토한다.
새 UI·문법·권한·암묵 변환이나 C# 자동 재작성은 추가하지 않는다.

두 함수는 `(long amount, double real, out long count) -> long`이다. count를 double로
바꾸고 새 선언·본문을 명시한다. 기존 long count 소비자는 사용자가 선택한 기존 long
return으로 대응한다. 첫 함수의 count를 사용하던 둘째 amount와 둘째 count를 사용하던
caller 반환을 이 선택대로 바꾼다. 입력·out 이름/역할/수/순서와 반환 타입·ID·실행선은
유지한다. 원래 실행38과 변경 후38, 실제 provider의 원래 long40/out long34와 변경 후
long34/out double1.25를 구별해 확인한다. 새 out 값은 직접 작성한 `count=real`이다.

지원 경계는 직접 소유 동기 scalar 함수2~8개, 각 직접 native 구현의 단일 target과
일반 직접 Blueprint caller다. 값 입력 계약과 반환 타입은 유지한다. 바꾼 out은 원래
반환과 같은 타입이어야 한다. 기존 단일 계약의 out 이름 identity 또는 null 교체 대응을
유지하고, 화면은 이름 identity를 사용한다. 모든 원래 출력의
대응을 직접 검토하고 바꾼 out의 기존 소비자는 유지된 호환 return을 명시 선택한다.
나머지 out과 return의 대응은 identity다. 역할·입력/반환 타입·핀 수 변경이나 임의 저장소,
자동 변환·새 바인딩을 추측하지 않는다. 각 완전한 원래 단일 후보를 검증한 다음, 정·역순
동일한 공동 후보와 원래 source 해시·기존 출력 투영·한 Save/CAS로 결합한다.

기존 version3 receipt/readGuards를 저장·후속 설명 Save·cold Review·최종 Confirm까지
보존한다. 편집하지 않은 helper/C# bytes·부모/외부 소유권·override 계약·권한·authored
layout,64-member Review·240 source checks·2048 known source 예산은 유지한다.
동일 임시 Main 원문이 실제 생성 IInvoke의 CLR out 타입·값과 caller 실행을 확인하며,
제품 코드 생성을 대체하거나 reflection으로 원문을 수정하지 않는다.

역할 전환 UI·out 추가삭제/입출력 정의 변경, opaque/private 명시 C# 계획과 선택 native
callee 사이 의존성·다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다.
조합별 migration을 새 필수로 늘리거나 M11/M12/M4를 회귀 없이 다시 열지 않는다.
이전 reader의 새 그룹 재편집/검토 호환은 주장하지 않으며 같은 게시 세대 도구를 사용한다.
과거 간헐 빈 #app의 원인은 미확정이다. [검증 기록](VALIDATION_V666_NATIVE_OUTPUTS.md)에
신규/재사용과 LF/CRLF·실패/경합/응답 유실·새 package/full restore·보관을 구별한다.
Linux native/Chromium 자동화·Windows 교차 패키징과 실제 Windows/WebView2·물리 기기·
IME·GPU/audio·전체 UI 전수 검증은 별개다.

이 명시 native out 타입·본문 단위의 [최종 신규 40·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUTPUTS.md)을 마쳤다.
