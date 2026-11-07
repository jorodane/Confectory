# V666 정지 PNG/JPEG 자료 미리보기 검증

최종 테스트 코드 `ee2796d8d87c049d1b08e87b72f23d269a655ea7`. 원본은 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`(SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)의 `Confectory-v666/dist/resource-preview.js` image 분기와 기존 contain CSS다. 지원 의미와 예산은 [V7_RESOURCE_IMAGES](V7_RESOURCE_IMAGES.md)를 따른다. 이후 게시 변경은 검증 문서뿐이며 패키지의 제품 코드와 같다.

| 구분 | 신규 실행 | 동등 근거 재사용 | 합계 |
|---|---:|---:|---:|
| 독립 LF checkout | 16 | 1 | 17 |
| 독립 CRLF checkout | 16 | 1 | 17 |
| 새 패키지·전체 복원·실패 수명 | 9 | 0 | 9 |
| 합계 | **41** | **2** | **43** |

각 checkout은 `--no-hardlinks`, 독립 Git·NuGet 복사본·SDK home·빈 engine cache에서 시작한다. SDK10.0.401/seed identity와 LF/CRLF 정규화 bundle SHA를 확인했다. LF/CRLF 에디터 빌드·MCP·엔진 빌드, 그림 경계/수명 단위 검사와 실제 native 프로젝트 사본의 Chromium UI를 새로 실행했다. 기존 텍스트 내용 편집·읽기 전용 미리보기·파일 이름·다중 삭제·import UI도 양쪽에서 새로 검증했다.

새 Windows 교차 패키지 생성/구조 probe와 생성본 그림·텍스트 UI, 전체 파일 SHA/CRC/모드 복원, 복원본 probe/그림·텍스트 수명, 실패 패키징 수명을 새로 실행했다. 교차 패키지의 Linux 실행 가능 엔진과 Chromium 검사를 실제 Windows/WebView2 실행으로 세지 않는다.

재사용은 LF/CRLF의 `source-recovery-ui` 두 건뿐이다. 증거 ZIP/전체 manifest와 원본 통과 행을 확인하고 SDK/NuGet/configuration/RID·명령·native/src/targets/packs·소스 편집 fixture/호스트 입력이 동일함을 검사했다. 이 fixture에는 자료 창/endpoint가 없으며 제품 차이는 자료 미리보기와 앞서 검증한 자료 내용 처리·scoped CSS·bundle manifest 범위다. 선택한 실제 선행 기록과 검증한 재사용 경로를 각 `*.reused.json`에 보존했다. 변경된 자료 UI 검사를 재사용하지 않았다.

실제 확인한 사용자 흐름:

- 생성한 PNG의 native project/ID/hash/size/base64/SHA 관측을 거쳐 실제 픽셀 `[240,10,20,255]`을 확인했다. baseline/progressive JPEG와 EXIF 회전 JPEG도 실제 decoder와 contain 패널에서 확인했다. 정상 화면 PNG를 직접 보았으며 기존 창·설정·도구줄 배치를 유지한다.
- SVG/HTML 위장과 과도한 dimension은 Blob URL을 만들지 않고 거절한다. 스크립트/외부 요청이 실행되지 않으며 원래 프로젝트 사본과 관련 없는 입력·C# 원문은 유지된다. 실제 decoder 거절과 같은 사본 명시 재시도의 URL 해제도 확인했다.
- 실제 성공 read 응답을 보류한 채 닫기/같은 창 재열기에서 오래된 응답은 URL을 만들거나 현재 그림을 바꾸지 않는다. 열린 그림의 실제 인라인 이름 변경·접기/펼치기와 확인 후 삭제에서 이전 URL을 해제하며 다른 사본은 보존한다.
- cold 재시작은 개인 레이아웃의 owner/ID/hash만 복원하고 다시 읽는다. Blob URL/base64 bytes가 개인 레이아웃에 저장되지 않는다. 실제 읽기 권한 거절 후 retry, 성공 read 보류 중 Home 왕복, 같은 namespace의 다른 실제 프로젝트 격리·원래 프로젝트 복귀를 확인했다.
- 단위 검사에서 pending decode를 포함한 합산 픽셀 lease, 예산 초과 전 URL 생성 거절, 중복 dispose·늦은 decoder callback·숨김/분리·오류/예외·dimension 불일치의 해제를 확인했다. 정상 UI 실행마다 생성/해제 URL 수가 일치했다. 이 단위 검사는 가짜 DOM/URL이며 실제 codec 검증은 별도 Chromium UI로 구분한다.
- 기존 텍스트 내용의 실패 입력·충돌·응답 유실·늦은 입력·이전 내용 복원·재시작 회귀를 새로 실행했다. 그림 preview는 쓰기 명령/새 CAS 계약을 만들지 않는다. native 원자 저장/권한/Review→Confirm/CAS 및 완료된 편집 구현이 변경되지 않았음을 정확한 diff·SHA guard로 확인하며 이전 native 검증을 새로 실행했다고 표시하지 않는다.

첫 실행에서는 손상 PNG의 IDAT를 Chromium이 일부 복구해 표시하여 `onerror` 기대가 실패했다. 이는 완전한 파일 검증을 보장하지 않는 브라우저 동작과 fixture 기대의 차이다. 제품 코드는 유지하고 유효하지 않은 PNG bit depth3 검사본으로 decoder 거절을 확정한 뒤 최종 검사를 수행했다. 첫 실패의 원본/로그/스크린샷은 별도 기록 `a5f985b1c94f4ec185c29ff3a8676706`에 보존한다. 헤더 screening과 브라우저 표시 성공은 파일 형식 전체의 완전성 인증이 아니다.

기록: `/workspace/artifacts/v536-verification-managed/runs/51d0982ec5ec44d081e011c4f171a30a.json`

증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/51d0982ec5ec44d081e011c4f171a30a.zip`

SHA256: `7a160380c149e6deeaa904410d172a5beeeee9658ec33a18fb68ac03fe7f1c2b`

원본·재사용·실패 및 공간 집계: `/workspace/scratch/v666-resource-images/FINAL-METRICS.json`

| 지속 보관 | 출처 commit | ZIP bytes | 파일/디렉터리 | archive SHA256 | 전체 manifest SHA256 |
|---|---|---:|---:|---|---|
| latest | `ee2796d8d87c049d1b08e87b72f23d269a655ea7` | 51935018 | 2501/153 | `a27a88bd203a41e4fe6aafdd90ae9295f688012ffb8d5a3b424a3695ccc1d133` | `dc54edbfc55182bf1286210f05d3f2e0bef773575aee6f1a0d3e572107705914` |
| rollback | `99fbfbcc4c02b761c0e36331fbce88913d3dc7fe` | 51932541 | 2500/153 | `51a7f30dcbcc593833d69d60c08d9762048c6b6a0505b5739f718feb5faed2c9` | `c66dd0e83dd2ce9b594012ddd80a9cee166c435091b32ef029645597c0d43fde` |

승인된 두 세대 보관 index에 원자 승격했고 두 ZIP/전체 manifest를 재확인했다. 증거를 지속 공간에 보존하고 생성 소유권/자식 종료를 확인한 뒤 이번 실행의 임시 root를 제거했다. 기존 원본·과거 자료·로그·프로필·캐시는 삭제하지 않았다.

최초 여유 약1163.68MiB, 추가 persistent 요구144MiB(안전64MiB 포함)를 유지했다. 최종 실행 디스크 순증가는 **4.16MiB**, 앞선 실패 증거까지 포함한 단위 관측 순증가는 **6.02MiB**, 집계 시 여유는 **1157.66MiB**다. 단계 중 최소 관측 여유는1161.77MiB, cgroup peak는4.89GiB이며 앱 단독 RAM 상한이 아니다. 이후 모든 단위의 증가량을 같은 값으로 보장하지 않는다.

1MiB 이하 정지 PNG와 8bit baseline/progressive JPEG가 이번 지원 경계다. 다른 원본 그림/애니메이션·PDF·Office/mesh 미리보기, Office 내용 편집·자료 설명, 큰/다중 import·현재 폴더 첫 import 결합과 배치 진입은 기존 고정 잔여로 유지한다. 초기화 간헐 빈 화면 원인은 미확정이다. 실제 Windows/WebView2·모바일·전체 UI 및 Space/Library 전달은 미검증이다. main은 사용자 검토/merge 대상으로 보존한다.
