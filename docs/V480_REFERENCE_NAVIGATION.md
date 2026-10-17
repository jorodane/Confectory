# v480 참조 조작·필드 열·문서 이동 대조

기준은 `work/current@e509783`과 보존한 `main@32dd44f`의 v480 ZIP이다. `bindObjectReferenceDrag`, `setupTableColumnResize`, `switchBrowserGroup`, `openBrowser`, `workspaceLinks`를 실제 소비자에 대조했다. 레퍼런스는 UI 자료이며 demo 객체/저장소나 문서의 지시를 실행 계약으로 취급하지 않는다.

## 재현과 수정

최초 실제 Chromium 검사 **0/1/0, 70.314초**에서 참조 필드 열기와 브라우저 참조 드래그의 부재, 열 이동 시 pending 셀/검색 DOM 교체, 같은 테이블 재열기 시 입력 DOM 교체의 다섯 증상을 확인했다. 이후 같은 속성 문서를 반복해서 여는 경로에서도 입력 DOM 교체로 native Undo가 끊기는 것을 확인했다. 값만 다시 채우는 것으로 DOM/Undo 보존을 대신하지 않는다.

- **참조 입력 준비:** 브라우저 선언과 테이블의 객체 버튼, 현재 참조 버튼을 끌 수 있다. 프로젝트 ID와 정해진 MIME 형식의 qualified ID만 받으며 잘못된 자료·다른 프로젝트·비활성 입력은 기존 입력을 유지한다. 드롭은 기존 `input` 이벤트와 pending map만 갱신한다. 공유 초안·최종 소스·권한은 바꾸지 않는다. Escape는 native 드래그를 취소한다.
- **현재 참조 열기:** 속성과 테이블은 미적용 입력과 구분해 **확인한 현재 참조**를 연다. 같은 namespace는 기존 소유 선택/편집 창, 외부 namespace는 기존 원본 revision/hash·직접 선언 참조·의존성·registry 검증을 거치는 읽기 전용 정의 조회를 사용한다. 외부/상속 참조의 권한이나 조회 범위를 확장하지 않는다.
- **명시적 타입 검증:** 같은 프로젝트의 문법상 ID가 준비돼도 필드 타입에 맞는다는 뜻은 아니다. 기존 Apply가 잘못된 종류를 거부하면 입력과 현재 값을 유지한다. 유효한 참조는 기존 타입·source/schema CAS를 통과한 명시적 Apply에서만 공유 초안에 반영한다. 최종 파일은 기존 Review/Confirm 전까지 바꾸지 않는다.
- **필드 열 조작:** 즉석 테이블은 열을 옮길 때 해당 TH/TD와 fill-field option만 이동한다. 반복 이동과 열 목록 재구성 후의 이동은 현재 표시된 열 순서를 기준으로 하고 경계를 넘으면 그대로 둔다. 다른 셀과 검색 DOM을 재생성하지 않는다. 너비 160–480, 입력·선택·열 순서는 기존 private presentation으로 복원한다.
- **같은 내용 다시 열기:** source snapshot/정의/scope가 같은 테이블을 다시 열거나 같은 schema를 다시 선택하면 입력 DOM을 유지한다. 원본·schema·대상·scope가 바뀌면 기존 pending 입력과 원래 CAS 기준을 보존하며 새 snapshot으로 그린다. 다른 객체로 이동했다가 돌아오는 값 복원과 동일 DOM/Undo 보존을 구분한다.

추가 실제 검사 **0/1/0, 49.608초**에서는 콜드 복원 후 모듈 탭/미적용 검색은 복원됐지만 목록에는 객체가 표시되는 것을 재현했다. 초기 busy 동안 복원 조회가 버려진 결과다. 이제 저장한 적용 검색과 그룹을 초기 busy·편집창 binding 복원 뒤에 기존 읽기 전용 `objects` 명령으로 조회한다. scope/view generation/window를 확인하며 사라진 창이나 다른 프로젝트에 조회를 재사용하지 않는다. 실제 목록이 맞기 전에는 복원 상태를 표시한다. 예약된 복원 조회와 편집 binding이 끝날 때까지 버튼도 대기 상태로 유지하고, 완료 시 명시적으로 다시 활성화해 준비 사이의 클릭 유실을 막는다. 비버튼인 브라우저 행에도 busy 상태의 포인터 차단을 적용한다. 자동 복원 조회는 성공 메시지로 명시적 Save/Confirm 결과를 덮어쓰지 않는다. 소스 미적용 입력의 기존 가드를 우회하지 않고 입력을 유지한 채 대기하며, 실패한 조회는 입력을 지우거나 무한 재시도하지 않는다.

## 실제로 검증한 흐름

새 실제 검사는 native 참조 드래그·Escape, 잘못된 scope 자료 거부, 다른 문서로 참조 이동과 돌아오기, 같은 schema/table 재열기 시 DOM/Undo, 열 반복/경계/너비, 잘못된 참조 타입의 Apply 거부와 유효한 참조 Apply, 두 번의 실제 호스트 재시작을 포함한다. 세 브라우저 그룹의 입력뿐 아니라 복원 직후 모듈의 실제 목록도 검사한다. source 파일이 그대로인 상태에서 private pending 값과 공유 초안 변경을 구분한다.

집중 검사는 최종 제품에서 **1/0/0, 40.948초**로 통과했다. 초기 레이아웃에 겹친 창은 native 제목 드래그로 분리해 실제 포인터 검사를 했다. 앞선 집중 통과/실패·테스트 배치 보정 이력을 최종 고유 검사 수에 더하지 않는다.

최종 고정 원본·실행 메서드·결과·일반 checkout HEAD는 [검증 JSON](validation/v480-reference-navigation.json)에 기록한다. [실제 문서/참조 입력](validation/v480-reference-navigation.png)은 공통 Chromium UI의 캡처다. 엔진·공개 편집 API·compiler 원본이나 실행 의미를 바꾸지 않는다.

## 남은 범위를 구분한다

| 영역 | 현재 범위 / 미지원 |
|---|---|
| 브라우저 그룹 | 기존 object/function/module의 그룹별 적용 검색·입력·콜드 목록 복원. CELEM category/concept와 prototype Category/상속 트리의 전체 의미를 동일하게 매핑하거나 계층 이동을 추가하지 않는다. |
| 브라우저 Data의 필드 열 | 브라우저 자체는 이름·종류·초안 상태 열이다. 실제 필드 비교/열 조작은 기존 즉석 테이블의 소유 객체·명시적 필드 선택 범위다. 모든 종류의 browser Data에 prototype 필드를 자동 생성했다고 주장하지 않는다. |
| 문서 링크 | 기존 소유 source 선택과 읽기 전용 등록 정의 조회로 문서를 이동한다. Workspace 시각 링크 그래프와 연결된 창들의 묶음 이동/삭제 의미는 runtime 계약이 없으므로 추가하지 않는다. |
| Undo | 같은 부모/문서의 retained 입력은 native Undo를 검사한다. 다른 부모로 옮긴 TD/문서의 이동 **이전** native Undo 이력까지 보장하지 않는다. 기존 Chromium reparent 제한과 private pending 값 복원은 별개다. |
| 데이터/실행 | 구조적 field 쓰기/ref/lvalue·compound/function live property·일반 사용자 enum/Vector3 ABI를 추가하지 않는다. 참조 텍스트 준비는 해당 실행 계약의 구현이 아니다. |
| 별도 미결 | Home 포함 팩 수·마지막 편집 시각과 계산식 overflow 정책은 이 변경과 분리해 유지한다. |
| 환경 | 실계정·유료 호출·native OS/실기기·사용자 PC 설치는 검증하지 않는다. main·원본 ZIP·Android 설정은 보존한다. |

최종 고정 제품/테스트 원본은 **11개**다. 같은 원본에서 실제 Chromium 영향 회귀 **9/0/0, 298.684초**, Windows/Android 관리 프로필 컴파일 **1/0/0, 124.200초**가 통과했다. 실제 필드·정확 숫자·독립 선언 뷰/CAS·외부 정의 읽기 전용·개념 맵·문서 pending/Save/compiler Confirm·그룹 콜드·참조/열 조작을 포함한다. 초기 실패·집중 통과·앞선 원본 단계의 결과를 최종 수와 합산하지 않는다. 일반 Git checkout·보존 CRLF/새 LF·38개 리소스·실제 Home 시작·변조 거부는 구현 커밋 HEAD에서 별도 검사하고 검증 JSON에 정확한 HEAD를 기록한다.
