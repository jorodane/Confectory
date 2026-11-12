# 명시 native out·반환 타입 검증

제품 동결 `96abb70b9dbb647334e4abda4a7d215da1b13f64`의 [지원 범위](V666_NATIVE_OUTPUT_MIX.md)를 최종 **신규 46단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet와 기존 seed 복원, 빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 package·구조/무결성 및 ZIP 전체 복원을 검사했다. 개발 단계와 최종 단계를 합산하지 않는다.

- 게시19e6e0ed에서 원래 실행과 각 single out·반환 타입/본문/caller 선택은 유효하지만 공유 공동 후보가 거절됨을 재현했다.
  수정 후 정역순 공동 후보가 동일하며 원래 hash·caller ABI/profile·노드 ID·실행선을 유지한다.
- 기존 상세창에서 out count와 반환의 long→double을 함께 선택하고 out long saved와 입력 amount/real을 유지했다.
  기존 호출 계약 창에서 원래 count/return 소비를 saved로 직접 대응한다. C# 본문은 count=real;
  saved=helper(amount+2); return real+0.5를 직접 작성한다. 캐스트·변환 함수·기본값·자동 해제는 생성하지 않는다.
- 실제 IInvoke 반환40L→1.75D, out34L/37L→1.25D/35L와 공유 caller38→40을 실행했다.
  다른 함수에 out만/반환만 선택한 원래 single 계획도 각각 검증한 뒤 정역순으로 합성했다.
- 누락/틀린 소비 대응·유지 출력 identity 변경·입력/역할/이름/핀 수·void 전환·stale 선언/본문/caller·잘못된 C#은 전체 거절했다.
- 기존 460px UI의 타입·명시 소비 대응·본문 취소/저장·Undo/Redo·미저장/저장 cold·Review 취소·Confirm·실행을 검사했다.
  checkpoint 실패/재시도·Save/조회 응답 유실·owner 경합·반복 Save 보호와 늦은 설명의 cold 복원·후속 Save·Confirm·실행을 확인했다.
- 후속 정보/함수 설명 저장은 새 ABI와 version3 readGuards를 유지한다. 누락·변조 receipt는 거절했다.
  Save 전 helper 선언과 Review 후 helper 선언/본문·caller graph·선택 native 헤더/본문 변경은 Confirm 전체 거절이다.
  정확한 복원·cold·새 Review 뒤 Confirm한다. 모든 비선택 원문 bytes를 대조했고 helper 선언·C# 본문은 최종 Confirm에서 inode·mode·mtime도 보존한다.
  선택한 본문만 명시한 새 텍스트로 반영했다.
- 기존 out 타입 native/API/UI, 반환 타입 native/UI 및 입력 정의·타입 UI와 forwarded·중첩·ref·private/import 경계를 새 코드에서 회귀 검사했다.
  새 package와 전체 추출본의 저장·응답 유실·늦은 입력·실행·패키지 실패 수명을 검사했다.

개발 24단계는 실패0이다. 최종 단계는 동결 코드에서 모두 새로 실행했다.
과거 구 Reference reader 증거는 해시 대조한 재사용 자료이며 신규 단계에 포함하지 않는다.
같은 게시 세대의 저장·재편집·검토 기준이다. 이전 authoring 세대 호환·자동 migration/downgrade를 주장하지 않는다.
시작 화면 전송8회 관측은 과거 간헐 빈 화면 원인 확정으로 세지 않는다.
개발 중 일시적인 exec transport 연결 오류는 실제 읽기로 작업 트리·기존 프로세스 보존과 정상 완료를 확인했다.
프로세스 생성 전에 거절된 명령만 미실행임을 확인한 뒤 수행했으며 빌드나 검증을 중복 시작하지 않았다.
최종 대기 호출 중단 뒤에도 같은 최종 record와 실제 worker identity를 확인해 기존 검증을 계속했으며 재시작하지 않았다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 96abb70b9dbb647334e4abda4a7d215da1b13f64 | 1c7d60ce0ac034c593acc211176d0f5eaec49994eb7faf810da2b10cf3518110 | 54099997 |
| rollback | 19d6501aa8ed9f74dd58cb1f171bff80d5d6c2ae | e8e737d53446a8082a1f3d0fabf0e462975f4ac8516bc37a0b90e1391faa07ff | 54097359 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/c134a22b5da34bf5a97918c5897c2887.json` · evidence SHA256 `ad365deb07616dbedf265d5a074654e3963d2b0fbaeb17c2902684c204b247b5`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/cbf38d21ce004daca24bc7d44a0d68f6.json` · evidence SHA256 `955c05e2384a9e4488cb5195a5735aabf7f94c3118a72e3c5b46a43cceb83bfa`.
보관 package2개와 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존한다. 퇴역한 세 번째 관리 ZIP의 전체 보존을 주장하지 않는다.
여유 24865120256bytes(23.16GiB)다.

남은 고정7/8행은 원래 UI의 복합 계약/본문·다른 속성 공동 편집(입출력 동시 편집·출력 정의/void·타입 결합 포함),
opaque/private 호출자의 명시 C# 계획, 선택 native callee 의존성과 기존 import/등록 외부 관측 결합으로 묶어 대조한다.
원래 조작의 재현·지원/정상 거절 경계와 회귀 증거를 종료 기준으로 삼고 optional 타입/문맥 조합을 필수로 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface와 원본 소유권·권한·override 계약·authored layout·최종 CAS를 유지한다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio 및 전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
