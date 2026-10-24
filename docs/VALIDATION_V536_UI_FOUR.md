# v536 선택·중첩 흐름·모바일 분기 화면 연결

원본은 `196c605`의 v536 prototype이다. 기존 layout/CSS를 재설계하지 않고 화면 adapter를 연결했다. 현재 구현과 한계를 [27개 조작 표](V536_RESIDUAL_UI_AUDIT.md)에 고정했다. 예전 25행 표에서 중첩 전환/root 분기 계약을 따로 두 행으로 분리했으며 무제한 조합을 추가하지 않았다.

## 변경

- 원본 영역 선택 메뉴/사각형, modifier 다중 선택·이동 및 좌표 Undo/Redo를 연결했다. 입력 도중 IME/텍스트 편집기의 Delete와 Undo는 canvas가 가로채지 않는다.
- 직접 소유 ordinary root의 연결 없는 여러 노드 삭제는 모든 대상을 먼저 검사한다. 기존 authorBatch의 같은 검증 후보/CAS/checkpoint/receipt에 removeNode를 허용한다. 늦은 삭제가 거절되면 앞선 삭제도 적용하지 않는다. 연결/참조/수정 중 본문 보호는 기존 native 검사를 그대로 사용한다. private/slot/copy 다중 삭제를 순차 쓰기로 대체하지 않는다.
- 기존 `kind=graph`를 동작 카드와 원본 내부 흐름/상위 버튼·breadcrumb에 연결했다. 개인 입력 키에 private path를 포함하고 root에서 자식 입력을 잘못 수집하지 않는다. 위치와 Undo 이력은 graph별로 분리한다. 복원은 native root 소유 기능을 다시 확인한다. 취소하거나 프로젝트/창이 바뀐 늦은 응답은 적용하지 않는다.
- 모바일 code/wrapper enum의 원본 분기 패널을 기존 후보에 연결했다. 이름은 원본 double-click/F2, 순서는 드래그/Alt+방향키/원본 touch 화살표를 사용한다. enum 숫자와 ID는 순서 변경으로 재할당하지 않는다. 잘못된 이름은 최종 enum에 넣지 않고 개인 raw 입력으로 보관한다.

## 실제 검증과 근거

격리 fixture만 사용했다. 모델 호출·사용자 로그인·권한 승인·실제 프로젝트 실행은 없다. Playwright Chromium에서 생성된 Linux 엔진을 사용한 결과와 controlled renderer를 구별한다.

- `v536_blueprint_selection.py`: controlled renderer 6건. modifier 이동/Undo/Redo, 영역 사각형, 한 묶음 삭제 취소/재실행, 연결 시 전체 거절, private 다중 순차 삭제 차단, retired project callback 차단.
- `v536_blueprint_selection_engine.py`: 실제 엔진·renderer 5건. 늦은 connected 삭제 전체 rollback, 실제 이동/Undo/Redo·입력 불변, 두 삭제의 cold 보관, 단일 authorBatch와 receipt 조회/재시도, Review 취소·compiler Confirm의 소유 graph만 변경.
- `v536_mobile_branch_panel.py`: 실제 엔진·renderer 5건. stable enum/연결 보호, 이름·순서·추가, Undo/Redo, 잘못된 이름 cold/Escape, Save 및 별도 compiler Confirm. source/callee/다른 구현은 불변이다.
- `v536_mobile_code_branch_panel.py`: 실제 엔진·renderer 3건. 일반 code 동작의 원본 F2 이름/추가 패널, 기존 C# 본문·enum 숫자/ID·실행 경로 보존, 한 enumCode checkpoint, compiler Confirm에서 소유 graph/code record만 변경. wrapper 검사와 구분한다.
- `v536_blueprint_internal_flow.py`: 실제 엔진·renderer 4건. native 내부 graph 진입, 본문 취소/개인 입력 보관·상위 복귀, desktop breadcrumb/mobile/cold, 저장·Review 취소·compiler Confirm. 선택한 leaf 파일만 최종 변경했다.
- `v536_document_windows_engine.py`: 실제 엔진 6건. 두 독립 요소 창의 원문 입력 격리, Pack Manager 플로팅/배경 선택, 일괄 닫기/재열기, cold 후 layout/입력/활성 탭, 모바일 Browser 재진입. 이 검사는 최종 소스 파일을 변경하지 않는다.
- `v536_document_projects_engine.py`: 실제 엔진 4건. 같은 이름의 서로 다른 프로젝트/독립 View 입력 분리, 실제 A→B 전환, retired 쓰기 거절, 프로세스 재시작.
- `v536_mobile_blueprint_touch.py`: Chromium protocol 합성 touch 4건. 원본 View/미니맵/설명, pan/pinch, touch cancel, Korean IME finder. 초기 Browser 열기 전 idle을 실제 enabled 상태로 기다리고 영역 선택의 새 연결 상태를 검증한다. 실제 Android/터치 하드웨어는 아니다.

로그/이미지: `/workspace/scratch/v536-ui-four/`. native 내부 흐름 이미지 evidence는 `/workspace/scratch/v536-info-definitions/tmp/confectory-wide-mixed-xxgpgm_8/internal-flow.png`, 모바일 분기 패널은 `/workspace/scratch/v536-info-definitions/tmp/confectory-mobile-enum-pins-wkdmqv8s/mobile-branch-inspector.png`이다. 390×844에서 원본 카드·상위 버튼·breadcrumb 배치를 실제 열어 확인했다. 원본 `dist/blueprint.js`의 `renderBlueprintContractPanel`, `bindBlueprintOrder`, `openInternal`, breadcrumb 및 `data-flow-parent`와 대응시켰다. 전체 pixel equality를 주장하지 않는다.

## 남은 정확한 경계

M3은 기존 native graph 진입만 완료다. 기존 C# code를 내부 graph로 변환할 때 body와 graph를 함께 보존하는 계약은 없다(M11). root의 별도 실행 출력도 native 함수 data signature와 대응하지 않아 비활성이다(M12). async(M4), 등록 multi-target/상속·copy group/opaque ABI(A4–A6), info 정의 전환/cardinality/picker/schema 부모·기능/아이콘(I1–I6), runtime Data 소유권·worker badge(B1–B2)는 표에 각각 제한으로 남긴다. 모바일 ABI를 그래프로 이동해 갱신하는 A7과 공유 출력 정의 rename의 특정 M6 흐름은 추가 수용 근거가 아직 없다. 실패한 A7 선택 driver는 scratch에 보관하고 검증된 기본 ABI 테스트는 바꾸지 않았다.

실제 Windows apphost/WebView2·DPI/native IME 및 모바일 기기 검증과 Library 파일 전달은 미확인이다. 이 결과는 전체 UI 복원 또는 새 backend 완성을 뜻하지 않는다. 패키지/checkout/게시 결과는 완료 후 아래에 별도로 기록한다.

## 빌드·패키지 사전 검토

최종 Linux 엔진 생성은 exit0, blueprint warnings0이다. Release solution은 경고/오류0. 73개 UI 리소스 canonical 크기/SHA, 변경 Python 구문, enum 기존 suite의 import-guard 전후 AST 동일, `git diff --check`를 통과했다. 원본 분기 double-click/F2·Alt 순서 동작까지 마지막 native 분기5건을 다시 확인했다. 선택 native5/renderer6, 내부 흐름4, 독립 창6, 프로젝트 전환4, 합성 touch4 결과와 구분한다. 전체 backend 전수 검사는 아니다.

로컬 Windows 교차 패키지는 `/workspace/artifacts/Confectory-v536-ui-four/Windows-x64/Confectory.exe`를 포함한 **전체 폴더**다. .NET Desktop Runtime10 x64/WebView2가 별도 필요하다. probe는 선언2321파일·73리소스·PE/의존성/변조 거절, 다른 cwd에서 설치 SDK 없이 packaged managed 웹 기동과 최소 로그인 렌더를 통과했다. Windows apphost/WebView2 실행은 하지 않았다.

marker 포함 2322파일/131896943bytes. marker SHA-256 `3a9941354e233264e6bbaefc313fdbcb99b6a6ac697ce6330ce60ab905c2b6de`, 정렬 checksum 목록 SHA-256 `4bd5e8dcdb660194aa8bd344494867e5cb4db7e3070a5719623c64ce36ece1f8`. 사전 검토 15파일(구현4/테스트7/문서4) 비밀 패턴 검출0, 로그/사용자 데이터/산출물은 게시 대상에 없다. 패턴 검사가 모든 비밀의 부재를 증명하지 않으며 인증 파일 내용은 읽지 않았다. 파일 목록/checksum은 scratch review에 보관한다.

실행 코드 커밋 `8cedf58dfbfb714100bb64185c12bde2b18c4470`을 기존 깨끗한 checkout에 ff-only 적용했다. Release 경고/오류0, checkout Linux 엔진 exit0/warnings0. 실제 retained-CRLF attribute pull·fresh-LF 73리소스와 content/encoding/BOM/binary/budget 거절 검사를 통과했으며 검사 전후 바이트가 같다. root/checkout의 추적 실행 소스·테스트3206파일은 줄끝 정규화 후 동일했다. 최초 resource probe는 아직 생성 중인 빈 JSON 보고서를 읽어 시작 단계에서 실패했으며 엔진 완료 확인 후 정상 재실행했다. 리소스/사용자 데이터 결함으로 오인하지 않는다. 후속 일반 code 패널 검사는 같은 실행 코드에서 수행했으며 마지막 커밋은 테스트/검증 기록만 추가한다.
