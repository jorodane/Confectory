# 명시 native out 추가 공동 저장 검증

제품 동결 `bb15884c90602cb54473af1f95505e4f04fffcf2`의 [지원 범위](V666_NATIVE_OUT_ADDITION.md)를 **최종 신규 41단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. 확인한 기존 NuGet seed를
각 격리 환경에 복사해 restore했다. 개발과 최종 단계 수는 합산하지 않는다.

- 게시39c39406에서 원래 실행38과 각 단일 out 추가/본문/기존 출력 identity 후보는 유효하지만
  공동 후보만 거절되는 것을 재현했다. 기존 상세창에서 새 out 이름·타입을 고르고 원래
  호출 계약과 새 C# 선언·본문을 직접 검토한다. 원래 입력/out·반환·소비자 연결은 유지한다.
- 같은 임시 Main 원문으로 실제 생성된 두 IInvoke의 CLR 매개변수 수·타입·값을 확인했다.
  원래 long34·out 부재, 변경 후 long34/out double1.25이며 caller는 전후38이다.
  원래 첫 반환을 쓰는 둘째 amount와 최종 반환·원래 모든 binding/route는 동일하다.
  새 out은 직접 작성한 `count=real`로 할당하며 원래 소비자에 자동 연결하지 않는다.
  새 기본값·바인딩·C# 자동 재작성이나 제품 코드 생성의 reflection 대체는 없다.
- 단일·정역순 공동 후보·원래 쓰기 hash·한 그룹을 검증했다. 역할·반환/입력 타입·이름·수,
  가상의 이전 out/누락 mapping, 본문/호출 계획 누락·stale hash·잘못된 native 선언,
  할당 전 out을 사용하는 C#, 잘못된 원래 출력 대응·새 입력·caller hash·문맥 삽입의19개
  fault는 전체 거절했다. 기존 out 삭제의 후보·후속 정보/함수 설명 Save·원본 경합,
  입력 타입·forwarded/opaque 보존·ref·private 이름·로컬 import 회귀도 새로 실행했다.
- 기존 상세창의 추가·이름/타입 선택·원래 출력 대응·본문 UI에서 취소·Undo/Redo·미저장/
  저장 cold·checkpoint 실패/재시도·owner 경합·Save/settlement 응답 유실을 확인했다.
  실제 trusted Save의 활성화/거절과 복원을 검증하며 이미 발행된 명령을 임의 재실행하지 않았다.
- 후속 정보/함수 설명 Save는 새 out을 가진 정확한 ABI·본문·caller 그룹과 version3
  readGuards를 유지했다. 저장된 선언 hash·원래 source 증거 아래에서 추가 형태를 인증하며
  원본이나 새 계획을 추정하지 않는다. guard 전체/일부 누락·hash/path·관측 밖 경로·owner/
  version·implementation proof 누락은 거절했다. Save 전 helper 선언 변경과 Review 뒤
  helper 선언·본문/caller graph/선택 native 본문·선언의5경로 변경은 Confirm 전체 거절이었다.
  peer·checkpoint·원래 receipt와 입력을 유지했고 정확한 복원·cold 뒤 새 Review/Confirm은
  실제 새 out·반환값·실행38을 확인했다. helper의 bytes·inode·mode·mtime도 유지했다.
- 성공 Save 응답 지연 중 추가한 실제 설명은 반복 Save 비활성 동안 남고 cold에서 복원됐다.
  후속 명시 Save·Review 취소·새 Confirm·cold는 추가 계약·두 본문과 설명을 함께 보존했다.
  새 package와 전체 복원본에서도 저장·응답 유실·늦은 입력·실행을 확인했다.
- 현재3D 전송의 정체/부분 POST·reload8회·단절·child/root·프로젝트 왕복/cold와 package
  실패 수명을 검사했다. 과거 간헐 빈 #app의 원인을 확정한 증거로 세지 않는다.

개발은 20시도 중 19통과·해결된 검사 실패1건이다. 최초 UI 검사에서 새 out의
편집 ID를 arg2로 가정했으나 기존 화면은 crypto.randomUUID()를 사용했다. 최초 실패 요청·
검사 원문과 제품 UI source hash를 보존했다. 제품 변경 없이 새 non-return 출력 행을 선택하고
실제 UUID·화면 증거를 기록하도록 고쳐 corrected UI를 통과했다. 최종은 동결 코드에서 새로 실행했다. [구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시를
대조해 개발 증거에 보관한 과거 증거 재사용이며 이번 최종 수에 포함하지 않는다.
새 그룹의 저장·재검토는 같은 게시 세대 도구 기준이며 이전 authoring 세대의 새 그룹
재편집/검토 호환은 주장하지 않는다. 새 문법·자동 migration/downgrade·기존 profile 삭제는 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | bb15884c90602cb54473af1f95505e4f04fffcf2 | ba6c935e1fa1cf7579dff1a00152cc55085d86ac6e03a93c0bf0a66d9b7200ff | 54087362 |
| rollback | f0b9ac9b146699da582008c44bd9069ecced3d95 | ea8eb091095c612f4f2d981d8c20609c3dd88ee676e30734cff991f4c1ecdc75 | 54086948 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/6e37a64053654747a4d656dad7fba51a.json` · evidence SHA256 `b15d18ebb6870f8385a3ea0a6e54d9aed71256384daaef2d39a19b67c1472325`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/895430a00e624fa694f2e6429b57f97f.json` · evidence SHA256 `f4b4b80e6bf0c7b4328c105de767515be51602fc7b04ae6af3a758056a4f42f1`.
두 관리 package와 증거 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와
이번 소유 RAM 임시물 정리만 적용했다. 원래 checkout/main·비관리 자료·과거 증거는 유지한다.
퇴역한 세 번째 관리 ZIP 전체의 보존은 주장하지 않는다. 여유 25116880896bytes(23.39GiB)다.

역할 전환 UI·다른 입출력 정의 결합, opaque/private 명시 C# 계획, 선택 native callee 사이
의존성과 다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다. 조합별 migration을
새 필수로 늘리거나 M11/M12/M4를 회귀 없이 다시 열지 않는다. 부모/외부 직접 편집 거절은
원래 소유권 보호다.64-member Review·240 source checks·2048 known source 예산, 권한·override
계약·authored layout·Review/Confirm·최종 CAS를 유지했다. 실제 Windows/WebView2·물리 기기·
IME·GPU/audio·전체 UI 전수 검증은 수행하지 않았다. 새 credential/grant·라이브 AI/과금·main 변경은 없다.
