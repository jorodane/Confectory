# 아키텍처 경계 감사 — 2026-10-07

현재 구현은 경계를 모두 지키고 있다고 판정할 수 없다. 코어의 일반 ID 해석은 두 비파괴 재현에서 정상 동작했지만, Android exporter의 제품 이름별 화면 선택, 웹의 특정 화면 자산 결합, 테스트의 SKIP 성공 집계가 확인됐다. 실제 제품 팩의 공통 타깃 이식은 아직 완료되지 않았다. 이 문서는 감사 결과이며 해당 결함을 수정했다는 보고가 아니다.

## 기준과 작업 상태

독립 검토자 3명이 실행 팩, 빌드/호스트, 테스트를 각각 검토했다. 감사용 checkout은 `4e37c144c2fc193c7932e7032ea18fc8a109eb48`에 고정했고 시작·종료 시 tracked 변경은 없었다. .NET10 솔루션 빌드는 경고·오류 0개(4.26초)였다. 정식 타깃별 구현 선택 자체는 허용된 설계로 취급했다. 임시 fault/minimal-pack probe는 보조 재현이며 제품 실행 성공으로 집계하지 않았다.

| 상태 | 기준 | 의미 |
|---|---|---|
| 이전 공개 작업 | `4952a2c` | 별도 Android Activity/웹 shell과 모델 연결을 검증했던 버전 |
| 감사 시작 직전 원격 | `317897a` | .NET10·Windows export/sign 기능·API36 설정 포함, 기존 Android 이름 분기는 남음 |
| 고정 감사 소스 | `4e37c14` | 공통 HostLoop 도입 및 옛 Main.android 제거 후, 플랫폼 제공자 통합 전 |
| Android 미통합 작업 | `5dc96a5`, `6ee9c9b`, `c4fc924` | 범용 Activity/provider·entry 검사 준비; 실제 범용 exporter 통합은 안 됨 |
| 공통 런타임 미통합 작업 | `5043856`, `9a07c4a` | 진행 중 job 정리, Console 신호를 desktop host로 이동; 감사 HEAD와 다름 |
| 브라우저 미통합 작업 | `8b61103`, `daf91bf`, `96e7938`, `bf96e15` | 범용 Canvas/native-field 제공자와 실제 제품 팩 wiring; 시작 검사 실패 |

후속 작업 파일은 감사 증거에 섞지 않았다. 스냅샷 당시 root/audit checkout은 깨끗했고 Android는 `c4fc924`였다. 브라우저는 당시 `e75de28` 및 미커밋 변경을 별도 기록한 뒤 `bf96e15`로 보존됐다. 전체 로컬 스냅샷 메타데이터는 `/tmp/confectory-audit-snapshot.json`에 있다. Git에는 소스/보고서만 저장하며 키·암호·바이너리·이미지·원시 로그는 저장하지 않았다.

고정 실제 제품 파일 SHA256:

- `examples/editor-home/Main.csbody`: `30cbd0d51dfa5a8e2ecdea700f23b0b4decc3e99fa81e2ad43ec849b71da8354`
- `examples/editor-home/MainBody.celem`: `791837dc76f8ac1a1f5996ea3ea42e0dcc32c13914c7167c23eeab096d97b74a`
- `examples/editor-home/project.cpack`: `30fc997c50211707f40e1ba4c75d96dc71fbd3a97039cd1473d73cf103ab24ab`

## 발견 및 검증표

| ID | 심각도·판정 | 현재 사실·사용자 영향 | 근거/관측 | 최소 수정 방향 |
|---|---|---|---|---|
| A1 | 높음·확정 | Android host가 실제 public entry 대신 제품별 화면을 실행한다. 유효한 다른 팩은 export 후 컴파일할 수 없다. | exporter `Program.cs:39-57`, `MainActivity.cs:50-53`; 최소 팩의 빈 PackCalls에 CreateOwner 호출을 컴파일하면 CS0117 | 범용 host에서 생성된 entry 실행, 제품 UI는 제품 팩/공용 역할 경로 유지 |
| A2 | 중간/높음·확정 | exporter가 모든 팩에 Window의 물리 파일을 강제한다. 없는 팩은 관리 코드 빌드 후 부분 출력과 예외를 남긴다. | `Program.cs:54`; Window 등록 제거 probe에서 KeyNotFoundException | 타깃 소유 bridge/public resource 계약으로 선택하고 쓰기 전 검증 |
| A3 | 중간·소스 결합 확정, 일반 앱 브라우저 실행 미검증 | browser target은 고정 Entry/Home 자산·snapshot 구조·owner를 요구한다. 일반 entry를 실행해도 화면이 그 entry의 UI라는 보장이 없다. | browser-wasm `Program.cs:9-10,25,28-29,43-44`, Bridge `:22,29`, runtime `app.js:16,19,22`, `dom.js:5-10` | 범용 부트스트랩/제공자 자산과 특정 애플리케이션 화면을 분리 |
| T1 | 높음·실행 재현 확정 | GUI/워크로드 미지원 SKIP이 PASS로 집계돼 녹색 합계가 미실행을 숨긴다. | test runner `Program.cs:18,21-22`; DISPLAY 제거 시 SKIP 3개 뒤 `3 passed, 0 failed`, exit0 | skipped 상태/개수 도입, 필수 acceptance 미실행은 완료로 처리하지 않음 |
| T2 | 높음·실행 재현 확정 | 공통 Main만 남았는데 테스트는 android Main body를 요구한다. 현재 검사 그래프가 실제 소스와 불일치한다. | MainBody `:53`, EntryHomeTests `:56`, ProjectShellTests `:36`; Android export 검사 `0 passed,1 failed`,199.578초 | 실제 entry와 선택 제공자·presentation 흐름을 검증하도록 교체, 단언 완화로 해결하지 않음 |
| T3 | 제품 이식 근거로 사용하면 높음·범위 차이 확정 | 기존 Browser/BrowserWasm 테스트는 다른 ProjectPack/화면을 실행한다. 실제 WASM 성공은 맞지만 데스크톱 Main 이식 증거는 아니다. | BrowserTests `:8-14`, BrowserWasmTests `:9-14`, 별도 EditorHome.Browser entry/수동 DOM | 같은 제품 manifest/Main의 실제 UI·입력·열기·편집 검사를 별도 필수 gate로 유지 |
| R1 | 중간·정확한 소스 보조 실행으로 확정 | session이 먼저 disposed가 돼 실행 종료 실패 후 CloseSession 재시도가 manager 정리에 도달하지 않는다. | model CloseSession `:1` → manager Dispose `:2` → execution Dispose `:5-6`; 재시도 `disposeAttempts=1`, manager active, registry retained | closing/closed 상태 분리, 실패 handle 유지, 성공한 정리만 확정 |
| R2 | 중간·제어 흐름 확정, native fault 미실행 | 초기 session/control/Owner/surface/listener 실패가 cleanup guard 밖에 있다. 재사용 host에 자원이 남을 수 있다. | Main `:5-19,102`, cleanup guard `:111`; 충돌 listener/native startup fault는 재현 계획만 작성 | 초기 획득 전체를 감싸고 획득된 자원만 독립 정리 |
| R3 | 높음·미완성 통합 확정 | 감사 HEAD의 Android/browser HostLoop delegate installer와 일부 surface/entry 제공자가 없다. 공통 Main 실행은 아직 미지원이다. | Run.android/browser `:1`은 getter/throw만 존재; CreateSurfacesBody common만, ProjectEntry Android 명시 거부 | 정식 플랫폼 제공자/host 연결 후 같은 실제 제품 팩 실행 검증 |

### A1/A2 호출 흐름

Builder와 Planner는 실제 entry를 해석한다. 이후 exporter는 entry imports만으로 PackCalls를 만들고, `registry.Project.Namespace == "Confectory.EditorHome"`이면 EditorHomeActivity를, 나머지는 BaseUI sample MainActivity를 복사한다. 전자는 CreateSession/Snapshot/Command와 구체 UI를 직접 호출하고, 후자는 정확히 두 View 및 Count/Toggle 모델과 sample alias를 요구한다. 둘 모두 생성된 Program.Main을 호출하지 않는다. 따라서 이름별 특별 대우이며 정식 target-body 선택과 다르다.

Window를 명시 등록한 최소 `Audit.Arbitrary::Launch()->int` 팩은 실제 portable 빌드/실행에 성공한다. 같은 입력의 Android source export는 관리 코드 성공을 정확히 기록하지만, 빈 PackCalls와 sample Activity가 맞지 않는다. `androidAppCompiled=false`라 패키징 성공을 거짓 기록한 것은 아니다. 문제는 일반 export 후보 자체의 호출 구조다.

### R1/R2 수명 경계

ProjectExecution은 Stop 실패 시 session을 보존해 재시도하도록 설계돼 있다. 그러나 EditorHome.Model.CloseSession은 그보다 먼저 state[6]을 true로 만들고 재호출에서 바로 반환한다. 정확한 고정 body를 복사한 delegate fault harness에서 첫 Dispose를 실패시키고 두 번째 시도를 허용했지만 Dispose 호출 횟수는 1이었다. 이것은 실제 native kill 실패 재현이나 제품 성공 검사가 아니다.

Main의 HostRun 실패 정리(`4e37c14`)는 마지막 Run 호출을 보호한다. 앞선 자원 획득과 EntryListen까지 보호하지 않는다. 다른 process-owner가 listener lock을 이미 소유하거나 두 번째 NativeCreate가 실패하는 경로는 정적 제어 흐름상 cleanup에 도달하지 않는다. 이 native fault 경로는 실행하지 않았다.

## 비파괴 재현

모든 명령은 고정 checkout과 SDK10을 사용했다. 실제 프로젝트/키/공유 산출물은 변경하지 않았다.

```sh
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet
export DOTNET_CLI_HOME=/tmp/confectory-audit-dotnet
cd /workspace/Confectory-audit-20261007
"$CONFECTORY_DOTNET" build Confectory.sln -c Release
env -u DISPLAY "$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll actual_linux_startup actual_linux_menu EntryHomeResizeTests
"$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll test_android_home_export_selects_activity
```

관측: build 경고·오류 0개; SKIP gate는 3 passed/0 failed; Android gate는 옛 body 선택 단언에서 exit1. 그 앞의 export/template/report 검사는 실제 통과했다.

일반 해석 probe는 `/tmp/confectory-axis2/alpha/unusual.cpack`와 namespace·위치·파일 배치를 바꾼 `/tmp/confectory-axis2/renamed/deeper/unusual.cpack`였다. 두 팩 모두 public Build.DotNet target과 `()->int` entry/provider를 선언하고 body는 return0이었다. 함수/구현 파일도 `start-any.celem`, `implementation-any.celem`, `arbitrary.csbody`로 바꿨다. 두 실제 DLL 실행 exit0을 확인했다.

```sh
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build /tmp/confectory-axis2/alpha/unusual.cpack portable
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build /tmp/confectory-axis2/renamed/deeper/unusual.cpack portable
"$CONFECTORY_DOTNET" targets/android-export/bin/Release/net10.0/Confectory.AndroidExport.dll /tmp/confectory-axis2/alpha/unusual.cpack /tmp/confectory-axis2/new-export
"$CONFECTORY_DOTNET" build /tmp/confectory-axis2/compile/Probe.csproj --nologo
"$CONFECTORY_DOTNET" run --project /tmp/confectory-close-retry-probe -c Release
```

export 폴더는 반드시 새 이름을 써야 한다. compile probe는 실제 출력 PackCalls와 sample의 첫 CreateOwner 호출을 사용해 CS0117을 관측했다. Window 등록만 제거한 별도 입력은 exporter `Program.cs:54`에서 실패했다. 임시 입력/소스는 로컬 `/tmp`에 보존됐고 Git에 원시 출력/바이너리를 넣지 않았다.

검토 범위와 원시 근거: `/tmp/confectory-audit-{runtime,build,tests}.md`, `/tmp/confectory-audit-frozen-build.log`, `/tmp/confectory-axis2-*.log`. 이 임시 파일 경로는 당시 workspace의 근거이며 사용자 PC에 파일이 있다는 뜻은 아니다.

## 정상 경계 및 판정하지 않은 부분

- Core Build `:20-27`, Resolution `:272-274`, Generation `:75-82`의 public target/entry/qualified-ID/signature 해석은 검토 및 두 최소 팩 재현에서 특정 EditorHome 우회가 없었다. 전체 코어/모든 플랫폼 무결성을 보장하는 결과는 아니다.
- 정식 target-specific provider, 선언된 public ID, 타깃 소유 부트스트랩 파일 이름, 별도 managed contract/locality 검사는 정상 설계다. 파일 이름이 있다는 사실만으로 결합 결함이라 하지 않았다.
- 실제 BrowserWasm Bridge는 generated Program.Main을 실행한다. WASM/Chromium/GET-only 검사는 실제이며 가짜 실행으로 판정하지 않았다. 다만 별도 앱의 성공을 같은 제품 UI 성공으로 바꿔 읽으면 안 된다.
- fake-reply/FakeTool은 명시적인 임시 negative protocol fixture다. 제품 실행 우회에 쓰인 증거는 없다. 복사본 poison과 comment locality probe도 보조 검사로는 허용된다.
- 검토한 실행 팩에서 테스트 이름을 감지하거나 숨겨진 PASS를 반환하는 생산 분기는 발견하지 못했다. 확인한 RuntimeBase/BaseUI ownership/revision, native Window API, ProjectEntry lock/message 경로는 실제 계약 흐름이었다.
- Linux GUI helper는 실제 report.run·native 입력·pixel/로그 단언을 사용하고 browser helper는 page error/실제 runtime 요청을 확인한다. 검토한 helper에서 단언 실패를 광범위하게 무시하는 성공 경로는 찾지 못했다.

## 미통합 작업의 관측 — 감사 판정과 분리

`5043856`의 같은 제품 팩은 Linux/Windows 관리 코드 빌드 및 기존 ProjectShell X11 검사를 통과했다. Home X11 검사는 :97/:98에서 GTK chooser 종료 실패로 남았고, 입력 위치가 `/tmp/co`까지인 화면을 확인했지만 원인은 확정하지 않았다. 검사 조건을 완화하지 않았다.

브라우저 미통합 제공자는 실제 `Confectory.EditorHome::Main`을 컴파일했지만 Chromium 시작 검사가 실패했다. 진단 stack은 `PosixSignalRegistration.Register -> Console.add_CancelKeyPress -> 실제 MainBody -> Program.Main -> Bridge.Initialize`였다. 별도 shell로 성공 처리하지 않았다. `9a07c4a`는 이 신호 처리를 desktop HostLoop로 이동하는 후보지만 아직 통합/검증하지 않았다. 진단 bridge logging으로 재현한 런타임은 이전 common body stage라 최신 WIP 전체 성공 근거로 쓰지 않았다.

범용 Android 후보는 PackEntry.Run/공통 HostLoop 및 generic Window/input/import 제공자를 준비했고 SDK source compile만 통과했다. root exporter의 범용 entry 연결 및 같은 제품 팩 실제 APK/AAB 검사는 미수행이다. API36 도구/전환 패키징 및 native 정렬 조사도 이 product-flow 검사를 대체하지 않는다. 실제 키 서명·기기 실행·Play 업로드는 하지 않았다.

다음 순서: 먼저 A1/A2와 T1/T2의 최소 수정·검증, 이어 같은 product pack의 플랫폼 제공자 통합, R1/R2 수명 재현·정리, 마지막 실제 동일 입력의 Linux/Windows/browser/Android acceptance. 감사 요청 자체로 추가 대규모 수정은 시작하지 않았으며 미통합 작업은 보존했다.
