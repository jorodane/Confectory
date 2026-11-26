# v821 직접 소유 자식 frame의 일반 동작 추가

2026-11-20. 시작 게시본은 `157dd73575f13771baf7e9df3790f9674cedf664`다. 이전 자식 순서·슬롯 교체 기록은 별도로 보존한다. 이번은 기존 일반 셀이 있는 직접 소유 자식에 인수 없는 void C# 동작 하나를 추가하는 첫 단위다.

## 소유·계약과 저장 경계

- 물리 root·전체 child graph ID/path·root/frame 관측 해시와 기존 source proof/checkpoint를 사용한다. 기존 `documentFrameOrderBinding`은 편집 허가가 아니며 서버가 관측과 계획을 다시 검사한다. 같은 local ID가 형제/부모에 있어도 자식을 추정하지 않는다.
- 직접 소유 `sync-acyclic-nested-v1` 전체 트리가 기존 exit로 끝나는 완전한 독립 직렬 code/graph 사슬이며, 선택한 비어 있지 않은 자식이 일반 next C# 셀만 포함할 때 지원한다. depth 8·전체 256개·frame별 63개·편집 64개·관측 소스 64개·기존 byte budget은 유지하고 새 셀까지 포함해 검사한다. 공유/분기 진입·call/opaque/receiver·copy/slot·forwarded storage·async·상속 문맥은 이 경로에 열지 않는다.
- 기존 셀 바로 다음 연결 한 곳에 args 없는 void 셀 하나를 넣는다. 생성·이름·의도·본문과 두 next 연결의 정확한 6개 편집만 허용한다. 기존 entry/exit·스코프·입출력·arguments·C# 파일·형제/부모 후속 흐름은 유지한다. 기존 노드의 본문/계약/구조 변경이나 삭제·복수 생성·다른 frame의 입력과 섞지 않는다. 원래 소유 root 소스에 다른 저장 편집이 있으면 먼저 Confirm/discard해야 한다.
- 기존 `BlueprintNode`가 같은 프로젝트 안에 새 `nodes/<server-guid>.node.json`을 만들며 source ID는 `root/node:<전체 부모 경로>/node:<새 local ID>`다. 경로/파일명을 클라이언트가 정하지 않는다. 같은 local 이름이 있는 부모나 형제의 파일을 가져오거나 덮지 않는다. raw graph/프로젝트/노드 레코드·체크포인트 버전과 런타임 의미는 추가하지 않는다.
- 새 연결과 C# 본문은 같은 isolated 후보에서 root 전체로 검증하고 기존 checkpoint lease로 원자 저장한다. 기존 코드/선언 원본 읽기 가드(`propertyObservations`라는 기존 필드/검증기)를 사용해 프로젝트 등록·원래 코드·형제·새 파일의 missing 관측을 cold→Review→최종 파일 commit lease까지 보존한다. 이 가드는 property 노드뿐 아니라 기존 owned code/declaration closure도 검증하며 읽기 관측으로 쓰기 권한을 만들지 않는다. nested 경로도 기존 원본 등록 읽기에 포함한다.
- 저장 전 개인 Undo/Redo와 전체 경로별 cold 입력 복원을 제공한다. 저장 후는 기존 소유 멤버십 변경인 `OWNERSHIP_CHANGED` 경계를 유지한다. 공유 Undo/Redo 요청의 전송 성공과 `accepted:false/changed:false` 거절을 구별한다. 새 파일을 지워 되돌리는 의미를 만들지 않는다.
- v821 문서형 수직 셀·입력 왼쪽/출력 오른쪽·조건 탭·기존 Blueprint·보기를 유지한다. 추가 버튼을 기존 셀에서 연결하며 새 레이아웃이나 설명 행을 넣지 않는다. 새 동작은 기존 보호 C# 편집기로 작성하고 실제 실행은 명시 Save/Review/Confirm 뒤 확인한다.

## 실제 검증

고정 제품·검사 소스는 `e6b0973d341e736b5e58a0e772408502cb1bff34`다. 최종 record `035ba75f25714e239ca4980ece3f07ea`는 `cleaned`, 오류 없음, 신규 **25단계 통과·실패 0·재사용 0**이다. .NET SDK 10.0.401과 수정 없는 독립 LF 체크아웃 하나에서 실제 Linux 엔진·Chromium으로 실행했다. 이 문서와 기준 문서의 후속 커밋은 검증한 제품·검사 소스를 바꾸지 않는다. 개발 overlay/실패/진단 결과를 최종 고정 실행에 합산하지 않는다.

| 신규 단계 | 실제 통과 범위 |
| --- | --- |
| 1–6 | LF 복제·고정 checkout, .NET 복원·Release·MCP·Linux 엔진 빌드 |
| 7–8 | 전체 child 경로의 추가 성공, 공유 진입 거절·입력 보존·원래 실행 |
| 9–11 | 이전 자식 순서 편집의 성공·값 의존성·공유 진입 거절 회귀 |
| 12–13 | 이전 복합 전체 이동과 분기 내부 추가·이동·실행 회귀 |
| 14–17 | 문서형 조건 탭·접힘, 일반 셀 추가·이동, 생성 미리보기·네이티브 편집 |
| 18–19 | 이전 슬롯 교체 성공·계약 불일치와 원본/입력 보존 |
| 20–22 | Windows x64 교차 패키지·구성/probe, managed 앱의 Linux child 추가 전체 성공 |
| 23–25 | 전체 복원 후 공유 진입 거절·입력 보존/실행, 네이티브 실행, 패키지 실패 수명 |

- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/035ba75f25714e239ca4980ece3f07ea.zip`
- 증거 SHA-256: `19b7bdc68c66397a1b73f67a97826f1cd121d7d64002cc68293f707892813b0b`
- 패키지 source: `e6b0973d341e736b5e58a0e772408502cb1bff34`, 54,250,610bytes
- 패키지 SHA-256: `e6eb133881a1580627a72b3f9746ca7fa632e5bb504fe89cc99f14dbb61aa6a8`
- 전체 복원은 파일 2,761개와 디렉터리 158개, 합계 2,919개 항목의 바이트·종류·모드를 대조했다. `full-restore.json`의 `files`는 디렉터리를 포함하는 항목 수다.
- 인증된 2세대 저장소 latest는 위 소스이며 rollback은 이전 검증 소스 `58178272bcf88eb0cf08f852c0c7dc999a027a26`다. rollback 54,245,177bytes와 SHA-256 `8d60e313400812653379416835a80548df2bebed97227e9e3e0b3e4d061d2bf1`도 실제 파일에서 재확인했다. 전체 검증·증거 보관 후 승격했고 이번 인증된 임시 공간만 정리했다. 기존 원본 체크아웃 `b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee`와 알 수 없는 기존 임시 폴더는 보존했다.

대표 Linux fixture는 `body/nest`와 `other/nest` 양쪽에 `inner`/`tail`을 둔다. 선택한 자식의 inner 뒤에 새 동작 하나를 추가·편집하고 개인 Undo/Redo·cold 복원, 기존 보기 전환과 다른 frame 입력에 의한 조작 거절을 검사한다. 같은 이름이 부모에 있는 제안은 다른 자식으로 해석하지 않으며, depth·frame별·전체 노드 한계는 새 셀을 포함해 거절한다.

전체 경로/해시·owner/frame·ABI·scope·continuation·기존 source 대상·삭제/복수 생성·stale proof/checkpoint·혼합 의도를 거절하고 초안/원본/입력을 보존한다. 형제 원본 변경과 checkpoint 권한 실패 후 재시도·cold는 정확한 새 child body 하나만 저장한다. Review 취소, 최종 형제 CAS와 읽기 전용 graph 거절에서 기존 파일·입력·동시 변경과 새 파일의 missing 상태를 유지한다.

새 Confirm 뒤 실제 출력은 `body → inserted-child → inside → parent-tail → peer-inner → peer-tail → after → 10`, 종료값은 10이다. 물리 파일 변경은 graph 하나와 새 C# node 레코드 하나다. 새 node와 두 연결만 제거해 원래 edges로 되돌리면 전체 graph 객체가 원본과 같다. 기존 모든 다른 소스 바이트와 모든 원본 모드·명시 입력/반환·부모/형제 후속 실행을 유지하고 다시 열린다.

개발 최초 시도에서는 Save/cold/소유권 경계가 통과했지만, 형제 파일 변경 뒤 Confirm이 실제 성공하는 결함을 발견했다. 트래픽의 `sourceConfirmed:true`와 물리 graph/새 node 쓰기를 보존했다. 최종 read-baseline 가드가 없었던 원인을 기존 관측/최종 lease로 연결했다. 후속 Save 거절은 요청이 미적용(`checkpointSaved:false`, 빈 changes)임을 먼저 확인했다. 격리 clone의 짧은 진단에서 `Property project registration observation required`를 확인하고, 기존 nested 읽기에 원래 manifest를 포함했다. 가드를 줄이거나 UI 성공으로 꾸미지 않았다. 진단 없는 엔진에서 성공/공유 진입 거절을 별도 재검증했다. 진단 출력은 제품에 넣지 않았으며 과거 초기 빈 화면 원인과 구별한다.

실제 소스 앱 캡처에서 `Pair › body › nest` 경로와 inner 뒤에 생긴 새 수직 셀, 왼쪽 입력·오른쪽 출력/없음 표시를 직접 확인했다. 원본 v821 목업과 직접 시각 대조한 결과는 아니다. 기존 슬롯 회귀는 실제 반환값 45/out 55·true를 유지했고, 복원본 네이티브 회귀는 컴파일 실패·늦은 입력·원본 CAS를 보존한 뒤 실행값 15를 확인했다. 기존 표시 없는 API/그래프 경로의 대표 회귀와 모든 구 실행 파일·reader의 호환을 구별하며 후자는 이번에 보증하지 않는다.

개발 증거 record `26eaa76033194f23a10c970dcdb3b1ee`는 위 Confirm 결함·미적용 저장 거절·격리 진단과 수정 후 별도 성공을 보존한다. ZIP SHA-256은 `686e466d9d47fb5fb144a691680595d5ceea07ecd9c80ec0ec9cfa6b7fbdd743`다. 제품에 진단 출력을 포함하지 않았고 인증된 개발 임시 공간만 정리했다. 최종 신규 25단계와 합산하지 않는다.

## 기존 빈 void 자식의 첫 동작 삽입

실행 계약은 기존의 `nodes: []`, `edges: []`, `entry: "exit:return"`, `exits: {"return": null}`을 이미 지원한다. 직접 소유한 인수 없는 void 복합의 해당 경로에서만 기존 일반 셀 추가를 연결한다. 빈 frame 관측은 정확한 반환을 확인하는 무변경 순서 계획이며 실제 순서 편집을 허용하지 않는다. 첫 동작의 새 entry와 원래 return으로 가는 연결만 생성하고, 삽입 후 기존 전체 복합 검증을 다시 거친다. 선택하지 않은 빈 frame, 다른 반환 계약, 복사·공유·비동기 등 기존 미지원 경계는 그대로다.

기존 원본·소유권·전체 본문 관측과 최종 lease, 저장/검토/확정 모델을 재사용한다. Save 전 개인 Undo/Redo는 새 동작 입력 여섯 개를 함께 이동하며 Save 뒤 기존 `OWNERSHIP_CHANGED` 공유 이력 보호를 유지한다. 새 C# 파일은 명시 Confirm 뒤에만 생성한다.

[빈 자식 삽입 검사](../tests/web/v821_empty_child_insert_ui.py)에서 Linux Chromium의 실제 빈 자식 진입, 첫 동작 및 C# 편집, 개인 Undo/Redo와 재시작, Save/Review 충돌 거절 및 명시 Confirm을 검증했다. 삽입 전 `body → inside → parent-tail → after`, 확정 후 `parent-tail`과 `after` 사이에 새 동작만 실행됐다(반환값 10 유지). 재개방 뒤에도 정확한 frame과 기존 형제는 유지되었다. 비void·인수 있는 빈 frame 및 임의 return 변경은 metadata 계획에서 거절했다. 최초 검사에서 하위 `nodes/`의 생성 파일을 세지 못한 시험 오류를 수정한 뒤 전체가 통과했다. 비어 있지 않은 기존 자식의 시작 삽입(`v821_child_insert_ui.py start`)과 정상 객체 드래그 입력도 같은 빌드에서 통과했다. 실제 Windows/WebView2는 미실행이다.

## 남은 범위

내부 삭제·복합 생성/분해·여러 frame/여러 새 셀의 공동 편집, 슬롯 내부, private 네이티브 보기와 분기/opaque/receiver/async/copy/상속 문맥은 별도 범위다. 이번은 인수 없는 void 셀 하나이며 모든 ABI·구조·실행 조합이나 전체 엔진 검증이 아니다. 기존 source scope가 바뀐 미결정 요청은 자동 rebase하지 않고 입력을 보존한다.

실제 Windows/WebView2·물리 기기·전체 UI·원본 v821 목업 직접 시각 대조·신규 CRLF 실행은 미실행이다. Windows x64 교차 패키지와 Linux managed 앱 검사를 실제 Windows 실행과 구별한다. 기존 reader Reference 제약과 과거 초기 빈 화면 원인은 이번 단위로 해소됐다고 단정하지 않는다. main과 Sites는 변경하지 않는다.

## 중첩 private 일반 셀에서 등록 기능 호출

직접 소유 물리 root의 정확한 child 경로를 사용해, 기존 일반 직렬 private frame의 시작 또는 일반 셀 다음에 등록된 동기 기능을 참조한다. root의 typed import 및 선택된 child의 호출·입력·정확한 next 연결을 기존 격리된 authorBatch에서 한 후보로 저장한다. 호출 등록은 private frame 밖에 별도 코드 원본을 생성하거나 호출 대상 본문을 복사하지 않는다. 원래 root/frame/source proof, 체크포인트, 소유 경로 및 물리 원본 검사를 유지한다. Review/Confirm의 읽기 관측은 선택된 root의 실제 본문·선언·등록 기능 closure에 한정하고 무관한 선택 입력을 가져오지 않는다.

재실행: `tests/web/v821_private_call_ui.py <repo> <run-report> normal` 또는 `method-nested`. 두 레벨의 `body/nest`와 같은 local ID를 가진 `other/nest`를 사용하는 합성 프로젝트에서 기능 검색/취소, 한 번의 개인 Undo/Redo, 현재 frame 입력 amount 연결, 외부 변경 Save 거절, 형제 원본의 최종 Confirm 거절, Review 취소, 확정과 컴파일·실제 실행 순서(7 전달, 원래 반환 10), 재시작, 독립 객체 설명 초안 보존 및 같은 ID의 별도 프로젝트 격리를 검사한다. 기존 Save 이후의 소유권 history boundary는 바꾸지 않는다.

범위는 기존 일반 직렬 frame에 처음 직접 참조를 추가하는 동작이다. 기존 호출이 섞인 frame에서 추가 호출 삽입, 공유/암시적 분기, ref/out·async·public execution 계약, Windows 실기는 확장하지 않았다.

일반 중첩 profile은 별도 프로젝트를 열었다 돌아온 뒤 실제 프로젝트 ▶에서 전달값 7의 독립 표식과 종료 코드 10까지 확인했다. method-nested profile은 동일 제품 UI Save/Review/Confirm과 실제 컴파일러 실행, 재열기 및 독립 입력 보존이 통과했다. 기존 일반 child 삽입, root switch case 호출 및 최초 기능 호출의 Linux 회귀도 통과했다.

### 기존 호출 이후 연속 호출

`tests/web/v821_private_call_ui.py <repo> <run-report> normal --multiple`은 기존 중첩 frame의 첫 호출을 Save하고 Confirm 없이 재시작한 뒤 두 번째 호출을 추가한다. 일반 편집·이동 판정과 별도로 참조 삽입의 정확한 frame binding을 제공한다. 이전 Save의 원본/초안 증명과 소스 소유권이 일치하는 경우에만 동일 root의 다음 호출을 허용한다. 다른 편집을 자동 합치거나 승인하지 않는다.

첫 반환값을 두 번째 입력으로 연결하고, 두 번째 삽입의 개인 Undo/Redo, 외부 호출 선언 변경 거절과 재시작 후 재시도, Review 취소와 형제 원본 변경 거절, Confirm, 실행 순서 (`private-probe:7`, `private-next:12`), 재개방, 독립 설명 입력과 동일 ID 별도 프로젝트의 보존을 확인한다. Confirm 이후에도 다시 호출을 추가할 수 있는 버튼이 활성화된다. 한 번의 Save에는 기존처럼 호출 한 건이 포함된다. private 분기, ref/out, async 및 Windows 실기는 이번 범위가 아니다.

같은 `--multiple` 시나리오는 `method-nested`에서도 통과했다. 일반 child 삽입(`v821_child_insert_ui.py normal`) 및 기존 root 분기 직접 호출(`v821_branch_structure_ui.py call`)도 같은 Linux Chromium 빌드에서 통과했다.

### 여러 직접 호출의 한 번 Save

`v821_private_call_ui.py <repo> <run-report> normal --batch`에서는 두 호출을 모두 로컬 입력으로 작성하고 첫 반환값을 두 번째 입력으로 연결한 뒤 한 번에 저장한다. 기존 직렬 frame의 정확한 gap을 로컬 호출 삽입 순서로 대조하고, 저장 후보는 최종 실행 순서로 재생한다. 각 호출의 기존 선언/타입/원본/소유권 검사를 유지하면서 동일 격리 후보 안에서만 적용하며, 마지막 호출이 거절되면 체크포인트 전체가 그대로 남는다. 미결정 저장 시도는 해결하기 전 새 호출 삽입을 막는다.

일반 중첩 및 `method-nested --batch --loss`에서 실제 Linux Chromium 검색, 개인 Undo/Redo, 값 연결, 두 번째 호출의 외부 선언 변경에 대한 전체 Save 거절, 재시작 후 재시도, Review 취소와 Confirm 원본 충돌, 실제 실행과 재개방, 독립 입력 및 동일 ID 프로젝트 격리를 검사했다. `--loss`는 실제 호스트가 체크포인트를 기록한 후 응답만 유실하도록 하여 재시작 뒤 별도 적용 명령 없이 정확한 영수증을 복구하는 것을 검증한다. 기존 각 호출별 Save도 가능하다. private 분기 및 Windows 실기는 별도 범위다.

`normal --batch --reverse`는 소비하는 호출을 먼저 작성한 뒤 그 앞에 결과를 제공하는 호출을 삽입해 연결하여, 생성 순서가 아닌 실행 순서로 저장·실행됨을 확인했다. `normal --multiple` 기존 분할 Save 경로도 동일 빌드에서 통과했다.

### Private 복합 분기에서 직접 호출

`v821_private_case_call_ui.py <repo> <run-report> empty` 및 `after`는 기존의 명시 분기 반환과 일반 셀 사이에 등록 기능 두 개를 삽입한다. `after --nested`는 두 단계 `body/nest`를 사용한다. 기존 분기 소유 ID와 정확한 기존 case/next/return 연결을 root/frame 증명과 함께 확인하고, 이전 호출의 반환을 다음 호출의 입력으로 연결해 동일 분기의 한 번 Save로 저장한다. 각 호출의 기존 계약/원본 검증과 최종 컴파일 검증은 유지한다. 별도 순서·삭제·분기 이동 계약은 바꾸지 않는다.

실제 Linux Chromium에서 빈 분기·셀 사이·중첩 경로, 개인 Undo/Redo, 외부 호출 선언 수정에 따른 전체 Save 거절, 재시작 후 재시도, Review 취소와 형제 원본 변경에 따른 Confirm 거절, 정확한 원본 차이, 독립 설명 입력 및 같은 ID 별도 프로젝트의 격리를 확인했다. 컴파일 실행 출력은 해당 분기에서만 `case-probe:7` 다음 `case-follow:12`가 나오고, 나머지 분기·continuation 및 기존 종료 코드 14는 그대로였다. 별도 프로젝트에서 돌아온 뒤 실제 프로젝트 ▶도 종료 코드 14를 확인했다. `shared` 시나리오는 공유된 분기 진입에서 호출 삽입을 제공하지 않는다.

범위는 기존의 명시적·독립된 두 비주 분기가 기존 owner로 반환하는 직접 소유 동기 switch frame이다. 한 배치의 여러 호출은 동일 case에 한정한다. 암시/default 경로, 공유 진입, 다른 분기 동시 편집, ref/out·async·public execution, Windows 실기는 확대하거나 검증하지 않았다. 기존 직렬 `v821_private_call_ui.py normal --batch --reverse`도 같은 빌드에서 통과했다.

기존 루트 분기 `v821_branch_structure_ui.py call`도 동일 빌드에서 통과했다.

### 새 기능을 복합으로 전환한 뒤 일반 동작 추가

`v821_new_function_document_ui.py <repo> <run-report> compound`은 기존 프로젝트 브라우저의 새 기능 만들기에서 직접 작성, 원본 코드 Save/Confirm, 내부 흐름 진입 및 복합 전체의 개인 Undo/Redo, Save/Confirm, 재개방, 첫 자식 앞 일반 동작 추가까지 실제 제품 UI로 진행한다. 새 기능의 기본 switch-capable profile은 동기 직렬 흐름에서도 사용되며, 내부화가 만드는 기존 `retainedCode` 및 반환 export 때문에 종전 nested-only 분류가 일반 자식 삽입을 제공하지 않았다.

기존 원본을 보존하는 직접 소유 wrapper의 정확한 경로와 전체 직렬 next 연결을 확인하고, 분류용 복사본에서만 고정 반환 export를 종료 경계로 취급한다. 실제 후보의 retainedCode, 반환 export/값 및 다른 실행선을 바꾸지 않는다. 기존 원본·초안 증명, 전체 소스 관측, 독점 경로, 컴파일/Confirm 및 깊이/노드/바이트 제한을 유지한다. 이 특별한 관측은 삽입 전용이며 전체 순서 재작성이나 임의 반환 변경에는 사용하지 않는다. 소스가 새로 소유되는 Save의 기존 `OWNERSHIP_CHANGED` 경계도 유지한다.

실제 Linux Chromium에서 첫 Confirm 뒤 재개방한 신규 기능, 내부화 및 그 전체 미저장 작업의 Undo/Redo, 새 자식 삽입/Undo/Redo, C# 원문 편집, 외부 그래프 변경에 따른 전체 Save 거절, 재시작/재시도, Review 취소/Confirm, 원래 graph 및 반환 export와 물리 retained C# 보존, 냉간 재개방을 검증했다. 별도 합성 실행 사본의 일반 ▶는 원래 `new function executed` 및 새 자식 `37` 표식을 모두 기록했다. 이번 새 기능 시나리오는 Confirm 후 재개방하여 정확히 갱신된 모델을 사용한다. 첫 Confirm 직후 갱신 전 클릭과 새 복합 Confirm 직후 선택이 오래된 상태인 문제는 별도 관측으로 남긴다.

기존 일반 child 삽입, 새 기능 최초 Save 전 등록 호출, 이미 존재하는 private case 추가의 Linux 회귀도 확인했다. 기존 case 추가의 한 차례 UI 실측은 삽입 표시 238ms, C# 입력 가능 74ms, 실제 키보드 입력 12ms였다. 이전 기록의 같은 종류 측정은 각각 307ms/75ms/7ms였다(다른 실행 시점의 단일 관측으로 엄밀한 benchmark는 아님). 신규 복합 자식 삽입 표시 244ms, 별도 재사용 합성 사본에서는 88ms 및 Save 2,441ms였다. 새 기능에서 private 분기를 처음 선언하고 여러 경로를 구성하는 기능, 기존 저장 후 복합 전체의 공유 Undo/Redo를 새로 확대하는 작업, Windows 실기는 이번 변경에 포함하지 않았다.

### 새 복합 셀의 첫 직접 소유 분기

`v821_new_function_document_ui.py <repo> <run-report> branch`는 신규 기능/복합 전환 및 자식 추가 흐름을 이어, no-argument void-data 일반 동작의 첫 분기를 논리 코드에서 명시적으로 선언한다. 기존 보호 C# editor에서 `Result`를 통해 실행 분기를 선택하며, 주 흐름과 두 비주 분기의 명시적 `return:owner`를 같은 격리 후보에 저장한다. 선택된 분기의 반환은 기존 next 흐름으로 돌아가며 기능의 반환 타입이나 기존 terminal export 값을 바꾸지 않는다. 새로운 graph 포맷이나 의미를 도입하지 않는다.

기존 원본 wrapper 내부에서만 분기/반환 경계를 대조한다. 분류용 사본에서 고정 return export를 종료 경계로 보며, 실제 저장 시 원본 retainedCode 및 export는 보존한다. 정확한 소유/원본/초안 증명과 독점 소스 경로, Save와 Review/최종 Confirm의 CAS 및 컴파일 검증을 유지한다. 첫 선언 이후 일반 셀과 직접 호출을 기존 case 삽입 경로로 추가할 수 있다. 이 단위는 저장된 직접 소유 wrapper의 첫 selector 하나, 비주 분기 두 개, 기존 동기 반환 및 값 입력에 한정한다.

실제 Linux Chromium에서 신규 선언 및 복합 전환의 개인 Undo/Redo, 첫 분기 편집 취소 및 Undo/Redo, 외부 graph 변경 시 Save 거절, 선언 초안 Save 뒤 selector 원본 변경 시 실제 Confirm 요청 거절 및 입력/원본 보존, 복구/재시작, 빈 분기 내 일반 동작과 그 뒤의 기존 등록 기능 호출 및 정수 입력 37, 확정과 재개방을 검증했다. 격리된 실행 사본의 실제 ▶는 positive/negative/primary를 각각 호출해 0의 원래 결과와 continuation을 유지했으며 positive의 일반 셀/호출만 실행했다. 원래 retained C# 파일과 terminal export도 보존했다. 기존 `v821_private_case_call_ui.py after` 및 `shared`는 같은 최종 빌드에서 각각 정상 호출/실행·같은 ID 프로젝트 격리와 공유 분기 삽입 거절을 통과했다.

현재 작성 흐름은 복합 전환, 첫 분기 선언, 일반 셀/호출 저장의 기존 소유·검토 경계를 따라 각각 확정 후 재개방한다. 한 번에 여러 미확정 단계의 공동 저장이나 확정된 복합 전체의 공유 Undo/Redo 경계를 확대하지 않는다. 임의 분기 entry/exit, ref/out·async·공개 실행 분기, 다중 selector와 Windows 실제 실행은 별도 검증 범위다.

### 확정 전 새 복합 셀의 연속 작성

직접 소유한 기존 C# 셀을 복합으로 전환하여 Save한 경우, 아직 Confirm하지 않아도 같은 private frame에서 일반 동작 추가, 첫 분기 선언, 분기 내부 동작과 등록된 기능 호출 및 값 연결을 이어갈 수 있다. 각각의 기존 Save는 동일 로컬 초안의 체크포인트이며 마지막 한 번의 Review/Confirm으로 확정한다. 처음부터 마지막까지 Save 한 번만 하는 메모리 편집은 아직 지원하지 않는다.

원본 C#의 해시 및 소유 ID, 직전 Save의 소스 증명, 동일한 완전한 atomic group, 각 실제 원본/missing 소스의 CAS를 다시 확인한다. 다른 저장 변경, 다른 소유 형태 및 혼합 변경에는 기존 제한이 적용된다. 새 일반 셀의 원본만 정확하게 같은 묶음에 추가하며, 기존 실행/반환 계약 검증과 Confirm의 원자적 파일 쓰기를 유지한다. 기존 Save 전 개인 구조 Undo/Redo와 소유 멤버십 변경 후 이력 경계는 그대로다.

재실행: `python tests/web/v821_new_function_document_ui.py <repo> <run-report> staged`. 기존 `branch` 방식은 비교 대상으로 유지한다. 실제 Linux Chromium에서 새 기능 작성, 복합 전환 및 Undo/Redo, 자식 동작 및 분기 생성, 분기 호출과 상수 37 연결, 외부 원본 변경의 Save 거절과 cold recovery, Review 취소, 최종 원본 변경의 Confirm 거절, 최종 Confirm, 재개방을 검사했다. 실행은 기존 일반 ▶와 별도의 합성 entry harness에서 positive/negative/primary의 세 경로, 입력 37 및 원래 반환값 0을 확인한다. 실제 사용자 프로젝트와 계정, Windows/WebView2는 검증하지 않았다.

동일 Linux 빌드의 격리 프로필 각각 한 번 측정한 성공 경로의 시간이다(오류 주입, Review 열기, 재시작 및 실행 시간 제외). 복합 전환 클릭부터 문서 표시까지는 기존 2,937ms, 연속 초안 5,332ms로 개선되지 않았다. 일반 자식 추가 클릭부터 셀 표시까지는 127ms와 96ms였다. 실제 셀 편집까지도 검사했지만 이 수치는 첫 키 입력 지연 측정은 아니다. 성공한 Save 5회의 합은 기존 15,353ms, 연속 초안 13,075ms였다. Confirm 5회의 합 55,872ms가 최종 한 번 12,013ms로 줄었다. Save와 Confirm 합은 약 71.2초에서 25.1초로 줄었다. 단일 관측이므로 개별 처리 시간의 통계적 개선은 주장하지 않는다. 제거된 확정 왕복이 주효하며 복합 전환과 단일 최종 검증의 지연은 남아 있다.
