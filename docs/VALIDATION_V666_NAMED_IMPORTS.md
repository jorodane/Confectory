# 공개 이름·native 본문과 로컬 import 검증

제품 동결 `c83e9cae180787323d9d19184d67852b15a72028`의 [지원 범위](V666_NAMED_IMPORTS.md)를 **신규 28단계·동등 재사용 10단계·총 38단계·최종 실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. 개발과 최종 수는 합산하지 않는다.

- 게시20a2a4e1에서 두 native 함수의 각 명시 이름/본문 후보와 실제 원래 프로그램46은
  유효하지만 공동 후보만 import 일괄 제한으로 거절되는 것을 재현했다. 기존 C# 이름
  모드에서 amount→leftAmount를 대응하고 두 본문을 직접 편집했다. 실제 결과는26이다.
- 정·역순 후보와 원래 hash·단일 group, helper가 쓰기 후보에 없음을 검사했다. 원래
  helper의 value+3·CRLF/한글/emoji C# 원문과 선언/구현/alias, native parameter 선언,
  함수/본문/노드 ID·기존 caller 값/실행선/출력 소비자·정확64를 유지했다.
- 타입/역할/잘못된 대응/native 선언 변경, 필수 본문 필드 누락·위조 hash·C# 컴파일
  실패, helper 관측 누락/위조 ID·타입/원문은 전체 거절했다. C# 자동 재작성이나
  helper 쓰기·import/alias 변경·외부 권한 확대가 없다. 기존 ref·private 이름/본문과
  과거 로컬 import 거절 fixture를 새로 회귀했다. 후자는 지원되는 positive로 갱신했다.
- 실제 UI 취소·Undo/Redo·미저장/저장 cold·checkpoint 쓰기 실패/복구·owner 경합과
  apply/settlement 응답 유실을 검사했다. 저장 성공 응답 지연 중 추가한 실제 설명은
  재시작 후에도 남았고 후속 명시 Save·Review 취소/Confirm은 새 설명과 결과26을 확인했다.
- version3 readGuards의 누락·잘못된 hash/path·관측 밖 경로·owner/version 변조를 거절했다.
  후속 설명 Save 뒤에도 정확한 guard와 group이 같았다. Save 전 helper 선언 변경,
  Save 후 cold Review 전 helper 본문 변경, Review 뒤 helper 선언·구현·C# 본문 및
  편집 graph 변경은 전체를 거절했다. peer와 checkpoint·입력을 유지하고 원문 복구·
  cold 뒤 새 Review/Confirm은 성공했다. 변경하지 않은 helper/header의 bytes·inode·
  mode·mtime도 유지했다. 저장된 helper 관측을 새 live 기준으로 재배정하지 않는다.
- 현재 실제3D 전송 정체/부분 POST·reload8회·단절·child/root·프로젝트 왕복·cold와
  패키지 실패 수명을 검사했다. 과거 간헐 빈 #app 원인은 계속 미확정이다.

개발 14단계에서 실패 0건이었다. 원래 재현·전체 후보·실제 UI와
helper source/receipt 경계·후속 Save·늦은 입력/실행 및 과거 fixture 회귀의 증거를 보존했다.
추가 metadata 대조에서 캡처한 함수 hash가 맞고 guard60개가 있는데도 후속 함수 설명의
native guard 선택이 비는 것을 재현했다. 첫 최종 실행의 26개 통과 결과와
진단을 보존하고 의도적으로 중단했으며 패키지 승격은 하지 않았다. 수정 집중
11단계도 모두 통과했다. 이미 캡처한 함수·경로·hash와 동일 계약/identity
map만 metadata로 인정하고, 원래 source scope에서 guard 필요성을 판단한다. 빈/누락 guard나
바뀐 함수 proof로 후속 Save/Review를 통과하지 못한다. 실제 카드·상세창 설명 Save,
후속 cold·Review 취소/Confirm·함수 설명/실행26과 helper 경합을 새로 확인했다.
첫 통과 결과는 위 최종 신규 단계에 재사용하거나 합산하지 않았다.
기존 imported-source 관측과 version3 readGuards·최종 source lease를 재사용하고, 단순
leaf의 빈 추가 guard 의미와64-member·240 read/write·2048 known source·Tree 예산을
유지했다. 기존 원문·override 계약·권한·Review/Confirm·CAS·authored layout도 유지한다.
새 receipt 필드/문법·import 편집기·provider 선택이나 미결 정책을 추가하지 않았다.

두 번째 최종 실행에서는27개가 통과하고 CRLF 경합 UI 관찰1개가 시간 초과였다. 보관한
화면은 Ready·두 입력 보존 상태이며 applySlots 요청과 오류 표시가 없었다. 이 결과를 제품
거절 성공으로 세지 않았다. 실제 trusted pointer/click과 handler·연결 상태를 기록하고,
peer schema를 읽은 뒤 명시 Save의 경합 거절을 확인하도록 검사했다. 새 경합 재현
6단계도 통과했다. 재시도는 trusted click도 명령도 발행되지 않고
checkpoint·입력이 동일할 때의 미전달 UI 동작 한 번만 허용한다. 제품 코드는02e6c4ed와
동일하며 새 제품 패치로 이 UI 관찰을 고쳤다고 주장하지 않는다.

새 [재사용 검증](../tools/verification_named_imports_reuse.py)은 기록/ZIP/결과·SDK/NuGet·
LF/CRLF 독립 checkout과 변경된 전체 파일을 검사한다. runner의 conflict-only 분기를
제외한 기존 경로·Python 의존성·제품이 같아야 하며 SDK/제품 변경은 negative로 거절한다.
10개 통과 사실만 재사용하고 실패 경합·변경 검사·빌드·새 패키지·모든 복원은 새로 실행했다.
따라서 최종은 신규28·재사용10·총38이며 이전 실패/중단과 분리한다.
초기화/전송 관찰은 이 재사용 중 하나이며 과거 빈 화면 원인 확정이 아니다.


구 Reference TYPE 거절과 optional 문자열 metadata의 [기존 바이너리 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는
개발 evidence에서 SHA만 다시 확인했다. 구 reader 신규 실행이 아닌 과거 증거 재사용이며
위 최종 단계 수와 별개다. 같은 게시 세대 reader/authoring/runtime을 사용하며 자동
migration/downgrade·소급 수정이나 원문/profile 삭제는 하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | c83e9cae180787323d9d19184d67852b15a72028 | eda7c56ef9b92480821f84eb97a02b68b9c0731e6eede6154a9f89693d75e762 | 54076804 |
| rollback | 6ff8c0765d72f7664b64c76b803137f5401de6d0 | c7a433a7af800230a171bbd72d7930ebf1b9497dacf0382e4705658483052788 | 54080336 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/042f0f0872104649a622ec7a2f7b65ab.json` · evidence SHA256 `43698606a16df773b6142d3c4edefb37312c1023fbefa6fd0659d66be1a41c18`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/0989f35eb22b46ec804feee6c6ff8c61.json` · evidence SHA256 `662c89b58fd9c2c20ff9d715ad34fc5b7de9436aee8aa7d73f7afa46f6d67e88`.
수정 집중 record `/workspace/artifacts/v536-verification-managed/runs/b9ea9d3712d745d2abe6c7e1c19d31b9.json` · evidence SHA256 `1e43f375a15703009a103cc2b7e44cd4ca0151464d764c741a6c42ace5570330`.
중단 첫 최종 record `/workspace/artifacts/v536-verification-managed/runs/edaffd3dc43d4568bb56252a088c6674.json` · evidence SHA256 `c5d75909a9bd31baf2f692b56edc78d549b99864bff78ad6fb1ee72e55cf53b6`.
두 번째 최종 record `/workspace/artifacts/v536-verification-managed/runs/8ad6576d204a471b8f74cfbe0451b52f.json` · evidence SHA256 `ffda62df521fea319326364a1bb8a6923595b424869d841a77f1307b6a8b1d24`.
경합 재현 record `/workspace/artifacts/v536-verification-managed/runs/f2d78e0f64ab450886a011b9c5db4a35.json` · evidence SHA256 `08869b0045ca967bed461c15afc63c8b820c4b2b6fd3f19deff409bac6f386e5`.
두 관리 package와 증거의 SHA를 재확인했다. 승인된 latest/정상 rollback2세대 교대와 이번
소유 RAM 임시물 정리만 적용했다. 원래 checkout/main·과거 비관리 자료와 증거는 보존하며
퇴역한 세 번째 관리 ZIP 전체를 계속 보관한다고 주장하지 않는다. 여유 25260036096bytes(23.53GiB)다.

고정7/8행 forwarded/opaque·선택된 native callee의 별도 의존성 합성·새 import/alias 편집과
등록 외부의 기존 관측 결합 등 다른 원래 source closure는 같은 유한 잔여다. 부모/외부
원문 직접 쓰기 거절을 새 구현 요구로 만들지 않는다. 임의 조합을 새 필수로 늘리거나
M11/M12/M4를 다시 열지 않는다. 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·
전체 UI 전수 검증은 Linux native/Chromium 자동화와 교차 패키징과 별도다. 새 자격증명/
외부 grant·라이브 AI/과금·main 변경은 없다.
