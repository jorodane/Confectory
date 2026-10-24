# I5-6 3행: 기존 출력 타입의 명시적 대응

기준은 저장소 `196c605`의 v536이다. 기존 정보 함수 상세창의 출력 타입 선택과 기존 계약 대응창을 사용한다. 레이아웃·CSS·Agent/Helper 권한·프로젝트 실행 권한은 변경하지 않는다.

## 이번 지원 단위

직접 소유한 함수 하나에서 기존 일반 출력 **하나**의 숫자 타입(int/long/float/double)을 바꾼다. 일반 `out`과 반환 출력에 같은 검증을 적용한다. 다른 입력·출력의 이름·순서·역할은 유지한다. 각 직접 Blueprint target의 해당 출력은 단일 내보내기 노드 또는 직접 exit 바인딩이어야 한다. 화면은 바뀐 타입과 정확히 같은 타입의 현재 루트 입력을 사용자가 선택하게 한다. 새 값·수치 변환·기본값·저장소를 추측하지 않는다.

원래 graph hash, 출력 이름·노드·원래 바인딩과 새 타입/source를 같은 후보에 묶는다. 호출마다 원래 출력에서 어느 현재 출력으로 받을지도 명시 선택한다. 사용 중인 출력은 정확히 같은 타입의 현재 출력에 대응해야 한다. 연결 없음은 실제 사용처가 남으면 거절한다. 소비되는 바인딩 전체를 유지하며 상수 안의 `node`/`output` 이름은 그래프 연결로 해석하지 않는다. 함수·구현·import·graph·code definition hash·공개 출력 계약을 기존 원자적 후보/CAS와 Review/Confirm에 넣고 C# 원문은 보존한다.

공개 출력은 호출 후 SourceContext 읽기라는 기존 의미다. 프로젝트 접근/공유 권한이 아니다. C# After/enum 후처리의 형식 매개변수가 바뀌는 경우에는 기존 차단을 유지한다. 컴파일 성공만을 근거로 기존 C# 식별자를 추측해 다른 매개변수/멤버에 재결합하지 않는다.

## 검증 기록

격리 fixture와 실제 엔진/Chromium/컴파일러만 사용한다. 사용자 계정·유료 추론·사용자 프로젝트 실행은 없다. 원시 로그는 `/workspace/scratch/v536-information-output-types`에 보관한다. 체크 수는 기능 개수나 통과율이 아니다.

| 검사 | 실제 결과 |
|---|---|
| 격리 실제 API | out+쓰기 실패 4, return 3, out 최종 caller-map 검사 3 check 통과. 바인딩/graph hash/새 타입/source/호환 출력 대응의 누락·위조 및 초과 선택 거절, checkpoint 보존, cold, 실제 컴파일 Review/Confirm |
| 실제 화면 | 독립 out 쓰기 실패 3, 기본 return 2, 독립 out 저장·조회 응답 유실 3, 기본 취소 2, 실제 peer 충돌 2, 기존 out 이름 변경 2 check 통과. 마지막 제한 보완 뒤 기본 return/치수 동일성 2 check도 재검증 |
| 추가 순수 후보 경계 | 값 선택 없는 출력 추가 거절, 원래 유효한 C# After formal 계약 변경 거절 2 check 통과 |
| 영향 회귀 | Native 함수 계약 7, 기존 out C# After 보호 1 check 통과 |
| Native/Linux | 최종 Native 0 warning/0 error, 실제 저장소 Linux 엔진 빌드 성공·stderr 0. 두 마지막 보완은 출력 read를 요청할 때만 실행하고, 선택 없는 output 변경 후보를 거절함 |
| clean checkout·리소스·패키지 | 소스 커밋 뒤 재현 검사를 수행하고 결과를 별도 확정 기록한다. 아직 이 행을 통과로 간주하지 않음 |

UI는 기존 출력 타입 선택과 동일 계약 대응창을 사용한다. [상세창](evidence/v536-information-output-types/output-contract-popover.png), [출력 대응창](evidence/v536-information-output-types/output-contract-mapping.png)을 실제로 열어 확인했다. 기존 수용 레이아웃 `9318098`의 style/consumer/runtime CSS는 byte 동일이며 타입 변경 전후 상세 카드/제목/행 치수도 동일하다. 전체 화면 pixel diff 또는 실제 Windows 비교는 아니다.

후보 점검에서 새 out을 source 지정 없이 추가해도 순수 후보가 성공하는 경로를 재현했다. 디스크/초안에 적용하지 않았다. 출력 변경은 실제 선택된 생산자 assignment를 요구하도록 제한한 뒤 같은 후보가 거절되는 회귀를 추가했다. 출력 추가를 구현한 것으로 보고하지 않는다. 기존 입력만 편집하는 read에는 새 출력 catalogue의 개수 제한이나 비용을 추가하지 않도록 출력 조회는 명시 요청에만 수행한다. 검사 실패를 숨기거나 CAS/타입 검사를 완화하지 않았다.

## 명시적 잔여

3행 전체 완료는 아니다. 출력 추가·삭제와 그 실행 경로/반환 계약 변경은 `outputCreates/removeOutputs/outputRoutes/outputEntry`를 같은 후보와 caller 출력 대응에 결합해야 한다. 값 선택 없는 출력 추가는 이번 단위에서 거절한다. 여러 출력의 동시 타입 변경, 같은 출력의 여러 writer, 숫자 외 타입, 현재 루트 입력 이외의 대체 값/source는 이번 지원 단위에 포함하지 않는다. 기존 일반 out 이름 변경은 유지한다.

고정 9행의 4~9행(C# 명시 본문 결합, nested, 전체 본문/ref/out 역할, 등록/복사 출처, 여러 함수 동시 후보, 고급 핀 타입/표시명)은 기존 명세의 미구현으로 유지한다. 이번 거절을 그 기능의 완료로 표시하지 않는다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미검증이다.
