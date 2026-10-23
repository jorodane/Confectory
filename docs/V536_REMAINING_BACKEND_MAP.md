# v536 잔여 UI의 backend 경계

고정된 복원 목록의 판정이다. 원본 ZIP/레이아웃을 바꾸거나 새로운 실행 의미를 정하는 문서가 아니다. 소유 슬롯 ABI(`50f5058`)·모바일 whole-body 값/ref/out(`bd0cd5f`)은 기존 검증으로 유지한다.

| 잔여 | 실제 존재하는 backend | 부족한 연결/계약과 최소 후속 |
| --- | --- | --- |
| 등록 callable ABI | `BlueprintCallableContracts.Query`는 소유 ProjectPack의 직접 등록 의존성만 읽고 함수/manifest receipt·bodyReads=0을 제공한다. `BlueprintCallAbi.Prepare`는 순수 typed import/호출 갱신을 준비한다. `BlueprintCall.csbody`에는 기존 참조 생성 시 receipt 재검사가 있다. | 이번 묶음에서 같은 receipt를 명시적 ABI 선택·적용·checkpoint 재확인에 결부한다. 등록 팩/provider를 쓰기 대상으로 만들지 않는다. 단일 소유 root/본문/호출 값↔ref 제한은 그대로다. common/long 값↔ref 실제6건을 수용했다. 정확한 결과와 예외는 `VALIDATION_V536_REGISTERED_CALL_ABI.md`를 따른다. |
| 복사 초안/저장 복사본 ABI | `ImplementationCopy`/`ImplementationCopyEdits`와 slot batch 저장은 있다. 현재 copy-edit는 source/argument/route/parameters 등만 다루고 stale source definition을 거절한다. | ABI wrapper와 typed import 및 copy provenance를 함께 바꾸는 계약이 없다. 새 copy intent의 검토된 callee 증거를 준비하고 **복사본만** 원자적으로 갱신하는 제한된 작업 단위가 필요하다. 기존 원본/부모/등록 소스를 자동 고치거나 copySource 차단을 삭제할 수 없다. |
| 다중 target ABI | body별 read/정확한 target 선택, EditBatch/checkpoint는 있다. | import는 implementation 전체에서 공유된다. `BlueprintCallAbi`는 단일 본문만, 기존 root group은 정확한3/4개 소스만 검증한다. 영향받는 모든 body의 계약 증거·명시적 선택·취소/Review 그룹을 묶는 ABI 작업이 없다. C# body를 추측해 바꾸거나 한 graph만 바꾸는 지원은 불가하다. |
| 특수 실행 핀/wrapper enum의 모바일 연결 | 기존 `FeatureBlueprint` switch/enum, `previewEnum`/`applyEnum`, 후속 C# 편집·계약 검사가 있다. | wrapper enum 문맥의 이름 우선 ID 대응을 원본대로 수정하고 모바일 편집/취소/분기 노드 삽입/저장/cold/명시 Confirm/충돌 보존 실제8건을 수용했다(`VALIDATION_V536_ENUM_PINS.md`). 후속 일반 소유 static/void code의 원본 C# Result·본문·보조 함수를 한 후보/checkpoint로 저장하는 어댑터와 불완전 입력 재진입을 연결했다(`VALIDATION_V536_GENERAL_ENUM.md`). 슬롯·복사·private path·데이터 반환 enum의 일반화는 포함하지 않는다. root 데이터 반환을 실행 채널로 바꾸거나 모바일 모든 분기 탭/async를 일괄 켜지 않는다. |
| 속성/property-ref 카드 | `RuntimeObjectContracts`, metadata `blueprintPropertyCatalog` 및 read/createProperty·참조 시점/readonly 검사가 있다. | 추가 원본 대조: `resourceNodeMarkup(property)`는 실행 핀이 없고 `blueprintExecutionOutputs`의 순차 노드에도 property가 없다. 현재 backend는 실행 경로에 도달할 때 읽기/쓰기를 수행한다. 원본에 실행 핀을 임의 추가할 수 없으므로 단순 카드 어댑터만 남았다고 볼 수 없다. 순수 값 핀의 평가 시점을 표현하는 계약이 필요하다. 원본에는 캐시 정책이 없었지만 사용자 결정으로 읽기 작업의 실행 시점 현재 값/재실행 시 재읽기, 이미 생성된 출력 보존으로 확정했다(`V536_PIN_AND_ATOMIC_NEXT.md`). 실제 UI 연결은 남아 있다. mutable ref를 일반 읽기로 바꾸지 않는다. |
| 지역변수 중간저장/set | Core의 local-assignment와 `createLocal/updateLocal/removeLocal/createSet`는 있다. | 원본 set은 지역변수 선택/새 변수/저장한 값 핀이다. 필드에 쓰는 property-set과 다른 동작이다. 원본 plan은 targetVariableId와 outputVariableId를 구별하지만 후속 backend에는 호환되는 선택적 outputLocal/stored와 새 local+Set+연결의 setPlan 후보/checkpoint 저장을 구현했다. Core7/실제 엔진9/복사 차단2를 수용했고 화면 어댑터는 아직 남아 있다(`VALIDATION_V536_SET_BACKEND.md`). 원본 정의의 최소 구현 경계를 유지한다(`V536_PIN_AND_ATOMIC_NEXT.md`). 단계를 따로 저장해 부분 적용하거나 원본 Set을 실제 객체 필드 쓰기로 바꾸지 않는다. |
| 공유/고정 반환 이름·빈 출력·영역/다중 선택·내부 흐름/async | 각각 일부 데이터/실행 계약은 있으나 원본의 모든 지원 문맥을 수용하지 않았다. | 고정 잔여로 유지한다. 표시 이름과 native ABI, 잠정 UI와 최종 문법, 선택 도구와 새 실행 모델을 구분해 항목별로 연결한다. 새 시각적 분기/반복이나 가짜 성공을 추가하지 않는다. |

등록 ABI 묶음의 완료 조건은 명시적 선택 receipt, 누락/위조·등록 변경 차단, 입력/원본 보존, Save/cold/재시도 및 Review/명시 compiler Confirm이다. 기존 소유 슬롯·모바일6건을 다시 실행한 것만으로 이 조건을 대신하지 않는다.

다음 **혼합 저장**은 속성/스키마 변경과 복사본 intent를 하나의 원자적 저장 단위로 표현하는 현재 누락을 먼저 다뤄야 한다. raw EditBatch가 있다는 이유로 서로 다른 저장 경로를 순서대로 호출해 부분 성공시키지 않는다. 계약이 없을 동안 혼합 Save 차단과 입력 보존은 유지한다. **조작 검증**은 실제 연결된 문맥에서 원본 선택/삭제/줌/검색/키보드 및 창/프로젝트 전환을 유한 목록으로 검사할 수 있다. 복사본/다중 target 등의 미구현을 완료로 덮을 수 없으며 전체 v536 완료 판정은 여전히 보류다.

후속 계약의 구현 가능/결정 필요 구분: `V536_PIN_AND_ATOMIC_NEXT.md`. Set 출력·copy ABI·다중 target·동일 owner 혼합 Save는 기술 계약으로 진행 가능하고, 속성은 사용자 답변으로 읽기 실행 시점의 현재 값과 이미 생성된 출력 보존으로 확정했다. 추가 질문 없이 해당 어댑터를 후속 구현한다. 현재 차단을 유지하며 다음 기능을 완료로 합산하지 않는다.
