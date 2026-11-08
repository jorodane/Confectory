# 큰 Office 사본 읽기 전용 미리보기

원본 v666 ZIP의 resource-preview.js는64MiB 사전 검사 뒤 DOCX wordPreview,
XLSX spreadsheetPreview, PPTX slidePreview와 ODT content.xml을 표시한다.
이번 단위는 이미 보관 가능한1MiB 초과–4MiB DOCX/XLSX/PPTX/ODT의 내용 미리보기
누락을 같은 패널·서식·워크시트 선택에 연결한다. 전체 보관4MiB/64개·명시 File 가져오기
상한을 늘리지 않고, 실제 Office 앱 실행이나 네 형식의 전체 서식/기능을 주장하지 않는다.

큰 read는 기존 unavailable/reason·metadata 응답을 유지하고 document kind·기존 이름/MIME
형식 판정·표준 ZIP local header가 맞는 사본에만 선택 officePreview를 추가한다.
encoding/partBytes/total과 확정된 extension을 포함한다. signature는 ZIP/문서 인증이 아니다.
이전 backend/UI는 선택 capability가 없으면 원래 metadata-only 표시를 유지한다.
저장v1/기존 imagePreview/pdfPreview/text prefix나 작은 read의 뜻을 바꾸지 않는다.

readProjectResourceOfficePart/preview-office-part는 현재 ProjectContext의 기존 읽기 권한과
project/ID·전체 SHA·import generation·compound display revision·정수 part를 검사한다.
고정1MiB씩 최대 네 조각이며 각 요청에서 현재 전체 원본의 길이·canonical encoding·SHA와
manifest/identity/store/layout/이름/설명/삭제/content sidecar의 최종 읽기를 다시 검사한다.
외부 path·foreign/stale/누락/범위 밖 part·mutation/image/PDF lane을 거절한다. 캐시나 lease로
이전 bytes를 새 기준으로 위장하지 않는다.2MiB RPC·공개 celem/cpack/override 계약과
기존 저장·실행·권한·Review→Confirm/최종CAS는 보존한다.

브라우저는 header와 각 조각의 정확한 item/format·기준·순서·길이·canonical base64·조각 SHA와
전체 SHA를 모두 검증한 뒤 기존 실제 module Worker에 완전한 ZIP을 전달한다. metadata는
조각 대기 뒤 다시 bind하지 않아 늦은 설명 입력을 보존한다. busy만 같은 기준으로 제한
재관측하고 mutation을 자동 replay하지 않는다. 닫기/같은 창 재열기/삭제·Home/다른 project·
cold 및 hash 대기의 owner를 다시 검사하며, 접힌 창에서는 Worker를 만들지 않는다.
private presentation에 ZIP/XML·미결 part·Worker 상태를 남기지 않는다.

ZIP reader의 기본 source1MiB는 그대로다. 미리보기에서만 명시4MiB를 opt-in하며
archive=true인 편집 mode에서는 큰 source opt-in 자체를 거절한다. ZIP64/분할/암호화/
symlink/위장·중복·겹친 entry/불일치 header·CRC·실제 전개 길이의 기존 거절을 유지한다.
최대1024개 directory entry, 선택 XML64개·각2MiB·합계4MiB, XML node50000·깊이64·문자524288,
DOM20000·문자524288과 원본 문단/표/슬라이드/200행·30열/워크시트 표시 한도는 유지한다.
미사용 media 내용까지 CRC 인증하는 일반 ZIP 도구가 아니며 파일 SHA와 구조/선택 XML 검사를
구분한다. DTD/entity·문서 스크립트/매크로/외부 관계를 실행하거나 조회하지 않는다.
Worker당5초·최대4개 view, 종료·늦은 응답·XML/DOM 해제도 기존 규칙을 재사용한다.
타이머/입력·전개 한도를 모든 경우의 hard CPU/프로세스 전체 메모리 보장으로 표현하지 않는다.

큰 DOCX/XLSX는 편집 컨트롤러에 연결하지 않고 읽기 전용으로 표시한다. 기존 작은 DOCX/XLSX의
실제 편집·변화 없는 Save·실패/늦은 입력·백업/복원·private schema와1MiB 원본/출력 한도는
변경하지 않는다. native에서도 큰 원본의 save-content/restore-content는 쓰기 전에 거절한다.
큰 편집/백업·전송 상한 변경이나 자동 이행·구버전 parser 수정은 이번 읽기 단위에 포함하지 않는다.

생성한 ZIP/XML과 무작위 미참조 media만 사용한다. 네 형식의 실제 DOM/워크시트 값·서식과
정확4MiB workbook을 검증하며, 큰 media가 복잡한 문서 전체의 서식·성능 증거는 아니다.
native 본문/최종 읽기 race는 통제된 fixture, module Worker/Compression Streams/DOM은 실제
Linux 엔진·Chromium 실행이다. 기존 게시본 누락 재현과 개발 overlay·최종 LF/CRLF·새 교차
패키지/전체 복원·기존 작은 Office 편집·PDF/그림/내용 회귀는 최종 기록에서 구분한다.

큰 다른 그림 형식·큰 내용 편집/백업·4MiB 초과/전체 보관 확대·실제 신원/권한 backend와
QHD/4K/FHD+·GPU/물리 장치는 별도 잔여다. mesh/임의 조합과 새 권한 정책은 추가하지 않는다.
초기 빈 #app 원인은 미확정이며 M11/M12/M4는 구체적 회귀 없이 다시 열지 않는다.
실제 Windows/WebView2·모바일·DPI/IME·Office 앱 서식 호환·물리 오디오·전체 UI·Space/Library
전달은 자동화/교차 패키지 검증과 구분한다. 기존 원본·증거·로그/프로필·SDK/Git·사용자 자료와
main은 보존하고, 승인된 소유 임시 수명과 최신/롤백 두 세대 보관만 유지한다.

[최종 신규61단계·지속 보관·미실행 기록](VALIDATION_V666_RESOURCE_OFFICE_PARTS.md)을 따른다.
