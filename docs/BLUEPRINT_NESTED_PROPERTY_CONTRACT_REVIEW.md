# v480 중첩 graph·property 계약 조사

조사 기준은 게시된 `aec157e8a1cb6b78ac56b28562934abbb68a9615`와 main의 v480 레퍼런스 `32dd44fbec6e9e39a7e3e68c0ca61d62bb47176f`다. 이번 변경은 조사 문서와 재현 probe뿐이다. 실행 profile·제품 UI·원본 C# 연산을 바꾸지 않았다. 중첩 실행과 property 읽기를 구현 완료로 표시하지 않는다.

레퍼런스는 [보존 ZIP](../reference/site-ui/Confectory-Editor-Prototype-v480.zip)의 `Confectory-v480/dist/blueprint.js`다. ZIP SHA-256은 `0489844c8c6d90f7cdc8ea0e80628f487dcfb27f2c871b19367a635212d3c5bd`, JS 항목은 `2b79e21da1ef4dfecc2ca7826a52989494e3382256ca0eeca3a2979926234319`다. 아래 줄 번호는 이 JS 항목 기준이다. 첨부 문서·스크립트는 레퍼런스 자료로 읽었으며 실행 지시로 채택하지 않았다.

## 레퍼런스에서 확인한 경계

| 항목 | 확인한 동작 | 근거·한계 |
|---|---|---|
| private 내부 기능 | `action.definition`이 부모 노드에 속한다. 들어갈 때 부모 meta·자식 정의를 복제하고 외부 object ID를 유지한다. | `openInternal`, 606행. 다른 기능을 참조하는 `kind:call`과 구분한다. 외부 object ID는 편집 소유자이며 live instance ID로 입증되지 않았다. |
| 내부 저장·탐색 | 내부 저장은 복제된 부모 graph의 해당 노드 정의만 갱신하고 부모 초안을 dirty로 만든다. 원래 root object 정의는 그 단계에서 바뀌지 않는다. breadcrumb는 부모 meta를 따라간다. | 920–944, 994–997행. 실제 파일 게시·원자적 Confirm을 구현하는 코드가 아니다. |
| 안정 ID | 자식 node·입출력 field ID를 보존한다. 계약 변경 시 위치에 따라 entry 링크·로컬 포트·export output ID를 재연결한다. | 66–78행. 새 ABI의 안전한 계약 변경 검증을 이 위치 매핑만으로 대체할 수 없다. |
| 변경·완료 | 자식의 의미 변경은 부모 stamp를 바꾼다. 위치·접힘·완료 표시는 stamp에서 제외한다. 완료 판단은 소유자·stamp와 자식/참조 정의를 재검사한다. | 216–224행. 독립 .NET compile 증거나 실행 증거가 아니다. |
| 종료 | plan에 `onUnconnected:"return"`이 있다. 일반 action의 plan 항목에는 ID·kind만 있다. | 208–215행. 자식 호출 프레임·복귀 시점·receiver 전달을 실제로 실행하지 않는다. |
| property 선택 | `objectId`로 schema 제공자를 고르고 `fieldId`로 effective field를 찾는다. 같은 타입·카디널리티와 파생 객체 호환을 검사한다. | 236, 246–251행. schema lookup과 ancestry는 probe에서 명시한 fixture helper다. |
| self·target | 기본 concept property는 self, 독립 feature의 기본 property는 target을 요구한다. 명시적 target은 concept에서도 대상 핀을 요구한다. property 로컬은 concept의 자체·상속 field만 허용한다. | 80–86, 245, 342, 550–559, 1003/1031행. 245행 predicate에 직접 `scope:"self"`를 주면 feature에서도 false다. 이 좁은 관찰을 유효한 feature self receiver 계약으로 확대하지 않는다. |
| property 쓰기 | property는 값 출력이며 set의 대상 목록에서 제외된다. | 550–559, 719행. property 쓰기·ref 참조 지원을 추정하지 않는다. |

선택한 실제 편집·검증 함수의 19개 검사가 통과했다. schema·상속·signature 직렬화·render/save callback은 명시된 fixture다. 전체 프로토타입 브라우저, 중첩 실행, C# compile 검사가 아니다. [재현 probe](../tests/probes/v480_nested_property_contracts.py)와 [요청·관찰·해시](evidence/v480-integration/nested-property-contract-review.json)에 범위를 기록했다.

## 현재 실제 엔진과의 간격

[FeatureBlueprint](../src/Confectory.Core/FeatureBlueprint.cs)는 현재 code/call/export/set을 지원한다. 실제 element-authoring metadata host에서 최신 alias-locals profile에 `kind:graph`와 `kind:property`를 각각 주면 `GRAPH_NODE_KIND`, 함수 계약에 `object target`을 주면 `TYPE`으로 거부했다. 세 경우 모두 sourceWritten/executed는 false다. 이것은 거부 경계 검사이며 지원 구현이 아니다. 현재 함수 ABI 타입은 [Declarations](../src/Confectory.Core/Declarations.cs)의 bool/int/long/float/double/string과 지원 배열이다.

[BodyUnitMetadata](../targets/element-authoring/BodyUnitMetadata.cs)는 implementation/body target을 고르고 [BlueprintDocuments.NodeUnits](../src/Confectory.Core/BlueprintDocuments.cs)는 해당 graph의 최상위 code 노드만 발견해 `implementation/body:target/node:localID`를 만든다. [BlueprintCompilation](../src/Confectory.Core/BlueprintCompilation.cs)도 최상위 노드·파일과 `implementation.ID/localID` 소유 키, 단일 nodeId probe·source map·implementation별 receipt를 사용한다. 같은 local ID가 여러 자식에 존재하는 중첩 구조를 이 키에 바로 넣으면 소유·진단이 충돌할 수 있다.

[Generation](../src/Confectory.Core/Generation.cs)의 `this`는 생성된 구현 클래스 인스턴스다. 최종 binding의 각 Invoke는 구현과 Imports를 새로 만들며, BindingKey의 Owner는 정적 provider 해석의 키다. catalog의 schemaFields/typedData는 연결된 선언 자료다. 이들 중 어느 것도 자동으로 특정 live concept instance가 되지 않는다. 기존 C# 본문의 `this`·calls·재귀·연산 의미를 바꾸어 property self를 만드는 방식은 사용하지 않는다.

[RuntimeBase](../packs/runtime-base/README.md)는 기존 수명 계약의 참고가 된다. opaque owner 상태와 owner 범위 int handle, long 값·revision, 구독·폐기를 제공한다. 범용 concept field 저장소가 아니다. 같은 int가 서로 다른 owner에 존재할 수 있으므로 int나 선언 ID만 전달해서 instance 식별을 보장할 수 없다. `Read`의 `[value,revision]`은 새 snapshot이다. 실제 `RuntimeBaseTests.test_lifecycle_and_provider_locality`는 **1/0/0, 12.436초**로 통과했으며 이 범위는 기존 scalar 모델의 30회 수명 주기다.

## 기존 계약으로 설계할 수 있는 중첩 범위

다음은 레퍼런스와 현재 [확정 구조](FEATURE_BLUEPRINT_ARCHITECTURE.md)·typed 함수 호출 ABI를 결합한 구현 제안이다. 이번 조사에서 구현하거나 실행으로 증명한 내용은 아니다. 별도 사용자 정책 선택 없이 진행 가능한 제한 범위다.

1. private 자식을 외부 implementation/body와 전체 부모 node 경로에 소유시킨다. 자식 안의 local ID는 유지하되 원본 locator·View·생성 심벌·진단·Task 권한은 전체 경로로 구분한다. 기존 전역 함수 참조 call은 그대로 유지한다.
2. 현재 타입·next/bool 실행 포트로 동기·비순환 자식 호출을 조립한다. 명시적 입력·ref/out·출력 계약과 호출별 로컬을 사용하고, 부모 로컬을 암묵적으로 캡처하지 않는다. 자식 종료는 부모 호출 뒤의 경로로 복귀하게 기존 함수 ABI를 적용한다. 출력별 할당·경고와 실제 ref/out 저장 위치를 보존한다. receiver가 필요한 자식은 아래 runtime receiver 계약 확정 후 명시적으로 전달한다.
3. 부모·자식의 의미·계약과 모든 소유 본문을 compiler 증거에 포함한다. 원본 해시·누락 파일·imports·compiler identity의 build 전후 관찰, 읽기 예산, 독립 자식 compile과 진단 위치를 재귀적으로 검증한다. 자식 변경으로 부모 완료가 낡는 것도 실제 compiler로 확인한다.
4. 생성·계약 변경은 영향 graph/노드 원본의 필수 원자적 그룹으로 Review/Confirm한다. cold 복원은 입력만 유지하고 현재 원본 재조회·검토를 요구한다. locator, compiler, 독립 probe, CAS, 실제 UI 탐색이 함께 연결되기 전에는 새 종류를 수용하지 않는다.
5. 기존 whole-body 전환의 C#은 원래 구현 인스턴스·이름·calls·scope·재귀를 유지한다. 이를 임의의 정적 자식으로 옮기지 않는다. custom enum 실행 포트, 순환/async, 부모 로컬 캡처나 새로운 객체 ABI는 이 제한 범위의 성공으로 포함하지 않는다.

파일 배치, 내부 JSON 형식, 경로 인코딩과 깊이/개수 예산은 구현·검증 사항이다. 이를 사용자에게 제품 의미 선택으로 넘길 필요는 없다.

## property 실행에 실제로 필요한 결정

선택한 schema/field와 self/target UI의 정적 의미는 위와 같이 확인했다. 현재는 특정 실행 객체를 찾고 그 값을 읽는 계약이 부족하다. 핵심은 **property 대상이 호출자가 소유한 살아 있는 인스턴스인지, 선언된 프로젝트 데이터 객체/기본값인지**다. 같은 concept의 두 인스턴스가 다른 값을 가질 때 선언 ID만으로는 선택할 수 없다.

권장하는 의미는 호출자가 명시적으로 전달한 live receiver를 self/target으로 사용하고, property를 사용하는 시점의 현재 값을 읽는 것이다. 별도 receiver binding을 사용해 기존 C# `this`를 보존하고, 잘못된 타입·폐기·owner 불일치는 오류로 처리한다. 이는 제안이며 아직 선택하지 않았다. 한 호출 전체의 snapshot이 필요한지도 레퍼런스의 선택 함수만으로는 정해지지 않는다. 내부 표현을 CLR 참조로 할지 owner/instance/generation capability로 할지는 이 의미를 정한 다음 결정할 기술 사항이다.

실행 구현 전까지는 field origin·타입·필수 target의 편집 진단과 원본 탐색을 설계할 수 있다. catalog 값이나 임의 singleton을 읽어 property 실행을 완료로 표시하지 않는다. 실제 수용 검사는 같은 타입의 서로 다른 두 인스턴스, 상속 field ID, 중첩 self와 명시적 target, 잘못된 owner/타입·폐기·낡은 참조, 두 읽기 사이 변경을 포함해야 한다.

int/long 계산식의 overflow 오류 대 unchecked wrap 질문은 별도로 답변 대기 중이다. 이 조사에서 정책을 선택하거나 계산식을 추가하지 않았다. 현재 제품 UI의 재현된 결함도 발견하지 않았으므로 UI 수정은 없다. v480 전체 편집 회귀 완료를 뜻하지 않는다.

## 재현과 검사 범위

```sh
python3 tests/probes/v480_nested_property_contracts.py . --output /tmp/v480-nested-property.json
```

Node가 필요하며 ZIP은 읽기만 한다. metadata 세 요청은 증거 JSON에 원문을 보존했다. Release element-authoring host에 각 request를 JSON stdin으로 보내 거부 코드와 무실행 상태를 확인할 수 있다. RuntimeBase 검사는 기존 .NET 테스트 실행기의 `test_lifecycle_and_provider_locality --require-runtime` 필터를 사용했다. 서로 다른 세 검사 범위의 개수를 전체 UI/중첩 실행 통과 수로 합산하지 않는다.

후속 [private graph 구현](BLUEPRINT_PRIVATE_GRAPHS.md)은 이 조사에서 분리한 동기·비순환 typed 범위를 연결한다. 위 19개 레퍼런스 검사는 조사 당시의 독립 근거이며 새 실행 검사의 통과 수로 사용하지 않는다. property와 계산식 정책은 별도 답변 대기다.
