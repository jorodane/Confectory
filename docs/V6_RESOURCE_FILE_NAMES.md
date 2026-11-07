# 자료 파일 이름 변경

원본 v666 ZIP의 `dist/app.js::resourceContextMenu/renameResourceInline`처럼 자료 카드와 계층에서 `이름 변경`을 열고 Enter·포커스 해제로 확정, Escape로 취소한다. 기존 인라인 입력/CSS와 180자 범위를 사용한다. 확장자도 표시명의 일부이며 자동 확장자 덧붙이기·형식 재분류·내용 변환은 하지 않는다. 현재 지원은 브라우저 인라인 진입이며 미리보기 설정란은 읽기 전용 표시로 유지한다.

`Layout(...,"rename-file",{revision,command,id,name})`는 현재 소유한 파일 ID의 표시명만 `.confectory/resource-file-names.v1.json`에 원자 저장한다. 원래 `resources.v1.json`의 bytes·최초 이름/MIME/kind·import receipt, 기존 카테고리/이름·ID/부모·원본 C#/계약·권한은 변경하지 않는다. 파일시스템의 원본 파일을 rename하지 않으며 표시명을 경로로 사용하지 않는다. 최대64개/512KiB의 별도 durable 데이터이고 cache/cleanup 대상이 아니다.

이전 Request와 이전 Layout reader는 원래 사본 이름·ID·구조를 계속 읽는다. 현재 Layout 목록/`read {id,hash}`는 확인된 표시명과 원래 검증된 bytes를 함께 반환한다. Editor의 기존 3필드 읽기 전용 관측은 같은 ProjectContext/ID/hash 경계로 현재 metadata를 사용한다. 읽기 전후의 원본·소유 식별자·파일 목록·계층·두 이름 snapshot을 확인하며 읽기가 자료/metadata를 생성·수정하지 않는다. 기존 readonly endpoint의 입력·관측 권한과 취소 경계는 변경하지 않는다.

파일 이름의 저장은 전체 복합 revision과 최종 CommitPlan에서 원본/identity/파일 목록/계층/폴더 이름을 확인한다. 기존 생성·이동·폴더 이름 변경도 파일 이름 snapshot을 확인한다. 같은 command의 정확한 재시도는 현재 목록만 확인하며, 후속 이름으로 proof가 대체된 과거 요청은 오래된 CAS로 거절한다. 무한한 영구 명령 이력을 보장하지 않는다.

열린 미리보기는 같은 ID/hash의 새 metadata를 확인하면 이전 읽기 token을 취소하고 현재 표시명/bytes를 다시 읽는다. 오래된 성공 응답이 새 제목·읽기 전용 파일명·내용을 덮어쓰지 않는다. 다른 프로세스의 변경은 원래 목록 재확인/다시 읽기 경계를 따르며 새 파일시스템 watch를 추가하지 않는다.

파일 kind·owner·원래 이름·입력·고정 revision의 미확정 입력 및 제출된 exact command의 실패 입력을 개인 화면에 보존한다. 재시작은 입력만 복원하고 자동 저장/재시도하지 않는다. 취소는 적용된 이름을 삭제하지 않는다. 이전 UI는 새 파일 표시명과 그 미확정/재시도 입력을 지원하지 않지만 기존 copy/topology 데이터는 읽을 수 있고 적용된 이름 파일은 보존한다. 기존 source Undo/Review→Confirm을 보존하며 별도 자산 Undo 정책은 추가하지 않는다.

파일 삭제·설명/내용 편집·backup 복구·다른 미리보기는 별도 고정 잔여다. [검증 기록](VALIDATION_V666_RESOURCE_FILE_NAMES.md)에서 새 검사/재사용·패키지/전체 복원·수명/공간을 구분한다. 초기화 빈 화면의 원인은 미확정이며 실제 Windows/WebView2·모바일·전체 UI·Space/Library 전달을 완료했다고 표현하지 않는다.
