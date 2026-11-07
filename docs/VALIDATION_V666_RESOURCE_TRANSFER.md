# v666 여러 자료 선택 합계 4MiB 검증

제품/검사 동결 `416396dbcdaf5deedae705d94b0116c16d23b52e`. 후속 문서는 제품/검사 코드를 바꾸지 않는다.
최종 **61단계(신규 61·재사용 0)**:
독립 LF 25·CRLF 25·교차 패키지/전체 복원/실패 수명관리 11.

[닫힌 범위](V6_RESOURCE_TRANSFER.md)는 기존 자료 추가/명시 목적지의 선택 합계 4MiB다.
파일당 1MiB, 전체 보관 4MiB/64개, resources.v1 문법과 공개 함수 signature는 유지한다.
원본 v666 ZIP SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`
및 authored CSS/메뉴/레이아웃은 그대로다. 2MiB 글로벌 RPC를 늘리지 않고 세션의 최대
6,000,000B 휘발 버퍼와 1MiB 청크를 사용한다. 파일명/가상 카테고리는 계속 metadata다.

| 검사 | 실제 범위 |
|---|---|
| LF/CRLF | 독립 Git objects/checkout·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine, 정확한 8개 제품 파일과 원본/계약/레이아웃 경계 |
| native provider | 독립 pack consumer 단일/배치/목적지·레이아웃, 추출한 실제 production 본문 최종 CAS 경쟁·원자 파일 묶음 실패, 구버전 실제 reader로 정확 4MiB 새 그룹 load/read |
| 전송 protocol | UTF-8 코드포인트 중간 청크, 정확 중복/offset 재개, 바뀐 청크·미완성·변조 hash·초과 길이·임의 target/plan 거절, 삭제 이후 성공 재시도 부활 거절, 다른 프로젝트/경쟁·Home/cold 정리 |
| 실제 File UI | 합계 1MiB 초과 실제 선택·정확 bytes/SHA/ID/명시 폴더, 실제 쓰기 거절 뒤 원자 rollback/입력 retry, 성공 청크·최종 저장 응답 유실, 명시 취소와 확인된 사본 보존 |
| 수명/동시 변경 | late 검색 입력, 실제 peer 후 최종 CAS 반복 거절·refresh/cancel, 닫기 뒤 late 응답/다른 창 입력 격리·Home 왕복, Home 중 File 읽기·cold 미확정 휘발/확정 복원·동일 namespace 다른 프로젝트 |
| 경계/회귀 | 정확 4MiB·파일당/합계 초과 사전 거절, 기존 배치/목적지/원본 자료 메뉴/텍스트 내용 편집/BMP 실제 pixel UI, scope/cancel/disposal와 C# source 복구 회귀 |
| 새 패키지/복원 | Windows 교차 생성/probe, 생성본과 전체 압축복원본에서 transfer/destination/BMP UI 새 실행, ZIP CRC/전체 SHA/파일·디렉터리 mode와 프로세스 종료/실패 증거 보존 |

최종 CAS는 세션 버퍼 검증 뒤 기존 import-many 또는 Layout import-files의 최종 CommitPlan에서
실행한다. staging은 디스크에 파일을 만들거나 presentation에 bytes/전송 ID를 넣지 않는다.
완료 재시도도 durable 영수증을 다시 검사한다. 기존 parent/외부/override 계약·계정 권한·
Review→Confirm·사용자 C# 원문과 기존 편집기를 바꾸지 않는다. fixture는 생성한 바이트뿐이며
사용자 개인 파일/외부 자료를 읽거나 업로드하지 않았다. native 본문 변경이 있어 관련 provider/
CAS/호환 검사를 이번에 새로 수행했고 이전의 native 불변 증거로 대체하지 않았다.

개발 중 실제 숨김 창/Home 왕복에서 공유 목록 loading 때문에 보이는 다른 창의 자료 추가가
비활성화되는 결함을 재현했다. load 시작 전 현재 창 수명을 확인하고 retired read 뒤 상태 갱신을
연결했다. 같은 검사 SHA `07f044a06e0c4bfcef8c67b752c6f9e5b01c5e5ee3b9dba56072aea3c18603eb`의
수정 전 normal-5 실패와 수정 후 normal-6 통과를 보존했다. 초기 빈 화면 원인과 혼동하지 않는다.
메뉴 전 초기 입력 flush, 기존 read endpoint 사용, 명시 refresh 뒤 삭제, 창별 입력/활성 탭
규칙에 맞춘 fixture 보정도 따로 기록했다. 개발 검사는 최종 통과 수에 더하지 않는다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/95b2e233c0764e00a6337a73c899cbab.json`
- 증거 ZIP SHA256: `fb817f0120d26b43cbf701c0237561230028773fe30ceb661cffdda4e79088f7` (4,536,215B)
- 선행 실패/수정 기록: 2개. 통과 수에 중복 합산하지 않는다.
- 별도 UI 개발·수정 전/후 기록: `/workspace/artifacts/v536-verification-managed/runs/e8e004c1995f48a6afa3cb8a1ebcf523.json`. 초기 checkout과 수정 자산의 hash/재빌드 보고서·동일 검사 사본·실패 로그를 보존했다. 최종 61단계는 모두 최종 동결에서 새로 실행했다.
- 모든 기록은 archive/manifest 전체 검사 후 cleaned, 해당 실행 owned root 부재를 확인한다.

| 지속 패키지 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `416396dbcdaf5deedae705d94b0116c16d23b52e` | `5032d15756c574f679d50b0601f01a50a2ef19a82582237647fe729a0d5eb36a` | 53,802,814 | 2703/158 |
| rollback | `273c1c48cac321e2c39d692dc56ba65cc5be7e46` | `0cc0c023568cdd7c9f2926634e6c0444fcbbed8ccaf741767c203a5da3466b22` | 53,799,584 | 2703/158 |

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest `4ae0b054e4df5dbf4a007bede66ecef601443be19b3bfd64fcff0abf9962c4c6`, rollback manifest `5dae0cd1965905806ec6b0de76e8d253d7f109e5017497fbbb582dbfcecb49ae`.
직전 BMP 정상본을 rollback으로 보존한다. v1 저장 문법은 같아 구버전 reader가 새 4MiB
그룹을 읽을 수 있고 구버전 UI의 선택 한도는 기존 1MiB다. 관리형 원자 승격과 이번 실행이
직접 생성한 임시물만 정리했다. 과거 자료·원본·SDK·로그·프로필·사용자 데이터는 삭제하지 않았다.

사전 확인 후 순증가 11,280,384B (약 10.8MiB),
최종 실행 순증가 6,156,288B, 현재 여유 1,096,052,736B
(약 1.02GiB). 향후 실행 증가량 보장은 아니다.
사전 추가 예산 candidate56+증거20+코드/Git8+안전64=148MiB, RAM3GiB+여유512MiB,
추가 memory7GiB+안전1GiB를 유지했다. 단계 표본 최소 여유 1,102,143,488B,
cgroup peak 6,677,331,968B는 압축/승격 순간 전체 최저 측정은 아니다.

단일 1MiB 초과 File·전체 보관4MiB 초과·다른 형식 rich preview는 남는다. mesh는 원본의
분류/필터만 확인됐으며 실제 renderer 근거 없이 새 기능을 만들지 않는다. 초기 빈 화면은
원인 미확정이다. Linux 실제 엔진/Chromium 자동화와 교차 패키징을 확인했으며 실제
Windows/WebView2/mobile·전체 UI·Space/Library 전달은 미실행이다.
