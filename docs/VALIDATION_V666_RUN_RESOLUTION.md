# V666 Run 직접 해상도 적용 검증

최종 코드/검사 동결 `5d162eb3c6672ad0337b3a7b1b88635ee902dda5` 뒤 마감은 문서만 변경했다.
[지원 경계](V8_RUN_RESOLUTION.md) · [제품 전체 변경/해시](v666-run-resolution-delta.json).
최종 **54단계: 신규 54 / 재사용 0** 통과.
LF 22 · CRLF 22 · 패키지/전체 복원/IPC·실패 수명관리 10.
독립 Git 객체·빈 엔진 출력/캐시·독립 NuGet/SDK home을 사용했다.

- 원본 v666 ZIP/제품 허용 목록/리소스 전체 SHA·크기 및 기존 C#/frame Begin·Complete·
  소유권/권한·Review→Confirm/최종 source CAS 경계 보존 검사.
- 네이티브6개 검사: size opt-in 전/후·creator thread·복사된 RequestedSize·중복/늦은
  Configure 거절·닫기, 기존 최대 픽셀·단일 owner, WebUI scope/취소/폐기·미보관 읽기,
  기존 actual frame boundary/order/repeat/thread/close와 Pause/Step/reconnect/Stop 회귀.
- 실제 인증 채널에서 기존 heartbeat 분리/변조/최대1MiB 프레임 전송 검증을 새로 수행했다.
- 실제 native reader에서 size sequence 초과·미래 ACK·실제 픽셀과 다른 크기·필수 필드 누락·
  sequence/ACK 퇴행·잘못된 publisher 길이를 거절하고 올바른 pending/applied 관측을 회수했다.
  검증 실패는 원래 올바른 cache나 실행 제어를 변경하지 않는다.
- JS size proof의 초기/pending/applied·범위/식별자/순서/실제 픽셀 검증, 기존 전체 픽셀 SHA/
  최대 프레임·클라이언트 abort/폐기·늦은 응답 격리도 새로 검사했다.
- Linux 관리형 엔진/Chromium에서 원본 직접 입력 폼의 320×240·최대512×512 실제 canvas
  적용을 확인했다. paused 상태의 요청은 size receipt만 pending이고 frame/ACK/일시정지는
  그대로다. 실제 한 Step 뒤 새 픽셀과 size ACK를 확인하며 자동 Resume/Step은 없다.
  잘못된 publisher·오래된 size CAS·범위 밖 native 입력 및 HTML 범위를 거절했다.
- 미적용 폼 값은 메뉴/형제 창 왕복에 보존하고 다른 Run에는 적용하지 않는다. Stop/재실행은
  새 publisher/초기 크기로 시작하며 오래된 명령을 재생하지 않는다.
- 실제 접수 응답 유실 동안 추가한 다른 크기를 보존했다. 명시 read 재확인은 같은 pending
  receipt를 회수하며 명령을 재전송하지 않는다. 이후 Step은 원래 요청만 적용한다.
  거절된 닫기에서 실행/폼/새 입력을 유지하고 실제 닫기는 pending 요청을 실행하지 않고
  종료한다. 폐기된 폼 callback·다른 등록 ProjectContext는 옛 view/publisher를 제어하지 못한다.
  프로젝트 왕복/cold는 layout/chat 입력을 보존하고 runtime 크기·명령·실행은 복원하지 않는다.
- 기존 readonly software-output, Run 개발 메뉴 정상/응답 유실/닫기/재시작과 전체화면
  정상/race 회귀를 최종 코드로 새로 실행했다.
- 새 Windows 교차 패키지 출처·구조와 그 관리형 엔진의 직접 해상도/기존 영상, 전체 ZIP
  SHA/CRC/파일·디렉터리 mode 복원과 복원 엔진의 실패/늦은 입력/프로젝트·cold 흐름,
  기존 개발 메뉴와 실패 시 증거 보존·owned 임시물 수명 정리를 검증했다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/50c0a42e785b448990c79321b72ca567.json`.
증거 ZIP SHA256 `d8024b09d98cf8edc04967505ff02b99d87287f074525810f9bb442436ee57bd` (3656878 bytes).
전체 manifest/SHA/CRC와 owned RAM 작업공간 제거를 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `5d162eb3c6672ad0337b3a7b1b88635ee902dda5` | `09ffab00aa9f1aab5dffbf235f00bda78179371b972cac8a2e1790214fcca214` | 51815288 / 2441 / 151 | `c0a58ed82974aa8ae3db1027922de889db53af572b6ee1cdc3d6561ec609c8bc` |
| rollback | `edf0c239726cb7a4bb81774c6fd8cdc61d324909` | `e330ef49d86b52f2adf7ce5f412b98c425cf1842d072dbe37b880b61eff8f6d1` | 51803378 / 2426 / 151 | `0511ee4c85bc3b34c270da2c816431392f75ec4fc6a5d1c7999ab78f5a7e9486` |

기존 승인된 원자 승격으로 최신/정상 롤백을
`/workspace/artifacts/v536-verification-managed/packages/`에 보관했다. 과거 원본·로그·
프로필·SDK·캐시·사용자 데이터는 추가 삭제하지 않았다. 추가 disk144MiB(안전64MiB 포함),
RAM3GiB+512MiB, 메모리7GiB+1GiB 기준을 유지했다. 최종 실행 순증가 4.44MiB,
단위 전체 순증가 10.46MiB, 측정 시 여유 1431.93MiB.
명령 실행 중 표본 최소 여유 1436.29MiB, peak 메모리 4670.35MiB. 이후 보장값이 아니다.

최종에 재사용/합산하지 않은 단일 진단 기록 `/workspace/artifacts/v536-verification-managed/runs/896f94436e7a4f4b9512a032d24eb223.json`
(SHA `4ab68def1696175d1b8f8f600b3af9c7a29509f95cfc227235f9323d931d9e6f`)도 전체 검증/정리를 확인했다. 최초 fixture가 mutation의 과거 완료
행을 반복 읽어 pause ACK를 잘못 비교해 request ID별 중복 집계를 제거했다. 이후 출력이
없는 형제/숨김 창에서 실제 null 참조 결함을 발견해 고쳤다. 프로젝트 전환 fixture는 지원
목록 ID로 등록·선택하고 UI presentation을 flush한 뒤 직접 API로 이탈하도록 바로잡았다.
필수 size command 식별자 누락·GUID의 정확한 길이도 검토해 거절을 강화했다. 초기 시도와
수정·재검사 증거를 모두 보존했고 최종 코드에서 전체 단계를 새로 실행했다.

새 ConfigureSize/RequestedSize 및 출력 명령 역할은 최신의 짝맞춘 provider가 필요하다.
이전 롤백본은 기존 프로젝트용이며 새 API를 import한 프로젝트를 컴파일하지 못할 수 있다.
기존 C#을 자동 변경하거나 새 API를 구버전에서 지원한다고 가정하지 않는다.

지원은 opt-in한 소프트웨어 출력의240–512 직접 입력이다. 자동 창 해상도·preset 저장/삭제·
큰 surface·GPU/native Window 캡처·render FPS·오디오와 진행 중 IO 등 고정 잔여는 미완료다.
실제 Windows apphost/WebView2·모바일·GPU/오디오 하드웨어·DPI/IME·전체 UI·Space/Library 전달은
미검증이다. 라이브 AI/자격증명·실제 계정/접근권한 변경·유료 호출을 사용하지 않았고 main은 보존한다.
