# Private C# 미사용 out 삭제와 공동 저장 검증

게시본 `52fb492d0ed08ad6600cc68a2f8fe4e424d78504`와 기존 증거를 보존하고 runtime `2463533549e580fb55132e7621c81776af92194d`의 [미사용 out 삭제](V666_PRIVATE_NODE_REMOVE_OUT.md)를 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9다.

- 소유 qualified `inner/body` next-code의 원래 두 long 인자 중 마지막 out `secondNative`를 명시적으로 삭제한다. 원래 methods-v1 scope, 첫 long 값 입력·long 반환과 모든 기존 반환 소비·부모 frame/public/native ABI·입력 연결·locals·배치/실행선·선택 밖 원문 bytes/mtime를 유지한다. 원래 out에는 입력 연결이 없고, 삭제는 새 입력·저장소·기본값·출력 연결이나 자동 C# 수정을 만들지 않는다.
- 원래 C#은 out99를 할당하고 반환129·최종134를 실행했다. 실제 CLR reflection은 두 인자 중 마지막 long&/IsOut=true와 직접 호출 out99/반환129를 확인했다. 별도로 직접 작성한 한 인자 본문/helpers는 반환25와 다른 native 본문을 통해 최종20을 실행했다. 명시적으로 같은 결과를 작성한 본문은 out이 없는 한 인자·반환129·최종134를 실행했고, 선택된 다른 native 원문은 그대로였다. 같은 결과 사례가 임의의 본문에 대한 자동 의미 보존을 뜻하지 않는다.
- 원래 out을 exit·지역 source·다른 노드 입력에서 사용하는 세 원본은 이전 온전한 패키지에서도 유효하게 실행했다. 현재 후보는 이 소비를 지우거나 재배정하지 않고 전체 삭제를 거절했다. 반환의 암시적/명시적 return 포트 소비는 보존했다. 삭제한 이름이 남은 원래 C#은 CS0103으로 거절했다. 본문이나 helpers를 자동 고치지 않았다.
- stale source/graph/before 서명·첫 인자의 이름/타입/역할·반환/수 혼합·다른 인자 삭제·공개 계약·잘못된 C#·helper 경계·마지막 native 오류를 거절했다. 원본 연결·frame·독립 source·plan/receipt/그룹 증거 변조도 원본과 checkpoint를 보존했다. 물리 읽기 버전은 Review/최종 CAS 책임으로 유지했다.
- 기존 C# 매개변수/본문/helper 영역에서 사용되지 않는 마지막 out 이름과 삭제·소비 보호·부모 계약 유지를 안내한다. removableNativeOuts는 원본 scope에서 계산한 읽기 metadata이며 저장 field가 아니다. 기존 out 선언 그대로의 본문 편집, 취소·Undo/Redo·첫 owner Save 전 재진입·fresh DOM 초안 복원·거절 입력 보존을 검사했다. 모의 metadata DOM과 실제 Linux engine/Chromium 화면 증거를 구분했다.
- 실제 Save/cold·쓰기 실패/재시도·응답 유실/중복 방지·늦은 설명·기본/독립 창·프로젝트 경계·후속 설명/본문 Save·Review 취소/Confirm을 검사했다. 후속 C#은 현재 한 인자 서명/whole을 검증하면서 최초 out 서명/source/graph 해시·물리 읽기 버전을 유지했다. post-Review graph/독립/private source/caller header/선택 native source 경합은 전체 Confirm을 차단하고 peer/checkpoint/input을 보존했다. 원본 복원 뒤 새 Review/Confirm과20 실행이 통과했다.
- 기존 private out→값·native 값→ref·struct 입력·whole API·native 반환·retained guard·등록 helper와 직전 private 값→out 후보/guard를 새로 실행했다. 값→out·ref→값·값→ref·순서·삭제·반환·타입·이름 DOM 회귀도 실행했다. 모든 private/retained/opaque 조합이나 전체 UI 검사로 표현하지 않는다.
- 새 Windows용 package의 구조/hash/mode 사전검사와 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창·실행·DOM을 확인했다. package 실패 주입은 기존 runtime/package를 보존했다. Windows 산출물 사전검사는 실제 Windows 기기 실행 증거가 아니다.

제품 변경은 Graphs·Contracts·WholeBodies·feature-authoring.js·WebBundle의5파일이다. 새 저장 schema/profile/receipt나 권한을 추가하지 않았다. workspace1·receipt3/nativeBodyContexts·소유권·읽기·권한·Review/Confirm·최종 CAS와 이전 ApplySlots 선택 소스 그룹 보완을 유지한다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류도 유지한다.

개발 검사 19건 중 정상 종료 18건·실패 1건이다. 개발과 최종48은 별도 신규 실행이다. 첫 모의 DOM에서 제품 편집기의 인자 수 사전검사가 미사용 out 삭제를 막는 결함을 확인했다. 기존 개수 검사에 계산된 삭제 capability를 추가하고, 같은 DOM을 다시 실행한 뒤 engine을 새로 빌드해 실제 API/UI를 검증했다. 실패 로그와 보완 전 JS/bundle·입력 해시는 보존했다. 개발 실패 원인 `{"dev-private-node-remove-out-renderer": "Product C# editor arity precheck allowed 2-to-1 only for literal-input deletion and blocked the newly validated unused-out deletion. Added computed removableNativeOuts capability to that existing arity gate; exact signature/consumer guards remain unchanged. Renderer unchanged; rebuilt engine before actual UI/API checks."}` 및 준비 단계 진단 `[{"stage": "new native test generation syntax check", "error": "SyntaxError: expected 'else' after 'if' expression", "cause": "Generated conditional omitted a space before numeric else branch; no test or product build had started.", "correction": "else134 -> else 134", "preserved": "setup-native-before.py"}]`를 별도 보관했다. 생성한 검사 스크립트의 숫자 else 문법 오류는 실행 전 수정했고, 잘못된 원문 snapshot은 보존했다. 원래 out 선언은 유지하고 C#만 일부러 잘못 준 음성 검사의 capability 기대도 native 실행 전 교정했으며 이전/현재 입력 hash를 보관했다. trusted UI 경합 클릭과 늦은 설명 확정 원문을 개발1·최종2 path/hash로 확인했다.

이전 runtime `2ccc2722747155d16e0dde6cc0159a58ac6ca528`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard는 거절했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20 실행과 실제 한 인자/반환을 확인했다. 이전 패키지·원본 source hash/inode/mode/mtime를 유지했다. pending과 확정 source 호환성은 별개이며 일반 Reference reader migration/downgrade는 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 2463533549e580fb55132e7621c81776af92194d | ba9241c4695bfb37487ee15301e2d09db3a4a08999bff9217c8a47a749d66abb | 54166235 |
| rollback | 2ccc2722747155d16e0dde6cc0159a58ac6ca528 | 70029c446f8e2dc00eff8e67e8f08cb7ad7bc32a7a526073681c8b32acd67a3e | 54163381 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/2f8996d9ef8d413e92c8b1105289edab.json`, evidence SHA256 `f236d60d6ce15052ef212cf34ae6f736b65f1eb4a3b17ab0bcbf8747691cfcfb`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/5b83541e505f4955b85f7a9cd9eb98b2.json`, evidence SHA256 `af751958745d139953f2cc228529fbaf62cc341f3cc4dc02a0c62e606ef8e29d`.
두 package·두 evidence hash를 대조했다. 원본 checkout·과거 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23735853056bytes(22.11GiB).

완료 범위는 원래 두 long 인자 중 사용되지 않는 마지막 out 삭제와 수동 본문/helpers·다른 native 본문의 공동 저장이다. 다른 역할·타입/수/입출력 구조·소비 remap·새/alias 저장소 선택·부모 ABI와 추가 retained/opaque/copy/import·외부 관측은 잔여다. 이 유한 조건을 일반 기능의 영구 UX 정책으로 확정하지 않는다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면·과거60/480초·전송 오류 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
