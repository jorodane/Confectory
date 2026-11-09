# 여러 본문 저장과 기존 호출 후처리 검증

최종 runtime `98ff546e6469f7487f8ff9bb789b425a7a5257bb`의 **신규43단계·재사용0**을 통과했다.
LF18·CRLF17·프로세스 수명1·새 패키지/전체 복원/실패 수명7이다.
[원본 근거와 지원 경계](V666_RETAINED_WRAPPERS.md)를 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 | 두 native 본문의 단일 후보와 원래 wrapper 프로그램42는 유효. 기존 구현 선택창에서 실제 callee 본문을 각각 선택한 뒤 공동 후보/UI Save만 거절. 원본·checkpoint·입력 보존 |
| 후보/원문 | 후보 순서를 바꿔도 동일. serial After/source/helpers·enum wrapper와 native-return 매핑·출력 공개·ID17/-3·실행 연결·정확64 fallback·호출자 graph 원문을 새 쓰기로 만들지 않음 |
| 검증/거절 | 낡은 wrapper hash·빠진 매핑·변경된 공개 출력·잘못된 enum ID/값·control/mode·임의 OriginalExecution·C# 반환 타입 오류9개를 전체 거절. 기존 typed graph·원래 publication 증거와 전체 조립 C# 컴파일 유지 |
| Save/CAS | code/locals/private graph 없이 wrapper만 있어도 원문 전체 readGuards 결부. Save 전 header 및 Review 후 caller header·Main C#·After/enum graph·선택 함수의 출력 공개 변경을 각각 최종 Confirm에서 거절. checkpoint·peer·두 본문 입력 보존 |
| 복구/실행 | 정확 복구·cold·새 Review/Confirm 뒤 실제29. 기존 serial After 계산과 native return22를 같은 원래 negative-3 분기로 전달해7을 더함. native 값과 실행 enum을 cast/치환하지 않음 |
| 원본/계약 | 읽기 전용 caller header·Main·graph의 bytes/inode/mode/mtime 보존. 선택 함수 선언은 명시한 빈 설명을 정상 저장하며 signature·publication values/provider 관계는 원래대로 유지 |
| cold/증거 | 후처리가 제거된 peer graph는 원래 receipt를 재기준화하지 않고 cold Review 거절. 정확 복구 후 원래 receipt로 재검토. readGuards 누락/hash/path/owner/version 변조7개 거절 |
| UI/수명 | 기존 구현 선택창·460px 기본/독립 화면에서 취소·명시 본문 편집·Undo/Redo·미저장/저장 cold·Review 취소/Confirm. 저장 실패 재시도·응답/조회 유실·stale 활성화·프로젝트 전환·취소와 late 입력 보존 통과 |
| 이전 기능 | 최종 코드에서 기존 중첩 후보/거절·네 common/Linux target 후보/거절·native caller CAS·ordinary bool/Result caller·단일 target/빈 guard 기록을 새로 검증 |
| 패키지/복원 | 독립 LF/CRLF·HOME/NuGet·Release/MCP·빈 engine cache. 새 Windows 교차 패키지 구조/무결성·포함 Linux 엔진 UI, ZIP CRC/SHA·파일/디렉터리 mode 전체 복원 및 복원본 CAS/응답 유실·실패 수명관리 통과 |

제품3파일은 같은 계약 본문 그룹의 기존 wrapper를 수용하고, wrapper 원문을 전체
관측/CAS와 조립 C# 검증에 연결한다. 변경 없는 source·helpers·contract hash와 graph
바이트는 그대로이며 새 receipt 문법/native ABI/권한·UI 배치는 없다. 기존64-member Review·
240 read/write·2048 known unit과 Tree 예산을 유지한다. 새 후처리 생성/계약 변경을
자동 승인하지 않으며 기존 `OriginalResult.NoBranch`를 공개 실행 결과로 추측하지 않는다.
다른 실제 public/native ABI·copy/whole/forwarding source closure는 기존7/8행의 같은
잔여다. 일반 입력/out 표시명과 고급 정보·참조 타입은9행이다. 조합별 새 의무를 만들지 않는다.

개발16회 중15통과·1실패였다. 실패 검사는 모든 CAS 거절·정확 복구·실행29까지 통과한
뒤 선택 함수 선언에도 읽기 전용 파일의 불변 bytes/inode/mtime을 요구했다. 실제 후보에는
요청한 빈 설명이 들어가 있어 그 선언은 원래 쓰기 대상이었다. 입력·원문·실행 코드·
로그와 `selected-declaration-diagnostic.json`을 보존했다. 검사를 readonly caller와
선택 선언의 값/provider/signature 보존으로 나눴으며 제품 코드는 바꾸지 않았다.
이후 API·guards·cold Review·UI·late Save를 통과했다. 개발 결과는 최종43단계에 재사용하지 않았다.

관리 ZIP/index의 SHA·크기·inode/mode/mtime을 확인한 read-only FD별 cache 조언과
준비 프로세스의 사용하지 않는 heap 반환만 사용했다. 전체 cache·다른 프로세스·데이터·
예산은 바꾸지 않았다. 최종 launcher도 동일 자기 heap 반환·preflight/worker 예산과
실제 cgroup 계측을 유지했다. 원래 최종 preflight SHA
`dfa97238c5cb5dfcd1e3d87cf0bc24d26e9b9af8c6fc3346a7820e0cc2a93cfb`는 수집 과정에서 그대로였다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 98ff546e6469f7487f8ff9bb789b425a7a5257bb | befb0302f700dfcc8c4d0c6fe53c30919000234e7e57f58a05b45039a824cecf | 53,867,862 |
| rollback | 4f3aa92f82a72e3395204310c8b1b8dc506c882e | 6a533e1b13ce414ff9eff6c661664a340e0c33efcda74346bfbe2458ab118c29 | 53,867,903 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/4b2981d2d70b452e81e093a5e9fc793f.json`, evidence `320e93557681dd283722fa8a74bc58aafd9c3c9a61a308d57d4eb413bfd61185` (8,342,302B).
개발 evidence `eaac0d739395b55e9ac040b037ff4de9c7ba826907c7d95544b45e84c150454e` (2,855,093B).
양쪽 manifest와 보관 ZIP2개를 재검증했다. 시작 index `f0863b19d60d5c519de10d1518c46ff99fcb3cc08e74cdb8d746d1519df4db09`,
종료 sidecar `b7c786be1e2582356af5f2faf2c41ebe52420a1c08f904c7b9756e9c035f02dd`. 승인된 두 세대 보관에서 이전 rollback
`b44470af6a44b5a9f660c573492774ddee51f990`의 관리 ZIP만 교체했다. 과거 evidence·사용자 원본·이전 checkout은
보존했다. 이번 개발/최종 RAM workspace만 identity·봉인 뒤 정리했고 재생성 출력 해시
목록과 fixture 원문·checkpoint·실패/실행 로그·화면은 남겼다.

시작 여유 25,717,735,424B, 마감 25,701,572,608B(23.9365GiB), 순증가 16,162,816B.
최대 cgroup 전체 memory 9,738,018,816B, 최종 stage 최소 디스크 25,712,783,360B.
추가 cgroup9GiB+안전1GiB·RAM 임시파일4GiB+파일시스템 여유512MiB·디스크 안전64MiB·
개발 evidence256MiB/최종512MiB의 기존 예산을 유지했다.

고급 정보·참조 핀의 공통 값/참조 CLR 대 정보별 생성 타입은 답변 대기다. 기존
신원/그룹 backend·종류 CLR/사용 중 삭제 정책과 다른 고정 잔여도 임의 확정하지 않았다.
닫힌 M11/M12/M4·초기 빈 화면의 모든 원인을 이 단위로 재판정하지 않는다.
실행 검증은 Linux native·Chromium 격리 fixture다. 실제 Windows/WebView2·모바일·물리
IME/GPU/audio·사용자 프로젝트·전체 UI, Space/Library 전달 및 모든 구 reader와의
checkpoint 교환은 미검증이다. 교차 패키지는 실제 Windows 실행이 아니다.
초기 빈 화면 및 과거 Save 요청 미발행의 모든 간헐 원인은 계속 미확정이다.
