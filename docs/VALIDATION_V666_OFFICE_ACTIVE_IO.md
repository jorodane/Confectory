# V666 진행 중 도구 I/O 관측 기반 검증

[지원·부분 완료 경계](V3_WORKSPACE_ACTIVE_IO.md) · [고정 제품 delta](v666-office-active-io-delta.json).
코드/검사/도구 동결 `87e62a3da052f6af47206d3702aed161d07fb681` 이후는 문서만 변경했다.
최종 **41단계: 신규 34 / 재사용 7**.
LF 17 · CRLF 17 · 패키지/전체 복원/실패 수명관리 7.
독립 Git 객체·NuGet/home·빈 엔진 cache와 출력을 사용했다.

LF의 동일 소스 통과7개(boundary/projection/B2/native 진행/native 완료/진행 UI 소비/완료 UI)를
봉인된 직전 기록에서 재사용했다. Git commit 전체, SDK·의존성·검증 도구 SHA, LF 독립
checkout·실제 명령의 일치를 확인하고 source/SDK 변경 거절 guard도 실행했다. 실패한
배치·빌드·패키지 검사는 재사용하지 않았다. CRLF와 새 패키지/전체 복원은 새로 실행했다.

- 기존 도구 admission/chat-use guard, 소유/ID/namespace/target 검증·Stage/Commit/CAS와
  동기 Snapshot의 코드는 유지했다. 새 Observe는 같은 capability의 읽기 API이며 Agent
  tool schema/rights에 추가하지 않는다. 하나라도 바쁘면 전체 snapshot 수집을 건너뛰고
  캐시된 초안 관측에 pending을 표시한다. primary만 전체 결과를 보관하고 부 관측은 필요한
  origin/staged/log/lastToolIO 네 필드만 보관해 프로젝트 provenance 중복을 막았다. 실제
  native 검사에서도 primary 보존/secondary 제외를 확인했다. 원본 채택은 기존 Review→Confirm/최종 CAS다.
- 실제 DevelopmentTools read와 stage/CAS는 그대로 사용했다. owned scheduling gate로
  실제 reader 호출을 보류하고 Observe 및 ProjectAI Poll이2초 내 반환함을 확인했다.
  ProjectAI의 Worker inventory/adoption은 이 단위 native fixture의 test double이다.
  private origin의 project/task/worker·hash가 맞아야 진행 신호를 연결했고 다른 Worker는
  거절했다. read 완료 뒤 원래 완료 receipt/전체 snapshot으로 복구했다. Stage 예외·CAS
  충돌·성공 모두 active를 해제하며, 중복 call은 신호를 만들지 않았다. 실제 manifest와
  ToolObject 원문 bytes가 유지됐고 새 capability/Close도 신호를 재생하지 않았다.
- 이 gate는 실제 OS 파일 읽기가 EditWorkspace 내부 잠금을 잡은 상황을 재현한 것이
  아니다. 전체 편집기와 물리 I/O의 동시성/UI 갱신 완료로 확대하지 않는다.
- 3D UI는 실제 승인된 Worker를 owned loopback provider에서 대기시킨 뒤 **UI receipt만
  주입**했다. 읽기/초안 문구·잘못된 target/project/receipt 거절·해제·새 chat 입력 보존을
  확인했다. native I/O 타이밍의 end-to-end 증거로 사용하지 않는다. 주입 값은 실제 선택
  변경으로 새 revision을 받은 뒤 표시하며 transport revision 보호를 우회하지 않았다.
- 같은 실제 Worker에서 원래 read/stage 완료, 3D 비활성 상태의 실행 지속, 완료 검증
  대기, 명시 compiler Review→Confirm/채택과 ready 취소를 새로 실행했다. 표시/이동이
  실행·승인·성공 조건이 되지 않았다. 별도 완료 신호 UI/API 회귀도 새로 통과했다.
- 실제 cold journal에 active 필드를 넣어도 진행 신호/실행을 복원하지 않았다. 다른
  프로젝트·Helper/비공개·잘못된 기록은 격리됐고 원래 기록을 복구 명목으로 수정하지
  않았다. 프로젝트 없음은 3D 정체성을 폐기하면서 데이터/실제 작업 기록을 보존했다.
- 순수 projection은 실제 running/assignment/visible-owned root/receipt/ordinal/phase를
  확인하고 완료/실패/취소/ready/needsCheck를 구별했다. snapshot은 불변이고 시작/종료
  시각이나 duration을 만들지 않는다. 복수 대상 자동 선택·새 권한·원본 레이아웃/CSS 변경은
  없다. 기존 B2 표시·배치 정상/늦은 저장 실패·Run 그리드의 관련 회귀도 새로 실행했다.
- 새 Windows 교차 패키지의 구조/전체 SHA/누락·변조 거절, 관리형 엔진 시작과 UI 소비를
  검사했다. ZIP 전체 SHA/CRC·전체 파일/디렉터리 mode 복원 뒤 cold/가시성/입력 보존을
  검사했고 실패 증거 보존·소유 임시물 수명관리도 통과했다. 이는 Linux 관리형 엔진과
  Chromium 자동화이며 Windows apphost/WebView2·모바일/물리 장치 실행이 아니다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/045f19c2064d4163a4087c2340a64ecb.json`.
증거 ZIP `/workspace/artifacts/v536-verification-managed/runs/045f19c2064d4163a4087c2340a64ecb.zip` · SHA256 `e0170b331c0ff8b1b1f0556b0433693dabfc7aa189967cc9a97ec81dfe9ec9ac` · 5643110bytes.
전체 manifest/CRC/파일 mode와 실행 소유 RAM root 제거를 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `87e62a3da052f6af47206d3702aed161d07fb681` | `48927abd242608b5133dedd9c24613072dc67f5d7f670d71bb0a7070223e090a` | 51852221 / 2471 / 152 | `d5ffad25a70e55bc9c11a4974c4148818c7a88cf0703a48e2fbee047ada3dcf1` |
| rollback | `c5693833fc7b9aa1e6f1690430b0a69e77fcc6d9` | `d65490af69d9798231819acc9078a6071f7ad7dd8d9113e4b6443edf643608de` | 51846978 / 2468 / 152 | `dd41d0c693782051e20f6d0cb3493cdfc6897b8bf11a36445b8f32ba2eb49f3c` |

기존 승인된 최신/정상 롤백 두 세대 승격과 자체 임시물 수명관리만 사용했다. 과거 자료·
원본/SDK/사용자 데이터/기존 로그·프로필을 추가 삭제하지 않았다. 사전160MiB 예산에는
안전64MiB가 포함된다. RAM3GiB+512MiB·추가 메모리7GiB+1GiB 기준을 유지했다.
최종 실행 순증가 6.32MiB, 단위 순증가 17.29MiB,
측정 시 여유 1366.41MiB, 단계 표본 최소 여유 1372.68MiB,
peak 메모리 4759.39MiB다. 이후 실행 증가량의 보장값이 아니다.

집중 진단 `/workspace/artifacts/v536-verification-managed/runs/b85465480ae3470ab9b8835f4524be57.json`의 SHA `71935ae4d1ebf65267e914e5155c2109ad08bbacc0a7d5f1fb107b1bd7a17b74`와 모든 통과/실패·입력을 보존했다.
진단 17개 통과/7개 실패는 최종 수치에 합산/재사용하지 않았다.
제품의 완료/진행 C# 패턴 변수 충돌은 이름을 분리해 수정했다. 새 native fixture의 실행기
등록·중복 pack registry·ProjectPack 선언/직접 의존성/default provider 누락은 fixture 설정
오류로 구분했다. UI 주입의 동일 revision은 실제 선택/새 revision으로 바로잡았다.
진단 종료는 의도적 예외로 증거 보존/정리했으며 패키지를 승격하지 않았다.

첫 최종 후보는 정상 검사35개를 모두 마치고 패키징 전 의도적 checkpoint marker로
기존 checkout guard에서 종료했다. 다수 Worker의 provenance 중복 스캔/보관을 줄이기 위한
수정 경계이며 tracked 코드는 그대로였고 패키지 승격은 없었다. 이35개는 최종 재사용에서
제외했다. 수정 소스의 동일 증거7개 재사용과 새 검사의 구분은 위 집계와 같다.

- `/workspace/artifacts/v536-verification-managed/runs/1f64e189269c4b8981e30656415c63d2.json` · SHA `087d7ca65653979d23861917c93b18629d566615266f9fc9e24112c7a645295b` · 정상 통과 35 / 실패 검사 0 · Checkout changed during verification
- `/workspace/artifacts/v536-verification-managed/runs/99fa34c103224c94ac3ae9cbf5b6abcd.json` · SHA `d1bb43b43c9b657202b266bda482d9faa5e12fa066027c68a7e52088b51d0228` · 정상 통과 16 / 실패 검사 1 · lf-office-arrangement-ui: exit 1; log /tmp/cv-92fpae_k/evidence/lf-office-arrangement-ui.log

같은 소스의 LF 배치 검사에서 실제 page.reload 뒤 #app이 비어 .work-body 대기를 넘긴
실패도 보존했다. 그때 JS/external 오류 기록은 없었다. 원인은 미확정이며 재실행 통과가
원인 해결을 뜻하지 않는다. 진행 I/O 코드 변경 없이 해당 경로를 새로 검사했고 이것을
전 UI 초기화/재시작의 완전 검증으로 확대하지 않는다.

현재 마감은 도구 capability의 진행 신호·비차단 batch 관측과 표시 소비 경계다. 실제
OS I/O가 편집기/공유 Workspace 잠금을 잡은 동안의 end-to-end UI 갱신은 미검증이므로
**진행 중 I/O 전체를 완료로 표시하지 않는다**. provider 대기·사용자 C#·최종 파일 쓰기를
도구 진행 신호로 추정하지 않는다. Run HD 이상 전송·GPU/FPS/요소 경계, 기존 신원/권한·
자산·참여자/대화 및 실제 기기·전체 UI·Space/Library 전달은 고정 잔여다. 자격증명·유료/
라이브 AI·새 접근 권한을 사용하지 않았고 main은 보존했다.
