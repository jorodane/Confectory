# Windows 시작 파일: Confectory.bat

최신: Git에 추가된 v196 원본의 해시와 실제 화면을 확인했습니다. 기본 시작은 내장 HTML EditorHome입니다. 홈·프로젝트 생성·기존 프로젝트·의미 객체 속성·초안·Save/Review/Confirm·Helper·AI 설정/권한 검토·증강/Worker·로컬 YogiBox를 연결했으며 나머지 기능은 [지원 범위](EMBEDDED_WEB_UI.md)에 구분했습니다. Windows OS 실행 검증은 보류입니다.

저장소 밖에 푼 Windows 배포 묶음의 진입점은 **Confectory.exe**입니다.
[표준 사용자 수락 시험](#표준-사용자-windows-수락-시험)의 절차를 사용합니다.

개발 체크아웃에서는 저장소 루트의 **Confectory.bat**를 엽니다. 기존 .NET 10 SDK와 Windows에
있는 Windows PowerShell을 사용하며, 도구를 설치하거나 전역 환경변수/setx를
설정하지 않습니다. `CONFECTORY_DOTNET`을 이미 지정했다면 해당 실행 파일을
사용하고, 아니면 PATH의 `dotnet`을 사용합니다.

루트 실행은 메뉴 없이 솔루션을 빌드하고 내장 HTML EditorHome을 엽니다.
`Confectory.bat "C:\path with spaces\project.cproj"`는 기존 DesktopEntry의
같은 인스턴스 전달/metadata-only 열기를 사용하며 해당 프로젝트 코드를 실행하지 않습니다.

개발 도구 메뉴는 **`scripts/windows/developer-tools.bat`를 명시적으로 열 때만** 나타납니다.
아래 빌드/내보내기는 기존 도구이며 새 에디터 내부 UI가 아닙니다.

| 개발 도구 선택 | 실제 동작 |
| --- | --- |
| 1 | 솔루션을 빌드하고 실제 `examples/editor-home/project.cpack`의 내장 HTML 에디터 실행. 파일 인수가 있으면 기존 DesktopEntry의 같은 인스턴스 전달/metadata-only 열기 사용. |
| 2 | 미연결 Helper/Worker/증강 등 남은 기능을 안내. 빌드·브라우저·서버·설치 작업 없음. |
| 3 | 솔루션/도구 및 Windows x64 에디터 exe 폴더 생성. 사용자 프로젝트 실행 없음. |
| 4 | 기존 Android exporter로 **unsigned** 내보내기. 기존 JDK/Android SDK/workload가 필요하며, 없으면 실패 진단. 설치·키 생성·서명 없음. 파일 선택 취소 가능. |
| 5 | `.confectory/Confectory.cproj.reg` 생성만 수행. 내용을 검토한 뒤 사용자가 직접 import해야 하며, 런처는 레지스트리를 변경하지 않음. |
| 6 → 1 | 개발 진단: 선택한 프로젝트에 대해 **외부 브라우저** WebUI 기반 화면 실행. `CONFECTORY_UI=web`, `CONFECTORY_WEB_PROJECT`를 자식 프로세스에 설정해 실제 EditorHome 팩 실행. 구웹데모를 실행하지 않음. |
| 0 | 종료. 잘못된 선택, 진단 메뉴에서 뒤로 가기, 입력 종료는 빌드를 시작하지 않음. |

기본 에디터는 Windows 창 내부 WebView2입니다. 실제 EditorHome 팩이 모델과 초안의 소유권을 유지하고, 별도 범용 호스트는 HTML 렌더링만 맡습니다. 기존 .NET 10 Desktop 및 WebView2 Runtime이 필요합니다. 없으면 실패를 진단하며 자동 설치하지 않습니다. 외부 브라우저는 개발 진단에서만 사용합니다. CMD·PowerShell·WebView2 창의 실제 Windows 실행은 이 Linux 환경에서 검증하지 못했습니다.

개발 도구 메뉴에서는 작업이 끝나거나 실패하면 Enter로 메뉴로 돌아갑니다. 각 작업은
별도 PowerShell 프로세스에서 실행하며 웹/구형 데모 모드 변수를 초기화합니다.
SDK 경로, 프로젝트 경로는 명령 문자열로 조립하거나 Invoke-Expression으로
평가하지 않습니다. 명시적 인수 배열/리터럴 경로를 사용합니다. Web 프로젝트
선택 취소는 도구 빌드 이전에 반환합니다. 로그는
`.confectory/launcher-logs/<작업>-<시각>-<pid>.log`입니다. Android exporter는
단계와 산출물 경로를 별도로 출력하며, 새 메뉴는 서명 대화를 열지 않습니다.

## 이동 및 기존 연결

- `scripts/windows/internal`: 빌드, 실제 Home, DesktopEntry 열기/복구/등록 파일,
  Android export 배치와 PowerShell.
- `scripts/windows/legacy`: 구형 Editor, Engine/authoring, 프로젝트 브라우저,
  구형 import-only 웹 데모. 사용자 기본 메뉴의 에디터가 아닙니다.
- `scripts/windows/verification`: 도구 산출물 검사와 windowless 실험.
- `scripts/windows/launcher.ps1`: 기본 editor 작업 실행과 명시적 개발 메뉴.
- `scripts/windows/developer-tools.bat`: 개발 메뉴 진입점.

모든 이동은 Git rename으로 추적하며 원본 팩과 사용자 데이터는 삭제하지 않습니다.
내부 배치는 위치에서 `../../..`를 계산하고 호출/문서/테스트 참조도 갱신했습니다.
기존 체크포인트 문서의 직접 실행 경로는 역사적/진단용입니다. 개발 체크아웃의
기본 진입점은 루트 `Confectory.bat`입니다.

새 파일 연결 등록 파일은 `Confectory.bat "%1"`을 가리킵니다. 파일을 누르면 빌드 후 기존 열기 경로로 바로 연결됩니다. 이미 이 루트 파일을 가리키는 연결은 재등록할 필요가 없습니다. **이미 Windows 레지스트리에 저장된
옛 `open-project-windows.bat` 경로는 자동 변경할 수 없습니다.** 기존 설치는
개발 도구 메뉴 5로 등록 파일을 생성·검토하고 직접 적용해야 합니다. 이전에 저장한
바로 가기도 새 루트 진입점으로 변경합니다. 사용자 PC/레지스트리는 건드리지
않았고, 제거한 루트 경로에 두 번째 사용자용 호환 런처를 남기지는 않았습니다.

## WebView2 도입 전의 창 내부 HTML 연결 조사

아래는 현재 Windows 내장 호스트를 도입하기 전의 조사 기록입니다. 당시 `packs/web-ui/Client.csbody`의 `WebView`는 JS 상태/요청 클라이언트이며 OS
WebView가 아닙니다. BrowserHost는 loopback HTTP, BrowserRuntime은 WASM 브리지입니다.
저장소에는 WebView2/CEF 같은 내장 렌더러 제공자가 없습니다.

Windows 후보인 [WebView2](https://learn.microsoft.com/en-us/microsoft-edge/webview2/get-started/win32)는
네이티브 창 안에서 HTML을 렌더링할 수 있습니다. 선택/도입 전 확인해야 할 연결은:

1. Windows 제공자가 렌더러 생성·크기·포커스·IME·메시지 루프·종료를 소유.
   `Window::SurfaceInfo`는 진단용 opaque ID이므로 이를 임의 HWND로 캐스팅하지
   말고 제공자 안에서 지원되는 소유권/자식 표면 계약을 마련해야 함.
2. `WebUI::Resource`의 선언된 리소스를
   [로컬 리소스 응답/가상 origin](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/working-with-local-content)으로
   공급. 별도 HTTP 리스너가 필수인 구조가 아님. 외부 이동/팝업/미등록 리소스는 차단.
3. [네이티브 메시지 교환](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/overview-features-apis)을
   기존 `WebUI::Request` envelope에 연결. 기존 JS의 `connectLocal()` 선택 부분을
   제공자 주입 transport로 분리하고, 엔진/파일/shell 객체를 JS에 통째로 노출하지 않음.
4. EditorHome의 Model/session 소유권과 `WebStart`의 HTTP Serve 부분을 분리해
   같은 consumer State/Invoke를 내장 호스트에 연결. 기존 scope/CAS/취소/Save와
   Review/Confirm 구분을 유지하며 창/렌더러 종료가 독립 Worker 종료가 되지 않도록 검증.

이는 구현 계획의 조사이며 SDK/runtime 설치, 제공자 확정, UI 이식 완료를 의미하지
않습니다. 같은 팩 HTML을 창 내부에서 쓰는 목표와 향후 서버 활용을 구분합니다.

## 정상 stderr 진행 메시지 표시 수정 (2026-10-11)

사용자는 실제 EditorHome 실행 성공을 확인했습니다. `RunProject.cs`의
`Resolving/building`과 `Pack build process started`는 stderr에 쓰는 정상 진행
메시지이며, 관측된 `NativeCommandError` 표시만으로 빌드 실패를 뜻하지 않습니다.

`internal/native-tool.ps1`에서 Windows PowerShell의 리디렉션 결과를 문자열로
변환한 후 화면과 UTF-8 로그에 즉시 기록합니다. stderr를 버리지 않으며, 실제
실패는 원래 네이티브 종료 코드로 판단해 launcher catch와 배치까지 전달합니다.
`Continue` 범위는 네이티브 호출 블록에만 한정하고 호출자/로그 쓰기 오류 처리는
유지합니다. [PowerShell 스트림 리디렉션](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_redirection?view=powershell-5.1)의
오류 객체를 그대로 Host에 넘겨 생기는 형식 표시를 피하는 변경입니다.

명령 문자열이나 새 비동기 프로세스 관리자를 도입하지 않았습니다. 기존 `&`와
인수 배열, 동기 파이프라인을 유지해 실행 중 출력과 CLI 종료를 기다립니다.
Ctrl+C 처리도 기존 PowerShell/CLI 콘솔 경로를 유지하며 Windows 실동작은 미검증입니다.

Windows PowerShell 전용 회귀를 추가했습니다: stderr 진행 후 성공/exit 23,
양쪽 스트림 각 2,000줄, 지연 종료 대기, 공백/한글 스크립트 경로와 `&`/`!` 인수,
로그 보존 및 NativeCommandError 장식 부재, 호출자 Stop 설정 보존을 검사합니다.
이 Linux 환경에는 Windows PowerShell이 없으므로 해당 회귀는 실행하지 못했습니다.
솔루션 빌드는 경고/오류 0으로 통과했습니다. 정적 회귀 4개 통과,
CLI/파일 연결 영향 회귀 3개 통과·실패 0·Windows 전용 4개 skip (14.187초).

## 직접 실행 수정 및 검증 (2026-10-11)

5d1bfc4의 `$home` 대입은 PowerShell의 대소문자 무시 규칙 때문에 읽기 전용
`$HOME`과 충돌했습니다. `$confectoryEditorProject`로 바꾸고 관련 Windows
스크립트의 예약 변수 대입도 검사했습니다. 이전 정적 검사는 이 오류를 놓쳤습니다.
기본 Action과 루트 배치는 이제 editor를 직접 실행합니다. 개발 메뉴는 별도 명시적 진입점입니다.

Python 회귀 검사는 원래 `$home` 오류를 탐지하고 전체 Windows 스크립트를 검사합니다.
Windows 전용 테스트에는 실제 PowerShell 구문/AST 검사와 CMD 직접 실행의
메뉴 부재·SDK 누락 오류 전파·공백/한글/기호 경로 검사를 추가했습니다.
이번 검증: .NET 10.0.401 솔루션 빌드 경고/오류 0, Python 정적 회귀 4개 통과,
CLI 공백 경로/종료 코드·DesktopEntry 인용/전달 실패·cproj 호환 회귀 3개 통과,
Windows 전용 3개 skip (14.167초). 현재 Linux에는 CMD, Windows PowerShell, PSScriptAnalyzer가 없으므로 Windows
실행 성공을 주장하지 않습니다. 아래 이전 검증 기록과 이번 결과를 구분합니다.

## 이전 검증 기록 (5d1bfc4)

최신 사용자 머지 `7a008bc70939918f465c6830baec6bffde86530d`를 work/current에 fast-forward 반영했습니다. main에는
push/merge하지 않습니다. 원래 18파일과 `/workspace/confectory-paused-ui-backup`
보존은 계속 유지합니다.

- 솔루션/테스트 빌드: 성공, 경고/오류 0.
- Python 정적 검사: 단일 루트 진입점, 이동 배치 호출 경로, 명시적 메뉴 분기,
  실제 EditorHome 연결, 등록 파일 대상 및 금지된 자동 설치/registry 작업 검사.
- CLI·DesktopEntry·실제 WebUI 동작 회귀: **4 passed, 0 failed, 1 skipped**
  (310.486초). CLI 공백 경로/오류 전파, 연결 명령 형식·전달 실패, manifest 호환,
  실제 EditorHome 및 ButtonGame의 Chromium 동작 통과. `/tmp/confectory-launcher-gates.log`.
- 이 환경에는 CMD/Windows PowerShell/Windows GUI가 없음. 실제 CMD 테스트는
  Windows에서만 실행하도록 추가했으며 여기서는 skip. 정적 검사를 CMD 실행
  성공으로 취급하지 않음. Windows 파일 대화상자 취소, 반복 선택, Ctrl+C,
  실제 네이티브 EditorHome, Android export 및 등록 파일 수동 import는 미검증.
- Windows 전용 테스트는 공백·한글·`&`·`!` 경로에서 잘못된 선택/미지원 안내,
  반복 메뉴, SDK 누락 오류/로그, 부모 환경 복원을 확인하도록 구성했습니다.
  실제 명령줄 실행은 Windows 인수로 명시적으로 구분합니다.

## 빌드 후 exe 실행

개발 도구의 3번 빌드 또는 `scripts/windows/internal/build-windows.bat` 실행이 성공하면
`Builds/Windows-x64/Confectory.exe`를 더블클릭할 수 있습니다. exe와 `content` 및 나머지 파일을
포함한 **결과 폴더 전체**를 함께 유지하세요. 단일 파일 배포나 설치 프로그램이 아닙니다.
이미 열린 저장소나 명령 프롬프트의 작업 위치 대신 exe 폴더를 기준으로 엔진·팩·UI·호스트를 찾습니다.
기존 결과 폴더는 유효한 Confectory 패키지일 때만 새 결과로 교체하며 이전 폴더를 `.previous-시각`으로 보관합니다.

필요한 런타임은 Microsoft .NET **Desktop Runtime 10.0 x64**와 Microsoft Edge WebView2 Runtime입니다.
사용자가 별도로 준비해야 하며 자동 설치하지 않습니다. .NET 10 SDK는 결과물을 만들거나 사용자 프로젝트를 빌드할 때 추가로 필요합니다.
기본 에디터 데이터와 시작 로그는 `%LOCALAPPDATA%/Confectory/EditorHome`에 저장하며,
기존 `CONFECTORY_HOME_STORAGE` / `CONFECTORY_ENTRY_STORAGE` 지정은 유지합니다. 사용자 계정·설정·프로젝트를 배포 폴더에 복사하지 않습니다.

명령으로 결과 폴더만 만들려면 솔루션 Release 빌드 후 저장소 루트에서 실행합니다.

```text
dotnet targets/editor-desktop/bin/Release/net10.0/Confectory.dll package . Builds/Windows-x64
```

`dotnet <결과폴더>/Confectory.dll --check-package <결과폴더>`로 구성·해시·x64 PE와 리소스 경로를 확인할 수 있습니다.
Linux에서 win-x64 apphost를 게시하고 별도 작업 디렉터리에서 패키지 엔진과 50개 웹 리소스의 시작을 검사했습니다.
실제 Windows exe 더블클릭·WebView2 창과 사용자 계정 연결은 별도 검증이 필요합니다.

배포 방식과 런타임 전제는 Microsoft의 [.NET 게시 문서](https://learn.microsoft.com/en-us/dotnet/core/deploying/)와
[WebView2 Runtime 배포 문서](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution)를 따릅니다.

A package built into an existing checkout’s `Builds/Windows-x64` reuses its existing `.confectory/editor-home` profile when present and no explicit storage override is set. Standalone distributions use the LocalAppData default. The profile stays outside the package; no user settings are copied into the ZIP. An owned checkout/profile fixture verifies reuse and unchanged sentinel bytes.

## 표준 사용자 Windows 수락 시험

처음에는 깨끗한 표준 사용자 Windows x64 계정 한 곳에서 ①을 검증합니다. 저장소 밖의
로컬 폴더에 푼 `win-x64` 묶음 전체와 승인된 기존 **.NET Desktop Runtime 10.0 x64** 및
**Microsoft Edge WebView2 Evergreen Runtime**을 사용합니다. 아래의 검토·확정·실행까지
검사하려면 [`global.json`](../global.json)이 선택할 수 있는 .NET 10 SDK x64도 필요합니다.
런타임이나 조직 정책으로 진행이 막히면 해당 단계와 오류를 기록합니다. ②부터는 별도의
승인된 시험 환경을 사용하고, 두 PC에 같은 묶음과 같은 매니페스트 해시를 사용합니다.
[Windows .NET 요구 사항](https://learn.microsoft.com/en-us/dotnet/core/install/windows) ·
[WebView2 Runtime](https://learn.microsoft.com/microsoft-edge/webview2/concepts/distribution)

표준 사용자 PowerShell에서 `$package`를 압축 해제한 실제 폴더로 바꿉니다.
`--check-package`는 파일 해시, x64 바이너리 구성과 시작 경로를 검사합니다. 출력의
`windowsExecuted: false`는 이 검사 자체의 범위입니다. 실제 첫 실행은 이어지는
`Confectory.exe`에서 확인합니다. 수락 시험에 사용할 빌드의 매니페스트 해시와 일치해야 합니다.
위치가 다른 폴더에 새 `EditorHome`과 시험 프로젝트 폴더를 두고, 그 위치를 작업 디렉터리로 실행합니다.

```powershell
$package = (Resolve-Path -LiteralPath 'C:\Test Bundles\Confectory Windows x64').Path
$lab = Join-Path $env:LOCALAPPDATA ('Confectory-Acceptance-' + [guid]::NewGuid().ToString('N'))
$env:CONFECTORY_HOME_STORAGE = Join-Path $lab 'EditorHome'
$env:CONFECTORY_ENTRY_STORAGE = $env:CONFECTORY_HOME_STORAGE
$projects = Join-Path $lab 'Projects'
New-Item -ItemType Directory -Path $projects -Force | Out-Null
Set-Location -LiteralPath $lab

dotnet --list-runtimes
dotnet --list-sdks
$checkJson = & dotnet (Join-Path $package 'Confectory.dll') --check-package $package
if ($LASTEXITCODE -ne 0) { throw 'Package check failed' }
$check = $checkJson | ConvertFrom-Json
if (-not $check.ok -or $check.rid -ne 'win-x64' -or $check.environment.CONFECTORY_UI -ne 'embedded') {
    throw 'Expected a Windows x64 embedded editor package'
}
$check
Get-FileHash -Algorithm SHA256 (Join-Path $package 'confectory-desktop-package.json')

$startEditor = { Start-Process -FilePath (Join-Path $package 'Confectory.exe') -WorkingDirectory $lab -PassThru }
$editor = & $startEditor
```

### ① 한 PC에서 만들기·논리 코드·재시작

1. Windows 에디터 창의 첫 화면에서 **나중에**를 선택합니다. 홈의 **＋ 만들기**에서
   `WinLogicAcceptance`처럼 고유한 시험 이름을 입력하고 **폴더 선택**으로 위 `$projects`를 고른 뒤
   **프로젝트 생성**을 누릅니다. Agent가 없는 시험 프로필에서는 Helper와 제안 없이
   로컬 프로젝트가 생성되어야 합니다. 별도 시험 프로필에 이미 오프라인 또는 대화 권한 없는
   Agent가 등록된 경우에는 **AI 없이 만들기**를 선택해 같은 동작을 확인합니다. 실제 Agent
   등록을 변경하지 않으며 그 시험 프로필이 없으면 해당 변형은 미실행으로 기록합니다.
2. 작업실 빈 곳의 우클릭 메뉴에서 **프로젝트 브라우저**를 엽니다. **개념** 탭에서
   `ProjectInfo`를 찾아 엽니다. 아직 등록 초안이 있으면 해당 창의 **확정**으로 검토를
   열고 **검토한 변경 Confirm**을 눌러 초기 등록을 확정합니다. 기능 전환은 저장된
   등록을 기준으로 하므로 이 확인을 먼저 마칩니다. 확인이 끝나면 `ProjectInfo` 창을 닫습니다.
   - 검색 결과가 있는 상태에서 검색 칸의 기존 검색어를 선택하고 실제 Windows 한국어 IME로
     `한글`을 직접 입력합니다. 음절이 정상적으로 조합되는지 보고, 마지막 음절이 아직 조합 중일 때 Enter를 누릅니다.
     이 Enter로는 `한글`만 확정되어야 하며 기존 검색 결과와 검색 칸의 초점이 유지되고
     항목 편집 창이 열리지 않아야 합니다. 조합이 끝난 뒤 Enter를 한 번 더 눌러 완성된
     단어로 검색되는지 확인합니다. 실제 한국어 IME를 사용할 수 없으면 이 항목은 미실행으로 기록합니다.
3. 같은 브라우저의 **기능** 탭에서 `Main`을 찾아 열고 함수 창의 **직접 작성**을 선택합니다.
   새 프로젝트의 진입 기능에는 기본 C# 본문이 있습니다. **네이티브 코드** 탭에서
   **블루프린트로 변환…**을 누르고 미리보기를 확인한 뒤 **저장**을 누릅니다. Windows
   에디터 창 안의 **논리 코드** 탭에서 시작·동작·종료가 위에서 아래로 배치되고, 동작 카드의
   **네이티브 코드 편집**이 열려야 합니다. 기본 C# 텍스트나 **블루프린트 보기**만 표시되면
   논리 코드 진입 단계의 실패 또는 미실행으로 기록합니다.
4. 같은 동작 카드에서 `return 0;` 앞에 `System.Console.WriteLine("win-local-acceptance");`을
   추가하고 **코드 저장** 후 함수 창의 **저장**을 누릅니다. **기능 완성**으로 검토를 연 뒤
   **취소**를 눌러도 원본 `main.csbody`와 `main_body.celem`이 바뀌지 않아야 합니다.
   프로젝트 채팅에 시험 문구를 쓰고, 전송하지 않은 채 Windows 에디터 창을 정상 종료합니다.
5. 같은 PowerShell에서 `$editor.WaitForExit()`를 호출하고 `$editor.ExitCode`가 `0`인지 확인합니다.
   시험 창과 엔진이 종료된 뒤 `$editor = & $startEditor`로 다시 시작합니다. 홈 목록에서 위와
   같은 프로젝트를 열어 미전송 채팅과 저장한 논리 코드 카드 입력이 복원되는지 확인합니다.
   같은 `Main`에서 카드를 다시 열어 시험 문구를 확인합니다.
6. 컴파일과 실행도 검증할 때는 **기능 완성**으로 재검토한 뒤 **검토한 변경 Confirm**을 누르고
   `▶`로 실행합니다. 실행 로그에서 `win-local-acceptance`와 종료 코드 `0`을 확인합니다.
   초대 없이 시작한 뒤, 프로젝트를 열었을 때, 실행하는 동안 작업 관리자의 시험 에디터·엔진
   PID를 `netstat -ano`와 대조합니다. 사설망 또는 와일드카드 TCP 수신 소켓이 없어야 합니다.
   로컬 루프백은 따로 기록합니다.

검토에서 대상 선택이 열리면 `windows`를 고릅니다. 추가 변경 확인이 요구되면 **고급 검토 · 소스 변경 보기**에서
변경 목록을 확인한 뒤 확인란을 선택합니다.

### ② 같은 사설 LAN에서 두 PC

1. 승인된 같은 사설망에서 PC A는 에디터로 직접 만든 프로젝트를 엽니다. PC B는
   자체 폐기용 프로젝트를 엽니다. 초대 창을 열기 전에 양쪽에서 자기 프로젝트의 보이는
   편집창 안을 `Ctrl+Y`로 드래그해 LaY를 만들고 `설명 적용` 후 `확정`으로 봉인합니다.
   각 PC의 기존 Chat 입력에 서로 다른 미전송 문구를 적습니다. A의 Chat에서 `LAN 채팅
   초대`를 열고 발급 전 닫아 봅니다. 리스너가 생기지 않고 기존 문구를 이어 쓸 수 있어야 합니다.
2. A에서 두 PC의 사설 IPv4를 입력해 `일회용 초대 발급`을 누릅니다. B는 프로젝트
   메뉴의 `LAN 초대 참가`에서 A가 직접 전달한 초대 텍스트와 시험 이름을 입력합니다. `연결 대상 확인`
   화면에서 호스트 주소·프로젝트·인증서 지문을 A의 시험 정보와 대조합니다. 참가 전
   `닫기`로 취소하고 입력을 계속 편집할 수 있는지 확인합니다. 5분 안에 같은 초대로
   다시 검토하여 `이 프로젝트에 참가`가 가능한지 확인합니다. A는 초대 창을 유지합니다.
3. B의 첫 공용 목록은 비어 있어야 합니다. 양쪽에서 구분되는 텍스트로 `공용으로 보내기`를
   누릅니다. 공용 작성란의 `봉인 YogiBox 첨부` 뒤 취소하면 공용 행이 생기지 않아야 합니다.
   다시 첨부해 명시적으로 보낸 뒤 상대쪽 `YogiBox 보기`에서 전송 당시 선택 영역과 설명을 확인합니다.
   B에 호스트 프로젝트 편집이나 EY 열람 권한이 생기지 않아야 합니다.
4. B가 떠난 뒤 이미 쓴 초대는 거절되어야 합니다. A의 초대 창을 닫아 연결과 수신이
   끝나는 것을 확인하고 새 초대로 B를 합류시킵니다. 이전 글과 첨부는 보이지 않아야
   합니다. A를 재시작하면 공용 이력은 A의 `EditorHome\project-chat`에 남아 다시 열려야
   합니다. B 재시작 뒤에는 B가 보낸 글과 첨부까지 포함해 공용 기록이 없어야 합니다.
   두 PC의 비공개 초안은 유지되고 공용 글이 `helper-conversations`에 들어가지 않아야 합니다.
   B에서 A의 폐기용 프로젝트 복사본을 열어도 그 복사본으로 초대를 발급할 수 없어야 합니다.

### ③ 사전 신뢰가 구성된 격리 중계

일반 패키지는 중계를 구성하지 않으므로 시험용 인터넷 초대 메뉴가 숨겨져 있어야 합니다.
서로 직접 라우팅되지 않는 두 시험망과, 호스트·참가 역할 및 중계 TLS 신뢰가 사전에
구성된 승인된 Windows 시험 호스트가 있는 경우에만 진행합니다. 기존 격리 fixture는
[Linux 편집기 시험](../tests/packs/editor_local_chat_development.py)을 위한 것입니다.
Windows 시험 호스트가 없으면 이 단계는 미실행입니다.

호스트의 `인터넷 채팅 초대 (시험)`과 참가자의 `인터넷 초대 참가 (시험)`에서 ②와 같은
텍스트·LaY·취소 후 포커스·권한·저장·재입장 검사를 합니다. 연결 대상 확인에는 사전
설정된 시험 중계와 원본 호스트·프로젝트가 표시되어야 합니다. 초대가 사전 설정과
일치하지 않거나 만료·재사용된 경우 참가가 거절되어야 합니다. `초대 철회 및 연결 종료`
후에는 공용 연결이 끝나야 합니다. 중계 자격과 프로젝트 초대는 서로 다른 시험 자격으로
취급합니다.

각 단계의 성공·실패·미실행, 빌드 커밋과 매니페스트 해시, Windows·.NET·WebView2 버전을
기록합니다. 시작 오류는 폐기용 `EditorHome\logs\launch-*.log`에서 해당 오류만 확인합니다.
초대 텍스트와 시험 중계 자격은 시험 기록에 남기지 않습니다.

### 2026-11-24 교차 패키지 확인

엔진 기준 `a1e3e81f48b1e5c78bb85cc506cd6e085e439e96`에서 Release `win-x64` 묶음을
생성했다. 저장소 밖 작업 디렉터리에서 `--check-package`가 2,857개 파일의 해시와 x64 PE,
묶음 내부의 WebView2 호스트 및 `embedded` 시작 경로를 확인했다. 이 결과물의
`confectory-desktop-package.json` SHA-256은
`e9cdd6734ec034e7d2f11e1be818143bf3620afeaffdf06511a1fc62f9e5d18d`다.

[패키지 회귀](../tests/probes/desktop_package.py)는 변조·누락 파일의 거절과 Linux에서 SDK 없는
런타임으로 묶음의 관리 엔진·Chromium 시작 및 등록된 웹 리소스 309개의 바이트를 확인했다.
Windows `Confectory.exe`와 내장 WebView2는 실행하지 않았다. 위 ①의 첫 시작·프로젝트 생성·
수직 셀 편집·정상 종료·최근 프로젝트 재열기와 ②·③의 Windows 실행은 실기 확인 대기다.
