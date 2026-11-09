# 정보 정의별 C# 구조체 기반 검증

최종 runtime `bc5433d49ba853635d51d823b958e328323f0868`의 **신규40단계·재사용0**을 통과했다.
LF14·CRLF17·프로세스 수명1·새 패키지/전체 복원/실패 수명8이다.
[원본 근거·정확한 지원 경계](V666_INFORMATION_STRUCTS.md)를 따른다.
제품9파일은 최초 `ea003e888346c0a5faa222ea74e060589dc1e04e` 이후 그대로이며,
후속 runtime 커밋은 검증기의 공개 입력 read cache 준비만 보완했다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 경계 | 기존 Parser는 생성 정보 타입의 native 함수 서명을 TYPE으로 거절. 원래 정보와 C# bytes 보존 |
| 생성/실행 | 정보 ID별 별도 struct와 pack type DLL/ref, 함수 interface/구현/최종 링크·catalog. 값 복사·같은 모양의 다른 ID·상속 유효 필드·빈 정보·키워드 @class·exact64·CRLF/Unicode를 실제 실행37로 검증 |
| 변경/호환 | 표시명 변경은 정체성/shape/함수 계약 산출물을 유지. 필드 추가는 정보·함수 산출물을 갱신. 불호환 필드 삭제/타입 변경은 C# 오류로 거절. 정확 복원은 원래 build key/실행 복구 |
| 거절/권한 | compound/reference/multiple/표현 불가 필드 ID·위조 generated type 거절. 등록 locator만 있고 dependency 없으면 거절. 명시 dependency로 외부 정보 DLL을 읽고 실행하며 외부 원문은 쓰지 않음 |
| 같은 계약 본문 | 관측한 정확한 정보 구조체로 단일 직접 소유 본문을 컴파일하고 원자 Save·version3 receipt/readGuards 유지. native schema 단위의 C# body와 ID/계약·나머지 원본 보존 |
| CAS | body snapshot 뒤 schema 변경은 Save 미적용. Review 후 long→int 변경은 CLR 이름이 같아도 Confirm 거절. checkpoint·peer 보존. 정확 복구/cold/새 Review/Confirm 뒤 실제 실행31 |
| 실제 UI | 원래460px 창·기존 구현 선택/C# editor에서 취소·Undo/Redo·미저장/저장 cold·저장 실패 입력 보존/재시도·명시 discard. 새 입력 없는 Save는 기존대로 비활성 |
| 회귀 | 기존 여러 native 본문/단독 배정 copy의 순수 후보·원자 저장/API, legacy bool/Result, 실패/응답 유실·conflict·늦은 입력을 최종 코드에서 새로 실행 |
| 패키지/복원 | 독립 LF/CRLF·HOME/NuGet·Release/MCP·빈 engine cache. 새 Windows 교차 패키지 구조/무결성·포함 Linux 엔진 UI. ZIP CRC/SHA·파일/디렉터리 mode 전체 복원 뒤 typed API/CAS·실제 struct 실행·응답 유실과 실패 수명 통과 |

개발27회 중22통과·실패5회다. 제품 실패1회는 readonly metadata 질의가 기본 Documents
cache의 빈 경로를 사용한 결함이었다. bounded/hash-observed read callback으로 보완하여
파일/cache를 쓰지 않는다. fixture 실패4회는 비동기 구현 선택창 대기 누락, 거절용 필드
loop 변수의 외부 fixture 재사용, DOM LF/원문 CRLF 좌표 혼동, 새 입력 없는 비활성 Save의
클릭 기대였다. 실행 코드·입력·원문·checkpoint·로그와 화면을 보존하고 검사만 보완했다.
이후 실제 UI 정상/저장 실패 재시도/취소를 통과했고 마지막 catalog에서 readonly 질의
전용 실행 플래그를 빼고 solution/MCP/editor/native/API를 다시 검사했다. 개발 증거를
최종40단계에 재사용하지 않았다.

최종 첫 호출의 잘못된 명명 인자는 parser에서 거절되어 검사가 시작되지 않았다.
그 다음 두 호출은 memoryCurrent6,462,980,096B/6,463,213,568B에서 기존 추가9GiB+
안전1GiB 사전검사로 차단되었으며 worker/workspace는 생성되지 않았다. 제품 결함으로
세지 않는다. 검증기가 해시를 계산한 SDK·공개 NuGet 입력의 해당 read-only FD에만
cache 조언을 하고 inode/크기/mode/mtime 불변과 tree SHA를 기록하도록 보완했다.
전역 cache·다른 프로세스·SDK/의존성 내용·예산을 바꾸지 않았다. 보완 후 최종 preflight
memoryCurrent 5,664,165,888B에서 같은 예산을 통과했다. 공개 입력 cache 증거,
원래 실패 로그와 최초 제품 freeze를 함께 봉인했다. 최종 preflight SHA
`f34ba14806f3eb5d91d7d523d21d237a1d4f5d15b72f619d633078d0ea140c76`는 수집 중 그대로였다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | bc5433d49ba853635d51d823b958e328323f0868 | 1aaf48eff5922e48e1c2fdafd2659d5a6c6f93d5ab1a0ee06af7f3b70ca08cca | 53,907,366 |
| rollback | 1b8a51a2512879db9869f312a32fca99e0a563ab | fac87b8f3ce2ef420636b0d326d4c4b92b35dfe14bb5711a4ed14452b3093db1 | 53,871,283 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/8d6c13beabfc4bc38785b5061be9a933.json`, evidence `4f38494604fc5a771d1dc1592b298936e57dc00871db4237dc835387edd9a26c` (4,808,974B).
개발 evidence `7c733f922ec688b0a828fd2d8233de3670f2e255ea6ebb7242481836fe15bcb3` (2,057,139B).
양쪽 manifest와 보관 ZIP2개를 재검증했다. 시작 index `8202bec4a3553483e2b12fbbadd2d5c9d2c2e9dc1f56ff51e8eb5f1a6433abf9`,
종료 sidecar `25475d6f60d4435d1d837fbbc31bae71955857fb4f070b90563dc01cceb089d3`. 승인된 두 세대에서 이전 rollback
`98ff546e6469f7487f8ff9bb789b425a7a5257bb`의 관리 ZIP만 교체했다. 과거 evidence·사용자 원본·이전 checkout은
보존했다. 이번 개발/최종 RAM workspace만 identity·봉인 뒤 정리했고 재생성 출력 해시,
fixture 원문·checkpoint·실패/실행 로그·화면은 보존했다.

시작 여유 25,684,295,680B, 마감 25,672,335,360B(23.9092GiB), 순증가 11,960,320B.
최대 cgroup 전체 memory 9,005,314,048B, 최종 stage 최소 디스크 25,679,835,136B.
추가 cgroup9GiB+안전1GiB·RAM 임시파일4GiB+파일시스템 여유512MiB·디스크 안전64MiB·
개발 evidence256MiB/최종512MiB의 기존 예산을 유지했다.

정보 정의별 구조체 선택은 확정이며 답변 대기가 아니다. 이 단위는 단일 cardinality 기본형 필드의
native 정보 값의 생성 기반이고 전체 고급 핀 편집 완료가 아니다. 정보/참조 타입 선택 UI,
복합·배열·reference·함수·종류 필드, 고급 Blueprint 상수/핀 대응과 명시 계약 전환은
동일 고정9행 후속이다. 기존 객체 ID/$ref의 정체성·수명을 struct snapshot으로 바꾸지
않는다. editor 기본값 자동 주입·schema hot migration/serialization/구 reader 자동 변환도
없다. 생성 타입을 쓰는 새 선언은 과거 Parser가 읽지 못하며 모든 롤백 reader와의 교환은
미검증이다. 기존 기본형 선언·원문 C#·공개 override와 권한 의미는 유지한다. M11/M12/M4는
새 회귀 근거 없이 재개하지 않는다. identity/group backend와 다른 고정 잔여도 별도다.

실행 검증은 Linux native·Chromium 격리 fixture다. 실제 Windows/WebView2·모바일·물리
IME/GPU/audio·사용자 프로젝트·전체 UI, Space/Library 전달은 미검증이다. 교차 패키지는
실제 Windows 실행이 아니다. 초기 빈 화면과 과거 Save 미발행의 모든 간헐 원인은 미확정이다.
