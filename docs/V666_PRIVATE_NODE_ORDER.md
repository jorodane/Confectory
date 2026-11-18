# Private C# 값 인자의 명시 순서 변경과 공동 저장

기존 v666 고정7/8행에서 직접 소유 qualified private next code의 두 long 값 인자 순서를 명시적으로 바꾼다. 일반 C# 매개변수 편집기의 원래 이름·타입·전달 방식 보존 규칙을 private 자체 ABI에 연결하며 부모 frame/public/native 계약은 유지한다. 원래 연결이 단일 입력 읽기 또는 타입을 명시하지 않은 정확한 int32 상수인 유한 범위다. 기존 생성기의 입력 표현식은 단순 매개변수 읽기/숫자 승격이며 이 범위에서 새 getter·저장소·값 평가를 만들지 않는다.

인자 선언만 정확히 역순으로 명시하고 이름·타입·값 역할·인자 수·long 반환은 유지한다. 각 이름의 원래 연결 JSON을 그 이름에 보존하며 위치대로 값을 바꾸어 넣지 않는다. 명시 C# 본문/helpers 외 텍스트를 생성하거나 바꾸지 않는다. 원래 본문/helpers 그대로의 순서 변경은 실제40을 유지하고 CLR reflection에서 secondNative,firstNative 순서를 확인한다. 별도로 수동 편집한 본문/helpers와 다른 native 본문을 한 후보로 저장해20을 실행한다. 이 두 결과는 다른 검증이며 순서 변경 자체가 계산을 바꾼다는 의미가 아니다.

기존 C# Script 매개변수 영역·취소·Undo/Redo·초안/cold·복구·읽기 관측·Review/Confirm·최종 CAS를 재사용한다. 첫 owner Save 전 재진입과 후속 source Save에서 현재 node/graph 증거를 검증하고 최초 서명/소스/graph 해시·물리 읽기 버전을 보존한다. workspace1·receipt3/nativeBodyContexts와 현 metadata 편집 가능 표시를 사용하며 저장 schema/profile/receipt·권한은 추가하지 않는다.

local/alias·typed/wide literal과 다른 선언/역할/반환 혼합은 이번 유한 지원 밖이다. 유효한 원본 실행 후 거절 경계를 검증하며 일반 순서 변경의 영구 UX 정책으로 확정하지 않는다. 다른 인자 수·타입/ref-out·반환/구조·부모 frame ABI·retained/opaque/copy/import·외부 관측은 잔여다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다. 모의 DOM과 실제 Linux engine/Chromium·CLR을 구분하며 실제 Windows/기기/전체 UI는 미검증이다. 초기 빈 화면과 기존60/480초 시간 초과 원인은 미확정이다. main·원본·latest/rollback·기존 증거를 기존 보호·교대 범위에서 보존한다.

명시적으로 선택한 C# 본문이 원문과 같아도 검토 그룹에서 빠뜨리지 않는다. 기존 guard가 요구하는 선택 함수·본문의 원래 kind/path와 증거를 같은 atomic 그룹에 보관한다. 이 흐름에서 재현된 불변 선택 본문의 그룹 누락을 저장 경로에서 보완하며, 엄격한 guard·권한·소유·읽기 관측과 최종 CAS는 유지한다.

이 유한 흐름은 [최종 신규48·재사용0 검증](VALIDATION_V666_PRIVATE_NODE_ORDER.md)을 마쳤다.
