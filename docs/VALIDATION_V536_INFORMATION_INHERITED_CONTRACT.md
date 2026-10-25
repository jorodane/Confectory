# 상속 공개 핀 이름·Blueprint 부모 연결 검증

[고정 지원 범위](V536_I5_6_INHERITED_CONTRACT_SCOPE.md)에 따라 직접 소유 정보 함수의 상속 C# copy에서 공개 입력/out 이름을 편집하는 경로와 상속 Blueprint 부모의 복사를 연결했다. HTML/CSS와 기존 UI 어댑터, 원본 v536 ZIP은 이전 게시 `74ea806`과 바이트가 같다. 새 화면·권한·실행 모델을 만들지 않았다.

## 재현한 문제와 수정

공개 핀 이름을 같은 native 위치/타입/역할로 명시 대응해도, 사용하지 않는 상속 선언을 직접 구현 변경으로 처리해 `Direct owned implementation and all targets required`로 거절했다. 이제 그 native 경계가 그대로인 명시적 이름 대응은 상속 선언을 보존한다. 부모 쓰기를 허용하는 예외가 아니며 타입·역할·반환/순서 변경은 별도 guard를 유지한다.

Blueprint 부모 복사에서 `GRAPH_IMPLEMENTATION_CONTEXT_STALE`를 재현했다. 부모가 선언한 graph의 문맥을 child ID로 검증하던 것이 원인이었다. copy metadata와 실제 compiler 양쪽 모두 실제 body origin의 문맥을 먼저 검증하며, 자식과 native 이름/서명/import/scope가 정확히 같은 경우에만 사용한다. 원본 graph/node/hash를 바꾸지 않는다. 독립 선언의 node 소유권 검사는 유지한다.

처음에는 Confirm endpoint의 transport 성공만 확인한 뒤 다음 읽기에서 실패했다. 테스트를 강화해 실제 `sourceConfirmed=true`와 소유 copy/owner 전체 Review ID를 요구했고, compiler 경로의 같은 문맥 결함을 확인·수정했다. 저장을 최종 확정으로 취급하지 않는다.

확정한 copy의 본문 재편집도 선택하지 않은 부모 whole-body 계획을 요구했다. 검증된 copy 증거·같은 공개 ABI·부모 선택 부재를 확인한 경우 부모의 정확한 body/node 물리 파일 기준만 관측하여 보존한다. 부모 계획이 있으면 기존 변경/컴파일/쓰기 검사를 그대로 받는다.

추가 API 실패 하나는 fixture가 정확한 whole-body lift에 retained-graph용 출력 대응 필드를 보낸 것이 원인이었다. 실제 `sourceKind`에 맞는 기존 계획 형태로 고쳤고, product schema나 타입/계약 검사는 완화하지 않았다. 초기 실패와 중간 로그는 검사 저장소에 보존했다.

## 실제 검사 상태

전체 Release solution build는 경고/오류 0건이다. 공개 입력/out 이름 변경의 실제 API 저장 실패·재시도·cold·compiler Confirm, Blueprint 복사/Confirm/소유 본문 재편집, 부모/비소유/문맥 위조·stale node·실제 부모 파일 변경 차단을 확인했다. 기존 상속 body node 소유권 회귀 2건도 통과했다. 최종 화면·checkout·패키지 결과와 각 명령의 근거는 이 단위 검증을 마친 뒤 아래에 추가한다.

일반 원본 C# 자동 재작성, 등록 부모 계약 불일치 허용, 외부 쓰기 권한, 실제 계정/추론·사용자 프로젝트 실행은 포함하지 않는다. 고정 7행 전체와 8·9행은 위 범위 문서의 잔여로 유지한다.


## 집중 화면 검증 완료

격리 fixture의 집중 **42 check**와 기존 보호 회귀 **6 check**가 통과했다([명령별 기록](evidence/v536-information-inherited-contract/focused-checks.json)). 완료된 검사를 반복하여 새 기능 수로 계산하지 않는다. 공개 입력/out 이름의 순수 후보와 실제 API 저장·compiler Confirm, 위조/타입/역할/반환/순서·물리 부모 변경 거절, 기본·독립 창의 불완전 C# 입력/Undo/Redo/취소/cold, 저장 실패·응답/receipt 유실 조회·충돌 및 두 프로젝트의 같은 copy ID 문맥을 포함한다.

Blueprint는 whole-body 부모의 기본·독립 창, 저장 실패/재시도·응답 유실 복구·Review 취소/재검토·명시 Confirm을 확인했다. 추가 code 노드와 반환 writer를 둔 부모 그래프도 독립 창에서 편집·저장·확정했고, 복사본의 다른 노드 원문은 보존됐다. 원래 child의 compiler probe는 실행 없이 통과하며 다른 native 별칭·위조 문맥·stale node는 metadata와 compiler 모두 거절한다. 기존 정상 상속 node owner/독립 선언 빌림 차단 두 회귀도 유지한다.

[C# 복사 편집](evidence/v536-information-inherited-contract/copy-csharp.png), [Blueprint 선택창](evidence/v536-information-inherited-contract/blueprint-picker.png), [독립 창 확정 후](evidence/v536-information-inherited-contract/blueprint-confirmed.png)를 실제 렌더로 확인했다. 기존 제목 드래그/선택 조작을 사용하고 강제 클릭이나 레이아웃 변경을 하지 않았다. HTML/CSS·UI 어댑터·WebBundle과 원본 ZIP의 이전 게시 대비 바이트 불변은 [기록](evidence/v536-information-inherited-contract/layout-source-evidence.json)으로 남겼으며 모든 화면 pixel equality를 주장하지 않는다.
