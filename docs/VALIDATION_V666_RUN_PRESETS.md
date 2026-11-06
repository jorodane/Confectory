# V666 프로젝트별 개인 해상도 등록 검증

코드·검사 동결 `6e7a5c5eb9cfac70a1340f969b2e26366d8df490` 이후 마감은 문서만 변경했다.
[실제 지원](V8_RUN_PRESETS.md) · [전체 제품 delta/해시](v666-run-presets-delta.json).
최종 **37단계 통과: 신규 37 / 재사용 0**.
LF 15 · CRLF 15 · 패키지/전체 복원/IPC·실패 수명관리 7.
독립 Git 객체·초기 빈 엔진 cache/출력·독립 NuGet/SDK home을 사용했다.

- 원본 v666 ZIP/리소스 핀과 제품 허용 목록, 기존 source/override·권한·Review/Confirm·
  FrameControl/RunSurface/Audio의 기존 구현·크기 요청 계약과 CAS 보호를 보존했다.
- 실제 활성 ProjectContext의 native API에서 저장 파일 전체 SHA/revision CAS·안정적 ID,
  정규화된 마지막 명령의 정확한 재확인·다른 입력/기준 충돌을 검사했다. receipt가
  가리키는 실제 대상 크기를 바꾼 경우 과거 성공을 회수하지 못한다.
- 같은 이름·크기는 기존 ID/파일 바이트를 유지한다. 다른 크기·잘못된 ID/범위/필드·외부
  경로 요청을 거절한다. 실제 파일을 읽은 뒤 바꾸면 old revision의 쓰기는 거절된다.
- 실제 readonly 파일 쓰기 실패에서 원본 전체 바이트를 보존하고 권한을 복구한 **자체
  fixture**의 같은 입력/명령으로 한 번 저장했다. 손상 JSON·다른 프로젝트 자료·symlink는
  unavailable이며 새 빈 목록으로 덮어쓰지 않는다. 32개 한도·삭제 재확인·cold/다른
  실제 프로젝트/홈 경계를 검사했다. 사용자 파일이나 실제 접근권한을 변경하지 않았다.
- 원본 팝오버에서 Unicode/기호 이름 등록·선택·삭제를 실제 backend에 연결했다. 등록
  확인 뒤 별도 크기 요청이 발생하고, paused 출력64×36은 자동 진행하지 않는다.
  실제 한 Step으로320×240 등 새 픽셀과 size ACK를 확인한다. 이름 충돌 입력을 보존하고,
  같은 이름·크기는 추가 등록 없이 선택한다. HTML로 해석되는 이름 노드는 만들지 않는다.
- 형제 Run 창은 같은 개인 목록을 읽고 자신의 lease에만 요청한다. 삭제는 이미 적용되거나
  pending인 출력을 유지한다. 숨겨진 형제 창에서도 선택 치수를 보존하고 기존 Step이
  이전 요청을 그대로 완료한다. cold는 확정 목록/chat/layout만 복원하며 process/옛 크기
  명령은 재생하지 않는다. 미저장 폼의 cold 보존을 주장하지 않는다.
- 실제 접수한 등록 응답을 보류·유실 처리하는 동안 새 이름/치수를 작성했다. 명시적인
  같은 명령 재확인은 파일/ID를 중복 생성하지 않고, 늦은 입력이나 옛 크기를 적용하지
  않는다. 삭제 응답 유실도 receipt만 회수하며 이전 pending 출력과 새 입력을 유지한다.
  닫기 중 접수한 저장/retired handler는 다른 창을 수정하거나 크기를 요청하지 못한다.
  실제 등록 ProjectContext 왕복에서 목록과 입력의 격리·원본 보존을 확인했다.
- 기존 직접 해상도 정상/실패·늦은 입력·응답 유실·닫기/cold, 실제 PCM 오디오/graph의
  정상/수명과 native surface·WebUI 관측/취소/소유·폐기 회귀를 신규 검사했다.
- 새 Windows 교차 패키지의 전체 리소스 SHA/누락·변조 거절/관리형 엔진 시작과 등록 UI,
  전체 ZIP SHA/CRC/파일·디렉터리 mode 복원과 복원 엔진의 실패/늦은 응답/닫기/프로젝트·
  cold 흐름, 실패 증거 보존과 owned 임시물 정리를 검증했다. 실제 Windows 실행은 아니다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/edf3de62e1d146b8aec418b8d89afc95.json`.
증거 ZIP SHA256 `ac641fb1463c1d0b9b8b59669d7a3a8e1396fb41dc64585d90335d5dd540c1a8` (1701698bytes).
전체 manifest/SHA/CRC와 owned RAM root 제거를 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `6e7a5c5eb9cfac70a1340f969b2e26366d8df490` | `9041961e74deab62a5b308b8a8b4e1c119d53886a7f179b0487bc7b3c18e3fc0` | 51844476 / 2466 / 152 | `d57a3b4c8b9eb6b4175dc07ae031493a1d9dcf5af23c320cfb2417c377687e62` |
| rollback | `5ffbbc28134c749c7d04b6bd83358c2eaf5d1590` | `ac271aca12a734698b32ae7fa0e648be7ab9027afafc6dc2e679ba9b6d8300fa` | 51833945 / 2462 / 152 | `67563d2cd32adac276d313e5e87daf053a14e7a549f40a967da767b0a86fba61` |

승인된 managed 두 세대 승격으로 최신/정상 롤백을 지속 보관한다. 그 밖의 과거 원본·SDK·
프로필·로그·사용자 데이터는 정리하지 않았다. disk 추가144MiB(안전64MiB 포함), RAM3GiB+
512MiB·메모리7GiB+1GiB 기준을 유지했다. 최종 실행 순증가 2.45MiB,
단위 순증가 10.13MiB, 측정 시 여유 1406.73MiB.
명령 중 표본 최소 여유 1409.14MiB, peak 메모리 4663.64MiB.
이는 이후 실행의 증가량 보장값이 아니다.

마감에 재사용/합산하지 않은 진단 `/workspace/artifacts/v536-verification-managed/runs/687e39bcf2fb4f998f06f38bab21d054.json`
(SHA `175d3a8fa69cd02e642254629b4df8151eab4d3eb0c4e42227dcd44bcb10bf89`)와 최초 컴파일 실패 `/workspace/artifacts/v536-verification-managed/runs/64055e4acc4c4a1f88a38929793df06e.json`
(SHA `09a90ec0c032b5cfa1fa097fc3f8993a698155be2a260a1d024c3d1fc52dd063`)도 검증·보존·정리를 마감했다. 초기 지역 변수 충돌과 모듈의
canonical LF 선언 누락을 수정했고, 실제 숨김 창의 치수 초기화 결함을 재현·수정했다.
preset 선택 시 실제 출력 대기 안내가 숨겨지는 결함도 수정하고 가시성을 검사했다.
숨겨진 첫 팝오버를 참조한 selector, 새 native open 이전의 옛 로그 읽기, 표시 선택을
요청 접수와 혼동한 대기 및 cold 초기화 완료 전 전역 함수를 호출한 오류는 fixture 문제로
구분했다. 앞선 최종 시도의 실패 기록도 별도로 보존하고 신규 통과 수에 합산하지 않았다.

- `/workspace/artifacts/v536-verification-managed/runs/4862f39d634441b3ad65f6f63fe285a5.json` · SHA `55337c6b8ffd024eae6aa80afeefebefd1c2641fccc00f4c9ca7ef08069469fd` · 통과 27/실패 1

모든 시도/입력/실패/수정 근거는
보존하며 최종 코드에서 관련 전체 단계를 새로 실행했다.

현재 provider의240–512 개인 등록 지원이다. 자동 창 크기/고정 대형 해상도·8192px·GPU/FPS·
진행 중 I/O와 기존 신원/권한·자산·참여자/대화 잔여는 별도다. source/C# bytes·공개
입출력/override 계약·권한·Review/Confirm을 바꾸지 않았다. 실제 Windows WebView2·모바일·
장치/DPI/IME·전체 UI·Space/Library 전달은 미검증이며 실제 계정/권한·유료 호출·라이브 AI를
사용하지 않았다. main은 보존한다.
