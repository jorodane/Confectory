# 여러 본문 저장과 기존 중첩 호출자 검증

최종 runtime `4f3aa92f82a72e3395204310c8b1b8dc506c882e`의 **신규42단계·재사용0**을 통과했다.
LF17·CRLF17·프로세스 수명1·새 패키지/전체 복원/실패 수명7이다.
[원본 근거와 지원 경계](V666_RETAINED_NESTED.md)를 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 | 두 native 본문의 단일 후보와 원래 중첩 프로그램41은 유효. 원래 구현 선택창에서 실제 callee 본문을 각각 고른 뒤 공동 후보/UI Save만 거절. 원본·checkpoint·입력 보존 |
| 후보/원문 | 두 본문 후보의 순서를 바꿔도 동일. 호출자 graph와 depth2·동명 형제 qualified C#를 새 쓰기 대상으로 넣지 않음. CRLF/Unicode·지역 ID·정확64 값·핀/실행 연결·원래 native/public/override 계약 유지 |
| 거절 | private copy·forwardCallerStorage·implementationContext·wrapper·stale/누락 코드와 잘못된 바인딩7개를 전체 거절. 자동 source 재작성·새 copy/권한·불완전 후보 없음 |
| Save/CAS | Save 전 caller header 변경은 입력/checkpoint/peer 유지·거절. 루트 locals/code 없이 graph만 있어도 내부·형제 원문을 version3 readGuards에 결부. Review 후 header·qualified code·graph·형제 코드의 유효한 peer 변경을 각각 최종 Confirm에서 거절 |
| 복구/실행 | 정확 원문 복구·cold·새 명시 Review/Confirm 뒤 실제 프로그램21. caller header·두 private 코드·graph의 bytes/inode/mode/mtime 보존 |
| cold/증거 | 원래 중첩 상태를 제거한 peer graph에서 cold Review는 이전 receipt를 재기준화하지 않고 거절. 정확 복구 후 원래 receipt로 Review 가능. 기존 readGuards 누락/hash/path/owner/version 변조7개 거절 |
| UI 수명 | 기존 구현 선택창·460px 기본/독립 화면에서 두 본문 취소·명시 편집·Undo/Redo. 공동 Save·미저장/저장 cold·Review 취소/Confirm, 저장 실패 재시도·응답/조회 유실 복구·프로젝트 왕복·취소 통과 |
| 늦은 입력 | Save 응답 중 새 설명을 cold/후속 Save/Review/Confirm까지 보존. owner peer 변경은 재기준화하지 않고 입력/checkpoint 보존·거절. stale 활성화 회귀 유지 |
| 이전 기능 | 기존 네 common/Linux target 후보·누락/서명/부모/stale 거절, native caller CAS·ordinary bool/Result caller·단일 target/빈 guard 기록을 최종 코드에서 새로 검증 |
| 패키지 | LF/CRLF 독립 checkout·HOME/NuGet·Release/MCP·빈 engine cache. 새 Windows 교차 패키지 구조/무결성·포함 Linux 엔진 UI, ZIP CRC/SHA·파일/디렉터리 mode 전체 복원과 복원본 CAS/유실·실패 수명관리 통과 |

제품2파일은 기존 `BlueprintTree`/qualified record·전체 source-ready/assemble·C# 컴파일을
유지하면서 이미 소유한 중첩 호출자를 보존한다. 새 receipt/native ABI/권한·UI 배치는
없다. 기존64-member Review·240 read/write·2048 known unit과 Tree 예산을 유지한다.
기존 단일 target/빈 readGuards 기록은 새로 검증했지만 모든 구 reader와 checkpoint를
교환한 것으로 표현하지 않는다. copy/whole/forward/wrapper의 다른 실제 source closure와
고정7/8행 잔여·9행 일반 입력/out 표시명은 별도다. 가능한 조합별 새 의무는 만들지 않는다.

개발19회 중16통과·3실패는 모두 검사 fixture 문제였다. 첫째는 private child에 루트의
feature/contractHash 및 비private profile을 복제해 기존 소유 검증이 거절한 경우다.
둘째는 기존 구현 선택창을 건너뛰고 곧바로 코드 창이 열린다고 가정한 경우다.
셋째는 `Path.read_text()`가333 CRLF를 LF로 정규화한 비교 오류다. 별도 후보 진단에서
caller graph/코드 쓰기가 없고 원래 unit draft와 실제 bytes가 같음을 확인했다.
각 실패 입력·실행 코드·로그/화면과 진단 후보를 보존했고, 검사 오류에 맞춰 소유/타입 검증을 완화하지 않았다.
이후 후보/실제 UI/CAS·late Save 검사는 통과했으며 개발 결과는 최종42단계에 재사용하지 않았다.

검사 전 관리 ZIP/index를 SHA·크기·inode/mode/mtime으로 확인한 read-only FD별 cache
조언과 준비 프로세스의 사용하지 않는 heap 반환만 사용했다. 전체 cache·다른 프로세스·
데이터·예산은 변경하지 않았다. 최종 launcher도 기존 자기 heap 반환을 재사용하고
동일 preflight/worker 예산·실제 cgroup 계측을 유지했다. 원래 최종 preflight SHA
`bb536078d3049db40d238e2920160b4c959d7a9c06a56e54711feb319a7690ed`는 수집 과정에서 그대로였다.

CRLF 진행 중 읽기 전용 상태 조회 한 번이 `exec-server transport disconnected`로
실패했다. 관리 상태의 connected/running 표시만으로 복구를 판단하지 않고, 실제
명령으로 같은 HEAD와 기존 검사 PID/record를 확인했다. 검사를 재시작하거나 환경을
재생성하지 않았다. 해당 관측은 `transport-observation.json`에 보존했다. 연결 오류의
인프라 원인이나 초기 빈 화면 원인까지 확정하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 4f3aa92f82a72e3395204310c8b1b8dc506c882e | 6a533e1b13ce414ff9eff6c661664a340e0c33efcda74346bfbe2458ab118c29 | 53,867,903 |
| rollback | b44470af6a44b5a9f660c573492774ddee51f990 | 865f0dbb303028d9851c092ae1ef569dd4d7d76f532fdcdab1f018a2050bd886 | 53,869,462 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/72185139bb6f47a792a0e340e5b279ef.json`, evidence `93e00c8cee0939b76b902939604b960c0303541c0a28dd1589fac338db34329f` (8,331,861B).
개발 evidence `87d81b9d5b2f0b273b65002cf075221715805b872facd62ce39acdd6cf226567` (2,997,254B).
양쪽 manifest와 보관 ZIP2개를 재검증했다. 시작 index `ecb0da082ff2ac2986a59f9f4ee2d3b1b35efee88874882e86e7a1427bb94dbf`,
종료 sidecar `f0863b19d60d5c519de10d1518c46ff99fcb3cc08e74cdb8d746d1519df4db09`. 승인된 두 세대 보관 절차에서 이전 rollback
`8820e99c46cb5d28f2d1248c278c0bf29f1c72fd`의 관리 ZIP만 교체했다. 과거 evidence·원본·이전 checkout은
보존했다. 이번 개발/최종 RAM workspace만 identity·봉인 뒤 정리했으며 재생성 출력
해시 목록과 fixture 원문·checkpoint·실패/실행 로그·화면은 남겼다.

시작 여유 25,734,238,208B, 마감 25,717,882,880B(23.9516GiB), 순증가 16,355,328B.
최대 cgroup 전체 memory 9,724,522,496B, 최종 stage 최소 디스크 25,729,069,056B.
추가 cgroup9GiB+안전1GiB·RAM 임시파일4GiB+파일시스템 여유512MiB·디스크 안전64MiB·
개발 evidence256MiB/최종512MiB의 기존 예산을 유지했다.

고급 정보·참조 핀의 공통 값/참조 CLR 대 정보별 생성 타입 선택은 답변 대기다.
기존 신원/그룹 backend·종류 CLR/사용 중 삭제 정책과 다른 고정 잔여도 임의 확정하지
않았다. 닫힌 M11/M12/M4와 초기 빈 화면의 모든 원인을 이 단위로 재판정하지 않는다.
Linux native·Chromium 격리 fixture와 실제 Windows/WebView2·모바일·물리 IME/GPU/audio·
사용자 프로젝트·전체 UI는 구별한다. Windows 교차 패키지는 실제 Windows 실행이 아니다.
Space/Library 전달과 모든 구 reader 교환은 미검증이며 초기 빈 화면 및 과거 Save
요청 미발행의 모든 간헐 원인은 미확정이다.
