# V666 카테고리 첫 자료 보관 검증

최종 테스트 코드 `6fdb09f1e9996836bfb844915c12bf6a46104603`. 원본은 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`(SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)의 `app.js::importResourceFiles(files,w,folderId)`/`resourceCreateMenu`/`bindResourceDrop`다. [선택 대상·원자 저장 계약](V6_RESOURCE_DESTINATION.md)을 따르며 이후 게시 변경은 docs뿐이다.

| 구분 | 신규 실행 | 동등 근거 재사용 | 합계 |
|---|---:|---:|---:|
| 독립 LF checkout | 22 | 3 | 25 |
| 독립 CRLF checkout | 25 | 0 | 25 |
| 새 패키지·전체 복원·수명 | 13 | 0 | 13 |
| 합계 | **60** | **3** | **63** |

최종 신규 행은 모두0 종료다. 각 checkout은 `--no-hardlinks`, 독립 Git/NuGet 복사본·SDK home·빈 엔진 cache에서 시작하고 SDK10.0.401/seed identity와 LF/CRLF canonical bundle SHA를 확인했다. 에디터/MCP/엔진 빌드와 모든 UI, CRLF의 모든 native 검사를 새로 실행했다. 기존 단일/다중 가져오기·카테고리 배치·내용 편집/복구·그림·다중 삭제·C# Undo/Redo/취소·Review→Confirm/CAS/실행/늦은 입력도 영향에 맞춰 새로 확인했다.

재사용3건은 같은 제품 코드/검사 입력/SDK로 이미 통과한 LF의 destination provider(56개 assertion), destination CAS(27개 상황과 구 reader/writer 호환), 기존 layout provider다. 선행 실행은 이후 UI 메뉴 시간 초과로 실패했으므로 전체 성공으로 세지 않는다. 선택한 통과 행·원본 로그·전체 증거 ZIP/manifest SHA·코드와 probe/fixture/명령·SDK/NuGet/configuration/RID 동등성을 각 `*.reused.json`에 기록했다. 실패했던 UI와 그 후속 검사를 재사용하지 않았다. 최종 source의 제품 변경은 이전 source와 같고 유일한 후속 차이는 chooser 검사 준비 helper다.

새 Windows 교차 패키지 생성·구조 probe와 생성본의 destination/Root 다중 가져오기·그림·텍스트 UI, 전체 파일 SHA/CRC/모드 복원과 복원본 probe/같은 네 UI의 수명, 실패 패키징/owned IPC 증거 보존·정리를 새로 실행했다. Linux에서 실행 가능한 패키지 엔진/Chromium 검사와 실제 Windows/WebView2 실행을 구분한다.

실제 확인한 범위:

- 기존 카테고리의 자료 추가 메뉴에서 선택한 두 파일이 첫 resource store와 배치를 함께 만든다. 중첩 B의 파일을 미리보기로 읽어 원래 bytes를 확인했고 생성 File의 다른 폴더 C 드롭은 C에만 보관한다. 현재 B 화면/선택을 지우거나 임시 Root 항목을 만들지 않는다. 정상 화면 PNG도 직접 확인했다.
- 실제 두 번째 layout 파일의 쓰기 권한 거절이 앞선 resource append를 역순 복구한다. File 목록·대상 표시·정확한 요청은 보존하고 명시 재시도로만 전체를 한 번 보관한다. 실제 성공 응답 유실은 같은 파일/배치 영수증으로 재확인하며 더 늦은 검색 입력을 지우지 않는다.
- chooser가 열린 동안 대상 폴더를 제거하면 refresh/retry 후에도 원래 대상을 거절한다. Root/다른 폴더를 자동 선택하지 않으며 입력 취소는 기존 사본을 삭제하지 않는다. 선택 전체1MiB의 실제 두 File을 기존 IPC 제한 안에서 원자 보관했다.
- File read 중 탐색 위치만 바뀌면 이미 선택한 폴더/기준을 유지하고 다른 화면의 선택을 바꾸지 않는다. Home으로 나간 오래된 File read는 자동 전송하지 않으며 같은 소유자 복귀 후 명시 retry가 필요하다. 실제 cold는 확인된 파일/폴더·개인 탐색만 복원하며 미보관 File bytes/command를 레이아웃에 저장하거나 재전송하지 않는다. 동일 namespace의 다른 실제 프로젝트와 왕복도 격리했다.
- 독립 팩 소비자의56개 assertion은 잘못된 마지막 항목/대상·부분 재import·stale 폴더 alias·쓰기 실패에서 두 저장본/입력을 보존하고, 기존 파일/폴더 이름·내용/backup을 바꾸지 않음을 확인한다. 삭제 import 재생성은 거절하고 명시한 같은 ID의 새 세대는 이전 내용/백업을 채택하지 않는다. manifest/프로젝트 identity bytes는 유지한다. 세부 assertion 수를 단계 수와 합산하지 않는다.
- 추출한 실제 생산 body의27개 CAS 상황은 첫 저장/기존 저장본, manifest/identity/resource/layout/이름/deletion/기존·새 내용의 마지막 경합과 첫/두 번째 쓰기 전·두 번째 쓰기 후 실패를 확인한다. 준비 단계는 쓰지 않고 최종 한 CommitPlan은 고정된 두 파일만 쓴다. 변조된 준비 경로는 commit 전에 거절한다. 이 통제된 경합 검사와 실제 DSL/UI 연결 검사를 구분한다.
- 이전 `98997e7917f51f269bbd981726258373ac5bafb9`의 Request/Layout C# body를 전체 SHA로 고정해 새 파일/배치를 읽고 명시 Move를 실행했다. 뒤의 import 재확인이 그 Move를 되돌리지 않는다. 이는 실제 이전 native body 호환 검사이며 과거 Windows 패키지의 실기기 실행을 뜻하지 않는다. 브라우저의 내부 prepare operation과 임의 plan 필드는 거절했다.

첫 UI 검사에서는 자료 추가 메뉴를 찾지 못해 첫 파일 저장 전 중단됐다. 마지막 traffic에 private presentation/chatDraft 저장이 있었고, 제품 코드를 바꾸지 않은 채 입력 blur·presentation flush·idle을 명시한 준비 경계 이후 실제 chooser/UI를 통과했다. 이를 일반 메뉴 간헐 실패의 원인 해결로 단정하지 않는다. 실패 기록과 원래 입력/로그는 `8c7b83358c314bf092614e0770981ded`에 보존했다. 개발 CAS 기록도 별도 보존한다. 초기화 빈 화면 문제와 혼동하지 않는다.

제품 차이는 Request/Layout body의 후보 준비·합성, 기존 WebInvoke의 명시 operation 허용, 자료 browser/layout controls와 bundle pin 여섯 파일뿐이다. Request의 v1 Item/Validate/영수증, Layout의 기존 operation 처리·검증, source/target·FileStream CAS/원자 저장·실제 ProjectContext/권한·원본 C#/override 계약과 기존 미리보기/편집/CSS는 diff·SHA guard로 유지했다. 새 영속 형식/자동 migration/외부 권한·범용 plan 실행 endpoint는 없다. 입력 자산은 모두 생성했고 실제 OS 드롭/OS 선택 대화상자와 Playwright FileChooser/DataTransfer 자동화를 구분한다.

기록: `/workspace/artifacts/v536-verification-managed/runs/61c7f9dfdbf940b09b426a13786bb109.json`

증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/61c7f9dfdbf940b09b426a13786bb109.zip`

SHA256: `bea3a9ec76837d0282acbfdc9eda2529946ee30dac4f95f4b851890be09d1d1d`

집계·재사용·실패/개발 근거: `/workspace/scratch/v666-resource-destination/FINAL-METRICS.json`

| 지속 보관 | 출처 commit | ZIP bytes | 파일/디렉터리 | archive SHA256 | 전체 manifest SHA256 |
|---|---|---:|---:|---|---|
| latest | `6fdb09f1e9996836bfb844915c12bf6a46104603` | 51938486 | 2501/153 | `de42bdea3f8aff8a2f552669d9f7f22161672c3a649c9fc4459ac318c228b3a4` | `235130ae639c98db5b0966cf53351add20ddb2efc276b2eff07d4e1f34c55d55` |
| rollback | `991135eeec0330fd1731d0be68c85a58043f9c45` | 51937414 | 2501/153 | `c7d5c11adee124c2b525f1dc2f86416db594424919568092f6da5ea9c77ab496` | `5c4e5215439b98266e13cd5a2fcebe69f33fbdfca81c30799fd2df8676a75d42` |

최신/롤백 두 세대를 원자 승격하고 ZIP/전체 manifest를 재확인했다. 지속 증거와 생성 소유권·자식 종료를 확인한 뒤 이번 실패/최종 검사와 자체 개발 검사의 임시 root를 정리했다. 기존 원본·과거 자료·로그·프로필·캐시는 삭제하지 않았다.

최초 여유 약1151.04MiB, 추가 요구144MiB(안전64MiB 포함)를 유지했다. 최종 실행 디스크 순증가 **5.91MiB**, 실패/개발 증거까지 포함한 단위 순증가 **8.92MiB**, 집계 시 여유 **1142.11MiB**다. 단계 최소 관측 여유는1147.94MiB, cgroup peak는4.94GiB이며 앱 단독 RAM 상한이 아니다. 이후 단위의 증가량을 같은 값으로 보장하지 않는다.

큰 파일/선택 예산 확대·Office 편집·다른 원본 미리보기·자료 설명과 원본의 추가 메뉴 진입 등 다른 고정 잔여는 [수용 목록](V666_ACCEPTANCE.md)에 유지한다. 초기화 간헐 빈 화면 원인은 미확정이다. 실제 Windows/WebView2·모바일·전체 UI·Space/Library 전달은 미검증이며 main은 사용자 검토/merge 대상으로 보존한다.
