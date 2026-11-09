# 명시 검토한 플랫폼별 C# 본문 공동 저장 검증

최종 runtime `b44470af6a44b5a9f660c573492774ddee51f990`의 **신규42단계·재사용0**을 통과했다.
LF17·CRLF17·프로세스 수명1·새 패키지/전체 복원/실패 수명7이다.
[원본 수용 근거·지원·호환 경계](V666_MULTITARGET_BODIES.md)를 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 | 공통/Linux 각 target을 명시한 함수별 후보와 원래 프로그램40/44는 유효. 두 함수 공동 후보와 기존 구현 선택/UI Save만 거절. 원본·checkpoint·네 입력 보존 |
| 후보/실행 | 네 native target의 역순 후보도 동일. 같은 public/native/override 계약·핀 ID/타입·원래 헤더와 호출자 보존. 모든 target을 명시 검토한 뒤 portable/common20·Linux24를 실제 실행 |
| 기존 거절 | 누락/미등록 target·서명 불일치·부모 소유·stale body hash는 그룹 전체 거절. 미검토 target 자동 승인·자동 복제/원문 변환 없음 |
| 원자/CAS | Save 전 target header 변경 거절. Review 후 header·Linux 본문·유효한 caller graph·Main C# 변경 각각 최종 Confirm 거절. 모든 target 입력·checkpoint·peer 유지. 정확 복구·cold·새 Review/Confirm 및20/24 실행 |
| target 소멸 | live Review는 선언에서 target이 사라진 경우 거절. 강제 프로젝트 cold 시작도 기존 Restore locator 소유 규칙으로 거절하며 네 입력과 checkpoint bytes 보존. 정확 원본 헤더를 복구하면 다시 열고 새 Review 가능. 없어진 ID 이행은 추가하지 않음 |
| 완전한 증거 | 후속 설명 Save도 네 target·같은 readGuards·8-member 그룹 유지. body 증거 누락, 증거+header/body guard 동시 누락, kind/path/그룹 멤버5개 변조를 cold Restore 또는 Review 접수에서 거절. 정확 영수증 복구 뒤 새 Confirm과20/24 실행 |
| 다른 guard/구 기록 | readGuards 누락/hash/path/owner/version 변조7개 거절. 기존 단일 target/빈 guard의 cold/Review/Confirm·실행20, 그대로인 native caller의 CAS, ordinary bool/Result caller 후보를 최종 코드에서 새로 검증 |
| 실제 UI 수명 | 기존460px 창/target 선택기에서 네 본문을 각각 취소·편집·Undo/Redo. 함수 단위 Undo와 미저장/저장 cold·Review 취소/Confirm. 실패 재시도·응답/조회 유실 복구·프로젝트 왕복·취소와 독립 창 확인 |
| 늦은 입력/활성화 | 본문 Save 응답 중 새 설명을 cold/후속 명시 Save/Review/Confirm까지 보존. owner peer 변경은 재기준화 없이 거절. 기존 pointerdown/peer refresh/release 활성화와 stale 입력 거절 유지 |
| 패키지/복원 | 독립 LF/CRLF no-hardlinks·HOME/NuGet·Release/MCP·빈 engine cache. 새 Windows 교차 패키지 구조/무결성·포함 Linux 엔진 UI, ZIP CRC/SHA·파일/디렉터리 mode 전체 복원과 복원본 CAS·응답 유실·실패 수명관리 통과 |

제품2파일은 기존 여러 본문의 native target 수용과 완전한 saved group 증거 인식을
연결한다. 영향받는 모든 native target의 명시 검토·source-ready/assemble·함수/구현
소유와 원래 typed signature 검증을 유지한다. 한 그룹은 기존64-member Review·
240 read/write·2048 known unit 예산을 넘기지 않는다. 같은 version3 readGuards,
원자 checkpoint/CAS·공유 이력·최종 source lease를 사용한다. 새 native ABI/receipt
문법·권한·UI 배치·자동 C# 재작성이나 target 복제 정책은 추가하지 않는다.

개발19회 중17통과·2실패를 기록했다. 첫 실패는 기존 Restore가 사라진 target locator를
거절하는데도 강제 프로젝트 fixture가 cold 시작을 허용한다고 가정한 오류다.
`Restore.csbody`/`WebStart.csbody`가 게시본과 같음을 확인했고, 검사를 거절·정확 복구
기준으로 고쳤다. 소유 guard를 완화하거나 이를 새 migration 의무로 만들지 않았다.
둘째는 후속 설명 Save 뒤 target 증거 하나를 제거하면 native 분류가 풀려 Review
요청이 접수되는 실제 누락이다. Confirm은 실행하지 않았고 원본8개 baseline 해시가
그대로였다. 실제 typed 그룹으로 native 그룹을 인식해 불완전 증거를 즉시 거절한다.
실패 당시 source/입력·실행 코드·로그와 해시 증거를 따로 보존했다. 개발 통과는
최종 검증에 재사용하지 않았다.

개발 시작 전 메모리 사전검사3회 차단은 workspace/build 생성 전이었다. 해시·크기·
inode/mode/mtime을 확인한 관리 ZIP/index의 read-only FD별 cache 조언과 해당 준비
프로세스의 사용하지 않는 heap 반환만 사용했다. 전체 cache·다른 프로세스·데이터·
예산은 바꾸지 않았다. 최종 launcher도 SDK/index identity 계산의 사용하지 않는
자기 heap만 반환하며 이후 동일 preflight/worker 예산과 실제 cgroup 계측을 사용한다.
원래 preflight SHA `0fe6edc02c24f2ec74b6f212b90a1634b2eb01848feb085d027bf7e42e55a2aa`는 수집 과정에서 그대로 보존했다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | b44470af6a44b5a9f660c573492774ddee51f990 | 865f0dbb303028d9851c092ae1ef569dd4d7d76f532fdcdab1f018a2050bd886 | 53,869,462 |
| rollback | 8820e99c46cb5d28f2d1248c278c0bf29f1c72fd | 86d3d9d373e0c498ce371c15c25da7c797c49cc16e37279ce17699f1b4ac98df | 53,866,852 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/a3ffbafd29b146f7baf6baf55f768cb3.json`, evidence `6eafdf8c914658df4876735d576bcc1e1d0a6e825dc20768514628958f0fccd4` (11,051,338B).
개발 evidence `fd7ed2b4bedd0ae51b9a4301eefd5d2e331fae28b6a2dfb1d5e4bcdb6d27d7dd` (3,676,885B).
양쪽 manifest와 보관 ZIP2개를 재검증했다. 시작 index `068abf67d5b9a10936fbbb0bab22fa7328b900b0d5bec2175889ab1e5372595b`,
종료 sidecar `ecb0da082ff2ac2986a59f9f4ee2d3b1b35efee88874882e86e7a1427bb94dbf`. 승인된 두 세대 보관 절차에서 이전 rollback
`7938a4f01e6331cd980e4397fbba66fc3ffc0ea8`의 관리 ZIP만 교체했다. 과거 evidence·사용자 원본·이전
checkout을 보존했으며 이번 개발/최종 RAM workspace만 identity·봉인 검증 뒤 정리했다.
재생성 build 출력의 해시 목록을 남기고 fixture 원문·checkpoint·실패/실행 로그·화면은
archive에 유지했다. 그 밖의 과거 자료나 임시 경로는 삭제하지 않았다.

시작 여유 25,754,087,424B, 마감 25,734,381,568B(23.9670GiB), 순증가 19,705,856B.
최대 cgroup 전체 memory 9,766,449,152B, 최종 stage 최소 디스크 25,748,279,296B.
추가 cgroup 메모리9GiB+안전1GiB·RAM 임시파일4GiB+파일시스템 여유512MiB·
디스크 안전64MiB·개발 evidence256MiB/최종512MiB의 기존 예산은 유지했다.

고정7/8행의 다른 실제 ABI/source closure와9행 일반 입력/out 표시명·고급 타입
실행 통합은 기존 잔여다. 고급 정보·참조 핀의 공통 값/참조 타입 대 정보별 C# 타입
생성은 사용자 답변 대기이며 임의 확정하지 않았다. 기존 신원/그룹 backend·종류
CLR/사용 중 삭제 정책·실기기 잔여와 구별하고 경우의 수별 새 의무를 만들지 않는다.
닫힌 M11/M12/M4·초기 빈 화면의 모든 원인을 이 단위로 재판정하지 않는다.

실행 검증은 Linux native 엔진·Chromium·격리 fixture다. Linux target과 실제 Windows/
WebView2·모바일·물리 IME/GPU/audio·사용자 프로젝트·전체 UI를 구분한다. 교차 패키지는
Windows 실행이 아니다. Space/Library 전달과 모든 구 reader 교환은 미검증이며,
초기 빈 화면 및 과거 Save 요청 미발행의 모든 간헐 원인은 계속 미확정이다.
