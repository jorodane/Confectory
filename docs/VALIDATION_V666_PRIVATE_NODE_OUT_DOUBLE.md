# Private 미사용 long→double 반환과 기존 out 연결 검증

게시본 `43609aa8172690c5b05bc9e553ba11e6ebd72354`와 증거를 보존하고 runtime `b1b3c4379151dc1dce067f7e0be49f9105325dd5`를 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9다.

이번 범위는 원래 methods-v1의 소유 qualified `inner/body` next-code다. 원래 두 long 인자(첫 값, 마지막 out)와 모든 입력/out 연결·소비를 유지하고, 사용되지 않는 long 반환만 double로 명시한다. 부모 frame/public/native ABI·locals·실행선·좌표·선택 밖 C# bytes/mtime를 보존한다. 반환이 쓰이는 원본은 명시적 소비 대응 없이 전환하지 않는다. 본문·helper·cast·저장소·연결을 자동 생성하지 않는다.

원래 long 반환129/out99는 실제104를 실행했다. 반환 선언만 double로 명시한 경우 C# 본문과 helper는 UTF-8 bytes 그대로이며 실제 double129/out99·최종104를 유지했다. 이 변환은 사용자가 명시한 C# 반환 선언에 대한 C#의 숫자 변환 규칙이며 source에 cast를 삽입하지 않는다. 다른 별도 사례에서는 사용자가 분수 반환문과 helper를 직접 작성해 double55.25/out25를 계산하고, 함께 선택한 native 본문과 최종20을 실행했다. CLR reflection으로 실제 반환 타입/값과 동일한 두 인자·Long&/IsOut=true를 확인했다. 임의의 C# 본문에 대한 자동 의미 보존을 주장하지 않는다.

기존 out을 노드 입력·local source·local을 통한 exit에서 함께 소비하는 원본은 실제 Save/cold/Review/Confirm과20 실행을 통과했다. 원래 소비 JSON과 선택 밖 소비 C#은 그대로다. 원래 반환을 암시적 exit·명시적 return 포트·local source·노드 입력에서 사용하는 네 원본은 이전 온전한 패키지에서 먼저 유효하게 실행했고 현재 후보도 전체 거절했다. 소비를 자동 cast/remap하거나 버리지 않는다. 기존 out exit를 native 반환으로 바꾸는 변조도 guard에서 거절했다.

값 없는 반환은 CS0126, 모든 경로의 반환 누락은 CS0161, out 미할당은 CS0177, out 할당 전 읽기는 CS0269로 거절했다. 원본 source/graph/before 서명·타입/이름/역할/인자 수 혼합·float 반환·공개 계약·helper 경계·마지막 native 본문 오류도 전체 거절하고 원본/checkpoint를 보존했다.

계산된 읽기 metadata는 이 미사용 long/out 문맥의 반환 선택을 기존 void에서 double/void로 확장한다. 기존 long→void 검사는 void 지원 자체를 계속 검증하며 새 선택을 금지하지 않도록 범위를 명확히 했다. 기존 반환/매개변수/본문/helper 편집 영역을 사용한다. 모의 DOM의 원문 CRLF·초안 복원·재진입·취소·보호 영역·거절 입력과 실제 Linux engine/Chromium의 편집·Undo/Redo·owner Save·cold·Review/Confirm을 별도 증거로 보관했다. 현재 double/out의 body-only 편집도 원문 CRLF/helper를 유지한다. 실제 화면 검토 SHA는 `01a4a8d82c9dec76e67157526fed1a85d7ba99e0bd06032bda12873082c4ae45`다.

Save 실패/재시도·응답 유실/중복 방지·프로젝트 경계·기본/독립 창·후속 설명과 본문 Save를 검사했다. 현재 double/out 서명·whole을 확인하면서 최초 long/out source/graph 서명과 물리 읽기 버전을 보존한다. Review 뒤 graph·private/독립 source·caller header·선택 native source 경합은 Confirm을 차단하고 peer/checkpoint/input을 유지한다. 복원 뒤 새 Review/Confirm과20 실행이 통과했다. trusted UI 경합 클릭과 늦은 설명 확정 원문을 개발1·최종2 path/hash로 확인했다.

직전 void→long native/guard와 기존 out→값·native 값→ref·struct 입력·whole API·native 반환·retained·등록 helper 및 DOM 회귀를 새로 실행했다. 새 Windows 산출물의 구조/hash/mode 검사와 Linux 실행, 전체 ZIP 별도 복원, package 실패 시 기존 runtime/package 보존을 확인했다. 실제 Windows 기기 실행과 구분한다.

제품 변경은 Graphs·feature-authoring.js·WebBundle의3파일이다. 기존 Returns 계획에 유한한 out 문맥을 명시하고 입력 복사를 원래 non-out 인자로 한정했다. Contracts·WholeBodies의 기존 Returns 및 나머지 보호 파일, 번들의 다른 행은 baseline과 byte-identical이다. 새 저장 schema/profile/receipt·권한을 만들지 않았다. workspace1·receipt3/nativeBodyContexts·소유권·권한·읽기·Review/Confirm·최종 CAS와 기존 ApplySlots 보호를 유지한다. 정보별 struct·종류 enum·모듈 interface·명시 async 전환 전 sync caller 오류를 유지한다.

개발 18건, 정상 종료 18건, 실패 원인 `{}`, 준비 단계 진단 `[{"action": "launch dev-chain", "result": "prelaunch assertion: dev-chain.py missing from orchestration copy list; no worker or build launched", "fix": "Copied existing sequential focus/checks orchestrator; baseline exit0 retained"}]`를 최종48과 구분해 보관했다. 준비 단계의 누락된 순차 실행 파일 보완은 worker/build 시작 전이며 제품 실패와 구분했다.

이전 runtime `8a888810f1ae44948b995c091e25f60b01c0c0cb`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard가 거절했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20·실제 double/out 실행을 확인했다. 이전 package·원본 source inode/hash/mode/mtime를 보존했다. 일반 Reference reader migration/downgrade를 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | b1b3c4379151dc1dce067f7e0be49f9105325dd5 | 7951d9d0abb65f8b7874301c7b140af006be9aa06b9103a8d8b54b343872005f | 54163149 |
| rollback | 8a888810f1ae44948b995c091e25f60b01c0c0cb | c1eb13086505625836141c54ebc34d960b163f99b464d382ee114457621728f8 | 54164293 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/0c54162070f64bd98ceb85e2f70a785d.json`, evidence SHA256 `62d94b712178d84586749fa1ea3763928bbdf10328316de4e1e55d2c80add352`. 개발 record `/workspace/artifacts/v536-verification-managed/runs/e69b925609c04b9ebe3d7f260c6bb871.json`, evidence SHA256 `f65613e7ad45c0b58bf2994e765a95dd6059f377fd88ef76d34e86c187dda763`. 두 package·두 evidence hash를 대조했다. 원본 checkout·기존 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23671504896bytes(22.05GiB).

다른 private 역할·타입/수/구조 변경, 반환 소비의 명시적 대응, 부모 ABI, retained/opaque/copy/import 결합과 일반 reader migration은 잔여다. 이 유한 범위를 영구 UX 정책으로 확정하지 않는다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면·과거60/480초·전송 오류 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
