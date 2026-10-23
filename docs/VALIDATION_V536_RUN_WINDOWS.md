# v536 실행창 연결 — 첫 검증 묶음

2026-10-23, `work/current`의 미게시 변경. 기준 HEAD는 `cf2fcaef2788eab256e65f171b42e0579d7b1fbd`이며 전체 UI 복원/Windows 패키지/게시는 아직 완료하지 않았다.

## 원본과 실제 엔진

사용자가 지정한 `196c605`의 v536 `app.js:442–486`은 창별 세션과 502×348 실행창, 헤더 재생/중단·일시정지/재개·다음 프레임·내보내기를 정의한다. 닫으면 해당 창의 데모 시계를 정리한다. 원본의 엔티티 애니메이션/30fps/모의 내보내기는 실제 엔진 동작이 아니다.

실제 `ProjectExecution.LaunchConfigured/Observe/Control/Stop`은 독립 프로세스와 소유한 프로세스 트리 종료, 협력적 프레임 경계의 pause/resume/step을 지원한다. 내장 렌더 표면과 렌더 FPS 계약은 없다. 원본 헤더/CSS와 문서 탭 구조에 실제 프로세스를 연결하고 화면 본문에 별도 프로세스·렌더 미지원, FPS 위치에는 `—fps`를 표시했다. 가짜 엔티티나 30fps를 표시하지 않는다. 내보내기 메뉴는 기존 실제 BuildJobs 진입점에 연결했지만 원본 결과창 대조와 내보내기 통합 검사는 남아 있다.

`RunWindows` 서버 어댑터는 현재 선택한 manager context/manifest와 창별 일시적 lease/handle을 결부한다. UI는 프로젝트 경로/실행 파일/환경변수나 내부 전체 종료 작업을 지정할 수 없다. 공개 결과에 비밀 pipe/secret·raw stderr를 넣지 않는다. 실행은 명시적인 재생 동작에서 선언된 target의 확정 소스를 빌드한 뒤 시작하며 초안을 자동 Confirm하지 않는다. 시작 command id를 중복 실행 방지에 사용한다. 프레임 변경은 실제 runtime/ACK/sequence와 대조하며 불확실한 명령을 재생하지 않는다. 창 id만 private layout에 저장하고 프로세스/lease/실행 권한은 디스크에서 복구하지 않는다.

창·탭 닫기는 해당 lease의 실행 정리 성공 후 닫는다. 프로젝트 숨김/전환과 엔진 종료에는 새 실행창 소유자 정리 경로를 연결했다. 기존 legacy 실행 API는 호환 경로로 보존한다. 전체 프로젝트 종료는 실행창 활동도 확인하되 동의 전 중지하지 않도록 분리했다. 이 마지막 전체 종료 확인/취소 경로의 전용 UI 검사는 아직 남았다.

## 실제 검사

- `run-windows-build-5.log`: 실제 Linux C# 컴파일 exit 0. resource 64개, canonical text 55개의 hash/size 일치. 관련 JS 문법/Python 컴파일/diff 공백 검사 통과.
- `tests/web/v536_run_windows_backend.py`, `run-windows-backend-2.log`: 실제 Linux 엔진과 격리 `examples/frame-loop` 복사본에서 **7건** 통과. 단순 열기 무실행, 내부/소유권 위조 차단, 두 독립 실행과 자기 프레임 Step, 시작 중복 방지, 틀린 handle/lease/과거 ACK 차단, 자기 Stop/Close·재열기 새 lease, 실제 컴파일 실패→명시 재시도, 같은 이름/다른 경로 프로젝트 전환 정리, 엔진 재시작 무자동실행·과거 권한 거부, 원본 fixture 파일 바이트 보존을 확인했다. 증거 `/tmp/confectory-run-windows-backend-kro2kv8u`.
- `tests/web/v536_run_windows_ui.py`, `run-windows-ui-3.log`: 실제 Linux 엔진+Chromium **5건** 통과. 헤더/문서 탭과 무실행 열기, 실제 재생/Pause/1 frame Step, 두 탭 독립·한 탭 닫기와 다른 실행/한글 입력 보존, 중단/페이지 재진입·입력 복원, 390×844 원본 헤더 줄바꿈과 실제 패널 bounds. JS 오류/외부 요청 0. 증거 `/tmp/confectory-run-windows-ui-7ruxpxcf`.
- 기존 `v536_document_windows_renderer.py` **8건** 통과. 새 닫기 hook 이후에도 비실행 문서의 분리/플로팅·일괄 닫기·입력 보존과 프로젝트 소유권 동작을 보존했다. 이 검사는 renderer fixture이며 실제 실행 프로세스 검사가 아니다.
- 원본 `v536-original-run-window.png`와 실제 `run-floating.png`, desktop/mobile 캡처를 직접 열어 확인했다. 502×348 플로팅 창에서 원본/실제 모두 헤더 500×49, 제어 그룹 92×28, 세 버튼 각 28×28, 내보내기 56.484375×28, 본문 500×297로 일치한다. 치수 자료는 `v536-original-run-measurements.json` 및 실제 fixture의 `run-measurements.json`이다. 전체 UI 픽셀 일치의 근거로 확대하지 않는다.
- 최종 호스트 종료 후 위 두 격리 fixture 경로를 가진 dotnet 프로세스가 남지 않은 것을 확인했다. 다른 사용자 프로세스를 종료하거나 환경변수/인증 자료를 읽지 않았다.

## 실패와 수정

- backend 첫 검사에서 browser RPC로 native 전용 `host.open-file`을 호출하여 admission에서 거부됐다. 보안 설정을 바꾸지 않고, 두 격리 프로젝트를 각각 지정한 시작 실행으로 등록한 뒤 기존 listing/openProject 경로로 전환하도록 테스트를 수정했다.
- UI 첫 검사에서 한글 채팅 입력 직후 실행 버튼을 눌러도 창이 열리지 않았다. blur의 서버 초안 저장이 클릭 전에 버튼을 비활성화하는 기존 문제다. 순수 화면 열기인 실행/전투 로그로 이동할 때 private presentation에 입력을 보관하고 클릭을 유지하도록 좁게 수정했으며 실제 입력 보존을 재검증했다.
- UI 두 번째 검사는 실행 문서 탭을 연 상태에서 숨겨진 Workspace dock 버튼을 누르려 했다. 원본처럼 Workspace 탭으로 돌아가 다음 실행창을 여는 실제 경로로 테스트를 수정했다. 제품 버튼을 임의로 추가하거나 원본 레이아웃을 바꾸지 않았다.

## 첫 묶음 뒤의 잔여 기록

원본 내보내기 결과창과 실제 artifact 연결·통합 검사, 전체 종료 확인/취소·진행 중 닫기/실패 시 재시도 경계, 프로젝트 전환 및 cold 복원의 화면 통합 검사를 마무리해야 한다. 백그라운드 상태조회가 일반 입력/버튼을 불필요하게 차단하는지도 확인한다. 기존에 통과한 backend 7건/기본 UI 5건은 영향 있는 변경 없이 반복하지 않는다.

내장 renderer/FPS는 백엔드 부재이다. 브라우저에서 그린 배경을 실제 프로젝트 렌더라고 표시하지 않는다. 실제 Windows/WebView2/기기 터치 실행, Windows 교차 패키지·checkout·원격 게시와 전체 v536 수용 회귀는 미완료다. 실제 사용자 프로젝트 실행/로그인/유료 추론/새 계정 권한 설정은 수행하지 않았다.

## 후속 실행창 묶음 완료 — 2026-10-23

원본 `openBuildResult`의 430×285 창/상태 태그·제목·설명·산출물 요약 배치를 유지하는 `run-exports.js`를 연결했다. 기존 개발용 BuildJobs 폼으로 이동하지 않는다. 실제 `startBuild/buildInfo`의 소유 프로젝트/대상·산출물 개수와 `verified/changed/missing/unavailable`만 표시하며 원본의 ‘모의 빌드 완료’를 가져오지 않았다. 내보내기는 컴파일일 뿐 Run/외부 배포가 아니다. 선언하지 않은 Android 등은 요청을 보내지 않는다.

새 내보내기 UI는 요청 UUID를 사용하고 기존 BuildJobs가 context/path/target에 묶은 세션 내 영수증으로 같은 요청을 중복 실행하지 않는다. 요청 UUID만의 조회는 그 영수증을 읽는 작업이며, 재시작 후 없는 영수증은 `owner-unavailable`로 반환한다. 조회를 새 빌드로 승격하지 않는다. 이 바인딩은 실제 계정/지속 실행 권한을 만들지 않는다. 동일 프로젝트에서 이미 진행 중인 빌드의 결과창을 닫고 다시 열면 그 job을 읽는다.

원본 `app.js:847 saveLayouts`는 **build-result를 저장 레이아웃에서 제외**한다. 이 수명을 그대로 유지했다. 엔진 재시작에 결과창을 자동으로 열지 않고 빌드 이력/산출물 기록을 보존한다. 편집 입력을 가진 Run/문서의 private 복원과 결과창의 일시적인 수명을 혼동하지 않는다.

상태조회에서 확인한 두 결함을 수정했다.

- 정상 수신을 기다리는 Run 읽기가 전역 `work/busy`를 사용하여 일반 버튼을 비활성화했다. 실제 지연 응답으로 재현한 `run-followup-red.log`는 해당 assertion에서 실패했다. Run 및 build 상태 읽기는 별도 대기 읽기로 처리하고, 사용자 명령은 선행 읽기 뒤 최신 view를 검사한다. 사용자 입력·버튼은 읽기 때문에 비활성화하지 않는다. 읽기 실패는 해당 창의 다시 확인 상태로 남기고 별개 사용자 동작을 함께 취소하지 않는다.
- 전체 프로젝트 종료의 UI 활성 작업 판정이 legacy executionState만 봤다. 새 Run 창의 실제 실행/아직 결과를 모르는 시작 상태도 확인창에 포함한다. 취소는 Stop을 보내지 않는다. 프로젝트 정보/Run 버튼으로 이동하는 채팅 blur는 private 입력을 보관하여 그 클릭을 잃지 않게 했다. 소스 검증/CAS/동의 가드는 그대로다.

후속 실행 결과는 다음과 같이 구분한다.

1. `run-followup-ui-1.log`: 실제 Linux 엔진+Chromium에서 **앞의 7개 검사 완료**. 지연 상태읽기 중 입력과 뒤따른 Pause, 전체 종료 취소, 실제 서버의 lease 거절 뒤 창/실행 유지→명시 재시도, 실제 시작 뒤 결과 전달 실패→같은 handle 재조회/시작 재전송 없음, 실제 컴파일 실패→재시도/전체 종료 확정, source lease를 기다리는 컴파일 중 닫기, 원본 결과창에서 실제 13개 산출물 검증/Run 금지/같은 요청 dedup와 target 위조 거절이다. 이 결합 스크립트 전체 exit는 1이다. 마지막 검사가 결과창에 포커스를 준 뒤 숨겨진 Run 탭의 버튼을 다시 누르려 했다. 스크립트를 실제 탭 재진입 경로로 정정했으며 이 로그 전체를 ‘전부 통과’로 기록하지 않는다.
2. `run-exports-followup-3.log`, session 98876 exit 0: 이어진 실제 엔진+Chromium **4건 통과**. 원본처럼 결과창 무자동복원/저장 산출물 재검사, 미선언 target/없는 command 조회 무실행, source lease 대기 중 결과창 닫기→같은 job 재열기→파일 일치, 같은 이름/다른 경로 A/B 재시작·전환의 입력/산출물 분리·외부 job 조회 거절이다. JS/외부 요청 0. 증거 `/tmp/confectory-run-followup-6fex_vk2`.
3. `run-read-error-1.log`, session 61287 exit 0: 실제 엔진 **1건 통과**. Run 읽기 결과만 실패로 바꾼 fixture transport에서 그 실패를 실행창에 남기면서 대기 중인 실제 프로젝트 정보 조회와 새 입력은 정상 진행했다. 증거 `/tmp/confectory-run-read-error-5kilatri`. 이는 upstream/provider 실패를 재현한 검사가 아니다.
4. 최초 export 후속 두 실행의 잘못된 ‘자동 결과창 복원’ 기대는 원본 saveLayouts와 대조하여 바로잡았다. 첫 결합 검사 중단 때문에 아직 flush하지 않은 layout을 기대한 점과, 명시 flush 뒤에도 원본이 결과창을 제외한다는 점을 각각 확인했다. 테스트의 source 보존 기준에서도 `.confectory/.build` 산출물을 소스와 구별했다. 원본 동작/소유권 검사를 완화하거나 fixture 실패를 제품 복구 성공으로 바꾸지 않았다.

같은 7개 성공 경로를 상태 보고를 위해 반복하지 않고 미완료 후속 4개와 읽기 오류 1개를 집중 검증했다. 결합 테스트 수정본의 전체 재실행은 이 단계에 포함하지 않았으며 게시 전 영향 회귀에서 구분한다. 테스트의 지연/오류 응답은 브라우저 fixture에만 있고 배포 코드에 test flag/provider/승인 우회 API를 추가하지 않았다. 실제 OS Stop 거절/전원 손실을 주입한 것은 아니다.

최종 생성 Linux 컴파일 `run-followup-build-4.log` exit 0. resources 65/canonical text 56개의 hash/size, 관련 ESM/Python 문법과 diff 공백 검사를 통과했다. 원본 `v536-original-export-window.png`와 실제 `export-reopened.png`를 직접 열어 배치·상태를 확인했다. 이전 Run 창 7영역 치수 일치 근거도 보존한다. Windows 교차 패키지/실기기/checkout/commit·push는 아직 수행하지 않았다.

이번 지원 가능한 Run/내보내기 후속 묶음의 알려진 실패는 남지 않았다. 내장 renderer/FPS backend 부재와 실제 Windows 실행 미검증은 그대로다. 전체 v536의 완료/부분/backend 부재 및 중간 빌드 준비 순서는 `V536_UI_CONNECTION_STATUS.md`에 분리했다. 새 이미지 제공자/협의 backend/Helper 편집 도구 확장은 이번 묶음에 추가하지 않았다.

## 로컬 중간 검증 재실행

2026-10-23 사용자 요청에 따라 새 실제 작업 트리 Linux 빌드에서 수정한 결합 `v536_run_windows_followup.py` **전체8건/exit0**을 확인했다(`/workspace/scratch/v536-local-validation/run-combined.log`). 앞 단계의 결합 전체 재실행 잔여는 해소됐다. Windows 교차 패키지/구성/packaged 웹 시작도 통과했으나 Windows native 실행은 아니다. 이 단계는 로컬 전용이며 커밋·푸시·업로드를 하지 않았다. 전체 영향 회귀와 한계는 `VALIDATION_V536_LOCAL_INTERMEDIATE.md`에 기록했다.
