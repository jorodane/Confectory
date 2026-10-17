# Blueprint ref 노드 입력과 실제 저장 슬롯

v480의 C# 계약은 입력 필드를 `value/ref`, 출력 필드를 `out`으로 구분한다. 이번 단위는 일반 CELEM C# 함수·typed import의 ref와, 기존 graph 저장 슬롯을 참조하는 코드/호출 노드의 ref 입력이다. 외부 ref 인터페이스를 가진 graph와 그 C# 본문 전환은 아직 지원하지 않는다. 전체 ref 지원이나 v480 전체 완료로 표시하지 않는다.

## C# 계약과 실행

CELEM의 함수·구현·module require·import는 `ref T`를 타입·역할·순서 계약에 포함한다. JSON 인수는 `"mode":"ref"`를 보존하며 값 입력의 mode 생략과 기존 out 직렬화/계약 해시는 유지한다. 생성 인터페이스·구현·최종 바인딩·내부 호출·독립 노드 probe 모두 실제 C# ref 선언과 호출을 사용한다. 변경된 값을 나중에 복사해 되쓰는 어댑터를 만들지 않는다.

```text
function Example::Alias (ref int first, ref int second, out int audit) -> int {}
import Example::Alias as Alias (ref int, ref int, out int) -> int;
```

일반 C# 구현은 같은 호출자 변수를 두 ref에, 또는 ref와 out에 함께 전달할 때의 CLR 별칭을 그대로 보존한다. 예를 들어 `a=10; b+=a; audit=a+b; return a+b+audit;`에서 두 ref가 같은 변수이고 out만 다르면 결과/변수/audit는 `80,20,40`, 세 인자가 모두 같은 변수면 `120,40`이다. 이 차이를 별도 실제 실행으로 확인한다.

## ref 노드 profile

새 profile은 `sync-acyclic-ref-nodes-v1`, 생성기는 `feature-blueprint-source-v6`다. 기존 명시적 locals/out/암묵적 종료의 동기·비순환 실행과 각 종료선의 누락 warning을 포함한다. 기존 profile의 노드는 ref 입력을 조용히 받아들이지 않는다. 명시적 forward upgrade와 별도 compiler Review/Confirm을 거치며 조회·cold 복원으로 올리지 않는다.

ref 입력은 기존 값 binding에서 다음 저장 슬롯만 선택한다.

- `{"local":"cell"}`: 이 호출에서 초기화한 정확한 타입의 로컬 슬롯.
- `{"input":"n"}`: 현재 함수의 값 매개변수 슬롯. ref 노드가 이를 바꿔도 함수 호출자가 값으로 전달한 원래 변수에 복사해 되쓰지 않는다.
- `{"node":"source","output":"return"}` 또는 이름 있는 결과: 모든 경로에서 선행한 노드의 결과 슬롯. 기존 dominance와 타입 검사를 유지한다.

상수·변환식·property·배열 원소 표현식을 ref 대상으로 허용하지 않는다. 새 ref 변수·별도 초기값·공유 상태·동시성·새 수명 규칙을 추정하지 않는다. 기존 호출별 슬롯을 실제 lvalue로 전달한다. ref는 입력이며 자동으로 새 출력 필드를 만들지 않는다. out 결과는 계속 노드별 새 슬롯이고 기능 출력은 기존 export로 내보낸다.

같은 binding을 두 ref 입력에 사용하면 생성 C#도 같은 변수에 `ref`를 두 번 전달한다. 첫 인자의 쓰기가 두 번째 인자에게 즉시 보인다. 서로 다른 binding은 서로 다른 슬롯이다. 일반 노드의 값 복사 결과는 로컬을 나중에 설정해도 그대로지만, 그 노드 결과 슬롯 자체를 ref로 명시적으로 전달하면 이후 읽기는 수정된 슬롯을 관찰한다.

배열의 요소를 함께 보는 것과 배열 변수 자체를 참조하는 것도 구분한다. 두 ref 배열 입력이 같은 슬롯이면 첫 인자에서 배열을 새 배열로 바꾼 뒤 두 번째 인자는 새 배열을 본다. 이를 `40,20`의 반복 호출로 확인하며, 기존 값 배열 공유 검사를 ref 지원의 증거로 대신하지 않는다.

## 편집과 호환성

입출력 폼의 ref 역할, module/import의 `ref T`, 새 코드 노드의 `[ref 또는 out] 타입 이름`, C# 헤더와 호출 미리보기·연결 검사에 역할을 보존한다. ref 입력 핀은 저장 슬롯 선택임을 표시하고 기존 입력·로컬·앞선 결과를 준비한다. 선택은 미적용 입력이며 기존 Apply·모든 소유 소스 CAS·Save·Review·Confirm을 따른다. 상수를 적용하면 실행 경로에서 `GRAPH_REF_STORAGE`로 거부하며 compiler 성공으로 표시하지 않는다.

일반 C# ref 함수는 typed 호출의 대상이 될 수 있다. 소유/등록 함수 선택과 현재 계약 미리보기, import+graph의 소유 그룹, 명시적 scope/provider 해석, peer 변경 거부와 cold basis 거부를 유지한다. source-ready는 실제 C# compiler 증거를 대신하지 않으며 독립 probe는 노드를 실행하지 않는다. 열기·복원·폼 입력·Save가 AI·Task·프로젝트 Run을 자동 시작하지 않는다.

새 외부 ref 함수 계약의 graph 생성 버튼은 현재 미지원 경계를 설명하고, 코드/호출 계약 편집은 유지한다. 원래 ref C# 본문 전환 준비도 명시적으로 거부하고 소스와 초안을 보존한다. 새 profile의 root 함수에 ref가 있으면 `GRAPH_REF_FEATURE_UNSUPPORTED`다. 이 경계를 고치지 않은 채 변환을 성공으로 표시하지 않는다.

특히 호출자의 ref와 out이 같은 저장소를 공유하면 이전 profile의 진입 시 out 기본값 대입과 out 임시 복사/내보내기는 원래 C# 동작을 바꿀 수 있다. 이를 보존하는 외부 graph 인터페이스·전체 본문 변환은 후속 설계와 실제 별칭 검증이 필요하다. 기존 ref 없는 전체 본문 전환과 원본 관찰·타깃·calls/this·재귀·인수 이름·CRLF·원본 보호는 그대로 유지한다.

## 검증과 남은 전체 범위

실제 .NET 10 검증은 일반 C#의 두 ref/세 ref-out 동일 변수, graph의 같은 로컬 즉시 공유와 분기 out 누락, 값 입력의 `80,20,5`(호출자 5 유지), 앞선 결과 슬롯의 `20,40`, 배열 참조 슬롯 교체 `40,20` 반복, 명시적 객체 scope와 독립 probe를 포함한다. 공개 API는 profile gate·현재 typed ref 미리보기·peer CAS·동일 binding의 cold 복원·별도 import+graph compiler 확정 후 `0,0 → 80,20`, 지원하지 않는 본문 전환의 원본/초안 무변경을 확인한다. 양쪽 embedded 메타데이터 편집기도 ref를 보존한다. [단계별 검증](evidence/v480-integration/ref-node-storage.json).

최종 고정 소스에서 엔진·공개 편집 회귀 **31/0/0 (439.590초)**, 실제 Chromium UI **9/0/0 (695.213초)**, Windows/Android 관리 대상 컴파일 **1/0/0 (155.168초)**을 확인했다. 이전 집중 검사 **8/0/0 (214.157초)** 등은 별도 중복 단계이며 합산하지 않는다. [같은 저장 슬롯의 ref 입력](evidence/v480-integration/ref-node-bindings.png)과 [명시적 compiler 확정 후 화면](evidence/v480-integration/ref-node-published.png)을 보존한다. 일반 Git 체크아웃·리소스 시작은 구현 커밋 후 별도로 확인한다.

남은 범위는 외부 ref graph 인터페이스/본문 전환의 caller alias 보존, 중첩 graph 소유 ID·파일·버전·호출/복귀, property/expression/출력 별칭 로컬, enum/복합 타입·임의 실행 출력, 분리된 C# 영역·외부 helper, loop/async, 물리 삭제·일괄 타깃 이관·포털/픽셀 일치·별도 전체 v424 서비스 회귀다. 검사 경계는 소유 Linux/.NET 10/Chromium 및 관리 대상 컴파일이며 native/device·실제 계정·유료 모델·사용자 PC 설치 검증이 아니다. main·원본 ZIP·Android 설정은 보존한다.
