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

1. 묶음의 `./run`으로 GTK 창을 열고 ‘나중에’를 선택한다. 새 로컬 프로젝트를 만들고 GTK 창을 닫는다.
2. 같은 묶음에서 `./run --logic-code`를 실행한다. 터미널의 `CONFECTORY_WEB_UI` 뒤에 표시된 주소 전체를 같은 컴퓨터의 브라우저에서 열고, 최근 목록에서 프로젝트를 선택한다.
3. 작업을 마치면 런처를 실행한 터미널에서 Ctrl+C로 에디터를 종료한다.

브라우저 경로에는 설치된 브라우저가 필요하다. 현재 새 프로젝트의 폴더 선택은 GTK에서 한다.
두 화면은 같은 로컬 프로필과 최근 목록을 쓰므로 한 화면을 닫고 다른 화면으로 전환한다.
논리 코드 모드는 기존 루프백 호스트의 `127.0.0.1` 임시 포트와 세션 검사를 사용한다.
터미널에 표시된 주소는 현재 세션에만 사용한다.

[`editor_linux_package_logic_x11.py`](../tests/gui/editor_linux_package_logic_x11.py)는 아래 GTK 시험과
같은 로컬 이미지·Xorg·SDK에 Chromium과 Playwright를 더해 두 진입점을 이어서 검증한다.

```sh
python tests/gui/editor_linux_package_logic_x11.py Builds/Linux-x64 "$FIXTURE_IMAGE"
```

압축에서 푼 읽기 전용 묶음, 빈 HOME, 비관리자 UID와 외부 연결을 차단한 컨테이너를 사용했다.
GTK에서 실제 폴더를 골라 프로젝트를 만들었고, GTK가 열려 있는 동안 같은 설치의 논리 코드
모드는 시작이 거절됐다. GTK 종료 후 Chromium의 최근 목록에서 그 프로젝트를 열었다.
실제 화면에서 기본 `Main`을 수직 셀로 변환하고 본문 카드 수정·Save·검토 취소·확정·실행을
통과했다. 새 호스트와 브라우저를 실행해 같은 카드를 확인하고 같은 결과를 다시 생성했다.
세션 키 없는 요청은 거절됐고, 브라우저 모드의 리스너는 루프백 하나였으며 종료 후 사라졌다.

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
GTK 논리 코드 탭과 Windows 실기 실행은 이번 시험 범위 밖이다.

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
