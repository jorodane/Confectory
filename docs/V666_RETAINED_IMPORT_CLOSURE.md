# 소유 callee 계약과 opaque C# 호출자 공동 저장

고정 7/8행의 남은 private 및 retained/opaque 범위를 실제 저장 흐름으로 다시 대조했다. 이번 우선순위는 primitive 타입·역할 조합을 추가하는 대신, 정보 창에서 바꾼 소유 함수의 계약·C# 본문과 그 함수를 import하는 소유 root opaque C# 호출자 본문, 다른 선택 함수 본문을 한 Save로 저장하는 의존성 결합이다.

기존 단일 함수 후보는 각 명시 계획을 검증했지만 여러 함수의 후보를 결합할 때 호출자 소스를 편집 대상 함수의 구현으로 오인해 거절했다. native 매개변수 편집기도 scoped caller만 인식해 whole-caller가 있으면 편집을 열지 못했다. 원래 소스 선택창과 기존 매개변수·본문 영역에서 계획을 직접 작성하고, 기존 단일 후보 검증과 정확한 원본 closure를 재사용한다.

외부 호출자 계획은 편집 함수의 원래 typed import를 가진 직접 소유 root implementationContext C#만 분류한다. 호출자 자신의 공개/native/frame ABI와 import 별칭·위치 인자 이름, 원래 source/graph receipt, 배치·지역값·실행선은 보존한다. 사용자가 callee 역할과 본문, 호출자 본문 및 일반 호출선의 제거·출력 대응을 명시한다. 코드·cast·out 저장소·연결을 앱이 생성하지 않는다. 본문이 새 계약과 맞지 않으면 기존 C# 컴파일 오류를 유지한다.

후속 본문 Save에서는 현재 metadata의 source/whole을 확인하되, 영수증에는 최초 before 계약·source/graph 해시·물리 읽기 버전을 보존한다. 외부 caller가 callee의 편집 행 안에 있다는 이유로 이를 놓치지 않도록 실제 implementation의 Function/import로 의존성을 판별한다. 현재 본문 Save에 과거 호출선 변경 선택을 다시 넣지 않는다. 원래 선택은 검증된 영수증에 남는다.

새 저장 형식·profile·receipt·권한을 추가하지 않는다. workspace1/receipt3·nativeBodyContexts·원본/현재 해시 검증·Review/Confirm·최종 CAS를 유지한다. 명목 고급 입력 타입 범위와 외부/등록 원본 쓰기는 넓히지 않는다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류도 유지한다.

다음 우선순위는 여러 변경 계약이 하나의 retained 호출자 소스를 공유할 때의 일치 계획과 실제 소비가 있는 private 반환의 명시 대응이다. 그다음 copy/registered/forwarded 원본 관측 closure를 다룬다. 구 pending reader migration, 실제 Windows/물리 기기 및 전체 UI 검증은 별도 잔여다. 이번 표본을 모든 opaque/private 조합이나 고정 7/8행 전체 완료로 세지 않는다. 초기 빈 화면과 과거 시간 초과 원인은 미확정이다.

[새 실행21·재사용22 검증](VALIDATION_V666_RETAINED_IMPORT_CLOSURE.md)을 마쳤다.
