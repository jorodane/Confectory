# Blueprint 이름 있는 out 출력

v480의 `blueprintCSharpContract`는 일반 입력, 참조 입력, 출력 필드를 구분하며 출력 필드를 C# `out` 매개변수로 표현한다. 이번 단위는 이름 있는 `out` 출력을 실제 CELEM·compiler·편집 경로에 연결한다. `ref`의 공유 참조/별칭 의미와 중첩 graph는 포함하지 않는다. v480 ZIP의 스크립트나 저장 데이터를 제품 원본으로 실행·이관하지 않았다.

## 계약과 실행

```text
function Example::Split (int n, out int count, out bool ready) -> int {}
implementation Example::SplitBody for Example::Split (int input, out int amount, out bool flag) -> int { ... }
import Example::Split as Split (int, out int, out bool) -> int;
require Example::Split (int, out int, out bool) -> int;
```

입력과 out의 타입·역할·순서는 구현, import, module 요구 계약과 참조 함수의 호환성에 포함한다. 이름이 다른 함수의 참조는 같은 순서의 필드를 연결하며 원본 이름을 다시 쓰지 않는다. JSON 시그니처는 해당 인수에만 `"mode":"out"`을 기록한다. 기존 값 입력에는 mode 필드를 추가하지 않아 예전 계약 해시·캐시 직렬화를 유지한다. C#의 호출과 인터페이스·구현·문맥 보존 멤버에 `out`을 전달한다. 지원 타입은 기존 primitive와 배열 그대로다.

새 profile은 `sync-acyclic-implicit-out-v1`, 생성기는 `feature-blueprint-source-v4`다. 기존 `sync-acyclic-v1`/v2와 `sync-acyclic-implicit-v1`/v3는 유지하며 out 계약을 조용히 받아들이지 않는다. 새 profile은 기능 매개변수 64개, graph 노드 256개까지 지원하며 기존 편집 소스 읽기/쓰기 예산도 적용한다.

기능의 출력 목록은 기존 비void `return`과 선언한 out 필드다. out은 기능/노드의 입력 핀과 인수 binding에 나타나지 않는다. 노드 결과는 `{"node":"split","output":"count"}`처럼 고른다. 기존 `{"node":"split"}`는 주 반환값을 가리킨다. 선언하지 않은 출력, 타입 불일치, 실행상 앞서 있지 않은 결과는 계속 오류다. 참조 호출은 선언된 scope/provider를 그대로 사용한다.

각 노드 호출은 독립 결과 슬롯에 out 값을 한 번 받는다. 구조적 `export` 노드는 선언된 출력 이름과 정확한 타입의 `value` binding을 받아 기능의 출력 슬롯에 할당한다. 기능 out 매개변수는 시작 시 C# 타입 기본값으로 초기화되지만 이 초기화는 graph 할당 분석에서 할당 완료로 세지 않는다. 그래프에서 내보내지 않은 값은 수치형 0, bool false, 문자열·배열 null이다. 이것은 이번 구현에서 유지한 정책이며 사용자에게 구체 기본값을 다시 선택받았다는 의미가 아니다.

## 종료별 분석

연결 없는 next/true/false 포트와 빈 시작은 종료다. 각 출력별로 선행 경로의 must(교집합)와 may(합집합) 할당을 계산하고, 종료마다 누락된 출력 이름·타입·기본값·일부 경로 할당 여부를 표시한다. 합류에서 서로 다른 경로가 서로 다른 출력을 할당하면 각 누락 출력마다 별도의 미할당 경로 예시를 제공한다. 개별 may 값은 출력 묶음 전체가 같은 경로에서 할당됐다는 뜻이 아니다.

누락은 기존 `GRAPH_RETURN_UNASSIGNED` warning으로 보고하며 컴파일·실행을 막지 않는다. bool 분기나 데이터 가용성 오류, 노드 본문에서 실제 C# out 매개변수를 할당하지 않은 오류는 정상 compiler 오류로 남긴다. default 초기화로 잘못된 C# 본문을 숨기지 않는다. compiler probe는 본문을 컴파일하고 호출하지 않는다.

## 편집과 명시적 갱신

기능/구현 입출력 폼의 출력 추가와 역할 선택, module/import의 `out T`, 새 노드의 `[out] 타입 이름`, 호출 계약 미리보기와 결과 핀을 연결했다. 새 기능/객체의 빈 구현은 코드 노드 하나와 출력별 export를 만든다. 참조 구현은 typed call 노드 하나와 출력별 export만 만들며 원본 C#을 복사하지 않는다. 설명이 없는 새 기능에도 생성 노드의 기본 설명을 넣는다. 파일은 기존 소스 그룹의 별도 Review/Confirm에서만 게시한다.

기존 graph는 조회·프로젝트 열기·cold 복원으로 갱신하지 않는다. `readContract`는 현재 외부 계약과 후보 profile/hash를 미리보기만 한다. `rebindContract`는 미리보기 basis와 관찰한 소유 원본의 리비전/raw 내용 CAS 및 현재 외부 typed 계약을 확인한 뒤 graph 헤더를 명시적으로 갱신한다. 새 out이 있으면 구 profile에서 v4로 올릴 수 있다. 기존 노드·binding·본문을 자동으로 다시 연결하거나 고치지 않으며, 기존 구조가 여전히 유효해야 한다. 모든 호출자의 typed import·구현 일치는 최종 compiler가 확인한다.

전체 본문 전환 노드는 원래 public Invoke의 인수 이름·out 역할·calls/this·직접 재귀와 raw 본문을 유지한다. 계약에 out을 추가할 때도 원래 멤버는 유지하고 현재 인터페이스만 별도 명시적 멤버로 조립한다. 달라진 interfaceSignature가 본문 정의 해시를 바꾸므로 사용자가 원문을 재검토해 다시 적용해야 한다. 새 출력은 export로 직접 연결할 때까지 종료별 누락 경고와 기본값을 갖는다. 기존 [전환 origin·소유 그룹·원본 보호](BLUEPRINT_IMPLICIT_END_AND_BODY_CONVERSION.md)는 유지한다.

핀 선택은 기존 JSON 입력을 준비하며 Apply 전에는 원본을 바꾸지 않는다. private 배치·미적용 입력은 복원하지만 미리보기 basis, contract 승인, compiler/AI/Run 권한을 재생하지 않는다. 새 graph/node 원본도 기존 Save·Review·Confirm 및 동시 편집 검사를 따른다.

## 검증과 남은 전체 범위

검사 결과·실패 원인·고정 소스 해시와 일반 체크아웃 증거는 [검증 기록](evidence/v480-integration/named-out-outputs.json)에 기록한다. 서로 겹치는 실행의 통과 수를 합산하지 않는다. 실제 .NET 10 실행의 branch/join 기본값과 경로별 누락, typed scope, whole-body 변환, 명시적 계약 갱신과 공개 편집 API의 CAS/cold/그룹 확정, Chromium의 출력 계약·핀·본문 입력을 검사한다.

v480 전체가 완료된 상태는 아니다. 남은 범위는 ref의 공유 참조/별칭 계약, 중첩 graph의 소유 ID·호출/복귀·버전 계약, 로컬 값과 set/property/expression의 수명·타입·가용성, enum/복합 타입과 임의 실행 출력, 분리된 C# 영역·외부 helper 계약, loop/async, 구현의 물리 파일 삭제와 일괄 타깃 이관, prototype 포털/픽셀 일치의 추가 범위다. 기존 v424의 전체 편집/실행 회귀도 이번 집중 검사와 별도로 관리한다. native/device·실제 계정·유료 모델·사용자 PC 설치를 검증한 결과가 아니다. main, 원본 ZIP과 Android 설정은 변경하지 않는다.


최종 보완 뒤 집중 검사는 **5/0/0 (352.614초)**, 나머지 엔진·이력 검사는 **11/0/0 (357.884초)**, 나머지 브라우저 검사는 **6/0/0 (366.924초)**, Windows/Android 관리 대상 컴파일은 **1/0/0 (178.381초)**로 각각 통과했다. 집중 검사에는 두 embedded 메타데이터 템플릿의 실제 관리 코드 왕복 검사와 새 다중 출력·새 노드 out 폼·모듈 out 편집, 기존 카메라/모듈/선언 폼을 포함한다. [종료별 출력](evidence/v480-integration/named-out-warnings.png), [확정·cold 복원](evidence/v480-integration/named-out-published.png).

이보다 앞선 out 핵심·공개 편집·전체 본문 전환·초기 UI 묶음은 **10/0/0 (153.486초)**였다. 기존 엔진의 16개 성공과 UI의 4개 성공/카메라 1개 실패를 관찰한 광범위 실행은 확인된 결함 수정 때문에 중단했으며 완료된 suite로 표시하지 않는다. 초기 새 기능 생성의 빈 설명 거부, 카메라 상태 혼입과 embedded mode 누락은 재현 뒤 수정했다. module 출력 열 보완까지 포함한 마지막 7개 경로와 그 전후 해시를 별도로 보존한다. 중간 시험 코드의 진단 기대값·nullable 배열·예외 wrapper와 독립 probe의 변수명 수정도 근거에 구분한다. 이 단계들을 합쳐 단일 전체 회귀 통과 수로 표시하지 않는다.

구현 커밋 `8739fb0bc15ee40245e84c7a690b153e03b38823`의 일반 Git 체크아웃 검사도 **1/0/0 (6.921초)**로 통과했다. 속성 적용 후 CRLF가 남은 사본과 새 LF 체크아웃에서 33개 정적 리소스, 실제 Home 시작, 텍스트·인코딩·BOM·바이너리·예산 변조 거부와 원본 바이트 보존을 확인했다. 별도 증거 커밋은 제품·테스트 원본 28개의 해시를 바꾸지 않는다.


후속으로 [명시적 로컬 값·set](BLUEPRINT_LOCAL_VALUES.md)을 별도 profile에 연결했다. 위 로컬 미구현 표시는 out 단위 시점의 기록이며, property/expression·별칭 로컬과 ref·중첩 graph 등 나머지 전체 범위는 여전히 남아 있다.


후속 [외부 ref graph·본문 별칭 보존](BLUEPRINT_EXTERNAL_REF_STORAGE.md)은 별도 v7 profile에서 caller의 ref/out 저장소를 직접 전달하고 미할당 out 기본값을 종료로 미룬다. 위 구 profile의 진입 초기화·외부 ref graph 미지원 표시는 해당 단계 시점의 계약이다. 구 graph는 자동 전환하지 않는다.
