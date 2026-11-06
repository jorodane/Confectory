# V666 소유 선언의 내용 찾기 검증

제품·검사·도구 동결은 `47cd51d7b6a9be264349394f9c28af182ee009a8`이며 이후 마감 commit은 문서만 바꾼다.
[이번 지원 경계](V9_FINDER_CONTENT.md)와 [정확한 delta](v666-finder-content-delta.json)를 따른다.

## 원본과 구현 범위

기존 `d92e7b0`은 배치된 창/메모와 허용 선언의 이름/종류를 찾지만 배치하지 않은 선언의 값은
읽지 않는다. 저장소 v666 ZIP의 `openWorkspaceFinder`·`workspaceSearchText`는 배치하지 않은
프로젝트 객체 내용도 검색한다. 이를 기존 권한 검증된 `browserElements` 읽기 표현과 소유
선언 설명에 연결했다. 원문 전체 읽기나 외부 가시성·권한 확장은 하지 않는다.

qualified ID별 설명·Browser Data가 노출하는 값·상속된 유효 값·복합 Unicode를 검색한다. 정수는 원래 JSON
숫자 표기를 보존한다. 64개 배치, 이미지 payload/깊이/문자수 제한, 현재 source 기준 갱신,
일부/미지원/실패 안내와 명시 재시도, 늦은 응답 폐기와 검색어의 비영속 수명을 연결했다.
기존 CSS·배치 Ctrl+F·Run·source authoring과 src/targets/packs는 기존 게시본과 동일하다.
C# bytes·원본/override 계약·권한·Review→Confirm·최종 CAS·M11/M12/M4는 바꾸지 않는다.

## 최종 검증

독립 LF 15·CRLF 15·새 교차 패키지/전체 복원/IPC·실패 수명관리 9, **총 39단계(신규 39·재사용 0)** 통과했다.
두 checkout의 Git 객체/EOL/NuGet/home/엔진 cache는 독립이다. 개발 반복과 실패 재현은 이
합계에 넣지 않는다. 과거 증거를 새 검증으로 재분류하지 않는다.

- 실제 Linux .NET/Chromium: 배치하지 않은 Data/설명, 동일 표시명의 ID, 정확한 큰 정수,
  상속·복합 Unicode, 현재 선택/개인 입력 보존과 기존 정의 열기를 확인했다.
- 생성 fixture의 기존 Data 편집은 draft에만 반영하고 sourceWritten=false를 확인했다.
  변경 뒤 색인 갱신, 이전 CAS 재사용 거절, 등록 외부 ID 내용 읽기 거절, Confirm 없음과
  모든 원본 bytes 보존을 확인했다. UI 검색 요청에는 편집/Review/Confirm/실행이 없다.
- 명시적 transport fixture의 지연/실패, 읽기 중 query 변경·Enter·닫기, 늦은 응답 폐기,
  명시 재시도, cold→home→같은 namespace/ID의 B 프로젝트 격리와 검색어 비저장을 확인했다.
  이는 실제 네트워크/계정 backend 장애를 재현했다는 뜻이 아니다.
- 제어된 controller에서 64+1 배치/허용 ID 제한, foreign reply, 미확인 필드·지원하지 않는
  종류의 partial 표시, 설정 프로젝트의 무조회, 복합 이미지 payload 제외를 확인했다.
  renderer guard에서 projection 재검증·busy/IME·password/token/hidden 제외를 확인했다.
- 기존 Workspace/프로젝트 찾기·목록 실패/재시도, 배치 Ctrl+F/IME와 실제 Run 최대화·제어
  회귀를 새 코드에서 실행했다. 실제 OS IME/모바일/계정 권한 backend 검사로 과장하지 않는다.
- 새 Windows 교차 패키지의 생성·구조/무결성, 패키지 엔진의 기본·중단/재시작을 검사했다.
  전체 파일 SHA/CRC/권한 모드로 복원한 엔진에서도 같은 흐름을 통과했다. 성공/실패/예외
  증거 보존과 자식 종료·소유 임시물 정리를 기존 수명관리 검사로 확인했다.

개발 중 정의 열기 대기는 Python time.sleep이 Playwright의 routed 응답 처리를 멈춘 fixture
문제였다. 실제 native select가 정상임을 확인한 뒤 page.wait_for_timeout으로 응답을 처리하며
기다려 정확한 대상 열기를 검증했다. 열린 source 창과 정의 결과를 같은 하나의 결과로
가정한 fixture도 구분했고 실패 기록을 보존했다. 이를 제품 수정/실패로 혼동하지 않는다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/d043979f1f604e0dba9fe5a343db7582.json`
개발 증거 SHA `a98158e1118219cdeb7eff76978e5b507db6f8b780af9810477f0fea9258a648`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/d32db925ecec43e2aaf3dc709fc0bafc.json`
최종 증거 `/workspace/artifacts/v536-verification-managed/runs/d32db925ecec43e2aaf3dc709fc0bafc.zip`
SHA `3b176844a022dce2fd46f071efb20ba76e3390890708856ec602d162f1b165be` (4.31MiB).

## 보관·공간·잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `47cd51d7b6a9be264349394f9c28af182ee009a8`, `ec4fe34177d4553f30d30d5deae3868ec7d54f8caead84d80b0ee30878e34017.zip`, 49.15MiB, 파일 2383·디렉터리 147, manifest `a6b62d678667821857ff4968f0c02e38b715fb32ff1b084c7fb1eb3b2d380685`.
- rollback: `d9ceb3cf1fc41f167d0b12672dec302f3ba90f02`, `ae9fd5d6fcb705c20236d1b89a7fc7ae6ce75dc736e6697fb6f34b7494bba0c2.zip`, 49.14MiB, 파일 2382·디렉터리 147, manifest `345393880afaf79097f2b35a405ad6ea26c8e95c2776a510cfc18ee1e677b09b`.

전체 archive SHA/manifest·완전 복원 검증 후 승인된 managed 최신/이전 정상 롤백과 증거를
지속 보관했다. 이번 실행이 생성한 임시물만 자식 종료/소유 확인 뒤 정리했다. 다른 과거
자료·원본·로그·프로필·SDK/캐시 삭제나 보관 정책 변경은 없다.

표본 최소 디스크 여유 1494.46MiB, 최대 cgroup 메모리 4826.77MiB.
최종 실행 순증가 5.21MiB, 개발 시작부터 보관 확인까지 10.49MiB,
문서 마감 전 여유 1489.32MiB. 다음 단위의 증가량을 보장하지 않는다.

이번 소유 설명/Browser Data 검색은 마감했다. 원문 C#/그래프 구조·미지원 종류 내용,
참가자/Helper·연락처/대화(V4/V5), office(V3), V6/V7 자산·편집과 V8 내장 surface/audio
backend는 고정 잔여로 남는다. 이 환경에는 DISPLAY/Xvfb와 오디오 장치가 없으며,
현재 Run surface IPC/audio provider도 없어 화면/음성을 모의 성공으로 채우지 않았다.
종류 C# 표현/사용중 항목 삭제 결정, V1/V2 후속과 실제 Windows apphost/WebView2·모바일·
DPI/IME·전체 UI·Library/Space 전달은 미완료다. 기존 3D/권한 별도 팩·이동 연출/실행
분리·동기 caller의 명시 async 전환 규칙과 main을 보존한다. live AI·새 계정/키·유료 호출은 없다.
