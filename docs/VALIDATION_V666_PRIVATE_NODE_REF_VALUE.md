# Private C# ref→값 복사와 공동 저장 검증

게시본 `e5d51ede8c740d90bb63bca93b0425dabf2a5e68`와 기존 증거를 보존하고 runtime `66b8c63d87f8f0797f1b9ecf7353dcf05867d132`의 [유한 ref→값 전환](V666_PRIVATE_NODE_REF_VALUE.md)을 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9다.

- 직접 소유 qualified `inner/body` next-code의 두 long 인자 중 마지막 `secondNative`의 ref를 명시적으로 제거한다. 원래 methods-v1의 직접 long local `ref_counter`와 그 초기값·연결 JSON·이름·타입·인자 수/순서·long 반환·부모 frame/public/native ABI·배치·실행선·선택 밖 원문 bytes/mtime를 유지했다. 기존 local을 읽어 값 복사본을 전달하며 새 저장소·연결·기본값·형변환·C#을 추측하지 않는다.
- 같은 원래 C# 본문은99를 쓰며 원래 ref에서는 local99·최종104를 실행했다. 동일 본문/helpers와 다른 native 본문을 그대로 둔 값 전환을 실제 Save/cold/Review/Confirm하면 local35를 유지해40을 실행했다. CLR reflection은 원래 long&와 확정 뒤 long/IsOut=false를 확인했다. 이 명시 전환은 본문 쓰기를 복사본에 한정하는 의미이며 원래 ref 동작이 자동 보존된다는 뜻이 아니다.
- 별도로 수동 private 본문은25를 쓰지만 값 복사이므로 local35를 유지하며, 함께 수동 편집한 native 본문과30을 실행했다. 요청의 정·역순, 단일/공동 후보를 대조했고 원래 부모 계약과 독립 source bytes/mtime를 확인했다.
- 온전한 이전 패키지에서 원래104/ref·ABI 불변 후보는 유효했고 값 전환 후보는 거절됐다. 이전 UI도 거절된 값 선언과 입력·원본을 보존했다. 원래 부모 입력 연결은40/ref, alias local은104/ref, int 원본은40/ref로 유효하게 실행했다. 이 세 후보는 이번 직접 long local 전환 범위에서 거절됐다. patched build 전 이전 패키지의 세 유효 원본도 별도 baseline으로 확인했다.
- stale source/graph/before 서명·타입/이름/역할/반환/수 혼합·중복 이름·공개 계약·잘못된 C#·helper 경계·마지막 native 오류는 전체 후보를 거절했다. 원래 local 연결·frame·독립 source·plan/receipt/그룹 증거 변조도 원본과 checkpoint를 보존했다. 물리 읽기 버전은 Review/최종 CAS 책임으로 유지했다.
- 기존 editableNativeRefs metadata와 매개변수/본문/helper 영역을 재사용한다. 원래 local 이름/ID와 ref 제거 시 복사본에만 쓴다는 효과를 안내한다. 취소·Undo/Redo·첫 owner Save 전 재진입·fresh DOM 초안 복원·거절 입력 보존을 검사했다. 모의 metadata DOM과 실제 Linux engine/Chromium 화면 검사를 구분했다.
- 실제 Save/cold·쓰기 실패/재시도·응답 유실/중복 방지·늦은 설명·기본/독립 창·프로젝트 경계·후속 설명/본문 Save·Review 취소/Confirm을 검사했다. 후속 C#은 현재 value node/whole 증거를 검증하면서 최초 ref 서명/source/graph 해시·원래 물리 읽기 버전을 유지했다. post-Review graph/독립/private source/caller header/선택 native source 경합은 전체 Confirm을 차단하고 peer/checkpoint/input을 보존했다. 원본 복원 뒤 새 Review/Confirm과30 실행이 통과했다.
- 기존 private out→값·native 값→ref·struct 입력·whole API·native 반환·retained guard·등록 helper와 직전 private 값→ref 후보/guard를 새로 실행했다. 값→ref·순서·삭제·반환·타입·이름 DOM 회귀도 실행했다. 이를 모든 private/retained/opaque 조합이나 전체 UI 검사로 표현하지 않는다.
- 새 Windows용 package의 구조/hash/mode 사전검사와 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창·실행·DOM을 확인했다. package 실패 주입은 기존 runtime/package를 보존했다. Windows 산출물 사전검사는 실제 Windows 기기 실행 증거가 아니다.

제품 변경은 Graphs·Contracts·WholeBodies·feature-authoring.js·WebBundle의5파일이다. 기존 direct-local metadata를 재사용하며 새 저장 schema/profile/receipt/metadata 필드를 추가하지 않았다. workspace1·receipt3/nativeBodyContexts·원래 path/hash/whole·읽기·소유권·권한·Review/Confirm·최종 CAS와 이전 ApplySlots 선택 소스 그룹 보완을 유지한다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류도 유지한다.

개발 검사 17건이 모두 정상 종료했고 실패는 0건이다. 실패 원인 기록은 `{}`이고 준비 진단은 `[]`다. 개발과 최종48은 별도 신규 실행이며 최종은 재사용·실패0이다. trusted UI 경합 클릭과 늦은 설명의 확정 원문을 개발1·최종2 path/hash로 대조했다.

이전 runtime `db106214edac51eb82c194ceefbb3551a4b43c2b`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard는 거절했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·30 실행과 실제 long 값 선언을 확인했다. 이전 패키지·원본 source hash/inode/mode/mtime는 유지했다. pending과 확정 source 호환성은 별개이며 일반 Reference reader migration/downgrade는 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 66b8c63d87f8f0797f1b9ecf7353dcf05867d132 | a64828a4086d6875b943eecaf23581c4d93f3fb9a86879b0ed24a8e38fd13d39 | 54161645 |
| rollback | db106214edac51eb82c194ceefbb3551a4b43c2b | 6338131881f5db83548785de4d129e81fabc194ac6de0baa95875448fa5ec30f | 54160769 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/cc77aba393bd48e3b76185267b600305.json`, evidence SHA256 `b618ad6ef85d4bb9e34d974b567be1c9c3f120e4665dcdc73b36e0c5fe818e29`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/5e9368f5cc704aa199c92ec7d97b1e72.json`, evidence SHA256 `e118a488439370b113752f8aa07b64bcd4c84db800e24d28ffddb5eb973021b1`.
두 package·두 evidence hash를 대조했다. 원본 checkout·과거 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23777992704bytes(22.14GiB).

완료는 원래 두 long 인자의 마지막 ref를 기존 직접 long local의 값 복사로 전환하고 수동 본문/helpers·다른 native 본문과 공동 저장하는 유한 흐름이다. 다른 역할/out·타입/수/입출력 구조·소비 대응·새/alias 저장소 선택·부모 frame ABI와 추가 retained/opaque/copy/import·외부 관측은 잔여다. 이 조건을 일반 기능의 영구 UX 정책으로 확정하지 않는다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면·과거60/480초 시간 초과·전송 오류의 근본 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
