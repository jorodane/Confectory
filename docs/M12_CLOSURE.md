# M12의 유한한 원래 사용자 흐름과 종료 조건

기준은 저장소 v666 ZIP의 `dist/app.js:2469–2476`(입출력/실행 분기 우선), `dist/blueprint.js:135`(참조 함수의 call 포트), `:969–976`(정의/반환 편집), `:248`(출력→결과 분기→다음 실행)와 확정된 원문/override/권한 보존 합의다. CLR 타입과 문맥을 곱해 새 필수 행렬을 만들지 않는다. 현재 의미가 유지되는 기존 데이터·body·caller 계약을 아래 네 흐름으로 마감한다.

| 실제 사용자 흐름 | 현재 근거와 닫을 범위 |
|---|---|
| 데이터와 공개 분기를 함께 반환 | 기존 value/ref/out·ordinary 비void 반환, 소유/저장·새 copy/자식 직접 본문·등록 외부의 ordinary 반환을 이미 연결했다. 새로운 타입/소유 조합을 별도 잔여로 늘리지 않는다. |
| 직접 소유 공개 함수의 계약을 전체 caller/provider에 갱신 | 여러 provider/target·ordinary/private frame은 연결했다. native whole-body의 기존 instance 진입과 원래 C#·`this.Invoke`·수신자/재귀·import 의미를 보존한다. 자체 결과를 계산하는 postCall wrapper와 ordinary IInvoke 소비자는 새 공개 분기로 자동 재해석하지 않고 실제 영향만 대조한다. caller 자신의 공개 분기·private forwarding 계약도 보존해야 한다. native whole-body 진입은 원문/receiver/재귀/scoped import·원자 저장/최종 CAS 및 새 패키지/복원 검증까지 마감했다. caller 자신의 공개 분기나 private forwarding과 postCall은 실제 의미/영향을 대조할 다음 복합 호출 경계다. |
| 이미 존재하는 같은 계약 copy·자식 소유 본문이 포함된 전체 갱신 | 완료한 본문 반환 선택과 공개 정의 갱신을 구별한다. 소유한 공개 선언을 바꾸는 거래에서 실제 소유 target/호출 대응과 기존 provenance/배정·상속 소유자를 명시적으로 결합한다. 부모/참조 원본을 쓰거나 override에서 독립 IO/계약을 만들지 않는다. 실제 누락과 정상 보호를 원래 소유 규칙으로 판정한다. |
| 등록된 외부 import를 포함한 관측과 저장 | 새 접근권한 없이 기존 등록/의존성을 따라 외부 함수/manifest를 readonly로 관측한다. 소유 manifest·scope·원시 receipt를 저장/복원/Review/최종 CAS까지 결합하고 경합/누락/변조를 거절한다. 외부 선언은 writable member로 위장하지 않는다. |

종료 조건은 위 실제 흐름에서 공개 분기의 추가/이름·순서/삭제/None, 반환 배치·기존 데이터, 명시한 실행 연결이 저장·복구·실제 실행까지 이어지고 전체 영향 후보가 하나의 Review/Confirm·최종 CAS로 검증되는 것이다. 실패/취소/Undo·중단/응답 유실/경합/재시작은 입력과 원본을 보존해야 한다. 이미 지원하는 interface 소비자는 보존하거나 실제로 호환되지 않는 조작을 명확하게 거절하며, 모호한 의미를 추정해 바꾸지 않는다.

비소유 부모/외부 원본 쓰기, override의 독립 입출력/계약 변경, 독립 새 계약 복제, 구형 profile 자동 migration은 M12 필수 잔여가 아니다. 현재 안전 경계를 영구 UX 정책으로 확정하지 않는다. 필요한 원래 흐름을 닫을 때만 기존 profile/원문 호환을 대조하며 없는 자동 변환 요구를 추가하지 않는다. 정보 종류의 C# 표현은 별도 기존 항목이다. M11은 구체적 회귀가 없으면 닫혀 있다.

이 종료 조건을 충족하면 M12를 마감하고 M4의 실제 async 실행을 진행한다. 확정된 M4 규칙은 동기 caller가 명시적으로 async로 바뀌기 전에는 호환되지 않는 호출을 오류로 거절하며, await→출력 발행→완료→결과 분기→다음 실행 순서를 지키는 것이다. 자동 blocking/호출자 변환·원문 await 치환이나 새 권한은 도입하지 않는다. 전체 UI/Windows·모바일 실기기/Space 전달은 별도 검증이다.
