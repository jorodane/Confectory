# v536 잔여 UI의 backend 경계

고정된 복원 목록의 판정이다. 원본 ZIP/레이아웃을 바꾸거나 새로운 실행 의미를 정하는 문서가 아니다. 소유 슬롯 ABI(`50f5058`)·모바일 whole-body 값/ref/out(`bd0cd5f`)은 기존 검증으로 유지한다.

| 잔여 | 실제 존재하는 backend | 부족한 연결/계약과 최소 후속 |
| --- | --- | --- |
| 등록 callable ABI | `BlueprintCallableContracts.Query`는 소유 ProjectPack의 직접 등록 의존성만 읽고 함수/manifest receipt·bodyReads=0을 제공한다. `BlueprintCallAbi.Prepare`는 순수 typed import/호출 갱신을 준비한다. `BlueprintCall.csbody`에는 기존 참조 생성 시 receipt 재검사가 있다. | 이번 묶음에서 같은 receipt를 명시적 ABI 선택·적용·checkpoint 재확인에 결부한다. 등록 팩/provider를 쓰기 대상으로 만들지 않는다. 단일 소유 root/본문/호출 값↔ref 제한은 그대로다. common/long 값↔ref 실제6건을 수용했다. 정확한 결과와 예외는 `VALIDATION_V536_REGISTERED_CALL_ABI.md`를 따른다. |
| 복사 초안/저장 복사본 ABI (부분) | 기존 `ImplementationCopy`/`ImplementationCopyEdits`, 저장 copy의 `rebindCopyAbi`와 원자 slot batch가 있다. | 새 private copy는 immutable seed와 현재 callee/직접 등록 receipt를 분리한 한정 후보/CAS로 연결했다(`VALIDATION_V536_PRIVATE_COPY_ABI.md`). 단일 target·context 없는 code·값↔ref만 지원하고 원래/외부 source는 쓰지 않는다. 저장 copy의 기존 직접 배치·독점 범위는 `VALIDATION_V536_SAVED_COPY_ABI.md` 그대로다. whole-body C#·여러 target copy/일반 ABI는 미지원이다. 현재 widget의 new-copy/owner 결합 지원은 아래 최신 혼합 범위를 따른다. |
| 다중 target ABI | `BlueprintCallAbiGroup`가 모든 Blueprint target의 graph/record·공용 import를 한 후보/CAS·정확한 Review 그룹으로 검증한다. | `VALIDATION_V536_MULTI_TARGET_ABI.md`의 owned ordinary root2target/common-long, 같은 callee1회/target·context 없는 code·값↔ref 실제 수용이다. opaque C#/상속/copy/context 있는 code·직접 등록 all-target·같은 callee 복수 사용·일반 ABI·다른 편집과 혼합은 차단한다. |
| 특수 실행 핀/wrapper enum의 모바일 연결 | 기존 `FeatureBlueprint` switch/enum, `previewEnum`/`applyEnum`, 후속 C# 편집·계약 검사가 있다. | wrapper enum 문맥의 이름 우선 ID 대응을 원본대로 수정하고 모바일 편집/취소/분기 노드 삽입/저장/cold/명시 Confirm/충돌 보존 실제8건을 수용했다(`VALIDATION_V536_ENUM_PINS.md`). 후속 일반 소유 static/void code의 원본 C# Result·본문·보조 함수를 한 후보/checkpoint로 저장하는 어댑터와 불완전 입력 재진입을 연결했다(`VALIDATION_V536_GENERAL_ENUM.md`). 슬롯·복사·private path·데이터 반환 enum의 일반화는 포함하지 않는다. root 데이터 반환을 실행 채널로 바꾸거나 모바일 모든 분기 탭/async를 일괄 켜지 않는다. |
| 속성/property-ref 카드 | `RuntimeObjectContracts`, metadata catalog/read/createProperty와 node-time 읽기/쓰기/ref 계약이 있다. | 후속 Set/속성 묶음은 원본 무실행 핀 카드와 모바일 receiver/값을 연결했다. 새 읽기는 명시한 소비 작업 직전 main-line에 부착하고 기존 출력 스냅샷을 유지한다. 단일 `propertyPlan` 후보의 descriptor/receiver/가용성·typed import·CAS를 검사했다. 실제 UI 및 CLR 읽기→쓰기→별도 읽기는 `VALIDATION_V536_SET_UI.md`를 따른다. mutable ref·자기 receiver·branch/private/slot/copy 일반화·모든 graph 재구성은 미완료다. |
| 지역변수 중간저장/set | 선택적 `outputLocal/stored`, 단일 `setPlan`/checkpoint가 있다. | 원본260px 카드·출력 핀 이름·모바일 대상/타입/값·검색 삽입을 연결했다. 기존 void Set 열기는 무변경이고 명시적 편집만 새 출력을 준비한다. 원자 저장·취소·cold·응답 유실/늦은 입력·충돌·Review/Confirm 결과는 `VALIDATION_V536_SET_UI.md`를 따른다. 저장된 출력 타입 변경은 비활성, copy/다중 target/혼합 저장 차단은 유지한다. 객체 필드 쓰기와 local Set은 구별한다. |
| 공유/고정 반환 이름·빈 출력·영역/다중 선택·내부 흐름/async | 각각 일부 데이터/실행 계약은 있으나 원본의 모든 지원 문맥을 수용하지 않았다. | 고정 잔여로 유지한다. 표시 이름과 native ABI, 잠정 UI와 최종 문법, 선택 도구와 새 실행 모델을 구분해 항목별로 연결한다. 새 시각적 분기/반복이나 가짜 성공을 추가하지 않는다. |

등록 ABI 묶음의 완료 조건은 명시적 선택 receipt, 누락/위조·등록 변경 차단, 입력/원본 보존, Save/cold/재시도 및 Review/명시 compiler Confirm이다. 기존 소유 슬롯·모바일6건을 다시 실행한 것만으로 이 조건을 대신하지 않는다.

다음 **혼합 저장**은 속성/스키마 변경과 복사본 intent를 하나의 원자적 저장 단위로 표현하는 현재 누락을 먼저 다뤄야 한다. raw EditBatch가 있다는 이유로 서로 다른 저장 경로를 순서대로 호출해 부분 성공시키지 않는다. 계약이 없을 동안 혼합 Save 차단과 입력 보존은 유지한다. **조작 검증**은 실제 연결된 문맥에서 원본 선택/삭제/줌/검색/키보드 및 창/프로젝트 전환을 유한 목록으로 검사할 수 있다. 복사본/다중 target 등의 미구현을 완료로 덮을 수 없으며 전체 v536 완료 판정은 여전히 보류다.

후속 계약의 구현 가능/결정 필요 구분: `V536_PIN_AND_ATOMIC_NEXT.md`. Set 출력·copy ABI·다중 target·동일 owner 혼합 Save는 기술 계약으로 진행 가능하고, 속성은 사용자 답변으로 읽기 실행 시점의 현재 값과 이미 생성된 출력 보존으로 확정했다. ordinary main-line의 Set/속성 어댑터는 `VALIDATION_V536_SET_UI.md`의 한정 범위로 연결했다. 다음은 복사본 ABI→다중 target→동일 owner 선언+copy 원자 저장이며 각 차단을 실제 결합 계약 없이 제거하지 않는다.

후속 최소 혼합 단위는 `VALIDATION_V536_MIXED_COPY.md`를 따른다. 새 copy 하나와 같은 owner 설명/기존 단일 primitive 값은 한 후보/CAS·선언 결부 receipt로 저장한다. 현재 유효한 wrapper와 export를 보존한다. 새 private ABI의 명시적 한정 갱신은 `VALIDATION_V536_PRIVATE_COPY_ABI.md`에 추가했고 여러 target copy는 차단한다. 이후 현재 widget의 복수 new copy/parent/modules/새 primitive 정의/복합 값 결합은 `VALIDATION_V536_WIDE_MIXED_SAVE.md`로 연결했다. 기존 schema 편집·saved-copy ABI·multi-target ABI/Setproperty 혼합은 여전히 미지원이다. 전체 v536 완료 판정을 바꾸지 않는다.

다중 target의 후속 한정 단위는 `VALIDATION_V536_MULTI_TARGET_ABI.md`를 따른다. 모든 owned Blueprint target의 같은 호출 값/ref 계약을 한 후보/CAS·정확한 source/record 검토 그룹으로 연결한다. opaque/상속/copy/context 있는 code/등록 callee all-target/복수 사용/일반 ABI와 넓은 혼합은 미완료다. 고정된 혼합 조합은 `V536_ATOMIC_REMAINING_COMBINATIONS.md`에 분리했으며 전체 v536 완료 판정은 바꾸지 않는다.

최신 혼합 범위: `VALIDATION_V536_WIDE_MIXED_SAVE.md`의 현재 owner widget+여러 new private copy는 원자적으로 연결했다. 기존 schema 편집·saved-copy ABI/multi-target ABI/Setproperty/다른 provider/dirty source와의 결합은 미완료다. 일반 ABI·특수 문맥 및 조작 수용을 backend 존재/계약 누락/UI 미연결로 구분한 구체적 완료 조건은 `V536_REMAINING_ACCEPTANCE.md`를 따른다.

최신 명시 general mapping: `VALIDATION_V536_GENERAL_ABI.md`. 현재 supported 단일 root/슬롯/saved/private copy/직접 등록 및 owned ordinary target group에 입력/출력 선택을 연결했고 모든 ABI authorBatch의 전체 typed graph 검사 누락을 수정했다. 등록 callable의 all-target은 `MultiAbiRequest`의 owned contract/검토 group만으로 receipt를 표현할 수 없어 계속 차단한다. copy-alltarget/여러 동일 호출/opaque context 역시 현재 group/provenance 범위를 넘어가므로 자동 재작성하지 않는다.

후속 schema/Save 첫 단위는 `VALIDATION_V536_SCHEMA_SAVE.md`를 따른다. primary owner-only Save와 직접 사용하는 소유 primitive schema 타입·값·새 copy를 한 후보/CAS·원자 Review 그룹에 연결했다. 기존 schema 표시 이름/삭제/복합 정의, 독립 View/dirty raw source/provider/saved-copy ABI·다중 target·Set-property 혼합은 여전히 별도 미완료다.

후속 root 표시 이름/삭제는 `VALIDATION_V536_SCHEMA_MUTATIONS.md`에 연결·검증 범위를 기록한다. stable native key를 표시 이름으로 rename하지 않으며, 삭제는 현재 owner 로컬 값과 같은 후보로 검사한다. 자손 데이터/Blueprint 참조는 거절한다. 복합/중첩 정의·독립 View/raw source 결합과 전체 ABI·모바일 수용은 여전히 미완료다.

최신 독립 properties View Save: `VALIDATION_V536_VIEW_SAVE.md`. 설명과 기존 복합/정확한 숫자 값을 한 후보/CAS로 보관하고 자기 View receipt·취소·경합·프로젝트 전환·cold/Review/Confirm을 검증했다. source View/copy/타 owner는 허용하지 않는다. 복합/중첩 정의 생성 및 원본 정보 picker/기본값, raw source와 다른 계획의 결합은 미완료다. compound/reference native 타입은 존재하므로 backend 전체 부재와 구별한다.

최신 정보 picker: `VALIDATION_V536_INFORMATION.md`. 소유 named schema의 중첩 primitive·상속 fallback/내부 multiple을 새 compound 정의로 선택하고 source hash proof와 owner 값·등록·설명을 한 후보에 결부한다. ref/function/imported/custom-default는 미연결로 표시한다. 정보 자체 정의/custom 기본값·legacy inline 변경과 raw source 결합은 다음 미완료다. native 타입 존재와 원본 UI 어댑터/기본값 계약 부족을 구분한다.

최신 정보 자체 정의/기본값: `VALIDATION_V536_INFORMATION_DEFAULTS.md`. schema owner-only 후보와 명시 typed-default metadata를 compiler 검증까지 연결했다. 현재 지원된 기본값은 정보 picker에서도 같은 projection을 사용한다. 다른 owner/slot/copy 권한을 확장하지 않으며 legacy inline/미지원 타입 전환/raw source 결합은 유지한다. 다음은 source 원문 보존과 같은 후보/CAS의 raw 결합이며 순차 endpoint 호출로 대체하지 않는다.
