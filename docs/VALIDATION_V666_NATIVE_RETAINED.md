# 독립 그래프 상태를 보존한 native ABI 검증

Runtime source `2afbe93143ecfea870c4f92192151019c971218d`를 고정했다. [지원 범위](V666_NATIVE_RETAINED.md)와
[제품 canonical 해시](v666-native-retained-delta.json)를 따른다. 최종 기록 commit은 문서만
더하고 제품 바이트는 이 runtime source와 같다.

**최종45단계: 신규34·동등 재사용11**: LF17·CRLF18·owned IPC1·새 package/전체 복원/실패 수명관리9.
독립 LF/CRLF checkout에서 기존 SDK와 NuGet seed를 사용해 빌드·수정 검사·패키지/복원을 새로 수행했다. 아래 coverage는 최초 최종 실행과 검증된 동등 재사용을 함께 포함한다. 개발 결과는 최종 통과로 재사용하지 않았다.

- 직접 소유 동기 retained root의 int 입력/반환을 정보 struct로 전환했다. 한 문맥의 실제
  native 인자명·서명/본문·일반 C# 호출자와 root 반환 writer의 새 source를 명시 선택했다.
  원래 entry·노드/반환 ID·좌표·실행선과 정확한 long local9223372036854775806을 보존했다.
  독립 code/helpers의 전체 Unicode/CRLF bytes·mtime와 원래 `.csbody` 파일도 유지하며
  실제 실행30→31을 확인했다. 변경 없는 독립 record는 읽기 의존성으로만 보관했다.
- native 출력 해제와 명시 writer 교체를 함께 저장했다. 이전 출력이 독립 code 인자에
  여전히 연결된 별도 사례는 UI/API 양쪽에서 전체 거절했다. 원래 출력 사용처 목록의 모든
  슬롯이 명시 교체 대상일 때만 UI가 해제를 허용하며 backend 소비자 검사를 약화하지 않았다.
- 누락 본문/호출자/writer 계획, stale whole/context/return receipt, 틀린 native ABI·출력
  대응과 잘못된 C#은 checkpoint/원본 쓰기 없이 거절했다. 후보를 cold 복원한 compiler
  Review와 새 Confirm이 통과하고, Review 뒤 code record의 공백 변경은 최종 CAS로 거절했다.
- 원래460px 카드/420px 상세창과 C# chooser에서 고급 타입 선택, 초기 출력 선택, 본문·
  호출자 편집 뒤 최종 출력 대응, 취소·Undo/Redo·cold 복원·원자 Save·중복 저장 차단·
  Review/Confirm·실행을 확인했다. 같은 C# 편집기로 다시 열어도 원본을 추가 생성/재작성하지 않았다.
- checkpoint 쓰기 실패·원본 충돌·명시 취소·apply/정산 응답 유실과 cold 회수, 늦은 이름과
  후속 Save를 확인했다. 기존 단일 whole lift의 고급 ABI API/UI와 기존 기본형 retained
  그래프의 별칭·출력·본문 UI/API 연계를 새로 회귀 검사했다. 소유/권한·override와 원본 배치는 유지했다.
- 새 Windows 교차 package 생성·구조/무결성 probe, 포함 Linux 엔진의 실제 UI와 전체
  압축 복원본 API/storage/lost-response/late-input·패키지 실패 수명도 새로 확인했다.
  실제 Windows 실행이나 전체 UI 수용으로 합산하지 않는다.

개발 14단계와 fixture 실패2개를 보존했다. 첫 API 실패는 원래 노드 변수를
fixture가 내보내지 않은 오류였다. 첫 UI 실패는 타입 선택 직후의 기존 출력 대응창을 건너뛰어
그 창이 다음 C# 클릭을 막은 경우였다. 원래 창에서 현재 입력을 명시 선택하고, C# 본문 계획
뒤 새 node 결과를 최종 선택하는 실제 사용자 순서로 fixture를 수정했다. 제품 코드는 최초
빌드 이후 바꾸지 않았다. 실패 로그·원본 fixture와 복구 결과를 증거에 보존했다.

첫 최종 실행은17단계 통과 뒤 기본형 retained UI의 오래된 fixture 기대에서 멈췄다.
변경되지 않은 독립 code가 쓰기 목록에서 생략되는데 항상 변경 row와 그룹에 있다고
가정한 KeyError였다. row가 있으면 기존 source 검사를 유지하고, 없으면 전체 물리 원문이
snapshot과 같음을 확인하도록 수정했다. 제품4파일은 처음 고정한 bdd23dff와 byte-for-byte
동일하다. 실패 증거·manifest 전 파일 해시, 같은 SDK/NuGet/configuration/RID, 실제 명령과
통과 테스트의 transitive import closure가 수정 fixture에 의존하지 않음을 검사했다.
이미 통과한 IPC·LF 선언/아이콘/receipt/API/UI11단계만 동등 재사용했다. 실패/수정된 검사,
LF/CRLF 빌드와 package/전체 복원은 새로 수행했으며 재사용으로 실패를 통과 처리하지 않았다.

직전 package runtime `46b8595f93831467d3a9b6a65aa89274ffe0b759`의 ZIP/추출 파일 해시를
검증하고 이전 authoring 바이너리의 readonly metadata 질의를 실제 실행했다. 이전 scope는
독립 노드/local을 가진 이 retained 전환을 거절한다. provider 실행/원본 쓰기·이전 전체
workspace reader 실행은 하지 않았다. 기존 nominal/enum parser 비호환·자동 migration 없음은 유지한다.

| 기록 | evidence SHA256 |
|---|---|
| 최종45단계 | `c4c0abb27dd698524f27145e479782b3bc71747ca6b0274103c6a6eaa23d3f0b` |
| 개발·fixture 진단/복구 | `64c8f8aac38c0e4b10aba5ef4696da1b7d6b69f63cd77c141cb16b4f49596579` |
| 첫 최종 실행·동등 재사용 출처 | `e963199e25eac45275d8c252a4baf7dbd8a9ef23777c4cc0c31a47cf7e75738d` |

최종 record `/workspace/artifacts/v536-verification-managed/runs/b36f3500e10049e1904399211d974b3b.json`. evidence ZIP/manifest 전 파일 해시를 재확인했다.
원본·증거를 보존하고 소유한 재생성 가능 임시 산출물만 기존 관리 규칙으로 정리했다.

| 세대 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | `2afbe93143ecfea870c4f92192151019c971218d` | `b5a7d5a4a6431915d6381996bf04e198bafadb963548bddd458b10dc1f414605` | 53978888 |
| rollback | `46b8595f93831467d3a9b6a65aa89274ffe0b759` | `cb61ab8cc94e034b02b9b5f5b101ac395948700c9eb4d4a01a8994fcfe194d99` | 53977655 |

이전 latest를 rollback으로 보관하고 이전 rollback 한 세대만 기존 관리 규칙으로 교체했다.
추가 메모리9GiB+여유1GiB·RAM 파일4GiB+여유512MiB·evidence512MiB·디스크 여유64MiB를
유지했다. SDK/seed·알려진 관리 archive의 읽기 FD cache advice만 사용했고, 전역 cache·
과거 evidence·원래 checkout은 정리하지 않았다. 디스크 여유 25,543,004,160B
(약23.79GiB), 관찰 cgroup peak 9,128,079,360B다.

독립 code/private frame ABI와 다른 기존 문맥, 살아 있는 참조 객체/접근자·수명, 모듈
async/공개 실행 결과의 계약-only closure/DLL 순환, multiple/함수 필드 native 생성은 같은
유한 잔여다. M11/M12/M4를 새 회귀 없이 다시 열거나 조합별 새 필수 행을 늘리지 않는다.
이번 범위에 미결정 정책은 없다. 실제 Windows/모바일·전체 UI는 미검증이며 초기 빈 화면
원인은 미확정이다.
