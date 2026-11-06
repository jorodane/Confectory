# V666 Run PCM 오디오 검증

최종 코드·검사 동결 `5ffbbc28134c749c7d04b6bd83358c2eaf5d1590` 이후 마감은 문서만 변경했다.
[실제 지원 경계](V8_RUN_AUDIO.md) · [제품 전체 변경/해시](v666-run-audio-delta.json).
최종 **41단계: 신규 19 / 재사용 22** 통과.
LF 17 · CRLF 17 · 패키지/전체 복원/IPC·실패 수명관리 7.
독립 Git 객체·빈 엔진 출력/캐시·독립 NuGet/SDK home을 사용했다.
제품과 해당 검사·SDK/NuGet 입력이 동일한 직전41a2d4f8의 LF/CRLF22단계만 재사용했다.
최종 변경은 package probe의 raw-string 줄바꿈 가정 한 줄과 제한된 증거 재사용 helper다.
전체 source diff·정확한 parser 수정·봉인 ZIP/manifest·개별 통과 결과·EOL/독립 checkout·
호출 인수를 대조했고 SDK 또는 제품을 변경한 실제 입력의 거절도 확인했다.
원래 windows-probe 실패는 재사용하지 않았다. 새 clone/restore/build/engine·패키지·전체
복원·실패 수명관리는 신규다. 최종 증거의 `audio-reuse.json`에22개 원본을 기록했다.
재사용 원본 기록 `/workspace/artifacts/v536-verification-managed/runs/1e3f430d3d3b44128828b3c9577d4da3.json`,
ZIP SHA256 `3057dc0789ddb9cc3e37458090bf45c257ca6d3d9e2febd2fdd6c9346f024a2e`를 확인했다.


- 원본 v666 ZIP·제품 허용 목록·리소스 전체 SHA/크기와 기존 C#/Frame Begin/Complete·
  Surface/Resize·소유권·권한·Review/Confirm·최종 source CAS의 변경 없음 확인.
- native7개 검사: PCM 단일 owner/샘플 정렬·크기/canonical base64/실패 시 sequence 미변경/
  creator-thread 종료·새 publisher, 기존 surface 최대 크기/단일 owner·size opt-in,
  WebUI scope/취소/폐기·미보관 읽기, 실제 FrameControl 경계/반복/스레드/닫기와
  Pause/Step/reconnect/Stop 회귀.
- 실제 등록 프로젝트·인증 pipe·소유 view/lease/handle을 통해 전체 PCM SHA와440Hz
  생성 샘플 위상/범위를 비교했다. 처음/Off의 baseline은 옛 PCM을 반환하지 않고,
  오디오만 읽으면 metadata heartbeat가 갱신되지 않아 실제 실행은 안전하게 pause한다.
  한 번의 명시적 Step은 새 PCM 하나만 내보내며 같은 cursor 반복은 중복되지 않는다.
  보관64청크/32000샘플 초과 시 명시적 gap/reset으로 유실 구간을 만들지 않는다.
- 변조된 SHA/rate/순서/offset/count/필수 필드/reset/GUID/퇴행/noncanonical base64 및
  retired publisher를 실제 native reader에서 거절하고 유효 receipt를 회수했다.
  외부 view/lease/handle과 일반 mutation 경로의 audio operation도 거절한다.
- JS canonical 샘플/Int64 cursor/전체 SHA·범위·순서·reset과 최대12000개(0.75초 분량)의 PCM 대기량을
  검사했다. graph 생성 중 예외로 이미 할당된 context가 남는 결함을 재현해 정리했고,
  해당 failure injection 회귀를 포함했다. 각각 한도 안인 두 묶음이 총 대기량을 넘기는 결함도
  재현해 기존 대기량과 새 묶음을 합산하도록 수정했다. 새 청크 없는 반복 읽기는 예약을
  취소하거나 다시 만들지 않는다는 회귀를 포함했다. 순수 scheduling 단위는 모의 context이며,
  아래 Chromium 실제 graph와 구별한다.
- Chromium의 실제 AudioContext/AudioBuffer/BufferSource를 사용했다. default Off에서는
  context가 없고, 명시적 사용자 클릭 뒤 running 상태와 복사된 PCM 전체 SHA가 native
  관측과 일치한다. `테스트`는 별도 로컬 oscillator로만 계수하며 프로젝트 PCM 증거로
  쓰지 않는다. 주입한 시작 거절은 실제 할당 context를 닫고 명시적 재시도를 요구한다.
- Off 뒤 새 scheduling이 없고 실제 프로젝트는 실행을 유지한다. 손상된 관측 형식은
  graph를 닫고 다시 켜기로 복구한다. pause 중 반복은 중복 재생하지 않고 실제 Step만
  새 PCM을 만든다. 숨겨진 창·다른 Run·Stop/새 handle은 이전 graph를 재생하지 않는다.
- 실제 접수 audio 응답을 보류한 뒤 Off/닫기를 실행하고 늦게 해제해도 옛 PCM이 예약되지
  않는다. 거절된 닫기는 실제 프로세스와 새 입력을 남기며 소리는 Off로 정리한다.
  retired handler·등록 프로젝트 전환에서 옛 owner가 다른 실행을 제어하지 못한다.
  cold는 layout/chat 입력을 보존하고 handle/cursor/context/프로세스는 재생하지 않는다.
- 기존 직접 해상도 정상/응답 유실/취소·충돌/늦은 입력·닫기/프로젝트·cold, 기존 software
  frame의 변조 거절, Run 개발 메뉴의 정상/실패/재시작 흐름도 동일 제품의 봉인된 검사로 확인했다.
- 새 Windows 교차 패키지 관리형 엔진의 실제 PCM/graph UI와 전체 ZIP SHA/CRC/파일·
  디렉터리 mode 복원본의 응답 보류/닫기 거절/retired callback/프로젝트·cold 흐름,
  실패 증거 보존과 owned 임시물의 수명 정리를 검증했다. 실제 Windows 실행은 아니다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/7c50b2a5b1204eb1b09a9ad7622264f1.json`.
증거 ZIP SHA256 `f2068712cb6706084c109f4b67ed66491a1472a5516398301b282906e81fd713` (994522 bytes).
전체 manifest/SHA/CRC와 owned RAM 작업공간 제거를 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `5ffbbc28134c749c7d04b6bd83358c2eaf5d1590` | `ac271aca12a734698b32ae7fa0e648be7ab9027afafc6dc2e679ba9b6d8300fa` | 51833945 / 2462 / 152 | `67563d2cd32adac276d313e5e87daf053a14e7a549f40a967da767b0a86fba61` |
| rollback | `5d162eb3c6672ad0337b3a7b1b88635ee902dda5` | `09ffab00aa9f1aab5dffbf235f00bda78179371b972cac8a2e1790214fcca214` | 51815288 / 2441 / 151 | `c0a58ed82974aa8ae3db1027922de889db53af572b6ee1cdc3d6561ec609c8bc` |

기존 승인된 원자 승격으로 최신/정상 롤백을
`/workspace/artifacts/v536-verification-managed/packages/`에 보관했다. 과거 원본·로그·
프로필·SDK·캐시·사용자 데이터는 추가 삭제하지 않았다. 추가 disk144MiB(안전64MiB 포함),
RAM3GiB+512MiB·메모리7GiB+1GiB 기준을 유지했다. 최종 실행 순증가 1.70MiB,
단위 전체 순증가 14.88MiB, 측정 시 여유 1416.96MiB.
명령 실행 중 표본 최소 여유 1418.63MiB, peak 메모리 4652.75MiB.
이후 증가량의 보장값은 아니다.

최종에 합산/재사용하지 않은 단일 진단 `/workspace/artifacts/v536-verification-managed/runs/cb09b701eac245b8aedf5ebef67b3b76.json`
(SHA `1b42f6a493cacdd82d0ea8cc679cd70694be40f5b81fdde807fc4869b188dce7`)도 전체 보존·정리를 확인했다. 소수점 완전 일치 비교·페이지 생성 API·
자연 종료된 buffer의 stop 횟수 가정은 fixture 결함으로 분리해 바로잡았다. 실제 graph
구성 예외의 context 잔류는 제품 결함으로 수정했다. 거절된 시작이 즉시 Off로 돌아가는 동작을 check()가 On 유지를 요구해 실패한 fixture도
click() 뒤 Off 검증으로 수정했다. 그 후 완료된 LF/CRLF 실행은 총 queue 한도 결함을
재현한 시점의 패키지 빌드를 안전 중단하고 증거/임시물 정리를 마감했다. 해당 두 기록도
최종에 합산하지 않는다. 모든 초기 실패와 수정/재검사 증거는
보존했다. 그 뒤 유효한 inline raw JSON의 줄바꿈을 가정한 package probe 실패를
재현해 JSON 내용과 무결성 검사를 유지한 parser로 수정했다. 제품/22개 검사는 동일함을
봉인된 증거와 대조해 재사용했고, 실패한 probe와 최종 패키지/복원은 신규 수행했다.

지원은 opt-in 모노 PCM16/16kHz 소프트웨어 미리듣기다. 새 RunAudio import에는 최신의
짝맞춘 provider가 필요하며 과거 rollback의 새 API 지원은 보장하지 않는다. 기존 C#을
자동 변경하지 않는다. 다채널/다른 rate·native sink/장치 선택·실시간 품질/출력 지연,
자동/preset 해상도·큰 surface·GPU/FPS·진행 중 IO 및 고정 신원/권한·자산·참여자/대화는
별도다. 실제 Windows apphost/WebView2·모바일·물리 오디오/DPI/IME·전체 UI·Space/Library
전달은 미검증이다. 라이브 AI/자격증명·실제 계정/접근권한 변경·유료 호출은 사용하지 않았고
main을 보존한다.
