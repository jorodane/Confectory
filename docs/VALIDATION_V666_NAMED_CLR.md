# 종류 enum·모듈 interface 검증

최종 runtime `93009353073720d600f06b75b6a54bb6861f9564`의 **신규47단계·재사용0**이 통과했다.
LF17·CRLF19·소유 프로세스 수명1·새 패키지/전체 복원/실패 수명10이다.
[원본 근거·실제 지원/제한](V666_NAMED_CLR.md)을 따른다.

| 범위 | 실제 결과 |
|---|---|
| 구 게시본 | 346b4e9c의 native enum/interface 타입 선택을 INFORMATION_CLR_TYPE으로 거절. 항목/정보/함수/C# 원문 보존 |
| 생성·실행 | 실제 public enum(int), 0 미선택, 비순서 번호12/43, ID 변환, 단일 enum 필드·정확64비트 값·C# 입출력. 실제 모듈 interface 구현과 호출 결과37. default provider는 실행되면 throw하는 원문 그대로이며 실행 안 됨 |
| 안정성·거절 | 이름/순서 변경은 번호·C# 심볼·shape/함수 계약 유지. 추가 시 의존 계약 갱신. 삭제 ID/숫자·중복/0/소수/누락 대응표·잘못된 모듈 요구 계약 거절. 정확 복원 뒤 원래 key/실행 회복 |
| UI | 명시 숫자 계약 준비·private Undo/Redo·미저장 cold·임시 저장/cold·compiler Review/Confirm. 저장 실패 후 입력/cold/원본 유지·재시도, 명시 취소/cold. 기본/독립 창에서 기존 선택 ID와 소비자 원문 보존 |
| Save/Confirm CAS | enum 숫자 source 변경과 모듈의 부모만 변경한 경우 각각 관측 뒤 Save·Review 뒤 Confirm 거절. 원래 body/peer/checkpoint/전이 read guard 유지. 정확 복구·cold·새 Review/Confirm 뒤 실제31 |
| 회귀 | 기존 module/default 계약과 실행 분기 enum·종류 ID 값 검사10개. 기존 종류 행/이미지/순서/삭제/Review, 선택값의 늦은 입력·정의 보관 응답 유실, compound native/scalar CAS, 소유 copy의 실제 충돌·응답 유실·늦은 입력, 공통 혼합/헤더 원자 저장을 최종 코드에서 새로 실행 |
| 패키지 | 독립 LF/CRLF checkout/HOME/NuGet/Release/MCP/빈 engine cache. 새 Windows 교차 패키지 구조/무결성, 포함 Linux 엔진의 준비 UI. ZIP 전체 추출 후 enum/interface native 실행과 두 source CAS, 독립 창 저장 실패/재시작·응답 유실·실패 수명 검사 |

개발26시도 중24통과·2실패 후 수정이다. 첫 UI 시작은 갱신 누락된 pinned resource 크기/
해시로 거절됐다. 두 번째는 enum-native의 공통 receipt adapter 누락으로 Save 요청 자체가
발행되지 않았다. 각각 원인을 수정하고 이후 기존 UI와 새 준비 normal/storage/cancel,
최종 UI를 통과했다. 실패 fixture·로그·수정 전 파일은 개발 증거에 보존했다. 이 두 건을
초기 빈 화면의 원인으로 일반화하지 않는다.

첫 최종 후보 f182442f는31단계 중30통과 후 CRLF 독립 창에서 enum-native 누락으로
서버가 저장을 거절했다. 소유/authorBinding·raw/slot 제한은 유지하며 해당 동작과 최대
헤더4항목만 연결했다. guard 재검증9시도 중8통과·1실패다. 실패는 모든 저장/확정 검사를
통과한 뒤 DOM 교체와 겹친 element screenshot이었다. viewport 캡처로 수정하고 실제
readOwnerEdits basis에서 오래된 창/다른 owner/raw/슬롯/관련 없는 동작을 거절하는
normal/storage/cancel 독립 창을 통과했다. 제품 결함과 캡처 fixture 실패를 구분한다.
개발/guard/첫 최종 후보의 통과 결과는 수정 후 최종47단계에 재사용하지 않았다.
첫 후보 증거 `c8508c0564040a1f583b9d17f399381cae5dde0a53b0755b40669a28f8bf38f5`, guard 증거 `fbba1dcc3730fa2e3150c8ffe2c1c86508b64a7ba2b3630990a25a9436c72836`도
manifest/무결성 검증 뒤 보존했다.

기존 선택값은 ID 문자열이며 숫자는 별도 명시 version 계약이다. 실제 enum 저장을
기존 실행 분기 Result enum과 혼동하지 않는다. 원문 C#·정보/모듈 ID·public/override
계약·소유·권한·등록/부모/외부 원본·Review→Confirm/최종 CAS를 보존했다. 기본형/복합
struct source와 타입 정체성도 유지한다. 새 parser 문법·자동 migration·implicit provider
선택/객체 생성·참조 snapshot·DLL hot replacement는 없다. 모듈 첫 interface의 동기
기본형/배열 제한과 타입 선택 UI/참조 접근 등 고정9행 잔여는 지원 문서에 명시했다.

검증기가 해시를 읽은 공개 SDK/NuGet과 기존 관리 ZIP/index/evidence의 해당 read-only
FD에만 cache 조언을 했으며 inode/크기/mode/mtime 및 tree/archive SHA를 검증했다.
전역 cache·다른 프로세스·파일 내용·예산은 바꾸지 않았다. 최종 preflight memoryCurrent
5,669,765,120B, SHA `e95b9535d18491633f77f9569566188afda189cb706b85b522f4a45a955b4f26`는 수집 중 그대로였다.
개발 input/preflight 증거는 development 이름으로 분리해 최종 증거를 덮어쓰지 않았다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 93009353073720d600f06b75b6a54bb6861f9564 | 96fd09dc5a81e2879ea8f0388fc842dc38ccdacbc25cdf92a6003804483d982a | 53,953,531 |
| rollback | c6b3449acd6febb8ab5eb2fe75b17da65308fa49 | 7b4ec88525c7f91dfb84580a822430ed847eee541e5998f3f8c3cc2fba11e6d9 | 53,923,735 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/3a1d1a3575214b3d94a12054a173b0b8.json`, evidence `d4c5ccffff66e278dba80f8eef8ace8d5df78caf4ab503e415109cdddfa9fae8` (4,272,824B).
개발 evidence `d05482088e8aea816f0acd75f6d96f3526a8b3666c1cc69bd58de4ae10fc520e` (1,326,422B).
manifest4개와 보관 ZIP2개를 재검증했다. 시작 index `0b1539f4458f2126981d8f8e9508132b285f3b55855617fed1a67dd78420670c`,
종료 sidecar `312041e5f7ca868bff32d6eb1888078fc4cde31fc31b914d3b9ea39da3a1a7b1`. 승인된 두 세대에서 이전 rollback
`bc5433d49ba853635d51d823b958e328323f0868`의 관리 ZIP만 교체했다. 과거 evidence·사용자 원본·이전 checkout은
보존했다. 이번 개발/최종 RAM workspace만 identity·봉인 뒤 정리했다.

시작 여유 25,660,878,848B, 마감 25,647,058,944B(23.8857GiB), 순증가 13,819,904B.
최대 cgroup 전체 memory 9,020,272,640B, 최종 stage 최소 디스크 25,654,042,624B.
추가 cgroup9GiB+안전1GiB·RAM 임시파일4GiB+여유512MiB·디스크 안전64MiB·개발
증거256MiB/최종512MiB의 기존 예산을 유지했다.

M11/M12/M4는 새 회귀 없이 재개하지 않는다. 초기 빈 화면 원인은 미확정이다. 실제
Windows/WebView2·모바일·물리 GPU/audio/IME·사용자 프로젝트·전체 UI는 미실행이며
Linux native/Chromium 격리 fixture·교차 패키지/복원 검사와 구별한다.
