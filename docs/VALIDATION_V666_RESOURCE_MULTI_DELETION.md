# V666 다중 선택 삭제 검증

최종 검증 source는 `14c507d51b37020e7e85ff67f9457608be4968e2`. 선택/다중 삭제는 `349c36f9`, 저장 중 확인 보존은 `4ebef9f2`, 미선택 drag source의 선택 표시는 `14c507d5`에서 고정했다. 그 후 제품 변경 여부는 최종 source 비교로 확인한다. 실행 기록 `/workspace/artifacts/v536-verification-managed/runs/c319b9f957f2458c81c21e3271e768d5.json`, 증거 ZIP SHA256 `58df6cfb76ab98571ff7e4202aa303679170e898470da179af760b71e30673bd`. 실패/재현 결과도 보존했고 통과로 집계하지 않았다.

## 결과와 범위

LF 32·CRLF 32·새 패키지/전체 복원/실패 수명관리 11, 총 **75단계(신규 70·재사용 5)** 통과. 독립 Git(`--no-hardlinks`), `core.autocrlf=false/true`, 독립 NuGet/dotnet CLI home와 최초 빈 engine cache를 사용했다.

- 새 독립 pack 소비자 실제47개: 명시한 여러 파일/폴더와 조상/하위 overlap의 정확한 합집합, 하나라도 unknown/wrong hash/중복/빈/예산/다른 owner/path이면 전체 거부, 확인 후 하위 변경 거부, 실제 쓰기 거절, unselected bytes/원본 import/표시명/옮겨 나온 이력 보존, 지연 import 재생성 방지, 정확한 재시도·새 세대 재삭제 방지, recomputed checksum에서도 unknown target 거부, 파일만/폴더만 선택 시 관련 없는 저장 파일 무재작성. 기존 폴더43개·파일41개와 다른 provider/CAS도 회귀했다.
- 실제 production body/CommitPlan 13개: 혼합 selected roots 성공, 일곱 관측 파일의 최종 CAS 충돌, 다섯 번의 쓰기 각각 직후 예외. 모든 이전 bytes가 복원됐고 peer 변경은 보존됐다. 기존 계약/권한/원본 C#·FileStream primitive는 변경하지 않았다.
- 실제 Node selection/drag adapter 세 경우를 LF/CRLF에서 실행했다. 선택 밖/빈 선택에서 source 하나 선택, 선택 안에서는 기존 명시 집합 유지, nonce/project/revision을 담은 drag payload와 화면 선택 일치, drag 시작 자체는 native write0. 이는 실제 모듈의 제어된 어댑터 검사이며 실제 브라우저/기기 검사로 집계하지 않는다.
- 실제 Linux engine와 Chromium: Ctrl 토글·Meta 추가·Shift 현재 표시 순서 범위, 정렬/밀도/검색 뒤 선택 보존, 숨겨진 명시 대상의 N개 확인/취소, 선택 밖 우클릭의 단일 메뉴, 선택 밖 파일의 단일 drag 선택과 명시 다중 drag 왕복, mixed 파일/폴더 확인·실제 쓰기 거절, 실제 성공 응답 유실 재확인, 늦게 만든 선택/query/chat 입력·outside preview 보존. 한 target 변경은 refresh/retry 후에도 전체 거부하고 입력만 취소할 수 있었다.
- cold restart는 개인 selected IDs/anchor와 정확한 pending을 복원하되 자동 삭제하지 않았다. 명시적 receipt 확인은 새로 만든 선택을 유지하고 추가 쓰기 없이 끝났다. 다른 실제 프로젝트 왕복에서 선택/자료/pending이 섞이지 않았다. 기존 단일 파일·하위 카테고리·이름·미리보기·import 회귀 및 새/전체 복원 package에도 적용했다.

재사용 출처 commit은 `4ebef9f237d6ebff0aefb9bd92f957197c69daa0`, `5fe5c940984593e36e0efe18bcc417a47f861ebf`. 일반 C# 복구 UI LF normal/CRLF late는 자료 창/endpoint를 사용하지 않는다. Core/targets·일반 편집기·모델/저장/권한 primitive·Main·runtime·원본 검사/fixture는 같고, workspace-host 차이는 그 입력에 없는 resourceSelections/resourceAnchor whitelist다. 나머지는 관련 C#/probe/fixture/SDK 입력이 같은 IPC와 새 native47개/CAS13개다. 원본 증거 ZIP SHA/전체 manifest, 관련 source/test/mode/명령과 SDK/NuGet 동일성을 row별로 확인했다. 자료 UI·새 패키지·전체 복원은 최종 코드로 신규 실행했다.

## 발견/복구와 실패 구분

실제 제품 결함 하나를 재현했다. 선택 밖 파일을 끌 때 payload는 그 파일이었지만 선택 표시는 이전 항목에 남았다. 실제 JS event binding을 제어한 재현은 native write 없이 assertion 실패를 기록했다. 원본 bindResourceDrag처럼 시작 시 명시 source를 선택하도록 수정했고, 세 adapter 경우와 실제 브라우저의 카테고리 안/밖 drag로 확인했다. 재현 log/JSON/SHA는 최종 증거에 포함했다.

UI fixture 첫 실패는 Escape가 context menu를 닫았다고 가정한 뒤 가려진 카드를 누른 것이었다. 다음은 좁은 status output이 resize handle에 가려지는 위치를 고른 것이었다. 원본 레이아웃 안의 빈 content 영역을 눌러 메뉴를 닫도록 검사만 수정했다. 제품 위치/스타일을 바꾸거나 force click으로 우회하지 않았다. 이미 실행은 실패 증거를 보존하고 cleaned 상태였으므로 SIGINT 전송이나 별도 프로세스 중단은 실행하지 않았다.

## 지속 패키지와 공간

| 역할 | 출처 commit | ZIP SHA256 | bytes | files/dirs |
|---|---|---|---:|---:|
| latest | `14c507d51b37020e7e85ff67f9457608be4968e2` | `408db721c95b3bc0bdcbf06494c5f265f7eb881c2bd3b421dba967aa68ed3f91` | 51921163 | 2499/153 |
| rollback | `113c80a0eac3a437add28b4dd89d623587ab1013` | `f32a246d5f3e6609292c06f3f7aac76c9856467443a18ef839600ab753a7da14` | 51918174 | 2498/153 |

latest manifest SHA256 `ce15b2b85cd4428928ef46f7cc3a313294a63a831e839a244c0aadf9fcb4e992`, rollback `062595aba19e09d9f3604fab3e39e00b6f0a1978051468ba2c1f17d6373ce7af`. 기존 `/workspace/artifacts/v536-verification-managed/packages`의 소유 index를 사용했다. ZIP CRC/SHA·전체 file bytes/modes·전체 전개와 생성/복원 package의 실제 engine UI를 통과한 뒤 원자 승격했다. 기존 latest는 rollback이다. 검증 source와 게시 checkpoint 사이에는 검증 결과 문서만 추가한다.

사전 여유 1188.68MiB, 추가 지속 예산144MiB(안전64 포함). 최종 실행 순증가 6.36MiB, 이번 개발/실패 증거 포함 순증가 9.88MiB; 측정 여유 1178.80MiB, 검사 중 관측 최저 1185.06MiB, cgroup peak 4992.24MiB. 고정3~6MiB 순증가는 보장하지 않는다. 자식 종료·소유권, 증거 ZIP 전체 manifest 확인 후 해당 실행 임시 root만 정리했고 부재 `True`. 원본·사용자 데이터·과거 로그/캐시/프로필의 추가 삭제나 Git 산출물 게시는 없다.

## 남은 경계

내용 편집/한 단계 백업 토글 복구가 아직 선행 기반을 필요로 한다. 큰/다중 파일 import·현재 폴더 첫 import·설명·다른 rich preview와 고정 backend 항목도 별도다. 원본처럼 삭제는 영구 제거이고 휴지통/삭제 Undo를 새로 만들지 않았다. 새 selected intent를 모르는 과거 receipt reader는 안전 거부하며, 더 이전 writer의 지연 import 보호 한계도 남는다. 기존4,096건/2MiB에서 자동 이력 가지치기 없이 거부한다.

초기화 빈 화면은 원인 미확정이다. 실제 Windows apphost/WebView2·모바일·물리 영상/오디오·전체 UI·Space/Library 전달 완료와 구분한다. main은 사용자 검토/merge용으로 보존한다.
