# Private void→long 반환 생성과 기존 out 연결 검증

게시본 `6db32f192a0d99a09f284d5e25b6255479577974`와 증거를 보존하고 runtime `8a888810f1ae44948b995c091e25f60b01c0c0cb`를 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9다.

이번 범위는 methods-v1의 소유 qualified `inner/body` next-code다. 원래 두 long 인자(첫 값, 마지막 out)를 유지하고 void 반환만 long으로 명시한다. 새 native 반환은 연결하지 않는다. 원래 input/out 선언·연결·소비, 부모 frame/public/native ABI, locals·실행선·좌표 및 선택 밖 C# bytes/mtime를 유지한다. 새 저장소·기본값·반환문·cast·연결을 자동 생성하지 않는다.

원래 void/out99는 실제104를 실행했다. 수동 본문/helpers는 long 반환55/out25를 계산하고, 별도로 선택한 다른 native 본문과 함께20을 실행했다. 별도의 수동 본문은 long 반환129/out99를 계산하면서 기존 최종104와 다른 native 원문을 유지했다. CLR reflection으로 실제 반환 타입과 값, 동일한 두 인자·Long&/IsOut=true를 확인했다. 자동 의미 보존을 주장하지 않는다.

기존 out을 노드 입력·local source·local을 통한 exit에서 함께 소비하는 원본을 실제 Save/cold/Review/Confirm으로 전환하고20을 실행했다. 원래 소비 JSON과 선택 밖 소비 C#은 그대로다. 존재하지 않는 원래 void 반환을 암시적 exit·명시적 return 포트·local source·노드 입력에서 참조하는 네 원본은 별도로 기록했다. 암시적/명시적 exit·노드 입력 세 원본은 실제 build 실패 뒤 후보를 거절했고, local 원본은 기존 정의 검사에서 GRAPH_LOCAL_ALIAS_SOURCE로 먼저 거절됐다. 이 네 사례를 유효한 원본 실행 증거로 계산하지 않는다. 새 반환을 기존 out exit 대신 연결하는 변조도 guard에서 거절했다.

기존 void의 `return;`을 둔 long 후보는 CS0126, 모든 경로의 반환 누락은 CS0161, out 할당 누락은 CS0177, out 할당 전 읽기는 CS0269로 거절했다. 원본 source/graph/before 서명·타입/이름/역할/인자 수 혼합·double 반환·공개 계약·helper 경계·마지막 native 본문 오류 역시 전체 거절하고 원본/checkpoint를 보존했다.

계산된 읽기 metadata는 이 원본 문맥에 long만 제공한다. 기존 반환/매개변수/본문/helper 편집 영역을 사용하며 본문과 반환문은 수동으로 작성한다. 모의 DOM은 원문 CRLF·초안 복원·재진입·취소·보호 영역·거절 입력을 확인했다. 실제 Linux engine/Chromium은 별도로 원본 UI의 Cancel·Undo/Redo·첫 owner Save·cold·Review/Confirm과 경합을 확인했다. 실제 화면 검토 SHA는 `ee193c3e6e38d1f8edfd4ba97a6688b2cc2f5f230bdde50dfc61e2ecd6267771`다.

실제 Save 실패/재시도·응답 유실/중복 방지·프로젝트 경계·기본/독립 창·후속 설명 및 본문 Save를 검사했다. 현재 long/out 서명·whole을 확인하면서 최초 void/out source/graph 서명과 물리 읽기 버전을 보존한다. Review 뒤 graph·private/독립 source·caller header·선택 native source 경합은 Confirm을 차단하고 peer/checkpoint/input을 유지한다. 원본 복원 뒤 새 Review/Confirm과20 실행이 통과했다. trusted UI 경합 클릭과 늦은 설명 확정 원문을 개발1·최종2 path/hash로 확인했다.

직전 private out 유지 long→void native/guard와 기존 native/ref/out·struct·whole·반환·retained·등록 helper 회귀를 새로 실행했다. DOM은 기존 값/ref/out·삭제·순서·타입/이름·반환 흐름도 포함한다. 새 Windows 산출물의 구조/hash/mode 검사와 Linux 실행, 전체 ZIP 별도 복원, package 실패 시 이전 package 보존을 확인했다. Windows 산출물 검사는 실제 Windows 실행과 구분한다.

제품 변경은 Graphs·Contracts·WholeBodies·feature-authoring.js·WebBundle의5파일이다. 새 반환 계획을 기존 부모 ABI/본문 및 후속 Save 허용 범위에 명시적으로 연결했다. 나머지 보호 파일과 번들의 다른 행은 baseline과 byte-identical이다. 새 저장 schema/profile/receipt·권한을 만들지 않았다. workspace1·receipt3/nativeBodyContexts·소유권·권한·읽기·Review/Confirm·최종 CAS와 기존 ApplySlots 보호를 유지한다. 정보별 struct·종류 enum·모듈 interface·명시 async 전환 전 sync caller 오류도 유지한다.

개발 15건, 정상 종료 14건, 실패 원인 `{"dev-private-node-out-long-native": "Fixture expected every malformed void-return consumer to reach candidate generation. Existing original definition validator rejects local alias first with GRAPH_LOCAL_ALIAS_SOURCE; explicit early-refusal proof now records unchanged files. Product unchanged; failed log/fixtures preserved."}`, 준비 단계 진단 `[]`를 최종48과 구분해 보관했다. 이전 runtime `b5cbdce14e40ccf82199e9c92147ffaf78ff1008`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard가 거절했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20·실제 long/out 실행을 확인했다. 기존 패키지/source inode/hash/mode/mtime를 보존했다. 일반 Reference reader migration/downgrade를 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 8a888810f1ae44948b995c091e25f60b01c0c0cb | c1eb13086505625836141c54ebc34d960b163f99b464d382ee114457621728f8 | 54164293 |
| rollback | b5cbdce14e40ccf82199e9c92147ffaf78ff1008 | 10753a8d9ba275ed606706f00e1526bf4eeac9e4eef54ee3bdb351e3d200b4f6 | 54165013 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/fce9df8b28544ce7b44db84c103903b8.json`, evidence SHA256 `2b1f5d8e95f0f5ae857fd8d0def563c7962e02776dc665dd75c72c9de2efb0f3`. 개발 record `/workspace/artifacts/v536-verification-managed/runs/329eabd32570429194b84ef539833dfb.json`, evidence SHA256 `5b9dfc89b6612bd4c5ed888982fa850cdd2d87820dc6462f8b6bd81fce5a8f2a`. 두 package·두 evidence hash를 대조했다. 원본 checkout·기존 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23693860864bytes(22.07GiB).

다른 private 역할·타입/수/구조 변경, 기존 소비를 바꾸는 명시적 새 반환 연결, 부모 ABI, retained/opaque/copy/import 결합과 일반 reader migration은 잔여다. 이 유한 범위를 영구 UX 정책으로 확정하지 않는다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면·과거60/480초·전송 오류 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
