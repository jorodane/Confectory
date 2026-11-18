# Private C# 상수 값→out과 공동 저장 검증

게시본 `f49f19195df88d53021d4df5a1e155d02c374862`와 기존 증거를 보존하고 runtime `2ccc2722747155d16e0dde6cc0159a58ac6ca528`의 [유한 상수 값→out 전환](V666_PRIVATE_NODE_VALUE_OUT.md)을 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9다.

- 소유 qualified `inner/body` next-code의 두 long 값 인자 중 마지막 `secondNative`를 out으로 명시한다. 원래 methods-v1 scope와 정확한 int32 상수 연결에 한정하며 그 마지막 상수 연결만 해제한다. 첫 입력·long 반환·기존 소비·부모 frame/public/native ABI·배치/실행선·locals·선택 밖 원문 bytes/mtime를 유지한다. 새 out은 자동 연결하지 않으며 저장소·기본값·C# 할당을 추측하지 않는다.
- 원래 C#은 마지막 인자에99를 대입하고 반환129를 계산해 최종134를 실행했다. 같은 본문/helpers와 다른 native 본문을 그대로 둔 명시 out 전환도 실제 Save/cold/Review/Confirm 후134를 실행했다. CLR reflection은 long→long&/IsOut=true를 확인했고 실제 반사 호출에서 out99·반환129를 대조했다. 원래 값 호출의 인자 배열 값9977은 변하지 않았다. 이 사례의 원래 동작 유지가 임의의 본문에서 입력 해제가 안전하다는 뜻은 아니다.
- 별도의 수동 private 본문은 out5와 반환25를 직접 작성하고 다른 수동 native 본문과 최종20을 실행했다. 단일/공동 후보와 요청 정·역순을 비교했다. out을 쓰지 않는 본문은 CS0177, 할당 전에 읽는 본문은 CS0269/CS0177로 거절됐고 원본·checkpoint를 보존했다. 자동 기본값이나 할당을 삽입하지 않았다.
- 온전한 이전 패키지에서 원래134/value·ABI 불변 후보는 유효했고 새 out 후보는 거절됐다. 이전 UI도 거절한 out 선언과 입력·원본을 유지했다. typed/wide 상수와 local 원본은 patched build 전 이전 패키지에서도 각각134/value로 유효하게 실행했으며 새 후보는 이 연결들의 해제를 거절했다.
- stale source/graph/before 서명·타입/이름/역할/반환/수 혼합·중복 이름·공개 계약·잘못된 C#·helper 경계·마지막 native 오류를 전체 거절했다. 원래 연결·frame·독립 source·plan/receipt/그룹 증거 변조도 원본과 checkpoint를 보존했다. 물리 읽기 버전은 Review/최종 CAS 책임으로 유지했다.
- 기존 매개변수/본문/helper 영역에서 원래 상수 인자명·연결 해제·새 out 미연결·직접 할당 필요를 안내한다. editableNativeOuts는 현재 원본에서 계산한 읽기 metadata이며 저장 field가 아니다. 취소·Undo/Redo·첫 owner Save 전 재진입·fresh DOM 초안 복원·거절 입력 보존을 검사했다. 모의 metadata DOM과 실제 Linux engine/Chromium 화면 검사를 구분했다.
- 실제 Save/cold·쓰기 실패/재시도·응답 유실/중복 방지·늦은 설명·기본/독립 창·프로젝트 경계·후속 설명/본문 Save·Review 취소/Confirm을 검사했다. 후속 C#은 현재 out node/whole 증거를 검증하면서 최초 value 서명/source/graph 해시·물리 읽기 버전을 유지했다. post-Review graph/독립/private source/caller header/선택 native source 경합은 전체 Confirm을 차단하고 peer/checkpoint/input을 보존했다. 원본 복원 뒤 새 Review/Confirm과20 실행이 통과했다.
- 기존 private out→값·native 값→ref·struct 입력·whole API·native 반환·retained guard·등록 helper와 직전 private ref→값 후보/guard를 새로 실행했다. ref→값·값→ref·순서·삭제·반환·타입·이름 DOM 회귀도 실행했다. 이를 모든 private/retained/opaque 조합이나 전체 UI 검사로 표현하지 않는다.
- 새 Windows용 package의 구조/hash/mode 사전검사와 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창·실행·DOM을 확인했다. package 실패 주입은 기존 runtime/package를 보존했다. Windows 산출물 사전검사는 실제 Windows 기기 실행 증거가 아니다.

제품 변경은 Graphs·Contracts·WholeBodies·feature-authoring.js·WebBundle의5파일이다. 새 저장 schema/profile/receipt나 권한을 추가하지 않았다. 기존 before/after signature와 whole/path/hash가 명시한 out과 정확한 원래 상수 해제를 증명한다. workspace1·receipt3/nativeBodyContexts·읽기·소유권·권한·Review/Confirm·최종 CAS와 이전 ApplySlots 선택 소스 그룹 보완을 유지한다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류도 유지한다.

개발 검사 18건 중 정상 종료 17건·실패 1건이다. 첫 모의 DOM의 거절 목록에 정상 지원하는 마지막 out 선언이 잘못 포함돼, 의도대로 저장된 뒤 사라진 오류란을 기다리면서 실패했다. 이 항목만 미지원 첫 인자 out 선언으로 교정하고 DOM을 새로 실행했다. 이 fixture 교정에는 제품 코드나 빌드 변경이 없었으며, 수정 전 fixture·실패 로그·교정된 입력을 대조했다. 준비 진단 `[]`, 실패 원인 `{"dev-private-node-value-out-renderer": "Controlled DOM negative list incorrectly included the valid supported last out declaration. Its acceptance closed the dialog as intended, so the error-locator expectation failed. Replaced only that invalid rejection expectation with an unsupported first-parameter out declaration; no product patch or build change."}`를 보관했다. 개발과 최종48은 별도 신규 실행이며 최종은 재사용·실패0이다. trusted UI 경합 클릭과 늦은 설명의 확정 원문을 개발1·최종2 path/hash로 확인했다.

이전 runtime `66b8c63d87f8f0797f1b9ecf7353dcf05867d132`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard는 거절했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20 실행과 실제 out 할당/반환을 확인했다. 이전 패키지·원본 source hash/inode/mode/mtime를 유지했다. pending과 확정 source 호환성은 별개이며 일반 Reference reader migration/downgrade는 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 2ccc2722747155d16e0dde6cc0159a58ac6ca528 | 70029c446f8e2dc00eff8e67e8f08cb7ad7bc32a7a526073681c8b32acd67a3e | 54163381 |
| rollback | 66b8c63d87f8f0797f1b9ecf7353dcf05867d132 | a64828a4086d6875b943eecaf23581c4d93f3fb9a86879b0ed24a8e38fd13d39 | 54161645 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/d88d8c2f0b93416c97fb205582722eca.json`, evidence SHA256 `2f051ac7334e5b75f5b43046aa60ef4bcec7ad4409551dd0ad04c1dec70211f4`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/69214198350d4d9dae10f6e90af12504.json`, evidence SHA256 `3c843d9150cb88623ea1dd69f6b5b40346825a1896a7c0f39a11726168ab1639`.
두 package·두 evidence hash를 대조했다. 원본 checkout·과거 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23756423168bytes(22.12GiB).

완료는 두 long 값 인자의 마지막 원래 int32 상수를 명시적으로 해제하는 out 전환과 수동 본문/helpers·다른 native 본문의 공동 저장이다. 다른 역할/ref/out·타입/수/입출력 구조·소비 remap·새/alias 저장소 선택·부모 ABI와 추가 retained/opaque/copy/import·외부 관측은 잔여다. 이 조건을 일반 기능의 영구 UX 정책으로 확정하지 않는다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면·과거60/480초·전송 오류 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
