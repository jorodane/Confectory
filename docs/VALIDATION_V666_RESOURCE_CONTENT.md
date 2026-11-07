# V666 텍스트 자료 내용·이전 저장 복원 검증

최종 테스트 코드 `99fbfbcc4c02b761c0e36331fbce88913d3dc7fe`. 원본 기준은 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`(SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)이다. 구현 의미/저장 계약/지원 한계는 [V6_RESOURCE_CONTENT](V6_RESOURCE_CONTENT.md)를 따른다. 이 코드 이후에는 검증 결과 문서만 갱신한다.

| 구분 | 신규 실행 | 동등 근거 재사용 | 합계 |
|---|---:|---:|---:|
| 독립 LF checkout | 11 | 14 | 25 |
| 독립 CRLF checkout | 11 | 14 | 25 |
| 새 패키지·전체 복원·수명 | 7 | 1 | 8 |
| 합계 | **29** | **29** | **58** |

각 checkout은 `--no-hardlinks`, 독립 Git·NuGet 복사본·SDK home·빈 engine cache에서 시작한다. SDK10.0.401과 seed 전체 identity를 확인했다. 최종 코드의 LF/CRLF 에디터 빌드와 내용 편집 UI, 새 Windows 교차 패키지 생성/검사, 생성본 UI, 전체 SHA/CRC/파일 모드 복원, 복원본 UI, 실패 패키징 수명은 **새로 실행**했다.

재사용29건은 동일 native 코드/fixture/SDK 입력의 provider·최종CAS·개인 draft, 기존 삭제/이름/미리보기/import, 일반 C# 소스 회귀 및 owned IPC 수명이다. 관련 원본 기록/ZIP SHA와 선택한 통과 행을 각 `*.reused.json`에 보존했다. 마지막 제품 차이는 자료 편집창의 성공 재확인 후 refresh와 복원 중 편집 진입/버튼 제어뿐임을 정확한 module/manifest diff로 확인했다. 일반 C# 회귀는 resource 창/endpoint를 사용하지 않으며 소스·실행/override 계약·권한/ReviewConfirm과 native 코드는 동일하다. 변경된 내용 편집 UI 검사를 재사용하지 않았다.

실제 검증한 사용자 흐름:

- 텍스트·코드 사본의 내용 수정/저장과 현재 metadata/read, 직전 내용 복원·복원 취소. 원래 import bytes/proof와 OS 원본·다른 자료/C# source는 바꾸지 않는다. UTF8/BOM·UTF16BE·CRLF 실제 UI 및 12개 BOM/newline codec 조합과 잘못된 인코딩 거절을 확인했다.
- 수정 중 닫기에서 계속 편집/수정 취소, Escape 취소와 Ctrl+S, 개인 draft cold 복구, readonly 쓰기 실패 후 원본/입력 유지와 cold 명시 재시도. 복구는 확인된1MiB 이하 입력에 적용한다.
- 실제 성공 응답 유실의 같은 command 재확인, 저장 중 더 늦은 입력 보존과 그 후 별도 명시 저장, 재시작 후 성공 재확인에서 편집 모드 종료. 복원 중/미확정 복원에서 새 편집을 막고 정확한 재확인이 두 번 toggle하지 않음을 확인했다.
- 동료 내용 변경 전/후 stale 기준 거절, refresh/retry/cancel의 무암묵 rebase, 같은 namespace의 다른 실제 프로젝트가 개인 입력을 이어받지 않음과 원래 프로젝트 왕복.
- 1MiB 현재 입력과 별도1MiB 미확정 제출의 전송/독립 복구가 기존2MiB request/result 제한 안에서 동작한다. 사용 중/변경된 private snapshot은 거절하며 다른 입력을 덮지 않는다.
- manifest/identity/original copy/layout/표시명/삭제 기록/내용 파일의 최종 CAS, 저장 후 주입 실패 역순 복구. 삭제 중 내용 tombstone 쓰기 실패도 current/backup 및 다른 sidecar를 byte 단위 복구한다. 명시 삭제 후 새 import 세대가 이전 편집본을 채택하지 않음을 확인했다. 개인 입력의 generation 바인딩도 구현했지만 같은 ID 새 세대의 모든 UI 조합을 실행했다고 표시하지 않는다.
- 기존 삭제·파일 이름·자료 보관/미리보기 및 일반 C# Undo/Redo/취소·cold·Review→Confirm·실행·늦은 입력 보호를 영향에 맞춰 검증/재사용했다. 생성본/전체 복원본 모두 내용 편집 및 수명을 새로 확인했고, 복원본 다중 삭제도 새로 실행했다.

중간 실패도 보존했다. 초기 standalone private draft 계획의 `checks` 누락과 cold 성공 재확인의 UI refresh 누락을 수정했다. 소비자 fixture LINQ 참조 누락 및 UI probe의 잘못된 read 경로는 검사 결함으로 구분해 수정했다. source 갱신으로 중단한 실행은 성공 실행으로 합산하지 않는다. 모든 최종 행은0 종료이고 앞선 실패/중단 기록은 아래 근거에 유지한다. 정상/편집 모드 PNG를 실제로 확인했으며 authored panel/textarea/settings 배치를 유지했다.

기록: `/workspace/artifacts/v536-verification-managed/runs/a6aa1e94e7804c359b5abfd17811382f.json`

증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/a6aa1e94e7804c359b5abfd17811382f.zip`

SHA256: `a2f754cfe1263aeec99a0477d0fbe891721f607857a7b92c6fd820cc7fd8f1a9`

원본/재사용/앞선 실패와 공간 집계: `/workspace/scratch/v666-resource-content/FINAL-METRICS.json`

주입용 초기 자체 fixture11개도 전체 SHA/CRC/모드와 로그를 보관한 뒤 생성 소유권/종료를 확인해 정리했다. 기존 원본·과거 캐시·로그·프로필·사용자 자료는 삭제하지 않았다.

| 지속 보관 | 출처 commit | ZIP bytes | 파일/디렉터리 | archive SHA256 | 전체 manifest SHA256 |
|---|---|---:|---:|---|---|
| latest | `99fbfbcc4c02b761c0e36331fbce88913d3dc7fe` | 51932541 | 2500/153 | `51a7f30dcbcc593833d69d60c08d9762048c6b6a0505b5739f718feb5faed2c9` | `c66dd0e83dd2ce9b594012ddd80a9cee166c435091b32ef029645597c0d43fde` |
| rollback | `14c507d51b37020e7e85ff67f9457608be4968e2` | 51921163 | 2499/153 | `408db721c95b3bc0bdcbf06494c5f265f7eb881c2bd3b421dba967aa68ed3f91` | `ce15b2b85cd4428928ef46f7cc3a313294a63a831e839a244c0aadf9fcb4e992` |

패키지는 `/workspace/artifacts/v536-verification-managed/packages/index.json`의 승인된 두 세대 보관으로 승격했다. 유일한 검증본을 RAM에만 남기지 않았고, 최종 검증 임시 root는 제거됐다. 관리되는 실패 수명·재시작/증거 보존도 확인했다.

최초 여유 약1178.72MiB, 요구 persistent 예산144MiB(안전64MiB 포함)를 유지했다. 최종 실행의 디스크 순증가 **2.43MiB**, 앞선 실패/중단 기록·초기 fixture 보관까지 포함한 이번 단위 관측 순증가 **14.91MiB**, 집계 시 여유 **1163.81MiB**다. 단계 중 관측 cgroup peak는 **4.88GiB**이며 앱 단독 RAM 사용량을 뜻하지 않는다. 재현 가능한 임시 복사본이 실행별로 남지 않음을 확인했지만 이후 모든 단위의 증가량을 같은 값으로 보장하지 않는다.

Office 내용 편집, 기타 원본 rich preview, 자료 설명·큰/다중 import·현재 폴더 첫 import 결합·배치 진입은 고정 잔여다. 초기화 간헐 빈 화면은 원인 미확정이다. 실제 Windows/WebView2·모바일 실행, 전체 UI 검증과 Space/Library 전달은 이번 교차 패키지/자동화 검증으로 완료 처리하지 않는다. 새 내용 sidecar를 모르는 과거 reader/rollback은 현재 편집본을 표시하지 못하며 자동 migration/새 권한 정책은 추가하지 않는다. main은 사용자 검토/merge 대상으로 유지한다.
