# v536 로컬 중간 빌드 검증 — 2026-10-23

이번 범위는 로컬 검증/패키징이다. 커밋·푸시·업로드를 하지 않았다. 기존 미게시 작업과 사용자 자료/원본 레이아웃을 보존했고 새 기능을 추가하지 않았다. 런타임 제품 코드 수정 없이 빌드 의존성 복원과 오래된 Blueprint 테스트 동작/기대의 정정, 실패 fixture의 집중 재검증을 수행했다.

## 저장소와 변경 목록

읽기 전용 `git remote get-url`의 fetch/push는 모두 `https://github.com/jorodane/Confectory.git`이다. URL 재작성 설정은 확인되지 않았다. 실제 `git ls-remote`도 성공했다.

- 현재 브랜치: `work/current`.
- 로컬 HEAD와 조회한 원격 work/current: `cf2fcaef2788eab256e65f171b42e0579d7b1fbd`.
- 조회한 원격 main: `196c605fd60bb6afe73d5765d994a8989639c31d`.
- 로컬 main 참조: `b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee`; 이번 작업 전후 동일하다. 원격 main으로 reset/merge/fetch하지 않았다.
- 시작 시 변경 352개: tracked 수정 74개/untracked 278개. examples 33, packs 82, src 8, targets 15, tests 186, docs 27, reference 1이다. UI/어댑터·저장/CAS·Blueprint compiler/authoring·검증 문서/테스트 및 원본 v536 레퍼런스를 포함하는 누적 미게시 작업이다.
- 전체 경로 목록: `/workspace/scratch/v536-local-validation/changed-files.txt`, 최초 목록/분류는 `baseline.json`에 보존했다. 최종 추가 검증 파일은 `changed-files-final.txt`에 구분한다.

따라서 원격 대상은 사용자가 지정한 **jorodane/Confectory**와 일치한다. 이번 산출물은 위 HEAD만의 빌드가 아니라 누적 미게시 작업을 포함한 로컬 스냅샷이다. 이번 검증을 위해 Git 인덱스나 커밋을 만들지 않았다.

## 로컬 산출물과 실행 방법

Windows x64 폴더:

`/workspace/artifacts/Confectory-v536-local-validation-20261023/Windows-x64`

Windows에서 이 **폴더 전체**를 유지한 채 `Confectory.exe`를 더블클릭한다. 단일 파일 exe나 설치 프로그램이 아니다. `content`의 runtime/packs/UI/도구와 DLL/config 파일이 함께 있어야 한다. Microsoft .NET Desktop Runtime **10.0 x64**와 Microsoft Edge **WebView2 Runtime**이 별도로 필요하다. 사용자 프로젝트를 컴파일하려면 .NET 10 SDK도 필요하며, 에디터를 여는 검사는 SDK 없는 런타임 복사본에서도 통과했다. 런타임/파일 연결/계정은 사용자 PC에 자동 설치하거나 변경하지 않았다.

Windows exe: `/workspace/artifacts/Confectory-v536-local-validation-20261023/Windows-x64/Confectory.exe`.

Linux 빌드:

`/workspace/Confectory/examples/editor-home/.confectory/outputs/linux/071abbdf66637a391f30cba06bc3501ed64508a08d2bc44cfd516844749f69fc-82b5b95095f7`

정확한 `run` argv/통계는 `/workspace/scratch/v536-local-validation/linux-build.json`에 있다. 이번 격리 검사는 `.NET 10` host의 `DOTNET_ROOT`, `CONFECTORY_EDITOR_REPO=/workspace/Confectory`, `CONFECTORY_UI=web`와 fixture 전용 HOME_STORAGE/ENTRY_STORAGE를 사용했다. 실제 사용자 프로젝트를 실행하지 않았다.

패키지에는 사용자 설정·프로젝트·자격 증명을 포함하지 않는다. 명시적 HOME_STORAGE/ENTRY_STORAGE override는 보존하며, 표준 checkout의 `Builds/Windows-x64` 위치에서 기존 checkout profile을 재사용하는 경로도 fixture로 확인했다. 이번 외부 artifacts 경로가 실제 사용자 PC의 기존 profile과 같다고 주장하지 않는다.

## 완료한 검사

| 검사 | 결과와 범위 |
| --- | --- |
| 솔루션 fresh Release 빌드 | 복원 후 0 warning/0 error. 최초 `NETSDK1127`은 WindowsForms targeting pack 누락이었다. 기존 프로젝트의 NuGet 의존성을 격리된 빌드 환경에 restore한 뒤 통과했으며 csproj/Android 설정은 바꾸지 않았다 |
| 실제 작업 트리 Linux 빌드 | 현재 source의 EditorHome 실제 생성/링크 성공. 과거 scratch engine만 다시 실행한 것이 아니다 |
| 핵심 영향 회귀 | 상속 node 소유권·독립 선언 차단·typed import·컴파일 중 source 변화·schema/reference/path 보존 8 passed/0 failed/0 skipped |
| 실행창 결합 전체 | `v536_run_windows_followup.py` 전체 exit 0, **8건** 통과. 상태조회 중 입력/queued Pause, 종료 취소, 거절된 close 복구, 시작 결과 전달 실패 뒤 중복 실행 금지, compiler failure/retry/전체 종료, compile 중 close, artifact 검증/dedup/위조 target 차단, 미선언 target/원본 결과창 수명 |
| 실제 A/B 문서·입력 | `v536_document_projects_engine.py` 전체 exit 0, **4건**. 같은 namespace/객체/슬롯의 다른 프로젝트 입력 분리, 늦은 A callback이 B를 수정하지 않음, 실제 재시작 보존 |
| Browser Data | `v536_elements_data_write.py` 전체 exit 0, **7건**. 실제 셀 쓰기/취소/stale·foreign 거절, 잘못된 int 입력 유지·재시도, 정확한 64비트/한글 cold 보관과 명시적 재적용, 별도 상세 창의 소유 대상·다른 입력 보존 |
| Agent 공통 승낙/Helper 대화 | `editor_codex_onboarding.py`의 agent-common scenario exit 0, **13개 확인 항목**. 명시 등록 전 무동의/무등록, 두 전역 Helper와 프로젝트 배치 후 직접 대화, 해제·철회·계정/문맥 변경 경계. 자체 fake CLI/계정/응답을 사용했으며 실제 사용자 인증/유료 추론 성공의 증거가 아니다 |
| Blueprint 영향 회귀 | 기존 serial script의 **전반 10개 항목**을 확인한 뒤 cold 창 가림에서 중단됐다. 저장된 fixture를 재생성/초기화하지 않고 `v536_blueprint_validation_recovery.py` **3건/exit 0**으로 cold 미저장 Save, 실제 그룹 Review/명시 compiler Confirm, 타 편집 후 stale Save 차단·입력/소스 보존을 검증했다. 원 serial script 전체를 exit 0이라고 보고하지 않는다 |
| Windows 교차 패키지 | 실제 2,304개 파일의 win-x64 폴더 산출물 생성, launcher/WebView host 둘 다 PE x64 확인 |
| 패키지 구성/격리 | marker/hash 검증, UI 파일 변조·필수 WebView DLL 누락 거절, 경로가 패키지 안으로 계산됨, 새 테스트/프로필/.git 디렉터리와 지정 fixture hook이 실제 entry/resources에 포함되지 않음을 확인했다 |
| 실제 packaged 웹 시작 | 별도 cwd에서 SDK 없는 .NET runtime 복사본으로 packaged Windows용 managed engine을 Linux 웹 모드로 시작, **65개 리소스** 크기/hash 조회 및 최소 Codex 로그인 화면 렌더 통과. Windows apphost/WebView2 실행과는 구별한다 |
| 보존/정리 | HEAD/main/원본 v508·v536 ZIP hash 유지, Android 변경 없음. 확인한 격리 실행 프로세스 잔류 없음. 테스트에서 실제 사용자 자료나 계정을 읽고 실행하지 않았다 |

전체 로그/JSON은 `/workspace/scratch/v536-local-validation`에 있다. `result.json`, `package-isolation.json`, `package-final-check.json`과 원본 실패 로그도 보존했다. 패키지 자체의 전체 파일 fingerprint는 `confectory-desktop-package.json`에 있다.

## 실패를 정정하고 확인한 내용

Blueprint 초기 실패는 backend가 올바른 입력을 거절한 사례로 단정하지 않았다. 테스트가 root의 **타입 버튼을 연결 핀처럼 클릭**하여 실제 값이 선택되지 않았다. 원본 ‘핀 값 선택’ 메뉴로 바꾸고 실제 payload/개인 초안/서버/원본 보존 assertion을 유지했다. 뒤의 `int` 옵션 부재 기대도 이전 규칙이었다. 현재 `canAdaptInput`은 소유 일반 숫자 입력 정의의 명시적 적응을 지원하므로 숫자 옵션의 존재/취소 시 native long 보존과 bool/long 비호환 옵션 부재를 각각 확인하도록 정정했다. 타입 검사나 CAS를 완화하지 않았다.

cold 후 남은 실패는 뒤쪽 Blueprint 창의 저장 버튼을 앞쪽 Browser 창을 통과해 누르려 한 것이었다. 원본 헤더로 창을 전면에 두는 실제 사용자 동작으로 테스트를 고쳤고, 기존 미저장 자료를 그대로 재개하여 3개 실제 경로를 완료했다. force click·DOM 상태 위조·초안 초기화로 통과시키지 않았다. 제품 레이아웃도 변경하지 않았다.

## 구체적인 원본 복원 잔여

Browser:

- embedded Data에서 확인한 범위 외 **standalone Data 전체 흐름**, 일부 context/reference hover·참조 상세 경로.
- 이름 변경의 모든 표시 표면, 아이콘/자식 수 배지·드래그 미리보기의 전체 원본 대조.
- 삭제/복구 receipt import와 commit check-path 집중 수용 및 다른 source 종류/외부 namespace 경계. 현재 논리 보관·참조 차단·owned concept/category 검증 범위를 전체 유형으로 확대하지 않는다.

Blueprint:

- **여러 구현/대상과 C# 변환의 실제 원본 UI 전체 문맥**, 구현별 미저장 입력·취소/저장/복원·기존 형식 호환의 전체 수용.
- 공유/고정 반환 이름·잠정 빈 출력·영역/다중 선택·내부 흐름/async·나머지 특수 핀/readonly 문맥.
- 검증한 단일 소유 값↔ref 호출 외의 ABI/소유 문맥과 typed import 재연결.
- 속성+복사본 혼합 Save의 안전 차단을 실제 원자 편집에 연결하는 잔여, 원본 줌/검색/키보드·밀집 rail 전체 정밀 수용.

전체 목록은 `V536_UI_CONNECTION_STATUS.md`와 `V536_UI_RESTORATION_SCOPE.md`에 구분되어 있다. Helper 이미지 자산/이력/제공자, 실제 협의/승자/공유 Confirm/신문고, 내장 renderer/FPS는 별도 **backend 부재**이며 이번에 구현하지 않았다. UI용 API가 존재한다는 이유로 Helper에게 최종 Confirm/프로젝트 실행/다른 프로젝트 권한을 추가하지 않았다.

## 검증 한계

전체 v536 UI 복원 완료가 아니다. 실제 Windows 더블클릭/WebView2/커스텀 타이틀바·DPI/IME/snap 및 실제 Android/터치는 미검증이다. 실제 사용자 계정·OAuth·유료 모델 호출을 하지 않았다. 이번 요청의 커밋 금지에 따라 현재 미게시 작업 전체를 새 커밋으로 만든 일반 Git checkout 검사는 하지 않았다. 이 로컬 패키지를 원격에 게시하거나 업로드하지 않았다.
