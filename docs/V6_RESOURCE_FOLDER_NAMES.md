# 자료 카테고리 이름 변경

v666 원본 ZIP의 `dist/app.js::resourceContextMenu/renameResourceInline`을 따른다. 실제 카테고리 카드와 계층의 `이름 변경`에서 인라인 입력을 열고 Enter·포커스 해제로 확정하며 Escape로 취소한다. 원래 180자 입력/CSS를 사용한다. 이름과 ID·부모 관계를 분리하며 열린 카테고리의 제목 경로·계층·검색은 확인된 metadata를 사용한다. 파일 이름 변경과 삭제/내용 복구는 이 단위에 넣지 않는다.

기존 `Layout(manifest,project,operation,payload)`에 `rename-folder {revision,command,id,name}`를 추가한다. 명시한 폴더 ID에만 적용한다. 새로운 `.confectory/resource-folder-names.v1.json`에 소유자·이름·마지막 정확한 요청 proof를 보관하며 기존 `resource-layout.v1.json`·파일 bytes/import receipt·C#·ID·부모/권한은 이름 변경 때문에 다시 쓰지 않는다. 현재 최대64개/512KiB다. 같은 이름의 다른 폴더는 허용하며 논리 이름을 OS 경로로 사용하지 않는다.

기존 v1 reader는 여전히 원래 카테고리 이름과 구조를 읽는다. 새 reader는 별도 이름이 있으면 표시명만 덮어쓴다. 기존 자료의 읽기 migration이나 자동 복구는 없다. 이전 패키지에서는 새 표시명과 이름 편집/미확정·재시도 입력 UI를 지원하지 않는다. 기존 topology와 파일 metadata를 손상/거절로 처리하지 않으며 적용된 새 이름 파일은 보존한다. 별도 이름 파일은 durable 프로젝트 데이터이며 cleanup 대상이 아니다.

복합 revision에는 이름 snapshot도 포함한다. 이름 저장은 manifest·소유 식별자·파일 목록·기존 카테고리 목록을 마지막 CAS에서 확인한다. 카테고리 생성/이동도 이름 snapshot을 확인하여 오래된 화면 입력을 조용히 재배정하지 않는다. 같은 command의 정확한 재시도는 현재 목록을 확인하며, 후속 이름 변경으로 proof가 대체된 과거 요청은 stale CAS로 거절한다. 무한한 영구 명령 이력을 보장하지 않는다.

미확정 입력은 owner/ID/원래 이름/입력/고정 revision을 개인 화면에 보존한다. 저장 제출 뒤 실패·응답 유실은 기존 pending intent에 정확한 command를 보존한다. 재시작은 입력만 다시 연결하고 자동 저장/재시도하지 않는다. Escape와 실패 입력 취소는 이미 저장된 이름을 지우지 않는다. 원본 소유·권한·Review→Confirm 및 기존 source Undo를 보존하며 별도 자산 Undo 정책은 추가하지 않는다.

[최종 검증 기록](VALIDATION_V666_RESOURCE_FOLDER_NAMES.md)에서 신규/재사용·실패/복구·패키지 복원과 공간을 구분한다. 초기화 빈 화면의 원인은 미확정이고 실제 Windows/WebView2·모바일·전체 UI·Space/Library 전달은 이번 Linux 자동화 검증과 구분한다.
