# V666 3D Workspace 보기 검증

최종 코드/검사 동결 commit: `6ad5b5d45dd88bea3a2fa177cd55ec486fde4a67`. 이후 게시 마감은 문서만 변경한다.
[지원 경계](V3_WORKSPACE_VIEW.md)와 [정확한 제품 delta](v666-office-view-delta.json)를 따른다.

최종 **35단계: 신규 35 / 재사용 0** 통과.
LF 12 · CRLF 14 · 패키지/전체 복원/실패 수명관리 9.
독립 Git 객체/빈 엔진 캐시/SDK home/NuGet 복사본을 사용했다. 사전 안전 예산은 추가
144MiB(64MiB 안전 포함), 별도 RAM 3GiB와 RAM filesystem 여유, 추가 메모리 7GiB+1GiB다.
안전 기준을 낮추지 않았다.

실제 생성한 두 프로젝트와 관리형 엔진/Chromium software WebGL에서 확인했다.

- 실제 소유 분류의 원본 3D 방 표시·지도/방 메뉴→기존 Browser·읽기 전용 메뉴.
- 150% 카메라와 반복 패널/3D 전환·폐기한 popup callback·프로젝트 A/홈/B/A의 이전
  배율 열기 callback·동일 namespace/표시 이름의 프로젝트 격리.
- 늦은 모듈 응답을 명시적으로 취소한 뒤 편집기로 유지·새 엔진의 개인 카메라/보기 복원.
- 서버 checkpoint 후 성공 응답 유실을 제어 주입하고, 저장 중 새 300% 카메라를 유지한 뒤
  같은 프로젝트의 다음 private checkpoint를 재시도. 원본 source는 바꾸지 않았다.
- WebGL context 생성 불가와 고정 자산 SHA 불일치를 각각 주입. 기존 편집과 개인 배율이
  유지되며 성공한 renderer/Worker 실행으로 표시하지 않는다.
- 기존 native Blueprint Apply의 늦은 설명 입력과 Workspace 배율 수명 회귀.
- 새 Windows 교차 패키지의 구조 검사, 패키지 엔진 UI, 압축 전체 파일 SHA/CRC/디렉터리 모드
  복원과 복원 엔진의 cold/응답 유실/비지원/변조 경계. 실패 수명관리 검사를 포함한다.

이벤트/응답 유실·WebGL 불가·변조는 통제된 검사 조건이다. 실제 Windows apphost/WebView2,
모바일/하드웨어 GPU·DPI/IME·전체 UI·Space/Library 전달·프로젝트 Run 영상/오디오는 미검증이다.
기존 backend 코드를 그대로 사용한 것은 구현 재사용이며 위 최종 단계의 검사 재사용으로
계산하지 않는다. 라이브 AI·계정/권한 grant·유료 호출을 실행하지 않았다.

최종 기록: `/workspace/artifacts/v536-verification-managed/runs/e54759aadbc84c8cb5e1eefe59d9845a.json`

증거 ZIP SHA-256: `8a1ff8f3f38a2077c36894ea55365317c22d062e217fa240554517cab2a39ae5` (4227624 bytes).
최종 상태 `cleaned`와 owned RAM 작업공간 제거를 확인하고 압축 증거의 전체 manifest도 검증했다.

| 보관 역할 | 출처 commit | ZIP SHA-256 | bytes / files / dirs | 전체 manifest SHA-256 |
|---|---|---|---|---|
| latest | `6ad5b5d45dd88bea3a2fa177cd55ec486fde4a67` | `74c7d1a03f3bb6998d36eb420d77f2775137703a0bbded236a1d53829c542293` | 51778143 / 2403 / 150 | `438571943abcb3fdd3922f8e81ef80afd3f226a5af015718855dd679f8211514` |
| rollback | `1ee505504ff79c29daa099b19db00fcdd9273c72` | `749a721162ae62744e23bf1f30d2ff77e6f1656e70e425120d52e50e831a0474` | 51542481 / 2386 / 147 | `e4bbe7550860f5010a344489354d3cf0651ef62a8c7032c19346c4b08ca6bc74` |

보관 위치는 `/workspace/artifacts/v536-verification-managed/packages/`다. 새 팩의 원본 MIT
라이선스도 패키지 전체 manifest에서 확인했다. 최신/이전 정상본 승격과 이전 관리 세대의
정리는 기존 승인된 transaction만 사용했다. 과거 원본·별도 산출물·로그·프로필은 삭제하지 않았다.

최종 실행의 디스크 순증가 6.26MiB,
이번 checkpoint 전체 순증가 14.45MiB,
측정 시 여유 1508.61MiB다. 검사 단계 중 관측 최소 여유 1513.74MiB,
관측 peak 메모리 4557.14MiB. 이후 증가량을 보장하는 값은 아니다.

초기 어댑터 중복 선언과 선언 읽기 누락을 수정했다. 이후 숨겨진 선택 라벨 재클릭,
미등록 manifest 대신 기존 listing ID가 필요한 전환, CSP 문자열 평가 대기는 검사 fixture
문제로 분리해 수정했다. CSP·권한·소유 규칙은 완화하지 않았다. 최종 commit에서는 모든
단계를 새로 수행했고 아래 실패 기록은 최종 통과/재사용에 포함하지 않는다.

- `/workspace/artifacts/v536-verification-managed/runs/df35f887e8b347f7905fcb1e259ff3f0.json` (`f95cf275faad020aa9cc91fe5fafbb0fe4f11598c0a12d8d2626999f21f550b7`): 9 통과 / 1 실패.
- `/workspace/artifacts/v536-verification-managed/runs/720c7a245048458b86b85645ddf96e32.json` (`88a267180645af05cdc3ab340044d980d7fba4d7e046ba2794f9921c06046d96`): 22 통과 / 1 실패.
- `/workspace/artifacts/v536-verification-managed/runs/a9be41cce27749638d37268833a983fc.json` (`f51b2b6425b1fe3337f11a00ceb644629f84eeb6e6950e0acb94f97edc5f7742`): 9 통과 / 1 실패.
- `/workspace/artifacts/v536-verification-managed/runs/89294f432b7443c5ac38d21f8ac0ab5d.json` (`d928dfcf9e22177212926c94ec7198ed36cd3a47f6a8b7661ae5636bc1e8ee9f`): 9 통과 / 1 실패.
- `/workspace/artifacts/v536-verification-managed/runs/d9f501e53881408c9938e6b8f88ee074.json` (`f7287a37cf11db5859b5d8e293b6b1e032176eba6eb9ffb5c4e751bd77ea4e6b`): 9 통과 / 1 실패.
