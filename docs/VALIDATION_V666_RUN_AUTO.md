# V666 Run 창에 맞춤 검증

[지원/수명/호환 경계](V8_RUN_AUTO.md) · [원본 대조 및 제품 파일 delta](v666-run-auto-delta.json).
최종 코드·검사 동결 `ecf4b013ac41ec1a372dd10359ee3557a1dc76af` 이후는 문서만 변경했다.
최종 **39단계 통과: 신규 39 / 재사용 0**.
LF 16 · CRLF 16 · 패키지/전체 복원/실패 수명관리 7.
각 checkout은 독립 Git 객체·NuGet/SDK home·처음 빈 엔진 cache/출력을 사용했다.

- 원본 v666 ZIP의 실제 CSS client 크기 의미와 새 리소스 핀을 대조했다. 제품 변경은
  Run UI/controller/manifest 세 파일뿐이다. 프로젝트 C#·source/override 계약·native
  FrameControl/RunSurface/Audio·권한·Review/Confirm·최종 source CAS는 변경하지 않았다.
- 상태 검사는 명시적 activation 전 무요청, 정확한240–512 정수 범위, ACK 전 단일
  pending, ACK 후 최신 geometry, 동일 크기·숨김·범위 밖 억제, 모드 취소·publisher
  변경·실패 latch·폐기를 확인했다. source/heartbeat/Step으로 크기를 추정하지 않는다.
- 실제 원본 UI의 떠 있는 Run 창을 원래 drag/resize 조작으로 변경했다. 자동 mode는
  실제360×280 요청을 한 번 보내며 paused 픽셀64×36·실행 frame을 보존한다. 연속
  390×290/410×300 변경은 기존 ACK까지 기다리고 한 번의 실제 Step 뒤 최신410×300만
  요청했다. 다음 Step으로 해당 픽셀을 확인했고 같은 크기는 반복하지 않았다.
- current로 이탈하면 새 geometry 요청을 취소한다.650px 영역은 clamp/명령 없이 안내하고,
  440×310 영역으로 돌아오면 원래 실제 출력 계약으로 요청·적용했다. Stop/새 실행은
  옛 publisher의 자동 mode와 요청을 재생하지 않고 초기64×36을 보존했다.
- native가 접수한 자동 요청의 응답을 보류·유실 처리하면서 custom 크기와 이름을 새로
  작성했다. 읽기 재확인은 같은 receipt만 회수했고 늦은 입력을 보존했다. 실제 Step은
  원래360×280만 적용하며 자동 명령 재전송이 없다. pending에서 auto를 해제해도 접수한
  요청은 취소하지 않으며 예약 geometry만 중단한다.
- auto를 유지한 응답 유실도 별도로 확인했다. 상태 read와 기존 ACK 뒤에도 실패 latch가
  새 크기를 요청하지 않았고, 사용자가 명시적으로 다시 선택한 뒤에만 재개했다.
  닫기/폐기된 handler는 다른 창에 적용되지 않는다. cold의 layout/chat 복원과 빈 runtime
  상태를 확인했다. 미저장 폼 전체의 cold 보존을 주장하지 않는다.
- 기존 개인 preset의 실제 native CAS/replay/저장 실패·ProjectContext 격리, UI 등록/삭제·
  지연/닫기/cold·프로젝트 왕복, 직접 해상도 정상/거절/응답 유실·실제 ACK, PCM 오디오
  정상/수명과 native surface·WebUI 소유/관측/취소/폐기 회귀를 새로 실행했다.
- 새 Windows 교차 패키지의 전체 구조/리소스 SHA·누락/변조 거절·관리형 엔진 시작과
  실제 자동 맞춤 UI, 전체 ZIP SHA/CRC·파일/디렉터리 mode 복원·복원 엔진의 실패/늦은
  입력/재시작을 확인했다. 실패 증거 보존과 해당 실행 소유 임시물 정리도 검사했다.
  Linux 관리형 엔진/Chromium 자동화이며 실제 Windows 기기 실행이 아니다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/cc484a9fa3a8416fbd28429e03ef9d3b.json`.
증거 ZIP `/workspace/artifacts/v536-verification-managed/runs/cc484a9fa3a8416fbd28429e03ef9d3b.zip` · SHA256 `93e545ccd0bf5eacb5625c5e1cd55ec5a915833fe3183fae929f35812e458346` · 1798450bytes.
전체 evidence manifest/ZIP을 검증했고 owned RAM root가 제거됐음을 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `ecf4b013ac41ec1a372dd10359ee3557a1dc76af` | `73eaa48b91852c5134d9f490171b24a7140016ecc3d45e6609c38dcec3bf87f8` | 51845090 / 2467 / 152 | `4a58b3d6b695ff3f2f13c893ed17e3c5d1d8acb673bb04cda4e01f5e127c6df4` |
| rollback | `6e7a5c5eb9cfac70a1340f969b2e26366d8df490` | `9041961e74deab62a5b308b8a8b4e1c119d53886a7f179b0487bc7b3c18e3fc0` | 51844476 / 2466 / 152 | `d57a3b4c8b9eb6b4175dc07ae031493a1d9dcf5af23c320cfb2417c377687e62` |

기존 승인된 managed 최신/롤백 보관과 자체 임시물 수명관리만 사용했다. 과거 원본·로그·
SDK·프로필·사용자 자료를 추가 삭제하지 않았다. disk 추가144MiB(안전64MiB 포함),
RAM3GiB+512MiB·메모리7GiB+1GiB 기준을 유지했다. 최종 실행 순증가
2.56MiB, 단위 순증가 3.70MiB,
측정 시 여유 1401.84MiB. 표본 최소 여유 1404.34MiB,
peak 메모리 4766.43MiB. 이후 실행 증가량 보장값이 아니다.

집중 진단 `/workspace/artifacts/v536-verification-managed/runs/e34eb18cae414f53bccd0ffd428dd0e3.json` (SHA `8cf54877e17f5529c4bdebf433413dd3f41ccd43dab131d3709676c69f9c9d9c`)은 두 UI 흐름 통과 뒤 의도적으로
종료해 패키지 승격 없이 증거 보존·정리를 완료했다. 최종 수치에 재사용하지 않았다.

현재240–512 provider 범위의 명시적 자동 mode이다. 큰 출력/고정 대형 해상도·GPU/FPS,
진행 중 I/O의 비차단 runtime 제공 경계, 신원/권한·자산·참여자/대화의 기존 고정 잔여는
별도다. 실제 Windows WebView2·모바일·장치/DPI/IME·전체 UI·Space/Library 전달은 미검증이다.
실제 계정·외부 권한·자격증명·유료/라이브 AI는 사용하지 않았고 main은 보존했다.
