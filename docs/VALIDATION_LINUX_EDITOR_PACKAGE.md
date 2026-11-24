# Linux 편집기 배포 결과물 첫 실행 검증

## Linux x64 독립 패키지

Linux x64 빌드 호스트에서 .NET 10 SDK로 필요한 Release 도구를 빌드한 뒤
기존 데스크톱 패키저의 명시적 `linux-x64` 대상을 사용한다.

```sh
for project in \
  targets/dotnet/Confectory.Build.DotNet.csproj \
  targets/element-authoring/Confectory.ElementAuthoring.csproj \
  targets/project-execution-host/Confectory.ProjectExecutionHost.csproj \
  src/Confectory.Cli/Confectory.Cli.csproj \
  targets/editor-desktop/Confectory.EditorDesktop.csproj
do
  dotnet build "$project" -c Release || exit
done
dotnet targets/editor-desktop/bin/Release/net10.0/Confectory.dll package . Builds/Linux-x64 linux-x64
```

묶음 전체를 실행 권한을 보존하는 방식으로 풀고 `./run`을 실행한다.
`./run --check-package`는 파일 체크섬과 필수 구성 요소를 검사한다.
런처는 묶음의 `content`를 사용하고 외부 체크아웃을 찾지 않는다.
기본 사용자 데이터는 `$XDG_DATA_HOME/Confectory/EditorHome` 또는
`~/.local/share/Confectory/EditorHome`에 둔다. 묶음 디렉터리는 읽기 전용으로 둬도 된다.

시작에는 Linux x64, X11 세션, GTK 3, GtkSourceView 4와 **.NET 10 x64 런타임**이 필요하다.
컴파일러를 사용하는 Review·Confirm 및 Build·Run에는 **.NET 10 SDK**가 추가로 필요하다.
`dotnet`을 PATH에서 찾을 수 있게 하거나 `CONFECTORY_DOTNET`에 실행 파일을 지정한다.
런처는 시스템 의존성을 설치하지 않는다.

대상을 생략한 `package` 명령은 기존 Windows x64 패키지를 만든다.
체크아웃에서 개발할 때는 계속 `examples/editor-home/run-home.sh`를 사용할 수 있다.

### 수직 셀 논리 코드

1. 묶음의 `./run`으로 GTK 창을 연다. 로컬 프로젝트를 만들거나 최근 목록에서 연다.
2. 프로젝트 제목 메뉴의 **Open Logic Code in Browser**를 누른다. GTK 편집기가 프로젝트를 닫은 뒤 기본 브라우저가 같은 프로젝트의 실행 진입 함수를 연다.
3. 같은 프로젝트의 GTK 작업공간으로 돌아가려면 작은 **Confectory - Logic Code** 창의
   **Return to GTK**를 누른 뒤 브라우저에서 **GTK로 돌아가기**를 확인한다.
   복귀는 현재 작업실 상태와 미전송 채팅을 저장하고 브라우저 세션을 정리한 뒤 GTK를 연다.
   **계속 편집**을 선택하면 브라우저에 남는다. 열린 검토나 처리 중인 저장·미적용 입력은 안내에 따라 처리한 뒤 다시 요청한다.
4. 작은 세션 창의 닫기 버튼은 로컬 편집 세션을 종료한다. 브라우저 탭을 닫아도 GTK로 자동 복귀하지 않는다.

이 메뉴는 실행 진입 함수가 선언된 로컬 프로젝트에서 사용한다.
미적용 소스나 속성 입력이 있으면 먼저 저장하거나 되돌린다. 진행 중인 작업은 기존 프로젝트
닫기 확인을 따른다. 전환 자체는 소스를 확정하거나 실행하지 않는다.
새 프로젝트의 초기 등록 초안이 진입 함수 읽기를 막으면, 원래 검토 화면에서 초안을 확정한 뒤
함수 창의 **진입 기능 다시 읽기**를 선택한다.
기본 브라우저가 없으면 현재 GTK 프로젝트가 열린 채로 유지된다.
브라우저 실행이 실패하거나 시스템이 열기 요청을 수락한 뒤 20초 안에 로컬 세션에 연결되지 않으면,
세션과 임시 파일을
정리한 뒤 같은 프로젝트와 미전송 채팅 초안을 GTK에서 다시 연다.
원래 프로젝트의 신원을 확인할 수 없으면 최근 목록으로 돌아간다.
자동으로 브라우저를 열기 어려운 환경에서 논리 코드를 계속 쓰려면 GTK를 닫고
`./run --logic-code`를 실행할 수 있다.
터미널의 `CONFECTORY_WEB_UI` 뒤에 표시된 주소 전체를 같은 컴퓨터의 브라우저에서 열고,
최근 목록에서 프로젝트를 선택한다. 이 대안 경로는 터미널에서 Ctrl+C로 종료한다.

기존 루프백 호스트의 `127.0.0.1` 임시 포트와 세션 검사를 사용한다.
자동 전환에서 OS에 전달하는 값은 사용자 전용 임시 파일의 위치이며, 세션 주소를 담은
파일은 브라우저 인증 후 또는 종료 때 제거된다.

[`editor_linux_package_logic_x11.py`](../tests/gui/editor_linux_package_logic_x11.py)는 아래 GTK 시험과
같은 로컬 이미지·Xorg·SDK에 Chromium과 Playwright를 더해 진입을 검증한다.

```sh
python tests/gui/editor_linux_package_logic_x11.py Builds/Linux-x64 "$FIXTURE_IMAGE" --switch
```

`--switch` 시험은 압축에서 푼 읽기 전용 묶음과 빈 HOME, 비관리자 UID, 외부 연결을
차단한 컨테이너를 사용한다. 시험용 기본 브라우저 핸들러는 OS가 실제 전달한 임시 파일을
Chromium 검증에 넘긴다. 실제 GTK로 만든 두 프로젝트 중 현재 열린 프로젝트만 전달됐다.
기본 브라우저가 없거나 GTK 소스에 미적용 입력이 있으면 GTK 창이 유지됐다.
초기 등록 검토 뒤 진입 기능의 수직 카드 수정·검토 취소·확정·실행이 통과했다.
`0e33a1e1`의 실제 패키지에서는 검토 중 복귀 차단, 복귀 취소 및 명시 복귀도 확인했다.
같은 프로젝트 ID와 경로에서 GTK가 미전송 채팅을 복원했다. 미확정 카드는 재시작한 논리 코드에서
열렸고 GTK와 브라우저는 확정본을 실행했다. 다른 프로젝트는 그대로였고,
인증 후 임시 파일과 종료 뒤 루프백 리스너가 제거됐다.
옵션 없이 실행하면 별도의 CLI 경로를 검사한다.

```sh
python tests/gui/editor_linux_package_logic_x11.py Builds/Linux-x64 "$FIXTURE_IMAGE" --browser-failure
```

`--browser-failure`는 기본 브라우저가 없는 경우, 실행할 수 없는 등록 핸들러,
시작 직후 종료하는 등록 핸들러를 별도 확인한다. 두 실패는 원 프로젝트의 GTK 복귀,
다른 프로젝트의 등록 파일 보존, 임시 파일과 리스너 정리, 미전송 초안을 계속 편집한 뒤
정상 종료·재시작하면 같은 값이 보이는지를 검사한다.
실제 Chromium 편집·검토·확정·실행은 `--switch`에서 확인한다.

### 설치 사용자 회귀 시험

[`editor_linux_package_x11.py`](../tests/gui/editor_linux_package_x11.py)는 위 결과 폴더와
[기존 GTK 시험 이미지](../tests/gui/editor_lan_chat_x11.py)를 받는다. 전용 Xorg와
컨테이너에서도 유효한 `XAUTHORITY`, 설치된 SDK의 `CONFECTORY_DOTNET`을 지정한다.

```sh
python tests/gui/editor_linux_package_x11.py Builds/Linux-x64 "$FIXTURE_IMAGE"
```

이 시험에서는 소스 체크아웃이나 캐시를 마운트하지 않고 압축에서 푼 묶음만
읽기 전용으로 제공한다. 앱은 UID 1000과 빈 HOME, 네트워크가 없는 두 컨테이너에서
실제 GTK 창으로 실행한다. 런타임만 있으면 시작과 로컬 프로젝트 생성은 되고,
Run은 SDK 요구 사항을 화면에 표시한다. SDK가 있으면 '나중에', 프로젝트 생성,
GTK Source 편집, Review 취소와 명시적 Confirm, Run 순으로 확인한다.
완전 종료 후에는 최근 프로젝트에서 확정한 Source와 미전송 초안을 복원하고 다시 Run한다.
이번 깨끗한 Linux 빌드 결과에서 매니페스트에 기록된 2,802개 파일을 확인했고,
런처의 실행 권한 유실과 번들 파일 변조는 검사에서 각각 거부됐다.
기본 Windows x64 명령도 별도로 교차 패키징했으며 PE 및 WebView2 구성을 확인했다.
GTK 설치 사용자 회귀 시험은 Source 편집을 사용한다. 수직 셀 논리 코드는 위의 별도 브라우저 시험에서 확인했다. Windows 실기는 미실행이다.

## 독립 Linux 패키지 도입 전

2026-11-24에 `work/current`의 `1e2735c5721cb4b02ac5dacbc868ee8fcb087b22`를 검증했다.

[`DesktopPackage.Build`](../targets/editor-desktop/DesktopPackage.cs)는 당시 `win-x64` 패키지만 만들었고 [`PackageLayout.Check`](../targets/editor-desktop/PackageLayout.cs)도 이 RID만 받았다. 당시 Linux에서 문서화된 [`run-home.sh`](../examples/editor-home/run-home.sh)는 체크아웃에서 솔루션과 EditorHome을 빌드하는 경로다. [DotNet의 `linux` 빌드 타깃](../targets/dotnet/Program.cs)이 만드는 `run`은 같은 폴더의 `Confectory.App.dll`을 실행하는 프레임워크 종속 런처다.

고정 SHA의 소스를 `git archive`로 별도 디렉터리에 풀고 빈 SDK 홈과 NuGet 디렉터리에서 CLI와 DotNet 빌드 도구를 Release로 빌드했다. 편집기 엔진 캐시 없이 아래 명령을 실행했다. 결과 디렉터리를 압축해 다른 위치에 푼 뒤 `run`과 `public-linkage.json`을 포함한 88개 파일의 SHA-256을 원래 빌드 결과와 대조했다.

```sh
dotnet build src/Confectory.Cli/Confectory.Cli.csproj -c Release
dotnet build targets/dotnet/Confectory.Build.DotNet.csproj -c Release
dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux
```

| 일반 사용자 격리 환경 | 실제 결과 |
| --- | --- |
| 압축에서 푼 런타임 결과물과 .NET 10.0.12 런타임 | 번들 `run`이 `Confectory repository required` 예외로 종료되어 첫 GTK 창에 도달하지 못했다. |
| 같은 결과물과 .NET 10 SDK 10.0.401 | 새 HOME에서 같은 예외가 발생했다. |
| 같은 결과물과 설치 의존성을 공급한 대조군 | 실제 GTK 첫 실행, Source 편집·확정, 두 차례 실행, 앱 종료·재시작 후 최근 프로젝트 재열기를 통과했다. |

모든 실행은 Linux x86-64에서 UID 1000, 별도 HOME과 무관한 작업 디렉터리, Docker `--network none`, 개발 체크아웃과 빌드 캐시 미마운트 상태로 수행했다. 실제 GUI에는 로컬 Xorg와 GTK 3.24.49, GtkSourceView 4.8.4, X11 라이브러리를 사용했다. 런타임 전용 케이스에서 `dotnet --list-sdks`의 출력은 비어 있었다.

## 대조군에서 확인한 동작

대조군에는 별도로 만든 읽기 전용 콘텐츠 디렉터리를 연결했다. 사용한 빌드의 팩과 `targets/dotnet/pack.cpack`, Release DotNet·ElementAuthoring·ProjectExecutionHost·CLI를 해당 디렉터리에 넣었다. `CONFECTORY_EDITOR_REPO`는 그 콘텐츠를 가리켰고, 프로필과 프로젝트는 테스트 사용자의 HOME에 두었다. 실행에는 위에서 압축 해제한 `run`을 그대로 사용했다. 프로젝트 컴파일에는 기존 요구사항인 .NET 10 SDK가 필요했다.

실제 GTK에서 ‘나중에’를 선택하고 폴더 선택기로 프로젝트를 만들었다. 기존 Source 편집기에서 `Main`의 C# 본문을 수정했다. Save와 검토 취소 시 원본을 보존했고, 명시적으로 확정한 뒤 Run이 새 코드의 결과를 기록했다. 창을 정상 종료한 뒤 새 프로세스의 최근 목록에서 같은 프로젝트를 열었고, 확정한 C#과 전송하지 않은 로컬 채팅 초안을 다시 확인했다. 이전 실행 결과 파일을 지운 뒤 두 번째 Run이 새 결과를 작성했다.

이 대조군의 편집 범위는 GTK Source다. 논리 코드 탭의 검증은 앞서 [Linux Chromium 흐름](../tests/gui/editor_local_first_workflow.py)에서 수행했다. 이번 대조군은 공식 Linux 배포물의 성공으로 집계하지 않는다. Windows 교차 패키징과 실기 실행은 이번 시험에 포함하지 않았다.

## 도입 전 확인된 배포 경계

[`CreateSession`](../packs/editor-home-model/CreateSession.csbody)은 GTK 창을 만들기 전에 콘텐츠 루트의 `targets/dotnet/pack.cpack`을 확인한다. 생성된 Linux 런타임 폴더에는 이 파일과 편집·빌드에 필요한 도구가 없다. SDK 설치만으로는 해결되지 않는다. 독립 Linux 패키지에는 이 콘텐츠와 Release 도구, 설치 위치를 콘텐츠 루트로 전달하는 런처, 묶음 외부의 사용자 프로필이 필요했다.
