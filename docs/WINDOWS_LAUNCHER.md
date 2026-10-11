# Windows 시작 파일: Confectory.bat

저장소 루트의 **Confectory.bat 하나**를 엽니다. 기존 .NET 10 SDK와 Windows에
있는 Windows PowerShell을 사용하며, 도구를 설치하거나 전역 환경변수/setx를
설정하지 않습니다. `CONFECTORY_DOTNET`을 이미 지정했다면 해당 실행 파일을
사용하고, 아니면 PATH의 `dotnet`을 사용합니다.

| 선택 | 실제 동작 |
| --- | --- |
| 1 | 솔루션을 빌드하고 실제 `examples/editor-home/project.cpack`의 현재 네이티브 에디터 실행. 파일 인수가 있으면 기존 DesktopEntry의 같은 인스턴스 전달/metadata-only 열기 사용. |
| 2 | 창 내부 HTML 에디터가 아직 미구현임을 안내. 빌드·브라우저·서버·설치 작업 없음. |
| 3 | 솔루션/도구 빌드만 실행. 사용자 프로젝트 실행 없음. |
| 4 | 기존 Android exporter로 **unsigned** 내보내기. 기존 JDK/Android SDK/workload가 필요하며, 없으면 실패 진단. 설치·키 생성·서명 없음. 파일 선택 취소 가능. |
| 5 | `.confectory/Confectory.cproj.reg` 생성만 수행. 내용을 검토한 뒤 사용자가 직접 import해야 하며, 런처는 레지스트리를 변경하지 않음. |
| 6 → 1 | 개발 진단: 선택한 프로젝트에 대해 **외부 브라우저** WebUI 기반 화면 실행. `CONFECTORY_UI=web`, `CONFECTORY_WEB_PROJECT`를 자식 프로세스에 설정해 실제 EditorHome 팩 실행. 구웹데모를 실행하지 않음. |
| 0 | 종료. 잘못된 선택, 진단 메뉴에서 뒤로 가기, 입력 종료는 빌드를 시작하지 않음. |

기본 에디터는 현재 네이티브 UI입니다. 개발 진단의 HTML 화면은 객체 조회와
공유 초안 편집/Save까지의 기반이며, Sites 전체 에디터나 창 내부 WebView가
아닙니다. 출력된 localhost URL을 브라우저로 열고 호스트를 유지해야 합니다.
Ctrl+C로 호스트를 종료할 때 메뉴까지 종료된다면 Confectory.bat를 다시 엽니다.
Windows 콘솔에서 이 동작은 아직 직접 검증되지 않았습니다.

작업이 끝나거나 실패하면 진단을 읽고 Enter로 메뉴로 돌아갑니다. 각 작업은
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
- `scripts/windows/launcher.ps1`: 새 메뉴와 작업 실행.

모든 이동은 Git rename으로 추적하며 원본 팩과 사용자 데이터는 삭제하지 않습니다.
내부 배치는 위치에서 `../../..`를 계산하고 호출/문서/테스트 참조도 갱신했습니다.
기존 체크포인트 문서의 직접 실행 경로는 역사적/진단용입니다. 일반 사용자는
루트 Confectory.bat를 사용합니다.

새 파일 연결 등록 파일은 `Confectory.bat "%1"`을 가리킵니다. 파일을 눌러도
메뉴 선택 전에는 빌드나 실행이 없습니다. **이미 Windows 레지스트리에 저장된
옛 `open-project-windows.bat` 경로는 자동 변경할 수 없습니다.** 기존 설치는
새 메뉴 5로 등록 파일을 생성·검토하고 직접 적용해야 합니다. 이전에 저장한
바로 가기도 새 루트 진입점으로 변경합니다. 사용자 PC/레지스트리는 건드리지
않았고, 제거한 루트 경로에 두 번째 사용자용 호환 런처를 남기지는 않았습니다.

## 창 내부 HTML 연결 조사 — 구현하지 않음

현재 `packs/web-ui/Client.csbody`의 `WebView`는 JS 상태/요청 클라이언트이며 OS
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

## 검증 기록

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
