# 큰 DOCX 사본의 문단 편집·복원·개인 초안

기준은 고정 v666 ZIP의 resource-edit.js `changeWordParagraph`, 보호된 문단 거절,
DOCX 내용 수정·이전 내용 복원이다. 3cf6a825의 실제 약2MiB 생성 DOCX에서 미리보기만
가능하고 편집 버튼이 없는 것을 재현했다. 기존 문단/표 DOM·문체·CSS와 텍스트 diff를
재사용하며, 이미 보관 가능한4MiB 이하 DOCX의 한 사용자 흐름을 연결한다.
XLSX 대용량 편집이나 Word 전체 서식/Office 앱 실행을 완료했다고 하지 않는다.

## 범위와 원본 보존

기존 읽기는 optional docxContent(4MiB/새 private codec)를 적격 DOCX에만 관측한다.
cap이 없으면 작은 기존 편집/큰 읽기 전용을 유지한다. 기본 ZIP/텍스트/XLSX 편집1MiB,
원래 파일당/선택합계/전체 import4MiB·64개, import upload6,000,000B와 RPC2MiB를 유지한다.
새 cap을 확인한 DOCX Worker만4MiB source/output을 명시한다. 원본 DOM·C# 소스·공개
celem/cpack·override·실행 계약과 권한 정책은 바꾸지 않는다.

모든 ZIP entry CRC/길이/겹침·symlink·경로·암호화/ZIP64/분할/중복·불투명 record 거절,
서명/매크로와 필드/변경 추적/content-control 보호를 유지한다. entry8MiB·총16MiB 전개,
XML2MiB·50,000 node·깊이64·문자524,288·DOM20,000과 문단1500개, 변경 문자열 합계
98,304 UTF-16 단위는 그대로다. 문서 XML만 다시 압축하고 수정하지 않은 ZIP local header/
압축 데이터/central metadata는 offset 외에 보존한다. Worker당5초·최대2개 편집 창은
기존 수명 규칙이며 hard CPU/모든 문서의 성능 보장은 아니다.

큰 변경에는 version2/format docx-v1 내용 sidecar를 사용한다. current와 직전 backup은
각4MiB 이하, sidecar snapshot은12MiB다. 기존 v1 content와 save-content는1MiB를 유지한다.
기존의 암묵적 전체 current64MiB 및 current+backup128MiB 상한도 명시 검사한다.
새 native Save는 기존 import generation까지 고정하고 활성 ProjectContext·ID·기준 hash·
compound revision과 마지막 CommitPlan CAS를 검사한다. 기존의 command/정규화 intent 영수증으로
동일 저장 재확인과 복원/복원 취소가 두 번 적용되지 않는다. immutable import와 OS 원본은
변경하지 않는다. 큰 현재 내용의 미리보기 조각도 import가 아닌 실제 current를 읽는다.

## 개인 입력과 전송

1MiB를 넘는 DOCX private bytes에는 docx-parts-v1 codec과 version2 private record를 쓴다.
header는 semantic changes와 pending metadata만 반환하고, data는1MiB씩 최대4개 조각으로
읽는다. 각 조각의 프로젝트/ID·private snapshot SHA·전체 SHA·순서/길이·canonical base64와
조각/전체 SHA를 검증한다. 마지막 native snapshot도 다시 확인한다. 과거 bytes를 새 기준으로
바인딩하거나 깨진 조각을 성공으로 재시도하지 않는다. busy만 같은 읽기 기준으로20회/50ms
이내 재확인하고 소유자/창/프로젝트 변경을 await 전후에 검사한다.

private Save만 별도 draft-docx upload target을 사용한다. 최대7MiB UTF8 요청을1MiB 조각으로
보내며, 큰 ZIP과 최악의 JSON escape 변경 문자열까지 보존한다. 기존 import upload 한도는
늘리지 않는다. 한 세션의 기존 단일 volatile upload에 실제 context/project·길이·전체 hash·
offset·중복 chunk 동일성을 확인한다. 성공/실패 후 해당 소유 cache만 해제하고 실제 입력은
메모리/지속 private record에 남긴다. private snapshot은 current/동결 pending bytes와 changes를
담는12MiB, 공통 snapshot/원자 CommitPlan16MiB 한도는 그대로다.

private record에는 upload ID/정확한 wire hash/value hash 영수증을 둔다. 응답 유실 때 같은
저장 명령을 자동 replay하지 않고 read-only 영수증으로 확인한다. peer bytes/새 영수증·다른
후보를 묵시적으로 rebase하지 않는다. 아직 확인하지 못한 응답은 다음 명시 확인/flush에서도
같은 영수증을 먼저 검사한다. 부분 전송·실패·미확정 상태에서 입력을 버리지 않는다.

실제 큰 문서 Save는 private pending에서 캡처한 정확한 ZIP과 command를 사용한다. 새 입력은
별도 changes로 남으며 private 저장 영수증 확인은 새 실행/접근 권한을 주지 않는다. 문서 Save의
성공 응답을 잃은 경우에는 기존처럼 사용자가 같은 요청으로 명시 재확인한다. 취소·프로젝트
전환/종료는 기존 private flush/모달·실패 보존 경계를 사용한다. source current와 backup은
복구/다시 읽기만으로 바뀌지 않는다.

## 호환과 검증 경계

이전 native reader는 새 content/private version·codec 또는 큰 snapshot을 거절할 수 있다.
작은 v1 자료는 유지하며, 새 형식을 이전 실행본으로 편집하는 것은 지원하지 않는다.
자동 이행/축소/비우기나 과거 패키지 수정을 하지 않는다. 최신본으로 다시 열어 보관한
내용/초안을 확인한다. 롤백 패키지의 보관·전체 복원 가능성과 새 데이터의 구 parser 호환은
구분한다. 현재 reader와 실제 baseline3cf native bodies의 거절/원본 보존을 검사한다.

생성한 ZIP/XML·미참조 고엔트로피 media만 사용한다. 실제 UI/Worker는 약2MiB 정상 DOCX,
ZIP module은 정확4MiB 실제 ZIP, native CAS/전송 경계는4MiB 불투명 생성 bytes로 따로 검증한다.
큰 media가 복잡한 Word 문서 전체의 호환/속도 증거는 아니다. 통제된 race·유실·손상 fixture와
실제 Linux engine/Chromium·LF/CRLF·교차 패키지/전체 복원을 구분한다.

초안 cold 조각의 실제 busy 거절은 제한된 read-only 재관측으로 처리한다. 별도 공개 cold
읽기 실패1건은 당시 payload가 없어 원인 미확정으로 보존하며, 기존 읽기 재확인 UI에서
입력/명령 불변을 검사한다. 역사적 초기 빈 #app의 원인이나 해결로 소급하지 않는다.
실제 Windows/WebView2·모바일·DPI/IME·Word/Office 앱·전체 UI·Space/Library는 미완료다.
큰 XLSX 편집·4MiB 초과/보관량·신원/권한 backend·종류 C#표현/사용중삭제 대응과 현재 예산 밖
custom 출력은 별도 고정 잔여이며, 정상 거절/선택적 조합을 새 필수 요구로 늘리지 않는다.
