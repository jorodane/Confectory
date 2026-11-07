# 자료 카테고리와 이동

원본 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의 `dist/app.js`에서 `resourceCreateMenu`, `resourceNameDialog`, `navigateResources`, `moveResources`를 따른다. 원본의 “새 카테고리” 이름 폼, 계층 탐색, 내부 `application/x-confectory-resource` 드래그를 연결한다. 원본의 선택 부모와 자식 동시 이동은 선택된 최상위 항목만 이동한다. 새 디자인이나 자동 원본 복제는 추가하지 않는다.

현재 활성 프로젝트의 실제 자료 사본과 최대 64개 카테고리의 ID·부모 관계를 표시한다. 카테고리를 생성하고 중첩 탐색하며 파일/카테고리를 다른 카테고리 또는 ProjectPack으로 이동한다. 기존 텍스트 미리보기는 원래 ID/hash로 같은 바이트를 읽는다. 파일 추가는 ProjectPack에서 하고 이후 이동한다. 현재 폴더에 직접 import하는 결합 저장, 이름 변경·삭제·내용 편집/백업 복구는 이번 단위 밖이다.

독립 `ProjectResources::Layout`은 `.confectory/resource-layout.v1.json`만 원자 저장한다. 기존 `resources.v1.json` 형식, 파일 바이트, import receipt, 프로젝트 원본·소유 식별자는 변경하지 않는다. OS 파일을 이동하지 않는다. 이전 패키지는 기존 자료를 평면 목록으로 읽을 수 있으며 새 카테고리 정보는 표시하지 못한다. 카테고리 64개·파일 배정 64개·목록 512KiB·요청 16KiB의 제한을 두고 초과/손상/순환/알 수 없는 부모/다른 프로젝트는 거절한다. 새 권한 부여나 외부 파일 접근은 없다.

공개 호출은 `Layout(manifest, project, operation, payload) -> string`이다. 소비자는 기존에 허용된 manifest와 영구 project ID 및 일반 FileStream providers를 제공한다. `load {}`는 파일+폴더의 metadata 목록과 복합 `revision`, 원래 파일의 `resourceRevision`, 별도 `layoutRevision`을 반환한다. `create-folder {revision,command,id,name,parent}`와 `move {revision,command,ids,parent}`만 변경한다. ID/command는 소문자 UUID N, parent는 폴더 ID 또는 null이며, 읽기 결과의 복합 revision을 그대로 제출한다. UI bridge는 활성 ProjectContext에서 경로를 정하고 클라이언트 경로를 받지 않는다. 기존 `Request`는 계속 평면 파일 목록/원래 바이트를 제공하며 파일 import는 그 `resourceRevision`을 사용한다.

생성과 이동은 관측한 파일+카테고리 revision을 고정하며, 최종 CommitPlan에서 원본 manifest·소유 식별자·파일 목록과 카테고리 목록의 CAS를 모두 확인한다. 읽기에는 생성/자동 복구 부작용이 없다. 생성 proof는 각 폴더에, 마지막 이동 proof는 해당 항목에 보관한다. 살아 있는 같은 command의 정확한 재시도는 현재 목록을 반환하며 이전 상태로 이동시키지 않는다. 모든 증거가 후속 이동으로 대체된 과거 요청은 stale CAS로 거절한다. 무한한 영구 명령 이력을 보장하지 않는다.

실패/응답 유실에는 정확한 이름·ID·부모·revision·command를 private presentation에 보존한다. 재시작은 표시/입력만 복원하고 자동 재실행하지 않는다. 명시 재시도는 같은 요청을 확인하며 새 목록 확인이 오래된 요청을 재배정하지 않는다. 입력 취소는 이미 저장한 자료를 삭제하지 않는다. 새 검색/선택과 다른 프로젝트/닫힌 창/퇴역 드래그 콜백을 보호한다. 자산 전용 공유 Undo는 추가하지 않으며 이동은 명시적 반대 이동으로 되돌릴 수 있다. 기존 소스 Undo/Review→Confirm은 그대로다.

검증 기록은 `VALIDATION_V666_RESOURCE_LAYOUT.md`에 최종 코드 기준으로 기록한다. 실제 Windows/WebView2·모바일·전체 UI·Space 전달 검증으로 표현하지 않는다. 초기화 빈 화면의 원인은 미확정 잔여다.

카테고리 인라인 이름 변경은 [별도 이름 metadata 확장](V6_RESOURCE_FOLDER_NAMES.md)에 연결했다. 기존 Layout/파일 저장 형식은 그대로이며 현재의 이름 변경·충돌/입력 복원 범위는 그 기록을 따른다.

후속 [카테고리 첫 가져오기](V6_RESOURCE_DESTINATION.md)는 파일과 배치의 원자 저장·기존 v1 호환을 연결한다. 위 ProjectPack 후 이동 표기는 초기 배치 단위의 경계이며 현재는 [후속 검증](VALIDATION_V666_RESOURCE_DESTINATION.md)을 함께 따른다.
