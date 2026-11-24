# Linux 편집기 배포 결과물 첫 실행 검증

2026-11-24에 `work/current`의 `1e2735c5721cb4b02ac5dacbc868ee8fcb087b22`를 검증했다.

## 현재 배포 경로

[`DesktopPackage.Build`](../targets/editor-desktop/DesktopPackage.cs)는 `win-x64` 패키지를 만들고 [`PackageLayout.Check`](../targets/editor-desktop/PackageLayout.cs)도 이 RID만 받는다. Linux에서 문서화된 [`run-home.sh`](../examples/editor-home/run-home.sh)는 체크아웃에서 솔루션과 EditorHome을 빌드하는 경로다. [DotNet의 `linux` 빌드 타깃](../targets/dotnet/Program.cs)이 만드는 `run`은 같은 폴더의 `Confectory.App.dll`을 실행하는 프레임워크 종속 런처다.

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

## 확인된 배포 경계

[`CreateSession`](../packs/editor-home-model/CreateSession.csbody)은 GTK 창을 만들기 전에 콘텐츠 루트의 `targets/dotnet/pack.cpack`을 확인한다. 생성된 Linux 런타임 폴더에는 이 파일과 편집·빌드에 필요한 도구가 없다. SDK 설치만으로는 해결되지 않는다. 독립 Linux 편집기 배포를 검증하려면 편집기에 필요한 콘텐츠와 Release 도구를 포함하는 패키저, 설치 위치를 콘텐츠 루트로 전달하는 런처, 쓰기 가능한 사용자 프로필 위치가 먼저 정의되어야 한다.
