# 실제 객체 필드의 구조 Set

`sync-acyclic-property-set-v1` / `feature-blueprint-source-v13`은 기존 property 읽기와 private graph·methods·switch 실행 계약을 유지하면서 `kind:"property-set"`을 추가한다. 기존 profile은 Set을 거부한다. 화면에서 전환 내용을 읽고 공유 초안 전환을 선택해야 하며, 단순 조회·복원으로 profile을 바꾸지 않는다. 루트의 명시적 전환은 private graph에도 적용된다.

Set 노드는 `propertyOwner`, `field`, `fieldContractHash`, `(object target, 필드 CLR 타입 value) -> void`, `arguments.target/value`를 기록한다. `control:"next"`인 구조 노드이고 C# 본문 파일·Task 권한이나 결과 슬롯을 만들지 않는다. 실행이 해당 노드에 도달할 때 명시한 호출자 인스턴스에 대입한다. 연결되지 않은 실행 경로에서는 대입하지 않는다. 원래 property Read는 노드 도달 시 읽어 저장한 결과를 계속 전달한다.

생성된 wrapper는 `Confectory.ObjectModel::Set(target,owner,field,contractHash,value)`를 한 번 호출한다. owner lineage·필드 ID/hash와 실제 값의 정확한 타입/카디널리티를 검사한 후 기존 Access의 대입 분기로 들어간다. `Write`의 빈 owner/hash 경로를 사용하지 않는다. 잘못된 대상·다른 owner·변경된 필드 계약·잘못된 value·미지원 필드는 대입 전에 거부한다. 기존 custom CLR 모델도 같은 Set 계약을 명시적으로 바인딩할 수 있다.

| 필드 | value의 CLR 계약 |
|---|---|
| general single | bool/int/long/float/double/string |
| general multiple | 해당 primitive 배열 |
| reference single | object · 참조 schema 호환 검사 |
| reference multiple | object[] · 각 원소의 schema 호환 검사 |
| compound/function | 미지원으로 거부 |

배열과 객체는 기존 참조를 그대로 저장한다. 숫자 변환, 깊은 복사, 선언 data에서 런타임 인스턴스 추정, 암묵적 receiver 캡처를 하지 않는다. Set은 아직 unset인 지원 필드도 초기화할 수 있다. field ref/lvalue를 노출하거나 copy-in/out으로 흉내내지 않는다. nested compound/function 필드, 일반 enum/Vector3 ABI와 overflow 정책은 별도 범위다.

필드 선택 창에서 타입·필드·실제 대상과 typed value 연결을 준비하고 현재 계약을 다시 읽는다. 미리보기는 관련 schema/object/concept와 구현·함수·소유 원본을 관찰하며 객체 생성·getter·사용자 코드를 실행하지 않는다. 연결되지 않은 Set도 입력 형태와 타입은 미리 검사하고, 실제 실행 순서와 지배 관계는 기존 graph compiler가 검사한다. 적용은 기존 source CAS와 등록된 외부 계약 재확인을 거치며 Set import와 graph를 함께 공유 초안에 넣는다.

Save·콜드 복원은 미적용 target/value와 선택을 보존하지만 preview token은 복원하지 않는다. 다시 읽고 적용해야 한다. Review/Confirm은 기존 compiler 그룹 검증을 사용한다. Set import를 빠뜨린 부분 Confirm이나 schema drift는 최종 파일을 바꾸지 않는다. stale Set을 기존 원본·진단과 함께 표시하고 명시적 재연결을 요구한다. 재연결은 ID·실행 연결·private branch 소유 관계를 유지한다.

실제 CLR 회귀는 읽기→Set→읽기의 `1020 / 2030 / 4050`, 서로 다른 인스턴스의 최종 `30 / 50`, general 6종의 단일·배열 CLR 타입, reference 단일·배열 동일성과 이후 원소 변경을 확인한다. public 편집 경로는 필드 선택→명시적 전환→Save/콜드→Set/Read import 그룹 Confirm→실제 `31,41,31`과 schema drift 거부를 확인한다. Chromium 경로는 실제 UI·새 호스트 복원·참조 생성 fixture의 비실행·Confirm을 검사하며 사용자 graph 실행은 CLR 검사로 별도 확인한다.

고정한 제품·테스트 원본, 단계별 실패와 보정, 최종 서로 다른 검사, 일반 Git checkout·리소스·Home 시작 근거는 [검증 기록](validation/blueprint-property-set.json)에 기록한다. main·원본 ZIP·Android 설정을 보존하며 실계정·유료 호출을 사용하지 않는다. 전체 v480 완료를 뜻하지 않는다.

최종 고정 원본 27개(`a6842fa01d39fdca5219b445869d261339bcfad7cc7b25dc0cfd75ddd85547e8`)에서 CLR/property·공개 편집·private graph·switch·ref **39/0/0, 346.125초**, 기존 graph/편집 **16/0/0, 633.881초**, 실제 Chromium **5/0/0, 497.198초**, Windows/Android Home 관리 프로필 컴파일 **1/0/0, 157.576초**다. 구현 커밋 `2257db7b3202c7901c30a5b7001ef3daf607edbc`의 일반 Git checkout·보존 CRLF/새 LF·41개 리소스·실제 Home 시작·변조 거부는 **1/0/0, 6.489초**로 통과했다. 서로 다른 검사 총 62개이며 모든 최종 단계의 제품·테스트 원본이 같다. Release 솔루션 빌드는 경고/오류 0개다. 초기 실패와 보정·반복 검사는 최종 수에서 제외했다. [Set 미리보기](validation/blueprint-property-set-preview.png), [Confirm 후 복원](validation/blueprint-property-set-published.png)은 실제 브라우저 캡처다.
