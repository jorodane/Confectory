# v536 공유 호출자의 일반 out 이름 결합

고정 8행의 다음 지원 단위는 같은 정보가 직접 소유한 함수 2~8개의 out 이름 변경이다. 같은 위치·타입·값/out 역할·핀 수와 반환을 유지한다. callee는 import 없는 code/export leaf이고 shared caller는 선택한 함수의 call/export만 사용한다. 값 입력 이름을 함께 편집해도 동일한 원래 핀 대응을 유지해야 한다. scalar 타입 변경과 out 계약을 한 그룹에서 섞거나 추가 caller 선택·C# 편집·중첩·copy를 섞지는 않는다. 7행 독립 복제 정책은 답변 대기이며 새 ID/함수/호출 대상은 만들지 않는다.

기존 원본 상세창의 안정된 핀 대응을 각 원래 스냅샷에서 먼저 검증한다. 각 closure를 내부 overlay에 순차 준비하고 공유 소스는 한 번의 원래 hash로 제출한다. 이전 closure가 바꾼 출력 이름이 다른 call의 값 인자나 최종 exit에 사용되면 같은 call ID/출력 핀의 새 이름으로 전파된다. 이는 명시된 원래 핀의 이름 변경이며 다른 출력으로 추측해 연결하는 동작이 아니다. 코드 매개변수·C# 본문·writer ID·제어 경로·값은 보존하고 기존 후보/CAS·receipt·Review/Confirm을 사용한다. 중간 결과는 live 상태나 파일에 쓰지 않는다.

## 검증 상태

격리 fixture는 같은 count 이름을 가진 두 out 함수를 직렬로 호출한다. A.count가 B.amount에 연결되고 B.count가 caller 반환으로 연결된다. A.leftCount/B.rightCount 편집 뒤 두 연결과 공개 출력 이름이 함께 바뀌되, 각 code의 count 매개변수·본문·설명 속 count 문자열과 정확한 64비트 값은 유지한다. 편집 역순도 같은 결과여야 한다. 집중·checkout·패키지 결과와 근거는 이 단위 마감 시 기록한다.

## 남은 경계

출력 타입·추가/삭제·역할·반환과 입력 수/순서/ref 변경, C#·혼합 target·중첩/private/whole/postCall, copy/상속/등록 및 owner 속성이 섞인 여러 함수 후보는 별도 미완료다. 기존 source/body를 자동 재작성하지 않는다. 원본 v536 UI/레이아웃·권한과 단일 함수 지원은 유지한다. 9행 named 타입·표시명, I6/B2 및 A4~A6/M4/M11/M12도 별도 후속이다.

검사는 Linux managed 엔진과 Chromium 및 Windows 교차 패키징으로 진행한다. 공간 피크는 사전에 확인하고 새 기존 파일을 삭제하지 않는다. RAM fixture/패키지는 같은 exec 안에서만 사용하고 로그·선택한 화면·해시를 보존한다. RAM의 새 패키지를 영구 보관본이나 Library 전달로 표시하지 않는다. 실제 Windows apphost/WebView2·모바일 기기 실행은 미검증이다.
