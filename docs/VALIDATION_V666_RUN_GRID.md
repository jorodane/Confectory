# V666 실제 영상 디버그 그리드 검증

[지원·수명·한계](V8_RUN_GRID.md) · [원본 대조/제품 delta](v666-run-grid-delta.json).
코드·검사 동결 `c5693833fc7b9aa1e6f1690430b0a69e77fcc6d9` 이후는 문서만 변경했다.
최종 **44단계 통과: 신규 44 / 재사용 0**.
LF 19 · CRLF 18 · 패키지/전체 복원/실패 수명관리 7.
독립 Git 객체·NuGet/SDK home·처음 빈 엔진 cache/출력을 사용했다.

- 원본 v666 CSS의10% 그리드 규칙을 그대로 대조하고, 기존 스타일이 추가 규칙 밖에서는
  바뀌지 않았음을 확인했다. 제품 변경은 Run UI/helper/CSS/manifest 네 파일뿐이다.
  native 출력/실행·사용자 C#·계약/override·권한/부모·외부 원본·저장/Review/Confirm·
  최종 CAS는 변경하지 않았다. 요소 경계나 FPS를 만들어내지 않는다.
- 기하 검사는 가로/세로/정사각 실제 픽셀의 contain 사각형, letterbox, 소수점 view,
  invalid/zero/hidden shape와 불변 결과를 확인했다. 실제 UI에서는 canvas 픽셀 크기와
  CSS 표시 영역으로 계산한 독립 영역과 overlay의 실제 DOM 사각형이 일치했다.
- native resizable 프로젝트의 paused64×36 출력에서 checkbox를 반복 조작했다.
  canvas data URL/실행 frame/명령 수는 그대로이며 그리드는 실제 영상에만10% 간격으로
  표시됐다. pointer-events:none/aria-hidden으로 영상·컨트롤 입력을 차단하지 않는다.
  실제 portrait320×480은 명시 Step 뒤에만 적용하고, pending 중에는 이전 영상 영역을
  유지한다. 최대화/복원·390px 브라우저 viewport에서도 실제 픽셀을 늘리거나 새 실행/
  크기 명령 없이 영역을 따라갔다. viewport 검사는 모바일 기기 검증이 아니다.
- 형제 Run 창은 별도 선택이다. 숨김에서 영상/overlay를 숨기고, 다시 선택하면 실제
  관측 뒤 복구했다. 닫힌 handler는 다른 창을 바꾸거나 오류를 만들지 않는다. 실제 닫기는
  overlay/observer를 폐기한다. private presentation에 runGridEnabled를 저장하지 않고,
  cold는 원래 chat/layout과 빈 runtime만 복원하며 선택/프로세스/lease를 재생하지 않았다.
- 실제 native 영상 응답의 SHA를 검사 fixture에서 변조했다. browser는 영상과 그리드를
  함께 숨기고 checkbox 선택/늦은 width/name/chat을 보존했다. 정상 기존 관측을 다시
  허용하면 같은 owner의 실제 영상/그리드를 복구하며 추가 실행/크기 명령은 없었다.
  접기/펼치기와 native close의 lease 거절·명시 retry·실제 닫기도 확인했다. 변조 응답과
  거절 입력 주입은 fixture이며 native 실패 자체를 새로 구현했다고 주장하지 않는다.
- 실제 영상이 없는 idle 및 frame-only 프로젝트에서는 grid/bounds가 비활성이다.
  disabled DOM을 강제로 바꾸고 handler를 호출해도 원래 비활성 상태로 돌아가며 영상/
  실행 권한이 생기지 않았다. bounds는 계속 미지원이다.
- 기존640 출력/개인 등록·capability 교체/면적 거절/실패·유실·cold, 자동 맞춤,
  개인 preset CAS/프로젝트 격리·직접 해상도·PCM 오디오·native surface/WebUI 소유/
  관측/취소/폐기 회귀를 새로 실행했다. legacy publisher UI는 기존 응답 주입 검사이며
  실제 native provider/물리 기기 실행과 구분한다.
- 새 Windows 교차 패키지의 구조/전체 SHA/누락·변조 거절/관리형 엔진 시작과 grid UI,
  전체 ZIP SHA/CRC·파일/디렉터리 mode 복원·복원 엔진의 실패/입력/닫기 복구를 확인했다.
  실패 증거 보존과 해당 실행 소유 임시물 정리도 검사했다. Linux 관리형 엔진/Chromium
  자동화이며 실제 Windows apphost/WebView2 실행이 아니다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/88fd412ef44845509fb38a43fc72d08e.json`.
증거 ZIP SHA256 `04feabc42bcf347930b7adf433af02ce79f3aeccab524fbd850c491328ef195b` · 2109641bytes.
전체 evidence manifest/ZIP과 owned RAM root 제거를 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `c5693833fc7b9aa1e6f1690430b0a69e77fcc6d9` | `d65490af69d9798231819acc9078a6071f7ad7dd8d9113e4b6443edf643608de` | 51846978 / 2468 / 152 | `dd41d0c693782051e20f6d0cb3493cdfc6897b8bf11a36445b8f32ba2eb49f3c` |
| rollback | `2ab45f985689eb2d764793ab4d3851dabace185b` | `a6e191903493e38526c04766293ca07fe902366c6f43eccc19fe07b57a406a92` | 51845294 / 2467 / 152 | `27e9135e10688b90b1bc4a28e37ab46373576354ce1d171c907f5c2c320cd69c` |

기존 승인된 managed 최신/롤백 두 세대와 자체 임시물 수명관리만 사용했다. 기존 자료·
SDK·과거 원본·로그·프로필·사용자 데이터를 추가 삭제하지 않았다. disk 사전 예산160MiB
(안전64MiB 포함), RAM3GiB+512MiB·메모리7GiB+1GiB 기준을 유지했다. 최종 실행 순증가
2.87MiB, 단위 순증가 7.02MiB,
측정 시 여유 1383.78MiB. 표본 최소 여유 1386.60MiB,
peak 메모리 4708.63MiB. 이후 실행 증가량의 보장값이 아니다.

집중 진단 `/workspace/artifacts/v536-verification-managed/runs/e5aaa32a724949ef8aed01e479e22bea.json` (SHA `d2c3d59f1b5e9d123bca1e6a2cd5bff6fba5e3b997286b9a98fe6b6656403e1d`)은 모든 시도/입력/실패를 보존하고,
정상·수명·미지원 흐름 통과 뒤 의도적으로 종료해 정리했으며 패키지를 승격하지 않았다.
최종 수치에 재사용/합산하지 않았다. source paint가 disposed 객체를 다시 참조하는 실제
오류를 수정했다. CSS 두 배경 레이어의 계산값 문자열과 닫기 후 숨은 형제 창을 누르던
순서는 fixture 문제로 구분해 수정했다. 순수 기하 검사의 비트 단위 소수점 비교는
1e-12 허용 오차로 바꾸고 정확한 사각형 예제는 엄격 비교를 유지했다. 기존 자동 맞춤
회귀는640축 범위의 연속 드래그 중 유효한571×323이 먼저 접수되고 최종440×310이 ACK
뒤 대기한 로그로 원인을 구분했다. 기존 pending/연속 drag 결합 검사는 유지하고 별도
범위 복귀 검사의 geometry 전환만 단일 pointer move로 명시했다. 자동 맞춤 제품 코드와
단일 pending/실제 ACK 보호는 변경하지 않았다.

- `/workspace/artifacts/v536-verification-managed/runs/9df1b45e107f4b2e9d0752757d15096b.json` · SHA `534565175a6fee1493f4402e3f821dcb98f0f91b401312f0876aea7e838644a9` · 통과 14 / 실패 1

진행 중 I/O에는 현재 동기 잠금과 분리한 실제 관측 경계가 선행한다. HD 이상 출력은
기존1MiB 전송/메모리·수명 구조의 후속이며, 요소 경계·GPU/FPS·신원/권한·자산·참여자/
대화의 기존 고정 잔여를 이 표시에 합치지 않았다. 실제 Windows·모바일 기기/DPI/IME·
전체 UI·Space/Library 전달은 미검증이다. 실제 계정·외부 권한·자격증명·유료/라이브 AI는
사용하지 않았으며 main은 보존했다.
