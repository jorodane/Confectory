# v480 선언 계층에서 편집·Confirm·독립 브라우저 복원까지

기준은 `work/current@c8f2951`이다. 기존 `localInventory`의 확정 namespace/선언 ID·종류/소유 여부와 `relationsMap`의 버전 있는 소유 초안 노드·명시적 관계를 private 브라우저 projection으로 결합한다. 언어 parser·모델·공개 편집 API·compiler·실행 의미를 바꾸거나 prototype 저장소를 가져오지 않는다.

## 실제 매핑

| 자료 | 탐색과 정의 이동 |
|---|---|
| namespace | 실제 로컬 registry/manifest의 namespace 트리. 등록/설치/소유를 동일시하지 않는다. |
| 선언 ID·종류 | `object`, `category`, `concept`, `schema`, `function`, `module`, `implementation`의 실제 ID와 종류를 유지한다. namespace/상속 탐색의 개념 그룹 선언 목록은 object/category/concept를 포함하며 schema는 기존 명시적 필터/정의 링크로 연다. |
| 명시적 parent | 선언의 실제 상속 관계만 자식 목록·상속 breadcrumb로 연결한다. `browserCanEnter`는 실제 자식이 있는지, `browserHierarchyParent`는 확인한 parent ID인지 판단한다. category/concept라는 이유로 폴더를 만들지 않는다. 순환/불명확/64단계를 넘는 ancestry는 탐색 루프로 만들지 않는다. |
| contain·use·schema | `contain`은 상속 parent나 가상 폴더 소속으로 바꾸지 않는다. 기존 선언 정의/참조 목록에서 실제 관계를 확인한다. 직접 선언한 `use schema`는 같은 소유/등록 정의 경로로 연결하며 Variation의 상속 스키마 값은 기존 schema owner가 판단한다. |
| 소유 정의 | 기존 `select`/schema/선언 편집기로 연다. 파싱할 수 없는 소유 초안은 기존 고급 source로 연다. source 미적용 입력의 기존 선택 가드를 유지한다. |
| 등록 정의 | 등록 목록만으로 읽기 범위를 늘리지 않는다. 소유 map에 있는 직접 참조 source의 revision/hash를 기존 `readReferenceDefinition`에 전달한다. 직접 참조·registry·의존성·identity/CAS 검증이 최종 판단한다. 무관한 등록 항목은 읽기 전용 목록이다. |

브라우저의 필드/채우기 입력은 탐색 위치·계층 조회와 별개이며 원래 source/schema CAS 기준을 유지한다. namespace·parent·검색·그룹은 private metadata다. 계층을 바꾸어도 필터 입력을 지우거나 편집 대상을 자동 선택하지 않는다. 다른 그룹의 parent로 이동할 때 기존 그룹의 검색/위치를 보존한다. 확인할 수 없는 저장 위치를 루트로 임의 치환하지 않는다.

## 조회·창·복원

기존 소유 관계 조회를 필요할 때 지연 실행하며 프로젝트·창 복원이 끝난 뒤 읽는다. source revision이 바뀌거나 새 소유 선언이 생기면 관계를 다시 읽는다. 읽기 실패는 원본과 입력을 유지하며 반복 호출 루프를 만들지 않고 명시적 다시 읽기를 제공한다. 복원/예약된 읽기가 끝나기 전 조작을 대기 상태로 유지한다. 기존 관계 조회 응답은 활성 schema/inspection을 포함하지 않으므로, 선택 ID가 그대로일 때 기존 schema/inspect 읽기 API로 활성 projection을 복원한다. source나 미적용 입력의 버전을 재기준화하지 않는다. 읽기 완료가 Save/Confirm 결과를 자동 성공 메시지로 덮어쓰지 않는다.

Workspace의 창 검색은 실제 선언 ID·표시 이름·ancestor를 찾는다. 전달받은 group·창 key·parent·배치를 사용해 독립 브라우저를 연다. 소유/등록 정의 열기와 우클릭도 같은 소유/읽기 전용 gate를 사용한다. 독립 창은 기존 definition/선택/입력과 각각의 적용/미적용 검색·parent·namespace·그룹을 복원한다.

탐색 projection의 관계 snapshot과 참조 조회용 source hash는 runtime cache에만 둔다. 기존 셀/채우기 입력의 CAS 버전은 기존 private presentation 계약대로 보존한다. `project.objects`는 비열거 getter이며 원본·권한의 별도 저장소가 아니다. 실제 재시작 후 기존 조회를 통해 관계를 다시 읽는다. prototype의 Workspace 링크 수명·자동 쓰기 선택·새 category 편집/삭제·참조 치환은 추가하지 않는다.

## 통합 검증과 경계

실제 Chromium 시나리오는 **category 상속 탐색 → category/concept·직접 schema 정의 → 소유 객체/등록 parent 정의 → Variation 생성·등록 compiler Confirm → Workspace에서 독립 parent 브라우저 → 명시적 필드 비교·원자적 채우기·별도 입력 보존 → 두 번째 Review/Confirm → 서로 다른 parent·검색·셀/채우기 입력의 실제 콜드 복귀**다. 생성 등록은 기존 명시적 생성 그룹 Review를 사용하고, 이후 값 편집도 기존 별도 Review/Confirm을 사용한다. 필요한 등록/쓰기 ID를 몰래 확장하지 않는다.

순수 projection 검사는 live parent가 확정 inventory보다 우선하는지, category/concept·contain/use가 가상 폴더가 되지 않는지, 직접 참조 source·schema ID·순환·실패 재시도·프로젝트 격리를 확인한다. 소유/등록 관계 조회·참조 read-only·버전/원자적 table 모델 및 영향 UI 회귀를 같은 고정 원본에서 실행한다. 최종 원본·정확한 검사 결과·일반 checkout HEAD는 [검증 JSON](validation/v480-declaration-navigation.json)에 기록한다. 집중/초기 실패와 최종 고유 검사 수를 합산하지 않는다.

현재 projection은 소유 초안의 명시적 관계와 확정 registry identity를 연결한다. 무관한 외부 팩 내부의 상속 원본을 일괄 읽거나 상속된 foreign 참조에 직접 참조 권한을 부여하지 않는다. category/concept의 전체 제품 의미를 prototype 폴더로 구현했다고 주장하지 않는다. 자동 전체 필드 합집합/계산 열, 생성·삭제 전체 Undo, Workspace 시각 링크는 별도이며 overflow 정책도 유지한다. main·원본 ZIP·Android 설정을 보존하고 실계정·유료 호출은 하지 않는다.

최종 고정 제품/테스트 원본은 **12개**다. 같은 원본에서 실제 Chromium 영향 회귀 **14/0/0, 623.115초**, projection/소유 관계/직접 등록 참조/원자적 table 모델 **4/0/0, 65.037초**, Windows/Android 관리 프로필 컴파일 **1/0/0, 150.1초**가 통과했다. 테스트 프로젝트 빌드는 경고·오류 없이 통과했다. 일반 Git checkout·보존 CRLF/새 LF·39개 리소스·실제 Home 시작·변조 거부의 구현 HEAD와 결과는 검증 JSON에 기록한다.
