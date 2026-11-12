# 원래 C# 값→out 전환 검증

제품 동결 `bb193c51c0ca36dd922961a1230dd2069c15ec89`의 [지원 범위](V666_NATIVE_VALUE_OUT.md)를 최종 **신규 43단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet, 빈 엔진 cache의 Release/MCP와 실제 Linux
엔진, 새 Windows 교차 package의 구조/무결성 및 전체 ZIP 복원을 실행했다. 기존 NuGet seed를
각 격리 환경에 복사해 restore했다. 개발 단계와 최종 단계 수는 합산하지 않는다.

- 게시 b693ab6f에서 원래 실행38과 두 함수의 단일 native value→out 후보는 각각 유효하고,
  공유 caller 공동 후보만 거절되는 것을 재현했다. 수정 후 정역순 후보가 같고 원래 hash와
  모든 명시 계획을 유지한다. C# 창의 밝은 매개변수 영역에서 역할만 바꾸고 원래 입력을
  직접 해제한다. 새 역할 메뉴·자동 out 연결·암묵 입력 삭제·C# 자동 재작성은 없다.
- 같은 임시 Main으로 생성된 두 IInvoke의 CLR ABI와 실제 값을 검사했다. 원래 둘째 인자는
  값 long이고 인자5를 유지한다. 전환 뒤에는 out long이며34를 전달한다. 함수의 반환은
  전후 long34, 공유 caller는 전후38이다. native/public 별도 이름·다른 인자·반환·IDs·실행선과
  helper를 보존했다. 원래 본문은 이미 할당 후 반환하는 코드이며 역할만 편집했다.
- 역할/ref·이름·타입·수·반환·대응 변경, 빠지거나 틀린 입력 해제, 남긴 옛 입력,
  본문/호출 계획 누락·stale hash·틀린 native 선언·할당하지 않는 C#·출력 대응·caller 문맥
  삽입은 전체 거절했다. UI의 ref 시도도 오류를 표시하고 취소로 입력을 복원했다.
- 원래460px 화면의 취소·Undo/Redo·미저장/저장 cold·checkpoint 실패/재시도,
  Save/settlement 응답 유실, owner 경합과 반복 Save 비활성을 검사했다. 늦은 실제 설명은
  성공 응답 뒤에도 남고 cold에서 복원되며 다음 명시 Save와 Review/Confirm으로 반영된다.
- 후속 정보/함수 설명 저장은 정확한 변경 ABI, unchanged 본문의 read member,
  caller와 version3 readGuards를 유지했다. receipt 누락/변조, hash·path·owner·version·
  implementation proof 오류를 거절했다. Save 전 helper 선언 변경과 Review 뒤 helper 선언/
  본문·caller graph·native 본문/선언 변경은 Confirm 전체를 거절하고 peer/checkpoint를
  유지했다. 정확히 복원한 뒤 새 Review/Confirm과 cold 재시도는 실제 실행까지 통과했다.
  unchanged native C#의 UTF8 BOM·CRLF·bytes·inode·mode·mtime도 최종 Confirm에서 유지됐다.
- 기존 out 추가의 후보·메타데이터/경합, native 입력 타입, retained/forwarded·명명된 중첩,
  whole C# 값→out UI, ref·private/import 경계 회귀를 현재 코드에서 새로 검사했다.
  새 package와 전체 복원본에서도 저장·응답 유실·늦은 입력 및 실제 실행을 검사했다.
- 시작 전송 검사는8회 reload와 단절·프로젝트/child/root 왕복을 관측했다.
  과거 간헐 빈 #app의 원인 확정 증거로 세지 않는다.

개발 36회 중 33회 통과, 해결된 실패3회다.
첫 UI 시작 실패는 수정 JS의 WebBundle 무결성 목록 미갱신이었고 크기/해시를 갱신했다.
그 다음 시도는 검사 스크립트가 새 빌드 대신 이전 엔진 보고서를 가리킨 실행 대상 오류였다.
고유 stage의 새 보고서로 수정했다. 기존 whole-body UI 회귀에서는 새 본문 보존 함수의 fallback 자기 호출을 발견해 실제 editor body로 수정했다. 새 역할 전환·whole-body 역할·기존 본문 편집을 함께 재검사했다. 사전 준비가 실행 중일 때 baseline 실행을
요청한1회는 Workspace 소유자 보호가 작업 시작 전에 거절했다. 준비 완료를 확인한 뒤
실행했으며 중복 worker는 없었다. 모든 실패/거절 로그와 스크립트를 개발 증거에 보존했다.
최종 검증은 수정된 동결 코드와 올바른 보고서를 새 checkout에서 전부 새로 실행했다.

[구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시를 대조해 보관한 과거
증거 재사용이며 이번 최종 단계 수에 포함하지 않는다. 새 group의 재편집/Review는 같은
게시 세대 도구 기준이고 이전 authoring 세대 호환은 주장하지 않는다. 새 문법·자동 migration/
downgrade나 기존 profile 삭제는 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | bb193c51c0ca36dd922961a1230dd2069c15ec89 | 2be4dff6a72cf3113b4e151852fd6e18972009a552770c170adf2c6888f6e553 | 54088943 |
| rollback | bb15884c90602cb54473af1f95505e4f04fffcf2 | ba6c935e1fa1cf7579dff1a00152cc55085d86ac6e03a93c0bf0a66d9b7200ff | 54087362 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/e82bf5100b7141a5b320a2e3fff93c95.json` · evidence SHA256 `041323e217f9e677bf840447ea19f9bc987387db44815c23ca4dbebbc8e94da3`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/a14693366caf4f1a86dc3feafa859744.json` · evidence SHA256 `65442ab66da0b15e2fb9847f39aa4ceb99a6bd0803b8d78dabf46461f79317aa`.
두 관리 package와 증거의 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와
이번 소유 임시물 정리만 적용했다. 원래 checkout/main·비관리 자료·과거 증거를 보존했다.
퇴역한 세 번째 관리 ZIP 전체의 보존은 주장하지 않는다. 여유 25095499776bytes(23.37GiB)다.

현재 단위는 공개 실행 분기·상속/override가 없는 직접 소유 동기 scalar-return C#과 일반 Blueprint 호출자 기준이다.
남은 같은 고정7/8행은 raw C#의 반대 방향/ref 역할, 값 입력 추가·삭제 등의 정의 결합, opaque/private 명시 계획, 선택 native callee
사이 의존성과 다른 원래 import/등록 외부 관측 결합이다. optional 조합을 새 필수로 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 원래 권한·override 계약·authored layout·Review/Confirm·
최종 CAS와64-member/240-check/2048-source 예산을 유지했다. 실제 Windows/WebView2·물리 기기·
IME·GPU/audio·전체 UI 전수 검증은 수행하지 않았다. 새 credential/grant·과금·main 변경은 없다.
