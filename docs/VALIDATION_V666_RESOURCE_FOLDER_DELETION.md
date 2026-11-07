# V666 카테고리 하위 삭제 검증

검증 source는 `113c80a0eac3a437add28b4dd89d623587ab1013`다. 제품은 `be2bb231`에서 고정했고 후속 변경은 검사 조작만 수정했다. 최종 실행 기록 `/workspace/artifacts/v536-verification-managed/runs/4bfa563a029b4edb85834b9a3d1d44f6.json`, 증거 ZIP SHA256 `b7602d4c5a38b0095d3f54bd32c30a24da2e40437d3e032e570a3b27333cd4a4`. 실패한 개발 검사·생성 입력·통신 기록도 별도 증거 ZIP으로 보존했으며 통과로 집계하지 않았다.

## 최종 결과

LF 28·CRLF 28·새 패키지/전체 복원/실패 수명관리 10, 총 **66단계(신규 58·재사용 8)**를 통과했다. 독립 checkout은 `--no-hardlinks`, 각각 `core.autocrlf=false/true`, 독립 NuGet/dotnet CLI home·최초 빈 engine cache를 사용했다.

- 새 독립 pack 소비자 실제 실행43개: 빈 카테고리 삭제 시 file/name store 무생성, 하위 전체 제거, 별도 peer/옮겨 나온 폴더·생존 일괄 이동/과거 생성 이력과 bytes/proof 보존, 표시명 alias 정리, owner/hash/path/유형/command 거부, 확인 후 하위 추가 거부, 실제 쓰기 거절, 기존 파일 receipt와 새 그룹 receipt 동시 검증, 지연 import 거부, 정확한 재시도·새 세대 재삭제 방지, 손상 그룹 거부/복원. 기존 파일 삭제41개와 다른 자료 provider/CAS 회귀도 실행했다.
- 실제 production body/CommitPlan 13개 경우: 성공, manifest/identity/store/topology/file-name/folder-name/receipt 최종 충돌, 다섯 번의 쓰기 각각 직후 예외. 모든 이전 bytes가 복원됐고 peer 변경은 보존됐다. 현재 부모는 활성 folder여야 하며 historical create-parent/move ID만 검증된 retired 이력을 허용한다.
- 실제 Linux engine/Chromium: 원본 카테고리 삭제 확인창의 하위 개수/취소, 실제 folder-name 쓰기 거절 후 정확한 재시도, 지연 native 하위 읽기 성공과 창 재생성 차단, outside viewer·사본/별칭 보존, 빈 하위의 삭제 응답 유실 재확인, 확인 후 자식 이동의 stale 거부·input-only 취소, 새 query/chat 입력 보존.
- cold restart는 pending 자동 실행 없이 같은 확인 intent를 복원했다. 명시적 재확인은 추가 쓰기 없이 완료됐고 삭제된 활성 폴더는 ProjectPack으로 돌아갔다. 다른 실제 프로젝트 왕복에서 자료·개인 pending 상태가 섞이지 않았다. 기존 단일 파일 삭제·이름·폴더·이동·readonly preview·import도 회귀했다.

재사용 근거는 두 부류다. 자료 창/endpoint를 사용하지 않는 기존 일반 C# 복구 UI의 LF normal·CRLF late는 `5fe5c940984593e36e0efe18bcc417a47f861ebf`의 최종 증거에서 재사용했다. Core/targets·모델/편집기·권한/저장 primitive·Main·일반 runtime·원본 검사/fixture는 그대로이며 bridge 차이는 호출하지 않는 delete-folder whitelist뿐이다. 일반 C# 원문/계약/Undo/Review/Confirm 경로는 같다. 나머지는 제품 고정 뒤 검사만 바뀐 개발 실행의 IPC/정적/새 native 소비자43개·CAS13개다. 각 row의 원본 archive SHA/전체 manifest, 관련 source/test/mode/명령, SDK/NuGet 동일성을 검증했다. 모든 자료 UI·CRLF native·새 패키지·전체 복원은 신규다.

## 개발 실패의 구분

첫 UI 검사는 채팅 초안의 blur 자동 저장 중 삭제 메뉴를 눌러 확인창을 기다리다 시간 초과했다. traffic은 chatDraft 완료를 기록했고 delete 요청은 없었다. 초안 blur/완료를 기다리도록 검사만 수정했다. 두 번째는 트리의 파일을 열면서 부모 폴더로 이동한 뒤 이전 Root 카드로 상위 폴더를 찾은 검사였다. 현재 트리의 ancestor 메뉴를 사용하도록 고쳤다. 제품 레이아웃/권한/busy 보호를 바꾸거나 force click으로 검사를 통과시키지 않았다.

## 패키지·공간·정리

| 역할 | 출처 commit | ZIP SHA256 | bytes | files/dirs |
|---|---|---|---:|---:|
| latest | `113c80a0eac3a437add28b4dd89d623587ab1013` | `f32a246d5f3e6609292c06f3f7aac76c9856467443a18ef839600ab753a7da14` | 51918174 | 2498/153 |
| rollback | `5fe5c940984593e36e0efe18bcc417a47f861ebf` | `a65878bc2595690a1965809f090d87a5864d922ac8a98b6f34793fbb91815420` | 51915263 | 2498/153 |

latest manifest SHA256 `062595aba19e09d9f3604fab3e39e00b6f0a1978051468ba2c1f17d6373ce7af`, rollback `b01e84b2f8737e20cea083f1cb2d0663e8c3edaa5151a2ccd16defb997952725`. 저장소는 기존 `/workspace/artifacts/v536-verification-managed/packages`의 소유 index다. ZIP CRC/SHA, 모든 파일 bytes/modes와 전체 전개를 검증하고 생성/복원 package의 실제 engine UI를 실행한 뒤 원자 승격했다. 기존 latest를 rollback으로 보존했다. package 출처와 게시 commit 사이에는 검증 결과 문서만 추가한다.

사전 여유 1197.55MiB, 추가 지속 예산144MiB(안전64 포함). 최종 실행 순증가 5.56MiB, 이번 작업/실패 증거 포함 순증가 8.79MiB; 측정 시 여유 1188.77MiB, 검사 중 관측 최저 1194.24MiB, cgroup peak 4986.11MiB. 고정3~6MiB 순증가를 보장하지 않는다. 자식 종료·소유권 확인, 증거 ZIP 전체 manifest 검증 후 해당 실행의 임시 root만 정리했다. 임시 root 부재 `True`. 과거 자료/원본/로그/캐시/프로필을 추가 삭제하지 않았다. 사용자 데이터·비밀·빌드 산출물은 Git 게시하지 않는다.

## 남은 경계

카테고리 한 개와 현재 소유 하위만 지원한다. 확인 뒤 변화는 안전 거부하며 대상을 자동 확대하지 않는다. 다중 선택 삭제·내용 편집/백업 복구·큰/다중 파일과 현재 폴더 첫 import·다른 rich preview는 고정 잔여다. 원본처럼 영구 삭제이며 휴지통/삭제 Undo를 추가하지 않았다. 새 그룹을 모르는 과거 receipt reader는 안전 거부하고, 더 이전 writer의 지연 import 보호 한계도 남는다. 자동 migration/receipt 가지치기 없이 기존4,096건/2MiB 한도를 유지한다.

초기화 빈 화면은 원인 미확정이다. 실제 Windows apphost/WebView2·모바일·물리 출력/오디오·전체 UI·Space/Library 전달 완료로 표현하지 않는다. 기존 C# 원문/override 계약/권한·Review→Confirm과 main을 보존한다.
