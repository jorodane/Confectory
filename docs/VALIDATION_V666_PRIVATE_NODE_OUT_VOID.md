# Private C# 미사용 long→void 반환과 out 연결 검증

게시본 `6025ff450ceb4b7eb5737e93aec4baeeafd2aa47`와 기존 증거를 보존하고 runtime `b5cbdce14e40ccf82199e9c92147ffaf78ff1008`의 [미사용 long→void 반환과 out 연결](V666_PRIVATE_NODE_OUT_VOID.md)을 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9다.

- 소유 qualified `inner/body` next-code의 원래 두 long 인자(첫 값, 마지막 out)를 유지하고 사용되지 않는 long 반환만 void로 명시한다. 원래 methods-v1 scope·모든 입력/out 선언과 연결·부모 frame/public/native ABI·locals·배치/실행선·선택 밖 원문 bytes/mtime를 유지한다. 반환 포트의 암시적/명시적 소비는 out 소비와 구분한다. 새로운 출력 연결·소비 대응·저장소·기본값·자동 C# 수정은 만들지 않는다.
- 원래 C#은 out99와 long 반환129를 계산하고 실제 최종104를 실행했다. CLR reflection은 원래 두 인자·동일한 long&/IsOut=true·반환 long을 확인했다. 직접 작성한 void 본문/helpers와 다른 native 본문은 out25·실제 void/null 반환·최종20을 실행했다. 별도의 수동 void 본문은 기존 out99·최종104를 유지했고, 선택한 다른 native 원문은 그대로였다. 같은 결과 사례가 임의의 본문에 대한 자동 의미 보존을 뜻하지 않는다.
- out을 다른 노드 입력·지역 source·지역값을 통한 exit에서 함께 사용하는 원본을 실제 Save/cold/Review/Confirm으로 전환하고20을 실행했다. 원래 out 소비 JSON·순서·좌표·인자 수/이름/타입/역할과 선택 밖 소비 C# 원문을 유지했다. 원래 반환을 암시적 exit·명시적 return 포트·지역 source·다른 노드 입력에서 사용하는 네 원본도 이전 온전한 패키지에서 먼저 유효하게 실행했고, 현재 전환 후보는 그 소비를 버리지 않고 전체 거절했다.
- 기존 값 반환 본문을 그대로 둔 void 후보는 CS0127, out을 할당하지 않는 본문은 CS0177, 할당 전에 읽는 본문은 CS0269로 거절됐다. C# 반환식을 자동 삭제하거나 out 기본값을 넣지 않았다. 잘못된 원본 source/graph/before 서명·타입/이름/역할/인자 수 혼합·double 반환·공개 계약·helper 경계·마지막 native 본문도 전체 거절하고 원본·checkpoint를 보존했다.
- 기존 반환 타입/매개변수/본문/helpers 영역을 사용한다. editableNativeReturnTypes는 원본에서 계산한 읽기 metadata이며 이 out 문맥에는 void만 제공하고, 기존 값 인자의 double/void는 유지한다. 기존 선언 그대로의 본문 편집과 저장 후 void/out의 body-only CRLF 본문/helpers 보존, 취소·Undo/Redo·첫 owner Save 전 재진입·fresh DOM 초안 복원·거절 입력 보존을 확인했다. 모의 metadata DOM과 실제 Linux engine/Chromium 화면을 구분했다.
- 실제 Save/cold·쓰기 실패/재시도·응답 유실/중복 방지·늦은 설명·기본/독립 창·프로젝트 경계·후속 설명/본문 Save·Review 취소/Confirm을 검사했다. 후속 본문은 현재 void/out 서명과 whole을 확인하면서 최초 long/out 서명·source/graph 해시·물리 읽기 버전을 유지했다. Review 뒤 graph·독립/private source·caller header·선택 native source 경합은 전체 Confirm을 차단하고 peer/checkpoint/input을 보존했다. 원본 복원 뒤 새 Review/Confirm과20 실행이 통과했다.
- 기존 private out→값·native 값→ref·struct 입력·whole API·native 반환·retained guard·등록 helper와 직전 private 미사용 out 삭제 후보/guard를 새로 실행했다. 미사용 out 삭제·값→out·ref/값·순서·상수 인자 삭제·값 인자의 double/void 반환·타입/이름 DOM 회귀도 실행했다. 모든 private/retained/opaque 조합이나 전체 UI 검사로 표현하지 않는다.
- 새 Windows용 package의 구조/hash/mode 사전검사와 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창·실행·DOM을 확인했다. package 실패 주입은 기존 runtime/package를 보존했다. Windows 산출물 사전검사는 실제 Windows 기기 실행 증거가 아니다.

제품 변경은 Graphs·feature-authoring.js·WebBundle의3파일이다. Contracts·WholeBodies의 기존 Returns 계획과 나머지 보호 파일은 baseline과 byte-identical이다. 새 저장 schema/profile/receipt나 권한을 추가하지 않았다. workspace1·receipt3/nativeBodyContexts·소유권·읽기·권한·Review/Confirm·최종 CAS와 이전 ApplySlots 선택 소스 그룹 보완을 유지한다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류도 유지한다.

개발 검사 18건 중 정상 종료 18건·실패 0건이다. 개발과 최종48은 별도 신규 실행이다. 개발 실패 원인 `{}`, 준비 단계 진단 `[]`를 구분해 보관했다. trusted UI 경합 클릭과 늦은 설명 확정 원문을 개발1·최종2 path/hash로 확인했다.

이전 runtime `2463533549e580fb55132e7621c81776af92194d`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard는 거절했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20 실행과 실제 void/out을 확인했다. 이전 패키지·원본 source hash/inode/mode/mtime를 유지했다. pending과 확정 source 호환성은 별개이며 일반 Reference reader migration/downgrade는 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | b5cbdce14e40ccf82199e9c92147ffaf78ff1008 | 10753a8d9ba275ed606706f00e1526bf4eeac9e4eef54ee3bdb351e3d200b4f6 | 54165013 |
| rollback | 2463533549e580fb55132e7621c81776af92194d | ba9241c4695bfb37487ee15301e2d09db3a4a08999bff9217c8a47a749d66abb | 54166235 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/e6e340a826214f0d803533732bde2e16.json`, evidence SHA256 `b375f686cd88a3941aabd28083e3c6496cd619935df791a843ab5633b3e1a70e`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/1ed17a6db9674917b07e76772297f96d.json`, evidence SHA256 `bab2de594716e6af0e2b4187592bf7ac9af2e843d389ed1dffd6359375d9ad4f`.
두 package·두 evidence hash를 대조했다. 원본 checkout·과거 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23714877440bytes(22.09GiB).

완료 범위는 원래 두 long 값/out 인자와 모든 out 연결을 유지한 미사용 long→void 반환·수동 본문/helpers·다른 native 본문 공동 저장이다. 다른 역할·타입/수/입출력 구조·사용되는 반환의 대응·새/alias 저장소·부모 ABI와 추가 retained/opaque/copy/import·외부 관측은 잔여다. 이 유한 조건을 일반 기능의 영구 UX 정책으로 확정하지 않는다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면·과거60/480초·전송 오류 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
