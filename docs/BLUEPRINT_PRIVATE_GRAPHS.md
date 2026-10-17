# 부모 노드에 소유되는 private graph

새 `sync-acyclic-nested-v1` / `feature-blueprint-source-v9`는 기존 typed input/ref/out/return과 동기·비순환 실행으로 private 자식을 호출한다. 자식 종료는 부모 호출 뒤의 next/bool 경로로 복귀한다. 호출마다 로컬을 초기화하고 부모 로컬·receiver를 암묵적으로 캡처하지 않는다. property 대상·읽기 시점과 계산식 overflow 정책은 답변 대기 상태이며 이 기능에 포함하지 않았다. 기존 C# 본문의 연산과 구현 인스턴스 문맥을 바꾸지 않는다.

이전 [조사 기록](BLUEPRINT_NESTED_PROPERTY_CONTRACT_REVIEW.md)의 소유·편집 관찰을 실제 compiler와 원본 편집에 연결한 후속이다. 조사 probe의 19개 검사를 이번 실행 구현의 통과 수로 옮기지 않는다. v480 전체 완료를 뜻하지 않는다.

## 원본과 소유권

물리 root graph의 `kind:"graph"` 노드가 자식 `graph` 객체와 명시적인 `signature`, `arguments`, `intent`, `control`을 소유한다. 자식에는 schema/profile/nodes/entry/edges/exits와 선택적 locals를 기록한다. 전역 feature ID나 contractHash는 자식 원본에 넣지 않는다. 부모 signature에서 compiler 내부 계약을 만들며, 전역 함수 참조 `kind:"call"`과 구분한다.

자식의 C# leaf는 기존 schema 1 node 파일 형식을 사용하고 `implementation` 경로는 물리 root graph 디렉터리를 기준으로 해석한다. 모든 leaf는 별도 파일을 소유한다. inline graph는 별도 C# 원본 파일이나 임의 Task 권한을 만들지 않는다.

| 용도 | 예 |
|---|---|
| 물리 root 원본 | `App::ValueBody/body:common` |
| 자식 편집 화면 | `App::ValueBody/body:common/graph:private/graph:inner` |
| 소유 leaf 원본 | `App::ValueBody/body:common/node:private/node:inner/node:body` |
| compiler/probe leaf key | `private/inner/body` |

화면 ID는 물리 원본으로 등록하지 않는다. 원본 CAS·저장·Review는 실제 root graph와 실제 leaf 파일을 사용한다. 같은 local ID가 다른 자식에 존재할 수 있으며, private leaf 정의에는 구현 ID·body target·전체 부모 경로를 포함한다. 다른 구현/target/부모로 옮긴 본문의 정의 증거를 재사용하지 않는다. 노드 파일 내부 `node`는 마지막 local ID를 유지한다.

`BlueprintTree`의 제한은 private 깊이 8, 전체 노드 256, qualified key 768자다. 편집 읽기와 변경은 기존 64개 원본·2MiB 예산도 적용한다. root 전체의 소유 leaf를 관찰하므로 다른 자식의 변경도 오래된 편집 기준을 무효화한다. 경로·파일 공유·링크·소유 범위 검사는 기존 저장 규칙을 유지한다.

## 호출과 compiler 증거

private 자식을 정적인 typed C# 함수로 조립하고 필요한 함수 imports를 명시적 매개변수로 전달한다. 사용자 C# leaf와 시스템 wrapper를 구분해 각 실제 leaf의 본문 구문·예약 이름·매핑 지시문을 검사한다. 사용자 본문의 `#line` 등 기존 거부 경계를 유지한다. 생성 심벌·로컬·종료 label은 부모 경로에 따라 구분한다.

ref 인수는 현재 입력·로컬·선행 결과의 실제 슬롯을 전달한다. 일반 out 결과는 기존 노드의 독립 결과 슬롯이다. `forwardCallerStorage:true`는 기존 v7 계약대로 현재 함수와 같은 전체 타입·mode·순서·반환과 직접 입력 위치를 요구하며 graph 노드에도 적용된다. 이 경우 실제 호출자 ref/out 별칭을 전달하고 미할당 out 기본값은 정상 종료 시 적용한다. 임의 부분 out 매핑·property 참조나 부모 로컬 캡처는 추가하지 않는다. 기존 [외부 ref 저장 규칙](BLUEPRINT_EXTERNAL_REF_STORAGE.md)과 [별칭 로컬](BLUEPRINT_ALIAS_LOCALS.md)을 유지한다.

모든 중첩 leaf·계약·등록부·compiler identity와 누락 파일을 build 전후에 확인한다. 소유 파일을 공유하면 거부하고, C# 진단의 leaf key·파일·원본 해시를 전체 경로로 보존한다. 준비된 비연결 자식 본문도 실행하지 않고 실제 compiler에 포함한다. leaf의 독립 probe는 전체 경로를 받아 해당 본문만 컴파일하고 실행·게시하지 않는다. 실제 compile 중 입력이 바뀌면 이전 성공 산출물을 유지한다.

자식의 미할당 반환·out 경고는 전체 `privatePath`를 보존해 `nestedWarnings`와 빌드의 `blueprintWarnings`에 전달한다. 현재 graph 자체의 종료 경고는 별도로 유지하므로 다른 자식의 같은 local ID에 경고를 잘못 붙이지 않는다.

## 편집·복원·검토

현재 graph에서 명시적으로 v9 profile을 검토·적용한 뒤 노드 생성 창의 ‘내부 graph’를 선택한다. ‘내부로 이동’과 ‘상위로 이동’으로 편집하며 화면에는 자식 이름·경로를 표시한다. 각 화면의 배치·미적용 입력은 별도 private 상태다. root의 기존 code 정의는 profile 전환만으로 다시 작성하지 않는다.

자식 화면에서 설명·인수·실행/시작·출력·로컬·C#을 적용하면 물리 root 또는 해당 leaf의 공유 초안을 바꾼다. root와 모든 관찰 소스의 리비전·해시로 CAS를 검사한다. 새 leaf의 본문과 변경된 root graph는 필수 Review/Confirm 그룹이다. Save/cold 복원은 최종 파일을 게시하지 않으며 이전 basis·Task 권한을 재사용하지 않는다. 복원한 입력은 현재 원본 읽기와 기준 재검토 후 적용한다.

본문이 있는 private graph를 한 번에 제거해 자식 변경을 버리지 않는다. 내부 노드를 명시적으로 정리한 뒤 빈 graph를 제거할 수 있다. 게시된 기존 C# 파일은 보존한다. 자식에서 새 전역 함수 계약/가져오기 등록을 만드는 UI는 root의 명시적 계약 작업으로 제한하며, 기존 declared typed call의 중첩 실행은 지원한다.

노드 도구는 정확한 qualified leaf와 네 가지 기존 권한만 받는다. 부모 graph·다른 노드·파생 C#의 편집 권한을 주지 않는다. 부모 정의/계약 변경 시 stage를 거부하고, 공개 완료 증거도 올바른 body target과 독립 leaf compiler 결과를 요구한다.

## 검증 기록

경고 전달 보완 전 고정한 제품·테스트 소스에서 엔진 **60/0/0, 980.464초**, 실제 Chromium **12/0/0, 921.526초**, Windows/Android 관리 프로필 **1/0/0, 140.497초**로 통과했다. 이후 경고 전달용 제품 2개 파일과 테스트 1개 파일만 바꿨다. 같은 graph의 생성 C# 본문 해시가 유지되는 것을 확인했고, 최종 소스의 중첩 실행·소유·경고·도구 권한·CAS/cold/Confirm·실제 Chromium 추가 검사는 **8/0/0, 132.504초**로 통과했다. 중복 검사는 합산하지 않는다. [단계별 로그·소스 해시](evidence/v480-integration/private-graphs.json), [내부 편집](evidence/v480-integration/nested-child.png), [확정 후 복원](evidence/v480-integration/nested-published.png). 초기 실패와 수정 전 통과를 최종 소스의 회귀 수로 합산하지 않는다. 관리 프로필은 컴파일 검사이며 native 픽셀·장치 실행 증거가 아니다.

수용 범위는 실제 중첩 ref/ref/out 호출자 별칭·호출별 로컬·부모 분기 복귀, 같은 local ID의 형제 소유권, 명시적 imports, 비연결 본문의 실제 compile·무실행 probe, 부모 캡처/순환/경로 공유 거부, compiler 중 원본 변경 보존, 실제 편집 CAS/cold/필수 그룹 Confirm과 브라우저 생성·탐색·복원이다. custom 실행 포트·enum/객체 ABI·graph 순환/async·property/계산식·v480 전체 편집 회귀는 후속 범위다.

구현 커밋 `baff3ea31c0abfe01b67ff582b49d0224aa9edc9`의 일반 Git checkout·보존 CRLF/새 LF·33개 리소스·실제 Home 시작·변조 거부는 **1/0/0, 6.726초**로 통과했다. 경고 보완 뒤 추가 검사 이후 제품·테스트 소스는 바뀌지 않았다.

후속 [노드 도달 시 프로퍼티 읽기](BLUEPRINT_NODE_TIME_PROPERTIES.md)는 사용자 답변에 따라 호출자가 전달한 실제 객체를 해당 노드에서 한 번 읽고 결과를 전달한다. 위 property 미정·미구현 표시는 당시 단위의 기록이며 이 후속이 현재 의미를 정한다. 계산식 overflow 결정 대기는 유지한다.
