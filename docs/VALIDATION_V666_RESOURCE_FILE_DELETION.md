# V666 프로젝트 파일 사본 삭제 검증

검증 source는 `5fe5c940984593e36e0efe18bcc417a47f861ebf`다. 제품 코드는 `92ca00d3`에서 고정했고 이후 두 커밋은 검사만 수정했다. 최종 기록은 `/workspace/artifacts/v536-verification-managed/runs/f658494f353d43c38dfc50e6e76ac7c9.json`, 증거 ZIP SHA256은 `7a32733a3ec3d4721fa8bfbd3d34bb6c17ad8ddb6440f3735130ebb844380077`다. 실패한 개발 검사와 통신/스크린샷도 보존했으며 실패를 통과로 집계하지 않았다.

## 최종 결과

LF 25·CRLF 25·새 패키지/전체 복원/실패 수명관리 9, 총 **59단계(신규 52·재사용 7)**를 통과했다. 두 checkout은 `--no-hardlinks`, 각각 `core.autocrlf=false/true`, 독립 NuGet·dotnet CLI home·최초 빈 engine cache를 사용했다. 최종 제품 코드/변경 검사 기준 새 빌드를 수행했다.

- 독립 pack 소비자의 실제 실행 41개 검사: 파일 한 개 삭제, 표시명/배치 동시 제거, 다른 사본/원본 proof 보존, 일괄 이동의 생존 이력, wrong owner/hash/path/ID/command 거부, 쓰기 거절, 손상 receipt, 정확한 재요청, 같은 ID의 새 세대 보호, 빈 store hash ABA에서 지연 import 재생성 거부, 4,096건 한도에서 기록 자동 삭제 없는 안전 거절.
- 실제 production body/CommitPlan의 12개 경우: 성공, manifest/identity/store/topology/file-name/folder-name/receipt 최종 CAS 충돌과 네 단계 각각 쓰기 직후 예외. 실패 시 생존/삭제 대상/이름/배치/receipt의 모든 이전 bytes가 복구됐으며 peer 변경은 보존했다. 기존 import·category·folder/file-name CAS도 통과했다.
- 실제 Linux engine와 Chromium: 원본 `자료 삭제` 확인/취소, 실제 readonly 파일 쓰기 거절 후 정확한 재시도, 늦은 native 읽기 성공 후 창/내용 재생성 방지, 실제 성공 응답 유실 후 receipt 확인, 확인창을 연 뒤 peer 변경 거부와 input-only 취소, 새 query/chat 입력 보존. cold restart는 pending을 보존하되 자동 재실행하지 않았고 다른 실제 프로젝트 왕복에서 데이터/입력이 섞이지 않았다.
- 기존 파일/폴더 이름·폴더 계층/이동·readonly text preview·import·C# 일반 저장/Undo/Redo/Review/Confirm/실행/재시작 회귀. C# bytes/ID/override 계약/권한은 변경하지 않았다.

재사용 7개는 개발 단계 `a6fcac2f`의 소유 임시물/IPC 검사와 LF 정적 검사·새 소비자41개·삭제12개/기존 import CAS다. 최종과의 차이는 새 UI fixture의 이동 완료 대기 한 줄뿐이다. 각 재사용 기록에 product/test 입력의 불변성, 같은 SDK/NuGet SHA, 명령/mode, 원본 ZIP 전체 manifest/SHA 검증을 기록했다. 모든 UI·CRLF·새 패키지·전체 복원은 신규다.

## 개발 실패와 복구

첫 독립 소비자는 실제 34개 검사를 통과한 뒤 Python 래퍼가 오기된 최소35개와 비교해 실패했다. 제품 변경 없이 정확히41개의 실제 검사를 구성하고 ABA/receipt 상한 검사를 추가했다. 두 번째 UI 검사는 drag 후 native 완료 전에 목록을 관측해 실패했다. 보존 traffic에는 같은 명령의 native 성공과 올바른 parent가 확인됐고 script error는 없었다. DOM에서 이동 결과가 나타난 뒤 검증하도록 고쳤다. 소스/레이아웃/제품 동작을 검사 편의로 바꾸지 않았다.

## 지속 보관과 공간

| 역할 | 출처 commit | ZIP SHA256 | bytes | files/dirs |
|---|---|---|---:|---:|
| latest | `5fe5c940984593e36e0efe18bcc417a47f861ebf` | `a65878bc2595690a1965809f090d87a5864d922ac8a98b6f34793fbb91815420` | 51915263 | 2498/153 |
| rollback | `ca011efde83606e63a81480177eca7556e2aa8c8` | `a9e2894b0c5adad4e20449b86b73c256665bfbb2c744bb6b7a457c7af3780499` | 51910585 | 2495/153 |

latest manifest SHA256 `b01e84b2f8737e20cea083f1cb2d0663e8c3edaa5151a2ccd16defb997952725`, rollback `7541e575f692e71737bddc3fdbb313cd514e7013455b8079f380281a15423897`. 저장 위치는 `/workspace/artifacts/v536-verification-managed/packages`의 기존 소유 index다. ZIP CRC/SHA와 모든 file bytes/modes·전체 전개 manifest, 새/복원 package의 실제 engine UI를 검증한 뒤 기존 원자 승격을 사용했다. 기존 latest를 rollback으로 보존했으며 과거 자료의 추가 정리는 하지 않았다. package 출처와 게시 commit 사이에는 검증 결과 문서만 추가한다.

사전 여유 1206.56MiB, 추가 지속 공간 예산144MiB(안전64 포함). 최종 실행 순증가 5.14MiB, 이번 개발/실패 증거 포함 순증가 8.92MiB; 측정 시 여유 1197.64MiB, 검사 중 관측 최저 1202.71MiB, cgroup peak 4960.03MiB. 고정3~6MiB 증가를 보장하지 않는다. 실행 자식 종료·소유권과 증거 ZIP manifest 검증 후 해당 실행의 임시 root만 정리했고 `True`로 부재를 확인했다. 원본·개인 파일·사용자 데이터·과거 로그/캐시 삭제 및 Git 산출물 게시는 없다.

## 한계와 잔여

이번 단위는 직접 소유 파일 한 개의 프로젝트 사본 삭제다. OS 원본 삭제·휴지통/삭제 Undo·폴더/다중 삭제·내용 편집 백업 복구는 구현하지 않았다. 원본의 내용 백업 복구와 영구 삭제를 혼동하지 않는다. 새 삭제 receipt를 모르는 과거 writer로 프로젝트를 수정할 때 지연 import 방지는 보장하지 못하며 자동 migration/receipt 가지치기는 없다. 현재 파일/전체 bytes와 ID 예산도 유지한다.

초기화 빈 화면은 원인 미확정 잔여다. PDF/Office/이미지/메시 편집·전체 V6, 실제 Windows apphost/WebView2·모바일·물리 영상/오디오 장치·전체 UI·Space/Library 전달은 이 검증의 완료 범위가 아니다. main은 사용자 검토/merge용으로 보존한다.
