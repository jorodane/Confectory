# enum 계약·선언 소스 준비와 v480 호환성 검토

최초의 개인 계획·선언 미리보기 작업을 보존한 기록이다. 이후 사용자가 분기 작업 후 다음 메인 함수로 진행하는 모델을 확정했고, [순차 switch 실행·명시적 전환](BLUEPRINT_SWITCH_CONTINUATIONS.md)을 연결했다. 오류/기능 종료 선택을 묻던 질문은 폐기했다. 정수 계산식 overflow는 별도 미결이다.

## 준비하는 데이터와 소스

`execution-enum-proposal` schema 1은 소유 `sourceId`, 현재 `definitionHash`·전체 노드 파일 `sourceHash`, 기본 진행 포트 `primary`, `{id,name,value}` 항목을 가진다. 모든 항목에 명시적 ID와 int32 숫자를 요구한다. 최대 32항목·UTF-8 32KiB의 준비 계약이다. 기본 예시는 `next / Next / 0`이며 현재 bool true/false 또는 데이터 return 값에 매핑하지 않는다.

항목 ID는 편집 화면에서 고정하고 새 포트만 새 ID를 만든다. 이름 변경·값 변경·정렬은 같은 ID를 유지한다. 이름·값·위치로 이전 ID를 추측하지 않는다. 기본 포트는 지울 수 없으며 원본 연결의 기본 ID와 달라지면 거부한다. 중복 ID·C# 식별자·숫자, int32 범위 초과·소수·숫자 문자열 강제 변환, `Result`·`value__` 예약 이름과 선언 탈출을 거부한다. C# 식별자는 정규화된 Unicode 이름과 `@` keyword escape를 지원하며 조용히 이름을 고치지 않는다.

검증 결과는 `public enum Result : int` 선언과 ID 주석, 선언 해시, 순서와 독립적인 계약 해시다. 선언은 현재 노드 원본의 해시에 연결한 미리보기다. 미리보기 자체는 Execute 본문을 만들거나 현재 return을 바꾸지 않는다. 공유 전환은 별도 동작이다. UI는 컴파일하지 않으며, 테스트에서 선언만 실제 C# compiler로 별도 컴파일한다. 사용자 코드를 실행하는 검증으로 표시하지 않는다.

`undefinedValuePolicy`·`overflow` 같은 실행 정책 필드는 준비 계약에 넣을 수 없다. 응답은 `runtimePolicy: sequential-switch-continuation`, `executionEnabled:false`, `sourceWritten:false`, `compiled:false`, `executed:false`를 명시한다. 실제 실행은 별도의 명시적 switch profile과 compiler Review/Confirm을 사용한다. 임의의 미지원 profile은 거부한다.

## 원본 연결·개인 편집·콜드 복원

공개 Blueprint `previewEnum` 동작은 현재 graph 읽기의 `basis`, 소유 code-node ID, `contractJson`을 받는다. graph·노드·관련 선언의 모든 관찰 revision/hash를 다시 비교하고 정확한 소유 노드의 definition/전체 파일 hash에 연결한다. source나 definition이 달라지면 보존 입력을 자동 재연결하지 않는다. 현재 원본을 읽고 사용자가 ‘현재 읽은 원본으로 연결 재검토’를 선택해야 한다.

enum 계획은 창의 private `blueprintEnumDraft` metadata에만 저장한다. graph/node 파일과 공유 소스 초안, 현재 Review token을 쓰거나 바꾸지 않는다. 미적용 본문·매개변수 입력은 먼저 처리해야 미리볼 수 있다. enum 개인 계획 자체는 기존 소스 Apply/Review/Confirm을 막지 않는다. 서버 basis·실행 권한은 cold metadata에 저장하지 않으며 현재 소유 원본을 다시 읽는다. 변경된 원본에 대한 계획은 명시적으로 연결을 재검토한다. preview는 노드 Task의 네 권한을 늘리지 않는다.

## v480 요구와 현재 계약의 차이

원본 v480 ZIP과 `main@32dd44f`는 보존한다. 선택한 실제 `blueprintCSharpContract/Sections/ParseCSharpRegions` 함수의 [기존 probe](../tests/probes/v480_csharp_regions.py)는 14개 편집 계약을 확인한다. 원본 편집창도 C# compiler가 연결되지 않았다고 표시한다. 이 함수의 통과를 prototype runtime 또는 현재 제품의 enum 실행 증거로 사용하지 않는다.

| 요구/차이 | 현재 확인·지원 | 실행 연결 전에 남은 점 |
|---|---|---|
| 안정 포트 ID·명시적 int32·표시 순서 | private ID 중심 편집·값/이름 검증·선언 미리보기 | switch profile에서 ID 연결 유지·연결된 case 삭제 거부 |
| prototype의 Result return | 실행 출력 enum | 현재 데이터 return과 의미가 다름. 데이터 결과를 out으로 바꿀 때 기존 `return` 결과 binding의 명시적 대응 필요 |
| 현재 bool/next 실행 | 기존 동기 제어와 경로 분석 유지 | true/false/next를 enum 숫자로 자동 추측하지 않음. 이전 경로와 포트 remap 검토 필요 |
| 미정의 runtime enum 값 | 확정: default 작업 후 메인 계속, default 없으면 바로 메인 계속 | [실행 계약·실제 검증](BLUEPRINT_SWITCH_CONTINUATIONS.md) |
| 선언된 case의 미연결 | default가 있으면 해당 작업, 없으면 메인 계속 | 명시적 빈 case는 return:owner로 default를 건너뜀 |
| ref/out·중복 호출자 저장소 | 실제 CLR 별칭·기본값 적용 순서 지원 | switch/data out 분리에서도 실제 반복 alias 42·42와 별도 저장소 12,16,26을 확인; 자동 whole-body 이관은 제외 |
| whole-body 원본 문맥 | calls/this/재귀 Invoke·scope·인수 이름·CRLF 보존 | enum 실행으로 원래 Invoke 경계를 조용히 교체하지 않음. 별도 이관 검토 필요 |
| C# `Result` 이름 | 선언 미리보기의 보호된 타입 이름 | 기존 인수/본문/local/helper와 이름 충돌 시 명시적 변경·검토 필요 |
| 사용자 enum/Vector3/임의 CLR 타입 | primitive/배열 및 property/methods profile의 object ABI | prototype의 모든 csharpType을 CELEM ABI로 지원한 것이 아님 |
| property write/ref·compound/function live field | 명시적 ObjectModel.Write와 node-time general/reference read | field 자체 lvalue/ref·compound/function runtime은 미지원 |
| 계산식·정수 overflow | 기존 사용자 C# 코드 보존 | int/long overflow 오류/wrap 답변 대기. enum 항목의 int32 범위와 별개 |
| compiler·Task·CAS·복원 | 기존 source/definition receipt·네 도구·Confirm 경계 | 새 switch profile의 compiler·source map·CAS·Task·Confirm을 같은 경계에서 검증 |

개인 미리보기와 공유 enum 계약/실행은 별도 동작이다. 현재 실행 지원 범위는 [switch 계약](BLUEPRINT_SWITCH_CONTINUATIONS.md)을 따르며, 다른 v480 미완료 행은 [전체 상태표](EDITOR_V480_STATUS.md)에 유지한다.

## bounded helpers와 원래 Invoke 문맥

| 노드 | 본문/local helper | Execute 밖 helper | 매개변수 직접 편집 |
|---|---|---|---|
| 일반 static code | 기존 C# 본문과 함수 내부 local helper | methods profile에서 node-owned static 메서드 | 현재 typed profile 안에서 명시적 remap·stale 본문 재적용·Review/Confirm |
| ordinary caller-storage code | 동일한 ref/out 호출자 저장소 전달 | methods profile static helper 지원, 반복 alias 실제 검증 | 미지원. 외부 함수 계약 검토 경로 사용 |
| 전체 본문 이관 `Invoke` | 원래 calls/this/Invoke·이름·CRLF·local helper 유지 | 미지원. `NODE_HELPERS_CONTEXT`로 거부 | 미지원. 외부 계약 검토 경로 사용 |

methods helper 선언은 static과 선택적 public/private, 본문/식 본문을 지원한다. 필드·프로퍼티·생성자·초기화자·중첩 타입·특성·다른 modifier·공유 상태·상위 캡처 확장은 미지원이다. 일반 helper를 원래 instance 문맥에 주입하거나 원래 본문을 static으로 자동 변환하지 않는다. Source/Task/원자적 Confirm 계약은 [이전 구현 계약과 실제 증거](BLUEPRINT_STATIC_METHODS_AND_PARAMETERS.md)를 따른다.

개인 준비 작업과 실행 연결 후속의 [최종 검사·두 소스 단계](BLUEPRINT_SWITCH_CONTINUATIONS.md#최종-검증과-소스-단계)를 별도로 기록한다. 이전 검사 결과를 새 검사 수에 더하지 않는다.
