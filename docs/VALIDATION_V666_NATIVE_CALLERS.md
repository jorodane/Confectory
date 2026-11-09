# 여러 본문 그룹의 C# 호출자 보존 검증

최종 runtime `6a9b48d2af44eb4fa0227d80b164c24f17bcd164`의 **신규41단계·재사용0**을 통과했다. 분포 `{"lf": 17, "crlf": 16, "windows": 2, "restored": 3, "packaged": 1, "package": 1, "native": 1}`.
[원래 수용 근거·지원·호환 경계](V666_NATIVE_CALLERS.md)를 따른다.

| 범위 | 실제 결과 |
|---|---|
| 변경 전 재현 | 각 body 단일 후보는 유효하고 원래 C# 호출자의 실제 프로그램은46 반환. 두 본문 그룹은 native caller 제한으로만 거절. 원래 ‘구현 선택’의 callee target을 명시한 UI에서도 그룹 Save 거절·두 입력 보존 확인 |
| 후보 | public/native 계약·target·typed import·First/Second 별칭·left/right C# 매개변수·원래 hash를 유지해 두 명시 본문만 linked update로 합성. 역순 후보 동일하고 native/Blueprint caller 원문은 그대로 |
| 정상 UI | 원본 정보 화면/독립 창의 명시 구현 선택·코드 편집 취소·private Undo/Redo·미저장 cold·한 Save·저장 cold·Review 거절·Confirm 및 실제 C# caller 실행26 확인 |
| 저장 수명 | checkpoint 실패는 전체 미적용·입력 보존 후 재시도, 응답 유실/결과 조회 유실 뒤 cold는 저장된 receipt를 확인해 중복 적용 없음. peer 충돌·프로젝트 왕복·취소도 새로 확인 |
| 읽기 CAS | import 없는 leaf여도 native caller 선언/header/body를 version3 readGuards에 보존. Save 전 caller 변경 거절. Save 뒤 헤더 변경+ cold Review 거절 시 원래 receipt·두 본문·peer 유지, 정확한 복구 뒤 새 Review 허용 |
| 최종 CAS | Review 뒤 caller header/C# body/함수 선언 각각 변경하면 sourceConfirmed=false·두 본문 미적용·checkpoint 전체 바이트/peer 보존. cold 재시도는 원래 receipt 유지. 복구 후 명시 Review/Confirm·실행20, caller3파일 bytes/inode/mode/mtime 동일 |
| 거절/호환 | caller body snapshot 누락·stale typed import·부모/foreign caller·caller 편집 계획 5개 거절, native caller receipt 누락·해시 형식/경로/소유자/버전 등7개 변조 거절. 기존 native import 그룹 회귀 통과. 구 leaf/ordinary Blueprint caller 빈 readGuards는 cold/Review/Confirm·실행20 통과 |
| 최종 독립/패키지 | LF/CRLF no-hardlinks checkout·독립 HOME/NuGet·Release/MCP·빈 engine cache에서 새로 실행. 새 Windows 교차 패키지 구조/해시·포함 Linux engine 정상 UI·전체 ZIP CRC/SHA/파일/디렉터리 mode 복원·복원 CAS/응답 유실·실패 수명관리 통과 |

제품 변경은3파일이다. frontend/HTML/CSS/JS·구현 선택 UI·공개 ABI·code generation·
기존 source compiler/권한·Save receipt version·최종 source lease는 그대로다. 새 해석,
자동 C# 변환, override 계약 변경이나 권한 grant는 없다. 관련 새 흐름은 직접 소유
caller 원문 유지이며 모든 native/copy/외부 조합의 편집 지원을 뜻하지 않는다.

개발은26단계 중24통과·2실패다. 첫 UI 실패는 C# caller가 추가한 기존 구현 선택을
상속된 검사 코드가 처리하지 않아 editor를 기다린 시간 초과였다. 제품을 고치기 전에
이 단위 fixture에서 정확한 callee target 선택만 추가하고 UI 거절 재현을 통과했다.
두 번째는 충돌 시 Save 뒤 applySlots 요청/경계 안내가 관측되지 않은 시간 초과다.
그 시점의 pending2·요청/응답·화면을 보존했다. 동일 조건의 비변경 클릭 관측 재검사와
최종 새 conflict 검사는 통과했지만 **처음 요청 미발행의 원인은 미확정**이다. 이를 제품
수정으로 해결했다고 표현하지 않는다. 오류를 통과로 합산하지 않고 raw 실패/수정 전
fixture를 보관했다. 최종41단계는 최종 제품/검사로 모두 새로 실행했다.

초기 메모리 사전검사는6,485,225,472B와6,444,830,720B에서 거절됐고 어떤 빌드도
시작하지 않았다. 동일 보관 ZIP의 read-only FD/hash/inode/size/mode/mtime 불변을
확인하는 개별 file cache advice 뒤6,391,140,352B에서 통과했다. 예산을 낮추거나
파일·전역 캐시를 지우지 않았다. 이후 연결 해제 때 apply_patch는 첫 파일 읽기에서
exec-server transport closed로 실패했다. connected/running 표시와 실제 명령 불가를
구분했고, 실제 재연결 읽기에서 HEAD/미커밋3테스트·제품 diff 없음·기존 작업의 완료
로그/PID start·자식 회수를 확인한 뒤 정상 patch를 적용했다. 새 환경/중복 빌드는 없었다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 6a9b48d2af44eb4fa0227d80b164c24f17bcd164 | e7fd42884d7a717898bcdd979e065feb9679e26eba29ce703cda29ea9dbfe479 | 53,860,812 |
| rollback | 2897f3709cd44cf10c954ed9dd6a578dd421ec3d | 6cfb44aec836c6f235b40ac705f92f9ac0f64deb590367b91bcabdeb11582a8c | 53,860,668 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/998644d087604a14b7612040882a8633.json`, evidence `5c2f5a790f417dc80682d4439db3c36590ef0bba1160c8dd642c7d18b9e3191d` (7,897,196B).
개발 evidence `448a0d7bb3a705398b1bac71f079f4e2428507e00bc981a562b264f7c9f4c99e` (7,287,432B).
양쪽 evidence manifest와 보관 ZIP2개를 재검증했다. 시작 index `8b9a320f89530b3daf34b6b9ad79ac1ee1cfa3e2dd7e0bf0e721da91e916c29a`,
종료 sidecar `f3d0fe0b267cb538b137523324520475b69f70964bf8bc95d087d1d1f5ee0242`. 최종 preflight 원본을 덮어쓰지 않고 개발 사전검사·연결/캐시
증거·실패를 별도 이름으로 보존했다.

latest/rollback 두 ZIP만 승인된 관리 절차로 교대했다. 기존 rollback
`fe3d35dd441a1dccc5ca7d9b3bb6e14eb25b0e3d`의 관리 ZIP만 교체했고 과거 증거·사용자 데이터·원본 checkout은
유지했다. 개발/최종 RAM 작업공간은 evidence 봉인 후 소유 identity를 확인해 정리했다.
이 단위의 새 owned bytecode만 해시 기록 뒤 제거했다. 재생성 build outputs는 정확한
파일 해시 목록으로, 원문·checkpoint·실패 로그/화면은 archive에 보존했다.

단위 시작 여유 25,856,049,152B, 마감 25,836,716,032B(24.0623GiB), 순증가
19,333,120B(18.4375MiB). 관측 최대 cgroup memory 9,350,983,680B,
최종 stage 최소 디스크 25,844,809,728B다. 추가9GiB+safety1GiB·RAM4GiB+
reserve512MiB·최종 evidence512MiB의 기존 예산은 유지했다.

copy/상속/등록·private/whole/wrapper·계약 변경의 실제 영향 closure와 고급 타입/핀
표시명은 기존7/8/9행 잔여다. 실제 identity/group backend·종류 CLR/사용 중 삭제의
미결 정책은 임의 확정하지 않는다. 닫힌 M11/M12/M4를 회귀 없이 다시 열지 않는다.
frontend의 기존 late-input 보호는 동일 소스이며 별도 늦은 입력 행렬 전체를 이번에
새로 실행한 것은 아니다.

실제 검증은 Linux native engine·Chromium·생성한 격리 fixture다. Windows 교차
패키지는 실제 Windows/WebView2 실행이 아니다. 모바일·물리 IME/GPU/audio·사용자
프로젝트·전체 UI·Space/Library 전달은 미검증이며 초기 빈 화면 원인도 미확정이다.
