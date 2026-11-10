# 단일 복합 정보 구조체 검증

최종 runtime `c6b3449acd6febb8ab5eb2fe75b17da65308fa49`의 **신규44단계·재사용0**을 통과했다.
LF16·CRLF19·프로세스 수명1·새 패키지/전체 복원/실패 수명8이다.
[원본 근거·지원/제한](V666_INFORMATION_COMPOUND.md)을 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 |116ccecd는 실제 Root/Mid/Leaf 값 포함의 generated struct 질의와 native build를 INFORMATION_CLR_FIELD로 거절. 원문 보존 |
| 값 생성/실행 | Root/상속 타입 서명만 선택해도 전체 자식 closure를 생성. 3단계 값 복사·상속 복합·C# 키워드·exact64·CRLF/Unicode·실제37 실행 |
| 호환 | 같은 Leaf의 primitive v1 profile·shape hash·source를 실제 이전 게시본 descriptor와 대조. 변경 없음. 기존 기본형 native 전체 회귀도 최종 LF/CRLF에서 새로 실행 |
| 무효화 | 깊은 자식의 표시명 변경은 상위 shape/함수 계약 유지. 자식 필드 추가는 Root shape·타입 DLL·함수 계약 갱신. 삭제로 불호환인 원래 C#은 오류. 정확 복구 뒤 원래 key/실행 회복 |
| 경계/권한 | 값 포함 cycle·reference·종류·multiple은 자동 snapshot/숫자 변환 없이 거절. 등록 자식 dependency 누락 거절. 명시 dependency·명시 initializer 대응 뒤 별도 pack DLL/전이 참조로37 실행. 외부 원문 불변 |
| CAS | 자식만 snapshot 뒤/Review 뒤 long→int로 변경. Root 선언/CLR 이름이 같아도 Save/Confirm 거절, peer/checkpoint/두 정보 source guard 유지. 정확 복구·cold·새 Review/Confirm 뒤 실제31 |
| 실제 UI | 기존460px 창·구현 선택·C# editor의 취소·Undo/Redo·미저장/저장 cold·저장 실패 입력 보존/재시도·명시 discard. 새 입력 없는 Save는 비활성 |
| 회귀 | 기존 scalar 정보의 API/CAS와 여러 native 본문/소유 copy·legacy bool/Result·실패/응답 유실·실제 conflict·늦은 입력을 최종 코드에서 새로 실행 |
| 패키지/복원 | 독립 LF/CRLF·HOME/NuGet·Release/MCP·빈 engine cache. 새 Windows 교차 패키지 구조/무결성과 포함 Linux 엔진의 compound UI. ZIP CRC/SHA/mode 전체 복원 뒤 자식 CAS·deep value 실행·응답 유실·실패 수명 통과 |

개발14단계 전부 통과, 개발 실패0이다. 개발 증거를 최종44단계에 재사용하지 않았다.
후보 compiler와 실제 generator가 같은 정보 closure를 사용하며 원본 C#·public 계약·소유·
권한·override와 원래 source hash/CAS·Review/Confirm을 유지한다. 등록/부모 원본 쓰기나
기존 저장 데이터/서명/바이너리의 자동 migration은 없다. 참조를 값 복사로 바꾸지 않는다.
타입 선택 UI는 이번 단위에서 수정하지 않았다. parser 문법은 추가하지 않았으며
직전 정보 v1 compiler의 거절과 첫 struct 이전 parser의 TYPE 거절을 구별한다.
모든 구 reader 교환과 DLL hot replacement는 미검증이다.

사용자 후속 결정은 **종류는 C# enum, 모듈은 C# interface**다. 표현 선택은 답변 대기가
아니다. 결정이 runtime freeze 뒤 도착했으므로 이 checkpoint 제품은 compound 값만
구현하며, 마감 문서/잔여 목록에 결정을 반영한다. 종류의 기존 member ID와 이름·순서
변경 안정성을 숫자 연결에서도 유지해야 한다. 원본은 ID/name만 생성하며 index+1은
표시용이다. 행 순서를 숫자 ABI로 재해석하거나 기존 값을 바꾸지 않는다. enum/module
네이티브 표현과 타입 선택 UI·참조 접근 연결은 같은 고정9행 후속이며 새 필수 조합으로
늘리지 않는다. 이 결정 때문에 진행 중인 compound 검사를 중단/중복하지 않았다.

검증기가 해시를 읽은 공개 SDK/NuGet 파일의 해당 read-only FD에만 cache 조언을 하고
inode/크기/mode/mtime과 tree SHA를 확인했다. 기존 관리 ZIP/index/evidence에도 동일한
읽기 전용 확인만 했다. 전역 cache·다른 프로세스·파일/SDK/의존성 내용·예산은 바꾸지
않았다. preflight memoryCurrent 5,662,670,848B, SHA
`ef2892d4425e7b7f8d88f0ec092083c0aa3dacaba0e3a542beb717eec7889d36`이며 수집 중 그대로였다. 입력 cache 증거는 고정 SDK/seed
root·tree SHA/count/bytes/불변 flag만 포함한다. 개발 copy는 직전 실제 최종 증거와도
byte-identical임을 별도 note로 확인했고, 후속 수집은 development filename으로 분리했다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | c6b3449acd6febb8ab5eb2fe75b17da65308fa49 | 7b4ec88525c7f91dfb84580a822430ed847eee541e5998f3f8c3cc2fba11e6d9 | 53,923,735 |
| rollback | bc5433d49ba853635d51d823b958e328323f0868 | 1aaf48eff5922e48e1c2fdafd2659d5a6c6f93d5ab1a0ee06af7f3b70ca08cca | 53,907,366 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/e028e13aad6c4704954661e7b8169978.json`, evidence `d97573c0d029119216b158a1fae2c49cb310af77bb8fad5e37c2da8e8b71dddf` (4,994,636B).
개발 evidence `900b629f0e66083ad39fe1836e1b9d2102299477814e5e383e37e4719fef2b21` (1,378,818B).
양쪽 manifest와 보관 ZIP2개를 재검증했다. 시작 index `25475d6f60d4435d1d837fbbc31bae71955857fb4f070b90563dc01cceb089d3`,
종료 sidecar `0b1539f4458f2126981d8f8e9508132b285f3b55855617fed1a67dd78420670c`. 승인된 두 세대에서 이전 rollback
`1b8a51a2512879db9869f312a32fca99e0a563ab`의 관리 ZIP만 교체했다. 과거 evidence·사용자 원본·이전 checkout은
보존했다. 이번 개발/최종 RAM workspace만 identity·봉인 뒤 정리했고 재생성 출력 해시,
fixture 원문·checkpoint·실패/실행 로그·화면은 보존했다.

시작 여유 25,672,159,232B, 마감 25,661,026,304B(23.8987GiB), 순증가 11,132,928B.
최대 cgroup 전체 memory 8,909,676,544B, 최종 stage 최소 디스크 25,668,796,416B.
추가 cgroup9GiB+안전1GiB·RAM 임시파일4GiB+파일시스템 여유512MiB·디스크 안전64MiB·
개발 evidence256MiB/최종512MiB의 기존 예산을 유지했다.

M11/M12/M4는 새 회귀 없이 재개하지 않는다. 초기 빈 화면 원인은 미확정이다. Linux
native/Chromium 격리 fixture·교차 패키지와 실제 Windows/WebView2·모바일·물리
GPU/audio/IME·사용자 프로젝트·전체 UI/Library 전달 검증을 구분하며 후자는 미실행이다.
