# V7 보관된 텍스트 사본 미리보기

근거는 저장소 v666 ZIP의 `app.js::openResourceEditor`·`renderResourceEditor`와
`resource-preview.js::mountResourcePreview`의 텍스트 분기다. 첫 V7 단위로 자료 목록에서
두 번 클릭/Enter로 여는 760×520 창, 원본 미리보기 패널·도구줄·설정 영역과 파일명 표시를 연결한다.
UTF-8·BOM이 있는 UTF-16LE/BE를 원본처럼 `<pre>`의 텍스트 노드로 표시한다.
HTML/JS/XML은 해석하거나 실행하지 않는다. 잘못된 문자 인코딩의 대체 표시는 원본의 읽기 전용
TextDecoder 의미이며 보관 bytes를 바꾸지 않는다.

실제 사본은 기존 ProjectResources `read {id,hash}`가 검증한 bytes를 사용한다.
전용 `readProjectResource` observation은 project/id/hash만 받아 같은 읽기 계약에 전달한다.
추가 action/path/다른 프로젝트와 쓰기 endpoint의 observation은 거부한다. 기존 import/read 공개
계약·저장 형식·명령 receipt·기존 ID/원문·override 계약·권한·Review/Confirm/CAS는 유지한다.
사용자 개인 파일을 새로 탐색하거나 외부 자료를 가져오지 않는다.

원본의 확장자/MIME 우선순위와 BOM 판별을 재사용하고 현재 공급자의 파일1MiB 한계를 따른다.
이미지·PDF·Office 등 다른 렌더러와 내용 편집·이름/설명 변경은 이번 범위 밖이며 실제 지원처럼
표시하지 않는다. 설정의 파일명은 읽기 전용이다. 파일 읽기 실패는 원문/선택 hash를 유지한
명시 재시도로 처리하고, 새 hash로 자동 재배정하거나 파일을 다시 보관하지 않는다.

창은 현재 project·ID/hash·view generation/수명 토큰에 묶인다. 닫기/재열기·Home/프로젝트 전환 후
이전 관측은 화면을 바꾸지 않는다. 클라이언트 observation을 취소하고 표시를 폐기하지만 이미
실행 중인 모든 파일 I/O의 즉시 중단을 보장하지 않는다. 개인 레이아웃에는 owner/ID/hash만
보존하며 원문/base64/관측 요청은 저장하지 않는다. 실제 재시작은 동일한 소유 기준으로 다시
읽고 stale/손상/누락을 거부한다. 화면 복원이 파일 권한이나 실행을 만들지 않는다.

우선순위상 폴더·이동·삭제/복구는 불변 파일 bytes/receipt와 분리되는 가변 목록 기반이 필요하다.
이번에는 기존 읽기 계약만으로 사용자가 이미 보관한 사본의 내용을 확인하는 흐름을 마감한다.
폴더/이동/복구·큰/다중 파일·프로젝트 전체 이동/내보내기와 V7 나머지는 고정 잔여로 유지한다.
초기화 빈 화면 원인, V4/V5 실제 신원/권한 backend, 고급 Run 출력·물리 오디오, 실기기/전체 UI와
Library/Space 전달도 별도이며 선택적 조합을 새 필수 항목으로 추가하지 않는다.

현재 최종 검증 전이다. [검증 기록](VALIDATION_V666_RESOURCE_PREVIEW.md)에서 신규/재사용·
실패/복구·패키지/전체 복원과 실제 기기 미검증을 확정한다.
