# 명시 native out 삭제 공동 저장 검증

제품 동결 `f0b9ac9b146699da582008c44bd9069ecced3d95`의 [지원 범위](V666_NATIVE_OUT_REMOVAL.md)를 **최종 신규 41단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. 확인한 기존 NuGet seed를
각 격리 환경에 복사해 restore했다. 개발과 최종 단계 수는 합산하지 않는다.

- 게시0f8ec796에서 원래 실행38과 각 단일 out 삭제/본문/기존 소비자의 명시 return 대응은
  유효하지만 공동 후보만 거절되는 것을 재현했다. 기존 상세창에서 count를 삭제하고
  모든 원래 출력의 대응과 새 C# 선언·본문을 직접 검토한다. 입력·남은 out·반환 계약은 유지한다.
- 같은 임시 Main 원문으로 실제 생성된 두 IInvoke의 CLR 매개변수 수·타입·반환값을 확인했다.
  원래 long40/out long34, 변경 후 long34·out 매개변수 부재이며 caller는 전후38이다.
  첫 old count를 쓰던 둘째 amount와 둘째 old count를 쓰던 caller 반환만 직접 선택한
  compatible long return으로 대응한다. 새 본문은 helper 호출의 long 반환을 직접 작성한다.
  암묵 소비 삭제·새 바인딩·C# 자동 재작성이나 제품 코드 생성의 reflection 대체는 없다.
- 단일·정역순 공동 후보·원래 쓰기 hash·한 그룹을 검증했다. 역할·반환/입력 타입·이름·수,
  삭제한 out의 identity/누락 mapping, 본문/호출 계획 누락·stale hash·잘못된 native 선언,
  삭제한 count를 사용하는 C#, 잘못된 출력 대응·새 입력·caller hash·문맥 삽입의19개 fault는
  전체 거절했다. 기존 out 타입 변경의 후보·후속 정보/함수 설명 Save·원본 경합, 입력 타입·
  forwarded/opaque 보존·ref·private 이름·로컬 import 회귀도 최종 코드에서 새로 실행했다.
- 기존 상세창의 삭제·출력 대응·본문 UI에서 취소·Undo/Redo·미저장/저장 cold·checkpoint
  실패/재시도·owner 경합·Save/settlement 응답 유실을 확인했다. 실제 trusted Save의
  활성화/거절과 복원을 검증하며 이미 발행된 명령을 임의 재실행하지 않았다.
- 후속 정보/함수 설명 Save는 out이 삭제된 정확한 ABI·본문·caller 그룹과 version3
  readGuards를 유지했다. 저장된 선언 hash·원래 source 증거 아래에서 삭제 형태를 인증하며
  원본이나 새 계획을 추정하지 않는다. guard 전체/일부 누락·hash/path·관측 밖 경로·owner/
  version·implementation proof 누락은 거절했다. Save 전 helper 선언 변경과 Review 뒤
  helper 선언·본문/caller graph/선택 native 본문·선언의5경로 변경은 Confirm 전체 거절이었다.
  peer·checkpoint·원래 receipt와 입력을 유지했고 정확한 복원·cold 뒤 새 Review/Confirm은
  실제 out 부재·반환값·실행38을 확인했다. helper의 bytes·inode·mode·mtime도 유지했다.
- 성공 Save 응답 지연 중 추가한 실제 설명은 반복 Save 비활성 동안 남고 cold에서 복원됐다.
  후속 명시 Save·Review 취소·새 Confirm·cold는 삭제 계약·두 본문과 설명을 함께 보존했다.
  새 package와 전체 복원본에서도 저장·응답 유실·늦은 입력·실행을 확인했다.
- 현재3D 전송의 정체/부분 POST·reload8회·단절·child/root·프로젝트 왕복/cold와 package
  실패 수명을 검사했다. 과거 간헐 빈 #app의 원인을 확정한 증거로 세지 않는다.

개발 19단계는 모두 통과했고 개발 실패는0건이다. 최종은 현재 동결 코드에서
전부 새로 실행했다. [구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시를
대조해 개발 증거에 보관한 과거 증거 재사용이며 이번 최종 수에 포함하지 않는다.
새 그룹의 저장·재검토는 같은 게시 세대 도구 기준이며 이전 authoring 세대의 새 그룹
재편집/검토 호환은 주장하지 않는다. 새 문법·자동 migration/downgrade·기존 profile 삭제는 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | f0b9ac9b146699da582008c44bd9069ecced3d95 | ea8eb091095c612f4f2d981d8c20609c3dd88ee676e30734cff991f4c1ecdc75 | 54086948 |
| rollback | 56465896ba241f64ae2d7c09fe7c333e4067bc9f | 2e22e37e9e06d144a04a7764696f0dfa17ea1e9ca36e7fbe4e798de370a20b26 | 54085083 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/f4ba3981c85b44098c62a702a1d79dac.json` · evidence SHA256 `a4e0cadf6d5e7415e5ab3bf5d4a1c89f185c1f5c058a5c5cd83b10b911a85af4`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/bb2deb24a2a94ba4903be0622904ea60.json` · evidence SHA256 `d0371076680ec870b8773bb6b5b6102484aa18c9694a2b55a32c5ac508886852`.
두 관리 package와 증거 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와
이번 소유 RAM 임시물 정리만 적용했다. 원래 checkout/main·비관리 자료·과거 증거는 유지한다.
퇴역한 세 번째 관리 ZIP 전체의 보존은 주장하지 않는다. 여유 25133191168bytes(23.41GiB)다.

역할 전환 UI·out 추가/다른 입출력 정의 변경, opaque/private 명시 C# 계획, 선택 native callee
사이 의존성과 다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다. 조합별 migration을
새 필수로 늘리거나 M11/M12/M4를 회귀 없이 다시 열지 않는다. 부모/외부 직접 편집 거절은
원래 소유권 보호다.64-member Review·240 source checks·2048 known source 예산, 권한·override
계약·authored layout·Review/Confirm·최종 CAS를 유지했다. 실제 Windows/WebView2·물리 기기·
IME·GPU/audio·전체 UI 전수 검증은 수행하지 않았다. 새 credential/grant·라이브 AI/과금·main 변경은 없다.
