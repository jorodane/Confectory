# V666 소유 모듈 직접 필요 기능 검색 검증

제품·검사·도구 동결 `ba629cd66c8e319c1ddf332679753f94be60c277` 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V9_FINDER_MODULES.md)·[정확한 delta](v666-finder-modules-delta.json)를 따른다.

## 원본 대조·재현·구현

보관 v666 `dist/app.js:4000–4003`의 원본 `workspaceSearchText`를 원래 모듈의
`methods[].name` 모양에 실행했고 직접 기능 이름이 검색됨을 확인했다. 같은 파일의
2641–2643행은 직접 기능을 그 이름으로 표시한다. native의 대응은 직접 소유 모듈이
명시한 `require` 기능 이름이다. 상속의 표시와 직접 선언 저장 모양을 혼동하지 않는다.

게시 패키지 `6033c5e`의 실제 엔진에서 기능 이름으로 찾으면 기능 자체만 나오고 그
모듈은 빠졌다. 같은 모듈을 기존 인터페이스 편집기로 열면 해당 이름이 표시됐다.
당시 게시 `0d364f2`와 제품 소스가 동일하고 문서만 다름을 확인했다. 생성 fixture와
전체 무결성을 확인한 보관본을 사용했으며 사용자 프로젝트·파일은 사용하지 않았다.

기존 TableCommand finder-content의 정의 배열에 관측된 소유 모듈 직접 require의 짧은
기능 이름만 추가했다. 외부/부모/포함 모듈이나 다른 기능을 새로 읽거나 펼치지 않는다.
공개 read payload/모양·owner/kind/namespace·source/revision/hash 전후 확인·기존 색인
예산/부분 표시를 유지한다. source path·private 세션/뷰 식별자·본문을 추가 투영하지 않는다.
일반 Browser/Data API·UI/자산/CSS·Core/targets·계약/사용자 C# 본문·ID/연결·권한·원자 Save·
Review→Confirm·최종 CAS·기존 Undo는 바꾸지 않는다. 제품 delta는 한 삽입뿐이다.

## 최종 검증

독립 LF 13·CRLF 13·새 패키지/전체 복원/실패 수명관리 7,
**총 33단계(신규 33·재사용 0)** 통과했다. 최종 동결 코드의 Git
객체·EOL·NuGet/home·engine cache를 독립시켰다. 재현/과거 검증은 최종 합계에 넣지 않는다.

- 실제 Linux .NET/Chromium에서 직접 필요 기능으로 모듈과 기능을 찾았다. 포함 모듈의
  요구 이름/부모 설명은 그 소유 원본 결과에만 나오며 다른 모듈에 합쳐지지 않았다.
  빈 모듈의 빈 결과, 외부 ID·중복/과다 ID·추가 path 필드 거절과 현재 선택·개인 입력을 확인했다.
- 생성 fixture의 off-page 공유 초안에서 요구 기능을 바꾼 뒤 열린 색인이 갱신됐다.
  기존 Undo/Redo도 반영되고 결과는 정확한 qualified 모듈의 원래 인터페이스를 열었다.
  이러한 명시 fixture 편집과 찾기의 read-only 동작을 구분하며 물리 원본은 미변경이었다.
- 모듈 검색어는 cold에서 복원되지 않으며 동일 namespace/ID의 다른 프로젝트에서
  이전 요구 이름을 채택하지 않았다. 원래 실제 Data/필드·함수 서명·종류 이름 검색 회귀,
  지연된 read·검색어 변경·Enter·Esc/닫기·읽기 실패/명시 재시도·개인 입력 보존도 확인했다.
  지연/실패는 로컬 fetch 주입이며 실제 네트워크 장애를 시험한 것은 아니다.
- 새 Windows 교차 패키지의 구조/무결성과 패키지 managed engine의 정상 검색/Undo/
  정확한 열기를 확인했다. 전체 SHA/CRC/모드로 복원한 엔진에서 모듈 cold/프로젝트 격리와
  지연/실패 read 수명을 다시 확인했다. 실제 Windows apphost/WebView2 실행은 아니다.
- 기존 소유 임시물 수명관리의 성공·실패·예외, 증거 보존·자식 종료·정리를 확인했다.
  실제 계정/AI/키·유료 호출·외부 접근 부여·source Save/Confirm은 검색에 추가하지 않았다.

재현 record `/workspace/artifacts/v536-verification-managed/runs/4b62755e22da4302a33127a5a13b87a0.json`, 증거 SHA `6582e8fd7e423cdb70fd25b01d7048db4f2cb7316740a6384eef7ea877d20312`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/da95387654ad4ccaa3fd5c29b3c3feda.json`

증거 `/workspace/artifacts/v536-verification-managed/runs/da95387654ad4ccaa3fd5c29b3c3feda.zip`

SHA `0bc18c451fd74b9f2b074f7f9eba12206f1893ef751b464acad86b37fc8e1afc` (5.07MiB).

## 보관·공간·고정 잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `ba629cd66c8e319c1ddf332679753f94be60c277`, `4d08bbf6ef0f06181022506e03100ba8567a70b5846ebcd68a721a28fec26eba.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `255ff7deb220ab605bcb45b91fc3b4fa78827ca642b86f017fa0d3ce74cbc9f8`.

- rollback: `6033c5eb0bfffad4733527fefa3c272e24e07e57`, `b4ebc2e6a2efc61432ac9ac275e68f84c056a96ecb501cd8a68f56cd10a50046.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `68597e2752695cd08ba57fe5fc3cf7b3b57d4c590366a8ecd55d9c3beb057978`.

최신/롤백·증거의 전체 SHA/manifest를 재확인했다. 승인된 저장소의 원자 승격·2세대
수명과 해당 실행 소유 임시물의 확인된 정리만 수행했다. 다른 과거 자료·원본·로그·
프로필·SDK/캐시를 추가 삭제하거나 보관정책을 바꾸지 않았다.

표본 최소 디스크 여유 1424.82MiB, 최대 cgroup 메모리 4923.12MiB.
최종 실행 순증가 5.99MiB, 단위 시작부터 보관 확인까지 6.51MiB,
문서 마감 전 여유 1418.89MiB. 이후 단위 증가량은 보장하지 않는다.

직접 모듈 요구 이름 검색을 마감하며 다른 관계/타입 조합을 새 필수 잔여로 늘리지 않는다.
V9 참가자·Helper·연락처는 V4/V5 실제 신원/가시성, office는 V3 표시 팩이 선행한다.
V3–V7 팩/backend·V8 실제 내장 surface/audio·종류 C# 표현/사용중 삭제 대응·V1/V2 후속은
고정 잔여다. RenderInput Draw/Pump와 Run 제어 IPC는 내장 렌더/오디오 전달 provider가
아니다. 현재 DISPLAY/Wayland/Xvfb·오디오 장치와 provider가 없어 모의 성공을 채우지 않았다.
실제 Windows/WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달은 미완료다.
M11/M12/M4는 구체적 회귀 없이 재개하지 않으며 3D/권한 별도 팩·이동 연출/실행 분리·
명시 async caller 합의를 유지한다. main은 사용자 검토/병합을 위해 보존한다.
