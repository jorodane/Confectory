# V6 선택한 카테고리에 첫 자료 보관

기준은 검증된 v666 `app.js::importResourceFiles(files,w,folderId)`의 선택 대상 `targetFolder`와 한 readwrite transaction이다. 기존 자료 추가 메뉴를 중첩 카테고리 안에서도 제공하고, 외부 File 드롭은 실제 가리킨 폴더/ProjectPack을 대상으로 한다. 기존 창·tree·카드·설정/CSS는 유지한다. 사용자 개인 파일/폴더를 자동 탐색하거나 외부 URL을 가져오지 않는다.

원래 Request의 `import`/`import-many`와 v1 자료·배치 저장 형식은 유지한다. Layout의 추가 `import-files {revision,resourceRevision,command,parent,imports}`는 명시한 기존 카테고리에만 새 파일들을 보관한다. imports는 기존 `{command,item}` 목록이다. 카테고리 ID/전체 관측 revision·원래 resource revision과 항목별 ID/내용/영수증을 묶으며, 자동으로 대상을 고르거나 이미 보관한 파일을 재배정하는 API가 아니다. 이미 보관한 파일은 기존 명시 Move를 사용한다.

Request의 native 내부 `prepare-import-many`는 기존 검증을 거친 후보/관측을 반환하며 쓰지 않는다. 브라우저는 이 operation이나 임의 CommitPlan을 제출할 수 없다. Layout은 고정 경로·영수증·관측 hash를 확인한 후보와 원래 move 영수증 형식의 첫 배치를 한 CommitPlan에 합친다. 최종 CAS는 manifest/identity/자료 저장본·카테고리·폴더/파일 표시명·삭제 기록과 기존/새 파일 내용 관측을 포함한다. 두 번째 쓰기가 실패해도 앞선 자료 append를 역순 복구한다. 새 저장 파일이나 migration·권한 정책은 추가하지 않는다.

File 선택/메뉴·드롭 시 대상과 기준을 고정한다. 파일을 읽는 동안 현재 폴더를 탐색해도 이미 선택한 대상을 바꾸거나 다른 화면의 선택을 지우지 않는다. 삭제/변경된 폴더는 거절하며 ProjectPack으로 자동 대체하지 않는다. stale 기준은 refresh/retry로 자동 rebase하지 않는다. 같은 import와 배치 영수증의 재확인은 다시 쓰거나 나중의 명시 Move를 되돌리지 않는다. 삭제된 import는 재생성하지 않는다.

실패·응답 유실은 해당 창의 File 목록/원래 요청·대상 표시를 유지해 명시 재시도·입력 취소를 제공한다. 취소는 이미 보관된 사본을 삭제하지 않는다. Home/프로젝트 전환의 오래된 callback은 다른 소유자에 전송하지 않는다. 미보관 File bytes/command는 개인 레이아웃에 저장하지 않으며 실제 재시작 후 직접 다시 선택한다. 확인된 파일/카테고리는 기존 영속 저장에서 복원한다.

선택 전체1MiB/최대64개·프로젝트 전체4MiB/64개·카테고리64개와 기존 IPC 한도를 유지한다. 원본 OS 파일·C# 본문·값·설명·공개/override 계약·권한과 Review→Confirm을 보존한다. 대형 파일/선택 예산 확대·Office 편집·다른 원본 미리보기·자료 설명과 다른 고정 행은 남는다. 초기화 빈 화면은 원인 미확정이고 실제 Windows/모바일·전체 UI·Library/Space 전달과 생성 File 자동화 검증을 구분한다.

[최종63단계(신규60·동등 재사용3)](VALIDATION_V666_RESOURCE_DESTINATION.md)는 native/실제 엔진 UI·새 패키지/전체 복원과 기기 한계를 구분한다.
