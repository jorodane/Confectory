# 큰 XLSX 셀 편집·복원·개인 초안

고정 v666 ZIP의 `Confectory-v666/dist/resource-edit.js` XLSX 편집을 따른다.
원본은 `XLSX 내용 수정`, `수식 셀 · 읽기 전용`, `보호된 워크시트는 읽기 전용입니다.`를
표시한다. 게시98aa9945에서 생성한 약2MiB XLSX가 미리보기만 가능한 것을 실제 재현했다.
이미 보관 가능한1–4MiB XLSX의 셀 편집/저장/직전 내용 복원/개인 입력 복구를 한 단위로 연결한다.

## 원본·보호 경계

기존 worksheet/cell DOM·시트 선택·문체·CSS·수식/보호/병합 거절을 그대로 재사용한다.
숫자/boolean·앞자리0·수식처럼 보이는 literal text와 Unicode 처리, 다른 시트의 실제 수식
보존 및 원본 프로그램에 재계산을 요청하는 기존 calcPr/캐시 제거를 유지한다.
직접 수식 계산이나 Office 앱 실행을 구현했다고 하지 않는다.
기존30시트·30열·100행 표시,4096개/98,304 UTF16 변경 문자열 한도와 XML/ZIP/Worker 수명은 유지한다.

기본1MiB save-content/text/Office 편집과 기존 DOCX4MiB 지원은 유지한다.
새 optional xlsxContent cap을 확인한 XLSX만 source/output4MiB를 명시한다. Worker는 기존
entry8MiB/총16MiB archive, XML당2MiB·선택 XML총4MiB/64개·XML DOM/깊이 제한과
CRC/길이/경로/중복/겹침·symlink/암호화/ZIP64/서명/매크로 거절을 유지한다.
원본 ZIP을 실행/외부 요청하지 않고 바뀐 worksheet/workbook XML만 다시 압축한다.
수정하지 않은 local 압축 record와 central metadata는 offset 외에 유지한다.

새 native save-xlsx-content는 기존 import generation·원본 hash·compound revision·활성
ProjectContext를 고정한다. 기존 정규화 save-content receipt와 원자 CommitPlan 최종CAS로
같은 명령의 재확인이 backup을 두 번 변경하지 않는다. immutable import와 OS 원본은 수정하지 않는다.
내용은 기존 sidecar slot의 version2/format xlsx-v1로 저장하며 current/backup 각각4MiB,
snapshot12MiB·전체 current64MiB/두 사본128MiB를 유지한다. 다른 version2 format으로
묵시 변환하지 않는다. 표시 이름 변경은 문서 형식 변환 권한이 아니다.

## 개인 입력·전송·호환

새 xlsx-parts-v1 private codec은 DOCX와 기존 소유 upload/부분 관측·receipt 방식을 공유한다.
upload target draft-xlsx와 codec을 정확하게 묶고 기존 draft-docx/형식을 유지한다.
private 요청7MiB·chunk1MiB·header/개별 관측 RPC2MiB·snapshot12MiB다.
원래 import upload6,000,000B, immutable import/선택4MiB·64개와 공통 CommitPlan16MiB는 그대로다.

같은 기존 read-only endpoint를 사용하되 transfer encoding은 XLSX 전용이다. 각 조각과 전체
SHA/canonical base64·project/ID·private snapshot·순서/길이·최종 읽기를 확인한다.
유실 private commit은 wire/value 영수증으로만 관측하고 자동 replay/rebase하지 않는다.
실제 문서 Save는 지속 private pending의 캡처된 bytes/command를 명시적으로 적용한다.
새 입력은 별도 변경으로 유지하며 실패/충돌/취소/프로젝트 전환/재시작 경계를 보존한다.
불완전/손상/다른 형식이나 소유자의 데이터는 거절한다. busy만 같은 기준의 제한된 RO 재관측을 한다.

이전98aa reader는 새 XLSX content format/private codec을 명시적으로 거절할 수 있다.
작은 v1 XLSX와 기존 DOCX는 유지하며 자동 축소/비우기/이행하지 않는다.
rollback ZIP의 복원 가능성과 새 데이터의 구 parser 호환은 구분한다.
권한/계정 정책·공개/override 계약·사용자 C# bytes·원본 UI 레이아웃은 바꾸지 않는다.

생성한 유효 약2MiB XLSX의 실제 Linux engine/Chromium UI,4MiB ZIP module 경계와
4MiB 불투명 PK bytes의 native CAS/전송 경계를 분리해 검증한다. 미참조 고엔트로피 media는
복잡한 실제 Excel 문서 전체 호환·성능의 증거가 아니다. LF/CRLF·새 교차 패키지/전체 복원,
DOCX·작은 XLSX·Office/text 회귀와 최신/롤백·증거·소유 임시 정리를 최종 기록에서 마감한다.

초기 빈 화면과 역사적 공개 cold 실패 원인은 미확정이다. 실제 Windows/WebView2·모바일·
DPI/IME·Office 앱·GPU/물리 오디오·전체UI·Space/Library는 미실행/미완료로 구분한다.
4MiB 초과/보관량·실제 신원/권한 backend·종류 C#표현/사용중삭제 대응·현재 예산 밖 custom
출력은 별도 고정 잔여다. M11/M12/M4나 선택적 조합을 새 잔여로 다시 늘리지 않는다.
