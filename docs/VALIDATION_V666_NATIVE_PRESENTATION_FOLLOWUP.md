# 여러 표시 편집 뒤 native 읽기 범위 검증

제품 동결 `4b152d523cd6e30fbb1eebd1f75f5b7f08cc26a2`의 [지원 범위](V666_NATIVE_PRESENTATION_FOLLOWUP.md)를 최종 **신규 47단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet와 기존 seed 복원, 빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 package·구조/무결성 및 ZIP 전체 복원을 검사했다. 개발 단계와 최종 단계를 합산하지 않는다.

- 게시54dc2992에서 저장한 native ABI/body/caller 그룹의 정보 설명·아이콘·두 함수 설명을 다시 저장하면
  원래60개 readGuards가0개가 되고 helper 변경 뒤 Review가 ready임을 재현했다. Confirm하지 않았고 원문은 복원했다.
- 수정 뒤 같은 네 표시 편집은 원래60개 읽기 증거와 source 집합을 그대로 유지한다. 같은 helper 변경의 Review는 거절된다.
  기존 UI의 표시 편집·Undo/Redo·미저장/저장 cold·한 Save·Review 취소/Confirm·실제 Linux 실행을 확인했다.
  ABI·C# 본문·caller는 최초 명시 그룹 그대로이며 계획한 결과40이 유지된다. scalar 입력 ABI 그룹의 같은 표시 보존도 검사했다.
- Save 전 helper 변경은 전체 저장을 거절한다. Review 전과 후 helper/선택 native 선언·본문/caller 변경은
  원래 receipt·checkpoint·peer bytes를 보존하며 거절한다. 정확히 복원·cold·새 Review 뒤 Confirm한다.
  비선택 C# bytes와 최종 Confirm에서 helper 선언·본문의 inode·mode·mtime을 대조했다.
- 누락/변조 readGuards·틀린 owner/version/path·빠진 구현 proof·알 수 없거나 raw/빠진 선언을 거절했다.
  인식할 수 없는 새 편집이나 캡처 밖 함수가 원래 범위를 빈 receipt로 재기준화하지 못한다.
- checkpoint 실패/재시도·Save/조회 응답 유실·반복/취소·owner 경합·늦은 설명의 cold/후속 Save와
  그 직전 peer 변경에서 입력과 원래 읽기 범위를 보존했다. 기존 같은 계약·헤더/ABI·입력/ref·forwarded/private/import 경계를 회귀 검사했다.
  새 package와 전체 추출본의 저장·응답 유실·늦은 입력·실행·실패 수명을 검사했다.

개발 25단계는 실패0이다. 수정 전 재현은 별도 진단 단계이며 Confirm하지 않았다.
최종 단계는 동결 코드에서 모두 새로 실행했다.

과거 구 Reference reader 증거는 해시 대조한 재사용 자료이며 신규 단계에 포함하지 않는다.
같은 게시 세대의 저장·재편집·검토 기준이다. 이전 authoring 세대 호환·자동 migration/downgrade를 주장하지 않는다.
시작 화면 전송8회 관측은 과거 간헐 빈 화면 원인 확정으로 세지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 4b152d523cd6e30fbb1eebd1f75f5b7f08cc26a2 | f2a043797a2d664ecef0262b099f70246c274fef245e8f4fea49a3ddca5b34cf | 54100646 |
| rollback | 8909609b6467cd8e0325cac1f9fae85b77e2067d | 5db5bd1cdeb9a6b9669fe1f33be671b9d9cd6a09fb6049a4f5f9218e39c7cccf | 54099671 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/1472b8d31a9947c38ff0e4a103d9f0a8.json` · evidence SHA256 `9ab0b03759840820ee34c14b0b041144aca95871b1ae4f5592e87e6e40987033`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/c8412f8e677a4d3aa988c17e1a330195.json` · evidence SHA256 `ce8432ac41bf8674341d895316ce265a9a31c8cf8207aec95bc53a41f2c47a35`.
보관 package2개와 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존한다. 퇴역한 세 번째 관리 ZIP의 전체 보존을 주장하지 않는다.
여유 24815108096bytes(23.11GiB)다.

남은 고정7/8행은 원래 UI의 다른 복합 계약/본문·속성 구조 편집,
opaque/private 호출자의 명시 C# 계획, 선택 native callee 의존성과 기존 import/등록 외부 관측 결합으로 묶어 대조한다.
원래 조작의 재현·지원/정상 거절 경계와 회귀 증거를 종료 기준으로 삼고 optional 타입/문맥 조합을 필수로 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface와 원본 소유권·권한·override 계약·authored layout·최종 CAS를 유지한다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio 및 전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
