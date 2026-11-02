# M12: 소유 본문·copy의 기존 데이터와 분기 반환

## 원래 요구와 이번 연결

저장소 v666 `dist/app.js:2469–2476`은 입출력/실행 분기 정의를 구현보다 우선한다. `dist/blueprint.js:969–976`은 readonly 정의의 기존 분기 반환 배치를 제공하며, `:248`은 데이터 발행→결과 분기→후속 실행 순서를 정한다. 이미 지원된 ordinary switch-profile 본문 반환에 기존 비void 값·typed out/ref를 함께 보존한다.

직접 소유 정보의 저장/새 same-contract copy, 자식이 직접 선언한 Blueprint target, 등록 외부 함수의 로컬 ordinary provider와 저장/새 copy를 연결한다. 공개 함수/override IO·기존 분기 ID/None·provider 선택·donor/부모/외부 원본은 그대로다. 독립 새 계약 복제·원문 재작성·새 외부 권한을 추가하지 않는다. 부모에게서 빌린 본문은 읽기 전용이며 자신의 본문만 편집한다.

`{executionBranch, value}`를 공통 검증에 연결한다. 비void의 기존 직접 종료점 데이터 연결과 export-return/default는 유지하고 실행 선택·선만 바꾼다. 데이터 누락·치환과 잘못된 ID는 전체 후보를 거절한다. 새 copy의 sealed preview/첫 Save, 저장 copy의 복원 guard, 자식/등록 본문의 원자 그룹·원시 읽기 lease·최종 CAS에서 같은 규칙을 적용한다. void/private의 기존 한 필드 종료점 형식은 유지한다. C# 생성/Invoke 계약이나 원본 팝오버·CSS·HTML·제품 JS는 변경하지 않는다.

## 검사와 지원 경계

최종 동결 source와 검사·보관 결과는 아래에 기록한다. 동일한 int 반환·ref int·out long/string 프로젝트를 기존 소유 흐름에서 실행한다. 타입/역할/문맥의 모든 곱을 새 필수 검사 목록으로 만들지 않는다. 반환 계획과 무관한 데이터/본문 편집은 기존 별도 계약을 따른다.

`__fg_` 호출 노드 매개변수는 기존 NODE_RESERVED_NAME 규칙의 정상 거절이다. 유효한 일반 함수의 IInvoke 매개변수와 그래프 노드의 내부 예약 경계를 구분한다. 진단 입력이 이 보호에 걸린 근거와 정상 거절 검사를 보존하며 새로운 migration/이름 재작성 요구로 추가하지 않는다. 큰 데이터 그래프의 UI fixture는 기존 전체 맞춤 조작을 사용하고 강제 클릭이나 제품 레이아웃 변경을 하지 않는다.

이전 authoring의 해당 비void 반환 계획 편집/복원을 보장하지 않는다. 최신/정상 롤백, 기존 원문/checkpoint 및 재현 입력을 보존하고 자동 승격·삭제를 하지 않는다. 실제 Windows/WebView2·모바일 실행·전체 UI·Space/Library 전달은 교차 패키지/hosted UI 검사와 구분한다.

## 유한한 다음 흐름

M12의 ordinary 데이터 반환 연결은 기존 소유/등록 경계에 적용했다. 남은 계약 갱신은 두 사용자 흐름이다.

1. 중첩/private·기존 native 호출 문맥 또는 등록 외부 import를 사용하는 실제 caller/provider를 공개 계약 후보에 명시적으로 결합하기. 원래 코드/프레임 의미와 readonly 외부 관측을 보존하며 자동 의미 변환을 하지 않는다.
2. 여러 직접 소유 ordinary provider의 모든 target 반환과 실제 caller를 하나의 공개 계약·원자 후보에 결합하기. 자동 provider/target 선택이나 override 계약 변경은 하지 않는다.

구형 profile 자동 변환·부모/참조 원본 쓰기·독립 계약 복제는 필수 잔여가 아니다. M11은 구체적 회귀가 없으면 닫힌 상태다. M4는 확정된 규칙(동기 caller는 명시 async 전환 전 호환되지 않는 호출을 오류로 거절, 자동 blocking/전환 금지)에 따라 실제 async 저장·호출·await→출력→완료→분기→후속 실행을 연결하는 다음 고정 항목이다.
