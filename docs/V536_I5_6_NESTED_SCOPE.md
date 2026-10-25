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

## 정확한 잔여

이번 범위로 **5행 전체를 완료 처리하지 않는다**.

1. private `forwardCallerStorage` 호출의 함수 서명을 변경하면서 부모 graph 노드의 private 서명·호출 저장소/출력 계약까지 함께 바꾸는 조작은 아직 명시 후보에 연결하지 않았다. 고정 private 서명 안에서 본문/import를 다시 검증하는 것과 구별한다. 부모 계약을 추측하여 바꾸지 않는다.
2. private `branch`/`switch` C# 노드의 본문을 함수 상세창의 같은 owner 거래에 넣는 어댑터는 아직 없다. 현재 scoped Script 선택은 일반 `next` 코드다. 기존 별도 Blueprint 편집 가능 여부를 이 owner 결합 저장의 완료로 세지 않는다.
3. private graph의 copy provenance·등록/상속 callable의 receipt는 고정 **7행**의 별도 범위다. 이번 단위에서 외부/부모/donor를 수정할 권한을 추가하지 않았다.

7행은 소유 복사본·등록 callable receipt, 8행은 여러 함수 계약과 공유 caller의 합성 후보, 9행은 정보/참조/외부 타입 및 표시명/native 식별자 경계다. 이 목록을 새로운 조합으로 늘리지 않는다. I6/B2와 A4~A6/M4/M11/M12, Helper 작업 도구는 기존 후속이다. 실제 Windows/WebView2·모바일 기기 실행과 Library 전달은 별도 미검증이다.
