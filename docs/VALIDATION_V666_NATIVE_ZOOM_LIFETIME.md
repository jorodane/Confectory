# V666 일반 Blueprint 읽기·확대 수명 검증

동결 제품·검사·도구 `5deb5f28311aa275570dffd2f3c301b270c82b32` 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V1_NATIVE_ZOOM_LIFETIME.md)·[정확한 delta](v666-native-zoom-lifetime-delta.json)를 따른다.

## 관측·수정

고정 v666 `dist/blueprint.js:1407–1421`의 기존 확대 흐름에 대응하는 일반 Blueprint의
별도 viewport를 조사했다. 게시 `afeaf23`와 제품 코드가 같은 패키지 `5304b65`를 전체
SHA/manifest로 복원했다. 최초 실제 엔진 검사는 확대 전에 일반 Blueprint 진입의
`stale_revision`에서 멈췄다. 이 자연 발생 실패의 증거를 보존하고 통과로 세지 않았다.
새 fixture 재현에서는 원래 일반 Blueprint를 열어 닫힌 팝오버의 slider 함수를 호출하니
재개방한 viewport의 500%가 200%로 바뀌었다. 지연은 직접 callback 전달이며 OS 지연
또는 실제 기기 결함을 시험했다고 표시하지 않는다. 사용자 프로젝트/파일은 사용하지 않았다.

명시적 열기의 `list/read`만 프로젝트를 재확인해 view를 갱신하고 실제 `stale_revision`
거절에 한해 최대 세 번 관측한다. 다른 오류·scope 변경을 재시도하거나 변경/Save/
Confirm/실행 요청을 재생하지 않는다. 기존 `active()`를 zoom/fit/열기에 적용하고
입력·slider·preset·fit·Escape는 현재 팝오버 인스턴스에만 적용한다. markup/CSS·
배율/카메라 계산·원문/C#·IO/ID/핀/연결·부모/외부 원본·권한·Review→Confirm·최종
CAS·Undo는 보존한다. 다른 제품 변경은 두 UI 자산의 canonical pin 갱신뿐이다.

## 최종 검사

**31단계, 신규 31·재사용 0**, 모두 exit 0이다.
LF 12·CRLF 12·새 패키지/전체 복원/실패 수명관리
7로 구성한다. 독립 Git 객체·EOL·NuGet/home·빈 엔진
캐시에서 시작했다. 초기 재현/실패·개발 검사와 과거 통과를 이 합계에 넣지 않는다.

- 실제 생성 프로젝트의 일반 Blueprint를 한 번 명시적으로 열 때, 로컬 route가 요청을
  실제 서버에 stale revision으로 전달해 두 번 거절시켰다. 읽기만 재관측해 정상 진입했다.
  세 번 거절하는 경우 정해진 한도로 멈추고 source/부분 창을 만들지 않았으며 다음
  명시적 열기는 정상 동작했다. 다른 오류의 자동 재시도나 source 변환은 추가하지 않았다.
- 실제 엔진에서 재개방·반복 취소 뒤의 slider/preset/fit/blur/Enter/Escape가 현재 배율과
  새 미적용 입력을 덮지 않았다. 유효한 Enter/preset은 정상 적용했다. cold는 400%와
  개인 입력만 복원하고 명시적 현재 원본 읽기 후에만 실제 편집 화면을 다시 연결했다. 숨긴 실제 창은 오래된 열기/입력 함수로 팝오버를 다시 만들지 않았다.
- 실제 viewport 모듈/DOM의 통제 검사는 큰 카메라·wheel 포인터 기준·500%·Escape·
  source identity와 동일 DOM의 폐기/remount·stale 소유 문맥을 확인했다. 이 부분은
  실제 엔진/기기 검사로 표시하지 않는다. Workspace의 기존 반복/cold·A→홈→B→A와
  서로 다른 프로젝트의 배율/개인 입력도 실제 엔진의 관련 회귀로 다시 실행했다.
- 실제 fixture의 물리 원본은 byte 단위로 미변경이며 UI는 source 변경/Save/Review/
  Confirm·작업 실행을 호출하지 않았다. 새 source 거래가 없으므로 기존 최종 CAS의
  충돌 검사를 새로 통과한 것으로 계상하지 않는다. delta 감사로 source/backend 경계를 유지했다.
- 새 Windows 교차 패키지의 구조/무결성·packaged managed engine을 확인했다. 전체
  SHA/CRC/권한으로 복원한 엔진에서도 읽기 거절/재시도·확대 수명과 Workspace 프로젝트
  회귀가 통과했다. Linux .NET/Chromium 실행이며 실제 Windows apphost/WebView2 실행이 아니다.
- 성공·반복 성공·실패·예외 등의 기존 수명 검사도 통과했다. 자식 프로세스 종료와 증거
  보존 후 해당 실행의 소유 임시물만 정리했다. 최신/롤백 보관도 검증했다.

첫 구현 `37cbad2`의 LF에서는 retry가 오류 코드를 담은 `Error.message` 대신 존재하지 않는
`error.code`를 검사해 첫 주입 거절에서 멈췄다. 기존 WebUI client 계약을 읽어 확인한 뒤
predicate와 canonical pin을 고쳤다. 이 실패 record `/workspace/artifacts/v536-verification-managed/runs/0ecfea3e8c2c448b82868edc1aeb5e87.json`와
증거 SHA `436c1b3c1af64ad2170c5996666c4f10989c103a792842fb33dd3036d6884205`도 보존했다. 제품 코드가 바뀌었으므로 최종
LF/CRLF·모든 관련 UI·패키지/복원을 새로 실행했으며 앞선 통과를 합계에 재사용하지 않았다.

이후 `9a682f65`의 LF는 새 읽기 거절/재시도와 배율 수명까지 통과한 뒤 cold 검사에서
멈췄다. 일반 Blueprint의 cold는 배치만 복원하고 ‘현재 원본 읽기’가 있어야 데이터와
편집 화면을 연결하는 정상 보호다. fixture에 그 명시 동작과 cold의 편집 화면 부재
확인을 추가했으며 제품 코드는 바꾸지 않았다. 실패 `/workspace/artifacts/v536-verification-managed/runs/862e42977ae148e683b6bf1a5f43f2cd.json`도
보존했다. 실패 수명관리로 앞선 임시 빌드가 정리돼 최종 UI/패키지 실행용 독립 빌드를
다시 만들었으며 최종 합계는 이 새 실행만 사용한다.

초기 진입 실패: `/workspace/artifacts/v536-verification-managed/runs/348f0b6b78b04c73a5f22c40d7a719c7.json`, 증거 SHA `8ff2a761e2d7263b12bd6b60a386a93c4566e31ed43619de8577babdc9858c07`.

원래 배율 결함 재현: `/workspace/artifacts/v536-verification-managed/runs/b4866b5644e34d52a305fe856600d305.json`, 증거 SHA `b3e3d907981183f77559ec11a1a83e13d05119ca1912999b2b78c272fe06b0e5`.

개발 모듈 증거: `/workspace/artifacts/v536-verification-managed/runs/b7851a6749514ca39d7e1d95c9e28fd8.json`. 실행이 직접 만든 결과 두 파일을 확인해
관리 실행으로 옮겨 보존했으며 다른 임시물·과거 자료를 수집하거나 삭제하지 않았다.

최종 record `/workspace/artifacts/v536-verification-managed/runs/224142fb94a344be95d3ccc4b43891c7.json`

증거 `/workspace/artifacts/v536-verification-managed/runs/224142fb94a344be95d3ccc4b43891c7.zip`

SHA `34ea253f4bed30053c8fee6d7fb29b79c9c038708e1706b9f7b6a214e7233096` (1.37MiB).

## 보관·공간·유한한 잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `5deb5f28311aa275570dffd2f3c301b270c82b32`, `a2a9a5c37e230c5a587e73c9b2fbe96038bd42f23e0890b1b75c9b98b2a642a3.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `fa3bf332426ad753cee09db87ef8c81d7d20ebbaa8a307561609f995ac6c5b36`.

- rollback: `5304b65237cb020780781ea7c32ae25b9ddd5592`, `ca2446a0e5c3415305506f25ede63516883ddb052ff2b5162cc9d7e304a2eb7e.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `ab6c1868ef9786b93afb58f7e4f90dd73ad819c2cbba6133feabf4a1f9667fbb`.


최신/롤백과 모든 위 증거의 전체 SHA/manifest를 재확인했다. 기존 승인된 두 세대
원자 승격/실패 복구와 소유 임시물 수명만 사용했다. final RAM root는 제거됐다.
표본 최소 디스크 여유 1532.66MiB, 최대 cgroup 메모리 4478.11MiB.
최종 관리 실행의 순증가는 2.18MiB이며 현재 여유는 1530.52MiB다.
단위 전체 df 변화는 -114.66MiB이지만, 첫 실패 실행 구간에 별도로 관측된 약
117.90MiB의 여유 증가 원인을 이 검사로 특정하지 못했다. 이를 구현의 절감 효과나
향후 단위당 증가량으로 계상하지 않는다. 기존 144MiB 추가 예산/64MiB 안전 여유는 유지했다.

일반 Blueprint 수명을 마감하며 독립 정보 창의 모든 배율 문맥·DPI/IME는 별도 미검증이다.
M11/M12/M4를 새 조합으로 다시 늘리지 않는다. V2 다른 노출 안내, V3–V7 실제 팩/
상태/권한/자산 backend, V8 실제 surface/audio provider, V9 신원/가시성 및 종류 C# 표현/
사용 중 삭제 대응의 기존 경계는 유지한다. RunWindows의 실제 capability는 여전히
`surfaceSupported=false`, `fpsSupported=false`이며 frame-control IPC를 영상/음향으로
표시하지 않는다. 실제 Windows·모바일·전체 UI·Library/Space 전달은 미실행이다.
새 신원/권한·접근·과금·보관정책·원문 자동변환 결정은 없고 main은 사용자가 병합한다.
