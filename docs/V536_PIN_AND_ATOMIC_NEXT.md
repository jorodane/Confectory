# v536 속성·Set 및 결합 저장의 다음 구현 계약

사용자가 지정한 `196c605`의 `reference/site-ui/Confectory-Editor-Prototype-v536.zip`을 대조했다. 원본 파일은 변경하지 않았다. ZIP의 `CHANGES-v508-v536.txt`는 모바일 편집·순서·배치를 설명하지만 속성 값의 읽기 캐시 시점을 정하지 않는다. `README.txt`는 실제 C# 컴파일러·외부 실행 엔진이 연결되지 않은 프로토타입이라고 명시한다. 아래는 **소스에서 확인한 것**, **엔진 구현 제안**, **사용자 결정이 필요한 것**을 구별한다. 원본 UI에 실행 핀·새 패널을 추가하는 계획이 아니다.

## 속성: 사용자 결정으로 실행 시점 기준 확정

원본 `dist/blueprint.js`의 `resourceNodeMarkup(property)`는 명시적 대상 객체 입력과 값 출력을 그리며 실행 포트가 없다. `blueprintExecutionOutputs`의 순차 노드 목록에 property가 없고, `blueprintExecutionScope`는 실행 도달 집합과 데이터 의존 집합을 구별한다. 속성은 데이터 의존으로 활성화된다. 그러나 프로토타입에는 실제 속성 소비 런타임, 첫 읽기 캐시 또는 소비 시점마다 재읽기라는 정책이 없다. `blueprintEvaluateExpression`도 전달받은 resolve 함수를 호출할 뿐 속성 읽기 정책을 정하지 않는다.

현재 `src/Confectory.Core/FeatureBlueprint.Properties.cs`는 속성 읽기·쓰기·ref 취득 시점을 `execution-node`로 명시한다. 값 노드의 화면 위치로 실행을 추정하지 않는다. 후속 어댑터는 아래 사용자 결정에 따라 명시한 소비 연결의 실행 입력에 읽기를 부착하며 원본에 실행 핀을 새로 그리지 않는다.

사용자는 속성을 읽기 작업이 실행되는 시점의 현재 값으로 처리하도록 정했다. 기능 실행 전체에서 속성별 최초 값을 고정하는 캐시는 사용하지 않는다. 같은 읽기 작업이 다시 실행되면 그 시점의 값을 다시 읽는다. 이 결정은 이전의 미확정 질문을 해소하며, 추가 선택을 다시 요구하지 않는다.

한 번 읽어 만들어진 출력은 그 읽기의 값/참조를 보존한다. 이를 대상 필드의 실시간 getter/ref로 바꾸거나 임의 deep-copy로 바꾸지 않는다. 기존 `property-ref`의 명시적 cell 취득·수신자/readonly 검사는 별도 의미로 유지한다. 현재 Core의 `execution-node` 읽기·쓰기·출력 보존은 이 방향의 기반이다. 후속 ordinary main-line 어댑터는 원본의 실행 포트 없는 property 카드·데이터 의존을 사용자가 명시한 첫 소비 작업 직전에 연결한다. 단일 후보에서 node-time 읽기와 소비 binding/연결을 함께 검사한다. mutable ref/branch/private/copy 일반화는 포함하지 않는다. 첫 필드 읽기를 다른 읽기 작업과 합쳐 실행 전체 캐시로 사용하지 않는다. 미실행 경로의 null receiver를 미리 읽거나 새로운 쓰기/계정 권한을 부여하지 않는다. Set 화면 및 별도 읽기와 앞 출력 보존을 실제 UI와 격리 CLR 실행에서 확인했다(`VALIDATION_V536_SET_UI.md`).

## Set: 원본 정의로 구현 가능함

원본 `blueprintExecutionPlan`은 Set에 `operation:'set-local'`, `targetVariableId`, `outputVariableId`, `valueInput:'value'`를 저장한다. `blueprintSetValid`와 저장 대상 선택창은 기존 지역변수 대상과 해당 Set의 출력 변수를 구별한다. 새 지역변수이면 자기 출력 변수가 대상이며, 기존 변수를 선택하면 쓰는 대상과 이 Set의 출력 변수가 다를 수 있다. 원본의 ‘저장한 값’을 단순히 현재 대상 지역변수 읽기로 치환하면 이후의 대입으로 값이 바뀔 수 있다.

후속 backend 첫 묶음에서 기존 void Set을 보존하는 `outputLocal`/`stored` 출력과 `setPlan` 원자 후보를 구현했다(`VALIDATION_V536_SET_BACKEND.md`). Set의 대상 local과 출력 local을 구별하고 값을 한 번 평가한다. 출력 local이 원본에서 명시적으로 다른 Set의 쓰기 대상으로 선택된다면 그 저장소의 명시적 변경은 가능하다. 대상과 출력이 다를 때 대상의 후속 대입을 이전 출력의 실시간 참조로 바꾸지는 않는다. 원본 카드·모바일 화면 어댑터와 유한 수용 결과는 `VALIDATION_V536_SET_UI.md`에 기록했다. 저장된 출력 타입 변경과 copy/다중 target 일반화는 지원하지 않는다. 다음은 확정된 최소 구현/수용 범위다.

1. 기존 Set을 호환하는 선택적 출력 저장소 식별자를 추가한다. 대상·출력은 같은 소유 graph의 명시적 local이며 타입이 같아야 한다. 출력 저장소는 읽기 전용 alias 또는 외부 cell을 몰래 취득하는 수단이 아니다.
2. 값을 한 번 평가하고 대상과 해당 출력 저장소에 반영한다. 같은 지역변수에 후속 Set을 해도 앞 Set의 보관 출력은 유지한다. 값/배열/객체 참조의 기존 CLR 대입·identity 의미를 유지하며 임의 deep-copy를 추가하지 않는다. 호출 후 SourceContext 배열 복사는 기존 별도 계약이다.
3. 새 local·Set·입출력 binding·직렬 연결을 같은 소유 root의 한 후보와 checkpoint에 결부한다. 원본 저장 대상·타입·값·저장한 값 카드 및 모바일 편집만 연결한다.
4. 두 Set의 같은 대상/서로 다른 보관 출력, 잘못된 타입/readonly 대상, 취소·cold·Review/명시적 compiler Confirm·CAS 거절 시 입력 보존으로 완료 조건을 한정한다. backend와 ordinary root UI/사용자 취소·cold·명시 Confirm을 검증했다. 이 한정 범위를 전체 v536 완료처럼 표시하지 않는다.

## 복사본·다중 target·혼합 Save: 기술 계약으로 진행 가능함

| 범위 | 이미 있는 기반 | 필요한 최소 작업 단위 |
| --- | --- | --- |
| 복사본 ABI | `targets/element-authoring/ImplementationCopy.cs`, `ImplementationCopyEdits.cs`, `BlueprintCallAbi.cs`, slot batch | 명시적으로 선택한 복사본·실행 대상·callee receipt에 한정한 계획을 준비한다. 복사본의 typed import·wrapper·graph·node records·copy provenance를 함께 검증/적용하며 원본·부모·등록 팩을 쓰지 않는다. 기존 stale copySource 차단을 삭제하지 않는다. |
| 다중 target ABI | `BlueprintRootContract.cs`, `BlueprintRootGroup.cs`, body별 정확한 locator와 source proof | 공유 import를 바꾸는 영향 범위의 모든 body/target을 수집한다. 수정 대상은 사용자 선택으로 고정하고 나머지는 byte/source proof로 보존한다. 각 body의 현재 signature·contract와 변경 후 signature를 함께 검사한다. 불투명한 C# 본문이나 비호환 연결을 추측해 다시 쓰지 않는다. 기존 3/4개 root 그룹 검사를 단순 완화하지 않는다. |
| 속성/스키마+복사본 혼합 Save | `packs/edit-workspace/SlotBatch.csbody`, `EditBatch.csbody`, `packs/save/ApplySlots.csbody`, `WriteChecked.csbody` 및 선언 편집 metadata | 기존 분리 Save를 순서대로 호출하지 않는다. 하나의 동일 ProjectPack/소유 객체에 명시된 선언 변경과 slot/copy 계획을 먼저 하나의 후보에 적용하고 최종 문맥으로 재검사한다. 전체를 한 checkpoint CAS와 receipt로 저장한 뒤 live 상태를 반영한다. |

SlotBatch는 같은 owner의 1~8개 명시적 함수 변경을 candidate에서 검증하고, ApplySlots는 전체 후보를 `WriteChecked`로 저장한 뒤 live 상태를 바꾸는 기반이다. EditBatch는 최대64개 명시적 unit의 원래 revision/hash와 소유권을 검사하며 임의 manifest 쓰기를 허용하지 않는다. 새 결합 계획은 이 경계를 유지하고, 원래 읽은 checkpoint·unit ID/path/hash/revision·copy 출처·등록 callable receipt와 새 candidate의 hash를 기록해야 한다. 저장 실패/응답 유실은 기존 receipt로 결과를 확인하며 새 버전으로 덮어쓰는 재시도는 금지한다. 저장은 초안이고 compiler Review/Confirm은 별도의 명시적 동작이다.

이 세 항목의 원자성·버전·소유권·실패 보존은 엔지니어링 계약이다. **이를 구현하는 데 새 사용자 결정은 필요하지 않다.** 여러 target이나 비호환 핀의 어느 쪽을 고칠지는 실제 편집 시 원본의 기존 선택/명시적 갱신으로 받아야 하며 현재 대화나 준비 완료를 자동 승인으로 쓰지 않는다. 프로젝트 밖 쓰기·다른 프로젝트·최종 Confirm·실행 권한을 추가하지 않는다.

다음 순서는 Set 출력 계약 → 복사본 ABI 단일 대상 → 모든 영향 body를 묶는 다중 target → 동일 소유 객체의 선언+copy 혼합 Save다. 속성 읽기 정책의 답은 도착했으며 ordinary root 화면 연결에서 같은 실행 시점/출력 보존을 검증했다. 새 UI 설계·새 실행 모델·추가 내구성 요구로 범위를 넓히지 않는다. 이 문서는 다음 구현 경계를 고정하는 것이며 해당 기능의 완료 보고가 아니다.

후속 첫 원자 단위: 저장·확정된 직접 배치 copy의 단일 Blueprint/호출 값↔ref를 `rebindCopyAbi`로 결부했다. 출처·직접 owner·요구 계약·모든 node record 및 최종 provider 검증 뒤 한 후보/checkpoint CAS를 사용한다. 결과/제한은 `VALIDATION_V536_SAVED_COPY_ABI.md`를 따른다. **새 비공개 copy intent 결합·다중 target·선언+copy 혼합 Save는 여전히 미완료**이며 이 첫 단위로 완료 처리하지 않는다.

후속 최소 혼합 Save: `VALIDATION_V536_MIXED_COPY.md`의 새 copy 하나 + 같은 객체 설명/기존 primitive 값만 한 후보·CAS에 연결했다. 앞의 포괄적 미완료 표기는 이 한정 단위 이후에는 stale private ABI·다중 target·넓은 혼합 Save에 해당한다. 기존 current wrapper 편집 지원은 stale ABI 갱신과 구별한다.
