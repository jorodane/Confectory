# 원래 native C# ref→out 전환 검증

제품 동결 `c04ee2d0acfce87ea538ae537bad8f4e28661977`의 [지원 범위](V666_NATIVE_REF_OUT.md)를 최종 **신규 43단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet·빈 엔진 cache의 Release/MCP와 실제 Linux 엔진,
새 Windows 교차 package·구조/무결성·전체 ZIP 복원을 실행했다. 기존 NuGet seed를 각 환경에 복사해 restore했다.
개발과 최종 신규 단계 수는 합산하지 않는다.

- 게시 bb09e783에서 두 단일 ref→out 후보와 원래 ref ABI·caller 저장소 효과는 유효하나 공동 후보만
  거절되는 것을 재현했다. 수정 후 정역순 후보가 같고 모든 원래 hash·바인딩·경로를 유지한다.
- 기존 C# 창에서 ref를 out으로 바꾸고 caller의 정확한 원래 count 바인딩을 직접 해제한다.
  나머지 입력과 기존 출력은 identity로 유지하며 새 out은 자동 연결하지 않는다.
  caller 자체의 long/ref long→long 계약은 그대로다. 새 ref·임시 저장소를 추정/생성하지 않는다.
- 같은 임시 Main으로 실제 두 IInvoke의 CLR 매개변수/IsOut·반환을 검사했다. 둘째 매개변수는
  전후 long&이고 IsOut만 false→true다. 두 provider는 반환34·인자34를 쓰고 caller 반환은 전후38이다.
  원래 두 ref 호출은 caller의 second 저장소를5→38로 썼지만, 명시 해제 뒤에는 그 저장소가5로 남는다.
  새 out의34/38은 연결하지 않은 결과다. 원래 C# 본문은 할당 후 반환하는 코드 그대로다.
- 이름·타입·수·반환·다른 ref 방향/혼합 방향, 잘못된 native 선언·hash·할당 전 읽기/미할당 out,
  누락/변조된 해제·본문/caller·출력 대응·새 입력·caller 문맥 삽입은 전체 거절했다.
  UI의 ref→값 및 혼합 방향도 정확한 안내로 거절하고 취소로 입력을 복원했다.
- 원래460px UI에서 취소·Undo/Redo·미저장/저장 cold, checkpoint 실패/재시도, Save/settlement 응답 유실,
  owner 경합·반복 Save 비활성을 검사했다. 지연 성공 응답 중 새 설명은 남고 cold에서 복원되며
  다음 명시 Save·Review 취소·새 Confirm으로 계약·caller와 함께 반영된다.
- 후속 정보/기능 설명 Save는 변경 ABI·unchanged body read member·version3 readGuards를 유지했다.
  receipt 전체/일부 누락·hash/path/owner/version/implementation proof 변조는 거절했다.
  Save 전 helper 선언 변경과 Review 뒤 helper 선언/본문·caller graph·native 본문/선언 변경은
  Confirm 전체 거절이며 peer·checkpoint·원래 receipt를 유지한다. 정확한 복원·cold·새 Review/Confirm은
  실제 실행까지 통과했다. C#의 UTF8 BOM·CRLF·bytes·inode·mode·mtime도 최종 Confirm에서 유지됐다.
- 기존 out→값 후보/API·원본 경합, 입력 타입·retained/forwarded·중첩·ref·private/import 경계,
  whole ref→out UI 및 일반 C# 본문 편집을 현재 코드에서 새로 회귀 검사했다. 이전 값/out 두 방향도
  기존 규칙을 유지한다. 새 package와 전체 복원본의 저장·응답 유실·늦은 입력·Confirm·실행 및
  package 실패 수명 검사를 통과했다. 시작 전송8회 reload·단절·child/root/프로젝트 왕복은 관측 결과이며,
  과거 간헐 빈 #app의 원인 확정 증거로 세지 않는다.

개발 21단계는 실패0이다. 최종은 동결 코드에서 전부 새로 실행했다.
[구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시를 대조해 개발 증거에 보관한 과거 증거이며
최종 신규 단계 수에 포함하지 않는다. 새 group 저장·재편집·Review는 같은 게시 세대 도구 기준이다.
이전 authoring 세대 호환·새 문법·자동 migration/downgrade나 기존 profile 삭제는 주장하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | c04ee2d0acfce87ea538ae537bad8f4e28661977 | c537414d1d6c2e30b8454856e9b597101805141fc5f7dbbfe6c328467a9f1e68 | 54091839 |
| rollback | d22e1b919b94321be69d079414cdd3cf276b352c | e90d7df41eabe38bb3089e98e03b8c6655096e2cef82e43d64215a22e52c6f8d | 54091912 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/7c35a1d2b52641bda94ebf08e01294de.json` · evidence SHA256 `6065d7ec3a64b7c3366c332601b9f20f636479db92e3e767e309dfa40a5015b9`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/490b4092cf724be4af942b831e6e391c.json` · evidence SHA256 `84ab6f696b1662851d458e5df33a458ccf52e2681f899e879a670975ef7e74b8`.
두 관리 package·증거 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존했다. 퇴역한 세 번째 관리 ZIP 전체의 보존은 주장하지 않는다.
여유 25056227328bytes(23.34GiB)다.

직접 소유 동기 scalar-return·공개 실행 분기/상속/override 없는 기능·단일 native target·일반 Blueprint caller 범위다.
남은 고정7/8행은 ref를 새로 요구하는 다른 방향·값 입력 추가/삭제 등의 정의 결합, opaque/private 명시 C# 계획,
선택 native callee 사이 의존성과 다른 원래 import/등록 외부 관측 결합이다. optional 조합을 새 필수로 늘리지 않는다.
M11/M12/M4를 회귀 없이 다시 열지 않는다. 권한·override 계약·authored layout·Review/Confirm·최종 CAS와
64-member/240-check/2048-source 예산을 유지했다. 실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 전수 검증은
수행하지 않았다. 새 credential/grant·과금·main 변경은 없다.
