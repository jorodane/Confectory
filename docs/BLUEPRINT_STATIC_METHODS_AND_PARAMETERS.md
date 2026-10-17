# 노드 소유 정적 보조 메서드와 매개변수 계약 편집

일반 C# 코드 노드는 `sync-acyclic-methods-v1`에서 Execute 아래의 정적 보조 메서드를 편집한다. 기존 profile은 읽기만으로 전환하지 않는다. 명시적 전환은 내부 graph까지 함께 적용하며 기존 본문과 연결, 기존 코드 노드 definition hash는 유지한다. 생성기는 `feature-blueprint-source-v11`이다.

## 정적 메서드 경계

노드 파일은 기존 `schema:1`, `node`, `definitionHash`, `source`에 선택적 `helpers` 문자열을 추가한다. 본문과 보조 메서드는 하나의 노드 소유 파일·CAS·Task 원본 해시·검토 단위에 속한다. 보조 메서드가 있을 때 implementation hash는 두 문자열의 정규화된 canonical object를 포함한다. 보조 메서드가 없는 기존 본문 해시는 유지한다.

methods profile의 일반 코드 노드는 보조 메서드가 0개여도 같은 Execute 경계를 유지한다. 빈 영역·주석만 있는 영역·메서드 제거도 이 경계를 바꾸지 않는다. 각 노드의 본문과 메서드는 구현·body 타깃·전체 private 경로로 구별한 private static class에 생성한다. 부모/형제 노드의 지역 변수나 import를 캡처하지 않는다. 인수와 import를 메서드 인수로 명시적으로 전달해야 한다. 생성된 wrapper는 값/ref/out과 동일한 저장소를 그대로 전달한다. 내부 graph의 정적 클래스도 바깥 구현 소스와 각 graph 구현·최상위 본문 검증 해시까지 함께 포함하며 독립 leaf probe는 그 노드의 클래스만 컴파일한다. probe는 실행하지 않는다.

실제 Roslyn 구문 검사에서 본문은 완전한 block이어야 한다. helpers는 본문 또는 식 본문을 가진 static 메서드 선언만 허용한다. 선언 modifier는 static과 선택적 public/private를 지원한다. 필드·생성자·초기화자·프로퍼티·중첩 타입·특성·extern/partial 메서드와 외곽 선언 탈출, 생성기 예약 이름, helpers의 전처리 지시문은 거부한다. 타입·반환·상위 문맥 캡처는 실제 C# compiler가 검증한다. 필드와 공유 상태를 지원하는 새 수명 정책은 추가하지 않는다.

기존 `calls`, `this`, 재귀 `Invoke`, 별칭·scope와 CRLF를 유지하는 전체 본문 전환 노드는 원래 구현 문맥을 유지한다. 이 노드에는 Execute 밖 helpers 및 노드 자체 매개변수 편집을 허용하지 않는다. 기존 본문 내부 local helper는 유지하며, 외부 계약 변경은 기존 계약 검토 경로를 사용한다. 일반 정적 노드로 문맥을 자동 변환하지 않는다.

## typed 매개변수와 연결 대응

‘매개변수 계약 편집’은 이름·CELEM 타입·값/ref/out·순서를 편집하는 별도 계약 화면이다. 현재 반환 타입과 외곽 선언은 보호한다. 자유로운 C# 선언 문자열을 원본에 넣지 않는다. 전체 본문 문맥 및 caller-storage 전달 노드는 외부 계약 검토 경로를 따른다.

모든 기존 매개변수는 명시적인 old-name → new-name 또는 삭제 대응을 가진다. 이름을 바꿨는데 기존 대응이 유효하지 않으면 사용자가 새 이름을 선택해야 하며 위치로 추측하지 않는다. remap은 정확한 타입·전달 방식이 같은 매개변수만 연결한다. 새 입력은 미연결 상태이며 기존 입력 연결과 out 출력 사용처·종료식·별칭 로컬은 명시적 대응에 따라 갱신한다. 연결된 out을 삭제하려면 모든 사용을 먼저 해제해야 한다. 타입/전달 방식을 바꾸려면 기존 연결을 명시적으로 해제하고 새 typed 매개변수를 연결한다.

공개 `blueprint` API의 `parameters` 동작은 `id`, 현재 `basis`, `node`, typed 배열 문자열 `argsJson`, 모든 이전 이름의 대응 object 문자열 `remapJson`을 받는다. `source` 동작의 선택적 `helpers`는 같은 노드 파일에 본문과 함께 적용한다. 빈 helpers를 처음 전송한 것만으로 기존 본문 파일에 불필요한 필드를 추가하지 않는다.

화면에서 변경 계약과 remap을 검토·확인한 뒤 공유 초안에 적용한다. 이 단계는 실제 compiler Review/Confirm을 대체하지 않는다. graph의 계약 변경은 기존 본문이나 helpers를 다시 쓰거나 새 definition hash로 자동 승인하지 않는다. 본문은 stale 상태가 되며 사용자가 새 계약으로 수정·재적용해야 한다. 이후 graph와 restamped leaf를 함께 compiler Review/Confirm한다. 이전 graph basis와 Task definition은 변경 후 사용할 수 없다.

## 편집·복원과 검증

보호된 전체 C# 보기는 고정 class/Execute/괄호와 각각 편집 가능한 본문·helpers를 보여 준다. 영역을 넘는 삭제·입력과 외곽 변경을 거부한다. Tab·Undo/Redo·Ctrl+S와 raw 본문/메서드 편집은 같은 private 입력을 다룬다. 두 영역은 한 노드 원본에 원자적으로 적용한다. private 입력·계약 편집·보기는 cold 복원하되 server basis와 Undo 권한은 복원하지 않는다. 현재 원본 읽기와 명시적 기준 재검토가 필요하다.

Task 권한은 기존의 네 가지 노드 전용 도구 그대로이며 graph·다른 노드·계약 편집 권한을 넓히지 않는다. helper 변경도 전체 leaf 원본 해시로 fencing한다. 읽기/검토/독립 컴파일이 사용자 코드를 실행하지 않는다. 실제 실행 결과·거부·복원·compiler Confirm·일반 Git 리소스 시작 검사는 [검증 기록](evidence/v480-node-methods/validation.json)에 기록한다.

enum 실행의 미정의 반환값 처리와 정수 계산식 overflow는 답변 대기 상태 그대로다. 이 기능은 해당 의미를 선택하지 않으며 전체 v480 완료를 주장하지 않는다. 전체 상태는 [완료·미완료 표](EDITOR_V480_STATUS.md)를 따른다.


<!-- node-methods-current-validation -->
최종 고정 제품·테스트 원본 **25개**에서 엔진/공개 편집 검사는 서로 겹치지 않는 세 묶음 **27/1/0 + 26/1/0 + 26/1/0**였다. 같은 소스·기존 제한 시간으로 실패한 3개만 순차 단독 재검증해 3/0/0, 302.771초로 통과했다. 소스나 제한 시간은 바꾸지 않았다. **서로 다른 82개 메서드가 각각 통과**했으며 단일 82/0 실행으로 표시하지 않는다. 실제 Chromium은 **6/0/0 + 5/0/0**로 서로 다른 **11건**이 통과했다. 관리 프로필 컴파일은 **1/0/0, 375.74초**로 통과했다. 앞선 중첩 단계와 중단한 회귀는 최종 수에 더하지 않는다.

실제 [정적 메서드 편집](evidence/v480-node-methods/code.png), [typed 계약·명시적 대응 검토](evidence/v480-node-methods/parameters.png), [고정 원본·단계별 로그·전체 결과](evidence/v480-node-methods/validation.json)를 보존한다. 전체 v480 완료나 실제 Windows/Android 장치 실행을 주장하지 않는다.

일반 Git checkout·리소스 시작 검사는 구현 커밋 고정 후 별도로 기록한다.
<!-- /node-methods-current-validation -->
