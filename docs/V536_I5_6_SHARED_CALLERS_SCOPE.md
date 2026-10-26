# 고정 8행: 여러 정보 함수의 공유 호출자 저장

7행의 원래 오버라이드 계약 유지 정책과 구별되는 기존 직접 소유 함수 조작을 연결한다. 정보 창의 기존 함수 상세창 여러 개에서 입력 이름을 편집하고 같은 창의 임시 저장을 한 번 누르는 동작이다. 새 메뉴·레이아웃·함수 ID·실행 권한은 추가하지 않는다.

## 이번 지원 단위

- 같은 정보가 직접 소유한 기존 함수 2~8개의 **같은 위치·타입을 유지하는 값 입력 이름 변경**을 명시적 원래 핀 대응으로 함께 저장한다. 반환 계약은 유지한다.
- 각 함수의 직접 소유 일반 Blueprint와 공통 호출자의 입력/연결을 하나의 후보에 합친다. code/call의 직렬 next와 export 문맥만 대상으로 한다. 원래 함수·구현 ID, 코드 매개변수, C# 원문, 호출 결과 연결과 정확한 값은 보존한다.
- 각 closure는 기존 검증기를 사용해 내부 overlay에만 준비한다. 다음 closure는 앞선 후보의 그래프/계약을 읽는다. 최종 공유 소스 업데이트는 한 ID당 하나로 합치고 **원래 요청의 해시**로 제출한다. 중간 결과를 live workspace나 파일에 저장하지 않는다.
- 전체 후보의 기존 checkpoint CAS·receipt·Review/Confirm을 사용한다. 마지막 함수가 잘못되거나 실제 소스가 바뀌면 모든 변경이 미적용이다. 응답 유실은 저장 결과 조회로 정리하며 중복 적용하지 않는다.
- 계약이 그대로인 여러 함수의 설명 편집이나 계약 하나+다른 함수 설명 편집은 이 제한에 넣지 않고 기존 경로를 유지한다. native/ref 구현도 설명만 바꾸면 재작성하지 않는다.

같은 원래 스냅샷에서 각 closure를 독립 준비한 뒤 마지막 업데이트로 덮어쓰는 방식은 사용하지 않는다. 따라서 편집 순서를 뒤집어도 두 함수가 공유하는 caller의 최종 연결이 같다. 원래 물리 파일 관측은 overlay와 별개로 유지한다.

## 명확한 잔여

후속 [공유 값 입력 타입 단위](VALIDATION_V536_INFORMATION_SHARED_TYPES.md)는 같은 위치·이름·수의 값 입력을 기본 scalar 타입으로 바꾸는 경계를 추가한다. 직접 소유 leaf callee는 import 없이 code/export만, 공유 caller는 선택한 함수들의 call/export만 사용하며 반환 계약은 유지한다. 기존 선택창에서 callee 사용처의 대체와 caller의 새 값/기존 연결 해제를 각각 명시한다. 원래 스냅샷에서 모든 선택을 먼저 검증하며, 내부 overlay에서 다른 선택된 호출의 서명·인자 외에 변화가 있거나 현재 선택한 호출 자체가 변했으면 재사용하지 않는다. 사용자 원본 hash·checkpoint CAS는 바꾸지 않는다.

다음 [일반 out 이름 단위](VALIDATION_V536_INFORMATION_SHARED_OUTPUT_NAMES.md)는 같은 위치·타입·값/out 역할과 반환을 유지하며 여러 함수의 핀 이름을 편집한다. 위와 같은 독립 leaf/call 경계에서 원래 핀 대응만 제출하며 caller 입력의 새 값/다른 출력 선택은 하지 않는다. 기존 semantic binding 갱신기로 writer와 공개 출력 이름, call ID로 구별되는 출력 소비 연결을 같은 후보에서 전파한다. C#의 원래 out 매개변수 이름과 본문은 바꾸지 않는다.

후속 [scalar out 타입 단위](VALIDATION_V536_INFORMATION_SHARED_OUTPUT_TYPES.md)는 이름·위치·핀 수·역할·모든 값 입력과 반환을 유지한다. 기존 출력 writer 선택과 caller의 호환 출력 대응을 각각 원래 source에서 검증한다. 앞선 생산자의 명시 대응이 다른 선택 call의 인자로 전파됐다면 그 변환만 원래 graph 복제본에 적용해 현재 내부 후보와 대조한다. caller 입력 자체를 새 값으로 고르거나 hash만 갱신하지 않는다.

후속 [출력 정의/void 반환 단위](VALIDATION_V536_INFORMATION_SHARED_OUTPUT_DEFINITIONS.md)는 기존 `outputGraphs`의 모든 writer/exit 삭제, 새 배치의 값·삽입 위치·다음 경로 및 caller outputs를 원래 source에서 먼저 검증한다. 직접 소유 leaf/call 경계에서 값 입력과 유지되는 핀의 이름·타입·상대 순서는 고정한다. 명시한 scalar out 추가·삭제·삭제/추가 혼합과 양방향 void 반환 전환을 여러 함수에서 함께 저장하며, 새 출력은 자동으로 공개하지 않는다. 삭제된 출력을 소비하던 연결은 같은 타입의 명시 대응 없이는 저장하지 않는다. 이전 생산자 출력 대응만 원래 공유 graph 복제본에 투영한 뒤 현재 내부 overlay와 대조하며, 사용자 원래 hash와 단일 CAS는 유지한다. 새 ID는 원본 출력 배치가 요구하는 graph node에 한정되고 함수/계약/copy ID 정책을 변경하지 않는다.

후속 [비void 반환 타입 단위](VALIDATION_V536_INFORMATION_SHARED_RETURN_TYPES.md)는 모든 선택 함수의 인자 계약(이름·타입·위치·수·mode)을 고정하고 scalar 비void 반환 타입만 변경한다. 반환도 기존 typed 출력 writer로 검증하며 각 caller의 원래 출력마다 같은 타입의 현재 출력 대응을 명시한다. 기존 공개 출력 이름은 유지하고 반환 필드의 타입 snapshot만 갱신한다. 초기 반환 단위는 다른 계약 편집과 분리했으며, 아래 out/반환 타입 결합 단위가 입력을 고정한 혼합을 추가한다. 원래 source의 모든 writer/caller 선택을 먼저 검증한 뒤 같은 `ProjectOutputs`와 내부 후보/CAS에 연결한다. C# 원문을 새 반환 타입에 맞춰 자동 변환하지 않는다.

후속 [고정 로컬 import 단위](VALIDATION_V536_INFORMATION_SHARED_LOCAL_IMPORTS.md)는 위 독립 code/export·call/export 경계에서 선택 밖 같은 팩의 직접 함수 계약을 읽기 의존성으로 유지한다. 원래 선언과 typed import가 일치해야 하며 미선택 선언도 파일 관측으로 검증한다. callee C# 노드의 원문/import와 caller의 별도 호출을 보존하고 명시한 출력 대응만 전파한다. 선택 callee 사이의 의존·외부/상속 import·수동 최종 본문/문맥 편집은 추가하지 않는다.

후속 [값 입력/out 타입 동시 단위](VALIDATION_V536_INFORMATION_SHARED_IO.md)는 모든 선택 함수가 두 종류의 scalar 타입을 함께 바꾸되 이름·수·위치·역할·반환은 유지한다. 원래 사용처/새 값·writer·caller의 해제/출력 대응을 검증하고 한 후보에 결합한다. 앞선 출력 대응이 뒤의 해제 대상 인자를 옮기면, 원래 증거와 투영한 전체 graph가 일치하는 경우에만 내부 해제 계획을 대응시킨다. 사용자 source hash와 물리 관측/CAS는 갱신하지 않는다.

후속 [서로 다른 scalar 편집 종류 단위](VALIDATION_V536_INFORMATION_SHARED_MIXED_TYPES.md)는 입력 전용·출력 전용·입력/out 동시 타입 편집을 함수별 원래 사용처/해제/출력 계획으로 구분해 한 후보에 넣는다. 이 혼합 그룹은 전체에서 입력/out 타입 변경을 각각 최소 하나씩 포함한다. 이름·수·위치·역할·반환과 직렬 leaf/call 경계는 유지한다. 입력 전용 함수에 출력 재연결을 허용하거나 출력 전용 함수의 입력을 바꾸지 않는다.

후속 [out 유지 입력 타입 단위](VALIDATION_V536_INFORMATION_SHARED_INPUTS_WITH_OUT.md)는 같은 직렬 leaf/call 경계에서 여러 함수의 값 입력 타입만 변경하면서 기존 out writer·공개 계약·소비 출력을 유지한다. 원래 callee 사용처와 caller의 명시 값/해제 증거를 함수별로 검증하며 출력 선택 계획은 허용하지 않는다.

후속 [값 입력 정의 단위](VALIDATION_V536_INFORMATION_SHARED_INPUT_DEFINITIONS.md)는 새 입력의 명시 값과 사용 중인 입력 삭제/추가 시 callee 사용처·caller 바인딩 재사용/해제를 같은 후보로 결합한다. 유지되는 핀의 이름/타입/역할/상대 순서와 out·반환은 고정한다.

후속 [입력 정의/타입 결합 단위](VALIDATION_V536_INFORMATION_SHARED_INPUT_MIX.md)는 함수별 입력 정의와 scalar 타입 편집 및 같은 함수 안의 추가/삭제+타입 교체를 결합한다. 살아남는 핀 이름/역할/상대 순서와 out·반환은 유지하며, 같은 이름의 타입 교체도 원래 사용처/값/해제를 명시해야 한다.

후속 [out/비void 반환 타입 결합 단위](VALIDATION_V536_INFORMATION_SHARED_OUTPUT_RETURN_MIX.md)는 반환 전용·out 전용·out/반환 동시 scalar 타입 편집을 함수별 원래 writer/호환 소비 대응으로 구분해 결합한다. 값 입력과 핀 이름/수/역할/순서는 유지한다. 같은 함수의 두 종류 변경도 명시 출력 closure로 검증하며 기존 long 소비를 다른 타입으로 조용히 변환하지 않는다.

후속 [출력 정의/타입 결합 단위](VALIDATION_V536_INFORMATION_SHARED_OUTPUT_DEFINITION_MIX.md)는 출력 추가/삭제·양방향 void 전환과 유지 scalar out/비void 반환 타입 편집을 함수 간/같은 함수 안에서 결합한다. 값 입력과 유지 핀 이름/역할/상대 순서는 고정한다. 원래 그래프의 전체 writer 삭제/명시 새 배치와 유지 writer의 타입 대응을 구별하고 각 caller의 호환 소비를 한 후보/CAS로 검증한다.

후속 [입력 이름/출력 타입 결합](VALIDATION_V536_INFORMATION_SHARED_INPUT_NAME_OUTPUT_MIX.md)은 값 입력의 타입/수/역할/순서를 유지한 명시 이름 변경과 scalar out/비void 반환 타입 편집을 함수 간/같은 함수 안에서 결합한다. 이름 전용 행은 원래 핀 대응만 사용하고, 출력도 바뀐 행은 새 공개 입력 이름에 원래 caller 바인딩을 유지하며 모든 writer/호환 소비를 검증한다. C# 매개변수·본문은 재작성하지 않는다.

후속 [입력 이름/출력 정의 결합](VALIDATION_V536_INFORMATION_SHARED_INPUT_NAME_OUTPUT_DEFINITIONS.md)은 명시 값 입력 이름 대응과 출력 추가/전체 writer 삭제·양방향 void 반환 전환을 함수 간/같은 함수 안에서 결합한다. 입력 타입/수/역할/상대 순서와 기존 바인딩을 유지하며 이름 전용 행은 before/args만 사용한다. 기존 graph/writer/호환 소비 계획을 원래 스냅샷에서 모두 검증하고 한 후보/CAS로 저장한다.

후속 [값 입력/비void 반환 타입 결합](VALIDATION_V536_INFORMATION_SHARED_INPUT_RETURN_MIX.md)은 값 입력 타입 전용·반환 타입 전용·같은 함수의 동시 편집 및 기존 out 타입 계획을 원래 사용처/값/해제·writer/호환 소비와 한 후보/CAS로 결합한다. 이름/핀 수/역할/순서는 고정한다. 앞선 반환 대응으로 옮겨진 뒤 caller 해제의 원래 증거도 기존 투영기로 보존한다.

후속 [값 입력 타입/출력 정의 결합](VALIDATION_V536_INFORMATION_SHARED_INPUT_OUTPUT_DEFINITION_MIX.md)은 기존 입력 사용처/값/해제와 모든 출력 writer/exit 삭제·명시 생성/경로·소비 대응을 같은 원래 스냅샷에서 검증하여 함수 간/같은 함수 안에 결합한다. 양방향 void 전환과 유지 scalar out/반환 타입 계획도 보존하며 입력 타입 전용 행은 출력 투영에 등록하지 않는다.

입력 정의 추가·사용 중 삭제/삭제 후 새 입력 대응과 기존 scalar out·비void 반환 타입도 같은 함수/함수 간 원래 입력 사용처·값·재사용/해제·전체 writer·호환 소비와 단일 후보/CAS로 결합한다(VALIDATION_V536_INFORMATION_SHARED_INPUT_DEFINITION_RETURN_MIX.md). 출력이 바뀐 행만 producer 선택을 투영하며, 입력 정의 전용 행에는 출력 재선택을 허용하지 않는다.

scalar 입력 정의 추가·사용 중 삭제/새 입력 대응과 출력 추가·전체 writer 삭제/양방향 void 전환도 원래 사용처·값·재사용/해제·graph/writer/호환 소비 및 단일 후보/CAS로 결합한다(VALIDATION_V536_INFORMATION_SHARED_INPUT_OUTPUT_DEFINITIONS.md). 남은 입력/출력 식별자·역할·순서를 유지하며 삭제한 입력만 retained 집합에서 제외한다.

ref 보유 직접 계약의 값/ref 이름 편집은 원래 타입·역할·수·순서·반환과 같은 caller 저장소를 유지하고, 기존 native 본문/출력/graph receipt와 호출 확인을 명시 검토하여 한 후보/CAS로 결합한다(VALIDATION_V536_INFORMATION_SHARED_REF_NAMES.md). 새 역할이나 저장소를 추정하지 않으며 C# 원문/매개변수는 명시 검토한다. ref 역할 변경/타입/순서·ABI 혼합과 다른 C#/whole 문맥은 별도다.

8행 전체 완료는 아니다. 위 좁은 경계 밖의 입력/out/반환/정의 동시 편집 및 ref 역할·순서·유지 출력 역할과 정의 변경의 혼합, 명시 C# 본문 편집, 중첩/private·whole/native·postCall wrapper, 복사본/상속/외부 함수가 섞인 여러 closure의 결합은 아직 지원하지 않는다. 이미 지원한 입력/out 타입 동시 편집은 이 잔여에 포함하지 않는다. 이 조합은 기존 입력을 보존하며 거절한다. 함수 변경과 소유 정보의 속성/설명 변경을 함께 제출하는 확대도 이번 단위 밖이다. 결합한 linked source도 기존 64개 한도를 유지한다. 단일 함수의 이전 지원은 그대로다.

7행은 원래 매개변수/출력 계약을 유지하는 오버라이드만 대상으로 한다. 계약을 깨는 변경은 정상 보호이며 독립 계약 복제/새 ID 발급은 필수 복원에서 제외한다(V536_OVERRIDE_CONTRACT_POLICY.md). 직접 소유 함수의 기존 편집과 새 함수 생성은 제한하지 않는다. 9행의 정보/참조/외부 타입 핀과 표시명/native 식별자 분리는 별도다. 현재 함수 문법은 기본 CLR 타입/배열이며, 속성용 타입 catalogue를 단순 표시하는 것만으로 named 함수 계약이 구현되는 것은 아니다. 이 문법/타입 연결 작업은 독립 copy 정책과 무관한 기존 요구의 미구현이다.

전체 I5-6/v536 UI 또는 실제 Windows/WebView2·모바일 기기 검증 완료를 의미하지 않는다. 사용자 프로젝트·계정·유료 추론은 사용하지 않는다.

후속 [기존 저장소 값/ref 단위](VALIDATION_V536_INFORMATION_SHARED_REF_ROLES.md)는 같은 위치·타입·핀 수·반환 및 원래 caller 저장소를 유지한 값↔ref 전환을 연결한다. 기존 retained native 매개변수·본문·출력/graph receipt와 caller 바인딩을 명시 검토하며 typed import도 같은 후보에서 갱신한다. 원래 핀 이름 편집을 함께 할 수 있지만 out 역할·순서 변경은 별도다. 새 셀/별칭·자동 C# 재작성·오버라이드 원계약 변경을 만들지 않는다.
