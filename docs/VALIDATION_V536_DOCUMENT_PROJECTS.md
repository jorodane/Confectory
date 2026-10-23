# v536 실제 프로젝트 전환·독립 요소 View 연결

이 기록은 문서 창 첫 묶음 이후의 결과다. 전체 UI/독립 View 완성이나 게시 완료를 뜻하지 않는다. main/Android/원본 ZIP/사용자 자료와 기존 계정·권한·CAS/명시적 확정 계약은 유지한다.

## 실제 프로젝트 전환

같은 `Owned.Elements` namespace, 같은 Unit ID·View1·프로젝트 파일 이름을 두 개의 서로 다른 격리 경로에 두었다. B의 Unit HP/설명을 구별해 A 텍스트가 B에 들어가는지 검사한다. 두 경로는 모두 `/tmp/confectory-document-projects-*` 아래이며 실제 사용자 저장소는 사용하지 않았다. B는 명시한 fixture 시작 프로젝트로 등록한 후 실제 Home 목록에서 A↔B를 전환했다.

`document-projects-1.log`의 첫 오래된 버튼 검사는 retired DOM의 비활성 `.click()`만 호출하여 충분하지 않았다. `document-projects-2.log`에서는 실제 `onclick` 핸들러를 직접 실행해 **A의 오래된 Apply가 B의 같은 번호 View에 A 텍스트를 stage하는 결함**을 재현했다. 최종 소스 파일이 아닌 격리된 B의 작업 초안에만 반영됐으며, 이 재현 상태를 삭제하거나 사용자 Windows 원인으로 설명하지 않는다.

소스 View 핸들러는 이제 프로젝트 ID·현재 창 객체·연결된 DOM·객체 ID·서버 View/모드가 일치해야 한다. 요청 직전과 응답 후 재확인하며, 다른 창이 같은 슬롯을 차지한 경우에도 거부한다. reset/release/save도 이 소유자를 따른다. 늦은 Apply 응답이 새 입력을 무조건 지우지 않도록 캡처한 입력만 제거하고, 실제 자기 Apply 응답 텍스트/버전과 일치할 때만 남은 입력의 기준을 갱신한다. 서버의 프로젝트/View 소유권과 source CAS를 약화하지 않았다.

수정 후 실제 엔진 **4건 PASS**, `document-projects-3.log`, `/tmp/confectory-document-projects-2eay_td_/evidence.json`: 별도 프로젝트 ID, 실제 live A→B 및 반복 전환, 직접 호출한 오래된 A 핸들러가 write 요청을 내보내지 않음, 실제 프로세스 cold 후 두 입력 복원. 양쪽 원본 파일 바이트가 유지됐다. 실제 계정/토큰/유료 추론·Windows 네이티브 QA는 아니다.

## 원본 요소 화면의 독립 View 어댑터

원본의 `새 창으로 열기` 메뉴를 기존 object context에 연결하고, `element-instances.js`에서 기존 원본 기반 `createElementEditors`를 재사용한다. 새 generic/source 폼을 만들지 않는다. 프로젝트/객체/슬롯별 창과 입력 맵을 분리하고, 기존 generic properties 입력 형식도 해당 슬롯에서만 옮긴다. 모르는 이전 입력은 삭제하지 않고 기존 unresolved 보호를 유지한다.

요청은 정상 3-slot `openEditorView`/properties 계약을 사용하며, 필드·설명·정의·객체 구조·저장을 bound View로 보낸다. 알 수 없는 RPC는 primary로 조용히 보내지 않는다. 소유 선언만 새 창으로 열고, 계정/다른 프로젝트/최종 반영/실행 권한을 추가하지 않는다. 동일 객체의 보이는 창은 새 슬롯으로 열고, 숨긴 창의 정의 재진입은 기존 입력 DOM을 다시 연다. 문서/모바일의 기본 열기 및 명시적 플로팅 배경을 기존 문서 어댑터에 연결했다. 복사 구현 등의 아직 bound하지 못한 작업은 기존 실패 안내로 막는다.

현재 actual `element-instances-4.log`, `/tmp/confectory-element-instances-nzcsw715`에서 다음 **6건이 실제 통과**했다.

1. 원본 새 창 메뉴로 같은 Unit의 원본 기반 요소 렌더러 두 개 생성, 독립 HP/한글 설명 입력, generic/source fallback 없음.
2. 창 닫기→일반 정의 열기로 동일 View/DOM/입력 재진입, 추가 슬롯 중복 생성 없음.
3. 3개 슬롯의 입력 분리·3개 제한의 명시적 실패·원본 바이트 보존.
4. 실제 프로세스 재시작 후 세 원본 기반 창과 입력/proof 복원.
5. 첫 창의 명시적 작업 사본 Save가 bound View에서 수행되고 다른 두 입력 및 최종 소스가 유지됨.
6. 둘째 창의 오래된 revision/hash Save 거부, 입력 보존 및 공유 초안 불변.

일곱 번째 취소는 처음 실패했다. 복사 구현용 기본 snapshot 분리는 필요했지만 그 수정만으로 해결되지 않았다(`element-instance-cancel-recheck.log` 실패). 원래 실패 profile/작업 사본을 초기화하지 않고 다시 실행한 `element-instance-cancel-diagnostic.log`에서 실제 안내는 “변경 상태를 확인하지 못했어요. 입력은 유지됩니다.”였다. 동시에 세 창의 상태를 조회하며 일부 `browserDrafts/status`가 transport `stale_revision`으로 거부된 뒤, 취소가 유효한 상태 정보를 갖지 못한 것이 직접 확인된 차단 지점이다. 첫 창의 `saveEditorView`는 서버가 `accepted:true`로 완료한 응답도 확인했다.

취소는 이제 기존 작업 직렬화 안에서 서버 상태를 새로 읽고, 같은 소유 대상과 revision/hash를 다시 검사한다. 쓰기 충돌을 무시하거나 새 버전으로 강제 덮어쓰지 않는다. 최종 `element-instance-cancel-recheck-2.log`(session43167, exit0), 같은 `/tmp/confectory-element-instances-nzcsw715/cancel-recheck-evidence.json`에서 **집중 검사3건 PASS**: 실제 cold의111/222/333 복원, 둘째 창 취소 후 저장값111·셋째 창333 보존, View3개/원본 파일 불변. 이는 앞선6건에 이어 실패 지점을 같은 상태에서 검증한 결과이며 전체7건을 처음부터 다시 실행했다고 표시하지 않는다. 성공 후 fixture는111/111/333이므로 이전 replay의 초기222 조건은 더 이상 그대로 반복할 수 없다.

실제 `cancel-rechecked.png`를 열어 세 원본 요소 창과111/111/333을 확인했다. 셋째 창에는 실패한 배경 조회의 `stale_revision` 안내가 여전히 남아 있어, 백그라운드 조회 직렬화/복구 표시를 다음 집중 회귀에서 정리할 필요가 있다. 앞 세 실행의 spinbutton locator/겹친 창으로 인한 pointer 차단은 fixture 오류다. 타입 검사를 낮추거나 강제 클릭하지 않고 실제 제목 드래그로 창을 배치하도록 테스트를 고쳤다.

최종 Linux 생성 build `document-instances-build-4.log`(session37233, exit0),61개 리소스/정규 텍스트52개 해시·크기, 변경 JS4개/Python3개 구문 및 `git diff --check`를 통과했다. 환경이 한 차례 끊겨 명령이 실제 거부된 뒤 ready 확인과 실제 명령/빌드/엔진 실행으로 복구를 확인했다. 새 Windows 빌드/패키지/게시 또는 실제 Windows QA는 아직 진행하지 않았다.

## 첫 체크포인트 당시의 미완료 경계 (아래 후속 결과가 현재 상태)

- 닫은 clean View의 슬롯 회수/다른 객체 재사용과, 3개 모두 pending일 때의 보존. 무제한 독립 창 지원을 약속하지 않는다.
- 객체 이외의 기능·모듈 추가 인스턴스, 독립 View에서의 구현 복사 및 모든 참조/계약 편집은 아직 연결/검증되지 않았다. 원래 요소 창의 기존 경로와 원본 배치는 유지한다.
- 문서 위 기본 열기·Pack Manager 배경의 새 properties 창, 이전 generic properties 입력 cold 이전, 실제 Review/Confirm은 현재 새 어댑터의 추가 회귀가 필요하다.
- 늦은 source Apply 응답과 새 입력/Save/release의 조합, 서로 다른 창이 unsaved 공유 초안을 stage한 경우의 취소 범위를 집중 검증해야 한다. 다른 창의 stage를 지우거나 보호를 완화해 통과시키지 않는다.

이 목록은 첫 체크포인트 당시 상태다. 아래 후속 검증에서 닫힌 clean 슬롯 재사용·문서 재진입·확정·이전 입력 복원과 독립 입력 취소 경계를 확인했다. 독립 기능/모듈·복사 및 늦은 source 조합의 전체 수용 검사는 계속 미완료로 보존한다. 전체 UI·Windows 패키지/checkout/정상 work/current 게시도 남아 있다.

## 창 묶음 고정 잔여 검증 (2026-10-22)

이번 묶음은 배경 상태조회, 닫힌 clean 슬롯 재사용, 문서 재진입·명시적 확정의 세 경계에 한정한다. 무제한 창이나 모든 요소 편집 기능의 완료가 아니다.

- 상태조회는 모든 원본 요소 렌더러가 공유하는 직렬 읽기 큐와 기존 작업 수명을 사용한다. 한 조회가 끝나기 전에 다음 창의 조회를 겹쳐 보내지 않는다. 배경 조회의 실패는 해당 창에 정확한 한국어 안내로 남기고, 같은 원본 UI의 명시적 재진입에서 재조회한다. 유효한 소유 대상·버전의 응답을 받은 뒤에만 그 조회 오류를 지우며, 입력/저장 오류를 무조건 지우지 않는다. 원본 내용이 바뀌는 쓰기 CAS는 그대로 거부한다.
- 독립 요소 창의 취소는 자기 창의 입력만 취소한다. 다른 창이 공유 작업 사본에 적용한 미저장 내용을 `browserDrafts/discard`로 되돌리지 않는다. 기존 기본 요소 창의 공유 초안 취소 계약은 유지한다.
- 기존 3개 View가 찬 경우, **현재 프로젝트의 properties View 중 닫혔고, 문서 탭에 남아 있지 않으며, 창별 미적용 입력과 변경된 공유 초안이 없는 슬롯**만 정상 서버 `closeEditorView` 후 재사용한다. 다른 창의 입력을 삭제하거나 변경된 작업 사본을 버려 슬롯을 만들지 않는다. 같은 슬롯의 폐기된 핸들러는 후속 창을 조작하지 못한다.
- 창 연결/해제는 transport `stale_revision`으로 미실행된 요청만 동일한 대상·입력으로 제한 재시도한다. 시도마다 프로젝트와 현재 입력/소유를 다시 확인한다. 실제 쓰기 충돌이나 알 수 없는 실패를 새 버전으로 덮어쓰지 않는다.
- 독립 요소도 기본 요소처럼 관계 투영 변경을 반영한다. 새 관계를 읽은 뒤에도 `schema` JSON만 비교해 옛 하위 목록/표시를 남기는 경로를 수정했다. 원본 렌더러/HTML/CSS를 재사용하며 레이아웃을 새로 설계하지 않았다.

### 실제 실행 근거

`tests/web/v536_element_reentry_engine.py`의 최종 `element-reentry-engine-4.log`는 `/tmp/confectory-element-reentry-j7k6g3k9`에서 **6건 PASS 후**, 모바일 Browser 위에 남아 있는 플로팅 창이 클릭을 가리는 지점에서 중단됐다. 그 앞에서 실제 clean Unit 슬롯→Slime 재사용·다른 두 Monster 입력 보존, 폐기 핸들러 거부/모두 pending일 때 제한, 타 창의 unsaved stage 보존 취소, Review 취소→별도 선택/컴파일 Confirm→같은 창 재편집, Doc 재진입/동일 입력 DOM·Pack 플로팅, 실제 cold 복원·이전 properties 입력의 해당 슬롯 이전을 검증했다. 최종 소스는 명시적 Confirm 때 Monster의 HP224만 바뀌며, 뒤의 Save225는 작업 사본에만 남는다. 원본 Unit·Slime·다른 소스는 보존됐다.

첫 실행의 `openEditorView` transport 경합과 둘째 실행의 폐기된 핸들러 `TypeError`는 제품 결함으로 수정했다. 셋째 실행의 문서 DOM 검사는 Save 접수 직후 화면 갱신이 끝나기 전에 기준 DOM을 잡는 문제도 있었다. 원본과 같은 관계 갱신 경로를 연결하고 실제 UI 준비·presentation flush 후 기준을 잡도록 고쳤다. DOM 동일성 assertion은 삭제하지 않았다. 앞선 실패 로그를 보존한다.

모바일 가림은 강제 클릭이나 CSS 변경으로 통과시키지 않았다. 실제 플로팅 창의 **기존 닫기 버튼**으로 입력을 보존한 뒤 아래 목록을 열도록 fixture를 보완했다. 이미 통과한6건을 반복하지 않고 같은 실패 profile/소스를 초기화 없이 이어 쓴 `tests/web/v536_element_mobile_reentry.py`의 `element-mobile-reentry-1.log`(session93262, exit0)는 **집중3건 PASS**했다. 실제390×844 목록→Slime 정의 재진입의 소유 View·HP111 보존, 원래 새 창 메뉴로 숨긴 Monster View 재사용, 이전 입력의 취소225 복원과 세 오류란 모두 빈 상태를 확인했다. 이는 처음부터 전체8건 PASS라는 뜻이 아니다.

최종 상태조회 실패 검사는 `tests/web/v536_element_status_retry.py`/`element-status-retry-1.log`(session74346, exit0), 같은 profile의 `status-retry-evidence.json` **3건 PASS**다. Slime 배경 조회3회에 실제 transport의 오래된 revision을 넣어 서버가 실행 전 거부하게 했다. 한국어 실패가 남고 raw protocol을 성공처럼 표시하지 않음, 원래 문서 재진입의 새 정상 조회 이후에만 안내 제거, Slime111/Monster225 두 창 및 원본 파일 보존을 확인했다. 외부 계정이나 사용자 저장소의 장애 주입이 아니다.

기본 요소 경로의 `v508_elements_engine.py`/`document-remainder-primary-regression.log`(session24847, exit0)는 별도 **4건 PASS**: 실제 상속/하위 목록, Save, 로컬 취소와 기존 공유 초안 취소, 선택한 변경의 실제 compiler Confirm. 이 검사는 build3 시점의 공통 변경을 확인했으며 그 후 수정은 독립 렌더 갱신 및 상태 실패/재진입 처리다. 각 검사 시점과 근거를 섞어 하나의 전체 suite 통과로 표시하지 않는다.

최종 생성 Linux build6 `document-remainder-build-6.log`(session10480, exit0), 리소스61/정규 텍스트52 해시·크기, 변경 JS3개·Python3개 구문 및 diff 검사를 통과했다. 첫 모바일 캡처에는 build4 배경 조회가 낸 일시적인 raw toast가 있었다. 최종 build6은 배경 실패를 기존 작업 wrapper 밖으로 전달해 해당 창에만 표시하며, 후속 모바일 재검증 결과는 아래에 기록한다. 실제 Windows/Android 창·터치 하드웨어·가상키보드 QA, 새 Windows package/checkout/게시, 실제 계정/모델 호출은 수행하지 않았다.

### 남은 UI 범위

이 묶음 이후의 다음 구현은 **v536 모바일 Blueprint 카드/전체 화면 노드 편집**이다. 3-slot 계약, properties 이외의 독립 인스턴스/구현 복사 등 미연결 경계는 계속 명시한다. 기능·모듈/복사·ABI의 고정 지원 제한, 남은 요소 Browser·이미지/삭제·전투 로그/신문고/창별 Run, 최종 전체 회귀·Windows 패키징·checkout·게시가 여전히 남아 있다. 새 저장 내구성 범위는 추가하지 않았다. 늦은 source Apply 조합 등 기존 통합 회귀 잔여는 최종 수용 목록에 보존하며, 이 세 창 경계의 완료를 전체 UI 완료로 확대하지 않는다.

### 최종 모바일 재검증과 남은 토스트 수정

최신 build6의 모바일 재검사에서 창 내부 오류란은 비었지만, transient `stale_revision` toast가 남는 것을 실제 캡처에서 확인했다. `mobile-reentry-failure-before-filter-fix.json`의 실제 요청/결과를 대응시키자 모바일 `objects`(`kind:object, query:Slime`)가 실행 전 transport revision 거부된 뒤 재조회 없이 작업 실패 toast로 가는 것이 확인됐다. 다른 `openEditorView` 거부는 기존 제한 재시도로 회복됐음을 구분했다.

`objects`의 backend `filter`는 현재 소유 workspace의 비공개 query/kind/page만 바꾸며 원본/초안 쓰기·Review/Confirm/실행이 아니다(`packs/pack-workspace/Command.csbody`). 네 종류의 Browser 조회 진입점을 같은 프로젝트·WebView generation·현재 창 객체·미적용 소스 보호를 확인하는 제한 재조회에 연결했다. `stale_revision` 미실행만 같은 요청으로 재시도하며 source 쓰기/CAS 실패는 이 허용 목록에 없다. 문구만 바꾸거나 toast를 숨기는 수정이 아니다.

최종 build7 `document-remainder-build-7.log`(session68011, exit0) 이후 `element-mobile-reentry-5.log`(session1963, exit0), 같은 preserved profile의 `mobile-reentry-evidence.json` **3건 PASS**.390×844 실제 UI의 pending Slime111 재진입, 숨은 Monster View 재사용/새 로컬 입력227 취소→저장225, 세 창 오류란 전부 빈 문자열과 활성 raw toast 없음, 소스 파일/기존3개 소유 바인딩 보존을 검증했다. 첫 build4 집중 검사의 이전226→225 취소와 이번225에서 새227 입력 취소는 구분한다. 앞선 build6 mobile run2는 활성 문서의 숨겨진 헤더 닫기 버튼을 눌렀던 fixture 오류다. 원본 문서 탭의 X를 사용하도록 수정했으며 product CSS/레이아웃이나 assertion을 완화하지 않았다.

최종 mobile PNG(`mobile-reentry-rechecked.png`)와 조회 실패/정상 복구 PNG를 실제로 열어 확인한다. 최신 source/resource 구문·해시/diff 결과는 checkpoint와 bundle evidence에 기록한다. 이번 창 묶음의 고정 세 잔여는 이 지원 범위에서 검증을 마쳤으며 **다음 구현은 모바일 Blueprint**다. 전체 UI·실제 Windows/Android·패키지/게시 완료가 아니다.
