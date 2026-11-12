# 원래 native C# out→ref와 기존 caller ref 출처 검증

제품 동결 `a48d29c25aec571c5fe0d062bc3d6845db88b2b4`의 [지원 범위](V666_NATIVE_OUT_REF.md)를 최종 **신규 46단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 package·구조/무결성·전체 ZIP 복원을 실행했다. 기존 NuGet seed를 복사해 restore했다.
개발 단계와 최종 신규 단계를 합산하지 않는다.

- 게시b763의 원래 out 실행은 유효하지만 기존 scalar caller ref 출처를 지정한 single/shared 후보가 거절됨을 재현했다.
  수정 후 각 single과 정역순 공동 후보가 검증되고 원래 hash·바인딩·ID·경로를 유지한다.
- 기존 C# 창에서 out을 ref로 바꾸고, 원래 선언된 caller ref 입력 second를 직접 선택한다.
  scalar 값 매개변수·리터럴·local/node·없는/위조 출처는 ref로 선택할 수 없다. 임시/기본 셀을 만들지 않는다.
  기존 amount 입력은 identity, 기존 out 소비자는 같은 타입 반환에 명시 대응한다.
- 두 실제 IInvoke의 두 번째 매개변수는 전후 long&이며 IsOut만 true→false다. provider 반환34·인자34는 같다.
  원래 C# 원문에서 caller 반환은38로 같고 원래 second ref 셀은5→38로 바뀐다.
  caller 자체 long/ref long→long ABI·profile은 그대로다. out 스냅샷을 임의 ref 별칭으로 바꾸지 않는다.
- 역할 혼합·이름/타입/수/반환 변경, 누락/변조된 native 선언·본문·caller·입력·출력·원본 문맥과 잘못된 C#은 전체 거절했다.
  ref 출처의 없는 이름·값 인자·node/local·리터럴·기존 call 입력명·위조 플래그와 원래 amount 대체도 거절했다.
  UI ref 입력에는 직접 값 옵션이 없으며 원래 caller ref 출처를 직접 선택해야 한다.
- 460px UI의 취소·명시 대응·Undo/Redo·미저장/저장 cold, checkpoint 실패/재시도,
  Save/결과 조회 응답 유실·owner 경합·반복 Save 비활성·지연 응답 중 새 설명 보존을 검사했다.
  늦은 입력은 cold에서 복원되고 후속 명시 Save·Review 취소·새 Confirm·실행까지 통과한다.
- 후속 정보/기능 설명 Save는 변경 ABI와 version3 readGuards를 유지한다.
  caller ref 선언을 포함한 receipt 누락/변조는 거절했다. Save 전 caller ref 선언 변경과 Review 뒤
  caller ref 선언·helper 선언/본문·caller graph·native 선언/본문 변경은 Confirm 전체 거절이며 peer·checkpoint·receipt를 유지한다.
  정확한 복원·cold·새 Review/Confirm은 실행까지 통과했다. caller 선언과 C#의 bytes·inode·mode·mtime 및 BOM/CRLF도 유지한다.
- 기존 값→ref 후보/API·입력 타입·forwarded·중첩·ref·private/import 경계와 retained 값/ref·일반 본문 UI를 회귀 검사했다.
  out→ref를 오류로 기대하던 out→값 UI의 첫 거절 입력은 실제 이름 변경으로 바꾸고,
  기존 값→ref·out→값·ref→값 UI의 저장·복원·Confirm·실행을 현재 코드에서 새로 통과했다.
- package와 전체 복원본의 저장·응답 유실·늦은 입력·Confirm·실행 및 package 실패 수명이 통과했다.
  시작 전송8회 관측은 과거 간헐 빈 화면의 원인 확정 증거로 세지 않는다.

개발 24단계는 실패0이다. 최종은 동결 코드에서 전부 새로 실행했다.
[구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시 대조한 과거 증거이며 신규 단계에 포함하지 않는다.
새 group의 저장·재편집·Review는 같은 게시 세대 도구 기준이다. 새 문법이나 자동 migration/downgrade·이전 authoring 세대 호환을 주장하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | a48d29c25aec571c5fe0d062bc3d6845db88b2b4 | c6149385736eace25554b8243b0473e29dd1e83ffbe786f52166cf90b228d194 | 54093047 |
| rollback | 99394c46584adbc7f7c08a006c1b0bcdd05528d3 | 5c51aefb11809910a0e2750a6ea6dd13af07e78554f2a25fd49cbaf6b18df847 | 54092025 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/badf53abf0874f5da09e4eebdc495d26.json` · evidence SHA256 `37588596d9428cc050e482aae914f9607c2e5a311411e54268c20a275ae8038d`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/4dfdc7495a7c4b08846ac6a24c9df6cd.json` · evidence SHA256 `438ac97d0d5dd4198bdfdd15e47f90a59505a5beb55122c561f9ffbf87df1332`.
관리 package2개와 증거 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존했다. 퇴역한 세 번째 관리 ZIP 전체 보존은 주장하지 않는다.
여유 24986013696bytes(23.27GiB)다.

남은 고정7/8행은 값 입력 추가/삭제 등 정의 결합, opaque/private 명시 C# 계획,
선택 native callee 의존성·다른 원래 import/등록 외부 관측 결합이다. 제한된 역할 방향 지원을 전체 계약 변경 완성으로 표현하지 않는다.
optional 조합을 필수로 늘리지 않고 M11/M12/M4를 회귀 없이 다시 열지 않는다.
정보별 구조체·종류 enum·모듈 interface 및 권한·override 계약·authored layout·최종 CAS와 기존 예산을 유지한다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
