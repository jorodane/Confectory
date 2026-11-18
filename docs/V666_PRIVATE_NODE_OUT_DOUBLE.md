# Private 미사용 long→double 반환과 out 연결 유지

고정 7/8행의 명시적 private ABI/body 계획에 원래 methods-v1의 소유 qualified next-code, 원래 두 long 인자(첫 값·마지막 out), 사용되지 않는 long native 반환을 double로 바꾸는 유한 범위를 추가한다. 기존 void 전환도 유지한다. 모든 input/out 선언·소비·부모 frame/public/native ABI·locals·실행선·배치·선택 밖 소스와 원래 읽기 버전을 유지한다.

원래 scope의 node arguments·local sources·exits에서 암시적/명시적 return 소비를 조사하고, 소비가 있으면 명시적 별도 대응 없이 후보를 거절한다. out 소비는 독립적으로 유지한다. 원래 반환 사용처를 cast/remap하지 않는다. 다른 타입·역할·인자 수·부모 ABI 변경은 별도 계획이다.

사용자가 반환 선언을 명시하면 C# compiler가 그 선언에 따라 원문을 컴파일한다. 앱은 원문·helper·cast·반환문·저장소·연결을 생성하지 않는다. 원문 그대로 컴파일되는 사례와 분수 반환을 직접 작성한 사례를 구분한다. 값 없는/누락된 반환, out 미할당과 할당 전 읽기는 compiler가 거절한다. 기존 반환 타입 영역과 원본에서 계산한 editableNativeReturnTypes 읽기 metadata를 쓰며 새 저장 schema/profile/receipt는 만들지 않는다.

기존 workspace1/receipt3·nativeBodyContexts·원본/현재 whole 서명·읽기/소유권/권한·Review/Confirm·최종 CAS를 보존한다. 이전 reader의 pending 거절과 확정 일반 source 컴파일 호환성은 별도로 검증한다. 실제 Linux engine/Chromium·모의 DOM·실제 Windows/기기·전체 UI 미검증을 구분한다. 초기 빈 화면 원인은 미확정이다.

[최종 신규48·재사용0 검증](VALIDATION_V666_PRIVATE_NODE_OUT_DOUBLE.md)을 마쳤다.
