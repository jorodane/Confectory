# 정보 헤더와 native 계약 공동 저장 검증

제품 동결 `8909609b6467cd8e0325cac1f9fae85b77e2067d`의 [지원 범위](V666_NATIVE_HEADER_CONTRACTS.md)를 최종 **신규 47단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet와 기존 seed 복원, 빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 package·구조/무결성 및 ZIP 전체 복원을 검사했다. 개발 단계와 최종 단계를 합산하지 않는다.

- 게시4306ae42에서 원래 실행·각 native ABI/body single·그 계약-only 그룹·설명/아이콘은 각각 유효하지만
  원래 460px 창의 한 Save는 거절됨을 재현했다. 네 입력과 원래 checkpoint/source는 보존됐다.
- 수정 후 정역순 후보가 같으며, header를 뺀 계약/body 후보와 비소유자 변경 footprint·텍스트가 같다.
  소유 정보의 설명·아이콘과 이미 지원한 명시 계약/본문/caller를 한 후보/CAS에 연결한다.
- out/반환의 long→double·명시 기존 호환 출력 대응과 소유 헤더를 실제 UI로 선택했다.
  공유 caller38→40과 provider 반환1.75D/out1.25D·35L을 실제 실행했다.
  별도 scalar 입력 ABI 교체의 owner 표시 결합도 같은 원래 single 계획과 footprint로 검증했다.
- 중복/틀린 표시·길이 초과·잘못된 아이콘·구조/알 수 없는 행·소유권 밖/미완성/stale 본문·caller·틀린 소비 대응은 전체 거절했다.
  기존 설명/이미지 검증·예산·직접 소유/공개 override 계약·권한을 넓히지 않는다.
- 기존 UI의 설명/아이콘·명시 계약·본문 취소/저장·Undo/Redo·미저장/저장 cold·Review 취소/Confirm·실행을 검사했다.
  checkpoint 실패/재시도·Save/조회 응답 유실·owner 경합·반복 Save 보호와 늦은 설명의 cold·후속 Save·Confirm·실행을 확인했다.
  저장된 그룹의 늦은 설명을 다시 Save하기 직전 owner가 바뀐 경우에도 peer·늦은 입력·기존 checkpoint를 보존했다.
- 후속 정보/함수 설명 Save는 새 ABI와 version3 readGuards를 유지한다. 누락/변조 receipt는 거절한다.
  Save 전 helper 선언과 Review 후 helper 선언/본문·caller graph·선택 native 선언/본문 변경은 Confirm 전체 거절이다.
  정확한 복원·cold·새 Review 뒤 Confirm한다. 비선택 원문 bytes를 대조했고 helper 선언·본문은 최종 Confirm에서 inode·mode·mtime도 유지한다.
- header 없는 기존 out·반환 복합 타입 native/API/UI, 입력 복합 UI와 같은 계약 header/body UI 및
  forwarded·중첩·ref·private/import 경계를 새 코드에서 회귀 검사했다. 새 package와 전체 추출본의 저장·응답 유실·늦은 입력·실행·실패 수명을 검사했다.

개발 27회(26통과/fixture실패1) 중 실패는 Save 전 fixture의 이전 입력 수 판정이었다. 함수2개만 세던 late/conflict 판정을 owner 설명·아이콘을 포함한4개로 수정했다. 당시 applySlots 요청은 없었고 제품 코드는 바꾸지 않았다. 실패 증거와 수정 후 late 통과를 함께 보관했으며 이미 통과한13단계는 반복하지 않았다. 최종 단계는 동결 코드에서 모두 새로 실행했다.
과거 구 Reference reader 증거는 해시 대조한 재사용 자료이며 신규 단계에 포함하지 않는다.
같은 게시 세대의 저장·재편집·검토 기준이다. 이전 authoring 세대 호환·자동 migration/downgrade를 주장하지 않는다.
시작 화면 전송8회 관측은 과거 간헐 빈 화면 원인 확정으로 세지 않는다.
최종 대기 호출 중단 뒤에도 같은 record와 실제 worker identity를 확인해 기존 검증을 계속했으며 재시작하지 않았다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 8909609b6467cd8e0325cac1f9fae85b77e2067d | 5db5bd1cdeb9a6b9669fe1f33be671b9d9cd6a09fb6049a4f5f9218e39c7cccf | 54099671 |
| rollback | 96abb70b9dbb647334e4abda4a7d215da1b13f64 | 1c7d60ce0ac034c593acc211176d0f5eaec49994eb7faf810da2b10cf3518110 | 54099997 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/bc7d4feba642496e96030c6498b4866b.json` · evidence SHA256 `1b9a9db451fbb760fb325b7997ac658b3c5da75f93f04224f33469e3ea74e331`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/1a6e7bcca0c9443ea46e726902a2439d.json` · evidence SHA256 `7f9a571e317ca99820c7e7ab4b19278eedf4d49f242aeccaafc1f8a48d79b295`.
보관 package2개와 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존한다. 퇴역한 세 번째 관리 ZIP의 전체 보존을 주장하지 않는다.
여유 24836718592bytes(23.13GiB)다.

남은 고정7/8행은 원래 UI의 다른 복합 계약/본문·속성 구조 편집,
opaque/private 호출자의 명시 C# 계획, 선택 native callee 의존성과 기존 import/등록 외부 관측 결합으로 묶어 대조한다.
원래 조작의 재현·지원/정상 거절 경계와 회귀 증거를 종료 기준으로 삼고 optional 타입/문맥 조합을 필수로 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 구조체·종류 enum·모듈 interface와 원본 소유권·권한·override 계약·authored layout·최종 CAS를 유지한다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio 및 전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
