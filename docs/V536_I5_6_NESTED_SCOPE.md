# I5-6 고정 5행: 중첩/private graph의 명시적 계약 대응

기준은 저장소 `196c605`의 v536 원본과 기존 `BlueprintTree`/private graph 계약이다. 이번 단위는 직접 소유한 함수 하나의 계약을 편집할 때 그 함수를 호출하는 **직접 소유 private graph**의 값·출력 연결, 직접 작성한 C#·후처리를 함께 검증하는 범위다. 원본 레이아웃·CSS·권한·Review/Confirm은 바꾸지 않는다.

| 고정 조작 | 연결한 범위 |
|---|---|
| 정보 상세창에서 함수 계약을 바꾸고 내부 호출의 입력/출력을 명시 선택 | 기존 호출 갱신창에서 부모 경로를 구분한다. `left/invoke`와 `right/deep/invoke`는 다른 호출이며 같은 leaf 이름으로 합치지 않는다. 바인딩은 해당 frame의 인자·local source·exit만 바꾼다. |
| 내부의 일반 C# 노드가 변경한 함수를 import하여 호출 | 기존 구현 선택/Script 창에서 qualified source와 원래 고정 매개변수·본문 경계와 private ref 전달을 유지하며 사용자가 입력한 본문만 후보에 포함한다. 전체 조립 C#의 실제 컴파일로 import와 타입을 검증한다. 부모/형제의 계약과 C# 원문은 자동 재작성하지 않는다. |
| 내부 serial After/enum 후처리를 현재 공개 출력에 맞게 편집 | qualified wrapper receipt와 현재 함수 계약에 사용자의 source/helpers를 결부한다. 기존 실행 포트·enum 식별자는 유지한다. 공개는 호출 후 SourceContext 읽기이며 외부 공유 권한이 아니다. |
| 함수 루트 입력의 교체가 내부 graph 노드 인자로 전달되는 경우 | 해당 부모 노드 인자만 명시적으로 대응한다. 자식의 고유 매개변수·exits·C#은 별도 범위로 보존한다. |
| 기존 내부 흐름/상위·breadcrumb 탐색과 창별 입력 복원 | 기존 v536 탐색 경로로 qualified source를 연다. 다른 정보 창 및 프로젝트의 미적용 입력, 코드 취소·재시작 보관, Undo/Redo를 유지한다. |

원래 graph 전체 해시·qualified record ID/정의 해시·소유 source 경로·현재 계약을 검증한다. 모든 graph/선언/import/record/source는 기존 한 후보와 CAS에서 전체 성공 또는 전체 미적용이다. 낡은 증거·잘못된 경로·빠진 caller·컴파일 오류는 입력을 유지한 채 거절한다. 저장 성공과 최종 원본 반영은 별개이며 실제 compiler Review와 명시 Confirm을 통과해야 한다.

## 부모 private 계약과 실행 포트 연결

직접 소유 private `forwardCallerStorage`의 부모 계약·바깥 인자·각 내부 호출 출력과 부모 출력을 기존 호출 대응창에서 함께 선택한다. 깊이 2의 전달 계층과 추가 code/graph 노드·수식·live alias·직결이 아닌 반환도 각 frame의 의미 바인딩으로 보존한다. 내부 호출 출력은 부모 출력과 별도 선택이며 어느 쪽도 자동 추측하지 않는다. 계산에 남는 입력은 사용자가 선택한 바깥 저장소와 같은 타입·저장소 역할의 유일한 현재 입력에 대응해야 한다. 대응이 빠지거나 모호하면 후보 전체를 거절한다.

부모의 C# 매개변수·본문은 자동 재작성하지 않는다. 고정 native 경계를 가진 private `next`/`branch`/`switch`의 수동 본문·보조 함수를 같은 owner 후보에 넣고 조립 C#으로 검증한다. switch의 원래 실행 enum과 포트 식별자는 보존한다. 별도 Blueprint Script의 private enum 이름·값·순서와 본문·보조 함수 저장도 원래 private 경로·소스/정의 해시 및 물리 root의 한 checkpoint/CAS에 결부한다. 응답 유실 뒤 receipt 조회에는 저장 전 private 바인딩을 유지한다. enum의 공개 여부나 외부 접근 권한을 추가하지 않는다.

## 여러 forwarded 자식과 고정 5행 완료 경계

같은 함수의 forwarded 자식이 여러 개 있으면 공통 부모별로 전달 계층을 합성한다. 부모 계약·바깥 인자는 한 번만 구성하고 각 자식의 출력 대응은 따로 선택한다. 깊이가 다른 형제 graph/call, 추가 code·계산/별칭·후처리와 기존 실행 순서를 보존한다. 내부 바인딩은 frame마다 한 번만 대응하고, 모든 부모 인자를 구성한 뒤 바깥 소비자 출력 대응을 적용한다. 부모 A의 출력이 부모 B의 입력일 때 B가 이전 연결을 되살리지 않는다.

마지막 자식의 선택 누락·낡은 증거·잘못된 타입·현재 계약 불일치도 전체 후보를 거절한다. 정의·import·source·wrapper·모든 caller는 기존 한 후보/CAS로 저장하며 물리 원본 반영은 Review/Confirm을 별도로 거친다. 기존 C#은 자동 재작성하지 않는다. [여러 자식 수용 검증](VALIDATION_V536_INFORMATION_MULTI_FORWARD.md)에 정상/실패·Undo·취소·충돌·응답 유실·재시작·기본/독립 창·Confirm 결과를 기록한다.

따라서 고정 **5행의 직접 소유 함수 하나·현재 지원 native 타입/명시 대응이라는 지원 경계는 마감한다**. 없거나 모호한 계산 입력/저장소, 사용 중인 출력의 무대응 삭제, 다른 callee의 계약 변경은 추측하지 않고 전체 거절한다. 이 안전 조건을 새로운 미구현 조합으로 계속 늘리지 않는다.

고정 잔여는 다음 **7~9행**이다.

1. 7행: private graph의 copy provenance·등록/상속 callable 읽기 receipt와 소유 copy 후보를 결합한다. donor·부모·외부 팩은 수정하지 않는다.
2. 8행: 함수 둘 이상의 새 계약을 먼저 구성하고 공유 caller와 부모 저장소 후보를 합성한다. 다른 callee의 forwarded 형제가 있는데 그 계약 후보가 없으면 이번 5행은 변경을 거절한다.
3. 9행: 정보/참조/외부 핀 타입과 표시명/native 식별자 경계를 연결한다.

I5-6 전체·v536 전체 완료가 아니다. I6/B2와 A4~A6/M4/M11/M12, Helper 실제 작업 도구는 기존 별도 후속이다. 실제 Windows/WebView2·모바일 기기 실행과 Library 전달은 미검증이다.
