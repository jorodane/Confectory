# 단일 코드 whole-body 고급 ABI 검증

Runtime source `46b8595f93831467d3a9b6a65aa89274ffe0b759`를 고정했다. [지원 범위](V666_NATIVE_WHOLE.md)와
[제품 canonical 해시](v666-native-whole-delta.json)를 따른다. 최종 기록 commit은 문서만 더하며
제품 바이트는 이 runtime source와 같다.

**최종 신규45단계·재사용0**: LF17·CRLF18·owned IPC1·새 package/전체 복원/실패 수명관리9.
빈 cache의 독립 LF/CRLF checkout에서 각각 빌드했다. 개발 결과를 최종 통과로 재사용하지 않았다.

- 정확한 직접 소유 동기 whole-body lift의 int 입력/반환을 정보 struct로 전환했다. 원래
  C# native 인자명 `nativeAmount`와 공개 인자명 `amount`를 유지하며 서명·본문과 일반 C#
  호출자 계획을 명시 편집했다. 원래 코드/반환 writer ID·좌표·entry·실행선·소유/권한을 유지했고
  실제 실행30→31을 확인했다. 원래 `.csbody` 보관 파일 bytes는 변하지 않았다.
- 누락 whole-body/호출자 계획, stale graph/context/return receipt, 틀린 native 타입,
  잘못된 C#은 checkpoint/원본 쓰기 없이 전체 거절했다. 저장 후보를 cold 복원한 compiler
  Review가 통과하고, Review 뒤 code record에 공백만 추가해도 최종 CAS는 거절했다.
  정확 복원과 새 Review/Confirm만 반영한다.
- 원래460px 카드/420px 상세창과 C# chooser에서 struct 타입 선택, canonical nominal
  매개변수명·명시 본문/호출자 편집, 편집 취소·Undo/Redo·별도 창·cold 복원·원자 Save·중복
  Save 차단·Review/Confirm·실제 실행을 확인했다. 수락한 서명/본문을 같은 C# 편집기로 다시
  열어도 원본을 추가 생성하거나 다시 쓰지 않았다. 레이아웃/CSS 변경은 없다.
- checkpoint 쓰기 거절·원본 변경·명시 취소·apply/정산 조회 응답 유실과 cold 회수,
  늦은 이름/후속 Save 보존을 확인했다. 같은 계약/본문 계획을 중복 적용하지 않았다.
- 기존 고정 C# 노드의 struct 입출력 재연결·bytes/mtime/CAS/실행을 다시 확인했다.
  미사용 native 함수 및 기존 기본형 whole-body 계약의 API/UI도 새로 회귀 검사했다.
- 새 Windows 교차 package 생성·구조/무결성 probe, 포함 Linux 엔진의 실제 UI와 전체
  압축 복원본 API/storage/lost-response/late-input·패키지 실패 수명을 새로 검증했다.
  실제 Windows 실행이나 전체 UI 수용으로 합산하지 않는다.

개발 12단계와 최초 Review 실패를 보존했다. 최초 후보 저장은 통과했지만 cold
Review가 consumer_error로 거절됐다. 새 후보의 구현 헤더가 overlay로 보이는 상태에서
아직 원본인 graph context와 비교하던 제품 결함이었다. 원본 scope 관측은 물리 원본 구현
헤더와 비교하고, 변경된 후보는 별도의 전체 compiler 검증으로 확인하도록 수정했다.
읽기 source hash/최종 CAS를 제거하거나 새 원본을 자동 수락하지 않았다. 수정 뒤 cold
Review·원본 공백 충돌·정확 복원·새 Confirm·실제31 및 UI/늦은 입력 회귀를 통과했다.
개발 초기에 UI 매개변수 정규식의 수정 위치를 더 좁혀 원래 전체 본문 편집기만 변경했다.

직전 package runtime `68e4a940f374c48fa2f0dc6bed0e370fcda0b8f3`의 ZIP/추출 파일 해시를
검증하고 이전 authoring 바이너리의 readonly metadata 질의를 실제 실행했다. 이전 scope는
이 whole-body nominal 전환을 거절한다. provider 실행/원본 쓰기·이전 전체 workspace reader
실행은 하지 않았다. 기존 nominal/enum parser 비호환·자동 migration 없음은 유지한다.

| 기록 | evidence SHA256 |
|---|---|
| 최종45단계 | `84cc2c1a1cabb6cda9f72c1a25f24ef9a5d414a28db6cf7ffe1dd26320e18b6d` |
| 개발·Review 진단/수정 | `7cb7e7678cac5091ed239ad96aa14fa4b9638fcc54989923619eae60215a391c` |

최종 record `/workspace/artifacts/v536-verification-managed/runs/191fc78d631848239431091626dee555.json`. evidence ZIP/manifest 전 파일 해시를 재확인했다.
원본·증거는 보존하고 소유한 재생성 가능 임시 산출물만 기존 관리 규칙으로 정리했다.

| 세대 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | `46b8595f93831467d3a9b6a65aa89274ffe0b759` | `cb61ab8cc94e034b02b9b5f5b101ac395948700c9eb4d4a01a8994fcfe194d99` | 53977655 |
| rollback | `68e4a940f374c48fa2f0dc6bed0e370fcda0b8f3` | `48c641622b211b96f080d117b38dd92c482061a643b6c50ef3f5d7328f05377b` | 53976340 |

이전 latest를 rollback으로 보관하고 이전 rollback 한 세대만 기존 관리 규칙으로 교체했다.
추가 메모리9GiB+여유1GiB·RAM 파일4GiB+여유512MiB·evidence512MiB·디스크 여유64MiB를
유지했다. SDK/seed·알려진 관리 archive의 읽기 FD cache advice만 사용했다. 전역 cache·
과거 evidence·원래 checkout은 정리하지 않았다. 디스크 여유 25,555,345,408B
(약23.80GiB), 관찰 cgroup peak 9,127,911,424B다.

독립 code 노드 자체 ABI·private/retained whole 문맥, 살아 있는 참조 접근/수명, 모듈
async/공개 실행 결과의 계약-only closure/DLL 순환, multiple/함수 필드 native 생성은 같은
유한 잔여다. M11/M12/M4를 새 회귀 없이 다시 열거나 조합별 새 필수 행을 늘리지 않는다.
이번 범위에 미결정 정책은 없다. 실제 Windows/모바일·전체 UI는 미검증이고 초기 빈 화면
원인은 미확정이다.
