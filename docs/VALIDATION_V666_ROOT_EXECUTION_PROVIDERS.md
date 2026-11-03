# M12: 여러 직접 소유 provider의 공개 분기 계약

## 원래 사용자 흐름과 이번 범위

저장소 v666 `dist/app.js:2469–2476`의 입출력/실행 분기 우선 정의와 `dist/blueprint.js:969–976`의 공개 분기·반환 편집을 따른다. 기존 함수의 공개 분기를 바꿀 때 같은 계약을 구현하는 직접 소유 ordinary Blueprint provider가 여럿이면, 특정 provider의 target만 바꾸어 나머지를 낡은 계약으로 남기지 않는다.

이미 저장된 동일 함수의 직접 소유 provider와 그 Blueprint target 전부, 실제 직접 Blueprint 호출 위치 전부를 기존 명시 대응 후보에 결합한다. provider별 target 표시에는 기존 구현 ID를 붙여 같은 `common`/`linux`를 구별한다. 모든 추가 target의 반환 ID/None과 모든 호출 위치는 사용자가 명시해야 하며 자동 선택하지 않는다. 실제 실행 provider는 기존 scoped provide/배정 계약으로 선택되고 이 편집이 배정을 변경하지 않는다. 기존 UI/팝오버/레이아웃/제품 JS·CSS·HTML을 바꾸지 않는다.

다른 provider의 imports도 readonly 관측으로 수집해 같은 Review/Confirm·receipt·최종 CAS에 포함한다. 원래 C# record, 함수 IO·branch ID/값, 다른 함수 헤더, 호출자의 다음 줄과 명시 연결을 보존한다. 전체 그룹 복원에서 provider 멤버 누락을 거절하며 부분 Review·누락/중복 대응·저장 전 원문 변경·Review 뒤 다른 provider 원문/import 변경은 전체 미적용이다. 이전 단일 provider/호출자 없는 흐름도 유지한다.

모든 provider가 같은 기존 ordinary switch-profile의 직접 소유 Blueprint일 때만 공개 계약 갱신을 허용한다. opaque C#·whole-body/중첩 native·same-contract copy provenance·override·부모/외부 원본의 의미를 추정해 바꾸지 않는다. canonical 물리 그래프를 공유하는 target은 모호한 소유 초안으로 거절한다. 이는 현재 지원 경계이며 자동 변환/독립 계약 복제를 필수 후속으로 추가하지 않는다. override 원계약과 권한을 완화하지 않는다.

## 검증 상태와 유한한 잔여

집중 검사와 최종 source-bound 결과는 완료 후 아래에 기록한다. 새 데이터 타입 행렬을 만들지 않고 원래 scoped provider를 다르게 배정한 두 호출자·두 provider의 실제 실행, 명시 대응과 동일 원자 그룹을 확인한다. 이전 ordinary 비void와 copy 데이터 보존은 관련 회귀로 유지한다.

M12의 남은 기존 흐름은 중첩/private·기존 native caller/provider와 등록 외부 import 관측을 공개 계약 갱신 후보에 명시 결합하는 일이다. 이미 올바른 비소유 원본 쓰기/override 계약 변경 거절, 구형 profile 자동 migration은 미구현으로 세지 않는다. M11은 구체적인 회귀가 없으면 닫혀 있다. 이어지는 M4는 확정된 동기 caller 오류 정책과 await→출력 발행→완료→결과 분기→다음 실행 순서를 따른다. 실제 Windows/WebView2·모바일/전체 UI·Space 전달은 별도 미검증이다.
