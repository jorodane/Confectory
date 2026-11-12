# 원래 native C# ref→값과 공유 caller 공동 저장

고정7/8행의 기존 역할 전환을 직접 소유 동기 scalar-return 기능2..8개와 하나 이상의 직접 일반 Blueprint caller에 결합한다.
각 선택 구현은 원래 단일 raw native C# target이며 공개 실행 분기·상속/override가 없는 기존 지원 경계를 유지한다.
별도 native/public 이름은 각각 보존하고, 매개변수 이름·자료형·수·순서와 반환은 동일한 상태에서 ref→값만 한 방향으로 바꾼다.
C# 본문은 사용자가 선택한 정확한 텍스트이며 자동 재작성하지 않는다. 기존 로컬 helper는 원래 읽기 의존성으로 보존한다.

기존 C# 창의 밝은 형식 매개변수에서 ref를 제거하면 호출 계약 갱신 창이 열린다.
사용자는 원래 입력 바인딩과 기존 출력 소비자를 identity로 직접 선택한다. 원래 ref 입력을 그대로 값으로 읽고
callee의 쓰기는 caller 저장소에 전달하지 않는다. 리터럴·새 저장소·임시 ref 셀을 만들거나 원래 바인딩을 해제하지 않는다.
이 단위에서 다른 입력으로 교체하거나 새 ref를 요구하는 역방향·혼합 방향은 거절한다.
전체 원래 single 후보를 각각 증명한 뒤 공유 graph를 합치고, 원래 소유자·구현·본문·caller hash로 한 후보/CAS를 구성한다.
후속 Save·Review/Confirm·cold에서 원래 source/read guards를 유지하며 실패/경합 시 checkpoint와 입력을 보존한다.

실행 fixture는 두 `(long amount, ref long count)→long` 함수를 같은 C# 본문 그대로 값 매개변수로 바꾼다.
본문은 count의 기존 값을 읽고 helper를 통해 더한 뒤 count에 대입하고 반환한다.
실제 provider 반환은38로 같지만, caller의 연결된 두 호출은79→46이며 원래 ref 셀은79→5가 된다.
명시한 쓰기 전달 제거의 결과를 검사하며 프로그램 결과가 같다고 주장하지 않는다. caller 자체의 ref 계약은 유지한다.
UTF8 BOM·CRLF 원문, IDs·연결·authored layout과 권한·override 계약을 보존한다.

이 단위는 기존 ref→out·값/out 양방향과 일반 본문 편집을 유지한다.
남은 유한 고정7/8행은 실제 기존 저장소를 요구하는 값/out→ref, 값 입력 추가/삭제 등 정의 결합,
opaque/private 명시 C# 계획과 선택 native callee 의존성·다른 원래 import/등록 외부 관측 결합이다.
optional type/context 조합을 새 필수로 늘리지 않는다. M11/M12/M4는 회귀 없이 다시 열지 않는다.
구 Reference reader는 새 타입을 거절하는 과거 제약을 유지하고 자동 migration/downgrade를 약속하지 않는다.
간헐 초기 빈 #app의 원인은 미확정이다. 실제 기기와 전체 UI 전수 검증은 별도 잔여다.

이 ref→값 명시 역할·본문 단위의 [최종 신규 43·재사용0 검증과 보관](VALIDATION_V666_NATIVE_REF_VALUE.md)을 마쳤다.
