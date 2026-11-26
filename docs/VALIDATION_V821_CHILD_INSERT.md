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
