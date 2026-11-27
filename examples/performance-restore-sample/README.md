# 여러 창 복원 성능 시험 (Windows)

40개의 합성 객체만 포함된 로컬 시험용 프로젝트입니다. 실제 프로젝트, 계정 로그인,
PowerShell, Run/Build 또는 네트워크 서비스는 필요하지 않습니다.
.NET Desktop Runtime 10.0 x64 및 Edge WebView2 Runtime은 설치된 상태여야 합니다.

## 첫 실행: 창 준비

1. 다른 Confectory 창을 정상 종료하고 `Confectory-performance-restore-sample.bat`를 더블 클릭합니다.
   이 배치는 `%LOCALAPPDATA%\Confectory\PerformanceRestoreSample-v1`에만 처음 복사합니다.
   기존 PerformanceSample-v1과 일반 편집기 프로필은 변경하지 않습니다. 시작 화면이 뜨면 **나중에**를 선택합니다.
2. Home의 **열기**로 배치에 표시된 `project.cpack`을 엽니다.
3. 프로젝트 메뉴(≡) → **프로젝트 브라우저**. 개념 목록에서 `Sample D` 검색 후
   우클릭 → **스키마 열기**. Count 입력칸이 편집 가능한지 확인합니다.
4. `Sample A`, `Sample B`, `Sample C`를 각각 검색하고 우클릭 → **새 창으로 열기**.
   A를 처음 연 직후 창을 닫았다가 검색 결과에서 Enter로 다시 열어 재열기도 기록합니다.
   그런 뒤 B/C를 열어 네 속성 창을 모두 남깁니다. Count는 바꾸지 않아도 됩니다.
5. 프로젝트 제목 메뉴 → **프로젝트 도구**에서 **개념 맵**, **빌드 작업**,
   **의미 편집 이력**을 각각 엽니다. **빌드 작업**은 패널을 여는 것만이며 실행 버튼은 누르지 않습니다.
   브라우저 + 기본 속성 창 + 독립 속성 창 3개 + 도구 창 3개 = 총 8개입니다.
6. 창을 그대로 두고 앱 오른쪽 위 X로 정상 종료합니다. 강제 종료하지 않습니다.

## 두 번째 실행: 실제 냉간 복원

1. 같은 배치를 더블 클릭합니다. Home에서 이 샘플 프로젝트 카드의 객체 수가 40으로
   표시될 때까지 기다립니다(홈 요약 경쟁과 냉간 복원을 분리합니다).
2. 카드를 한 번 클릭합니다. 네 속성 창에서 Count/Note에 커서가 들어가는지 차례로 확인합니다.
   마지막 창 이후 ≡ → 프로젝트 브라우저를 클릭하고 `Sample A` 검색을 확정하여 결과가 보이는지 확인합니다.
3. 앱을 정상 종료합니다. 0창/1창 비교를 원하면 실제 창을 닫고 해당 수만 남긴 뒤 같은 절차를 반복합니다.
   기존 샘플 파일을 덮어쓰거나 사용자 프로젝트를 열 필요가 없습니다.

## 기록 읽기 (자동 업로드 없음)

배치 종료 후 열리는 성능 폴더의 이번 두 실행 폴더에서 `engine.jsonl`과 `webview.jsonl`을
직접 검토합니다. 다른 일반 런처 로그, 전체 폴더, 프로필, 프로젝트 파일, 경로 또는 실제 사용자 데이터를 공유하지 않습니다.
필요하면 아래 고정 이벤트의 `elapsedMs` 숫자만 전달해도 됩니다.

- `restore-workspace-ready`, `restore-first-editable`, `restore-last-editable`: 실제 Home 카드 클릭 이후 작업 공간 입력 / 첫 번째 / 마지막으로 표시된 편집 가능 속성. 0창 또는 복원 실패에는 마지막 속성 이벤트가 없을 수 있습니다.
- `restore-commands-ready`: 메뉴가 첫 활성화된 순간의 근사치. 실제 명령 성공이나 계속 활성화된다는 보장은 아닙니다.
- `browser-open-ready`, `browser-search-ready`: 사용자가 실제 브라우저 항목을 선택하거나 검색 확정한 순간부터 편집 가능한 검색 UI / 실제 결과가 표시될 때까지. 사용자가 카드 클릭 후 기다린 시간은 포함하지 않습니다.
- `window-ready / openEditorView`, `window-ready / reopenEditorView`: 일반 속성 창 열기와 재열기.
- `consumer`, `invoke-queue`, `authoring-process`, `authoring-stream`, `embedded-request`는 엔진 구간; `webview-init`, `webview-message`는 네이티브 WebView2 호스트 구간입니다.
- `input-delay`, `input-frame`은 입력 전달과 브라우저 프레임 근사치입니다. WPF 전체 화면 제시 시간과 GPU/OS 스케줄링을 독립적으로 측정하는 것은 아닙니다.

모든 이벤트는 고정 이름과 숫자로만 기록됩니다. 누락 이벤트를 성공으로 해석하지 마세요.
