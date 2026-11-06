# V666 Run 실제 소프트웨어 출력 검증

최종 코드/검사 동결 `edf0c239726cb7a4bb81774c6fd8cdc61d324909`. 이후 마감은 문서만 변경했다.
[지원 경계](V8_RUN_SOFTWARE_OUTPUT.md) · [제품 전체 변경/해시](v666-run-surface-delta.json).
최종 **44단계: 신규 44 / 재사용 0** 통과.
LF 18 · CRLF 18 · 패키지/전체 복원/IPC·실패 수명관리 8.
각 checkout은 독립 Git 객체·빈 엔진 출력/캐시·독립 NuGet와 SDK home을 사용했다.

- 별도 출력 팩의 단일 소유자/크기/정확한 입력/완전한 원자 제출/실패 revision 보존/닫기.
- 실제 생성 프로젝트의 FrameControl 기존 인증 채널과 native reader, 미보관 WebUI 읽기를
  통과한 최대 512×512/1MiB RGBA 전체 SHA 검증. 모의 scene/stdout를 영상으로 쓰지 않는다.
- native에서 잘못된 SHA/픽셀 길이/크기/null/누락/과거 revision/retired publisher/관측하지
  않은 unchanged를 거절한 뒤 유효 출력·기존 제어를 회수했다. 다른 lease/handle/view는 거절한다.
- 영상만 반복 읽으면 실행 heartbeat를 연장하지 않아 실제 루프가 안전하게 정지한다.
  기존 actual frame boundary/thread/repeat/close와 owned Pause/Step/reconnect/Stop 회귀도 통과했다.
- WebUI readonly 관측 64회/큰 결과는 completed request 행을 만들지 않는다. 고정 whitelist와
  scope 전후 검증, mutation 경계 거절, busy 중 mount, dispose/Close 취소와 자원 수명을 검증했다.
- 디코더 전체 SHA/크기/형식/순서·최대 프레임과 클라이언트 abort/폐기·늦은 응답 격리.
- Linux 관리형 엔진/Chromium에서 실제 64×36 canvas의 양쪽 모서리 픽셀, Pause/한 Step의
  실제 출력, readonly 해상도·미지원 FPS/audio, 반복 unchanged 읽기/재전송 행 없음,
  sibling/전체화면/Stop/새 epoch, 변조 응답 복구·held reply 중 닫기·다른 창 격리,
  새 입력 보존·cold에서 layout/input만 복원하고 픽셀/lease/자동 실행 없음.
- 기존 개발 메뉴의 실제 read 응답 유실·명시 재확인·거절된 닫기·cold·입력 보존,
  전체화면 정상/지연/race 회귀. 기존 invoke/Review→Confirm·최종 CAS·권한을 우회하지 않는다.
- 새 Windows 교차 패키지 출처/구조와 그 관리형 엔진의 실제 영상 표시, 전체 ZIP SHA/CRC/
  파일·디렉터리 mode 복원, 복원 엔진의 변조/늦은 응답/닫기/cold 및 개발 메뉴 실패 복구.
  실패 증거를 먼저 보존하고 해당 실행이 만든 임시물만 정리했다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/b8340a659c264a70b03a759a51559fff.json`.
증거 ZIP SHA256 `afb69eef144901bbcb1207ed8749d852cdba94d7c302ea0fd1407e4ac2aa1c40` (3081400 bytes).
전체 manifest/SHA/CRC·owned RAM 작업공간 제거를 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `edf0c239726cb7a4bb81774c6fd8cdc61d324909` | `e330ef49d86b52f2adf7ce5f412b98c425cf1842d072dbe37b880b61eff8f6d1` | 51803378 / 2426 / 151 | `0511ee4c85bc3b34c270da2c816431392f75ec4fc6a5d1c7999ab78f5a7e9486` |
| rollback | `81b6dbcfb8d28b3049010e0ec0725de3da5a6c48` | `63cc42c80e4aa7d9bbeb1e67310858a3dca8952862571515432ebfcfde910fa9` | 51785245 / 2405 / 150 | `aa2f3297d249b2e19c26bb781f81dc9e3eadc6436108bc058d7f87f66d1bf8be` |

최신/정상 롤백은 `/workspace/artifacts/v536-verification-managed/packages/`에 기존 승인된
원자 승격 절차로 보관했다. 과거 원본·패키지·로그·프로필·캐시·사용자 자료는 추가 삭제하지
않았다. 추가 disk144MiB(안전64MiB 포함), RAM3GiB+512MiB, 메모리7GiB+1GiB 기준을 유지했다.
최종 실행 순증가 3.81MiB, 단위 전체 순증가 8.85MiB,
측정 시 여유 1442.48MiB. 검사 중 최소 여유 1446.22MiB,
peak 메모리 4636.00MiB. 이후 실행의 보장값이 아니다.

최종에 재사용/합산하지 않은 단일 진단 기록 `/workspace/artifacts/v536-verification-managed/runs/297fa09fd9ec43429146ef539108aeb1.json`도 SHA/CRC와 수명 종료를 확인했다.
증거 SHA `19575478fd8774ad52a684b7436805dee0a23c15e600da808f984bd5b1c9911f`. 최초 fixture의 manifest Sync 누락, 예제 Linux target 누락,
저장 JSON 검사에서 원문의 pixels 변수명 오인과 그 fixture 들여쓰기를 수정했다.
native 변조 검사에서는 InvalidDataException 누락을 실제로 발견해 Surface reader의
거절 처리에 포함했다. 초기 시도·수정·재검사 모두 보존했고 최종 동결 코드에서 전부 새로 검증했다.

실제 Windows apphost/WebView2·모바일·GPU/오디오 하드웨어·DPI/IME·전체 UI·Space/Library 전달은
미검증이다. 선택적 소프트웨어 영상 이외 native Window 캡처·렌더 FPS·해상도 변경/preset·오디오,
V3 진행 중 IO·V4/V5 신원/권한·V6/V7 자산·V9 참여자/대화는 기존 고정 잔여다.
라이브 AI/자격증명·계정/접근권한 변경·유료 호출을 사용하지 않았다. main은 변경하지 않는다.
