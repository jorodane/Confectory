# 고정 C# 노드와 정보 함수 ABI 전환 검증

Runtime source `68e4a940f374c48fa2f0dc6bed0e370fcda0b8f3`를 고정했다. [지원 경계](V666_RETAINED_NATIVE_CODE.md)와
[제품 canonical 해시](v666-retained-native-code-delta.json)를 따른다. 최종 기록 commit은
문서만 추가하며 제품 바이트는 이 runtime source와 같다.

**최종 신규45단계·재사용0**: LF17·CRLF18·owned IPC1·새 package/전체 복원/실패 수명관리9.
개발 결과를 최종 통과로 재사용하지 않았다. 빈 cache의 독립 LF/CRLF checkout에서 각각
빌드하고 원래 UI/API·source 컴파일과 실제 실행을 확인했다.

- 일반 C# code 노드가 있는 직접 소유 동기 Blueprint 구현에서 root int 입력/반환을
  정보 struct로 바꾸고 기존 struct 입력 하나를 삭제했다. 사용하던 code 인자를 현재
  root struct로 명시 재연결하고 원래 writer/실제로 연결된 return exit에서 고정 code
  결과를 명시 선택한다. C# 호출자 본문만 사용자가 선택한 계획으로 바꾼다.
  writer와 exit 양쪽에서 실제 실행30→31을 확인했다.
- C# 노드 서명·source/helpers의 Unicode/CRLF·전체 JSON bytes와 Confirm 전후 mtime를
  보존했다. 변경 없는 record는 candidate 쓰기 목록에 들어가지 않으며 scope와 최종
  읽기 guard에 포함된다. 함수/구현/노드/핀 ID·좌표·entry·실행선과 원래 외부 연결을 유지한다.
- 누락 입력/출력/C# caller 계획, 없는 입력, 오래된 source proof, 잘못된 C# 및 오래된
  definition hash를 읽기/후보 검증에서 거절했다. context/wrapper/async/self-import를
  선택 가능한 코드 보존 권한으로 승격하지 않는다. checkpoint와 원본은 유지한다.
- Save 뒤 cold 복원과 compiler Review를 확인했다. Review 뒤 의미가 같은 code comment를
  추가한 경우 최종 CAS가 거절하며 checkpoint를 보존한다. 정확 복원과 새 Review/Confirm만
  반영한다. 원래 정보/enum/interface 타입 closure·등록 외부 원본·권한을 유지한다.
- Linux native engine+Chromium의 원래460px 카드/420px 상세창에서 타입 선택·입력 삭제,
  명시 input/output 연결 창, 보호된 C# caller 편집·취소, Undo/Redo·별도 창·재시작·원자 Save·
  Review/Confirm을 확인했다. 확정 뒤 원래 Blueprint 편집기에서 고정 code와 export 노드 및
  수락한 entry를 표시하며 source를 추가 생성/재작성하지 않는다.
- checkpoint 쓰기 거절·원본 변경·명시 취소·apply/정산 조회 응답 유실과 cold 회수·늦은
  이름/후속 Save를 확인했다. 같은 계획을 중복 적용하거나 새 입력을 버리지 않는다.
- 최종 코드에서 기존 call/export entry·반환 전환, 미사용 native 함수, 기본형 정보 함수 UI와
  receipt adapter를 새로 회귀 검사했다. live reference/module async 실행으로 합산하지 않는다.
- 새 Windows 교차 package 생성·구조/무결성 probe, 포함 Linux engine의 실제 UI 및 전체
  압축 복원본 API/storage/lost-response/late-input, 실패 수명관리도 새로 통과했다.

개발 14단계 중 실패 3개를 증거에 보존했다. 제품 코드는 최초 빌드 이후 바꾸지 않았다.
처음 두 실패는 지원 밖 graph 속성/잘못된 C#/stale definition에 대한 전체 metadata 읽기가
안전하게 거절되는데 검사가 unavailable 또는 apply 거절만 예상한 fixture 문제였다.
세 번째는 변경 없는 code record가 쓰기 목록에서 빠진 정상 결과를 검사가 변경 row로
예상한 문제였다. 올바른 읽기 거절·쓰기 생략·정확 bytes/읽기 guard를 검사하도록 수정했다.
이 실패를 제품 결함으로 단정하지 않았고 원래 로그/fixture를 보존했다.

직전 package runtime `a55bf720be4265505d0c1f2b67c38276baf1040d`의 ZIP 및 추출한 authoring
파일 해시를 확인하고 이전 바이너리의 readonly metadata 질의를 실제 실행했다. 이전 scope는
일반 code 노드가 있는 이 root ABI 전환을 거절한다. provider 실행·source 쓰기나 이전 전체
workspace reader 실행은 하지 않았다. 기존 nominal/enum parser 비호환과 자동 migration 없음은 유지한다.

| 기록 | evidence SHA256 |
|---|---|
| 최종45단계 | `769aa6aacf52a93e00a2fd1abeadb5e4784a861fd0df1308d50a26a346abee7b` |
| 개발·원래 실행·fixture 진단/복구 | `3adfe07e32a7cc7708fd5499d4b2ae8fb7bf7043a0260201ca474d58330bcda7` |

최종 run record `/workspace/artifacts/v536-verification-managed/runs/dfbb4ecf97ef497e93d50e43ebf9ab3e.json`. evidence ZIP manifest와 전 파일 해시를 다시 확인했다.
원본·증거를 보존하고 소유한 재생성 가능 임시 산출물만 기존 관리 규칙으로 정리했다.

| 세대 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | `68e4a940f374c48fa2f0dc6bed0e370fcda0b8f3` | `48c641622b211b96f080d117b38dd92c482061a643b6c50ef3f5d7328f05377b` | 53976340 |
| rollback | `a55bf720be4265505d0c1f2b67c38276baf1040d` | `5541e30476e3d6708c32592ea4d4a1f78f2e77253a95aafaa6cb66689a8ece5c` | 53976388 |

기존 latest를 rollback으로 유지하고 이전 rollback 한 세대만 기존 관리 규칙으로 교체했다.
추가 메모리9GiB+여유1GiB·RAM 파일4GiB+여유512MiB·evidence512MiB·디스크 여유64MiB를
유지했다. SDK/seed와 알려진 관리 archive에 읽기 FD cache advice만 사용했다. 전역 cache·
과거 evidence·원래 checkout은 정리하지 않았다. 디스크 여유 25,565,822,976B
(약23.81GiB), 관찰 cgroup peak 8,984,256,512B다.

남은 같은9행은 노드 자체 C# 서명/import ABI 변경 및 private/whole-body 대응, 살아 있는
reference의 실제 객체/접근자와 수명, module async/공개 실행 결과의 계약-only closure/DLL
순환 처리, multiple/함수 필드 native 생성이다. 선택 조합을 새 필수 행으로 늘리거나
M11/M12/M4를 새 회귀 없이 다시 열지 않는다. 이번 보존 경로에 미결정 정책은 없다.
실제 Windows/모바일·전체 UI는 미검증이며 초기 빈 화면 원인은 미확정이다.
