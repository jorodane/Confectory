# v666 XLSX 셀 값 편집 검증

최종 동결: `55b1d1ffdfc88c8cfb72be2e12be68efc901d050`. 이후 게시 후속은 문서만 바꾸며 제품/검사 코드는 같다.
총 **77단계(신규77·재사용0)**: LF29, CRLF29,
새 패키지·전체 복원·실패 수명관리19. 개발 검사는 최종 통과 수에 더하지 않았다.

| 구분 | 실제 확인 |
|---|---|
| 독립 LF/CRLF | 독립 Git objects/checkout, HOME, NuGet, engine cache; Release/MCP/실제 Linux engine 생성과 원본/계약·자산 경계 |
| XLSX DOM/Worker | 실제 Chromium의 워크시트 선택·원래 셀 필드, 숫자/boolean/문자/새 leading-zero 문자열·수식처럼 보이는 literal, 보호 시트/수식/병합/위조 키/DTD 거절 |
| 독립 파일 판독 | Python ZIP CRC/XML 판독, 원래 styles/속성/병합/수식/shared strings, 수정하지 않은 압축 local records/central metadata·주석 보존, 다른 시트 수식 캐시 제거와 재계산 속성 |
| XLSX engine UI | LF11·CRLF7흐름; 새 패키지와 전체 복원본에서도 각각 정상/수명 흐름을 새로 실행 |
| native/API | 독립 팩 consumer의 실제 byte 저장·정확 복원·receipt·MIME/크기/충돌 거절과 production 최종 CAS; private 최대1MiB+4,096개 변화+98,304 UTF-16 최악 escape 입력/전송·기록 예산 |
| 기존 기능 회귀 | DOCX ZIP/DOM/native/private/UI, 설명·검색·텍스트 내용, Office/PDF/정지 이미지, 다중 삭제·파일 이름, 일반 C# Review→Confirm/CAS/Undo/Redo/재시작·늦은 입력 |
| 보관·실패 | 새 Windows 교차 패키지 구조/프로브, 전체 SHA/ZIP CRC/파일·디렉터리 모드 복원, FIFO/예외/실패·자식 종료 뒤 증거 내구 보관과 owned 임시물 정리 |

기준은 저장소 v666 ZIP의 `resource-edit.js` XLSX 분기다. SHA256
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`을 유지한다.
[지원 경계](V7_RESOURCE_XLSX.md)에 따라 1MiB 이하 사본의 기존 화면에서 셀 값만 편집한다.
원본 CSS/미리보기·설정 배치, 프로젝트 소유권·읽기/쓰기 검증, 원본 import와 C#·공개/
override 계약은 그대로다. 실제 Excel 계산이나 서식/시트/수식 편집으로 표현하지 않는다.

실제 Linux engine/Chromium에서 close Keep/취소·입력 보관과 원본 bytes 불변,
Save·직전 내용 복원/복원 취소의 byte 세대를 확인했다. 워크시트 왕복 후 여러 셀의
숫자·boolean·새 문자 값을 한 Save로 저장하고 보호 시트의 readonly를 확인했다.
실제 쓰기 거절/정확 재시도, 압축 중 늦은 셀 입력의 별도 저장, native 성공 응답 유실
뒤 같은 command 재확인(추가 backup 변화 없음), peer metadata 최종 CAS 충돌/명시 취소,
접기 중 Worker 종료/늦은 응답 무시/펼치기 복구를 확인했다. CRLF/전체 복원본에서는
미저장 입력·미확정 요청의 cold engine 복구(자동 Save 없음), 프로젝트 이탈 전 private
flush와 왕복, 같은 namespace의 다른 실제 프로젝트 격리를 확인했다.

수식은 실행하지 않는다. 원본과 같이 오래된 수식 v 캐시를 제거하고 workbook 재계산
속성을 기록하며 수식 XML·병합 구조·style 속성을 보존한다. 미수정 ZIP 항목은 압축 bytes를
그대로 복사하며 수정한 시트/수식 캐시가 있던 시트/workbook만 다시 압축한다.
원본 파트/이미지/외부 관계는 유지하고 URL·스크립트·매크로를 실행/조회하지 않는다.
코드 점검 후 실제 engine에서 변경을 원래 값으로 되돌린 Save가 현재 bytes/hash는 같아도
직전 복원본을 바꾸는 결함을 재현했다. 변경 없는 경우 native 저장을 건너뛰고 private 입력만
확인하도록 수정했으며, 확인 중 늦은 입력은 별도로 남긴다. XLSX와 DOCX의 정상 UI에
복원본/영수증 불변과 늦은 입력의 다음 명시 저장 회귀를 각각 추가했다. 수정 전 실행은
증거를 보존하고 종료했으며 최종 수에 재사용하지 않았다. 재현 기록은
`/workspace/artifacts/v536-verification-managed/runs/838ac3a91b6e4d3cabd40238c98455ff.json`이다.
공통 저장 컨트롤러와 ZIP writer 변경의 영향을 기존 DOCX 전체 회귀로 별도 검증했다.
최대 초안 검사는 실제 UI 파일 형식 검사와 다른 production C# private consumer다.

증거:

- 최종 실행: `/workspace/artifacts/v536-verification-managed/runs/acf81ac09c2a4d999812a3b536e9019b.json`
- 증거 ZIP SHA256: `484d4cdbfd76a34e404787f8bafe2913b3645df4845d6b890c42d6a7728b7f68` (6,270,326B)
- 최종 실행은 전체 증거 manifest/ZIP 검증 후 `cleaned`; 해당 owned root 부재를 확인했다.
- 개발5단계: `/workspace/artifacts/v536-verification-managed/runs/c9f29fadea174e5094561b44b19d8f5e.json`
- 개발 DOCX Node ZIP 검사도 통과했으나 최종 수에 추가하지 않았다.

- `/workspace/artifacts/v536-verification-managed/runs/37bbebc4e74a47188ad0a54b5891ac87.json`: 수정 전 검증 종료, 통과 단계는 최종 수에 재사용하지 않음

| 지속 보관 | 출처 동결 커밋 | ZIP SHA256 | ZIP bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `55b1d1ffdfc88c8cfb72be2e12be68efc901d050` | `e977fd848fcfeecb35c87b2cdcae46fce006dba38746d68d806ca3f5e9bfbead` | 53,798,299 | 2703/158 |
| rollback | `179dae7ffba940cae62ab1c6cb2c6b9becdb077d` | `fc9e0e69a643d2f8fbf9307b9a61346d4f6c2147d2c0f8ca87cfcb453e7e345c` | 53,790,686 | 2700/158 |

rollback은 이전 검증본이며 이번 DOCX 동일값 Save 복원본 보호 수정이나 XLSX 편집은 포함하지 않는다.
새 private codec 비호환과 과거 DOCX 동일값 Save의 복원본 교체 제한을 가진 이전 실행본으로 구분하고,
과거 패키지를 수정하거나 새 수정이 들어 있다고 표현하지 않는다.

보관 index: `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest SHA256: `58027fe5e10cf1cb2b88f20057dbb6bfa596f816dda81531b38838d87e21c66e`.
rollback manifest SHA256: `5b2029fc583963dcd1919e3e503dd59e74eae53b7bd666ce1a4cc8cf7aab986c`.
압축본 전체 SHA/모드 복원 후 packaged engine UI와 restored engine UI를 각각 실행했다.
기존 관리형 원자 승격과 해당 실행 owned 임시물 정리만 사용했다.
과거 보관자료·원본·SDK·Git·로그·프로필·사용자 데이터의 추가 정리는 하지 않았다.

공간: 시작 여유 1,145,856,000B, 결과 수집 시 1,131,372,544B
(약 1.05GiB), 이번 단위 전체 순증가 14,483,456B
(약 13.8MiB). 개발/실패 증거와 Git 변경을 포함한 값이며
향후 단위당 증가량 보장은 아니다. 최종 실행 자체 순증가는 8,257,536B다.
사전 예산 candidate56+증거20+코드/Git8+안전64=148MiB, RAM 작업공간3GiB+여유512MiB,
추가 메모리7GiB+안전1GiB를 유지했다. 명령 단계 표본 최소 여유 1,139,507,200B,
환경 cgroup peak 5,458,038,784B는 압축/승격 순간 전체 최저 직접 측정으로 표현하지 않는다.

구버전 parser는 새 `xlsx-v1` private codec을 읽지 못한다. XLSX 초안이 있는 상태를
과거 패키지로 편집하는 것은 지원하지 않으며 자동 이행·원본 수정으로 숨기지 않는다.
큰 파일/선택 전체1MiB 초과·다른 원본 형식/mesh 범위와 나머지 고정 잔여는 남는다.
기존 간헐적 초기화 빈 화면은 원인 미확정이다. 실제 Windows/WebView2·모바일·Excel 앱의
계산/호환 실행, 전체 UI·Space/Library 전달은 미실행이며 자동화/교차 패키징과 구분한다.
