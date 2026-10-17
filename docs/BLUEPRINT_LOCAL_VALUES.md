# Blueprint 명시적 로컬 값과 설정

v480의 literal 로컬 값과 `set-local` 실행 계획을 현재 동기·비순환 graph에 연결한다. 이번 단위는 명시적 상수 초기값이 있는 함수 로컬 저장 공간과 구조적 설정 노드다. property·expression·노드 출력의 별칭 선언, ref, 중첩 graph는 별도 범위다. prototype 저장 데이터를 실행하거나 읽기만으로 현재 graph에 이관하지 않는다.

## 원본과 실행 계약

새 profile은 `sync-acyclic-locals-v1`, 생성기는 `feature-blueprint-source-v5`다. 이전 세 profile과 생성기, 외부 입출력 ABI·계약 해시·노드 본문 계약은 유지한다. profile 전환은 기존 graph의 명시적 forward upgrade이며 조회·cold 복원으로 수행하지 않는다. 기능/참조 생성과 기존 C# 본문 전환도 기존 profile 선택을 유지하고, 사용자가 필요할 때 별도로 올린다.

```json
{"locals":[{"id":"counter","name":"카운터","type":"long","initial":{"constant":5}}]}
```

로컬은 graph의 안정적인 ID로 참조한다. 이름은 표시용이며 C# 식별자로 삽입하지 않는다. 타입은 기존 primitive와 배열이며, 초기값은 그 타입에 맞는 명시적 constant다. 임의 참조·property·expression 초기화와 타입 추론, 암묵적 미초기화 기본값을 추가하지 않는다. 선언은 64개까지이며 기존 source/file/전체 읽기·쓰기 예산과 새 profile의 256개 노드·64개 기능 인수 제한을 적용한다.

각 Invoke는 선언한 초기값으로 새 로컬 슬롯을 만든다. 배열 리터럴도 매 호출 새 배열이며 같은 호출의 여러 노드가 읽으면 같은 배열 참조를 전달한다. 배열을 반환하거나 외부 C#에 전달하면 관리 참조의 수명은 일반 C# 규칙을 따른다. 이 배열 공유 검증을 ref 매개변수 지원으로 확대하지 않는다. 초기화는 실행 entry 이전에 한 번 수행하며, graph 실행은 기존 next/bool 포트와 DAG 순서를 따른다.

`{"local":"counter"}`는 읽는 시점의 슬롯 값을 정확한 타입으로 전달한다. 앞선 코드 노드의 반환 슬롯은 여전히 그 호출에서 받은 값이며 로컬의 이후 대입으로 다시 계산되지 않는다. 기존 입력·노드 결과·상수 binding 및 dominance 검사는 유지한다. 로컬은 모두 명시적으로 초기화되므로 entry에서도 읽을 수 있다.

```json
{"id":"set_counter","kind":"set","control":"next","intent":"Set counter","local":"counter","signature":{"args":[{"name":"value","type":"long"}],"return":"void"},"arguments":{"value":{"input":"n"}}}
```

set은 정확한 타입의 `value`를 실행 시점에 해당 슬롯에 대입한다. 독립 C# 파일, 새 함수 계약, 코드 본문이나 Task를 만들지 않는다. 구조적 노드만 추가하며 값과 실행선을 별도로 연결한다. 로컬 설정이 기능 out 출력의 할당 완료를 뜻하지 않는다. 기능 출력은 기존 export를 통해 내보내며 각 종료선의 return/out 누락·must/may·경로 예시와 타입 기본값 warning을 유지한다. loop·async·동시 작업·호출 간 공유 상태의 새 의미는 추가하지 않는다.

이름·초기값 변경은 ID와 노드 C# 계약을 유지한다. 편집 폼에서 기존 선언의 타입은 고정하며 다른 타입은 새 로컬로 명시적으로 만든다. 삭제는 모든 set 대상과 값 binding을 먼저 제거한 로컬에만 허용하고 실제 파일을 삭제하지 않는다. 새로운 profile의 생성 변수에 대한 미사용 경고만 생성 선언 부분에서 억제한다. 사용자의 노드 C# 경고는 그대로 검사하며, `_`라는 사용자 매개변수에 시스템 discard를 대입하지 않는다.

## 편집·저장·검증

별도 ‘로컬 값 · 설정’ 창에서 profile 전환, 선언/이름/초기값 편집, 설정 노드 생성과 참조 없는 선언 삭제를 수행한다. 입력 핀의 로컬 값 선택은 JSON binding을 미적용 입력에 준비하며 Apply 전에는 graph를 바꾸지 않는다. 기존 노드 생성·제거와 export 편집은 유지한다. C# textarea와 함수 원본·타깃·기존 본문 전환 원본은 수정하지 않는다.

공개 Blueprint API의 `createLocal/updateLocal/removeLocal/createSet`은 관찰한 구현·계약·graph·노드 원본 전체의 리비전과 raw 내용 CAS를 기존 EditBatch에서 확인한다. 잘못된 초기값, 오래된 peer 기준, 사용 중인 로컬 삭제는 소스를 바꾸지 않고 거부한다. 새 노드는 값과 실행 연결을 명시적으로 적용한 뒤 compiler Review/Confirm을 따른다. 게시된 기존 graph에서 이 변경은 graph 파일 하나만 확정할 수 있다.

초기값은 UI에 `initialJson` 문자열로 보내며 long의 큰 정수를 JavaScript Number로 왕복하지 않는다. private 폼 입력·배치는 저장하지만 basis·승인·실행 권한은 저장하지 않는다. 재시작 후 현재 graph를 읽고 기준을 다시 검토해야 미적용 초기값을 적용할 수 있다. 열기·복원·값 선택·Save는 AI·Task·프로젝트 Run을 자동 시작하지 않는다.

실제 .NET 10 검사는 분기에서의 `2,2 / 5,0 / 3,3 / 5,0` 초기화·경고, 설정 전 코드 결과와 이후 슬롯의 `1,2`, 같은 호출의 배열 공유와 다음 호출 초기화 `2,1 / 2,1`, 사용자 `_` 매개변수와 생성 선언의 분리를 확인한다. 공개 편집 API는 명시적 profile, peer CAS, 큰 정수·잘못된 초기값·삭제 보호, cold basis 거부와 graph-only compiler Confirm 뒤 실제 실행 `2,2 → 5,5`를 검사한다. Chromium에서는 실제 폼·핀 선택·설정 순서·정확한 초기값·cold 재검토·원본 보존·별도 compiler 확정을 검사한다. [단계별 검증 근거](evidence/v480-integration/local-values.json).

## 남은 전체 범위

v480 전체 완료가 아니다. ref의 실제 별칭·호출 의미, 중첩 graph의 소유 ID/파일·버전·호출/복귀, property·expression·출력 별칭 로컬, enum/복합 타입과 임의 실행 출력, 분리된 C# 영역·외부 helper, loop/async, 물리 파일 삭제·일괄 타깃 이관·포털·픽셀 일치와 전체 v424 서비스/실행 회귀는 별도로 남아 있다. 특히 ref/out이 같은 호출자 변수를 공유하는 C#에서는 out 복사본이나 진입 시 기본값 쓰기가 관찰 가능한 동작을 바꿀 수 있으므로 후속 ref 구현·본문 전환에서 실제 별칭 공유를 검증해야 한다.

검사는 Linux/.NET 10/Chromium 소유 fixture와 Windows/Android 관리 대상 컴파일 범위다. native/device·실제 계정·유료 모델·사용자 PC 설치 검증이 아니다. main, 원본 ZIP과 Android 설정은 보존한다.


최종 회귀는 엔진·공개 편집 **25/0/0 (302.587초)**, 실제 브라우저 **7/0/0 (475.919초)**, Windows/Android 관리 컴파일 **1/0/0 (138.695초)**로 각각 통과했다. 이후 제품을 유지하고 브라우저 측 창/출력 경계 측정만 추가한 검사는 **1/0/0 (65.682초)**로 통과했다. 출력 영역은 실제 창 안의 165px 영역에 있었으며 캡처에서 의심한 클리핑은 재현되지 않았다. [로컬 폼](evidence/v480-integration/local-values-form.png), [확정·복원](evidence/v480-integration/local-values-published.png).

첫 핵심 3건과 공개 API를 더한 4건, `_` 매개변수 충돌을 고친 뒤의 집중 6건은 중간 단계 기록이며 최종 숫자와 합산하지 않는다. 실제 생성 discard 충돌의 실패와 수정은 새 profile에만 적용했다. 첫 시험 코드의 var 다중 선언 컴파일 오류와 불충분했던 editor 상대 경계 측정도 근거에 구분한다.


구현 `f81a0a84c7f653bdbe5a0741aba0603bae13c44b`의 일반 Git 체크아웃도 **1/0/0 (6.294초)**로 통과했다. 기존 CRLF가 남은 사본과 새 LF 체크아웃에서 33개 리소스·실제 Home 시작·내용/인코딩/BOM/바이너리/예산 변조 거부·원본 바이트 보존을 확인했다. 별도 증거 커밋은 제품/테스트 소스 15개의 해시를 유지한다.
