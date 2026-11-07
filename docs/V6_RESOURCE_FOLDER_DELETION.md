# V6 카테고리와 하위 자료 삭제

원본 저장소 v666 `dist/app.js::deleteResource`는 선택한 카테고리의 하위를 재귀적으로 구하고, `자료 삭제` 확인/취소를 받은 후 file/content-backup과 목록을 함께 지운다. 이번 단위는 카테고리 한 개와 현재 소유 하위 카테고리/사본 전체를 연결한다. 다중 선택 UI와 내용 편집 백업 복구는 별도 잔여다. 사용자 OS 원본 파일·프로젝트 선언·외부 자료는 삭제 경로가 아니다.

UI는 기존 카드/트리 context menu·확인창을 사용하고 루트 이름과 하위 개수를 표시한다. `Layout(delete-folder,{revision,command,id,hash})`는 표시 metadata hash와 전체 관측 revision을 고정한다. 확인창 이후 새로운 하위가 생기거나 다른 곳으로 이동하면 거부하며 암묵적으로 삭제 대상을 넓히거나 rebasing하지 않는다. 변경 대상을 다시 보고 새 확인이 필요하다. 현재 backend의 활성 프로젝트 소유/identity 경계를 재사용하고 다른 사용자/그룹 ACL을 새로 만들지 않는다.

하위는 실제 topology에서 구한다. files·topology·파일 이름·폴더 이름·삭제 receipt를 한 CommitPlan의 쓰기/관측으로 묶으며 manifest/identity까지 최종 CAS로 확인한다. 파일이 없는 카테고리를 지울 때는 files store나 빈 이름 sidecar를 생성/재작성하지 않는다. 다른 곳으로 옮겨 나온 항목은 삭제하지 않는다. 생존 항목의 원본 bytes/import proof·생성/이동 이력·표시명은 보존한다. 현재 parent는 활성 카테고리여야 하며, 과거 create-parent와 일괄 move의 ID만 검증된 삭제 이력으로 확인할 수 있다. 과거 이력을 새 명령으로 바꾸지 않는다.

기존 `.confectory/resource-deletions.v1.json`의 파일 receipt는 그대로 읽는다. 새 folder row는 `folders` ID 목록·`imports`의 id/command/hash·원래 `intent`를 digest로 묶는다. 파일 내용·이름·백업은 보관하지 않는다. 한 그룹에 현재 예산인 폴더64/파일64까지, 전체 기록은 기존 4,096건/2MiB이며 자동 가지치기는 없다. 새 DeletionRecords의 네 번째 문자열은 검증된 retired ID/folder/import-command 요약이고 기존 세 관측 필드는 그대로다. Request.import는 이 검증 요약으로 삭제된 하위 파일의 원래 가져오기 재요청도 거부한다. 새 명시적 import/create와 예전 삭제 응답 재확인은 분리되며, 예전 응답 확인이 새 세대를 다시 지우지 않는다.

기존 파일 전용 receipt reader는 새 그룹 형식을 모르므로 안전하게 거부한다. 그보다 이전 writer로 수정할 때의 지연 import 보호 한계도 그대로다. 자동 migration·구버전 writer 사용·과거 이력 삭제를 구현하지 않는다. 현재 writer는 두 형식이 섞인 기록을 검증한다.

쓰기 실패·동시 변경·응답 유실은 정확한 확인 intent를 개인 작업공간에 유지한다. cold restore는 자동 재실행하지 않으며 같은 명령 확인/입력만 취소를 제공한다. 삭제된 현재 폴더는 ProjectPack으로 돌아가고, 하위 미리보기는 기존 수명 토큰을 중단하고 닫아 늦은 성공이 창·내용을 되살리지 못한다. 기존 소스 Undo·Review→Confirm·계약/권한은 변경하지 않는다. 원본처럼 삭제는 영구 제거이며 새 휴지통/삭제 Undo를 약속하지 않는다.

최종 검증은 `VALIDATION_V666_RESOURCE_FOLDER_DELETION.md`에 기록한다. 초기화 빈 화면은 원인 미확정이며 실제 Windows/모바일·전체 UI·Space/Library 전달 완료와 구분한다.
