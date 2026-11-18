# Private 미사용 double→long 축소와 기존 out 연결 검증

게시본 `9aff82666a8a8f2937fe6dfaf2357b4dc6d93d5d`와 증거를 보존하고 runtime `0ef25fdd139a5e2a39b19e742aa78f85ef48cc68`를 최종 새 실행21·재사용27·실패0(총48)으로 검증했다. LF26(새6+재사용20)·CRLF13(새6+재사용7)·새 package/전체 ZIP 복원9다. 제품·기존 테스트 bytes와 SDK/NuGet·명령·독립 LF/CRLF 원본을 확인한 테스트27건만 재사용했고, clone·restore·Release·MCP·engine과 모든 package/전체 복원은 새로 실행했다.

이번 범위는 원래 methods-v1의 소유 qualified `inner/body` next-code다. 원래 두 long 인자(첫 값, 마지막 out)와 모든 input/out 선언·연결·소비를 유지하고, 사용되지 않는 double 반환만 long으로 명시한다. 부모 frame/public/native ABI·locals·실행선·좌표·선택 밖 C# bytes/mtime를 보존한다. 반환 소비가 있으면 별도 명시 대응 없이 후보를 거절한다. 본문·helper·cast·저장소·연결을 자동 생성하지 않는다.

원래 double129.25/out99는 실제104를 실행했다. 반환 선언만 long으로 바꾸고 원문을 유지하면 CS0266으로 거절했다. 원문을 자동으로 자르거나 Convert/캐스트를 넣지 않았다. 사용자가 원래 helper를 유지하면서 checked long 캐스트를 직접 작성한 사례는 long129/out99·최종104를 실행했다. 별도의 직접 작성한 본문·helper는 long55/out25와 함께 선택한 native 본문으로 최종20을 실행했다. CLR reflection으로 실제 반환 타입/값과 같은 두 인자·Long&/IsOut=true를 확인했다. checked/unchecked/반올림 정책을 앱이 선택하지 않으며 샘플의 checked 캐스트는 명시적으로 작성된 C#이다.

기존 out을 노드 입력·local source·local을 통한 exit에서 함께 소비하는 원본은 실제 Save/cold/Review/Confirm과20 실행을 통과했다. 원래 소비 JSON과 선택 밖 소비 C#은 그대로다. 반환을 암시적 exit·명시적 return 포트·local source·노드 입력에서 소비하는 네 원본은 이전 온전한 패키지에서 먼저 유효하게 실행했다. 첫 세 원본은 원래 double 부모 frame과 root의 이미 작성된 double→long 어댑터를 사용하고, 노드 입력 원본은 원래 double sink를 사용한다. 부모 공개/native 계약은 long 그대로다. 후보는 소비를 자동 변환/remap하지 않고 전체 거절했다. 기존 out exit를 native 반환으로 바꾸는 변조도 guard에서 거절했다.

원문 축소 오류 CS0266 외에도 값 없는 반환 CS0126, 모든 경로의 반환 누락 CS0161, out 미할당 CS0177, out 할당 전 읽기 CS0269를 거절했다. 잘못된 원본 source/graph/before 서명·타입/이름/역할/인자 수 혼합·float 반환·공개 계약·helper 경계·마지막 native 본문도 전체 거절하고 원본/checkpoint를 유지했다.

계산된 읽기 metadata는 이 원본 double/out 문맥에 long만 제공한다. 기존 반환/매개변수/본문/helper 편집 영역을 사용하며 명시 캐스트·반환문 요구를 안내한다. 기존 double 선언 그대로의 본문 편집과 저장 뒤 long/out의 body-only CRLF 원문·helper 보존도 확인했다. 모의 DOM의 초안 복원·재진입·보호 영역·거절 입력과 실제 Linux engine/Chromium의 Cancel·Undo/Redo·Save·cold·Review/Confirm을 분리했다. 실제 화면 검토 SHA는 `4aa6b945537e0c10b277f1004e0b09c3b526b4d1ac18d4bcfcb6aec6fdb71881`다.

Save 실패/재시도·응답 유실/중복 방지·프로젝트 경계·기본/독립 창·후속 설명과 본문 Save를 검사했다. 현재 long/out 서명·whole을 확인하면서 최초 double/out 서명·source/graph 해시·물리 읽기 버전을 유지한다. Review 뒤 graph·private/독립 source·caller header·선택 native source 경합은 Confirm을 차단하고 peer/checkpoint/input을 보존한다. 복원 뒤 새 Review/Confirm과20 실행이 통과했다. trusted UI 경합 클릭과 늦은 설명 확정 원문을 개발1·첫 최종 시도2·후속 새 실행1 path/hash로 확인했다. 현재 합산된 LF 후속 저장 사실은 첫 시도의 검증을 재사용하고 restored 후속 저장은 새로 실행했다.

직전 long→double native/guard와 기존 out→값·native 값→ref·struct 입력·whole API·native 반환·retained·등록 helper 및 DOM 회귀는 첫 시도에서 신규 통과했고, 후속 실행에서 동일한 27개 source-test 사실로 재사용했다. 패키지/복원 DOM은 새로 실행했다. 새 Windows 산출물의 구조/hash/mode 검사와 Linux 실행, 전체 ZIP 별도 복원, package 실패 시 기존 runtime/package 보존을 확인했다. 실제 Windows 기기 실행과 구분한다.

제품 변경은 Graphs·Contracts·WholeBodies·feature-authoring.js·WebBundle의5파일이다. 원래 double→long 명시 계획을 부모 ABI 유지와 후속 Save 정상화에 연결하고 input 복사를 원래 non-out 인자로 한정했다. 나머지 보호 파일과 번들의 다른 행은 baseline과 byte-identical이다. 새 저장 schema/profile/receipt·권한을 만들지 않았다. workspace1·receipt3/nativeBodyContexts·소유권·권한·읽기·Review/Confirm·최종 CAS와 기존 ApplySlots 보호를 유지한다. 정보별 struct·종류 enum·모듈 interface·명시 async 전환 전 sync caller 오류를 유지한다.

개발 18건, 정상 종료 18건, 실패 원인 `{}`, 준비 단계 진단 `[{"stage": "pre-verification source preparation", "error": "Guide marker matched three CSharp editors instead of one; assertion stopped before UI/tests/build.", "preserved": "Already edited Graphs/Contracts/WholeBodies retained; no rerun of their patch.", "fix": "Qualified the original private return editor marker and resumed once after failed line; other editor guides untouched."}]`를 총48 사실과 구분해 보관했다. 준비 스크립트의 공통 guide 선택자 assertion은 검증/빌드 전 중단됐으며, 이미 반영된 C# 변경을 유지하고 정확한 편집기 선택자로 남은 준비만 한 번 이어갔다. 제품 실패와 구분했다.

첫 최종 시도는47통과·package-failure-lifetime1실패이며 record `/workspace/artifacts/v536-verification-managed/runs/056d83f3f94043daa4320325f2aa9fe9.json`, archive SHA `47d1f1ba3878511e21495178dce54be1571ba00c209cc07c734491f719454594`를 그대로 보관했다. ui-failure의 의도적 screenshot 예외가 최종 packaged-login.png 전에 5초 진단 screenshot에서 발동한 테스트 장치 결함이었다. copy cleanup은 완료됐고 기존 latest/rollback은 승격되지 않았다. 최종 파일을 저장한 뒤에만 예외를 주입하도록 바꾸고, 주입 proof와 readiness passed=true도 요구했다. 기존 30초 실제 readiness 조건·최초5초 관찰·실패 진단은 그대로다. 원래 진단 화면에서 충돌하는 것을 모의 callback으로 재현하고 수정 후 진단/메모리 screenshot의 정상 반환·최종 screenshot 후 예외와 SDK/재사용 보호2건을 검증했다. 모의 검사는 actual engine/device 검증이 아니다. 복구 guard record `/workspace/artifacts/v536-verification-managed/runs/c1e26fd5e6244c188b0f18b61b4e4783.json`, SHA `4914012102824731b3fa633c545e50ea24e1cd97cb56052d95db746d188a0060`다. 후속 실행의 실제 패키지 UI-failure는 readiness 통과·최종 screenshot·정확한 예외·복사 정리를 새로 확인했다. 초기화 지연이나 과거 빈 화면의 근본 원인을 확정하지 않는다. 제품5파일 bytes는 첫 frozen `ee8a327ded9410c2564d7f5a118024bf1c0423a5`와 동일하며 추가 변경은 패키지 검사 장치·엄격 재사용 helper/driver뿐이다.

이전 runtime `b1b3c4379151dc1dce067f7e0be49f9105325dd5`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard가 거절했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20·실제 long/out 실행을 확인했다. 이전 package·원본 source inode/hash/mode/mtime를 보존했다. 일반 Reference reader migration/downgrade를 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 0ef25fdd139a5e2a39b19e742aa78f85ef48cc68 | 4e9b666ebfa7f5b6191c694271849e2ddb0a793cdfc50a7e26e7bb5c9a662cb5 | 54164968 |
| rollback | b1b3c4379151dc1dce067f7e0be49f9105325dd5 | 7951d9d0abb65f8b7874301c7b140af006be9aa06b9103a8d8b54b343872005f | 54163149 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/b19e483cb56a48f39c1e10f7bab1609c.json`, evidence SHA256 `2273d6b86df5819c3d8eea5615f157886fa14178646da90b81d0f9d1e46b0ba5`. 개발 record `/workspace/artifacts/v536-verification-managed/runs/e9d5d6cec42e4855a5090e27eb9105e6.json`, evidence SHA256 `131005fe0688fa623ac70aafb5e4d2e7b83b049dff83cdfb240431f0ea742bfd`. 두 package·개발/첫 시도/복구 guard/최종 evidence4개의 hash를 대조했다. 원본 checkout·기존 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23642222592bytes(22.02GiB).

다른 private 역할·타입/수/구조 변경, 반환 소비의 명시 대응, 부모 ABI, retained/opaque/copy/import 결합과 일반 reader migration은 잔여다. 이 유한 범위를 영구 UX 정책으로 확정하지 않는다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면·과거60/480초·전송 오류 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
