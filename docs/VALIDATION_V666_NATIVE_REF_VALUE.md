# 원래 native C# ref→값 전환 검증

제품 동결 `1b84fef81084a987352f4d8c158f9eb8b9f52fc3`의 [지원 범위](V666_NATIVE_REF_VALUE.md)를 최종 **신규 43단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet와 빈 엔진 cache의 Release/MCP 및 실제 Linux 엔진,
새 Windows 교차 package·구조/무결성·전체 ZIP 복원을 실행했다. 기존 NuGet seed를 복사해 restore했다.
개발 단계와 최종 신규 단계를 합산하지 않는다.

- 게시70a0의 두 단일 ref→값 후보와 원래 ref ABI/저장소 효과는 유효하나 공동 후보만 거절됨을 재현했다.
  수정 후 정역순 후보가 같고 원래 hash·바인딩·ID·경로를 유지한다.
- 기존 C# 창의 밝은 매개변수에서 ref를 값으로 명시 전환하고, 원래 caller의 입력과 출력을 identity로 직접 선택한다.
  새 입력/리터럴/임시 ref 저장소·자동 해제는 만들지 않는다. caller 자체의 long/ref long→long 계약은 유지한다.
- 같은 임시 Main이 실제 두 IInvoke의 CLR 매개변수와 반환을 검사했다. 두 번째 매개변수는 long&→long,
  IsOut은 전후 false다. provider는 원래 count를 읽고 더한 뒤 반환하는 C# 그대로이며 반환38은 동일하다.
  반사 호출 인자 저장소는 전환 전38로 바뀌고 전환 후5로 남는다. 공유 caller의 두 호출에서 반환은79→46,
  caller ref 셀은79→5다. 이는 명시한 ref→값의 쓰기 전달 제거에 따른 결과이며 결과 보존을 주장하지 않는다.
- 새 ref 생성·혼합 방향·타입/이름/수/반환 변경, 잘못된 native 선언·hash·C#,
  누락/변조된 caller·입력·출력·문맥은 전체 거절했다. 원래 count를 리터럴/다른 입력으로 바꾸거나
  해제하는 계획도 이 identity 단위에서 거절한다. UI 새 ref/혼합 방향 거절과 취소 시 입력 보존을 검사했다.
- 원래460px UI의 취소·Undo/Redo·미저장/저장 cold, checkpoint 실패/재시도,
  Save/settlement 응답 유실·owner 경합·반복 Save 비활성·지연 응답 중 새 설명 보존을 검사했다.
  늦은 입력은 cold에서 복원되고 다음 명시 Save·Review 취소·새 Confirm으로 함께 반영된다.
- 후속 정보/기능 설명 Save가 변경 ABI·unchanged body read member·version3 readGuards를 유지한다.
  receipt 전체/일부 누락 및 hash/path/owner/version/implementation proof 변조는 거절했다.
  Save 전 helper 변경과 Review 뒤 helper 선언/본문·caller graph·native 본문/선언 변경은 Confirm 전체 거절이며
  peer·checkpoint·원래 receipt를 유지했다. 정확한 원본 복원·cold·새 Review/Confirm은 실행까지 통과했다.
  C#의 UTF8 BOM·CRLF·bytes·inode·mode·mtime도 유지했다.
- 기존 ref→out 후보/API·입력 타입·retained/forwarded·중첩·ref·private/import 경계와
  retained ref→값 UI 및 일반 C# 본문 편집을 현재 코드에서 새로 회귀 검사했다.
  package/전체 복원본의 저장·응답 유실·늦은 입력·Confirm·실행과 package 실패 수명도 통과했다.
  시작 전송8회 reload·단절·child/root/프로젝트 왕복은 관측 결과이며 과거 빈 #app의 원인은 미확정이다.

개발 24단계 중 최초 UI 공동 Save1건이 실패했다. 출력 목록이 같은 ref→값 전환에서 UI가 필수 identity 출력 대응을 생략한 제품 결함이었다. UI를 수정하고 후보/거절 및 UI 검사를 새 이름으로 재실행해 통과했으며 실패 로그도 보존했다. 최종은 동결 코드에서 전부 새로 실행해 실패0이다.
[구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시 대조한 과거 증거이며 신규 단계 수에 포함하지 않는다.
새 group 저장·재편집·Review는 같은 게시 세대 도구 기준이다. 이전 authoring 세대와의 호환이나
자동 migration/downgrade를 주장하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 1b84fef81084a987352f4d8c158f9eb8b9f52fc3 | 8ac5535669750826d3d650f2c85822ce2c4db2d11556d025fbe8e47ac766d2bd | 54092791 |
| rollback | c04ee2d0acfce87ea538ae537bad8f4e28661977 | c537414d1d6c2e30b8454856e9b597101805141fc5f7dbbfe6c328467a9f1e68 | 54091839 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/ab2cdbaa33904b8eac3f7053a7cc0162.json` · evidence SHA256 `a2abd3a97842aadc7660600b3f2dfef0a01301d576d01a0dfa522c64638fb314`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/6898fb96ded043999bcb5d1b70a0b020.json` · evidence SHA256 `33aff0f75b63bd1fd4492acf96624d1661077153365491e215bc9975b52e3b98`.
관리 package2개와 증거 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존했다. 퇴역한 세 번째 관리 ZIP 전체의 보존은 주장하지 않는다.
여유 25035542528bytes(23.32GiB)다.

남은 고정7/8행은 실제 기존 저장소를 요구하는 값/out→ref, 값 입력 추가/삭제 등 정의 결합,
opaque/private 명시 C# 계획과 선택 native callee 사이 의존성/다른 원래 import·등록 외부 관측 결합이다.
optional 조합을 필수로 늘리지 않고 M11/M12/M4를 회귀 없이 다시 열지 않는다.
권한·override 계약·authored layout·Review/Confirm·최종 CAS 및 기존 예산을 유지했다.
실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 전수 검증은 수행하지 않았다.
새 credential/grant·과금·main 변경은 없다.
