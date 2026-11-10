# 모듈 nominal 요구 계약 검증

최종 runtime `24d9493dc6924d866dcc42c217dc71c89b402595`의 **신규22단계·동등 증거 재사용23, 유효45단계**가 통과했다.
전체 수용은 LF17·CRLF18·소유 프로세스 수명1·패키지/전체 복원/실패 수명9이다.
LF/CRLF의 clone/checkout/restore/Release/MCP/engine12·프로세스 수명1·새 패키지/전체
복원/실패 수명9는 모두 신규이며 나머지23 검사는 같은 제품/호출/의존성의 봉인 증거다.
[원본 근거·실제 지원/제한](V666_MODULE_NOMINAL.md)을 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 | bafdbb35가 정보/enum 요구 메서드를 MODULE_CLR_PROFILE로 거절. 원래 source/C# 보존. 실제 기본형 module descriptor를 고정 fixture로 보존 |
| 생성·실행 | 상속 요구 함수가 복합 struct 입력/반환과 enum out을 그대로 투영. exact64 값·실제 interface 호출37. 다른 interface의 입력/반환도 실제 실행. default는 실행되면 throw하는 원문이며 실행되지 않음 |
| 호환·무효화 | 기본형 module source/profile/shape/methods가 게시본과 byte-for-byte 동일. 표시명 변경은 모듈 shape/함수 계약 유지. 깊은 정보 필드 추가는 모듈·소비자 산출물 갱신. 정확 복원 뒤 원래 key/실행 복구 |
| 등록/권한 | 모듈/값2팩의 타입 DLL과 전체 전이 ref를 compile/link하고 실제37. 외부 원문 불변. 참조된 interface 모듈의 require가 dependency 없이 프로젝트 함수로 역접근하면 UNDECLARED_DEPENDENCY. 등록 자체를 grant로 바꾸지 않음 |
| CAS | root module/CLR 이름은 같은 상태에서 깊은 Leaf만 long→int로 변경. 관측 뒤 Save·Review 뒤 Confirm 거절, peer/checkpoint/input 보존. 전체 모듈/요구 함수/enum/정보 source guards 유지. 정확 복원·cold·새 Review/Confirm 뒤 실제31 |
| UI | 기존460px C# body editor·본문 취소·Undo/Redo·미저장/저장 cold·저장 실패 입력 보존/재시도·명시 discard. 새 입력 없는 중복 Save는 비활성. 원래 배치/계약 유지 |
| 회귀 | 기존 모듈/default/실행 분기 enum 계약과 실제 basic enum/interface 생성·호출. basic module·scalar/compound 정보·enum의 기존 API/CAS. 소유 copy의 응답 유실·실제 conflict·늦은 입력과 공통 혼합/헤더 저장을 최종 제품과 동등한 봉인 증거로 재사용 |
| 패키지 | 독립 LF/CRLF checkout/HOME/NuGet·Release/MCP·빈 engine cache. 새 Windows 교차 패키지 구조/무결성, 포함 Linux 엔진의 모듈 method 값 UI. ZIP 전체 추출 후 native37·깊은 타입 CAS/실제31·UI 저장 실패/cold·응답 유실·실패 수명 검사 |

개발19단계 전부 통과·실패0이다. 개발 증거를 수용 단계에 재사용하지 않았다. 첫 후보
f386486a는41단계 중40통과 후 복원 native 비교에서 test fixture를 application content의
tests 폴더에서 찾지 못했다. 실제 nominal 실행/변경/복구5개 검사는 통과했고 경로 읽기만
실패했다. 제품2파일과 oracle JSON은 그대로다. 실행 테스트 checkout의 fixture 경로로만
수정하고 Git diff/AST·제품/SDK/seed identity·정규화 명령·기존 LF/CRLF checkout을 검증했다.
해당 두 native 명령에서는 새/옛 경로가 같은 파일이므로 이전 통과23개만 동등 재사용했다.
실패 단계·빌드·패키지·복원 검사는 재사용하지 않았다. 실패 증거
`9397942a593ce086ebcb579640e00907b8177e576ff3257fa0e79b4f579a4eac`와 각 reused result/정당화 proof를 보존했다. 이전 enum
UI·보관 전체 검사는 별도 게시본 기록의 범위이며 이번 신규 수에 합산하지 않았다.
사용자 C# 원문·ID·정확한 public/override 계약·권한·부모/외부 원본·Review/최종 CAS를
유지한다. 새 저장/parser 문법이나 서명/저장값/DLL의 자동 migration은 없다. 직전 reader는
nominal 모듈 생성을 거절한다. 첫 정보 type 이전 parser/enum v2의 구 reader 제한은 그대로다.
모듈 async/공개 실행 요구·선택 타입 순환/pack DLL 순환·CLR interface 상속/upcast는
현재 명시 지원 경계다. 타입 선택 UI 전체나 살아 있는 참조 접근을 완료로 세지 않는다.

공개 SDK/NuGet과 기존 관리 ZIP/index/evidence의 해시를 읽은 해당 read-only FD에만
cache 조언을 하고 inode/크기/mode/mtime 및 tree/archive SHA를 검증했다. 전역 cache·
다른 프로세스·파일 내용·예산은 바꾸지 않았다. 최종 preflight memoryCurrent
5,676,486,656B, SHA `bb8e8d506827f3ba03cd819353b597e785fc57326d70f2db45ba154d4d6bea29`는 수집 중 그대로였다.
개발 input/preflight 증거는 development 이름으로 분리해 최종 증거를 덮어쓰지 않았다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 24d9493dc6924d866dcc42c217dc71c89b402595 | 7308bbf4fab52a4d719480523e1321b74d4694448f07a3e3a0c226a10e73eacb | 53,959,822 |
| rollback | 93009353073720d600f06b75b6a54bb6861f9564 | 96fd09dc5a81e2879ea8f0388fc842dc38ccdacbc25cdf92a6003804483d982a | 53,953,531 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/9b13cf8e9d854a8eb72a12e2a14cb02a.json`, evidence `323a0cd36cd0fee87199074fffc03d64353d1d76bfc8b34035d59445ee1334b0` (2,488,899B).
개발 evidence `cc95fbb45219b2ae69059f0b42f372a4da2c931dab264acfa057e21224184ea7` (1,731,935B).
manifest3개와 보관 ZIP2개를 재검증했다. 시작 index `312041e5f7ca868bff32d6eb1888078fc4cde31fc31b914d3b9ea39da3a1a7b1`,
종료 sidecar `9d004d9b972680d9ab8020bc9a5417914444f0c90c21c8830f94158090c194c2`. 승인된 두 세대에서 이전 rollback
`c6b3449acd6febb8ab5eb2fe75b17da65308fa49`의 관리 ZIP만 교체했다. 과거 evidence·사용자 원본·이전 checkout은
보존했다. 이번 개발/최종 RAM workspace만 identity·봉인 뒤 정리했다.

시작 여유 25,646,895,104B, 마감 25,631,834,112B(23.8715GiB), 순증가 15,060,992B.
최대 cgroup 전체 memory 9,060,732,928B, 최종 stage 최소 디스크 25,636,610,048B.
기존 추가 cgroup9GiB+안전1GiB·RAM 임시파일4GiB+여유512MiB·디스크 안전64MiB·개발
증거256MiB/최종512MiB 예산을 유지했다. 실제 Windows/WebView2·모바일·물리 GPU/audio/
IME·사용자 프로젝트·전체 UI는 미실행이다. 초기 빈 화면 원인은 미확정이다.
