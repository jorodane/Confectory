# Private 미사용 double→long 반환과 out 연결 유지

고정 7/8행의 private ABI/body 명시 계획에 원래 methods-v1 소유 qualified next-code, 원래 두 long 인자(첫 값·마지막 out), 사용되지 않는 native double 반환을 long으로 바꾸는 유한 범위를 추가한다. input/out 선언·소비·부모 frame/public/native ABI·locals·실행선·배치·선택 밖 소스와 최초 읽기 버전을 유지한다.

원래 scope의 node arguments·local sources·exits에서 암시적/명시적 return 소비를 검사하고, 소비가 있으면 별도의 명시 대응 전까지 거절한다. 원본 소비의 유효성은 원래 double frame/root C# 어댑터 또는 double sink를 포함해 실제로 검증한다. 후보가 그 어댑터나 소비를 추가·변경하는 것은 허용하지 않는다. out 소비는 독립적으로 유지한다.

축소 C#이 컴파일되지 않으면 CS0266을 유지한다. 캐스트·반환문·본문·helper는 사용자가 직접 작성하며 앱은 checked/unchecked/반올림·기본값·저장소·연결을 선택하거나 생성하지 않는다. 테스트에 명시된 checked long 캐스트는 작성된 C#의 한 예이며 제품의 자동 정책이 아니다. 다른 타입·역할·인자 수·부모 ABI는 별도 계획이다.

기존 반환 타입 영역과 원본에서 계산한 읽기 metadata만 사용하고 새 저장 schema/profile/receipt를 추가하지 않는다. workspace1/receipt3·nativeBodyContexts·원본/현재 whole·소유권/권한·Review/Confirm·최종 CAS를 유지한다. 이전 pending 거절과 확정 일반 source 컴파일은 별도로 검증한다. 실제 Linux UI·모의 DOM·실제 Windows/기기·전체 UI 미검증을 구분한다. 초기 빈 화면 원인은 미확정이다.

[새 실행21·재사용27 검증](VALIDATION_V666_PRIVATE_NODE_OUT_NARROW.md)을 마쳤다.
