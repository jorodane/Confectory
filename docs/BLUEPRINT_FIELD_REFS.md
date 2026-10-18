# 제한한 실제 필드 ref

`sync-acyclic-property-ref-v1` / `feature-blueprint-source-v14`에서 `kind:"property-ref"` 노드를 명시적으로 추가한다. 이전 profile의 읽기·값 슬롯을 ref로 재해석하지 않는다. 루트의 전환 내용을 읽고 공유 초안 전환을 선택해야 하며 private graph도 함께 전환한다. 기존 property Read는 노드 도달 시 읽은 결과를 유지하고, 새 field ref는 노드 도달 시 실제 필드 셀을 붙잡아 이후 읽기와 ref/별칭 대입이 그 셀을 공유한다.

| 필드 | mutable ref | 기존 검증을 보존하는 이유 |
|---|---|---|
| general single bool/int/long | 지원 | 안전한 C# 대입의 전체 값 범위가 기존 필드의 값 범위와 같다 |
| float/double | 거부 | ref 대입은 NaN/Infinity를 직접 저장할 수 있다 |
| string·모든 배열 | 거부 | ref 대입은 기존 null/원소/카디널리티 검증을 거치지 않는다 |
| schema-reference single/multiple | 거부 | object/object[] ref 대입으로 다른 schema의 객체·원소 또는 null을 넣을 수 있다 |
| compound/function·unset·stale field | 거부 | 지원한 초기화된 실제 필드 저장소와 정확한 현재 계약이 필요하다 |

schema-reference에 ref를 연결하기 위해 schema 검증을 생략하거나 사후 copy-in/out을 하지 않는다. 해당 필드는 검증된 Read/Set을 유지한다. 더 넓은 mutable ref를 지원하려면 null·유한값·schema 호환 조건과 CLR 타입/ABI의 경계를 별도로 정해야 한다. 일반 enum/Vector3 ABI·compound/function live field·overflow 정책도 이번 범위에 넣지 않는다.

## 실제 저장소와 수명

새 ObjectModel 인스턴스의 비공개 형식은 v2다. general 단일 bool/int/long의 첫 유효한 초기화에서 `StrongBox<T>` 하나를 저장한다. 이후 Set/Write는 그 셀의 Value만 바꾸고 셀을 교체하지 않는다. 같은 인스턴스의 같은 필드에서 반복 획득한 RefCell은 동일한 객체다. 다른 인스턴스는 독립 셀을 가진다. Read는 셀의 primitive 값을 반환하고 기존 배열·객체 값은 기존 참조를 그대로 전달한다. 선언 data에서 값을 만들지 않고 생략한 필드는 unset으로 남긴다.

`Confectory.ObjectModel::RefCell(target,owner,field,contractHash) -> object`는 v2의 명시적 실제 대상, owner lineage, 필드 ID/hash, 지원 종류와 초기화된 정확한 typed cell을 검사한다. v1 인스턴스는 기존 Read/Write/Set을 유지하며 ref는 자동 변환 없이 거부한다. 필드 descriptor/hash는 바꾸지 않아 이전 읽기·Set 원본을 임의로 stale 처리하지 않는다. 호환 provider를 명시적으로 바인딩하면 반환 셀의 정확한 StrongBox 타입과 동일 필드의 안정된 동일성을 지켜야 한다. null이나 다른 typed cell은 실행 노드에서 거부한다.

graph의 ref 노드에는 `(object target) -> bool/int/long`, `propertyOwner`, `field`, `fieldContractHash`와 대상 연결을 기록한다. C# 본문 파일이나 Task 권한을 만들지 않는다. 생성기는 그 노드의 실행 label에서 cell을 한 번 획득하고 이후 값 연결을 `cell.Value`, ref 연결을 `ref cell.Value`로 생성한다. primitive 임시 슬롯을 만들어 되돌려 쓰는 경로는 없다. 선행 실행·타입·scope 지배 관계는 기존 compiler가 검증한다. 연결되지 않은 경로에서는 RefCell을 호출하지 않는다.

ref는 획득한 실제 인스턴스의 셀에 고정된다. 이후 receiver 변수에 다른 객체를 넣어도 이미 획득한 ref가 다른 객체로 이동하지 않는다. 같은 셀에 대한 Set·별칭 로컬 set·중첩 ref 호출은 즉시 보이며, 예외 전 대입도 그대로 남는다. 일반 함수의 값 반환은 그때의 값을 반환하며 새로운 ref 반환 ABI나 영속 참조 저장은 도입하지 않는다.

이미 C# 호출자에게 전달한 ref를 회수하거나 실시간 schema 변경에 맞춰 이동시키는 기능은 없다. 인스턴스의 캡처된 필드 계약은 바꾸지 않으며 새 획득마다 실제 인스턴스와 compiled hash를 비교한다. source의 schema drift는 기존 편집/빌드 CAS와 compiler Confirm에서 거부한다. 바뀐 schema와 호환되지 않는 인스턴스를 조용히 변환하거나 ref를 다른 셀로 연결하지 않는다.

## 편집과 검증

필드 선택 창에서 지원하지 않는 mutable ref 필드를 표시하고 비활성화한다. backend도 같은 경계로 거부한다. 미리보기는 관련 함수·구현·소유 원본과 schema/object/concept의 원본 리비전/hash를 관찰하고 실제 객체나 getter를 실행하지 않는다. RefCell import와 구조 ref 노드를 함께 공유 초안에 적용한다. Save/새 호스트 복원은 ref 모드·미적용 대상과 선택을 보존하되 preview token을 복원하지 않는다. 현재 계약을 다시 읽어야 한다. 재연결은 ID·실행 경로·private branch 소유 관계를 유지한다.

실제 C# ref 매개변수와 기존 입력/노드 슬롯 별칭을 그대로 사용한다. 새 코드 노드는 본문과 소유 graph를 함께 Review해야 하고 RefCell import가 빠진 부분 Confirm은 실패한다. stale schema는 필드 ref 원본과 진단을 유지하며 Confirm에서 최종 파일을 바꾸지 않는다. 기존 Worker의 네 도구와 자기 C# source 권한을 넓히지 않는다.

CLR 검사는 즉시 alias와 Set의 `40/40/70/True`, 읽기 snapshot과 필드 별칭의 `1030/30`, private ref 호출 뒤 `52/52`, 예외 후 `72/73/True`, receiver 변수 교체 뒤 `31/31/42`, bool 및 long 최대값을 확인한다. 잘못된 대상·owner/hash·unset·v1·제약 필드의 ref와 기존 NaN/null/schema 불일치 Set의 거부도 실제 CLR로 확인한다. 공개 편집 경로는 미리보기→CAS→Save/cold→ref 두 개와 C# ref 매개변수→그룹 Confirm→실제 `31,41,31`→schema drift 거부를 확인한다. Chromium은 실제 필드 선택·ref 매개변수 편집·새 호스트 복원·Confirm을 확인하며 사용자 객체 생성 fixture는 실행되지 않는다.

최종 고정 원본과 단계별 보정, 서로 다른 검사, 일반 Git checkout·리소스·실제 Home 시작은 [검증 기록](validation/blueprint-field-refs.json)을 따른다. main·원본 ZIP·Android 설정을 보존하며 실계정·유료 호출·기기 실행·전체 v480 완료를 주장하지 않는다.

최종 고정 제품·테스트 원본 29개(`34eb8063be163a394af9962994483823bf66b15e0262a05dd072169c55425d63`)에서 CLR/property·공개 편집·private graph·switch·ref **49/0/0, 472.493초**, 기존 graph/편집 **16/0/0, 645.506초**, 실제 Chromium **6/0/0, 606.695초**, Windows/Android Home 관리 프로필 컴파일 **1/0/0, 156.565초**로 통과했다. 구현 커밋 `c5db8d5237d3d6064f94db5e1f44006b382908dc`의 일반 checkout·보존 CRLF/새 LF·41개 리소스·실제 Home 시작·변조 거부는 **1/0/0, 6.763초**다. 서로 다른 검사 총 73개이며 모든 최종 단계가 같은 고정 원본을 사용했다. Release 솔루션 빌드는 경고/오류 0개다. 초기 fixture 보정과 반복 검사는 최종 수에서 제외했다. [실제 ref 미리보기](validation/blueprint-field-refs-preview.png), [Confirm 후 새 호스트 복원](validation/blueprint-field-refs-published.png)은 실제 브라우저 캡처다.
