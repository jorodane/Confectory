# V666 소유 정의 구조·종류 항목 검색 검증

제품·검사·도구 동결 `0f38e612812a76441ec5205002f92ebfb1c8bd38` 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V9_FINDER_DEFINITIONS.md)·[정확한 delta](v666-finder-definitions-delta.json)를 따른다.

## 원본과 실제 누락

기준은 저장소 v666 ZIP의 `Confectory-v666/dist/app.js`에 있는 `openWorkspaceFinder`와
`workspaceSearchText(object)`다. 배치하지 않은 객체 내용도 검색하는 원본 흐름에서
기존 `013e5a2`의 Data 읽기는 정보 필드/타입·함수 서명·종류 항목 이름을 놓친다.
기존 엔진에서 실제 누락과 기존 generic Data API의 종류 거절을 먼저 확인했다.

현재 `finderContent(ids)`는 같은 active ProjectContext/직접 소유 Read·namespace·등록 종류
검사를 쓰는 읽기 전용 endpoint다. 기존 Browser Data에 직접 선언된 필드·매개변수/반환
타입·종류 항목 이름을 더한다. parser의 내부 source location과 항목 ID/아이콘 payload를
구조 텍스트로 내보내지 않고, 별도 C# 본문이나 외부 원문을 읽지 않는다. 원래 Data와
편집 API는 그대로이며 종류를 generic Data로 편집할 수 있도록 바꾸지 않는다.

읽기 중 현재 선택/입력을 보존하고, source revision/hash 전후 일치를 확인한다. 일부 잘못된
정의는 해당 row만 unavailable로 표시한다. 원문 fallback이나 전체 확인 성공으로 채우지
않는다. 원래 팝오버/CSS·Core/targets·모든 .celem 계약·원본 C#·공개/override IO·권한·
Review→Confirm·최종 CAS·완료된 M11/M12/M4/저장 복구/Run은 유지한다.

## 최종 검증

독립 LF 16·CRLF 16·새 패키지/전체 복원/IPC·실패 수명관리 11, **총 43단계(신규 43·재사용 0)** 통과했다.
Git 객체·EOL·NuGet/home·엔진 cache를 독립시켰다. 개발 단계와 과거 증거는 최종 합계에
넣지 않는다. 역사적 완료 검증을 새 실행으로 재분류하지 않는다.

- 실제 Linux .NET/Chromium에서 배치하지 않은 정보 필드·함수 입력·종류 항목/설명을
  정확한 qualified ID로 검색하고 기존 소유 종류 정의를 여는 것까지 확인했다.
- native projection은 필드/타입·서명·항목 이름만 구조 텍스트로 내보낸다. empty/중복/65개
  요청·등록 외부/미등록 ID·임의 추가 경로 인자를 거절했다. 잘못된 종류 profile은
  해당 row만 unavailable이며 정상 row를 보존한다. 기존 enum Data 읽기/편집 거절도 유지했다.
- 생성 fixture의 원본 bytes·종류의 opaque 항목 ID·실행 계약·현재 선택/개인 입력을 보존했다.
  UI 검색 요청에 편집/Save/Review/Confirm/AI/실행이 없음을 확인했다. 동일한 owner/member ID를
  쓰는 A→cold→home→B에서 이전 검색어와 항목 내용이 재생되지 않음을 확인했다.
- 기존 Data 검색·큰 정수·복합 Unicode·상속 값·실제 draft 변경 뒤 색인 갱신·stale CAS·외부
  소유자 거절을 새 코드에서 실행했다. 지연/실패 transport fixture의 query 변경·pending Enter·
  닫기·늦은 응답·명시 재시도·cold·프로젝트/Workspace 격리도 실행했다.
- 기존 controller 64+1/foreign 응답/미확인 필드·설정 프로젝트 무조회, renderer의 busy/IME·
  비밀번호/token/hidden 제외, 배치 Ctrl+F와 실제 Run 제어/최대화 회귀를 실행했다.
  제어된 브라우저/transport fixture를 실제 OS IME·계정 backend·네트워크 장애로 표현하지 않는다.
- 새 Windows 교차 패키지 생성·구조/무결성 뒤 패키지 엔진에서 새 정의 검색과 기존 Data
  기본/중단 흐름을 실행했다. 전체 SHA/CRC/권한 모드로 완전히 복원한 엔진에서 종류의
  cold/프로젝트 격리 및 기존 Data 기본/중단을 실행했다. 성공·실패·예외 수명관리와
  증거 보존·자식 종료·소유 임시물 정리를 확인했다.

개발 중 표시용 JSON 구조 key를 사용자 검색 텍스트에서 제외하도록 정리하다가 C# 지역
변수명 충돌(CS0136) 1회를 발견해 수정했다. 바로 뒤의 1회 검사는 이전 엔진 보고서를
사용했으므로 최종 근거에서 제외했다. 수정 빌드·실제 normal 검사를 통과했고 최종 검사는
전부 새 checkout/새 엔진에서 실행했다. 실패와 기준 누락 재현 기록도 보존했다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/ff9508ccba094d0ea757985243bf9bb8.json`
개발 증거 SHA `1c069b36eda004e2f68cf1074595862a002cb038f9649e5622ecd43af9e74c09`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/2b8cb52e813e45c4adae399290f58007.json`
최종 증거 `/workspace/artifacts/v536-verification-managed/runs/2b8cb52e813e45c4adae399290f58007.zip`
SHA `2ea3eebeb6736656140a11b41df791a720254250119e87d5352ebb522c681ea4` (5.16MiB).

## 보관·공간·고정 잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `0f38e612812a76441ec5205002f92ebfb1c8bd38`, `198f4f49c125c39c08dd7e9d1fb5868ca7603bddfe3a13eb49403ce03c1c6740.zip`, 49.15MiB, 파일 2383·디렉터리 147, manifest `d30e55379b080770c54f5738fcf89c0f1a805e728c238dcc4ee9144693b87a8f`.
- rollback: `47cd51d7b6a9be264349394f9c28af182ee009a8`, `ec4fe34177d4553f30d30d5deae3868ec7d54f8caead84d80b0ee30878e34017.zip`, 49.15MiB, 파일 2383·디렉터리 147, manifest `a6b62d678667821857ff4968f0c02e38b715fb32ff1b084c7fb1eb3b2d380685`.

전체 archive SHA/manifest·복원 확인 후 승인된 최신/이전 정상 롤백과 증거를 지속 보관했다.
해당 실행이 만든 임시물만 소유/자식 종료 확인 뒤 정리했다. 다른 과거 자료·원본·로그·
프로필·SDK/캐시 삭제나 보관 정책 변경은 없다.

표본 최소 디스크 여유 1487.65MiB, 최대 cgroup 메모리 4832.80MiB.
최종 실행 순증가 6.14MiB, 개발 시작부터 보관 확인까지 7.64MiB,
문서 마감 전 여유 1481.57MiB. 다음 단위의 증가량은 보장하지 않는다.

직접 소유 필드/서명/종류 항목과 Data 검색은 마감했다. 원본 functionDefinition.body처럼
객체가 보관하는 구현 본문의 깊이/문자 한도 내 검색과 그 실제 읽기 adapter,
참가자/Helper·연락처/대화(V4/V5), office(V3)와 고정 V6/V7 자산·편집, V8 내장 화면/오디오
backend, 종류 C# 표현/사용중 삭제 결정, V1/V2 후속은 남는다. 현재 Run surface IPC/audio
provider 계약과 DISPLAY/Xvfb/오디오 장치는 없어 시연을 실제 renderer/음성 성공으로 채우지
않았다. 실제 Windows apphost/WebView2·모바일·DPI/IME·전체 UI·Library/Space는 미완료다.
3D/권한 별도 팩·이동 연출/실행 분리·명시 async caller 규칙을 유지한다. main을 보존하고
live AI·계정/키·유료 호출·새 외부 접근은 수행하지 않았다.
