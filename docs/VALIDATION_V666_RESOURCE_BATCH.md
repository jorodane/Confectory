# V666 다중 자료 사본 원자 보관 검증

최종 테스트 코드 `991135eeec0330fd1731d0be68c85a58043f9c45`. 원본 기준은 검증한 v666 ZIP의 `Confectory-v666/dist/app.js::importResourceFiles`이며 선택 File 전부를 한 readwrite transaction에 넣는 동작에 대응한다. 기존 체크포인트 `a25a10dbc44a8179645c670b54d1068739b19e70`의 그림/내용 편집을 보존한다. [지원 계약과 한계](V6_RESOURCE_BATCH.md)를 따르며 이후 게시 변경은 docs뿐이다.

| 구분 | 신규 실행 | 재사용 | 합계 |
|---|---:|---:|---:|
| 독립 LF checkout | 20 | 0 | 20 |
| 독립 CRLF checkout | 20 | 0 | 20 |
| 새 패키지·전체 복원·검사 수명 | 11 | 0 | 11 |
| 합계 | **51** | **0** | **51** |

모든 최종 행이0 종료다. checkout은 `--no-hardlinks`, 독립 Git·NuGet 복사본·SDK home·빈 엔진 cache에서 시작하며 SDK10.0.401/seed identity와 LF/CRLF canonical bundle SHA를 확인한다. 에디터/MCP/엔진 빌드, 단일·다중 독립 팩 소비자, 최종 CAS와 자료 삭제/내용 provider, 실제 native 엔진의 다중·단일 가져오기·내용/그림·다중 삭제·C# 편집 UI를 양쪽에서 새로 실행했다. 과거 검증을 최종 행으로 재사용하지 않았다.

새 Windows 교차 패키지 생성·구조 probe와 생성본의 다중 가져오기/그림/내용 UI, 전체 파일 SHA/CRC/모드 복원·복원본 probe 및 같은 세 UI의 수명, 실패 패키징/owned IPC 증거 보존·정리도 새로 실행했다. 교차 패키지의 Linux 실행 가능한 엔진과 Chromium 검사를 실제 Windows/WebView2 기기 실행으로 세지 않는다.

확인한 사용자/저장 흐름:

- 한 File picker 선택으로 한글·동명 파일3개의 서로 다른 ID/원래 CRLF·binary bytes와 전체 선택을 확인했다. 여러 파일을 순차 append하지 않으며 잘못된 두 번째 파일 때문에 첫 파일만 남지 않는다. 실제 화면 PNG도 확인했고 기존 자료 창/도구/배치를 유지했다.
- 실제 쓰기 거절에서 저장본 전체와 선택 목록을 유지하고, 권한을 되돌린 자체 fixture의 명시 재시도는 두 사본을 한 번만 보관한다. 실제 성공 응답 유실도 정확한 항목별 command 목록으로 확인하며 새 검색 입력을 지우지 않는다.
- stale 저장 기준은 목록 refresh 뒤에도 자동 rebase하지 않는다. 입력 취소·재선택만 새 기준의 의도를 만든다. 선택 전체1MiB 초과는 전송하지 않으며 실제 합계1MiB의 두 파일을 기존 IPC 제한 안에서 보관했다.
- 삭제된 한 멤버가 포함된 이전 묶음 재시도는 전체 거절하여 사본을 되살리지 않는다. 기존 항목과 새 항목의 부분 일치도 전체 거절한다. 완전히 확인된 항목별 영수증만 무쓰기 재확인하며 기존 단일 import API도 각 영수증을 읽는다. 새 전역 그룹 ID나 자동 대상 선택 정책은 만들지 않았다.
- 두 번째 File read 중 Home 왕복은 부분 전송/자동 재전송을 하지 않는다. 같은 소유자에게 돌아와 명시 재시도할 때만 전체를 보관한다. 실제 cold에서는 미보관 bytes/command를 개인 레이아웃에서 복원하지 않으며 다시 파일을 선택해야 한다. 동일 namespace의 다른 실제 프로젝트와 원래 프로젝트 왕복에서도 선택·사본을 섞지 않는다.
- 독립 DSL 팩 소비자의 다중31개 세부 검사와 기존 단일 provider를 새로 실행했다. 잘못된 SHA/중복 ID·command/빈 선택/항목 수·합산 byte 예산/동명·원래 bytes/다음 append 후 재확인을 확인한다. 단계 수와 세부 assertion 수를 합산하지 않는다.
- 실제 생산 body의 통제된 최종 CAS 검사는 단일/다중 각각 성공·manifest/identity/store/deletion ledger 경합·write 실패의12상황을 확인한다. 한 CommitPlan의 한 resource write 전에 관측을 확인하며 실패한 선택/상대 변경을 보존한다. 이 추출 body 검사와 실제 DSL/provider·UI 연결 검사를 구분한다. 개발 단계의 같은 CAS 증거도 따로 보존했고 최종 소스에서 다시 실행했다.
- 내용 편집·직전 내용 복구·실패/충돌/응답 유실/늦은 입력·cold, 그림 픽셀/URL 수명·읽기 거절/재시작/프로젝트 격리, 기존 다중 삭제와 C# Undo/Redo/취소·Review→Confirm/CAS·실행 회귀를 새로 확인했다.

제품 변경은 ProjectResources Request body의 원자 묶음 처리·기존 WebInvoke의 해당 operation 허용·자료 browser·bundle pin 네 파일뿐이다. 기존 v1 Item/Validate·영수증 grammar와 단일 import 계약, FileStream 원자/CAS·활성 ProjectContext/권한·원본 C#/override/실행·다른 자료 UI는 정확한 diff/SHA guard로 보존한다. 새로운 sidecar나 기존 데이터 migration은 없다. 사용자 개인 파일은 선택하지 않았고 입력은 생성한 검사 자산뿐이다. OS 수준의 실제 다중 파일 drag/drop과 파일 선택 대화상자 자체는 Playwright File 입력 검사와 구분하여 미검증으로 둔다.

기록: `/workspace/artifacts/v536-verification-managed/runs/be985eb021ea4b5f8d255f77562ec423.json`

증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/be985eb021ea4b5f8d255f77562ec423.zip`

SHA256: `c0eb967fde4abeba7789e02bfcd7bedc764c73bb22476f46010f643d51611b6d`

집계/개발 CAS 기록: `/workspace/scratch/v666-resource-batch/FINAL-METRICS.json`

| 지속 보관 | 출처 commit | ZIP bytes | 파일/디렉터리 | archive SHA256 | 전체 manifest SHA256 |
|---|---|---:|---:|---|---|
| latest | `991135eeec0330fd1731d0be68c85a58043f9c45` | 51937414 | 2501/153 | `c7d5c11adee124c2b525f1dc2f86416db594424919568092f6da5ea9c77ab496` | `5c4e5215439b98266e13cd5a2fcebe69f33fbdfca81c30799fd2df8676a75d42` |
| rollback | `ee2796d8d87c049d1b08e87b72f23d269a655ea7` | 51935018 | 2501/153 | `a27a88bd203a41e4fe6aafdd90ae9295f688012ffb8d5a3b424a3695ccc1d133` | `dc54edbfc55182bf1286210f05d3f2e0bef773575aee6f1a0d3e572107705914` |

승인된 최신/롤백 두 세대 index에 원자 승격하고 ZIP/전체 manifest를 재확인했다. 지속 증거를 확보한 뒤 생성 소유권·자식 종료를 확인하여 이번 실행과 자체 개발 검사의 임시 root를 정리했다. 과거 원본·자료·로그·프로필·캐시는 삭제하지 않았다.

최초 여유는 약1157.57MiB, 추가 요구 예산144MiB(안전64MiB 포함)를 유지했다. 최종 실행 디스크 순증가 **4.78MiB**, 개발 증거까지 포함한 단위 관측 순증가 **6.44MiB**, 집계 시 여유 **1151.13MiB**다. 단계 중 최소 관측 여유는1155.83MiB, cgroup peak는4.91GiB이며 앱 단독 메모리 상한이 아니다. 이후 증가량을 같은 값으로 보장하지 않는다.

큰 파일/선택 합계1MiB 초과·현재 폴더 첫 import 결합·배치 진입, 다른 원본 미리보기·Office 내용 편집·자료 설명과 다른 고정 행의 미완료는 [수용 목록](V666_ACCEPTANCE.md)에 유지한다. 초기화 간헐 빈 화면 원인은 미확정이다. 실제 Windows/WebView2·모바일·전체 UI·Space/Library 전달은 미검증이며 main은 사용자 검토/merge 대상으로 유지한다.
