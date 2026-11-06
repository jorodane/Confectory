# V666 작업 공간 찾기 검증

제품·검사·도구 동결은 `d9ceb3cf1fc41f167d0b12672dec302f3ba90f02`이며 이후 마감 commit은 문서만 바꾼다.
[이번 지원 경계](V9_WORKSPACE_FINDER.md)와 [정확한 delta](v666-workspace-finder-delta.json)를 따른다.

## 원본·누락·안전한 다음 단위

게시본 `b24fe4cc82ecaf5131007632b16975a59ed66ab9`에서 기존 배치 Ctrl+F는 작동하지만
v666의 검색 버블/요소 패널은 없음을 실제 엔진에서 확인했다. 기준 ZIP 안
`Confectory-v666/dist/app.js`의 `openWorkspaceFinder`·검색 helpers·버블 markup과 CSS를
실제 허용 프로젝트 상태로 연결한다. 기존 Ctrl+F를 중복 구현하거나 M11/M12/M4를 다시 열지 않는다.

원래 버블에서 현재 보이는 창·메모·하위 Workspace 표지의 이름/글자와 현재 허용된
선언 이름/종류를 검색하고, 정확한 key/qualified ID로 기존 창 중심 표시/선언 열기를 한다.
검색 열기는 기존 탐색기의 읽기 전용 localInventory/relationsMap만 재사용하고, 추가 파일
원문/외부 부모/계정·작업의 가시성은 만들지 않는다. pending/busy 중 선택을 거절하고
성공 뒤 자동 실행하지 않는다. 실패/명시 재시도·현재 내용/목록 갱신과 transient query를 다룬다.

제어된 브라우저에서 공통 추출기의 `aria-hidden` 영역 입력 노출을 재현해 기존 password/
token/hidden 보호와 함께 제외했다. 실제 채팅에서 버블로 이동할 때 blur 저장이 첫 클릭을
막는 진입 결함도 재현해 기존 Run/검토와 동일한 개인 입력 보존 경로에 연결했다.
원래 HTML을 해석하지 않고 결과 텍스트로만 표시한다.

Core·targets·packs, source authoring·Workspace ownership/lifetime·Run backend/최대화는
이전 게시본과 byte-identical이다. C# bytes·public/override 계약·부모/외부 원본·권한·
Review→Confirm·최종 CAS와 완료된 저장 복구를 보존한다.

## 최종 검증

독립 LF 14·CRLF 13·새 교차 패키지/전체 복원/실패·공통 IPC 수명관리
9, **총 36단계(신규 36·재사용 0)** 통과했다.
공통 수명관리 단계에는 실제 프로세스/실패/재시작/패키지 보관 22개 검사가 포함된다.
개발 반복/실패 재현과 역사적 증거는 이 최종 합계에 넣지 않는다. Git 객체·EOL·NuGet/home·
엔진 cache를 독립시킨 두 checkout에서 빌드했다.

- 실제 Linux .NET 엔진/Chromium: 원래 버블·요소/글자 모드, 개인 메모의 대소문자 무관
  검색·literal HTML·정확한 방향키/Enter 대상 이동·기존 선언 열기·반복 닫기/재진입,
  현재 메모 내용 갱신과 기존 배치 Ctrl+F를 확인했다. 390px viewport의 원래 모바일
  검색 패널도 확인했으며 실제 모바일 기기 실행으로 표현하지 않는다.
- 개인 child Workspace는 현재 배치된 메모만 검색하며 전환은 이전 panel/listener/query를
  폐기한다. 실제 A→cold→home→같은 이름의 B에서 개인 입력/메모가 분리되고 query가
  저장·재생되지 않음을 확인했다. 이전 결과로 source/runtime/AI/Review/Confirm을 쓰지 않는다.
- metadata invoke 직전 fetch를 보류·거절하는 명시적 transport fixture에서 pending Enter가
  실행/재생되지 않고 검색어·메모·채팅 입력을 유지했다. 명시 재시도만 기존 관계 조회를
  수행하고 결과를 복구했다. 실제 저장소/권한 backend 실패를 재현했다고 주장하지 않는다.
- 별도 제어된 renderer: 같은 표시명도 정확한 ID 선택, 허용 projection에서 제거된 결과의
  재검증, busy/다른 프로젝트의 stale callback 거절, IME/legacy229 Enter·Esc 보호,
  visible private 값과 password/token/hidden/aria-hidden 제외를 확인했다. 이는 native
  계정/그룹 backend 권한 검증이나 실제 OS IME 검사가 아니다.
- 기존 find IME renderer와 실제 Run 최대화·재생/Pause/Step·메뉴/종료 취소·반복/390px
  viewport/닫기 회귀를 새 코드에서 실행했다. 다른 완료 증거는 해당 기록에 남기며 신규
  합계에 재사용·합산하지 않는다.
- 새 Windows 교차 패키지 구조/무결성과 패키지 엔진의 기본/Workspace·프로젝트/cold를
  검사했다. 전체 SHA/CRC/권한 모드로 완전히 복원한 엔진에서 기본·목록 실패/재시도를
  검증했다. 성공/반복/실패/예외 수명관리, 증거 보존·자식 종료·소유 임시 정리를 확인했다.

개발에서 목록 조회 전 Enter 뒤 자동 선택을 기대한 fixture와 panel 뒤 portal을 직접
클릭한 fixture는 제품 안전 거절/정상 pointer 소유권과 구분했다. 결과 활성화 뒤의 명시
선택과 실제 Workspace 탭 전환으로 수정하고 실패 기록을 보존했다. 목록 미로드·채팅
blur 진입·aria-hidden 추출은 실제 구현 결함으로 수정했다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/5bbd03af1b6d4be8a5c85fd87878681b.json`

개발 증거 SHA `09a1031050891c52ff8c9e4606b6adec894ee7db6e129348fe4d0fbbb9c2739f`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/7e41440a5f814ddb91f5afe2b6305489.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/7e41440a5f814ddb91f5afe2b6305489.zip`

SHA `0c77bdaabb1517c57f0b378bf5716e31321c26f4a2c1c1caf25e483794d24678` (2.86MiB).

## 보관·공간·유한 잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `d9ceb3cf1fc41f167d0b12672dec302f3ba90f02`, `ae9fd5d6fcb705c20236d1b89a7fc7ae6ce75dc736e6697fb6f34b7494bba0c2.zip`, 49.14MiB, 파일 2382·디렉터리 147, manifest `345393880afaf79097f2b35a405ad6ea26c8e95c2776a510cfc18ee1e677b09b`.
- rollback: `76827d3aba2384acc66a67cea24de470d5de9ae2`, `0cfb3fb9580426c3b241a15af1d1dec7d5c77013f0d549e0790c01ba51876fe6.zip`, 49.14MiB, 파일 2381·디렉터리 147, manifest `6a612e7c9f42b45baa2c7202ed19b1385463c8d67b46fedad99527dbb8d2a25c`.

전체 SHA/manifest·복원 검증 후 승인 managed 수명관리로 최신/이전 정상 rollback과 증거를
지속 보관하고 해당 실행 소유 임시물만 정리했다. 다른 과거 자료·원본·로그·프로필·SDK·
캐시의 추가 삭제나 보관 정책 변경은 없다.

표본 최소 디스크 여유 1503.59MiB, 최대 cgroup 메모리 4764.95MiB.
최종 실행 순증가 3.70MiB, 개발 시작부터 보관 확인까지 순증가
5.28MiB, 문서 마감 전 여유 1499.95MiB다.
다음 단위의 고정 증가량을 보장하지 않는다.

이번 V9 배치/허용 이름 찾기는 마감했다. 배치하지 않은 객체의 전체 내용 검색은 실제
읽기 adapter, 참가자/Helper/Worker·연락처/대화는 V4/V5 실제 가시성 adapter, office 방/
작업자 이동은 V3 표시 팩의 후속 경계다. 가짜 사용자/Worker/권한을 만들지 않는다.

기존 RenderInput/Window는 명시 소유 native 창의 rectangle/text renderer이고 Stage는
선택 소비자의 자원 수명만 제공한다. Run 안으로 실제 화면을 전달/설정하는 surface 계약과
audio provider는 아직 없다. V8 해상도·오디오·렌더 debug를 UI 표시만으로 완료 처리하지 않는다.
V1 독립 창/배율 프로젝트 왕복의 미검증·V2 후속·V3–V7 팩/backend·종류 C# 표현/사용중
삭제 결정·실제 Windows apphost/WebView2/모바일/DPI/IME·전체 UI·Library/Space 전달은
기존 고정 목록에 남는다. 조합마다 새 필수 범위를 만들지 않는다.

3D/권한 별도 팩·이동 연출/실행 분리·동기 caller의 명시 async 전환 규칙을 유지한다.
live AI·계정/키·유료 호출·새 외부 접근은 없다. main은 보존한다.
