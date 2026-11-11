# 명시 값 입력 이름·native 본문 공동 저장 검증

제품 동결 `b3fb8f1e827d81e21783add5a1677774bcb59a6d`의 [지원 경계](V666_NAMED_BODY_GROUP.md)를 **신규 37단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. 개발과 최종 수는 합산하지 않는다.

- 게시23c3dbb0에서 두 native 본문/공개 값 입력 이름의 단일 후보는 각각 유효하지만 공동
  후보만 거절하는 것을 재현했고 원래 프로그램 결과40을 확인했다.
- 기존 상세창의 명시 C# 이름 모드에서 amount→leftAmount를 선택하고 두 본문을 직접
  편집했다. nativeAmount/nativeCount 선언과 타입·역할·순서·반환, 다른 C#·본문/함수 ID·
  기존 공유 caller의 값/실행선·출력 소비자를 유지한다. 한 Save·cold·Review 취소/Confirm
  뒤 실제 결과20을 확인했다. 표시 이름 metadata를 C# 계약 편집으로 혼동하지 않는다.
- 정·역순 순수 후보와 원래 hash·한 후보를 검사했다. 타입/역할/순서/반환 변경, native 선언
  변경, 잘못된 remap·누락/위조 본문 hash/path/계약, 컴파일·보호 경계 오류와 caller 계획
  끼워넣기는 전체 미적용이었다. import가 있는 각각의 단일 편집은 유효하지만 이번 새 이름
  공동 저장은 원래 입력을 보존해 거절한다. 기존 ref 이름과 같은 계약 다중 target도 새로 회귀했다.
- UI 취소·Undo/Redo·미저장/저장 cold, checkpoint 실제 쓰기 실패/복구, 동료 source 경합,
  실제 apply/settlement 응답 유실과 재시작 후 중복 apply 없는 복구를 검사했다. 지연 성공
  응답 중 추가한 실제 설명 입력은 보존됐고 후속 명시 Save·Review 취소/Confirm도 결과20이었다.
- API receipt는 명시 이름·두 본문·공유 caller graph를 같은 원래 source/write CAS에 묶었다.
  Save 전 caller 변경, Review 뒤 실제 편집 graph/본문 변경, 호환되지 않는 물리 caller 헤더는
  전체 거절하고 원본·peer·checkpoint를 보존했다. 복원/cold 뒤 새 Review/Confirm과 실제
  실행을 확인했고 편집하지 않은 native/header/다른 C#의 bytes·inode·mode·mtime도 유지했다.
- 현재 실제3D 전송 정체·부분 POST 중 reload8회·단절·child/root·프로젝트 왕복·cold와
  패키지 실패 수명을 새로 검사했다. 과거 간헐적 빈 화면 원인은 여전히 미확정이다.

개발 23단계의 실패 2건은 보존했다. fixture의 public export가 자체
base 모듈 참조를 덮어써 private import로 수정했다. 또 단순 scalar leaf에 추가 body readGuards가
반드시 있다는 기대가 기존 ObservedScope 정책과 달랐다. 기존 범위는 비어 있을 수 있으므로
편집 대상의 실제 CAS와 호환되지 않는 물리 헤더의 재컴파일 거절을 구분했다. 모든 미편집
원본 공백까지 새 raw-byte lease를 추가하지 않았고 BodyGuards/Confirm 정책을 바꾸지 않았다.
새 이름 결합은 import 없는 단일 scalar native target·일반 직접 caller로 한정해 추가 관측
closure를 암묵 허용하지 않는다. 기존 같은 계약 그룹과 ref dispatcher는 그대로다.

구 Reference TYPE 거절·optional 문자열 metadata의 [보관 바이너리 근거](VALIDATION_V666_ARGUMENT_LABELS.md)는
개발 evidence에서 SHA를 다시 확인했다. 구 reader 신규 실행이 아닌 과거 증거 재사용이며 위 최종
단계 수와 분리한다. 동일 게시 세대 reader/authoring/runtime을 사용하고 소급 수정·자동 downgrade/
migration·원문/profile 삭제나 TYPE만으로 버전/손상을 단정하는 처리는 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | b3fb8f1e827d81e21783add5a1677774bcb59a6d | 1a563958960b59025277f14b8be7c6ae7afab4e41728e7b045a7862fa916c250 | 54070915 |
| rollback | 45c7ee5c33212271b7efe095a765ec86ee447b5d | ec9e2f52309bcef76b5a1826781136bbbb961e1a75cf9e1753413ea747a7137a | 54072348 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/13009cfc537b40c4b91cc31834683eaa.json` · evidence SHA256 `93e6db8d55e76f34afe7709fd183c879c9bc292c161aa53396033f0408421769`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/78ffb72d88c3433e936cd7e1f62c1a6f.json` · evidence SHA256 `8dec3215d36ccc6d1d4fc72294ce9f91ecddc96be4eeed69517f2273747117c1`.
두 관리 package와 증거의 SHA를 재확인했다. 승인된 latest/정상 rollback2세대 교대와 이번
소유 RAM 임시물 정리만 적용했다. 원래 checkout/main·과거 비관리 자료/증거는 보존하며
퇴역한 세 번째 관리 ZIP 전체를 계속 보관한다고 주장하지 않는다. 여유 25314185216bytes
(23.58GiB)다.

고정7행의 forwarded/opaque·다른 frame 계약/본문 closure와 고정8행의 위 단위 밖 명시 계약·본문·
공유 caller 결합은 기존 유한 잔여다. 모든 타입/context 조합을 새 필수로 늘리지 않고 M11/M12/M4를
다시 열지 않는다. 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·전체 UI 전수 검증은 별도다.
새 자격증명/외부 grant·라이브 AI/과금·main 변경은 없다.
