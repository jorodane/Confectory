# V666 직접 소유 C# 본문 검색 검증

제품·검사·도구 동결 `aa52925a01fbb694c5dae41d9dccfc51254005ae` 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V9_FINDER_BODIES.md)와 [정확한 delta](v666-finder-bodies-delta.json)를 따른다.

## 원본과 수정

저장소 v666 ZIP `Confectory-v666/dist/app.js`의 `workspaceSearchText(object)`는
`object.functionDefinition.body`도 포함한다. 이전 게시 엔진에서 선언된 소유 C# 본문의
검색 누락을 생성 fixture로 확인했다. 이번에는 이미 등록한 직접 소유 C# target마다
별도 결과를 표시하고, 관측한 바로 그 target을 기존 원문 편집 창에서 연다.

새 bounded read는 기존 namespace/소유 등록·locator/링크 검사와 bounded snapshot을 쓰며
파일과 구현 요청당 1MiB·64회 시도 안에서 본문 전체를 읽는다. 구현별로 요청을 분리하고
초과/미지원/누락 본문은 부분 결과로 표시한다. 20,000자 뒤의 유효 본문도 검색한다.
working-copy 읽기이며 외부 디스크를 실시간 재스캔하지 않는다. 최초 적재 시 원래 Read와
같이 raw baseline/original/draft를 보존한다. C# 실행·소스 재작성·등록 밖 파일/외부 원문
탐색은 하지 않는다. 기존 source conflict·최종 CAS를 우회하지 않는다.

열기 요청은 owner/body revision·hash와 target을 다시 검증하며 경로 인자를 허용하지
않는다. UI private 미적용 입력을 보호한다. 기존 History.version의 readonly 관측으로
필터/페이지 밖 변경과 Undo/Redo도 열린 색인에 반영하고 ABA의 오래된 receipt를 거절한다.
기존 원본 Read/저장·Review/Confirm·실행/override 계약·ID/핀/연결·권한·레이아웃과
완료 M11/M12/M4/Run은 보존한다. 새 읽기 계약의 Main/Verify/VerifyShell provider를
명시 연결하며 기존 snapshot provider와 원문 baseline 연결도 함께 확인한다.

## 최종 검증

독립 LF 20·CRLF 20·새 패키지/전체 복원/IPC·실패 수명관리 15, **총 55단계(신규 55·재사용 0)** 통과했다.
독립 Git 객체·EOL·NuGet/home·엔진 cache에서 최종 동결 코드를 새로 빌드했다. 개발 검사와
과거 완료 근거는 최종 합계에 포함하지 않는다.

- 실제 Linux .NET 엔진/Chromium에서 target별 C# 본문·Unicode·21k 이후 tail 검색,
  초과 본문의 부분 상태, 정확한 원문 창 열기와 private 입력 보존을 확인했다.
- stale/변조/다른 소유자/알 수 없는 target/추가 path 인자는 cursor 변경 전에 거절했다.
  원본과 fixture 바깥 sentinel bytes를 보존했다. 검색 UI가 Save/Confirm/AI/실행을
  요청하지 않으며 미적용 source 입력이 있으면 다른 본문 열기 RPC도 보내지 않았다.
- 필터 결과에 본문 unit이 없는 상태에서 수정·Undo·Redo를 실행해 열린 검색이 갱신됐다.
  동일 내용으로 돌아온 뒤에도 이전 revision 열기 요청은 거절됐다.
- UTF-8 BOM/CRLF raw baseline의 SHA와 원문을 보존하고 외부 변경을 기존 source conflict가
  관측함을 확인했다. 적재 후 symlink 치환과 소유 선언의 locator 변경은 거절했고, 생성한
  원본 파일 복원 뒤 반복 열기는 정상 동작했다.
- cold→home→동일 namespace/ID의 다른 프로젝트에서 코드/검색어를 섞지 않았다. 기존
  정의·Data 검색/값·지연/실패/재시도·늦은 응답·pending Enter·닫기·프로젝트/Workspace
  격리, renderer busy/IME/비밀 필드 제외·배치 Ctrl+F·Run 최대화 회귀를 실행했다.
- 새 Windows 교차 패키지의 구조·무결성을 확인하고 패키지 엔진에서 본문 normal/보호와
  기존 검색 흐름을 실행했다. 전체 SHA/CRC/권한 모드로 완전히 복원한 엔진에서 cold/소유
  격리·baseline/링크 보호와 기존 검색을 확인했다. 성공·실패·예외의 증거 보존·자식 종료·
  소유 임시물 정리도 확인했다. 제어된 transport/브라우저 fixture는 실제 네트워크 장애나
  OS IME·Windows 기기 실행의 근거로 사용하지 않는다.

개발 중 Main 읽기 provider 누락을 찾아 Main/Verify/VerifyShell 연결을 수정했다. fixture의
editDraft id/revision 누락은 정상 거절이었고 인자를 수정했다. 필터 밖 변경 뒤 열린 검색의
stale 색인은 실제 제품 결함으로 재현하고 readonly version 관측으로 고쳤다. 마지막 연결
검사의 runner 등록 누락(0개, exit 1)도 수정한 뒤 실제 세 entry 계획을 통과했다. 모든 실패와
수정 결과를 보존했으며 실패/0개 실행을 최종 통과로 집계하지 않는다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/a356df3eafa7441089e3d52f5549215d.json`
개발 증거 SHA `b1659e0a705a0f3011eb2becdf22ec023131577ac6412d11fbad9f43b38fc8a4`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/45154e2023c440dba5f1159afec9c557.json`
최종 증거 `/workspace/artifacts/v536-verification-managed/runs/45154e2023c440dba5f1159afec9c557.zip`
SHA `167e863a6a2bdcd6c6b9a85c13d24ab3e06381c726d34b7a4c927168c815ce42` (11.32MiB).

## 보관·공간·잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `aa52925a01fbb694c5dae41d9dccfc51254005ae`, `6ebdbbd3574db8727849b7517764ae8ec668afc8c9ae90536301bd2150309f2d.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `827e6c2363dc7562b1fb44ca48b49a0358aeaed3443c2ae191d1102058a2a662`.
- rollback: `0f38e612812a76441ec5205002f92ebfb1c8bd38`, `198f4f49c125c39c08dd7e9d1fb5868ca7603bddfe3a13eb49403ce03c1c6740.zip`, 49.15MiB, 파일 2383·디렉터리 147, manifest `d30e55379b080770c54f5738fcf89c0f1a805e728c238dcc4ee9144693b87a8f`.

전체 archive SHA/manifest·복원을 확인하고 최신/이전 정상 롤백·증거를 지속 보관했다.
해당 실행이 만든 임시물만 소유와 자식 종료 확인 뒤 정리했다. 다른 과거 자료·원본·로그·
프로필·SDK/캐시의 추가 삭제나 보관정책 변경은 없다.

표본 최소 디스크 여유 1476.62MiB, 최대 cgroup 메모리 4944.95MiB.
최종 실행 순증가 12.48MiB, 개발 시작부터 보관 확인까지 17.25MiB,
문서 마감 전 여유 1464.21MiB. 다음 실행의 순증가를 보장하지 않는다.

직접 등록 소유 C# target 본문 검색/열기는 마감했다. graph 등 다른 원본 본문 표현의
깊이/예산 내 adapter, 참가자/Helper·연락처/대화(V4/V5)·office(V3), V6/V7 자산·편집,
V8 내장 surface/audio provider, 종류 C# 표현/사용중 항목 삭제 대응, V1/V2 후속은 남는다.
임의 전체 파일 탐색/모든 graph 깊이/타입 문맥 곱은 새 필수 요구로 만들지 않는다.
DISPLAY/Xvfb·오디오 장치와 내장 provider 부재를 모의 화면/사운드로 채우지 않았다.
실제 Windows apphost/WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달은 미완료다.
3D/권한 별도 팩·이동 연출과 실행 분리·명시 async caller 규칙을 유지한다. main을
보존하고 live AI·계정/키·유료 호출·새 외부 접근은 수행하지 않았다.
