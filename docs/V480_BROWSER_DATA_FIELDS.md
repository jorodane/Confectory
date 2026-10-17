# v480 브라우저 Data 필드 비교

기준은 `work/current@3748ac8`과 보존한 `main@32dd44f`의 v480 레퍼런스다. 레퍼런스의 `browserDataItems`는 demo 객체의 effective field/value를 직접 표시한다. 실제 소비자는 그 demo 저장소를 가져오지 않고 기존 `tableOptions` → `openTable`/`configureTable` → `SnapshotVersioned` → `editTable` 계약에 연결한다.

## 지원하는 매핑

| 화면 | 실제 계약 |
|---|---|
| Data의 비교 대상·필드 선택 | 기존 소유 객체 picker, 한 정의에 객체 1~64개·필드 1~16개. 설명, 메타데이터, `data:["field",…]` 경로는 picker가 제공한 정확한 ID를 쓴다. |
| Data의 이름·종류·작업 사본과 필드 열 | 브라우저의 현재 목록에 명시적으로 선택한 비교 대상이 겹칠 때 기존 snapshot의 `cellInfo`를 표시한다. 검색/그룹/namespace 변경으로 대상을 자동 확장하지 않는다. |
| 셀 입력·적용·재정의 제거·취소 | 독립 InstantTable과 같은 셀 렌더러 및 기존 `editTable`. 입력은 private presentation이며 Apply에서만 공유 초안을 바꾼다. |
| 타입과 원본 충돌 | 기존 타입 검사와 표시한 source revision/SHA-256/view hash를 그대로 전달한다. 실패 시 입력·원래 버전·기존 초안을 유지하며 자동 재시도/재기준화하지 않는다. |
| 비교 구성 변경 | 기존 definition hash CAS. 새 view 준비가 성공한 뒤 기존 subscriptions를 교체한다. 숨긴 객체/필드의 입력은 동일 ID/path와 원래 버전으로 보존하며 원래 구성을 열면 돌아온다. |
| Save·변경 검토·Confirm | 기존 공유 초안 저장과 compiler-backed Review/Confirm. 미적용 입력은 숨긴 대상까지 먼저 적용/취소해야 브라우저의 비교 변경을 검토하거나 비교를 해제할 수 있다. |
| 외부 팩·다른 종류·미선택 행 | 소유/종류/명시적 선택 여부를 표시한다. 외부 팩 필드 값을 임의로 조회하거나 쓰기 권한을 만들지 않는다. 기존 등록 정의의 읽기 전용 조회는 유지한다. |
| 재열기·재시작 | 기존 browser metadata의 table definition/inputs/width/order를 재사용한다. 같은 내용 재열기는 입력 DOM을 유지하고, 실제 재시작은 source owner를 다시 빌려 현재 값을 조회한다. |

검색 결과가 없어도 비교 설정과 입력 상태를 조작할 수 있다. 보기 밀도나 비교 구성을 바꿔도 셀별 미적용 입력을 지우지 않는다. 열 너비/이동은 같은 표시 계약을 사용한다. Data 셀 입력의 Delete/Enter·더블클릭·문맥 메뉴는 행의 객체 선택 명령과 구분한다.

프로젝트 모델·엔진·공개 편집 API·compiler 실행 의미를 추가하지 않는다. 표는 기존 borrowed view이며 행 데이터의 새 저장소가 아니다. 값은 `cellInfo.valueJson`의 정확한 JSON 텍스트를 사용하고 Int64를 JavaScript Number로 재인코딩하지 않는다.

## 검증

실제 Chromium 검사와 영향 회귀, 관리 프로필 컴파일, 일반 Git checkout·리소스 시작 검사를 동일한 고정 원본에서 실행하고 [검증 JSON](validation/v480-browser-data.json)에 기록한다. 집중 검사·보정 이력은 최종 고유 검사 수에 더하지 않는다.

## 남은 차이

이 변경은 명시적 소유 객체/필드 비교다. prototype의 모든 객체에서 자동으로 필드를 합치기, 사용자 정의 계산 열, browser category/concept 계층의 전체 의미, 외부 dirty overlay, Workspace 시각 링크 그래프는 추가하지 않는다. 이 체크포인트는 셀별 Apply를 제공한다. 후속 [브라우저 원자적 채우기](V480_BROWSER_ATOMIC_FILL.md)에서 기존 독립 InstantTable의 다중 행 fill을 같은 폼/핸들러로 연결했다. 구조적 field lvalue/ref·일반 enum/Vector3 ABI·새 overflow 정책을 정하지 않는다.

Home 포함 팩 수·마지막 편집 이벤트 시각은 별도 미결이다. native OS/실기기·사용자 PC 설치·실계정·유료 호출은 검증 범위 밖이다. main·원본 ZIP·Android 설정은 보존한다.

최종 고정 제품/테스트 원본은 **8개**다. 동일 원본에서 실제 Chromium 영향 회귀 **10/0/0, 369.577초**, InstantTable 타입·버전·정밀도·borrowed lifetime **1/0/0, 46.526초**, Windows/Android 관리 프로필 컴파일 **1/0/0, 139.209초**가 통과했다. 최종 테스트 프로젝트 빌드는 경고·오류 없이 통과했다. 일반 Git checkout·보존 CRLF/새 LF·38개 리소스·실제 Home 시작·변조 거부 검사의 정확한 구현 HEAD와 결과는 검증 JSON에 기록한다.
