# 직접 Blueprint 호출자의 고급 타입 입력 검증

Runtime source `a3659c2445b736db6234ce097b1f64cfbd962bc7`를 고정했다. [지원 경계](V666_BLUEPRINT_NATIVE_INPUTS.md)와
[제품 파일 canonical 해시](v666-blueprint-native-inputs-delta.json)를 따른다.
기존 C#과 공개/override 계약·소유/권한·원본 카드/상세창 배치를 보존한다.

## 신규 검증

**신규45단계, 재사용0**: LF17·CRLF18·owned IPC1·package/전체 복원/실패 수명관리9.
개발 결과를 최종 통과로 재사용하지 않았으며 독립 LF/CRLF checkout과 빈 엔진 cache에서
각각 빌드했다. 마지막 commit은 검증 기록만 추가하므로 제품 파일은 위 runtime 해시와 같다.

- 기존 Blueprint 호출자는 이미 가진 정보 struct·종류 enum·interface 배열의 입력을 선택한다.
  기존 int 입력 연결의 해제와 native C# 본문 계획을 명시하고 한 후보로 Save한다.
  일반 C# runtime 호출자의 원문은 변경하지 않고 실제 결과30→31을 확인했다.
- 빠진 C# 계획·알 수 없는/다른 타입/자기 결과 입력·임의 JSON 구조체 값·미확인 연결 해제·
  오래된 그래프 증거는 checkpoint/원본 쓰기 없이 거절한다. private copy·opaque code·
  async frame은 타입 선택 권한으로 승격하지 않는다.
- 전체 후보의 cold 복원과 compiler Review를 확인한다. Review 뒤 Blueprint 원문 변경은
  최종 CAS로 거절하며 정확 복원 후 새 Review/Confirm만 원래 ID·좌표·실행/반환 연결을
  유지하며 반영한다. 타입 정의와 등록 외부 원본을 쓰기 대상으로 추가하지 않는다.
- Linux native engine + Chromium의 원래460px 카드/420px 상세창과 기존 입력 대응 창에서
  실제 선택·C# 편집 취소·Undo/Redo·별도 창·재시작·명시 저장/검토/확정을 확인했다.
  확정 후 같은 계약의 C#을 다시 편집해 실제32를 확인하고 runtime 호출자의 bytes/mtime를 유지했다.
- checkpoint 쓰기 거절·저장 준비 중 원본 변경·취소·apply/정산 조회 응답 유실과 재시작·
  늦은 이름 및 후속 Save를 확인했다. 수락한 본문 계획을 중복 제출하거나 입력을 버리지 않는다.
- 동일 최종 코드에서 기존 직접 C# 호출자 전환/후속 저장·미사용 함수 전환·기본형 정보 기능
  UI와 nominal module 생성을 회귀 검사했다. 기존 receipt adapter 검사도 새로 실행했다.
- 새 Windows 교차 package 생성·구조/무결성 probe, 포함 Linux engine의 실제 UI와 전체
  압축 복원본 API·storage/lost-response/late-input·실패 수명 관리를 모두 새로 확인했다.

## 개발 진단과 호환성

개발15단계 기록과 실패3개를 모두 보존했다. 초기 시험 프로젝트는 `body common blueprint`
대신 기존 문법 `blueprint common`을 사용해야 했다. startup/정확한 parser 위치 진단 후
fixture만 고쳤다. 이후 UI 시간 초과는 본문 하나일 때 원래 C# 편집기로 바로 진입하는데
시험이 복수 본문 선택 목록을 기다린 탓이었다. 실제 열린 편집기의 화면/상태를 보존하고
시험 조작을 고쳤다. 제품 문법/계약/컴파일 검증이나 권한을 약화하지 않았다.
그 후 API·UI·늦은 입력과 최종45단계를 새로 통과했다.

직전 sealed package source `50d07f3be05f39a80de79fcd0e15985a9c1ae507`에서 추출한 authoring 파일들과
ZIP의 해시를 확인해 읽기 전용 metadata 질의를 실제 실행했다. 이전 scope는 Blueprint
호출자를 거절했다. provider 실행/원본 쓰기는 하지 않았다. 이전 전체 workspace reader 실행이나
모든 과거 parser/DLL 호환 완료로 주장하지 않는다. 기존 nominal/enum 구 reader 제한과
명시 거절은 유지하고 자동 migration을 추가하지 않는다.

| 기록 | evidence SHA256 |
|---|---|
| 최종45단계 | `69c06647c53ca6db2a839a5a0ff93c449b842b8c83c2e38110335cf1287d096f` |
| 개발·원래 실행/거절·fixture 진단/복구 | `3833e1ccb0c1a7bc19a916c3b5bc665b2f6352a19fb93edf54e153ff08753236` |

최종 run record `/workspace/artifacts/v536-verification-managed/runs/c21fd68a4aa141db8faecc808eeb4250.json`. 두 evidence ZIP의 manifest와 전 파일 해시를 재확인했다.
증거와 원본은 보존하고 관리자가 소유한 재생성 가능 임시 산출물만 기존 규칙으로 정리했다.

## 보관과 한계

| 세대 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | `a3659c2445b736db6234ce097b1f64cfbd962bc7` | `e364458ab6499cb361f48073a16ac57a25d137bd87ecfe7db36895882645cd09` | 53975188 |
| rollback | `50d07f3be05f39a80de79fcd0e15985a9c1ae507` | `d35fef4392874e683f36f6a207a9d651e68094b340d2967b5b85df78665014e5` | 53973789 |

검증 뒤 이전 latest를 rollback으로 유지하고 이전 rollback 한 세대만 승인된 관리 규칙으로
교체했다. 추가 메모리9GiB+여유1GiB·RAM 파일4GiB+여유512MiB·evidence512MiB·디스크 여유
64MiB를 유지했다. SDK/seed와 알려진 관리 archive의 읽기 FD cache advice만 사용했다.
전역 cache·과거 evidence·원래 checkout은 정리하지 않았다. 디스크 여유
25,585,299,456B(약23.83GiB), 관찰 cgroup peak 8,896,741,376B다.

Blueprint 구현 entry/출력의 고급 ABI, 살아 있는 reference의 실제 객체/접근자 연결,
module async/공개 실행 결과의 contract-only closure 및 assembly 순환 처리,
기존9행 multiple/함수 필드 native 생성은 남는다. 결과 ABI를 복제/생략하거나 기존 C#을
추정 변환하지 않는다. M11/M12/M4를 새 회귀 없이 재개하거나 선택 조합을 필수로 늘리지 않는다.
현재 입력 연결에 미결정 정책은 없다. 실제 Windows/모바일·전체 UI는 미검증이며
초기 빈 화면의 원인은 미확정이다.
