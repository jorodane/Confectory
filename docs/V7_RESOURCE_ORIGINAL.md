# V7 원본 파일 열기

기준은 저장소 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`
(SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)이다.
`Confectory-v666/dist/app.js::resourceContextMenu`의 파일 메뉴 “원본 파일 열기”와
`openResourceOriginal`을 연결한다. 기준 게시본8a9c8bd0에는 이 메뉴가 없었다.

원본의 `resourceBlob(ownerId,id)`는 현재 프로젝트의 `files` 저장소를 읽는다.
`writeResourceContent`도 명시 Save 때 같은 저장소를 바꾸므로 여기서 “원본”은
**마지막으로 저장된 프로젝트 사본의 전체 바이트**다. 최초 import 불변 사본이나
개인 복구 초안, OS 원래 경로를 뜻하지 않는다. 기존 자료 열기/편집/복원 흐름을 유지한다.

파일 한 개의 기존 컨텍스트 메뉴에만 항목을 더한다. 현재 ProjectContext의 기존 읽기
권한/소유 경계에서 `readProjectResourceFile`/`readProjectResourceFilePart` 관측을 수행한다.
이는 신규 두 관측 이름과 응답 codec이며 저장 형식·공개 실행/override 계약·권한 정책은
바꾸지 않는다. 기존 엔진/새 UI를 섞지 않고 같은 패키지의 bundle/관측 정의를 사용한다.
구 엔진은 새 이름을 거절하고 기존 보관본은 그대로 읽는다. 자동 이행/재작성은 없다.

파일당4MiB, 조각1MiB, RPC2MiB와 누적8MiB/64개 등 기존 예산을 유지한다. 각 조각과
전체 SHA, 현재 내용 generation, 전체 표시 revision/metadata, 마지막 재관측을 확인한다.
manifest/identity/catalog/layout/이름/설명/deletion/content의 최종 읽기 경계도 기존과 같다.
중간 변경은 전체 열기를 거절하며 저장·초안·백업·receipt를 작성하거나 재기준화하지 않는다.

사용자 클릭에서 빈 새 창을 먼저 확보하고 opener를 끊는다. 전체 검증 뒤 Blob URL로
이동한다. HTML/SVG/XML/JS는 원본처럼 text/plain으로 열고, 알려진 text/image/PDF 외 형식은
application/octet-stream으로 전달해 브라우저가 다운로드한다. 새 mesh/Office renderer나
OS 외부 앱 실행으로 표시하지 않는다. 유효한 UTF-8 텍스트에는 바이트를 바꾸지 않고
표시 MIME의 charset만 명시해 한글 오해석을 막는다. UTF-8이 아니면 그 가정을 하지 않는다. 브라우저별 형식 지원/파일명 처리는 별도다.

원본의5분 URL 수명을 유지하고 창 닫힘/pagehide에도 URL을 회수한다. 네 개까지의
완료/대기 파일(최대 raw16MiB)을 유지한다. 동일 원본 창의 대기 중 반복 클릭은 같은 새 창을
사용한다. 실패/닫힘/다른 프로젝트·탭/원본 창 폐기는 대기 요청을 취소하며, 사용자가 직접
이동한 새 창은 닫거나 덮어쓰지 않는다. 완료된 파일 새 창은 원본처럼 독립 창이다.
원본 자료 브라우저를 닫아도 완료된 파일은 유지되고 URL은 위 수명에 따라 회수된다.
팝업 차단/읽기 실패 후 사용자가 같은 메뉴를 다시 선택할 수 있다. 내용 변경 때문에
목록 해시가 오래됐으면 기존 “다시 확인” 버튼으로 목록을 명시 재조회한 뒤 다시 연다.
대기 새 창을 사용자가 닫은 뒤 재클릭하면 옛 요청을 취소하고 새 관측을 시작한다. 자동 Save/변경 재생은 없다.

이번 단위의 완료 기준은 이 기존 메뉴의 실제 파일 열기/저장본 일치/관측·취소 경계와
최종 LF/CRLF·새 교차 패키지·전체 복원·보관/실패 수명 검증이다. 상위 카테고리 열기,
4MiB 초과/일반 보관 확대·실제 신원/권한 backend·기존 종류 정책과 실제 기기/전체 UI는
각각 별도 잔여다. 초기 빈 화면과 과거 일시 실패의 원인은 미확정으로 유지한다.

[최종 신규53단계·재사용0·실패/호환/보관 기록](VALIDATION_V666_RESOURCE_ORIGINAL.md)을 따른다.
