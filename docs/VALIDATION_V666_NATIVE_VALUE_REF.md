# 원래 native C# 값→ref 전환 검증

제품 동결 `99394c46584adbc7f7c08a006c1b0bcdd05528d3`의 [지원 범위](V666_NATIVE_VALUE_REF.md)를 최종 **신규 46단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet와 빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 package·구조/무결성·전체 ZIP 복원을 실행했다. 기존 NuGet seed를 복사해 restore했다.
개발 단계와 최종 신규 단계를 합산하지 않는다.

- 게시73c9의 두 단일 값→ref 후보와 원래 value ABI/실행은 유효하지만 공동 후보만 거절됨을 재현했다.
  수정 후 정역순 후보가 같고 원래 hash·바인딩·ID·경로를 유지한다.
- 기존 C# 창에서 값 매개변수에 ref를 명시하고 실제 기존 caller 입력 바인딩과 출력 identity를 직접 선택한다.
  이름·자료형·수·순서·반환·caller 자체 long/ref long→long ABI·ref graph profile과 C# 원문을 유지한다.
  새 리터럴·기본값·임시 ref 셀·자동 해제를 만들지 않는다.
- 실제 두 IInvoke의 두 번째 매개변수는 long→long&이고 IsOut은 전후 false다.
  원래 count를 읽고 helper로 더한 뒤 count에 대입하는 동일 C#에서 provider 반환38은 같다.
  반사 호출 인자 셀은5→38, 공유 caller 반환은46→79, caller의 원래 ref 셀은5→79다.
  명시한 쓰기 전달 추가의 결과이며 프로그램 결과가 같다고 주장하지 않는다.
- 역할 혼합·이름/타입/수/반환 변경·누락/변조된 native 선언/본문·caller·입력·출력·문맥과 잘못된 C#은 전체 거절했다.
  원래 constant 입력의 value 실행은 먼저 검증하고 그 바인딩을 ref로 바꾸는 후보는 거절했다.
  identity 입력을 리터럴/다른 입력으로 바꾸거나 해제하는 계획도 이 단위에서 거절한다.
- 460px UI 취소·명시 대응·Undo/Redo·미저장/저장 cold, checkpoint 실패/재시도,
  Save/결과 조회 응답 유실·owner 경합·반복 Save 비활성·지연 응답 중 새 설명 보존을 검사했다.
  늦은 입력은 cold에서 복원되고 후속 명시 Save·Review 취소·새 Confirm·실행까지 통과한다.
- 후속 정보/기능 설명 Save는 변경 ABI·원래 read member·version3 readGuards를 유지했다.
  receipt 누락/변조와 Save 전 helper 변경, Review 뒤 helper 선언/본문·caller graph·native 선언/본문 변경은 거절했고
  peer·checkpoint·receipt를 보존했다. 정확한 복원·cold·새 Review/Confirm은 실행까지 통과한다.
  UTF8 BOM·CRLF·bytes·inode·mode·mtime도 유지했다.
- 기존 ref→값 후보/API·입력 타입·forwarded·중첩·ref·private/import 경계와 retained 값/ref 역할·일반 본문 UI를 회귀 검사했다.
  허용된 방향을 오류로 기대하던 기존 ref→값·ref→out·값→out UI의 첫 거절 입력을 실제 이름 변경으로 바꾸고,
  세 UI의 취소·복원·공동 Save/Confirm·실행을 현재 코드에서 각각 새로 통과했다.
- package와 전체 ZIP 복원본의 저장·응답 유실·늦은 입력·Confirm·실행 및 package 실패 수명을 통과했다.
  시작 전송8회 관측은 과거 간헐 빈 #app의 원인 확정 증거로 세지 않는다.

개발 24단계는 실패0이다. 최종은 동결 코드에서 전부 새로 실행했다.
[구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시 대조한 과거 증거이며 신규 단계에 포함하지 않는다.
새 group 저장·재편집·Review는 같은 게시 세대 도구 기준이다. 자동 migration/downgrade나 이전 authoring 세대 호환을 주장하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 99394c46584adbc7f7c08a006c1b0bcdd05528d3 | 5c51aefb11809910a0e2750a6ea6dd13af07e78554f2a25fd49cbaf6b18df847 | 54092025 |
| rollback | 1b84fef81084a987352f4d8c158f9eb8b9f52fc3 | 8ac5535669750826d3d650f2c85822ce2c4db2d11556d025fbe8e47ac766d2bd | 54092791 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/db58c55c02824e26989ac9f6db64d1b3.json` · evidence SHA256 `6619565fe7ed0956621743c94a7f601d130040414a43edce418328e51cd8d23c`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/adfb1d3d463a46e7ad0d9f6d3bef3bdc.json` · evidence SHA256 `15a3197df821a5ab7fb79e947af9355f0fa52a9886d9eea55517ed25e3b649ea`.
관리 package2개와 증거 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존했다. 퇴역한 세 번째 관리 ZIP 전체 보존은 주장하지 않는다.
여유 25010884608bytes(23.29GiB)다.

남은 고정7/8행은 out→ref, 값 입력 추가/삭제 등 정의 결합, opaque/private 명시 C# 계획,
선택 native callee 의존성·다른 원래 import/등록 외부 관측 결합이다. optional 조합을 필수로 늘리지 않는다.
M11/M12/M4를 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface 및 권한·override 계약·authored layout·CAS는 유지한다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
