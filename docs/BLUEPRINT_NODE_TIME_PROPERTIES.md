# 노드 도달 시 실제 객체의 프로퍼티 읽기

사용자가 2026-10-17 확정한 의미는 실행이 해당 노드에 도달한 시점의 실제 객체 값을 읽는 것이다. 새 `sync-acyclic-property-v1` / `feature-blueprint-source-v10`은 읽은 결과를 typed 슬롯에 저장하고 이후 소비자에게 전달한다. 같은 함수를 다시 호출해 그 노드를 실행하면 새 값을 읽는다. 배열·객체는 원래 참조를 전달한다. 깊은 복사나 함수 진입 시 일괄 스냅샷을 도입하지 않는다.

[이전 조사](BLUEPRINT_NESTED_PROPERTY_CONTRACT_REVIEW.md)의 ‘사용 시점 현재 값’ 제안과 [private graph 단위](BLUEPRINT_PRIVATE_GRAPHS.md)의 property 답변 대기는 당시 기록이다. 확정된 실행 의미는 이 문서의 **노드 도달 시 읽기**다. int/long 계산식 overflow의 오류 대 wrap 결정은 여전히 대기 중이며 계산식 구현과 기존 C# 연산 변경은 포함하지 않는다.

## 실제 대상과 타입

대상은 호출자가 함수 입력, 로컬 또는 선행 노드 결과로 전달한 `object` 참조다. 선언 ID·catalog의 `data`·전역 singleton·C# 구현 인스턴스의 `this`에서 런타임 대상을 추정하지 않는다. 일반 CELEM 함수에 `object`와 `object[]` CLR 계약을 추가했고 graph에서는 v10에서만 허용한다. 일반 schema field의 primitive 타입 계약은 유지한다.

`RuntimeObjectContracts`가 object/concept의 타입 상속, 적용 schema 상속과 effective field를 읽는다. 필드 ID는 기존 schema origin과 이름을 합친 `App::Vitals/field:health`이며 필드 hash에는 origin·이름·종류·타입·카디널리티를 포함한다. 같은 이름의 다른 origin은 기존 ambiguity 규칙대로 거부한다. 선언 `data`는 런타임 값이나 필드 hash에 넣지 않는다.

| 필드 | 노드 반환 계약 |
|---|---|
| general single | 기존 bool/int/long/float/double/string |
| general multiple | 해당 CLR 배열 |
| reference single / multiple | object / object[] · 참조 schema 호환 검사 |
| compound / function | 목록에 표시하되 live read 지원 전으로 거부 |

새 `Confectory.ObjectModel` 팩은 호출자가 소유한 실제 CLR 값의 기본 구현이다. Create는 descriptor와 명시한 필드 ID·실제 값으로 **서로 다른 인스턴스**를 만든다. 생략한 필드는 unset이며 읽으면 오류다. Read/Write는 실제 타입 lineage, 필드 ID/hash, 정확한 primitive/배열 또는 reference schema 계약을 검사한다. null 대상·다른 owner·unset·잘못된 타입/카디널리티·변경된 필드 계약을 거부한다. 배열과 참조는 복사하지 않는다. 불투명 내부 상태를 직접 편집하는 API나 선언 데이터 자동 초기화, 직렬화, 수명 관리자를 추가하지 않는다. 프로젝트가 별도 CLR 모델을 쓰면 같은 typed Read 계약의 구현을 명시적으로 바인딩할 수 있다.

## 원본·실행·private graph

프로퍼티는 `kind:"property"` 구조 노드이며 `propertyOwner`, `field`, `fieldContractHash`, `(object target)->필드타입`과 명시적 `arguments.target`을 기록한다. 생성된 wrapper는 그 노드의 실행 label에서 한 번 Read를 호출하고 일반 결과 슬롯에 대입한다. 뒤의 노드의 값 연결은 저장된 슬롯을 읽는다. 프로퍼티 자체를 set/ref의 field lvalue로 만들지 않는다. 결과 슬롯의 기존 별칭·ref 의미는 유지한다.

프로퍼티에는 C# 본문 파일이나 Task 권한을 만들지 않는다. 기존 C# 노드와 사용자 연산은 그대로 보존한다. private graph에서도 명시적 object 입력을 통해 대상을 전달하며 부모 receiver를 캡처하지 않는다. 연결되지 않은 실행 경로에서는 Read를 호출하지 않는다.

v10 전환은 명시적 미리보기 뒤 공유 초안에만 적용하며 private 자식들도 함께 전환한다. 이전 profile을 읽는 것만으로 전환하지 않는다. 기존 v9의 전체 경로 소유권, typed ref/out과 로컬 수명 규칙을 유지한다.

## 편집과 검증 경계

화면에서 타입 목록(32개씩), 현재 필드 목록, 실제 대상 연결을 선택하고 현재 계약을 다시 읽어 확인한 뒤 구조 노드와 typed Read import를 함께 적용한다. 대상 프로젝트에 ObjectModel 팩 등록과 직접 의존 설정이 필요하며 이를 몰래 추가하지 않는다. 필드 목록과 미리보기는 getter·객체 생성·사용자 코드를 실행하지 않는다.

root graph·구현·소유 leaf·함수·관련 schema/object/concept와 등록부의 원본 리비전/hash를 관찰한다. 적용 전 CAS와 등록된 외부 계약을 다시 확인한다. 스키마 변경은 오래된 미리보기와 일반 graph 편집 기준을 무효화한다. stale 필드는 화면에 기존 원본과 진단을 유지하며 명시적 재연결을 요구한다. 재연결은 node ID와 실행 연결을 유지하고 현재 필드·대상 계약을 수용한다. 타입이 달라져 기존 소비자와 맞지 않으면 별도 연결 편집과 compiler 검토가 필요하다.

Save/cold 복원은 미적용 입력을 유지하고 preview/basis를 재사용하지 않는다. Review는 원본 검토이고 Confirm에서 실제 compiler가 선택된 원본 조합을 검사한다. 필요한 import나 field 계약이 빠진 조합은 Confirm에서 거부하며 최종 파일을 바꾸지 않는다. 게시 전 새 객체의 소유·등록 초안은 기존 그룹으로 유지하며, 이미 게시된 property 계약의 overlay 검사와 구분한다. code-node Worker는 관련 property 선언의 hash를 관찰하지만 기존 네 도구와 자기 C# source 권한만 가진다. schema 원본 읽기 권한을 넓히지 않고 관련 선언 변경 후 Stage를 거부한다.

실제 build에는 관련 선언의 raw bytes를 입력 증거로 포함하고 compiler 뒤에도 다시 확인한다. 도중에 스키마가 바뀌면 `BLUEPRINT_SOURCE_CHANGED`로 거부하고 이전 성공 산출물을 유지한다.

## 검증 기록

최종 회귀 수와 소스 hash, 실패 단계 및 수정 범위는 [properties.json](evidence/blueprint-node-time-properties/properties.json)에 기록한다. 실행 검사는 CLR 결과와 참조 동일성을 확인한다. Chromium 검사는 실제 편집·cold·원본 보존·그룹 compiler Confirm을 확인하며 사용자 함수 실행을 주장하지 않는다. 별도 객체 생성 fixture는 미리보기/Confirm에서 호출되면 예외를 던져 실행되지 않음을 확인한다.

실제 실행 예: 노드 전 `10→20`, 노드 뒤 `20→30` 변경 시 이후 두 소비자의 결과는 `2020`이고 실제 필드는 `30`, 읽기 횟수는 `1`이다. 다음 호출에서는 새 값 `40`을 읽으며 다른 파생 인스턴스와 값·읽기 횟수를 공유하지 않는다. 배열 교체 뒤에도 기존 결과는 원래 배열을 유지하고 그 배열 자체의 변경은 보인다. 객체 참조 교체와 참조 대상의 후속 변경도 같은 기준으로 확인한다.

main·원본 ZIP·Android 설정을 변경하지 않는다. 실제 계정·유료 모델·사용자 PC 설치·native/device 실행은 검증 범위에 넣지 않는다. v480 전체 구현 완료를 뜻하지 않는다.

고정한 제품·테스트 47개 파일에서 최종 엔진/공개 편집/ABI **82/0/0, 1576.979초**, 실제 Chromium 편집은 서로 다른 테스트를 맡은 두 프로세스에서 **25/0/0**(개별 프로세스 최대 908.750초), Windows/Android 관리 프로필 **1/0/0, 171.496초**로 통과했다. 이전 중복 검사는 합산하지 않는다. [현재 계약 미리보기](evidence/blueprint-node-time-properties/property-preview.png)와 [확정 후 복원](evidence/blueprint-node-time-properties/property-published.png)은 실제 실행한 브라우저 캡처다.

구현 커밋 `2536d714675b56edf69ce45c1f502d4d6351bbdb`의 일반 Git checkout·보존 CRLF/새 LF·33개 리소스·실제 Home 시작·변조 거부는 **1/0/0, 6.600초**로 통과했다. 최종 회귀 뒤 제품·테스트 소스는 바뀌지 않았다.
