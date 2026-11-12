# 명시 native 값 입력 삭제 검증

제품 동결 `4f3e79b0c1c8cccc441175f4c6d5fc397d30f763`의 [지원 범위](V666_NATIVE_INPUT_REMOVAL.md)를 최종 **신규 46단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet와 기존 seed 복원, 빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 package·구조/무결성 및 ZIP 전체 복원을 검사했다. 개발 단계와 최종 단계를 합산하지 않는다.

- 게시4a00826c에서 원래 실행과 각 single 입력 삭제/본문/caller 선택은 유효하지만 공유 caller 공동 후보는 거절됨을 재현했다.
  수정 후 정역순 공동 후보가 동일하며 원래 hash와 노드 ID·실행선·반환 연결을 유지한다.
- 상세창에서 첫 long amount 입력을 삭제하고 root 입력 및 앞 호출 결과의 원래 연결을 각각 직접 해제했다.
  남는 double real과 nativeReal 별칭·리터럴1.25/2.5 및 caller 자체 ABI·profile은 그대로다.
  C# 본문은 테스트가 직접 작성한 텍스트로 바꾸며 자동 재작성하지 않는다.
- 실제 IInvoke에서 long 입력이 사라지고 double 값 입력만 남는다. 명시 본문으로 provider 반환34→9, 공유 caller38→10이 실행된다.
  삭제한 변수를 사용하는 C#과 누락/틀린 해제·남는 입력 값 대체·출력 재대응·타입/이름/역할 변경·stale 원본은 전체 거절했다.
- 460px UI의 삭제 선택·명시 해제·본문 취소/저장·Undo/Redo·미저장/저장 cold·Review 취소·Confirm·실행을 검사했다.
  checkpoint 실패/재시도·Save/조회 응답 유실·owner 경합·반복 Save 보호를 검사했다.
  지연 응답 중 새 설명을 보존하고 cold 복원·후속 Save·Review/Confirm·실행까지 확인했다.
- 후속 정보/함수 설명 저장은 새 ABI와 version3 readGuards를 유지한다. 누락·변조 receipt는 거절했다.
  Save 전 helper 선언 변경, Review 후 helper 선언/본문·caller graph·선택 native 헤더/본문 변경은 Confirm 전체 거절이다.
  checkpoint·peer와 모든 비선택 원본을 보존하고 정확한 복원·cold·새 Review 뒤 Confirm한다.
  모든 비선택 원문의 bytes를 대조했고 helper 선언·C# 본문은 최종 Confirm에서 inode·mode·mtime도 보존했다. 선택 본문은 명시한 새 텍스트로 반영한다.
- 기존 입력 추가의 native/API/UI와 입력 타입·forwarded·중첩·ref·private/import 경계 및 out→ref·값→ref UI를 새 코드에서 회귀 검사했다.
  새 package와 전체 추출본의 저장·응답 유실·늦은 입력·실행·패키지 실패 수명을 검사했다.

개발 24단계는 실패0이다. 최종 단계는 모두 동결 코드에서 새로 실행했다.
과거 구 Reference reader 증거는 해시 대조한 재사용 자료이며 신규 단계에 포함하지 않는다.
같은 게시 세대의 저장·재편집·검토 기준이다. 이전 authoring 세대 호환·자동 migration/downgrade를 주장하지 않는다.
시작 화면 전송8회 관측은 과거 간헐 빈 화면 원인 확정으로 세지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 4f3e79b0c1c8cccc441175f4c6d5fc397d30f763 | c9984cb254c6d8629ef8f0c7c0e856d60258d013c527e6fac628f6f1a25c894c | 54093606 |
| rollback | de5756720fe005bd8f5351131fe277fc035c4fd6 | 7d738fb9861f3d341815b0dff7b9155244962020e10116b71f7df6a12b303c1f | 54094118 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/429db62f253e4286b7321720f4c20055.json` · evidence SHA256 `0841c25e66bf65f2511b5f3974ff401aac153ad206ffa56e5861d484b635d2c9`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/58bb72f086214fc89b540169ec676565.json` · evidence SHA256 `a24c376f8ee62c5dca3b7f555b76d3b67dfbb8cd3c074238604421b119b32148`.
보관 package2개와 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존한다. 퇴역한 세 번째 관리 ZIP의 전체 보존을 주장하지 않는다.
여유 24937394176bytes(23.22GiB)다.

남은 고정7/8행은 다른 명시 계약/본문 공동 편집, opaque/private C# 명시 계획,
선택 native callee 의존성·다른 원래 import/등록 외부 관측 결합이다. optional 조합을 필수로 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface와 원본 소유권·권한·override 계약·authored layout·최종 CAS를 유지한다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio 및 전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
