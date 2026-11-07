# v666 DOCX 문단 편집 검증

최종 동결: `179dae7ffba940cae62ab1c6cb2c6b9becdb077d`. 게시 후속은 문서만 바꾸며 제품/검사 코드는 같다.
총 **67단계(신규67·재사용0)**: LF25, CRLF25,
새 패키지·전체 복원·실패 수명관리17. 앞선 실패 실행의 통과 결과는
최종 통과 수에 재사용하지 않았다.

| 구분 | 실제 확인 |
|---|---|
| 독립 LF/CRLF | 독립 Git objects/checkout, HOME, NuGet, engine cache; Release/MCP/실제 Linux engine 생성과 원본/계약 경계 |
| DOCX ZIP/DOM | 실제 표준 압축 stream/Worker, stored/DEFLATE/descriptor, 전체 CRC, Unicode/run/section/표/보호 필드, Python zipfile/XML 독립 판독과 미수정 parts/압축 record 보존 |
| 실제 DOCX UI | LF 8흐름·CRLF 7흐름; 새 패키지와 전체 복원본에서도 각각 정상/수명 흐름을 새로 실행 |
| 실제 native 저장 | 독립 팩 consumer와 production Snapshot/CommitPlan/WriteAtomic/Lease의 최종 CAS; 기존 텍스트 저장 및 DOCX bytes/current/backup/영수증/권한·MIME 거절 |
| private 초안 | 실제 C#에서 1MiB ZIP·최악 escape 98,304 UTF-16 입력·2MiB 전송/4MiB 기록 한도, pending bytes 재구성과 늦은 입력/정확 요청 보존 |
| 관련 회귀 | 설명·검색, 텍스트 내용, Office/PDF/이미지, 다중 삭제·파일 이름, 일반 C# 저장의 Review→Confirm/CAS/Undo/Redo/cold/늦은 입력 |
| 보관·실패 | 새 Windows 교차 패키지의 구조/프로브·전체 파일 SHA/ZIP CRC/파일 및 디렉터리 모드 복원, FIFO/예외/자식 종료/증거 내구 보관/owned 임시물 정리 |

원본 근거는 저장소 v666 ZIP의 `resource-edit.js` DOCX 문단/표 editor와
`changeWordParagraph`, 백업 복원 흐름이다. SHA256
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`을 유지한다.
[지원 경계](V7_RESOURCE_DOCX.md)에 따라 1MiB 이하 DOCX 중 UTF-8 document.xml의 문단·표 텍스트만
편집한다. 전체 Word 서식 편집이나 XLSX 편집·큰 파일·mesh renderer로 확장하지 않았다.

실제 Linux engine/Chromium에서 입력/close Keep·명시 취소가 import 원문을 바꾸지 않는지,
Save와 직전 ZIP 복원/복원 취소가 정확한 바이트 세대를 보존하는지 확인했다.
쓰기 실패/권한 거절과 정확 재시도, 압축 중 늦은 입력의 별도 저장, native 성공 응답 유실
뒤 동일 command 재확인(추가 backup 변경 없음), peer metadata 변경 최종 CAS 거절·명시 취소,
접기 중 Worker 종료/늦은 응답 무시/펼치기 복구를 확인했다. CRLF와 전체 복원본에서는
미저장 문단·미확정 요청의 cold engine 복구(자동 Save 없음), 프로젝트 이탈 전 private 입력
flush·돌아오기, 같은 namespace의 다른 실제 프로젝트 격리를 확인했다.

미수정 ZIP 항목의 local header/압축 bytes/descriptor는 그대로이고 central offset만 보정한다.
잘못된 CRC·opaque record·중복/경로 위장·암호화/ZIP64·전개 예산 초과, 서명/매크로와
보호된 문단·위조 문단 키·DTD/entity·잘못된 XML 문자는 편집을 거절한다.
원래 import, C# bytes/ID/공개·override 계약, 외부/부모 원본·권한 및 일반 저장 경계를
보존한다. 확인/최종 CAS를 약화하거나 문서 링크·외부 관계를 실행/조회하지 않는다.

개발 검사는 최종 수에 더하지 않았다. 별도 C# 개발 2단계와 DOM 개발 자료를 보존했다.
첫 동결 실행의 독립 팩 fixture에서 `SequenceEqual`을 extension 없는 문맥으로 호출한
CS0411이 발생했고, 명시 `System.Linq.Enumerable.SequenceEqual`로 검사만 고쳤다.
그 뒤 최종 동결 전체를 새로 검사했다. 이 실패를 제품 저장 결함으로 분류하지 않는다.

증거:

- 최종 실행: `/workspace/artifacts/v536-verification-managed/runs/25e0ed77cf744704b170df29bfef7cc6.json`
- 증거 ZIP SHA256: `b696cb368f73b891124594ccea02e3e7a297acdef77ff9f6b3f36a76c6684508` (5,482,710B)
- 앞선 실패 실행: `/workspace/artifacts/v536-verification-managed/runs/793c5455c58043cc866288d6e26f1797.json`
- 최종/실패 실행은 증거 ZIP·전체 manifest 검증 후 `cleaned`; 각 owned root 부재를 확인했다.
- 개발 C# 기록: `/workspace/artifacts/v536-verification-managed/runs/1eb909d1615e45c696bd12e80689aeed.json`
- DOM 개발 자료: `/workspace/scratch/v666-resource-docx/development-dom.zip`, SHA256 `23922c2296ba039ec1a243f034543e930bf22364c95af92e5b523abfafdc2df4`

| 지속 보관 | 출처 동결 커밋 | ZIP SHA256 | ZIP bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `179dae7ffba940cae62ab1c6cb2c6b9becdb077d` | `fc9e0e69a643d2f8fbf9307b9a61346d4f6c2147d2c0f8ca87cfcb453e7e345c` | 53,790,686 | 2700/158 |
| rollback | `d6f7befeb5f63b0be6b5542d8fd00871c7dae833` | `56265618751f3afade26fdd642866079da9facac10af5f2df7e096364a30e632` | 53,779,948 | 2696/158 |

보관 index: `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest SHA256: `5b2029fc583963dcd1919e3e503dd59e74eae53b7bd666ce1a4cc8cf7aab986c`.
rollback manifest SHA256: `c23964e2d6f2131f4d667e9021d7b7226f1921920541ae72851f25bc554b56bd`.
검증된 압축본의 전체 SHA/모드 복원 뒤 packaged engine UI와 restored engine UI를 각각
실행했다. latest/rollback 교체는 기존 관리형 원자 승격이며 과거 보관자료 삭제는 하지 않았다.

공간: 시작 여유 1,156,612,096B, 결과 수집 시 1,145,978,880B
(약 1.07GiB), 이번 단위 전체 순증가 10,633,216B
(약 10.1MiB). 실패/개발 증거와 Git 변경을 포함한 값이며
정상 반복 단위당 증가량의 보장값은 아니다. 최종 실행 자체 순증가는 7,299,072B다.
사전 예산 candidate56+증거20+코드/Git8+안전64=148MiB, RAM 작업공간3GiB와 여유512MiB,
추가 메모리7GiB+안전1GiB를 유지했다. 명령 단계의 표본 최소 여유 1,153,183,744B,
환경 cgroup peak 5,426,851,840B는 기록값이며 압축/승격 순간 전체 최저 직접 측정은 아니다.
승인된 해당 실행 owned 임시물 정리와 latest/rollback 교체만 수행했다.

구버전 private parser는 새 `docx-v1`/changes를 읽지 못한다. 새 DOCX 초안이 있는 상태를
과거 실행본으로 편집하는 것은 지원하지 않으며 자동 이행/과거 패키지 수정으로 숨기지 않는다.
XLSX 내용 편집, 1MiB 초과 자료, 다른 원본 형식·mesh 범위와 나머지 고정 수용 항목은 남는다.
기존 간헐적 초기화 빈 화면은 원인 미확정이다. 실제 Windows/WebView2·모바일·Word 앱의
서식 호환 실행, 전체 UI, Space/Library 전달은 미실행이며 교차 패키징/자동화와 구분한다.
