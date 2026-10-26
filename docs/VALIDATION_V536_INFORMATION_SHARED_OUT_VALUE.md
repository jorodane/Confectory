# 고정 8행: whole-body out→값과 공유 호출자

기준은 `7fbcf1d7797ea0c1edc481d40232a03b0e3f7cf0`의 기존 v536 정보/C# 및
명시 호출 대응 UI다. 기존 단일 계약 검증기가 지원하는 정확한 code/return lift의
out→값을 여러 직접 소유 함수와 공유 ordinary caller의 한 후보/CAS에 결합한다.
이름·타입·위치·핀 수·반환과 원문은 유지하며 새 UI/권한/계약 ID는 만들지 않는다.

## 원래 조작과 종료 조건

기존 C# 매개변수에서 `out long nativeTotal`의 out을 직접 제거한다. 공개
amount/count와 nativeAmount/nativeTotal은 구분한다. 새 count 값에는 원래
amount 바인딩을 명시 선택하고 다른 amount에는 정확한 값 5를 직접 입력한다.
원래 바인딩의 중복 선택이나 자동 복제는 하지 않는다. 기존 count out 소비자는
호환 return에 명시 대응한다. 원래 native C# 본문과 별도 원문 파일은 그대로다.

첫 호출의 out을 둘째 호출이 소비하고 둘째 out을 caller return이 소비한다.
명시 output 대응으로 옮겨진 뒤 입력도 원래 증거대로 투영해야 한다. 역순 후보가
같아야 하며 root caller의 기존 ref second 선언과 다른 입력·정확한 64비트 값·
설명·writer/실행 경로·부모/외부 원본을 보존한다. 새 값은 ref 셀로 만들지 않는다.

기본/독립 460px의 취소/재열기·Undo/Redo·미저장/저장 재시작·실패/재시도·
경합·응답 유실·프로젝트 전환·Review 취소/Confirm이 이번 종료 조건이다.
순서나 다른 계약 결합을 새 필수 조합으로 늘리지 않는다.

## 구현과 보호

Batch는 명시 body 계획과 원래 out→값이 있는 후보를 기존 whole-role 경계로
구분한다. 함수마다 한 역할 방향과 정확한 핀 식별자·타입·수·순서·반환 및 모든
caller/body 계획을 검사한다. 새 ref가 있는 이전 경로는 기존 저장소 선택을
계속 요구한다. 새 값은 기존 단일 검증기의 명시 값/바인딩·타입·중복/해제 검사를
사용한다. 기존 out 소비자는 호환 return에 명시 대응하고 다른 출력은 유지한다.

정확한 IsLift와 body/whole receipt가 있을 때만 implementationContext를
허용한다. 기존 WholeBody·RootContract·함수 사용처 검증기와 컴파일을 재사용한다.
모든 원래 선택을 먼저 검증한 뒤 내부 overlay를 합치며 MappingFor·ProjectOutputs·
Merge 및 원래 hash/CAS는 바꾸지 않는다. 중간 후보를 저장하거나 실제 source
변경을 사용자 동의로 재해석하지 않는다. 추가 노드/locals/alias·copy/private·
wrapper/native guard와 Review/Confirm을 유지한다. 제품 UI/bundle은 그대로다.

## 검증

변경 전 두 단일 out→값 후보가 유효하고 기존 그룹만 거절하는 실제 엔진 재현을
통과했다. 집중 10흐름·25확인과 영향 9흐름·26확인이 모두 통과했다.
기본/독립 화면의 편집 취소/재열기·명시 대응·Undo/Redo·미저장/저장 재시작·
Review 취소/Confirm, 저장 실패 뒤 재시도, 저장/조회 응답 유실 뒤 cold 결과
조회/중복 방지, 실제 peer 경합, 취소, 프로젝트 분리/오래된 창 차단과 마지막
불완전 대응 거절/Undo 재시도를 확인했다. 전체 graph/header/import·native/public
값·원문·원래 hash·정확한 값·실행 경로를 대조했다.

마지막 함수의 타입/순서/수/반환/역할·누락/중복 입력·해제/출력·본문/whole
receipt/컴파일·다른 문맥/copy 및 실제 source 경합은 전부 미적용이었다.
기존 ref→out과 out→ref는 각각 실제 플래그의 후보/독립 UI로 회귀했고, 값/ref·
입출력 정의·오버라이드 보호·출력 없는 경로·단일 out→값도 통과했다.
새 ZIP20개 파일 집합·권한·바이트/전체 SHA를 재검증했고 미해결 실패는 없다.
[집중·영향 근거](evidence/v536-information-shared-out-value/focused-verification.json)에
실제 실행/플래그/보존 근거를 기록한다. 독립 checkout·새 교차 패키지는 별도 기록한다.

## 정확한 잔여와 정상 금지

이번 exact whole-body out→값과 기존 ref 지원은 구분한다. 값→out·다른 입력/
출력 대응·공개 핀 순서·더 넓은 계약 결합, 일반 retained 그래프·선택 callee 의존·
native/mixed·중첩/private·whole/postCall·같은 계약 copy/상속/등록·소유 정보
property·scalar 밖 타입의 여러 closure 문맥은 기존 별도 수용 경계다.
정보 상세창에 없는 정렬 제어를 추가하지 않는다.

7행 원계약 copy 편집/배정과 9행 고급 함수 타입·표시명/native 식별자 분리,
I6/B2·A4~A6·M4/M11/M12는 별도 후속이다. 오버라이드 원계약 구조 변경 거절은
정상 보호이며 독립 계약 복제는 필수 범위에서 제외한다. 전체 v536 UI·실제
Windows/WebView2·모바일 기기·Library 전달은 미완료다. Helper 실제 작업은
UI 이후이고 이미지/협의/렌더 신규 backend는 이번 UI 복원 범위 밖이다.

| 구분 | 현재 판정 |
|---|---|
| 같은 계약 식별자의 직접 소유 whole-body out→값·명시 caller 대응 | 이번 지원 단위 완료 |
| 오버라이드의 원래 매개변수/출력 구조 변경 | 정상 금지, 미구현으로 세지 않음 |
| 독립 계약 복제/새 계약 ID와 정보 상세창의 새 정렬 제어 | 필수 범위에서 제외하거나 원본에 없는 추가 UI |
| 값→out·원본에서 가능한 순서 편집의 그룹 결합·위 별도 문맥 | 실제 남은 구현/수용 경계, 이번 완료와 구분 |
