# V6 다중 선택과 명시 대상 삭제

기준은 저장소 v666 `dist/app.js::selectResource`, `resourceContextMenu`, `deleteResource`, `bindResourceDrag`다. 원본의 Ctrl/⌘ 토글, Shift 현재 표시 순서 범위, 이미 선택한 항목 우클릭의 `N개 항목 삭제`를 연결한다. 선택 밖을 우클릭하면 단일 선택/기존 메뉴로 돌아간다. 검색/정렬/밀도는 원래 선택을 자동 확대하지 않는다. 숨겨진 명시 선택도 원본처럼 N개 개수에 포함한다. 폴더 진입은 선택을 비우고, 같은 폴더의 트리 파일 선택도 동일 규칙을 사용한다. 기존 multi-ID move에 현재 명시 선택을 연결하며 새 자동 대상 정책은 없다.

선택 ID/anchor는 활성 프로젝트의 개인 workspace/window에만 저장한다. 이전 resourceSelected metadata도 읽는다. 새 선택은 권한/실행 계약이나 프로젝트 자료 자체를 변경하지 않는다. 가져오기/삭제 응답 뒤에 사용자가 더 늦게 만든 선택·검색을 덮어쓰지 않는다. 메뉴 클릭과 개인 상태 저장이 겹치면 기존 idle 경계에서 기다리며, 클릭 시점 자료/revision은 고정해 다른 대상에 재배정하지 않는다.

`Layout(delete-selected,{revision,command,targets:[{id,hash}]})`는 중복 없는 명시 대상1~128개를 받는다. 모든 현재 ID·file/folder 관측 hash를 먼저 확인하고 선택한 폴더의 하위를 합집합으로 구한다. 선택한 조상/하위가 겹쳐도 한 번만 제거한다. 하나라도 누락/변경/권한 경계 오류면 전부 거부하며 다른 정상 대상만 부분 삭제하지 않는다. 확인 후 하위 변경도 전체 revision으로 거부하고 암묵적 rebase/자동 선택을 하지 않는다.

기존 five-component CommitPlan으로 사본·topology·file/folder 이름·receipt를 한 번에 저장한다. manifest/identity를 포함한 최종 CAS와 실패 역순 복구를 재사용한다. 관련 없는 sidecar를 생성/재작성하지 않는다. 생존 원본 bytes/import proof·현재/과거 parent/연결·C# 원문/override 계약·권한·Review→Confirm/소스 Undo는 그대로다. 사용자 OS 원본·외부 경로는 전달하거나 삭제하지 않는다.

새 receipt는 이전 grouped 형식의 `folders/imports/intent/digest`를 재사용하되 intent의 targets 목록을 검증한다. 파일만 선택하면 folders는 비어도 된다. 기존 delete-file/delete-folder 기록은 그대로 검증한다. receipt는 내용/이름 백업이 아니며 기존4,096건/2MiB의 안전 거부와 무자동삭제를 유지한다. 정확한 명령 확인은 재적용하지 않으며, 새 명시 세대를 예전 명령으로 다시 삭제하지 않는다. 삭제한 원래 import의 지연 재요청은 계속 거부한다. 새 intent를 모르는 과거 reader는 안전 거부하며 자동 migration은 없다.

실패/응답 유실 시 정확한 targets/revision/command를 개인 pending으로 보존한다. cold restore는 자동 삭제/재시도를 하지 않는다. 명시적 다시 확인/입력만 취소를 제공하며 다른 프로젝트에 선택이나 pending을 넘기지 않는다. 원본처럼 삭제는 영구 제거다. 내용 편집·백업 복구, 큰/다중 파일 import와 다른 rich preview는 별도 고정 잔여이며 휴지통/삭제 Undo를 새로 약속하지 않는다.

최종 검증은 `VALIDATION_V666_RESOURCE_MULTI_DELETION.md`에 기록한다. 초기화 빈 화면은 원인 미확정이고 실제 기기/전체 UI/Space·Library 전달 완료와 구분한다.
