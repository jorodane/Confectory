# 공유 retained 호출자의 입력 타입과 callee 공동 저장

기준 `8ea5f0254f37d02386225e9556e4f569e1dae989`의 이름 변경 결합을 보존하고, 일반 Blueprint caller의 한 scalar 값 입력 타입 변경을 native callee의 입력 이름·수동 C# 본문과 같은 정보 창 Save에 결합한다. 원래42와 두 개별 후보가 유효한 상태에서 온전한 직전 패키지가 공동 후보를 거절함을 먼저 재현했다.

대표 요청은 caller amount의 long→string, callee amount→rightAmount 및 callee의 수동 뺄셈 본문이다. 사용자가 바깥 호출자의 새 문자열 값과 기존 long 연결의 해제를 명시하고, caller 내부에서 옛 amount를 사용하던 callee 입력에는 long 값30을 직접 선택한다. 새 문자열을 숫자로 변환하거나 기존 C#을 다시 쓰지 않는다. 따라서 프로그램22는 명시한 숫자 대체값과 callee 본문 변경의 결과이며, 문자열을 자동 해석한 결과가 아니다.

두 원본 단일 closure를 먼저 검증한다. 원본 해시를 가진 타입 대체 계획은 caller에 먼저 적용하고, callee 이름 변경은 그 검증된 내부 overlay에 이어 적용한다. 준비 순서는 결정적이고 같은 원본 계획의 요청 순서를 바꿔도 같은 후보를 만든다. 사용자 선택·before·원본 hash를 바꾸거나 서로 다른 graph 문자열을 필드 병합하지 않는다. 일반 계약 그룹과 이전 이름 변경 그룹의 처리 순서는 유지한다.

범위는 같은 정보에 직접 포함된 동기 함수 두 개, 단일 ordinary Blueprint caller와 단일 native C# callee다. caller의 입력 수·이름·값 역할·반환과 callee native 별칭·타입·역할·반환은 유지한다. retained C# source/record, exact64 local·좌표·실행선·출력과 선택 밖 원문/보관 파일을 보존한다. caller 입력의 타입만 하나 바꾸며 사용 중인 연결과 새 값은 원래 picker의 명시 선택을 요구한다. 원래 owner 상속과 선택 밖 상속 구현/읽기 전용 함수는 그대로 둔다.

기존 workspace1·receipt3/nativeBodyContexts에 최초 타입/사용처/호출자/본문 계획을 보존한다. cold에서는 원본 전체 후보를 재생하고 정확한 source/group/read 경계를 확인한다. 후속 설명과 callee 본문 Save에서도 최초 계약·선택·물리 읽기 버전을 유지한다. 권한·Review/Confirm·최종 CAS, 정의별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다. 새 형식·profile·receipt 필드·자동 cast/변환·C# 생성은 추가하지 않는다.

callee 변경과 함께 묶는 caller의 여러 입력/다른 구조·ref/out·반환, callee 자체 입력 타입/native ABI의 동시 변경, whole/private/opaque 다중 계약 일치 계획은 별도 잔여다. 소비되는 private 반환과 copy/registered/forwarded 관측 closure, 구 reader migration도 남는다. 이번 대표 흐름을 모든 타입 조합이나 전체 UI 완료로 세지 않는다. 실제 Windows/물리 기기·전체 UI는 별도 검증 대상이며 초기 빈 화면 원인은 미확정이다.
