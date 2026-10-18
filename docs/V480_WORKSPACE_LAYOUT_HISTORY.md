# IMP7: private Workspace 이동·연결 Undo/redo

`04f9d32` 이후의 후속이다. [기존 삭제 역변경](V480_WORKSPACE_LINKS_AND_LIFETIME.md)을 확장해 완료한 private 이동·연결을 같은 프로젝트별 이력에 넣는다. [최종 실행 기록](validation/v480-workspace-layout-history.json)은 이번 관련 검사만 집계한다. 이전 235개 및 후속 결과와 합산하지 않는다.

## 완료 단위와 조건

- 캔버스의 창·메모·그룹·포털 위치 이동은 pointerup으로 확정한 한 조작이 한 이력이다. 기존 그룹 포함 판정과 링크 자손 확장을 그대로 사용한다.
- 포털/부모 Workspace로 옮긴 창 묶음은 소유 Workspace·상대 배치·내부 링크와 끊긴 경계 링크를 한 역변경으로 되돌린다. 대상의 같은 private ID·연결 한도 충돌은 기존 이동 검사가 거부한다.
- 연결·부모 교체·단일 연결 해제·자식 연결 모두 해제는 각각 한 이력이다. 같은 부모의 중복 연결은 아무 조작도 하지 않는다. 선택·연결 미리보기·취소·실패는 이력이 아니다.
- Escape·pointercancel·lostpointercapture는 원래 배치를 유지한다. 포인터 진행 중 입력 checkpoint는 최신 입력과 직전 확정 좌표를 저장한다. 진행 중 Undo/redo는 실행하지 않는다.
- 완료한 새 조작은 redo 분기를 비운다. 이동 없는 클릭·취소·조건 거부는 redo를 유지한다. 최근 16개와 전체 UTF-8 256KiB 제한은 기존과 같다.

캔버스의 Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z/Y와 배치 메뉴의 `배치 되돌리기`/`배치 다시 실행`을 사용한다. 입력·문서 탭·모달 안의 키보드 Undo는 기존 입력 처리에 맡긴다. 크기 조정·camera·도킹·문서 탭 순서의 새 Undo는 이번 범위에 넣지 않는다.

## 최신 문서와 원자적 거부

새 window/item patch는 `placement:true`로 표시한다. 창은 private key·소유 Workspace·좌표/크기·접힘/배치/숨김 상태만 담으며 metadata는 빈 object다. 메모·그룹·포털은 ID·kind·같은 소유 Workspace·geometry만 담는다. 링크는 기존 owner/parent/child 차이를 사용한다. `inputs`, `editorBindings`, source text, document ID, 편집 revision/hash와 CAS snapshot을 새 이동 이력에 복사하지 않는다.

Undo/redo는 현재 geometry·owner·영향받은 링크를 예상 상태와 비교하고, 후보 전체의 private 정체성·소유 Workspace·부모/링크 forest·한도를 검사한다. 하나라도 달라졌거나 같은 private 창이 문서 탭/다른 배치에서 사용되면 DOM·정규 문서·두 stack을 바꾸기 전에 전체 역변경을 거부한다. 이후 독립적인 geometry 변경도 이 조건에 포함된다. 현재 배치와 입력을 유지하며 자동 재기준화하지 않는다.

통과한 위치/링크 역변경은 현재 window metadata와 메모 text/name/style을 유지한다. 같은 캔버스 창과 inline 메모 DOM을 다시 만들지 않으며 canonical note item 객체도 유지한다. Workspace 간 이동은 기존 retained 창 캐시를 사용한다. 새 프로세스는 기존 presentation/편집 binding 복원을 사용한다. cold에서 이전 JS 객체나 이전 native 입력 Undo stack이 살아 있다고 주장하지 않는다.

## 저장 계약

기존 프로젝트별 presentation version 1의 `privateHistory:{version:1,undo,redo}`를 사용한다. 기존 4필드 삭제 patch를 계속 읽고, 새 nondestructive window/item patch에만 다섯째 필드 `placement:true`를 허용한다. 서버는 양쪽 정체성·geometry·정해진 필드/boolean을 검사하고 metadata/입력 주입·null 측·잘못된 collection/marker를 거부한다. source 권한이나 새 저장 경로를 만들지 않는다. presentation 1MiB·Workspace 128개·Workspace별 링크 255개 제한을 유지한다.

프로젝트 객체를 완료 토큰에 묶어 A에서 시작한 조작을 B의 이력에 기록하지 않는다. 이력과 현재 배치는 기존 원자적 presentation 저장/flush 및 dirty 상태를 사용한다. 서버 저장 실패는 기존 미저장 표시/재시도 계약을 따른다.

## 최종 검증: 11 passed, 0 failed, 0 skipped

기준 source/fixture 커밋은 `9eb3cddc83a9be99d29d8f15fc3c317ba5cf1975`다. 두 gate 이하로 실행했다. Release build는 경고/오류 0이며 이번 11개 서로 다른 메서드가 통과했다. 실제 IMP7 메서드는 그룹/메모 검사를 보강해 한 번 재실행했으므로 통과 실행 12회를 검사 12개로 세지 않는다. 일반 Git LF/retained CRLF·43개 리소스 실제 시작과 변조 거부를 포함한다. Windows/Android 결과는 managed compile이며 실제 장치 실행이 아니다.

## 확인 범위

순수 검사는 묶음 이동·부모 교체/해제·최신 input/CAS·canonical note·redo 분기·프로젝트 소유·JSON cold·16개 제한과 geometry/중복 ID/문서 탭/없는 endpoint/부모 충돌/순환/255개 한도에서 전체 거부를 검사한다.

실제 Chromium은 linked/group movement, 포털/부모 이동, 연결·재연결·해제, 모든 취소와 provisional flush, 최신 source/property/note DOM·미적용 값·기존 CAS, 프로젝트 A/B/A, 실제 host restart 후 두 stack과 입력, 외부 배치 충돌 및 저장 형식 거부를 검사한다. [이동·입력 화면](validation/v480-workspace-layout-history.png)과 [충돌 거부 화면](validation/v480-workspace-layout-history-conflict.png)을 남긴다. 기존 삭제·중첩 포털·외부 source CAS 거부, v318 수명, Data/원자적 fill/자동 필드 비교와 일반 Git checkout/resource startup의 정확한 최종 메서드는 JSON에 기록한다.

남은 IMP7은 native reparent 이전의 전체 문서 Undo 이력이다. 소스 삭제·참조 치환·새 소유 집합 전체 Undo는 DEC2다. main·원본 ZIP·Android 설정·CSP를 보존하며 native OS/실기기·실계정·유료 호출·설치의 검증으로 확대하지 않는다.
