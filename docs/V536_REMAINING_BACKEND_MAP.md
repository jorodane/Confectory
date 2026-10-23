# v536 잔여 UI의 backend 경계

고정된 복원 목록의 판정이다. 원본 ZIP/레이아웃을 바꾸거나 새로운 실행 의미를 정하는 문서가 아니다. 소유 슬롯 ABI(`50f5058`)·모바일 whole-body 값/ref/out(`bd0cd5f`)은 기존 검증으로 유지한다.

| 잔여 | 실제 존재하는 backend | 부족한 연결/계약과 최소 후속 |
| --- | --- | --- |
| 등록 callable ABI | `BlueprintCallableContracts.Query`는 소유 ProjectPack의 직접 등록 의존성만 읽고 함수/manifest receipt·bodyReads=0을 제공한다. `BlueprintCallAbi.Prepare`는 순수 typed import/호출 갱신을 준비한다. `BlueprintCall.csbody`에는 기존 참조 생성 시 receipt 재검사가 있다. | 이번 묶음에서 같은 receipt를 명시적 ABI 선택·적용·checkpoint 재확인에 결부한다. 등록 팩/provider를 쓰기 대상으로 만들지 않는다. 단일 소유 root/본문/호출 값↔ref 제한은 그대로다. common/long 값↔ref 실제6건을 수용했다. 정확한 결과와 예외는 `VALIDATION_V536_REGISTERED_CALL_ABI.md`를 따른다. |
| 복사 초안/저장 복사본 ABI | `ImplementationCopy`/`ImplementationCopyEdits`와 slot batch 저장은 있다. 현재 copy-edit는 source/argument/route/parameters 등만 다루고 stale source definition을 거절한다. | ABI wrapper와 typed import 및 copy provenance를 함께 바꾸는 계약이 없다. 새 copy intent의 검토된 callee 증거를 준비하고 **복사본만** 원자적으로 갱신하는 제한된 작업 단위가 필요하다. 기존 원본/부모/등록 소스를 자동 고치거나 copySource 차단을 삭제할 수 없다. |
| 다중 target ABI | body별 read/정확한 target 선택, EditBatch/checkpoint는 있다. | import는 implementation 전체에서 공유된다. `BlueprintCallAbi`는 단일 본문만, 기존 root group은 정확한3/4개 소스만 검증한다. 영향받는 모든 body의 계약 증거·명시적 선택·취소/Review 그룹을 묶는 ABI 작업이 없다. C# body를 추측해 바꾸거나 한 graph만 바꾸는 지원은 불가하다. |
| 특수 실행 핀/wrapper enum의 모바일 연결 | 기존 `FeatureBlueprint` switch/enum, `previewEnum`/`applyEnum`, 후속 C# 편집·계약 검사가 있다. | root 데이터 반환과 실행 채널을 구별해 원본 C#/wrapper 경로를 재사용해야 한다. 모바일 모든 분기 탭/async를 일괄 켜는 근거가 아니다. 다음에는 이미 지원되는 wrapper enum 문맥 하나를 실제 모바일→저장→Confirm으로 연결/검증한다. |
| property/set/property-ref 카드 | `RuntimeObjectContracts`, metadata `blueprintPropertyCatalog` 및 read/createProperty·참조 시점/readonly 검사가 있다. | 현재 `feature-authoring.show`는 code/call/export 외 노드의 일반 화면 연결을 차단한다. 원본 property/set의 대상/값 UI를 descriptor와 대응시키는 어댑터가 필요하다. backend 전체 부재로 분류하지 않는다. |
| 공유/고정 반환 이름·빈 출력·영역/다중 선택·내부 흐름/async | 각각 일부 데이터/실행 계약은 있으나 원본의 모든 지원 문맥을 수용하지 않았다. | 고정 잔여로 유지한다. 표시 이름과 native ABI, 잠정 UI와 최종 문법, 선택 도구와 새 실행 모델을 구분해 항목별로 연결한다. 새 시각적 분기/반복이나 가짜 성공을 추가하지 않는다. |

등록 ABI 묶음의 완료 조건은 명시적 선택 receipt, 누락/위조·등록 변경 차단, 입력/원본 보존, Save/cold/재시도 및 Review/명시 compiler Confirm이다. 기존 소유 슬롯·모바일6건을 다시 실행한 것만으로 이 조건을 대신하지 않는다.

다음 **혼합 저장**은 속성/스키마 변경과 복사본 intent를 하나의 원자적 저장 단위로 표현하는 현재 누락을 먼저 다뤄야 한다. raw EditBatch가 있다는 이유로 서로 다른 저장 경로를 순서대로 호출해 부분 성공시키지 않는다. 계약이 없을 동안 혼합 Save 차단과 입력 보존은 유지한다. **조작 검증**은 실제 연결된 문맥에서 원본 선택/삭제/줌/검색/키보드 및 창/프로젝트 전환을 유한 목록으로 검사할 수 있다. 복사본/다중 target 등의 미구현을 완료로 덮을 수 없으며 전체 v536 완료 판정은 여전히 보류다.
