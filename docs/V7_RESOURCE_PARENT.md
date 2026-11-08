# V7 상위 카테고리 열기

기준은 고정 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`
(SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)의
`Confectory-v666/dist/app.js::resourceContextMenu/openResourceParent/navigateResources`다.
원본은 한 파일 또는 카테고리의 상위 위치를 별도 창으로 열고 그 항목을 선택·포커스한다.
루트 항목은 ProjectPack을 연다. 원래 창의 검색/위치·편집 입력을 비우지 않는다.
여러 항목 선택의 기존 삭제 메뉴는 유지한다.

`browser-tree:resource:<parent|null>:<UUID>`라는 기존 창 키와 `resourceFolder`, 선택/검색 등
기존 private presentation을 사용한다. 새 저장 형식/루트 필드/팩 ID·공개 실행/override 계약·
권한 정책을 만들지 않는다. 현재 카테고리 기준 트리와 경로·기존 Enter/탐색/복제·배치/창
포커스·cold 복원을 연결한다. 이 루트는 표시 범위이며 접근 권한이 아니다. 유효한 루트가
삭제되면 원본처럼 ProjectPack으로 표시를 복구하며, 다른 항목의 데이터는 옮기거나 삭제하지 않는다.

`readProjectResourceLocation` 관측과 native `locate` operation을 추가했다. 입력은 현재
ProjectContext의 project/id/hash/전체 revision뿐이다. 폴더·파일의 현재 metadata와 실제
상위 folder 또는 null만 반환하며 원본 바이트나 OS 경로는 보내지 않는다. 기존 저장/파일/
카운트/RPC 예산과 permission/owner 확인을 유지한다. endpoint만 추가한 응답
`resource-location-v1`이며 기존 read/save/storage 문법은 그대로다. 구 engine은 새 관측을
거절하고 기존 자료를 다시 쓰지 않는다. 같은 패키지 UI/engine을 사용한다.

native는 manifest/identity/catalog/layout/이름/설명/deletion/content 최종 관측 경계를
유지한다. client는 같은 입력으로 마지막 관측을 다시 확인한 뒤에만 새 창을 만든다.
실패·이동/삭제·권한 철회·변조는 창을 만들지 않으며 기존 “다시 확인”으로 목록을 명시
재조회한 뒤 사용자가 다시 열 수 있다. 저장 요청을 재생하거나 재기준화하지 않는다.
같은 대기 클릭은 합치고 새 대상/입력은 오래된 요청을 폐기한다. 닫힘·그룹/프로젝트 전환·
새 검색 입력·다른 입력/편집기 포커스 이후의 늦은 응답은 포커스나 창을 만들지 않는다. 재시작에서 대기 탐색은 재생하지 않는다.

새 cold 검사에서 기존 검색 입력 표시 결함도 확인했다. 게시본064e922d의 실제 UI bytes로
재현했으며 native private presentation의 query/queryInput은 남지만 입력란만 비어 있었다.
복원된 값과 포커스되지 않은 입력란을 동기화해 고쳤다. 재마운트·초안 폐기·자동 Save는 없다.
현재 입력 중인 필드를 과거 값으로 덮어쓰지 않는다. 새 비동기 탐색에서 별도 chat 입력의
포커스를 빼앗는 현상도 통제 재현한 뒤, 편집 중이면 대기 탐색을 폐기하도록 보완했다.

완료 기준은 이 단일 메뉴의 파일/폴더/root·선택/포커스·기준 트리·독립 창과 복원,
현재 읽기·취소/늦은 입력/경합·기존 자료 탐색/원본 파일 열기 회귀 및 최종 독립 LF/CRLF·
새 교차 패키지/전체 복원·증거/최신롤백 보관이다. 실제 신원/그룹 권한 backend·더 큰
자료/보관·기존 종류 정책·실기기/전체 UI와 초기 빈 화면 원인은 각각 별도다.

[최종 신규49단계·재사용0·실패/호환/보관 기록](VALIDATION_V666_RESOURCE_PARENT.md)을 따른다.
