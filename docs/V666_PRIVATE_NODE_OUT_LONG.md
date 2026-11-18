# Private 노드의 void→long 반환 생성과 out 연결 유지

기존 고정 7/8행의 명시적 private ABI/body 계획에 다음 유한 범위를 추가한다. 원래 methods-v1의 소유 qualified next-code이고 원래 두 long 인자(첫 value, 마지막 out)와 정확한 첫 입력 연결을 보유한 void 반환을 long으로 바꾼다. out 이름 return은 제외한다. 새 native 반환은 자동 연결하지 않는다. 기존 input/out 소비·부모 frame/public/native ABI·locals·실행선·배치·선택 밖 소스와 물리 읽기를 유지한다.

원래 scope의 node arguments·local sources·exits를 조사하고, 존재하지 않는 void return을 원래 참조하면 기존 정의 검사 또는 후보 검사에서 거절한다. 이 전환으로 잘못된 원본을 암묵적으로 복구하지 않는다. 원본 out 소비는 그대로 유효하다. 새 반환 소비 연결·다른 타입/역할/인자 수·부모 ABI 변경은 별도 명시 계획이다.

본문/helpers·반환문·out 할당은 사용자가 직접 작성한다. 컴파일러가 값 없는 반환·반환 누락·out 미할당·할당 전 읽기를 거절한다. 기본값·cast·저장소·반환문·연결을 자동 생성하지 않는다. 기존 반환 타입 영역과 원본에서 계산한 editableNativeReturnTypes 읽기 metadata를 쓴다. 저장 schema/profile/receipt를 추가하지 않는다.

기존 workspace1/receipt3·nativeBodyContexts·원본/현재 whole 서명·읽기/소유권/권한·Review/Confirm·최종 CAS를 보존한다. 이전 reader의 새 pending 수용과 Confirm된 일반 소스 컴파일은 별도로 검증한다. 실제 Linux engine/Chromium, 모의 DOM, 실제 Windows/기기·전체 UI 미검증을 구분한다. 초기 빈 화면 원인은 미확정이다.

[최종 신규48·재사용0 검증](VALIDATION_V666_PRIVATE_NODE_OUT_LONG.md)을 마쳤다.
