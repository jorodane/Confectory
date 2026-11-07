# v666 자료 설명 검증

최종 제품 동결: `d6f7befeb5f63b0be6b5542d8fd00871c7dae833`. 이후 게시 커밋은 문서만 추가하며 제품 바이트는 같다.
총 **57단계(신규57·재사용0)**: LF21, CRLF21, 새 패키지·전체 복원·실패 수명관리 및
추가 이미지 회귀15. 이전 실패 실행의 통과 결과를 최종 통과 수에 재사용하지 않았다.

| 구분 | 실제 확인 |
|---|---|
| 독립 LF/CRLF | 각각 독립 Git objects/checkout, HOME, NuGet, engine cache; Release/MCP/engine 생성과 source/ABI 경계 |
| 새 설명 UI | LF10·CRLF9 흐름; 실제 Linux engine/Chromium, 새 패키지10·전체 복원9도 새로 실행 |
| 관련 회귀 | 파일 이름/폴더/다중 삭제/텍스트 내용 복구/PDF/Office와 일반 C# Review→Confirm/CAS/실행/늦은 입력 복구 |
| 이미지 추가2 | 최종 ZIP 전체 SHA/모드 복원 후 PNG 설명 저장이 픽셀/기존 Blob URL을 유지; 정지 PNG/JPEG·거절·닫기·cold/project 수명 |
| 보관·실패 | 전체 파일 SHA256/ZIP CRC/디렉터리·파일 모드, 실패/FIFO/자식 종료 후 증거 내구 보존·owned 임시물 정리 |


검증 대상은 파일·카테고리 Data 설명, 미리보기 설정 설명과 현재 폴더 설명 검색이다.
저장소 v666 ZIP의 app.js에 노출된 흐름으로 한정했다. Office 내용 편집이나
큰 파일 한도·mesh renderer·소스/권한 계약 변경은 이 단위에 포함하지 않는다.

실제 Linux engine/Chromium에서 입력 Undo/Redo·Escape, Enter/blur, 줄바꿈·공백,
파일/폴더 저장과 검색, 실제 쓰기 거절/재시도, 성공 응답 유실/동일 영수증 재확인,
늦은 입력의 별도 저장, 동시 편집 CAS 거절과 명시 취소, 취소 중 늦은 입력,
닫기 보호를 검증했다. CRLF에서는 비공개 초안/미확정 요청의 cold engine 복구,
자동 저장 없음, 프로젝트 왕복/같은 namespace 격리와 삭제/재가져오기 ID 세대의
입력 격리를 추가 검증했다. 아래 최종 기록으로 완료를 확정했다.

production C# Snapshot/CommitPlan/WriteAtomic/Lease 및 원본 Layout/Request를
별도 controlled-race consumer에서 실행한다. manifest/identity/resources/layout/
이름/설명 변화와 쓰기 실패를 최종 CAS에서 거부하고 호출 입력/타 writer를 보존한다.
파일/폴더 설명·clear·정확 재시도·command 재사용·세대·1000자 한도·tamper와,
설명 제거 뒤 실패하는 다중 삭제의 원자 복구 및 ID 재사용을 확인했다.
이 검사는 실제 독립 팩 consumer·engine UI 검사와 구분한다.

개발 중 실패는 증거 ZIP과 manifest로 보존했다. (1) 초기 연결의 view getter
조기 평가를 고쳤다. (2) 문자 Undo 단위를 단어 전체로 가정한 검사,
(3) 접힌 창을 다시 펼치지 않은 검사, (4) 이전 작업 종료 전에 blur를 실행한
검사 경계를 수정했다. 취소/응답 유실 중 늦은 입력과 분리된 DOM 바인딩도
보호했다. 기존 간헐적 초기화 #app 빈 화면의 원인 해결로 표현하지 않는다.

실제 Windows/WebView2·모바일 기기, 전체 UI, Space/Library 전달은 미실행이다.

증거:

- 최종55단계: `/workspace/artifacts/v536-verification-managed/runs/3e4d436bb0eb429c9f61340d5afeb381.json`
- 증거 ZIP SHA256: `a9d17e9a0eff9023691a8c823b57ce6178db77b68d4a992ad81e6de88369c974`
- 추가 이미지2단계: `/workspace/artifacts/v536-verification-managed/runs/c8c08697dc1a44a69dc6f1f91bad6824.json`
- 추가 증거 ZIP SHA256: `e4c7fcd780ac033e9ff7a8300d2cab0a45ae2212ccc94e906e2797f8d6139f47`
- 두 최종 실행과 앞선 실패4개 모두 manifest/ZIP 검증 및 `cleaned`, 각 owned root 부재를 확인했다.
- 개발용 C# probe4개는 생성 source/input/출력을 별도 ZIP/SHA로 보존한 후 정확한 자체 tmp만 정리했다.

| 지속 보관 | 출처 제품 커밋 | ZIP SHA256 | ZIP bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `d6f7befeb5f63b0be6b5542d8fd00871c7dae833` | `56265618751f3afade26fdd642866079da9facac10af5f2df7e096364a30e632` | 53,779,948 | 2696/158 |
| rollback | `e62d72ef27c774cfde708e0708bbfece2617f171` | `a5a52c6f7bd17d9416298a1fd5419357dfa21ca917c21e2d8329ce989697d1f8` | 53,775,706 | 2695/158 |

보관 index: `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest 전체 manifest SHA256: `c23964e2d6f2131f4d667e9021d7b7226f1921920541ae72851f25bc554b56bd`.
rollback 전체 manifest SHA256: `ae10f95530a94f626bc94b4f4184f9c72e1faa88ddd586d9b30663a9efa5d556`.

공간: 시작 여유 1,171,222,528B, 결과 수집 시
1,156,698,112B(약 1.08GiB), 이번 단위 전체 순증가
14,524,416B(약 13.9MiB)다.
실패/개발 증거와 Git 변경을 포함한 값이며 정상 반복 단위당 증가량의 보장값이 아니다.
최종55단계 실행 자체 순증가 7,929,856B와 추가 이미지 실행 순증가
499,712B를 별도로 기록했다.
사전 계획은 candidate56+증거20+코드/Git8+안전64=148MiB, RAM 작업공간3GiB와
512MiB 여유, 추가 메모리7GiB+안전1GiB를 유지했다.
명령 단계에서 표본 측정한 최소 여유 1,157,185,536B와 환경 cgroup peak
5,385,662,464B는 기록값이며 archive 압축/승격 순간 전체 최저의 직접 측정값은 아니다.
과거 보관자료·SDK·원본·사용자 데이터 정리는 하지 않았고 승인된 owned tmp와
관리형 latest/rollback 교체만 적용했다.

새 설명 sidecar가 없는 프로젝트의 revision은 기존 코드와 같음을 확인했다.
새 설명 작성 후 과거 rollback 실행본으로 metadata를 편집하면 새 CAS/삭제 시 제거를
보장할 수 없으므로 지원하지 않는다. 이는 원문 store 자동 이행이나 과거 패키지
수정으로 숨기지 않는다. 큰 파일·Office 내용 편집·원본 mesh 범위 및 그 밖의 고정
수용 잔여는 그대로 남긴다. 기존 간헐적 초기화 빈 화면은 원인 미확정이다.
