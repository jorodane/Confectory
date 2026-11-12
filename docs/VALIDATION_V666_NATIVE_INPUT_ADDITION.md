# 명시 native 값 입력 추가 검증

제품 동결 `de5756720fe005bd8f5351131fe277fc035c4fd6`의 [지원 범위](V666_NATIVE_INPUT_ADDITION.md)를 최종 **신규 46단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 package·구조/무결성·전체 ZIP 복원을 실행했다. 기존 NuGet seed를 복사해 restore했다.
개발 단계와 최종 신규 단계를 합산하지 않는다.

- 게시c020에서 원래 실행과 두 single 추가/본문/caller 후보는 유효하지만 공유 caller 공동 후보만 거절됨을 재현했다.
  수정 후 각 single과 정역순 공동 후보가 검증되고 원래 hash·바인딩·ID·경로를 유지한다.
- 기존 상세창에서 long step 입력을 추가하고 두 호출의 step 값5를 직접 선택했다.
  C# 창은 원래 nativeAmount/nativeReal 이름을 유지하며 새 step만 추가한 헤더를 보여 준다.
  새 입력을 사용하는 본문은 테스트가 직접 작성한 텍스트이며 자동 재작성하지 않는다.
- 실제 두 IInvoke는 long/double 인자 뒤에 long 값 인자를 추가한다. 모든 인자는 값 전달이며 원래30·1.25와 새5가 유지된다.
  명시 본문이5를 사용해 provider 반환34→38, 공유 caller38→46으로 실행된다. caller 자체 ABI·profile과 기존 real 바인딩1.25/2.5는 그대로다.
- 이름/타입/역할/반환·기존 native 별칭/순서 변경, 누락/변조된 선언·본문·caller·값·hash·원본 문맥과 잘못된 C#은 전체 거절했다.
  새 값 누락·암묵적 기존 입력 재사용·틀린 리터럴 타입·기존 바인딩 대체/해제·출력 재대응도 거절했다.
- 460px UI의 새 입력 생성·타입/이름 편집·값 선택·본문 취소/저장·Undo/Redo·미저장/저장 cold,
  checkpoint 실패/재시도·Save/결과 조회 응답 유실·owner 경합·반복 Save 비활성을 검사했다.
  지연 응답 중 새 설명은 보존·cold 복원되고 후속 Save·Review 취소·새 Confirm·실행까지 통과한다.
- 후속 정보/기능 설명 Save는 새 ABI와 version3 readGuards를 유지한다. receipt 누락/변조는 거절했다.
  Save 전 원본 변경과 Review 뒤 helper 선언/본문·caller graph·native 헤더/본문 변경은 Confirm 전체 거절이며 peer·checkpoint·receipt를 유지한다.
  정확한 복원·cold·새 Review/Confirm 후 선택한 본문만 반영하고 helper/비선택 C# bytes·inode·mode·mtime을 보존했다.
- 기존 out→ref 후보/API·입력 타입·forwarded·중첩·ref·private/import 경계, retained 값/ref·일반 본문과
  기존 out→ref·out 추가·값→ref UI를 현재 코드에서 새로 회귀 검사했다.
- 새 package와 전체 ZIP 복원본에서 저장·응답 유실·늦은 입력·Confirm·실행 및 package 실패 수명이 통과했다.
  시작 전송8회 관측은 과거 간헐 빈 화면 원인을 확정하는 증거로 세지 않는다.

개발 24단계는 실패0이다. 최종은 동결 코드에서 전부 새로 실행했다.
[구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시 대조한 과거 증거이며 신규 단계에 포함하지 않는다.
새 group 저장·재편집·Review는 같은 게시 세대 도구 기준이다. 자동 migration/downgrade·이전 authoring 세대 호환을 주장하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | de5756720fe005bd8f5351131fe277fc035c4fd6 | 7d738fb9861f3d341815b0dff7b9155244962020e10116b71f7df6a12b303c1f | 54094118 |
| rollback | a48d29c25aec571c5fe0d062bc3d6845db88b2b4 | c6149385736eace25554b8243b0473e29dd1e83ffbe786f52166cf90b228d194 | 54093047 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/fd4a3389b8d1444f89fb705c1f626d76.json` · evidence SHA256 `a973577c8ff6f368a141dde8a6bbaa7ddf59f79880665e2f5c6e15f51033bd12`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/79f9301d63404b9f817c9657703019e6.json` · evidence SHA256 `4d833724056aef8069a50e8704bd3ed1aa9a7036af4de765f901f88a5e9d5709`.
관리 package2개와 증거 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존했다. 퇴역한 세 번째 관리 ZIP 전체 보존은 주장하지 않는다.
여유 24961478656bytes(23.25GiB)다.

남은 고정7/8행은 값 입력 삭제/다른 정의·계약 변경 결합, opaque/private 명시 C# 계획,
선택 native callee 의존성·다른 원래 import/등록 외부 관측 결합이다. 제한된 추가 단위를 전체 계약 완성으로 표현하지 않는다.
optional 조합을 필수로 늘리지 않고 M11/M12/M4를 회귀 없이 다시 열지 않는다.
정보별 구조체·종류 enum·모듈 interface 및 권한·override 계약·authored layout·최종 CAS와 기존 예산을 유지한다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
