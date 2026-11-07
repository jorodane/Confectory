# V6 텍스트·코드 자료 내용과 이전 저장 복원

기준은 저장소 v666 `dist/app.js::{resourceEditFormat,writeResourceContent,renderResourceEditor}`와 `dist/resource-edit.js::{textCodec,mountResourceContentEditor}`다. 기존 미리보기 패널 안에 `내용 수정`, textarea, `내용 저장`/`취소`, `이전 내용 복원`/`복원 취소`를 연결한다. 문자 인코딩이 유효한 UTF8/BOM·UTF16LE/BE와 원래 CRLF/CR/LF를 유지한다. 텍스트는 실행하지 않는다. 그림/PDF/Office 문서 편집은 이번 지원에 포함되지 않는다. UI와 native 모두 기존 ID·프로젝트·형식 경계를 확인한다.

`Layout(save-content|restore-content)`는 명시한 현재 파일 hash, 전체 표시 revision, 고유 command를 요구한다. 편집본과 직전 내용은 `.confectory/resource-content/<id>.v1.json`에 따로 보관하고 원래 `resources.v1.json`의 bytes/import proof와 Request ABI를 바꾸지 않는다. 현재 파일의 **원래 import command**에 결합해 예전 ID의 편집본을 새 등록에 적용하지 않는다. 현재 내용/백업의 SHA·크기·canonical base64url, 소유·generation·receipt를 읽을 때 확인한다. 저장은 현재 내용을 백업으로 교체하고, 복원은 현재/백업을 교환한다. 별도 다세대 보관·휴지통·자동 migration은 추가하지 않는다.

최종 CommitPlan은 manifest/identity, 원래 사본, 폴더/표시명/삭제 기록과 활성 파일별 편집 관측을 함께 CAS한다. 예전 기준은 자동 rebase하지 않는다. 정확한 마지막 command의 응답 유실은 재저장/재복원 없이 확인한다. 더 나중에 바뀐 내용을 예전 명령으로 덮지 않는다. 파일당 편집 내용/백업 각각1MiB, 기존64개 파일 ID 경계를 유지한다. 원래 import의 전체4MiB 제한은 그대로이고, 편집된 현재 내용은 최대64MiB(백업 별도)다. per-file sidecar와 작은 삭제 tombstone으로 대형 집계 저장이나 primitive의16MiB plan 제한 확장이 필요하지 않다. 메타데이터 목록은 내용 bytes를 전달하지 않는다.

기존 삭제는 해당 편집본과 백업도 같은 CommitPlan에서 bytes 없는 소유/generation tombstone으로 대체한다. 삭제 승인 밖의 자료는 바꾸지 않는다. 기존 삭제 receipt ABI·지연 import 거절은 유지하며, 사용자가 새 command로 같은 ID를 다시 등록한 경우 원래 사본부터 시작한다. tombstone/과거 기록을 자동으로 삭제하지 않는다. CommitPlan의 기존 예외 역순 복구를 사용하며 OS 전원 중단에 대한 새 보장을 주장하지 않는다.

미제출 입력과 미확정 요청은 기존 개인 Home storage의 프로젝트별 `resource-content-drafts/<project-hash>/<id>.json`에 별도로 저장한다. active ProjectContext/identity를 서버에서 확인하고 클라이언트 경로를 받지 않는다. 원래2MiB WebUI request/result 제한을 유지하기 위해 현재 입력과 미확정 제출 bytes를 따로 읽고, 저장 시 같은 command의 제출 bytes는 검증된 개인 보관본에서 결합한다. 전송 크기를 줄이려고 입력/백업을 버리지 않는다. 자동 제출은 없으며 Ctrl+S·명시적 재확인·취소만 사용한다. 성공 뒤에도 응답 대기 중 새로 쓴 입력을 지우지 않는다. 닫기는 계속 편집/수정 취소를 확인하고 저장 중 닫기를 막는다.

개인 초안의 저장 실패는 화면에 알리고 메모리 입력을 유지한다. 재시작 복구는 **보관이 확인된 1MiB 이하 입력**에 적용된다. 1MiB를 넘는 지원 밖 입력은 화면에 유지하고 저장을 막으며, 그 초과 입력의 cold 복구를 보장하지 않는다. 다른 프로젝트는 입력이나 요청을 이어받지 않는다. 새 storage를 모르는 과거 패키지가 편집본을 읽는다고 주장하지 않는다. 원본 import bytes는 보존되지만 구버전 실행은 현재 편집본을 표시하지 못한다.

C# 원문/공개 override 계약·권한/부모외부 원본·Review→Confirm·소스 Undo는 변경하지 않는다. 검증은 `VALIDATION_V666_RESOURCE_CONTENT.md`에 최종 기록한다. 자료 설명, 큰/다중 import와 현재 폴더 첫 import 결합, Office 내용 편집·rich preview는 고정 잔여다. 초기화 빈 화면은 원인 미확정이고 실제 Windows/mobile·전체 UI·Space/Library 전달은 별도 미검증이다.
