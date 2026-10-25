# 고정 7행: 복사본·등록 상속 계약의 지원 경계

`V536_I5_6_REMAINING.md`의 7행만 다룬다. 같은 함수 하나의 명시적 편집과 원래 소유·출처·계약 증거를 사용하며, 8행의 여러 함수 공유 caller 합성과 9행의 고급 타입/표시명은 별도다.

| 사용자 조작 | 이번 지원과 검증 | 남은 경계 |
|---|---|---|
| 정보에 직접 배정한 저장된 복사 구현의 함수를 편집 | 단일 target·단독 직접 배정·프로젝트 소유 함수/복사 ID를 기존 `BlueprintCopyAbi`로 확인한다. copy owner/배정/모듈 또는 직접 포함 정보 함수/원래 provenance/graph·구현 해시/계약 문맥을 원래 입력에 묶는다. native donor를 보존한 입력 이름 변경·복사 C# 편집·원자적 저장/복원/Confirm을 검증한다 | 새 미확정 copy와 여러 target, 외부 함수 ID를 구현하는 copy는 이 경로의 기존 안전한 차단을 유지한다. 다른 소유자의 직접 공유 배정도 단독 갱신하지 않는다 |
| 다른 객체에 배정한 caller 복사본이 편집 중인 정보 함수를 호출 | 실제 모듈 require/provider와 copy owner를 확인하고 callee·선택한 수동 caller C#·import/context를 한 후보/CAS에 담는다. 원래 native caller donor의 선언·CRLF 본문과 복사 출처를 보존한다 | 같은 전역 함수 계약을 실제로 사용하는 다른 provider/원본이 부적합해지는 변경은 원본을 추측해 고치지 않고 전체 거절한다 |
| 등록 함수가 부모 함수를 상속 | 선택한 직접 등록 함수에서 시작하여 실제 선언의 부모 edge와 해당 팩의 명시된 dependency만 따라 읽는다. 최대 16개·순환/타입 검사·선언/manifest 해시·전체 부모 receipt를 결부한다. 부모가 별도 등록 팩에 있어도 현재 프로젝트의 직접 import 권한으로 확대하지 않는다 | 등록 부모를 쓰기 대상으로 바꾸지 않는다. 현재 프로젝트 소유 함수를 부모로 삼는 등록 함수의 별도 교차 경계는 자동 확장하지 않는다 |
| 직접 상속 implementation 참조를 통하여 편집 | 부모 본문·외부 구현을 수정하는 경로는 아직 연결하지 않았다. 기존 거절을 유지한다 | 직접 상속 참조의 전체 부모 header/body 증거와 기존 명시적 복사/로컬 편집 진입 연결이 남았다. 이것은 사용자 설계 결정이 필요한 항목으로 돌리지 않는다 |

소유 copy와 상속 참조는 다른 수명이다. 원래 donor·부모·등록 팩은 그대로 두며, 복사 ID와 `copySource.implementation`/`bodyOrigin`을 같은 소유 대상으로 취급하지 않는다. 현재 copy 형식에서 서로 다른 source/body origin을 주장하는 새 실행 의미를 만들지 않는다.

`InformationFunctionCopies`는 검증된 내부 편집 view에서만 provenance를 분리하고 후보를 내보내기 전에 동일 provenance를 복원한다. 그 뒤 실제 새 함수/모듈/provider 계약과 owner/target/배정을 다시 검증한다. 일반 root/private 편집기의 기존 copy guard를 지우거나 외부 요청의 boolean으로 우회하지 않는다. 파일 위치·해시·CPP 원문·정확한 숫자와 순서는 기존 전체 후보/CAS 검증을 거친다.

실제 계정·유료 AI·사용자 프로젝트 실행 없이 격리 fixture를 사용한다. 원본 v536 HTML/CSS/레이아웃·권한·명시적 Review/Confirm은 유지한다. **7행 전체 및 I5-6 전체 완료가 아니다.** 직접 상속 implementation 연결과 위에 명시한 copy 제한을 남기며 8·9행으로 무단 확장하지 않는다.
