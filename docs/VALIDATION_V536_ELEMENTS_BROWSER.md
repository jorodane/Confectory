# v536 요소 Browser 연결 — 첫 묶음

기준은 `origin/main` 196c605의 보존된 v536 ZIP이다. 전체 UI 복원·Windows 실행·패키징·게시는 아직 완료하지 않았다. 실제 사용자 계정이나 프로젝트는 사용하지 않았다.

## 원본 확인과 이번 변경

원본 `app.js`의 `renderObjectVariations`, `renderBrowser`, `visibleObjects`, `renderBrowserItems`, `setupBrowserActions`를 실제 Chromium에서 열어 확인했다. 원본 기본 데모는 시작 마이그레이션(58행)에서 Unit/Monster를 Category로 바꾸고 Slime의 `inherits`를 제거한다. 따라서 그 기본 화면의 폴더 포함 관계를 엔진의 객체 상속으로 단정하지 않았다. 별도 임시 원본 화면에 실제 엔진 fixture와 같은 Unit→Monster→Slime 상속, Unit.HP=100, Monster.Speed=2를 넣어 구조와 Compact/Preview 배치를 대조했다. 원본 실행은 UI 기준이며 실제 엔진 검증으로 계산하지 않는다.

- 기존 속성·기능·모듈 편집과 저장/취소/명시적 확정 계약을 재사용한다.
- 하위 Browser에 Compact/Preview 표시, 자손 이름 검색, 검색 전 입력과 제출한 검색어의 분리, 이름 정렬, 현재 요소 아래로 제한된 경로/계층 이동을 연결했다. 기본 순서는 엔진 관계 projection의 기존 ID 순서를 유지한다. 생성 시각이 없는 데이터를 최근 생성순처럼 만들지 않았다.
- 하위 요소 Enter/더블클릭은 기존 소유 요소의 독립 View를 연다. 부모 창을 다른 요소로 재사용하지 않으며 닫은 View의 입력과 대상이 유지된다. 기존 세 View 상한은 유지한다.
- 창/프로젝트/요소가 바뀌거나 이전 section이 폐기되면 그 DOM의 콜백은 동작하지 않는다. 목록 표시가 서버 소유권 검사를 대신하지 않는다. 실제 쓰기는 기존 View binding 및 revision/hash/CAS 검사를 통과해야 한다.
- 검색 상태는 디스크에 있었으나 복원 시 렌더러가 metadata보다 먼저 실행되어 검색창이 비워지는 결함을 실제 재시작으로 재현했다. 이미 서버가 확인한 같은 요소 schema인 경우에만 원본 화면 metadata를 먼저 읽는다. metadata가 source 또는 View 소유자를 선택하지 않는다.

이번 묶음은 하위 Browser 탐색과 입력 보존이다. Data 보기, 원본 inline 생성/이름 변경·삭제/다중 선택·드래그/참조 hover·Category 포함 관계는 완료로 표시하지 않는다. 지원하지 않는 Data/생성은 기존 미지원 안내를 유지하며 성공으로 처리하지 않는다. 기존 `tables.js`의 개발용 비교 구성 폼을 원본 Data 화면으로 대신 넣지 않았다.

## 실행 결과

- 실제 생성 엔진 `v536_elements_browser_engine.py`: 6건 통과. 직접 자식/자손 검색, Compact/Preview 이동과 키보드 뒤로가기, Enter/더블클릭·닫기/재열기, 부모/자식 한글·값 입력 분리, 실제 프로세스 재시작 및 미제출 검색어 복원, 자식 로컬 취소와 체크된 View Save. 최종 source bytes는 변하지 않았다. 증거 `/tmp/confectory-element-browser-iw37fog1`.
- 통제 renderer `v508_elements_shell.py`: 9건 통과. 실제 엔진이 아닌 versioned fixture의 CAS·늦은 취소·legacy 입력·대상 수명·속성 추가를 검사했다. 이전 fixture의 불완전한 projection row에 실제 group/kind/parent를 추가했다. 직렬 상태 조회에서 A 응답을 풀기 전에 B 요청이 시작된다고 기다리던 검사를 고쳐, A 완료 후에도 B의 pending/null proof가 보존되고 B 응답만 수용되는지 확인했다. 검사 조건을 제거하거나 source 보호를 완화하지 않았다. 증거 `/tmp/confectory-elements-shell-kwr2k471`.
- `browser_projection.mjs`: 관계/정체성·순환/깊이/프로젝트 격리 2묶음 통과. 최초 실행은 필수 repo 인자를 누락해 ENOENT였고 올바른 인자로 재실행했다.
- Linux 실제 엔진 build 4회 exit 0, embedded resources 62개/정규화 text 53개 해시·크기 일치, 수정 JS 구문·Python 구문·`git diff --check` 통과.
- 첫 실제 UI 실행은 hidden 경로 생략 문자까지 textContent로 비교한 fixture assertion에서 중단했다. 실제 title/표시 경로를 검사하도록 수정했다. 두 번째 실행에서 검색 metadata 복원 결함을 재현/수정했다. 세 번째 실행은 cold background 준비 중 열기 검사여서, 화면의 실제 enabled 상태를 기다린 네 번째 실행이 6건을 완주했다. 이 초기 실패 로그도 보존한다.

최종 Confirm 집중 검사에서는 다음 두 실제 결함을 구분했다.

1. 독립 View에서 Review 전에 primary cursor를 선택하는 읽기 요청이 background 상태 조회와 경합해 `stale_revision`으로 거절됐다. 동일 View/프로젝트와 source 입력을 매번 재검사하며 select 읽기만 최대 3회 다시 admission한다. 격리 서버에 stale admission을 한 번 주입한 검사에서 재선택→선택한 Slime만 Review→명시적 compiler Confirm이 실제 통과했다. 서명/쓰기 CAS나 검토 token을 새 버전으로 덮지 않는다.
2. 그 뒤 부모 Unit 창의 입력은 남았지만 shared cursor가 Slime여서 Unit Save가 거절됐다. 클릭한 원래 창과 프로젝트/대상을 확인하고 다른 source의 미적용 입력이 없을 때만 정확한 원래 요소를 다시 select한다. pending 입력의 기존 revision/hash는 그대로 유지한다. 그 다음 기존 flush/CAS가 성공해야만 저장한다.

`v536_elements_browser_parent_cursor.py` 실제 엔진 3건 전체 통과: 이미 확정한 Slime을 224로 다시 staged Save → Slime만 명시적 compiler Confirm → Unit의 보존한 111/한글 설명을 원래 proof로 staged Save. 최종 파일은 Slime만 변경됐고 Unit 및 다른 source는 그대로였다. 증거는 같은 소비 fixture의 `parent-cursor-evidence.json`, `parent-saved-after-child-confirm.png`다.

`v536_elements_browser_lifetime.py` 통제 renderer 3건은 프로젝트 변경·창 binding 제거·옛 DOM 분리 각각에서 이전 열기/검색 callback이 실행되지 않음을 확인했다. 실제 A/B 프로젝트 통합 검사로 과장하지 않는다. 증거 `/tmp/confectory-elements-shell-apup7hy7`.

초기 Confirm 검사에서 현재의 `data-review-unit`/`data-review-group` 대신 예전 checkbox 식별자를 기대한 fixture assertion도 수정했다. 이어 root를 명시적으로 다시 열었는데 이전 자손 검색이 그대로일 것이라고 가정한 fixture는 실제 검색 동작을 거치도록 수정했다. 네 번째 집중 실행은 child Confirm 1건 통과 후 위 부모 Save 결함에서 실패했으므로 그 전체 스크립트를 통과로 세지 않는다. 수정 후의 전체 실제 후속 3건 통과가 별도 근거다. 원래 6건 전체를 불필요하게 재실행하지 않았다. 최종 코드/정확한 서버 응답 완료를 기다리도록 고친 첫 Confirm 스크립트의 fresh fixture 전체 재실행은 이번에 하지 않았다.

## 화면과 한계

- 원본 기본 화면: `/workspace/scratch/v536-reference/elements-browser-reference/`.
- 원본 동일 상속 fixture: `/workspace/scratch/v536-reference/elements-browser-same-state/`의 Compact/Preview PNG와 `reference.json`.
- 실제 엔진: 위 실제 fixture의 `unit-child-browser.png`, `parent-input-and-query.png`, `child-saved-parent-preserved.png`, `parent-saved-after-child-confirm.png`를 직접 열어 확인했다. 창 위치/데이터/viewport가 다른 전체 화면의 픽셀 일치를 주장하지 않는다. 같은 원본 CSS와 요소 내부 구조를 재사용하며 전체 정밀 화면 수용은 남아 있다.
- 실제 Windows 네이티브 실행/Android/터치 하드웨어, 새 Windows 패키지와 전체 checkout/게시 검사는 이번에 하지 않았다. 브라우저 폭 검사와 Linux 엔진 결과가 이를 증명하지 않는다.

v536 전체 기준으로 Helper 기본 폼·프로젝트 생성/배치·공통 shell/문서 창의 앞서 검증한 묶음은 유지한다. 모바일 Blueprint와 요소 Browser/다중 구현/나머지 ABI는 부분 완료다. 이미지·폼 삭제·전투 로그/신문고·창별 실행은 미연결 또는 실제 backend 계약 감사가 남아 있다. 모바일의 공유/고정 반환 이름·잠정 빈 출력·영역/다중 선택·내부 흐름/async·특수 핀 제한은 `NEXT_MOBILE_BLUEPRINT_5.txt` 그대로 미완료다. 전체 UI 수용 후에만 Helper 편집 기능 확장과 최종 회귀·Windows 패키징·정상 게시로 진행한다.
