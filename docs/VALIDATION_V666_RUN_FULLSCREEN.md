# V666 Run 최대화·복원 검증

제품·검사·도구 동결은 `76827d3aba2384acc66a67cea24de470d5de9ae2`이며 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V8_RUN_FULLSCREEN.md)와 [검토한 정확한 delta](v666-run-fullscreen-delta.json)를 따른다.

## 원본과 실제 누락

게시본 `593ffa603cf1ac9a2dfa918255ef4a9609de47c9`에서 실제 Run 창을 열고
원본 v666 `data-run-maximize` 버튼이 없음을 먼저 확인했다. 저장 복구의 가능한 조합을
무한 잔여로 늘리는 대신, 고정 V8의 독립적으로 제공 가능한 최대화·복원 흐름을 연결했다.
근거는 `reference/site-ui/Confectory-Editor-Prototype-v666.zip` 안
`Confectory-v666/dist/app.js`의 `enterRunFullscreen`/`exitRunFullscreen`과 동봉 CSS다.

같은 DOM을 화면 크기로 표시하고 버튼/Esc로 원래 탭/플로팅 레이어로 돌린다.
원래 위치/크기와 개인 입력을 유지하며 resize 뒤에는 기존 창 맞춤 규칙을 따른다.
브라우저 전체 화면은 지원하면 요청하고 거절/미지원이면 CSS 최대화를 유지한다.
닫기·접기·프로젝트/세대 변경·재도킹·지연 응답과 실행 소유권은 분리한다.

원본 CSS와 native 창의 inline z-index 충돌, 문서 탭의 숨겨진 닫기 버튼,
floating resize의 재배치, 메뉴/확인 대화상자의 쌓임 순서를 같은 흐름에서 보강했다.
실제 Play/Pause/Step/Close는 기존 view/lease/handle/ACK 검증을 그대로 따른다.
내장 renderer·가짜 FPS·오디오/해상도 설정·새 실행 권한을 추가하지 않는다.

Core·targets·packs, 기존 `feature-authoring.js`·Blueprint·RunWindows backend는
이전 게시본과 byte-identical이다. 원래 C# bytes·공개/override 계약·부모/외부 데이터·
권한·Review→Confirm·최종 저장 CAS와 M11/M12/M4 마감은 그대로다.

## 최종 검증

독립 LF 13·CRLF 13·새 교차 패키지/전체 복원/실패 수명관리
및 공통 IPC 수명관리 9, **총 35단계(신규 35·재사용 0)** 통과했다.
공통 수명관리 단계에는 실제 프로세스/실패/재시작/패키지 보관 22개 검사가 포함된다.
개발 재현·반복 검사와 이전 완료 기능의 역사적 증거는 이 최종 합계에 넣지 않는다.
Git 객체·EOL·NuGet/home·엔진 cache가 분리된 LF/CRLF checkout에서 각각 빌드했다.

- 정상 UI: 실제 Linux .NET 엔진과 Chromium에서 브라우저 전체 화면 진입, 버튼/Esc 반복,
  동일 DOM/원래 geometry/개인 입력, 실제 Play/Pause/Step의 단일 handle·lease·ACK 보존을
  확인했다. 최대화 자체가 실행을 만들지 않고, 명시적 닫기만 소유 실행을 종료한다.
- 기존 내보내기 메뉴·선언되지 않은 Android 대상의 정상 거절 안내·프로젝트 종료 확인은
  overlay 위에서 조작 가능하다. 종료 취소는 실제 프로세스를 유지하고 빌드/확정을 만들지 않는다.
- 문서/플로팅 창, 브라우저 전체 화면 거절·미지원, resize·접기/펼치기·드래그 차단을
  확인했다. 390px viewport는 브라우저 반응형 검사이며 실제 모바일 기기 검사가 아니다.
- 응답 유실 뒤 Retry는 같은 실행을 관측하고 Start를 재생하지 않는다. 변조 lease의 닫기는
  거절하며 원래 창·실행·입력을 보존하고 명시적 재시도에서만 종료한다.
- 지연된 native 요청의 취소 뒤 성공, 같은 프로젝트의 명시적 다른 Run 전환,
  거절·다른 요소의 전체 화면 소유권은 제어된 browser API fixture로 검증했다.
  실제 브라우저 fullscreen 성공 경로와 이 fault-injection 경로를 구분한다.
- 실제 ProjectContext A→home→B→cold→A 왕복에서 overlay와 늦은 응답을 정리하고,
  같은 이름의 다른 프로젝트가 A view/lease를 쓰지 못함을 확인했다. 재시작은 원래 창/
  geometry/개인 입력만 복원하며 fullscreen·실행 handle·권한을 layout에서 복원하지 않는다.
- 기존 실제 Run backend 소유권/프로토콜과 문서/플로팅 창 renderer fixture를 회귀했다.
  새 패키지 구조/무결성·패키지 엔진의 정상/fallback, 전체 SHA/CRC/권한 모드로 완전히
  복원한 엔진의 응답 유실/닫기 실패/지연 fullscreen과 실패 수명관리를 검사했다.

개발 검사 중 동적 visible locator, 외부 API로 프로젝트를 바꾸기 전 geometry flush 누락,
재개 창의 fresh idle lease를 과거 closed receipt로 간주한 fixture를 수정했다.
제품 결함과 구별하고 실패 화면·입력·로그를 보존했다. 실제 Run 종료가 남긴 frame socket은
실행에 등록된 runtime inode/UID·모든 worker의 자식 회수 증명·커널 bound endpoint 부재를
확인한 뒤 내용 없이 metadata로 보관했다. 활성/출처 불명/종료 미확인/커널 조회 불가의
거절과 압축 복원을 별도 검증했다. FD/maps 제한은 우회하지 않았다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/3669bcea2bb745318952c1b6efe9b1c5.json`

개발 증거 SHA `96a1f92ed2c5da54ee6e04618441b603532bb4675b2d9dc458e5c00f94fe3327`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/63258cc946d94fe7ac8c14c245e6b3b0.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/63258cc946d94fe7ac8c14c245e6b3b0.zip`

SHA `770f8a7bda42f51081e9171cc34d406a0d5a95389a7c6fc1aaf4fb1979cbac11` (6.51MiB).

## 보관·공간·유한 잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `76827d3aba2384acc66a67cea24de470d5de9ae2`, `0cfb3fb9580426c3b241a15af1d1dec7d5c77013f0d549e0790c01ba51876fe6.zip`, 49.14MiB, 파일 2381·디렉터리 147, manifest `6a612e7c9f42b45baa2c7202ed19b1385463c8d67b46fedad99527dbb8d2a25c`.
- rollback: `fd65b6ed5b180c690e1ea1fffcf832927f9f06b0`, `8a5333c21e66a26a5ad3bf283260403390fa97606754827c3aba9e2cc1d2ab35.zip`, 49.14MiB, 파일 2381·디렉터리 147, manifest `e560fd80ee6fbd6cf7ac8eebd6d508dc64b08c9a913be1dcbe3276f09d80a3ca`.

전체 SHA/manifest·복원 검증 후 승인된 managed 수명관리로 최신/이전 정상 rollback과
증거를 지속 보관하고 이번 실행 소유 임시물만 정리했다. 다른 과거 자료·원본·로그·
프로필·SDK·캐시의 추가 삭제나 보관 정책 변경은 없다.

표본 최소 디스크 여유 1512.61MiB, 최대 cgroup 메모리 4773.42MiB.
최종 실행 순증가 7.32MiB, 개발 시작부터 보관 확인까지 순증가
16.56MiB, 문서 마감 전 여유 1505.34MiB다.
다음 단위의 고정 증가량을 보장하지 않는다.

이번 V8 최대화·복원 흐름은 마감했다. 해상도/preset·오디오·디버그 렌더 제어와 가로 회전/
기기 capability는 실제 surface/audio backend 선행 잔여다. V2 후속 안내와 재현 기반 혼합
저장 조사, V1 독립 창/배율 프로젝트 왕복의 미검증, V3 3D 표시 팩·V4 실제 권한 팩·
V5 공유 adapter·V6 소유 자산 backend·V7 미리보기/편집·V9 찾기/참여자 연결 및 종류 C#
표현/사용 중 삭제 결정은 기존 고정 목록에 남는다. 가능한 모든 조합을 새 필수로 추가하지 않는다.

실제 Windows apphost/WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달을 완료했다고
표현하지 않는다. 3D/권한 별도 팩·이동 연출/실행 분리·동기 caller의 명시적 async 전환
규칙을 유지한다. live AI·계정/키·유료 호출·새 외부 접근은 없다. main은 보존한다.
