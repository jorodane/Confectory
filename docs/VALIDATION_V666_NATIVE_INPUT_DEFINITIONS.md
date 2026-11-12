# 명시 native 입력 삭제·추가 검증

제품 동결 `d1085d87c321489d647e7ca60123bc83f24f4d20`의 [지원 범위](V666_NATIVE_INPUT_DEFINITIONS.md)를 최종 **신규 46단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet와 기존 seed 복원, 빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 package·구조/무결성 및 ZIP 전체 복원을 검사했다. 개발 단계와 최종 단계를 합산하지 않는다.

- 게시fe8202c4에서 원래 실행과 각 single 입력 삭제/추가·본문·caller 선택은 유효하지만 공유 공동 후보는 거절됨을 재현했다.
  수정 후 정역순 공동 후보가 동일하고 원래 hash·노드 ID·실행선·반환 연결을 유지한다.
- 상세창에서 long amount를 삭제하고 long step을 추가했다. 남는 double real과 nativeReal 별칭·값1.25/2.5 및 caller 자체 ABI/profile은 유지한다.
  root 입력/앞 호출 결과의 원래 amount 연결을 정확히 해제하고 두 호출의 새 값5/7을 각각 직접 선택한다.
  C# 본문은 직접 작성한 텍스트이며 변환·캐스트·기본값을 자동 생성하지 않는다.
- 실제 IInvoke에서 인자는 long/double→double/long으로 바뀐다. 새 step 값5를 전달해 provider 반환34→9를 확인하고,
  서로 다른 새 값5/7을 사용하는 공유 caller38→12를 실행했다. 남는 입력과 새 값의 실제 전달을 검증했다.
- 누락/틀린 원래 해제·새 값 누락/틀린 타입·암묵적 기존 입력 재사용·남는 별칭/타입/이름/역할/순서 변경·stale 원본과 잘못된 C#은 전체 거절했다.
  출력 재대응이나 누락된 본문/caller 선택도 원본 변경 없이 거절했다.
- 460px UI의 삭제/추가·명시 해제/값 선택·본문 취소/저장·Undo/Redo·미저장/저장 cold·Review 취소·Confirm·실행을 검사했다.
  checkpoint 실패/재시도·Save/조회 응답 유실·owner 경합·반복 Save 보호 및 늦은 설명의 cold 복원·후속 Save·Confirm·실행을 검사했다.
- 후속 정보/함수 설명 저장은 새 ABI와 version3 readGuards를 유지한다. 누락·변조 receipt는 거절했다.
  Save 전 helper 선언 변경과 Review 후 helper 선언/본문·caller graph·선택 native 헤더/본문 변경은 Confirm 전체 거절이다.
  정확한 복원·cold·새 Review 뒤 Confirm한다. 모든 비선택 원문 bytes를 대조하고 helper 선언·C# 본문은 최종 Confirm에서 inode·mode·mtime도 보존한다.
  선택한 본문은 명시한 새 텍스트로 반영한다.
- 기존 입력 삭제의 native/API/UI와 입력 추가·out→ref UI, 입력 타입·forwarded·중첩·ref·private/import 경계를 새 코드에서 회귀 검사했다.
  새 package와 전체 추출본의 저장·응답 유실·늦은 입력·실행·패키지 실패 수명을 검사했다.

개발 27회 중 초기 receipt 검사1회가 실패했다. 새 삭제/추가 경로의 후속 설명 Save 뒤 readGuards 누락이 허용됨을 재현했다.
인자 수가 같을 때 위치별 타입 교체로만 판단해 남는 입력 식별자를 잃던 retained-source 인증을 수정했다.
기존 위치별 이름 편집을 유지하고 정확한 남는 식별자로 인증하며, 원래 source/binding 동의나 기준 파일을 재구성하지 않는다.
변경된 검증 엔진을 빌드한 뒤 같은 receipt 검사와 나머지 검증이 통과했다. 초기 실패·원인·수정 해시 증거를 보존했다.
최종 46단계는 수정된 동결 코드에서 모두 새로 실행해 실패0·재사용0이다.
과거 구 Reference reader 증거는 해시 대조한 재사용 자료이며 신규 단계에 포함하지 않는다.
같은 게시 세대의 저장·재편집·검토 기준이다. 이전 authoring 세대 호환·자동 migration/downgrade를 주장하지 않는다.
시작 화면 전송8회 관측은 과거 간헐 빈 화면 원인 확정으로 세지 않는다.

최종 도중 읽기 전용 상태 조회가 `exec-server transport disconnected`로 실행 거절됐고 원래 출력 세션은 복구되지 않았다.
명령 접근 복구 뒤 작업 트리·원래 PID·로그·완료 기록을 읽어 34→36→46단계 진행을 확인했다.
검증을 재시작하지 않았으며 최종 완료 기록은 exit0이다. 연결 실패의 원인은 미확정이고 관련 관측을 최종 증거 ZIP에 보존했다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | d1085d87c321489d647e7ca60123bc83f24f4d20 | 38bcb32382fb54abf8b4939bd007e5dba73486c984777fb6a28dda98ee522d6a | 54097129 |
| rollback | 4f3e79b0c1c8cccc441175f4c6d5fc397d30f763 | c9984cb254c6d8629ef8f0c7c0e856d60258d013c527e6fac628f6f1a25c894c | 54093606 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/b7f309c885884f8e9dc45f4505edb920.json` · evidence SHA256 `60a08df7831959c88453cf63721b37641d08fc510a82b424506d9f955d45a878`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/5e9ef83a27e74657bc6c981d7df16113.json` · evidence SHA256 `775b22c2231f1ebe620a094fbc81e2e802f1c0e0b6c985b04fb8ca3a4505d527`.
보관 package2개와 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존한다. 퇴역한 세 번째 관리 ZIP의 전체 보존을 주장하지 않는다.
여유 24913031168bytes(23.20GiB)다.

남은 고정7/8행은 기존 명세의 다른 실제 복합 계약/본문 편집, opaque/private C# 명시 계획,
선택 native callee 의존성·다른 원래 import/등록 외부 관측 결합이다. optional 조합을 필수로 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface와 원본 소유권·권한·override 계약·authored layout·최종 CAS를 유지한다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio 및 전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
