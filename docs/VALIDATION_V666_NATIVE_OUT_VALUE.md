# 원래 native C# out→값 전환 검증

제품 동결 `d22e1b919b94321be69d079414cdd3cf276b352c`의 [지원 범위](V666_NATIVE_OUT_VALUE.md)를 최종 **신규 43단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet·빈 엔진 cache의 Release/MCP 및 실제 Linux 엔진,
새 Windows 교차 package·구조/무결성·전체 ZIP 복원을 실행했다. 기존 NuGet seed는 각 환경에 복사해 restore했다.
개발 단계 수와 최종 신규 단계 수는 합산하지 않는다.

- 게시 c26858c7에서 원래 out ABI/실행38과 두 단일 native out→값 후보는 각각 유효하나 공동 후보만
  거절되는 것을 재현했다. 수정 후 정역순 후보가 같고 모든 원래 hash·바인딩·경로를 유지한다.
- 기존 C# 창의 형식 매개변수에서 out을 제거하고 caller의 새 count 입력에 리터럴5를 직접 지정한다.
  이전 count를 쓰던 둘째 amount와 caller 반환은 호환 long return에 직접 대응한다. 기존 값 입력은
  identity로 유지하며 원래 바인딩 중복 사용·기본값·ref 저장소나 C# 자동 재작성을 허용하지 않는다.
- 실제 생성된 두 IInvoke의 CLR 매개변수/IsOut·반환값을 같은 임시 Main으로 검사했다.
  원래는 out long이며 인자에34를 쓰고, 이후는 값 long이며 전달한 인자5를 유지한다.
  두 함수의 반환은 전후 long34, caller는 전후38이다. 본문은 할당 후 반환하는 원래 코드 그대로다.
- 이름·타입·수·반환·ref/혼합 방향, 잘못된 native 선언·hash·C#, 누락된 본문/caller·새 입력/출력 대응,
  잘못된 리터럴·사용 중 바인딩 재사용·기존 입력 교체·불필요한 해제·caller 문맥 삽입을 전체 거절했다.
  UI의 ref와 혼합 방향도 정확한 안내로 거절하고 취소로 보관 입력을 복원했다.
- 원래460px UI에서 취소·Undo/Redo·미저장/저장 cold, checkpoint 실패/재시도, Save/settlement 응답 유실,
  owner 경합과 반복 Save 비활성을 검사했다. 지연 성공 응답 중 추가한 설명은 남고 cold에서 복원되며
  다음 명시 Save·Review 취소·새 Confirm으로 전환 계약·caller와 함께 반영된다.
- 후속 정보/함수 설명 저장은 변경 ABI·unchanged body read member·version3 readGuards를 유지했다.
  receipt 전체/일부 누락과 hash/path/owner/version/implementation proof 변조를 거절했다.
  Save 전 helper 선언 변경과 Review 뒤 helper 선언/본문·caller graph·native 본문/선언 변경은
  Confirm 전체 거절이며 peer·checkpoint·원래 receipt를 유지한다. 정확한 복원·cold·새 Review/Confirm은
  실제 실행까지 통과했다. 원래 C#의 UTF8 BOM·CRLF·bytes·inode·mode·mtime도 최종 Confirm에서 유지됐다.
- 기존 값→out 후보/API와 원본 경합, native 입력 타입·retained/forwarded·이름/중첩·ref·private/import 경계,
  whole out→값 UI 및 일반 C# 본문 편집을 현재 코드에서 새로 회귀 검사했다. 새 package와 전체 복원본도
  실제 저장·응답 유실·늦은 입력·Confirm·실행과 실패 수명 검사를 통과했다.
- 시작 전송8회 reload·단절·child/root/프로젝트 왕복을 관측했다. 과거 간헐 빈 #app의 원인 확정 증거로 세지 않는다.

개발 21단계는 실패0이다. 최종은 동결 코드에서 전부 새로 실행했다.
[구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시를 대조해 개발 증거에 보관한 과거 증거이며
최종 신규 단계 수에 포함하지 않는다. 새 group 저장·재편집·Review는 같은 게시 세대 도구 기준이고 이전 authoring
세대 호환은 주장하지 않는다. 새 문법·자동 migration/downgrade·기존 profile 삭제는 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | d22e1b919b94321be69d079414cdd3cf276b352c | e90d7df41eabe38bb3089e98e03b8c6655096e2cef82e43d64215a22e52c6f8d | 54091912 |
| rollback | bb193c51c0ca36dd922961a1230dd2069c15ec89 | 2be4dff6a72cf3113b4e151852fd6e18972009a552770c170adf2c6888f6e553 | 54088943 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/332f629f631b4130967e55cac0c735bd.json` · evidence SHA256 `971257d11c03090c5e2be22882e0b3c2b2dd43851251725f80a9477756b69d77`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/5eaa423ba2804708ac0329dd5ef6a770.json` · evidence SHA256 `e511758ad73218f852a4f678b4968f27232db2e817f039222d5f61cd20e3b8f4`.
두 관리 package·증거 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존했다. 퇴역한 세 번째 관리 ZIP 전체의 보존은 주장하지 않는다.
여유 25075851264bytes(23.35GiB)다.

직접 소유 동기 scalar-return·공개 실행 분기/상속/override 없는 기능·단일 native target·일반 Blueprint caller 범위다.
남은 고정7/8행은 다른 ref 역할·값 입력 추가/삭제 등의 정의 결합, opaque/private 명시 C# 계획,
선택 native callee 사이 의존성과 다른 원래 import/등록 외부 관측 결합이다. optional 조합을 새 필수로 늘리지 않는다.
M11/M12/M4를 회귀 없이 다시 열지 않는다. 권한·override 계약·authored layout·Review/Confirm·최종 CAS와
64-member/240-check/2048-source 예산을 유지했다. 실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 전수 검증은
수행하지 않았다. 새 credential/grant·과금·main 변경은 없다.
