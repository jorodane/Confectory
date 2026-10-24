# v536 raw 원문·요소 속성·새 복사 초안의 결합 Save

`37e65fe` 이후 현재 원본 화면에서 함께 편집할 수 있는 직접 소유 object의 raw 입력 하나, 기본 요소 창의 typed 입력, 같은 owner의 새 private copy1~8개를 기존 저장 배치에 연결한 단위다. 새로운 레이아웃·메뉴·실행 의미를 추가하지 않았다. 모든 UI/backend 문맥의 복원이 완료된 것은 아니다.

## 지원과 경계

- 기존 요소 임시 저장과 독립 source 창의 Save를 사용한다. raw를 먼저 쓰거나 copy를 먼저 선택할 수 있다. copy 선택창의 읽기 단계에서 같은 owner의 한 원문 입력만 정확히 제외하고, 다른 raw/속성 창·다른 계획은 자동 선택하지 않는다. 저장된 구현의 편집 권한이나 등록/상속 원본 쓰기로 확대하지 않는다.
- native SlotBatch는 원래 raw/typed 후보를 먼저 준비하고 모든 명시 새 copy의 immutable seed·현재 source/target·import/wrapper/record를 같은 후보에 결부한다. 마지막으로 원래 baseline/최종 owner/raw의 3-way 병합을 다시 검사한다. raw의 provider 참조와 copy 선택이 다르면 전체 거절하며 어느 참조도 조용히 덮지 않는다. copy owner와 registration formatter도 원래 주석·공백을 보존한다.
- 원래 source identity/hash, 현재 프로젝트/창 binding, 전체 Context/checkpoint CAS, schema/reference와 전체 typed graph 검사를 유지한다. `Save.ApplySlots`는 raw 후보의 원래 물리 source 경로·symlink·baseline hash를 staging 전과 checkpoint 쓰기 직전에 검사한다. 원래 파일을 Save 과정에서 다시 쓰지 않는다. checkpoint/activity는 기존 CAS와 persist-before-live를 사용하며, 최종 소스는 명시 Review/Confirm에서만 반영한다.
- copy journal에 raw/typed 캡처와 전체 copy 목록을 보관한다. receipt는 부분 목록이나 다른 declaration을 전체 성공으로 인정하지 않는다. 불확실한 Apply 결과는 query/cold recovery로 먼저 확인하고, 캡처와 같은 입력만 정리한다. 새로운 raw/typed/copy 입력은 보존한다. 원문을 새 기준으로 자동 재해석하지 않는다.
- 이전 raw-only 저장이 거절된 뒤 copy를 추가한 경우에는 원래 시도가 미적용이고 원래 source 기준이 같음을 확인한 후 새 명시 후보의 `priorOwner`에 결부한다. 성공한 전체 receipt를 확인할 때만 그 이전 journal을 정리한다. 이미 적용됐거나 결과가 불확실하면 먼저 복구하며, 실패 기록을 무조건 지우거나 새 hash로 덮어쓰지 않는다.
- source/properties/copy 입력의 취소 범위를 구별한다. 요소 창 Cancel은 그 typed/copy 입력을 정리하며 다른 source 창의 글은 그 창의 Reset 전까지 유지한다. 다른 owner 창의 입력과 초안은 자동 취소하지 않는다. 새 source·새 copy를 선택했다고 Agent 동의/프로젝트 권한이 늘어나지 않으며 source View 자체의 properties/slot API 역할 제한도 유지한다.

이번에 지원한 것은 **새 copy + 현재 root 요소 widget + 원문 하나**다. raw+saved-copy ABI/기존 본문 편집, multi-target ABI/Set/property/다른 Blueprint 계획의 원자 결합, 여러 raw 또는 독립 properties 창과 copy의 결합은 미지원이다. 알려지지 않은 같은 owner 계획은 입력을 유지하며 차단한다. 별도 Save를 순서 호출해 이 범위를 지원한 것처럼 보이지 않는다. 해당 경로는 고정된 ABI/혼합 후보 계약의 잔여이며 이미지·협의·렌더 같은 새 backend 요구와 다르다.

## 실제 검사

모두 격리 fixture다. 실제 사용자 프로젝트/자료·계정·인증파일·로그인·유료 추론·프로젝트 실행을 사용하지 않았다. PASS 수에는 공통 준비가 포함되므로 서로 합산한 독립 건수가 아니다. 로그·화면은 `/workspace/scratch/v536-raw-copies/`와 각 로그의 evidence 폴더에 있다.

| 검사 | 실제 결과 |
| --- | --- |
| 순수 source/copy/ABI | raw-owner metadata5, private copy4, general-private ABI4 PASS. 원문/정확한 숫자/immutable seed·출처·현재 ABI/변조·stale·외부 소유 보호 |
| 실제 native 후보 | `api3.log` 3 PASS. 마지막 copy/원문 provider·값 겹침/위조 위치/실제 source 변경의 전체 미적용, 두 copy+typed 구조/복합/배열/ref·새 schema/registration 한 후보, 전체 receipt와 cold 복원 |
| 정상 실제 UI | `ui-normal1.log` 4 PASS. 실제 typed 구조/값과 두 copy body/wrapper 및 raw 주석·한글·emoji→cold→Save/cold→Review 취소/compiler Confirm/cold. 후속 수정 영향은 아래 집중 회귀로 확인 |
| 취소·실제 충돌 | `ui-cancel1.log` 3 / `ui-conflict3.log` 3 PASS. 취소는 source 창 입력 보존 후 자체 Reset, 실제 source 변경은 모든 copy/owner/등록 미적용·cold 입력 보관 |
| 저장 장치 오류 | `ui-storage4.log` 5 PASS. 실제 checkpoint 쓰기 실패의 전체 미적용·원문/선택 보존→cold 명시 재시도→compiler Confirm/cold |
| 응답/조회 유실 | `ui-loss4.log` 5 PASS. 원래 전체 receipt query/cold 복구, 두 copy 중복 생성/추가 Apply 없음→명시 Confirm/cold |
| Undo·이전 거절 전환 | `ui-undo4.log` / `ui-prior4.log` 각5 PASS. raw provider 충돌→실제 textarea Undo→명시 재시도, raw-only 설명 충돌 거절→Undo→새 copy 선택→cold→한 후보/원래 journal 결부/Confirm |
| 마지막 copy 부적합 | `ui-last-copy4.log` 5 PASS. 첫 copy/선언/새 schema가 남지 않는 전체 미적용→cold 보존→명시 재시도/Confirm |
| 늦은 새 입력 | `ui-late4.log` 3 PASS. receipt 수신 전 새로 입력한 raw/정확한 MP 값은 삭제하거나 적용하지 않고 cold까지 유지, 기존 두 copy 중복 없음 |
| source 창 Save | `ui-source-save4.log` 4 PASS. 기존 source Save 버튼으로 같은 root/typed/copy 후보와 Review/Confirm/cold 완주 |
| 다른 창 보존·최종 상태 | 최종 `ui-peer5.log` 5 PASS. 다른 owner의 독립 View 입력은 Save/cold 후 유지되고 자기 Cancel만 그 입력을 정리한다. 기본 owner Review 취소/compiler Confirm/cold까지 완주 |
| 기존 경로 회귀 | `raw-only-regression.log` 4 PASS. 기존 독립 raw/properties owner-only Save·취소 Review/Confirm/cold. `mixed-regression.log` 4 PASS. 기존 raw 없는 두 copy/typed 후보·마지막 오류 전체 미적용·receipt/cold/compiler Confirm |

첫 native API는 기존 fixture의 6초 결과 poll을 넘겨 중단됐다. fixture는 실제 비동기 결과가 도착하는지 최대60초 동안 확인하고 host 종료·endpoint/action을 실패 시 기록하도록 고쳤다. 성공/거절 assertion을 제거하지 않았다. `api2/3`에서 실제 결과를 확인했다.

실제 source 파일을 바꾼 `ui-conflict1`에서 checkpoint 접수가 가능했던 결함을 재현했다. 원래 raw-only 경로의 physical source 검사를 copy 경로가 거치지 않은 것이 원인이었다. staging 전/저장 직전 hash 검사를 추가했고 `api3/ui-conflict3`에서 전체 미적용을 재검증했다. 최종 Confirm의 충돌 검사를 이 수정으로 대체하지 않는다.

`ui-storage3/loss3`에서는 readonly inspection이 `current.schema` projection을 비운 뒤 유효한 root 폼의 원래 기준을 찾지 못해 fresh retry가 차단됐다. 같은 project/id의 기존 요소 창 schema를 fallback으로 사용하며 원래 hash와 native 전체 검사는 유지했다. `ui-prior3`은 raw 입력이 있는 동안 새 copy 목록조차 열 수 없던 기존 picker guard에 막혔다. 읽기 copy 선택에만 한 raw snapshot을 결부했고 `prior4`에서 이전 거절의 미적용 확인·저장·명시 Confirm까지 완주했다.

`ui-peer4`에서는 다른 View 취소 후 기본 owner Confirm 상태가 갱신되지 않았다. `work()`가 다른 작업 중 조회의 접수를 거절하면 callback이 실행되지 않았는데도, 이전 `readStatus`가 undefined를 실제 조회 실패로 캐시한 것이 원인이었다. 조회는 동일 프로젝트에서 idle을 기다리고 callback이 시작되지 않은 경우에만 최대6회 접수를 재시도한다. 실제 조회가 시작된 뒤의 오류는 즉시 전달하고 source/revision/Confirm 검증은 그대로 유지한다. CDP로 접수 여부와 실제 상태 응답을 확인한 뒤 최종 uninstrumented `ui-peer5`에서 전체 흐름을 재검증했다. 검사 통과를 위해 dirty 상태를 조작하거나 Confirm을 강제하지 않았다.

## 빌드·패키지·화면 확인

Release helper와 solution 빌드는 경고/오류0, 최종 Linux 엔진 생성은 exit0/warning0이다. WebBundle의73개 리소스 지문을 최종 소스에 맞췄다. 실제 `ui-peer5`와 `ui-late4` 캡처를 열어 기존 요소/고급 source 창과 다른 owner 창을 확인했다. CSS/HTML·창 크기·컨트롤 배치는 변경하지 않았다. 이것은 전체 원본 화면의 pixel equality 검증이 아니다.

최종 Windows x64 교차 패키지는 `/workspace/artifacts/Confectory-v536-raw-copies-final/Windows-x64/Confectory.exe`를 포함한 **전체 폴더**다. 이전 `raw-copies` 폴더는 상태 조회 수정 전 중간본이므로 최종 산출물로 사용하지 않는다. `desktop_package.py`는 선언2321파일/73리소스, PE·의존성·변조 거절, 다른 cwd·설치 SDK 없는 packaged managed 엔진 웹 시작과 최소 로그인 렌더를 통과했다. Windows apphost/WebView2 자체는 실행하지 않았다. 실행 전제는 Windows x64 .NET Desktop Runtime10과 WebView2이며 폴더 내 동반 파일이 필요하다. checksum·깨끗한 checkout·최종 게시 결과는 후속 검증 기록에 남긴다.

로컬 사전 검토는 변경21파일(구현12/테스트3/문서6)을 검토 대상으로 분류했다. 비밀 패턴 검출0이며 실제 인증/profile 파일은 읽지 않았다. 패턴 검사는 모든 비밀이 없음을 증명하지 않는다. Git 후보에 생성물·로그·사용자 자료·패키지가 없다. 패키지 marker 포함2322파일/131882009bytes의 모든 선언 hash를 확인했다. marker SHA-256은 `5a4887abda969f1fb71ad33109110bd99f59f1a0a7f3a7245c153ec2ee69e9b4`, 정렬된 `PACKAGE_SHA256SUMS` 자체의 SHA-256은 `de0369068d2b19500f0b3ba8e425496bfc3a625ce00c33aa2e72998b62b78bec`이다. 전체 파일 목록과 hash는 `/workspace/scratch/v536-raw-copies/review/`에 있고 산출물과 함께 Git에서 제외한다.

## 고정 후속 수용

1. 등록 callable의 모든 target: 기존 `BlueprintCallAbiGroup`에 직접 등록 receipt와 모든 target/import/wrapper/record의 공통 원래 closure를 결부한다. 마지막 target/receipt 변경의 전체 거절, 원본 불변, Save/cold/Confirm이 조건이다.
2. copy-all-target·상속/whole-body/opaque·같은 callee 복수 사용: 각 seed/소유 provenance·node 식별성·모든 영향 source의 결합 계약이 남아 있다. opaque C#를 자동 재작성하지 않으며 원본에서 지원한 명시 편집 경로만 연결한다. 현재 단일 지원 문맥을 전체 지원으로 세지 않는다.
3. saved-copy ABI/기존 본문·multi-target·Set/property와 owner/raw의 결합: 각각의 검증 계획을 동일 후보/CAS와 Review 그룹으로 stage하는 계약이 필요하다. 현재의 순차 Save 차단은 유지한다. 지원되지 않는 조합을 단순 UI 숨김이나 거짓 성공으로 처리하지 않는다.
4. 모바일/최종 조작: 공유/고정 반환 이름과 alias/native ABI 구분, 원본 영역/다중 선택·readonly/특수 핀, 지원된 async/내부 흐름만 연결한다. 줌/검색/키보드·한글 IME·밀집 rail·desktop/mobile 폭·문서/프로젝트 전환에서 입력/연결/소유권 및 Save/cold/Confirm을 유한 시나리오로 확인한다. 브라우저 합성 입력과 실제 기기 수용은 구분한다.

정보 legacy inline/모든 compound·multiple 정의 전환·아이콘/순서·새 ref/function/imported 선택/정보 부모·기능도 기존 미완료다. 이미지 제공자/자산·협의/승자/shared Confirm·내장 renderer/FPS backend 부재는 이번 UI 연결에서 구현하지 않는다. 이후 전체 UI 통합 검사와 Helper 실제 에디터 도구 감사는 별도 단계다.

Windows 교차 패키지/리소스와 Linux에서의 managed 웹 기동은 실제 Windows apphost/WebView2·Android·터치/DPI/IME 검증이 아니다. Library의 기존 tools/list 네트워크 장애에 새 복구 근거가 없어 재호출·업로드 우회하지 않았다. 로컬 빌드 존재를 사용자에게 전달한 것으로 표현하지 않는다.
