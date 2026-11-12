# 명시 native 입력 정의·타입 검증

제품 동결 `19d6501aa8ed9f74dd58cb1f171bff80d5d6c2ae`의 [지원 범위](V666_NATIVE_INPUT_MIX.md)를 최종 **신규 46단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet와 기존 seed 복원, 빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 package·구조/무결성 및 ZIP 전체 복원을 검사했다. 개발 단계와 최종 단계를 합산하지 않는다.

- 게시4d8e7fa9에서 원래 실행과 각 single 입력 정의/타입·본문·caller 선택은 유효하지만 공유 공동 후보는 거절됨을 재현했다.
  수정 후 정역순 공동 후보가 동일하며 원래 hash·노드 ID·실행선·반환 연결을 유지한다.
- 기존 상세창에서 amount 삭제, real의 double→string 변경, long step 추가를 같은 함수에서 선택했다.
  원래 root/앞 호출 결과와 real 값1.25/2.5를 각각 명시 해제하고 첫째😀/second 문자열 및 새 숫자5/7을 직접 지정한다.
  C# 본문은 real.Length+step을 직접 작성하며 기존 helper를 사용한다. 캐스트·변환 함수·기본값을 자동 생성하지 않는다.
- 실제 IInvoke 인자는 long/double→string/long으로 바뀐다. first/5를 전달한 provider 반환34→13과
  서로 다른 문자열/5/7을 전달한 공유 caller38→16을 실행했다. caller 자체 ABI/profile과 출력·경로는 그대로다.
- 누락/틀린 원래 해제·대체/새 값 누락·틀린 literal 타입·암묵적 기존 입력 재사용·역할/순서/반환 변경·stale 원본과 잘못된 C#은 전체 거절했다.
  출력 재대응이나 누락된 본문/caller 선택도 원본 변경 없이 거절했다.
- 기존 460px UI의 입력 정의/타입·명시 해제/값 선택·본문 취소/저장·Undo/Redo·미저장/저장 cold·Review 취소·Confirm·실행을 검사했다.
  checkpoint 실패/재시도·Save/조회 응답 유실·owner 경합·반복 Save 보호와 늦은 설명의 cold 복원·후속 Save·Confirm·실행을 확인했다.
- 후속 정보/함수 설명 저장은 새 ABI와 version3 readGuards를 유지한다. 누락·변조 receipt는 거절했다.
  Save 전 helper 선언과 Review 후 helper 선언/본문·caller graph·선택 native 헤더/본문 변경은 Confirm 전체 거절이다.
  정확한 복원·cold·새 Review 뒤 Confirm한다. 모든 비선택 원문 bytes를 대조했고 helper 선언·C# 본문은 최종 Confirm에서 inode·mode·mtime도 보존한다.
  선택한 본문만 명시한 새 텍스트로 반영했다.
- 기존 입력 삭제/추가 정의의 native/API/UI와 입력 삭제·추가 UI, 입력 타입·forwarded·중첩·ref·private/import 경계를 새 코드에서 회귀 검사했다.
  새 package와 전체 추출본의 저장·응답 유실·늦은 입력·실행·패키지 실패 수명을 검사했다.

개발 24단계는 실패0이다. 최종 단계는 동결 코드에서 모두 새로 실행했다.
과거 구 Reference reader 증거는 해시 대조한 재사용 자료이며 신규 단계에 포함하지 않는다.
같은 게시 세대의 저장·재편집·검토 기준이다. 이전 authoring 세대 호환·자동 migration/downgrade를 주장하지 않는다.
시작 화면 전송8회 관측은 과거 간헐 빈 화면 원인 확정으로 세지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 19d6501aa8ed9f74dd58cb1f171bff80d5d6c2ae | e8e737d53446a8082a1f3d0fabf0e462975f4ac8516bc37a0b90e1391faa07ff | 54097359 |
| rollback | d1085d87c321489d647e7ca60123bc83f24f4d20 | 38bcb32382fb54abf8b4939bd007e5dba73486c984777fb6a28dda98ee522d6a | 54097129 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/626eb011b59544f8b4316e912a853123.json` · evidence SHA256 `28382ffae5c818845e205d6c62552458f3a6d2cd0ec6dff48a01dd5d810cd9ed`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/d80ec94a685e40e8aad41cea5465e2a9.json` · evidence SHA256 `c22aaf3f4140766c41b512a6f9feda2b1003d4fd7231280be206e96c5066258e`.
보관 package2개와 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존한다. 퇴역한 세 번째 관리 ZIP의 전체 보존을 주장하지 않는다.
여유 24889303040bytes(23.18GiB)다.

남은 고정7/8행은 다른 실제 복합 계약/본문 편집, opaque/private C# 명시 계획,
선택 native callee 의존성·다른 원래 import/등록 외부 관측 결합이다. optional 조합을 필수로 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface와 원본 소유권·권한·override 계약·authored layout·최종 CAS를 유지한다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio 및 전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
