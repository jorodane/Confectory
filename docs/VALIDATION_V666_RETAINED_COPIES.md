# 여러 본문 저장과 기존 소유 복사본 검증

최종 runtime `1b8a51a2512879db9869f312a32fca99e0a563ab`의 **신규43단계·재사용0**을 통과했다.
LF18·CRLF17·프로세스 수명1·새 패키지/전체 복원/실패 수명7이다.
[원본 근거와 지원 경계](V666_RETAINED_COPIES.md)를 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 | 두 native 본문의 단일 후보와 원래 copy 프로그램40은 유효. 기존 선택창의 공동 후보/UI Save만 거절하며 원본·checkpoint·입력 보존 |
| 후보/원본 | 순서와 무관하게 두 명시 native 본문만 linked write로 구성. donor·local copy header/graph·단독 배정·default provider·공개/native 계약과 핀/연결 보존 |
| 출처 검증 | 원래 copy proof 전체를 먼저 검증하고, 동일 계약으로 명시 저장한 함수 선언의 해시만 내부 후보로 투영. owner·출처·graph·나머지 context가 다르면 전체 거절 |
| 거절 | 빠진 copy proof·잘못된 owner/graph/context hash·변경 provenance/배정/공개 계약·중첩 provenance/forwarding9개 전체 거절 |
| Review/CAS | Save 전 copy header 변경 및 Review 후 copy header·Main C#·provenance graph·배정·등록 pack 변경을 각각 거절. peer와 checkpoint·두 본문 입력 보존. 정확 복구/cold/새 Review/Confirm 뒤 실제20 |
| 원문 | donor/copy와 배정·default provider·ID/실행 연결·CRLF Unicode·exact64 값 보존. 읽기 전용 copy header/Main/graph의 bytes/inode/mode/mtime 보존 |
| receipt | 기존 version3의 nativeBodyCopies로 원래 copy context 유지. 원래 snapshot에서 모든 필요한 copy proof를 다시 검증하고, 실제 등록 의존성과 native source guard의 정확한 합집합 유지. 누락/변조10개 거절 |
| cold/후속 Save | provenance가 제거된 peer graph는 cold Review에서 거절. 정확 복구 후 원래 receipt로 재검토. 늦은 설명 입력·cold·후속 Save·취소/재검토·Confirm과 stale peer 거절에서 원래 proof/readGuards 유지 |
| UI/수명 | 기존 화면·460px 기본/독립 창에서 본문 편집·취소·Undo/Redo·미저장/저장 cold, 실패 재시도·응답/조회 유실·프로젝트 전환·취소·반복/늦은 입력 보존 |
| 회귀 | 최종 코드에서 기존 네 common/Linux target·After/실행 enum·native caller CAS·ordinary bool/Result·단일 target/빈 guard 기록을 새로 검증 |
| 패키지/복원 | 독립 LF/CRLF·HOME/NuGet·Release/MCP·빈 engine cache. 새 Windows 교차 패키지 구조/무결성·포함 Linux 엔진 UI. ZIP CRC/SHA·파일/디렉터리 mode 전체 복원 및 복원본 CAS/응답 유실·실패 수명 통과 |

제품5파일은 기존 native body group에 원래 단독 배정 copy proof와 전체 읽기 범위를
결합한다. 실파일 기준을 재설정하거나 C#을 자동 치환하지 않는다. 기존64-member
Review·240 read/write·2048 known unit, 소유·권한·Review→Confirm·원자 저장/CAS는 유지한다.
공개 override 계약 변경·donor/부모/외부 쓰기, 새 복사·공유 배정·first-save copy·forwarding
전환은 자동 승인하지 않는다. 다른 실제 source/ABI closure는 기존7/8행의 같은 잔여다.
일반 입력/out 표시명과 고급 타입은9행이다. 경우의 수별 새 의무로 늘리지 않는다.

개발23회 중21통과·제품 실패2회였다. 첫 순수 후보는 첫 함수의 명시 설명이 내부
후보에 반영된 뒤 두 번째 함수의 원래 copy context와 달라져 거절됐다. 원래 proof를
검증한 동일 계약 함수 해시만 내부 후보로 투영해 보완했다. 다음 API는 Save 전 source
변경 거절과 원자 Save까지 통과했지만 첫 Review에서 거절됐다. 원래 등록 pack 관측은
copy guard에 있으나 owned unit 목록에는 없어 두 읽기 집합을 결합하지 못한 결함이었다.
원래 copy proof를 receipt에 보존하고 cold에서 원래 snapshot으로 다시 검증하여 정확한
전체 집합을 유지하도록 보완했다. 양쪽 실패 입력·실행 코드·checkpoint·로그와 별도
review-guard-diagnostic.json을 보존했다. 별도로 재개 스크립트의 이미 존재하는 로그명은
중복 worker 시작 전에 거절됐다. 원래 로그를 덮지 않고 새 단계명으로 이어갔다.
보완 뒤 native/API·guards·cold Review·UI·late/late-peer가 통과했다. 개발 증거는 최종43단계에 재사용하지 않았다.

관리 ZIP/index·직전 evidence는 read-only FD별 cache 조언 전후 SHA·크기·inode/mode/mtime을
확인했고 준비 프로세스의 사용하지 않는 heap만 반환했다. 전체 cache·다른 프로세스·데이터·
예산을 바꾸지 않았다. 최종 launcher도 같은 자기 heap 반환/preflight/worker 예산을 유지했다.
원래 최종 preflight SHA `51c0e5652b15eb1e8719d40cca9374fe16784738afc92b2f70ff29d97c93b85d`는 수집 과정에서 그대로였다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 1b8a51a2512879db9869f312a32fca99e0a563ab | fac87b8f3ce2ef420636b0d326d4c4b92b35dfe14bb5711a4ed14452b3093db1 | 53,871,283 |
| rollback | 98ff546e6469f7487f8ff9bb789b425a7a5257bb | befb0302f700dfcc8c4d0c6fe53c30919000234e7e57f58a05b45039a824cecf | 53,867,862 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/a352aedffc9244d5a781980d05898be9.json`, evidence `fa7041f40e888c101059afd5699e64b2399198ea151752ac452b7d974b25d798` (8,393,359B).
개발 evidence `561c027fac9511acef7ec05a08fbe8a14f3dfca52f26da180c70f9ce335c3f1e` (3,430,367B).
양쪽 manifest와 보관 ZIP2개를 재검증했다. 시작 index `b7c786be1e2582356af5f2faf2c41ebe52420a1c08f904c7b9756e9c035f02dd`,
종료 sidecar `8202bec4a3553483e2b12fbbadd2d5c9d2c2e9dc1f56ff51e8eb5f1a6433abf9`. 승인된 두 세대 보관에서 이전 rollback
`4f3aa92f82a72e3395204310c8b1b8dc506c882e`의 관리 ZIP만 교체했다. 과거 evidence·사용자 원본·이전 checkout은
보존했다. 이번 개발/최종 RAM workspace만 identity·봉인 뒤 정리했고 재생성 출력 해시,
fixture 원문·checkpoint·실패/실행 로그·화면은 보존했다.

시작 여유 25,701,429,248B, 마감 25,684,443,136B(23.9205GiB), 순증가 16,986,112B.
최대 cgroup 전체 memory 9,506,045,952B, 최종 stage 최소 디스크 25,695,719,424B.
추가 cgroup9GiB+안전1GiB·RAM 임시파일4GiB+파일시스템 여유512MiB·디스크 안전64MiB·
개발 evidence256MiB/최종512MiB의 기존 예산을 유지했다.

정보·참조 핀은 **정보 정의마다 별도의 C# 구조체 타입을 생성한다**는 사용자 결정을
반영했다. 공통 값/참조 타입과의 선택은 답변 대기가 아니다. 이 단위는 타입 생성·참조
수명·스키마 변경/구 reader 호환의 세부 정책을 구현하거나 임의 확정하지 않는다.
기존 identity/group backend·종류 CLR/사용 중 삭제 대응과 다른 고정 잔여는 별도다.
상태 조회 중 환경 starting 알림과 호출 중단이 있었다. 대기 도구는 ready를 반환했고,
실제 read-only 명령으로 같은 HEAD·clean tree·기존 launcher/worker와 진행 기록을 확인했다.
옛 제어 세션92668은 Unknown process id를 반환했으므로 원래 검사를 재시작하지 않고
record/실제 프로세스로 확인을 이어갔다. environment-observation.json을 최종 evidence에
보존했다. 이 알림만으로 제품 결함이나 초기 빈 화면 원인을 확정하지 않는다.
구 reader는 확장된 copy read scope를 거절할 수 있으며 자동 마이그레이션은 없다.
닫힌 M11/M12/M4와 초기 빈 화면의 모든 원인을 이 단위로 재판정하지 않는다.
실행 검증은 Linux native·Chromium 격리 fixture다. 실제 Windows/WebView2·모바일·물리
IME/GPU/audio·사용자 프로젝트·전체 UI, Space/Library 전달 및 모든 구 reader checkpoint
교환은 미검증이다. 교차 패키지는 실제 Windows 실행이 아니다. 초기 빈 화면과 과거
Save 요청 미발행의 모든 간헐 원인은 계속 미확정이다.
