# V6 프로젝트 자료 사본 한 개 삭제

기준은 저장소 `Confectory-Editor-Prototype-v666.zip`의 `dist/app.js::deleteResource`다. 원본은 쓰기 권한 확인 후 `자료 삭제` 확인창에서 Cancel/삭제를 받고 프로젝트 IndexedDB의 file/content-backup과 목록을 지운다. 휴지통이나 삭제 취소 기능은 아니다. 이번 단위는 직접 가져온 파일 사본 한 개만 카드/트리에서 확인 후 삭제한다. 사용자 OS 원본 파일은 경로로 전달받지도, 삭제하지도 않는다. 폴더 하위 전체·다중 삭제와 내용 편집/백업 복구는 후속이다.

`Layout(delete-file,{revision,command,id,hash})`는 활성 프로젝트에서 관측한 전체 revision과 파일 SHA를 요구한다. 현재 copy 항목·배치·표시명 alias와 receipt를 한 CommitPlan으로 저장한다. 생존 항목의 bytes·import proof·분류·이름과 폴더 이동 이력은 보존한다. 삭제된 ID가 과거 일괄 이동 proof에만 남으면 검증된 삭제 receipt로 역사적 참조를 확인한다. 현재 placement/alias는 삭제된 항목을 참조하지 않는다.

`.confectory/resource-deletions.v1.json`은 소유 프로젝트/manifest에 묶인 처리 기록이다. 파일 내용·이름·백업은 담지 않는다. 삭제 intent의 ID/hash/revision/command와 원래 import command를 digest로 검증한다. 정확한 삭제 재요청은 현재 목록을 확인하며 새 세대의 같은 ID를 재삭제하지 않는다. 원래 import command의 늦은 재시도는 `resource_import_deleted`로 거부한다. 새 명시 import command로 다시 가져오기는 가능하다. 이 기록은 프로젝트 데이터이며 임시 산출물 cleanup 대상이 아니다. 자동 가지치기 없이 4,096건/2MiB에서 안전 거절한다. 이전 writer는 이 새 보호를 모르므로 삭제한 프로젝트를 구버전으로 수정하면 지연 import 방지를 보장하지 못한다. 자동 마이그레이션/과거 기록 삭제는 없다.

프로젝트 identity·manifest·자료 store·topology·폴더/파일 이름·삭제 기록을 최종 CAS로 확인한다. 저장 도중 예외는 기존 CommitPlan의 역순 원본 복구를 따른다. 복구 자체가 실패하면 기존 aggregate 오류를 숨기지 않는다. 일반 소스 Review→Confirm/Undo/권한은 변경하지 않는다. 자료 삭제에는 원본처럼 별도 Undo/휴지통을 새로 약속하지 않는다.

확인창 취소는 쓰지 않는다. 실패·응답 유실 시 확인한 정확한 명령을 개인 작업공간에 유지하며 다시 확인 또는 입력 취소를 제공한다. 재시작은 자동 실행하지 않는다. 다른 프로젝트로 넘어간 intent/응답은 적용하지 않는다. 성공한 목록에서 사라진 파일의 미리보기는 토큰을 중단하고 닫으므로 지연 읽기 성공도 창·내용을 되살리지 못한다.

최종 검증 기록은 `VALIDATION_V666_RESOURCE_FILE_DELETION.md`로 남긴다. 실제 Windows/WebView2·모바일·전체 UI·Space/Library 전달 완료로 표현하지 않는다. 초기화 빈 화면은 원인 미확정 잔여다.
