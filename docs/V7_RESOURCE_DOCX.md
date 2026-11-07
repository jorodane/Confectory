# v666 DOCX 문단 편집

기준은 저장소 v666 ZIP의 `resource-edit.js`에 있는 DOCX 문단/표 필드,
`changeWordParagraph`, 보호된 필드 거절과 백업 복원 흐름이다. 원본 CSS와
문단/표 배치를 재사용한다. 1MiB 이하의 프로젝트 사본에서 문단 텍스트를
수정·저장하고 기존 직전 내용 복원/복원 취소에 연결한다. XLSX 편집, 큰 파일,
Office 앱 실행이나 Word 전체 서식 편집은 별도다.

활성 ProjectContext와 기존 읽기/쓰기 권한·ID·세대·hash·revision을 사용한다.
저장은 원래 Layout의 ContentIntent/최종 CommitPlan/CAS·동일 command 영수증을
사용한다. 원본 import/이름·설명·폴더/계약/C# 원문은 바꾸지 않는다. 변경된 ZIP과
직전 ZIP은 기존 content sidecar current/backup에 저장하고 정확한 바이트로 복원한다.
공식 DOCX MIME 및 `.docx` 이름의 빈/일반 binary/ZIP MIME만 허용하며 다른 Office
MIME의 표시명만 `.docx`로 바꿔도 편집을 허용하지 않는다.

문단/표 텍스트의 기존 run 서식·구조를 보존하는 원본 diff 알고리즘을 사용한다.
필드/변경 추적/content-control 문단은 읽기 전용이고 서명·매크로 ZIP은 편집을 거부한다.
namespace로 보호된 상위를 다시 확인하며 임의 문단 키나 잘못된 XML 문자를 거부한다.
DOCX 문서 XML만 다시 압축한다. 미수정 항목은 원래 local header/압축 데이터/
새 offset 외 central metadata를 그대로 유지하며 이미지·styles·관계 등도 보존한다.
외부 관계 URL·문서 스크립트·매크로·링크를 실행/조회하지 않는다.

일반 ZIP stored/DEFLATE와 descriptor를 지원하며 ZIP64/분할/암호화/중복/경로 위장/
심볼릭 링크/겹침/불일치 CRC·길이/불투명한 추가 record는 편집을 거부한다. 편집은
모든 항목을 CRC 검증하고 항목8MiB·합계16MiB 전개 한도를 둔다. 문서 XML2MiB,
50,000 node·깊이64·문자524,288, 표시 DOM20,000, 원본의 문단/표 표시 한도를 유지한다.
최대2개 편집 창, Worker당5초 응답 제한이며 hard CPU 상한으로 표현하지 않는다.
닫기/접기/프로젝트·관측 세대 전환에서 Worker를 종료하고 늦은 콜백을 무시한다.

비공개 초안은 기존 resource-content-drafts에 `docx-v1` encoding과 문단 changes를
보관한다. 변경 문단 문자열 합계는98,304 UTF-16 단위다. intended ZIP은 data에 두고
pending 요청의 bytes를 native에서 한 번 복원해 기존2MiB 전송 상한을 유지한다.
저장 중 새 입력은 별도 changes로 남기고 자기 성공 영수증 확인 후 새 기준과 함께
보존한다. 실패/재시작은 자동으로 문서를 저장하지 않으며 정확한 기존 요청만 명시
재확인한다. 개인 초안 snapshot 상한만4MiB로 확장하고 기존 텍스트 schema/파일 한도는
유지한다. 프로젝트 나가기/전환·완전 종료·명시 presentation flush에서는 private
입력을 먼저 보관하며 실패하면 전환하지 않는다. 무관한 일반 저장은 새 잠금으로
묶지 않는다. 미저장 문단이 있으면 먼저 저장/취소한 뒤 백업 복원을 허용한다.
명시한 프로젝트 사본 삭제의 기존 private/current/backup 제거 정책은 유지한다.

구버전 private parser는 새 codec/changes를 읽지 못한다. 새 DOCX 초안이 있는 상태를
과거 실행본으로 편집하는 것은 지원하지 않으며 자동 이행·과거 패키지 수정으로
숨기지 않는다. 기존 원본 import는 유지한다.

ZIP 처리는 [PKWARE ZIP 형식](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT)과
[표준 Compression Streams](https://compression.spec.whatwg.org/)를 기준으로 한다.
원본 fflate 0.8.2 vendor를 새로 복사하거나 설치하지 않는다.
실제 Windows/WebView2/모바일·전체 UI·Space 전달과 Word 앱의 서식 호환 실행은
자동화/교차 패키징과 구분한다. 기존 초기화 빈 화면은 원인 미확정이다.
