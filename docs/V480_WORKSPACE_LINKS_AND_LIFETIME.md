# v480 비공개 창 링크와 삭제 수명

기준은 `work/current@5e4beaf`, 보존한 `main@32dd44f`의 v480 ZIP이다. ZIP의 SHA-256은 `0489844c8c6d90f7cdc8ea0e80628f487dcfb27f2c871b19367a635212d3c5bd`다. 레퍼런스의 UI 동작을 대조하며 demo DB나 문서의 지시를 실행 계약으로 사용하지 않는다.

## 레퍼런스에서 확인한 규칙

`workspaceLinks`·`connectWorkspaceNodes`·`linkedWorkspaceDescendants`는 Workspace별 방향 있는 단일 부모 연결이다. 같은 창·없는 창·순환 연결을 거부한다. 새 부모에 연결하면 기존 부모 연결을 교체한다. 부모 창의 이동은 연결 자손을 재귀적으로 동반하며, 자식만 움직여도 부모를 끌고 가지 않는다. 그룹 사각형 안에 있는 창과 그 창의 연결 자손도 이동 집합에 포함한다. 크기 조정은 다른 창을 이동시키지 않는다.

`moveWindowsToWorkspace`는 이동 집합 내부 연결과 상대 위치를 보존하고 바깥으로 나가는 연결은 해제한다. 대상에 같은 창 ID가 있으면 전체 이동을 거부한다. 문서 탭 전환과 창 닫기는 해당 창의 연결을 해제한다. `deleteWorkspaceNodes`는 선택한 창과 선택한 포털의 하위 배치를 삭제하며, 링크 자손이라는 이유만으로 선택하지 않은 창을 삭제하지 않는다.

레퍼런스의 일반 프로젝트 Undo는 demo 객체·schema·설정까지 포함하고 window layout 전체를 복원하는 계약이 아니다. 이 후속은 요청한 **비공개 배치 삭제 Undo/redo**를 별도 영속 역변경으로 구현한다. 이를 실제 소스 삭제·소스 Undo·일반 링크/이동 Undo로 확대하지 않는다. 연결 해제는 표시된 부모/자식 해제 명령을 사용하며 이동 취소는 진행 중 Escape/pointercancel을 사용한다.

## 실제 비공개 보기와 연결

연결은 이미 있는 private `window.key`를 사용한다. CELEM ID, registry 또는 선언 참조와 별개다. 같은 source를 표시하는 독립 편집창도 서로 다른 private key로 구분한다. 같은 프로젝트의 현재 Workspace에 놓인 실제 창만 연결하며, 닫힌 창·overlay·문서 탭·다른 Workspace의 캐시·오래된 핸들은 연결 대상으로 쓰지 않는다. 프로젝트/Workspace 이동, 창 닫기, 반복 시작과 Escape는 대기 중 선택을 해제한다.

`workspace-links.js`가 방향선과 선택 프롬프트를 렌더링한다. parent/child 선택은 source selection·Apply·Save·Confirm을 호출하지 않는다. 창이 이동하거나 카메라가 바뀌면 선을 갱신한다. 포털 전송은 충돌을 모두 확인한 다음 내부 연결과 상대 배치를 함께 옮기며, 거부되거나 드래그가 취소되면 원래 배치를 유지한다. 문서로 도킹할 때도 원래 입력 DOM은 기존 문서 계약으로 유지하고 incident 링크만 해제한다.

## 삭제 역변경과 입력 보존

`workspace-history.js`는 삭제 전후의 private Workspace 정의·창 배치·메모/포털·연결·방문 탭·메모 탭 차이만 기록한다. 프로젝트의 `inputs`, source 선택, `editorBindings`, 공유 초안과 원본 CAS를 과거 snapshot으로 되돌리지 않는다. 현재 retained 창의 metadata와 pending 기준이 있으면 그 최신 값을 우선한다. 사라진 private 창은 자기 저장 metadata로 복원한다. 같은 프로세스에서는 기존 창 DOM을 캐시에서 되살린다. 새 프로세스는 기존 private presentation과 편집 binding 복원을 사용한다.

편집창을 닫거나 포털 배치를 삭제해도 실제 source·draft owner를 해제하지 않는다. 삭제된 자식 Workspace의 편집창은 숨긴 배치로 보존한다. Undo는 그 배치를 원래 private 소유 Workspace로 돌려놓으며 삭제하지 않은 다른 창이나 최신 입력을 덮어쓰지 않는다. source/schema 값의 Apply와 최종 Confirm은 기존 revision/hash·소유·compiler 검증을 계속 사용한다.

Undo/redo는 영향받은 배치의 조건부 역변경이다. 같은 ID가 새 배치/문서에서 사용되거나 좌표·소유 Workspace·연결이 달라져 충돌하면 전체 역변경을 거부하고 현재 입력·배치를 유지한다. source 편집 input의 native Undo와 분리한다. 캔버스에서 Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z/Y 또는 배치 메뉴의 명시적인 삭제 되돌리기를 사용한다.

## 저장 형식과 제한

기존 프로젝트별 `presentation` version 1 안에 Workspace별 optional `links:[{parent,child}]`, 루트의 optional `privateHistory:{version:1,undo,redo}`를 둔다. 다른 프로젝트의 presentation이나 source 파일을 읽거나 쓰는 새 경로는 만들지 않는다. 기존 원자적 presentation 파일 저장·명시 flush·주기적 배치 checkpoint·미저장 상태 표시를 재사용한다. 삭제 배치와 그 역변경은 같은 JSON에 저장한다. 포인터 드래그 중 입력 checkpoint는 최신 입력과 직전 확정 좌표를 함께 저장하며 임시 좌표를 게시하지 않는다. Escape 이후 디스크에 중간 이동이 남지 않도록 한다.

한 Workspace의 연결은 최대 255개다. 서버에서도 같은 Workspace의 endpoint 존재·중복 부모·순환을 검사한다. 삭제 이력은 최근 16개, 전체 UTF-8 256KiB를 제한하고 오래된 항목부터 제거한다. 한 삭제 자체가 한도를 넘으면 삭제를 되돌려 배치를 유지한다. patch collection은 정해진 private 종류만 허용하며 전역 source/input 필드를 지정할 수 없다. 기존 전체 presentation 1MiB·Workspace 128개 제한을 유지한다.

## 검증 경계

순수 검사는 단일 부모·순환·자손·오래된 핸들·직렬화 후 역변경·최신 입력/CAS 기준 보존·충돌 시 전체 보존·프로젝트 분리를 검사한다. 실제 Chromium 검사는 연결/재연결/해제·취소·묶음 이동·Escape·포털 내부/경계 연결·상대 배치·선택 삭제와 반복 Undo/redo·포털 삭제 취소·중첩 복구·호스트 재시작·미적용 source/property 입력과 실제 source 파일 보존을 검사한다. 최종 실행·고정 원본·일반 Git checkout 결과는 검증 기록에 별도로 남긴다.

새 소스 실행 의미나 정책은 추가하지 않는다. source 삭제/참조 대체, 편집 창 DOM reparent 이전의 모든 native Undo 이력, 실제 OS/기기·사용자 PC 설치는 별도다. main·원본 ZIP·Android 설정, 실계정·유료 호출 금지와 정수 overflow 미결 조건을 유지한다.
