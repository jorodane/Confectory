# 순차 switch와 메인 흐름 복귀

사용자가 확정한 실행 모델은 메인 함수들을 차례로 한 번씩 호출하고, 각 함수의 결과에 맞는 case 작업을 실행한 다음 다음 메인 함수로 진행하는 것이다. 미일치 값도 계속 진행한다. 명시적 default 작업이 있으면 그것을 실행한 후 계속한다. C# case fall-through나 모든 case 순회는 없다. 이전의 ‘오류 또는 기능 종료’ 선택지는 폐기했으며, 정수 계산식 overflow는 별도 미결이다.

## 명시적 전환과 원본

`sync-acyclic-switch-v1` / `feature-blueprint-source-v12`는 methods profile의 typed 인수·ref/out·로컬·private graph·node-time property·bounded static helpers를 잇는다. 저장된 이전 profile의 제어 의미와 생성 해시는 바꾸지 않는다. 루트에서 `upgradeProfile`로 명시적으로 전환하며 private graph의 profile도 함께 전환한다. 전환만으로 기존 next/bool 제어, 데이터 return, 본문, 실행 연결을 enum으로 바꾸지 않는다.

일반 code 노드의 데이터 signature `return:void`에서 `applyEnum`을 별도로 선택한다. `control:"switch"`, `executionEnum:{primary,members:[{id,name,value}]}`가 정의에 들어간다. 현재 sourceId·definitionHash·전체 소스 파일 hash에 연결한 검증된 계약만 받으며, 모든 관찰 원본의 revision/hash CAS를 통과해야 공유 초안이 바뀐다. 기존 본문과 next 연결은 보존하고 본문은 stale이 된다. 사용자가 `return Result.Member;`와 필요한 out 할당을 직접 작성해 현재 정의로 재적용하고 compiler Review/Confirm으로 확정한다. 데이터 반환이 있는 노드와 bool 분기는 자동 변환하지 않는다. 기존 반환 binding을 보존한 명시적 데이터/out 이관 또는 새 void 노드가 먼저 필요하다.

각 노드의 생성된 private static class에 `public enum Result:int`와 `Result Execute(...)`를 둔다. 데이터 결과는 이름 있는 out이다. selector는 내부 int로만 전달하며 일반 데이터 return pin이 아니다. CELEM 공개 인터페이스에 임의 enum/Vector3 ABI를 추가한 것으로 보지 않는다. 현재 profile에서 일반 caller-storage·bounded helpers의 기존 경계를 유지하며, whole-body Invoke 문맥은 enum으로 자동 전환하지 않는다.

항목은 안정 ID·서로 다른 명시적 int32·정규화된 C# 이름을 가진다. 이름·값·정렬 편집으로 ID를 재할당하지 않는다. 기본 ID 삭제/변경, 중복·잘못된 이름·범위 초과·소수·문자열 강제 변환을 거부한다. 이미 연결된 case ID 삭제는 거부한다. enum 또는 branchOwner 정의 변경은 독립 노드 정의 hash와 Task 권한 검증에 포함된다. 본문·helpers·선언은 구현 hash와 source map에 포함된다.

## case 작업과 메인 continuation

| 원본 항목 | 의미 |
|---|---|
| switch의 `next` | case/default 작업 이후의 메인 continuation |
| `case:<stable-id>` | 해당 enum 숫자에만 선택되는 작업 |
| `default` | 연결된 case가 없는 결과에 수행할 선택적 작업 |
| case 연결 없음·default 없음 | 다음 메인 함수로 진행 |
| 명시적 빈 case `return:<switch-id>` | default를 건너뛰고 다음 메인 함수로 진행 |
| 작업 노드 `branchOwner:<switch-id>` | 그 switch의 case/default 작업 범위 |
| 작업의 미연결 next/bool port | 소유 switch의 메인 continuation으로 복귀 |
| `return:<owner>` | 해당 범위의 명시적 메인 복귀 |
| 루트 미연결 next·명시적 `exit:` | 실제 기능 종료 및 출력 할당 검사 |

기존 next/bool 노드는 profile 전환 후에도 기존 제어를 유지한다. case/default 대상은 해당 switch의 작업 범위에 있어야 하고, 일반 연결은 같은 범위에 있어야 한다. 다른 범위로 직접 넘어가거나 다른 owner에 복귀하지 않는다. 소유 범위의 순환·깊이 초과·분기 안의 직접 entry를 거부한다. 중첩 switch는 먼저 자신의 next로 복귀하고, 그것이 바깥 분기의 복귀이면 바깥 switch의 다음 메인으로 이어진다. 실행 중 switch 함수를 다시 호출해 복귀하지 않으므로 중복 실행이 없다.

유효 CFG는 선택된 case/default와 복귀를 메인 continuation에 합친다. default가 모든 미일치를 처리할 때 불가능한 직접 bypass를 추가하지 않는다. 따라서 dominance와 out must/may는 실제 실행 가능한 경로를 따른다. 분기 복귀 자체를 기능 종료로 경고하지 않는다. 메인 continuation이 바로 기능 종료인 경우에도 경고는 실제 메인 next에 모으며, 각 미할당 경로의 예시는 보존한다. 명시적 case 작업의 기능 종료는 실제 종료로 검사한다. out 기본값은 실제 기능 끝에서만 적용하므로 호출자 ref/out 별칭의 관찰 순서를 유지한다.

## 실제 편집과 검증 경계

개인 enum 계획·선언 미리보기는 원본을 쓰거나 실행하지 않는다. `runtimePolicy:sequential-switch-continuation`, `executionEnabled:false`는 미리보기 응답이며, compiler 실행의 증거가 아니다. profile 전환과 enum 공유 적용은 별도 버튼이다. C# 보호 보기에는 enum 선언과 Result 반환형을 고정 외곽으로 보여주고, 본문과 기존 허용 helpers만 편집한다. 노드 생성에서 메인 또는 case/default 작업 범위를 선택하고 실행 연결에서 case/default, 메인 계속, 메인 복귀, 실제 기능 종료를 구분한다. 복원한 개인 입력은 새 읽기의 basis로 명시적으로 재검토한다.

검증에는 실제 CLR 선택 case/default/미일치·빈 case·두 메인 함수 호출 횟수·반복 호출·중첩 복귀·ref/ref/out 중복 저장소, 실제 종료의 할당/미할당 경고, 구 profile 거부/보존, 독립 무실행 compiler probe를 포함한다. 공개 편집 경로는 원본 CAS·이전 Task 무효화·원자적 Review/Confirm·콜드 basis 거부를 검사한다. 실제 Chromium은 전환·Result 보호 외곽·분기 소유 노드 생성·case 연결·메인 복귀·콜드 복원·compiler Confirm을 검사한다. 최종 소스 해시·정확한 검사 수·일반 Git checkout/리소스 시작 근거는 후속 검증 기록에 남긴다.

이 변경으로 [전체 v480 상태표](EDITOR_V480_STATUS.md)의 모든 행을 완료한 것은 아니다. 계산식 overflow, 일반 사용자 타입 ABI, property field lvalue/ref, compound/function live property, 외부 서비스·native/device·계정/사용자 PC 경계는 각각의 미완료 상태를 유지한다.

## 최종 검증과 소스 단계

고정한 제품·테스트 원본 27개에서 엔진/공개 편집 **94/0/0, 1277.209초**, 실제 Chromium **13/0/0, 999.502초**가 통과했다. 이전 helpers 단계의 서로 다른 82개 검사와 이번 enum/switch 12개를 이 실행에서 함께 검사했으며, 과거 결과를 더한 수가 아니다. 공유 enum 이름·값·정렬 변경의 안정 ID 연결, 연결된 항목 삭제 거부, 명시적 전환·본문 stale/재적용·Task/CAS·콜드·원자적 Confirm도 포함한다.

그 후 switch 전용 복귀 점선·포트 줄바꿈·캔버스 높이·표시와 해당 실제 UI 검사를 보완했다. 바뀐 5개 파일은 UI 세 파일, resource pin, UI Python 검사이며 compiler/API/엔진 검사 원본은 같다. 최종 원본은 28개다. 보완된 실제 UI는 **1/0/0, 113.754초**로 재통과했다. 이는 앞의 13개 중 한 건을 재검사한 것이며 서로 다른 14건으로 합산하지 않는다. 최종 원본에서 Windows/Android 관리 프로필 컴파일도 **1/0/0, 130.015초**로 통과했다.

실제 [분기 복귀 연결](validation/v480-switch-routes.png), [안정 ID·enum 선언](validation/v480-switch-enum.png), [메서드 목록·두 소스 단계의 해시·단계별 결과](validation/v480-switch-continuations.json)를 남긴다. 일반 Git checkout·보존 CRLF/새 LF·36개 리소스·실제 Home 시작·변조 거부는 구현 커밋 HEAD를 대상으로 검사하며, 정확한 HEAD와 결과는 같은 검증 JSON의 `checkout` 항목에 기록한다.

재개 직후 셸·원격 상태와 고정 원본 27개의 해시 일치를 확인했다. `/tmp` 복원용 파일은 사라졌지만 작업 원본과 완료된 회귀 로그는 보존됐다. 불필요했던 브라우저 다운로드는 403으로 거부되어 재시도하지 않았고, 기존 테스트에 명시된 `/usr/bin/chromium`으로 재검사를 완료했다. 크레딧 한도 오류는 재발하지 않았다.
