# Private C# 값→ref와 기존 지역 저장소 공동 저장 검증

게시본 `183a52c549322c75e9da91fac7f6a5ea278082b9`와 기존 증거를 보존하고 runtime `db106214edac51eb82c194ceefbb3551a4b43c2b`의 [유한 값→ref 전환](V666_PRIVATE_NODE_VALUE_REF.md)을 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9다.

- 소유 qualified `inner/body` next code의 두 long 값 인자 중 마지막 `secondNative`를 `ref long`으로 명시한다. 원래 연결은 methods-v1 내부에 이미 선언된 직접 long local `ref_counter`다. 이름·타입·인자 수/순서·long 반환·부모 frame/public/native ABI·입력 연결 JSON·local 선언/초기값·노드/좌표·실행선·선택 밖 source bytes/mtime를 유지했다. 새 저장소·임시 셀·기본값·연결·형변환·본문을 추론하지 않는다.
- 원래 같은 C# 본문은 값 매개변수 복사본에99를 쓰지만 실제 local35를 유지해40을 실행했다. 원래 본문/helpers와 다른 native 본문을 그대로 둔 채 ref만 명시하고 실제 Save/cold/Review/Confirm한 결과, 같은 local에99가 기록돼104를 실행했다. CLR reflection은 원래 long과 확정 뒤 long& 및 IsOut=false를 확인했다. post-Review 원래 graph 경합은 Confirm을 차단했고 복원 뒤 새 Review가 필요했다. 별도 수동 private 본문은25를 기록하고 다른 native 본문과 함께20을 실행했다. ref는 사용자가 명시한 저장소 공유이며, 값 전달 동작이 자동 보존된다고 주장하지 않는다.
- 이전 온전한 package에서 원래40·계약 불변 후보는 유효하고 새 ref 후보는 거절했다. 이전 UI도 거절한 ref 선언과 원본을 유지했다. 유효한 원래 상수·부모 값 입력·int local은 각각40을 실행하지만 이번 long 직접 local 전환 후보는 거절했다. alias local은 직접 local 조건에서 제외되며 별도 계획이 필요하다.
- stale source/graph/before 서명·타입/이름/ref-out/반환/수 혼합·중복 이름·공개 계약·잘못된 C#·helper 경계·마지막 native 오류가 원자적으로 거절됐다. source/graph/whole receipt·원래 local 연결·frame·독립 소스·읽기/그룹 증거 변조도 확인했다. 물리 읽기 버전은 Review/최종 CAS에서 검증한다.
- 편집기는 기존 매개변수/본문/helper 영역과 원래 local 이름/ID 안내를 사용한다. 취소·Undo/Redo·첫 owner Save 전 재진입·fresh DOM 초안 복원·거절 입력 보존을 검사했다. 모의 metadata DOM과 실제 Linux engine/Chromium 화면 검사를 구분했다. 실제 화면에서 명시한 ref 선언·local 안내·본문/helpers·취소/저장을 확인했지만 전체 UI를 검증한 것은 아니다.
- 실제 Save/cold·쓰기 실패/재시도·응답 유실/중복 방지·늦은 설명·기본/독립 창과 프로젝트 경계·후속 설명/본문 Save·Review 취소/Confirm을 검사했다. 후속 본문은 현재 ref node/whole 증거를 검증하면서 최초 value 선언/source/graph 해시·원래 물리 읽기 버전을 유지했다. post-Review graph/독립 source/private source/retained header/선택 native source 경합은 checkpoint와 peer/input을 보존한 채 전체 Confirm을 차단했다. 원본 복원 후 새 Review/Confirm과20 실행을 확인했다.
- 기존 private out→값·native 값→ref·struct 입력·whole API·native 반환·retained guard·등록 helper와 직전 private 순서 후보/guard를 새로 실행했다. 순서·삭제·반환·타입·이름 DOM 회귀도 실행했다. 이를 모든 private ABI/retained/opaque 조합 또는 전체 UI 검증으로 합산하지 않는다.
- 새 Windows용 package의 구조/hash/mode 사전검사와 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창·실행·DOM을 확인했다. package 실패 주입은 기존 runtime/package를 보존했다. Windows 산출물 검사는 Windows 기기 실행 증거가 아니다.

제품 변경은 Graphs·Contracts·WholeBodies·feature-authoring.js·WebBundle의5파일이다. 이전 선택 소스 그룹 보완 ApplySlots는 그대로 보호했다. 현재 metadata에 기존 local ref 가능 표시를 추가하며 workspace1·receipt3/nativeBodyContexts·원래 path/hash/whole·읽기·소유권·권한·Review/Confirm·최종 CAS를 재사용한다. 새 저장 schema/profile/receipt나 접근 권한을 추가하지 않았다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 검사 16건 중 정상 종료 14·실패 2다. 실패 원인 기록은 `{"dev-private-node-value-ref-native": "Fixture int-local original connected int storage to a long parameter, rejected by existing GRAPH_LOCAL_TYPE before candidate. Corrected original private parameter and reflection expectation to int; finite long-only ref candidate remains rejected. No product patch changed.", "dev-private-node-value-ref-native-corrected": "Second fixture correction had matched private int parameter but still connected the int local to the enclosing long return, rejected by existing GRAPH_LOCAL_TYPE at inner/exit:return. Corrected int original exit to its existing long-return node and explicit original body result35. No product change."}`이고 준비 진단은 `[{"action": "read-only boundary evidence audit", "failure": "Expected int-only rejection at private Text validation; actual grouped request rejects earlier at WholeBodies shape routing through caller batching. Corrected audit expectation to the exact observed earlier rejection; no product/test build rerun or source change."}]`다. 개발과 최종48은 별도 신규 실행이며 최종은 재사용·실패0이다. trusted UI 경합 클릭과 늦은 설명의 확정 원문을 개발1·최종2 path/hash로 확인했다.

패키지 ZIP 준비 중 단계 사이의 읽기 전용 모니터에서 부모 프로세스의 실행 상태와 다음 복원 검사의 통과를 확인했다. 추가 `/proc/io` 읽기는 PermissionError로 거절됐지만 검증 실행 오류는 아니며, 접근 확대나 검증/환경 재시작 없이 같은 실행을 이어갔다.

이전 runtime `22f1e9a868399096ee267869e0efd7aa8b544812`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 현재 guard는 새 pending을 수용하고 이전 guard는 거절했다. 이전 package와 원래 source hash/inode/mode/mtime는 유지했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20 실행과 실제 long&를 확인했다. pending과 확정 source 호환성은 별개다. 더 오래된 Reference reader·일반 migration/downgrade는 미지원/미검증 경계로 남긴다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | db106214edac51eb82c194ceefbb3551a4b43c2b | 6338131881f5db83548785de4d129e81fabc194ac6de0baa95875448fa5ec30f | 54160769 |
| rollback | 22f1e9a868399096ee267869e0efd7aa8b544812 | f894b7cd07b72384d05332c5ed57e79d03f1f4686b78b099688149d1a3e16632 | 54158475 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/6bb01a62a3c5456b8f4775901a5dd451.json`, evidence SHA256 `156ab36a46a86cfbd36db961a9cf8f12f031f3b3525ba84ba6e359c49c97528e`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/36b361e78b6b42e8a1b173c79d23ece3.json`, evidence SHA256 `75b4de512280aec91222060dc4a2c4412adb191e59022c8788ea1c9f71ff52c4`.
두 package·두 evidence hash를 다시 대조했다. 원본 checkout·과거 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23799566336bytes(22.17GiB).

완료 범위는 원래 long 직접 local에 연결된 마지막 값 인자의 명시적 ref 전환과 수동 본문/helpers·다른 native 본문 공동 저장이다. 이 조건은 검증된 유한 경계이며 모든 ref 입력의 영구 UX 정책으로 확정하지 않는다. inverse/ref→값·out·다른 타입/수/입출력 구조·사용되는 반환 소비·새/alias 저장소 선택·부모 frame ABI와 추가 retained/opaque/copy/import·외부 관측은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면·과거60초 미응답·최초 복원480초 시간 초과와 과거 전송 오류 원인은 미확정이며 이번 통과로 해결됐다고 주장하지 않는다. main은 사용자 검토/merge에 남긴다.
