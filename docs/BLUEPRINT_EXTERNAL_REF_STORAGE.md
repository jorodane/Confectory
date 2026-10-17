# 외부 ref graph와 원본 본문 전환

새 `sync-acyclic-ref-v1` / `feature-blueprint-source-v7` profile은 외부 함수의 ref 매개변수를 실제 호출자 저장소로 유지한다. 기존 v1~v6 profile의 생성 의미와 소스 해시는 바꾸지 않는다. 원본 graph는 조회·cold 복원으로 전환하지 않으며 명시적 profile/외부 계약 검토를 거친다.

## 직접 전달과 독립 노드

일반 코드/호출 노드의 ref 입력은 기존 입력·로컬·선행 결과 슬롯을 직접 참조한다. 일반 노드 out 결과는 계속 독립 결과 슬롯이다. `forwardCallerStorage: true`인 코드/호출 노드는 현재 함수의 전체 인수 계약을 타입·역할·순서·반환 타입으로 일치시키고, 모든 값/ref 입력을 현재 함수의 같은 위치 입력에 직접 연결해야 한다. out은 같은 위치의 외부 out 매개변수로 직접 전달한다. 이 필드는 노드 정의 해시에 포함한다.

전체 본문 전환의 `implementationContext` 노드에 ref/out이 있으면 이 직접 전달 규칙을 필수로 적용한다. 원래 public Invoke 본문·매개변수 이름·calls/this·직접 재귀·scope·원본 경로와 raw CRLF를 유지하고 별도 명시적 인터페이스 진입에서 호출한다. 원래 C# 파일과 선택하지 않은 타깃은 보존한다. 반환값은 별도 구조적 return 할당으로 전달하며 out을 임시 결과에서 호출자에 복사하지 않는다. 노드 out 결과 핀은 호출이 끝난 직후 실제 out 저장소 값을 읽은 스냅샷이다.

상수·변환·다른 입력/로컬로 전체 본문의 전달 연결을 바꾸거나 현재 인터페이스와 ref/out 역할·순서를 다르게 만드는 조합은 `GRAPH_CALLER_STORAGE_BINDING` 또는 `GRAPH_CALLER_STORAGE_CONTRACT`로 거부한다. 구 profile의 명시적 전달 표시는 `GRAPH_CALLER_STORAGE_PROFILE`로 거부한다. 일반 ref 노드에 상수·property·배열 원소를 참조시키는 기존 거부도 유지한다.

## out 기본값과 경로 경고

새 profile은 진입 시 out에 기본값을 쓰지 않는다. C# definite assignment에는 `Unsafe.SkipInit(out parameter)`를 사용하며 호출자 저장소를 초기화하는 어댑터로 사용하지 않는다. 출력별 할당 플래그를 별도로 두고, export 또는 직접 전달 호출이 정상 완료된 경우에만 설정한다. 정상 종료 시 미할당 out에만 기존 타입 기본값을 쓴다. 이미 할당된 out과 별칭인 ref가 나중에 변경되어도 종료에서 옛 값을 다시 복사하거나 기본값으로 덮지 않는다. 예외 종료에는 정상 종료의 기본값 쓰기를 실행하지 않는다.

기존 must/may 경로 분석과 종료선별 출력 누락·구체 미할당 경로 warning은 유지한다. 직접 전달 본문이 정상 완료하면 해당 out은 할당으로 계산한다. 원본 C# 본문이 out을 정상 경로에서 할당하지 않은 오류는 실제 compiler가 계속 거부한다. SkipInit이 원본 public Invoke 본문이나 독립 노드 probe의 out 할당 오류를 숨기지 않는다.

같은 호출자 변수의 ref/ref/out 또는 out/out 전달은 실제 C#의 동일 저장소 공유를 따른다. 여러 출력이 같은 변수로 전달되면 실제 쓰기 순서에 따른 하나의 최종 값을 관찰한다. 서로 다른 저장소를 전달한 결과와 구분하여 실제 실행으로 검증한다.

## 편집과 보호

외부 ref 계약의 새 graph·typed 참조 구현은 직접 전달 노드를 생성한다. 새 본문 전환은 ref 또는 out 계약에 새 profile을 사용한다. 새 out-only typed 참조 구현도 실제 out 전달을 보존하는 v7을 사용한다. 기존 out-only graph와 빈 out-only graph 생성의 v4 의미는 자동 변경하지 않는다. 입력 폼·ref 저장 슬롯 핀·원본 C# 편집은 기존 Apply, 모든 관찰 소스의 CAS, Save, 별도 compiler Review/Confirm을 유지한다. 전환은 구현·graph·독립 본문의 필수 소유 그룹이며 원본 origin 관찰과 cold 변조 거부를 유지한다. 읽기·복원·Save로 AI·Task·Run을 자동 시작하지 않는다.

검증 중인 범위는 소유 .NET 10 실행과 Chromium 편집, 관리 대상 컴파일이다. main·원본 ZIP·Android 설정·실제 계정·유료 모델·사용자 PC와 native/device 경계는 유지한다. 중첩 graph, property/expression·별칭 로컬, enum/복합 타입·임의 실행 출력, split C#·외부 helper, loop/async 등은 후속 범위다.

## 실행 검증

고정한 최종 소스의 엔진·공개 편집 **48/0/0 (817.034초)**, Chromium UI **10/0/0 (755.403초)**, Windows/Android 관리 대상 컴파일 **1/0/0 (180.433초)**를 확인했다. 집중 검사 11/0/0 (168.474초)와 초기 실패 단계는 [단계별 근거](evidence/v480-integration/external-ref-storage.json)에 별도로 보존하며 중복 합산하지 않는다. 일반 Git 체크아웃·리소스 시작은 구현 커밋 후 별도로 확인한다.

실제 실행은 ref/ref/out 같은 caller 변수 `120,40`, 별도 out `80,20,40`, 서로 다른 ref `52,10,16,26`, 합류 뒤 조건부 out/후속 별칭 쓰기 `11,11` 대 `6,0`, 배열 변수 교체 `24,12` 반복, 예외 종료 `expected,7`, out/out 동일 caller `20,20` 대 서로 다른 caller `10,10,20`을 포함한다. 원본과 변환 후의 재귀·scope·다른 타깃 결과, 실제 C# out 미할당 오류 거부도 검사했다. [종료 경고](evidence/v480-integration/external-ref-ends.png)와 [외부 ref 전체 본문·cold 복원](evidence/v480-integration/external-ref-conversion.png)을 보존한다.
