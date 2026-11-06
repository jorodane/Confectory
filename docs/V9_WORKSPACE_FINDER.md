# V9 작업 공간 찾기

기준은 저장소의 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`이다.
`Confectory-v666/dist/app.js`의 `openWorkspaceFinder`, `workspaceNodeSearchInfo`,
`placedNodeText`, `workspaceSearchText`와 검색 버블·동봉 CSS를 현재 실제 프로젝트에 연결한다.

## 이번 완결 흐름

- 원래 위치의 검색 버블에서 요소/글자 패널을 열고, 현재 창·메모·하위 Workspace 표지를
  이름/현재 글자로 찾는다. 방향키·Enter로 원래 대상을 선택·중앙 표시한다.
- 검색 패널을 명시적으로 열면 기존 탐색기의 읽기 전용 목록/관계 조회를 재사용한다.
  현재 native 권한 필터를 통과한 `workspaceRows()`의 선언 이름/종류는 검색할 때만
  결과에 포함한다. 같은 표시명도 qualified ID를 유지하고 기존 선언 열기 경로를 쓴다.
  검색을 이유로 원본 파일·외부 부모·비공개 계정/작업을 추가 조회하지 않는다.
- 같은 창 DOM과 개인 편집 입력을 보존한다. 목록 조회 중/실패/명시적 재시도를 표시하며 query와 개인 입력을 유지한다.
  쿼리 변경·현재 내용/목록 변경을 반영하고,
  stale 결과는 활성 프로젝트/세대/Workspace와 현재 projection에서 다시 확인한다.
- Esc/닫기·바깥 클릭·프로젝트/Workspace 변경은 panel과 listener를 폐기한다. query와
  결과는 개인 저장 데이터가 아니며 cold에서 재생하지 않는다. IME 조합 키는 소비하지 않는다.
- 이미 있던 Ctrl+F·Blueprint/메모의 배치 글자 찾기는 유지한다. 새 검색 버블의 title은
  이를 별도 패널의 단축키라고 오인하지 않도록 `검색 · 창과 요소`로 표시한다.
- 비밀번호/토큰/hidden 입력은 기존 추출 보호를 재사용한다. 제어된 실제 브라우저에서
  재현한 `aria-hidden` 영역 입력 유출도 공통 추출기에서 제외한다. 사용자 글자는 DOM
  텍스트로만 표시하며 HTML을 해석하지 않는다.
- 채팅 입력에서 검색 버튼으로 이동할 때는 기존 Run/검토의 개인 입력 보존 경로를
  재사용한다. blur 저장이 검색의 첫 클릭을 막지 않으며 전송/실행을 만들지 않는다.

원래 데스크톱/모바일 검색 패널 CSS를 재사용한다. 원본을 실제 native 상태로 번역하는
경계이며 프로젝트 전체 원문 검색·비공개 metadata 검색으로 확대하지 않는다.
  배치하지 않은 객체의 전체 내용 검색은 실제 읽기 adapter의 후속 경계로 남는다.
팝오버/창 배치·C# bytes·공개/override 계약·source ownership·권한·Review→Confirm·최종
CAS와 M11/M12/M4·완료된 저장 복구·Run 최대화는 그대로다.

[정확한 delta](v666-workspace-finder-delta.json)를 따르며 최종 검증은 진행 중이다.

## 유한 잔여와 backend 평가

참가자/Helper/Worker·연락처/대화 검색은 V4/V5의 실제 신원/가시성 adapter가 필요하며
이번에 가짜 항목이나 접근 권한을 만들지 않는다. 3D office 검색/방 이동은 별도 V3 표시
팩과 연결하고, 캐릭터 이동이 실제 작업 시작의 조건이 되지 않는 합의를 유지한다.

기존 RenderInput/Window는 명시 소유 native 창의 사각형/텍스트 renderer이며, Stage는
선택한 소비자의 자원/단계 수명을 관리한다. 현재 Run에 내장 화면을 전달·설정하는
surface 계약은 없고 오디오 provider도 없다. V8 해상도·오디오·렌더 디버그를 모의
scene/FPS/사운드 성공으로 채우지 않는다. 이 backend 연결과 V6/V7 자산 경계, 종류 C#
표현/사용중 삭제 결정, V1 미검증·V2 후속 등 기존 고정 잔여는 유지한다.

Linux .NET/Chromium과 교차 패키지 검사, 제어된 renderer guard 검사를 구분한다.
실제 Windows apphost/WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달은 별도다.
