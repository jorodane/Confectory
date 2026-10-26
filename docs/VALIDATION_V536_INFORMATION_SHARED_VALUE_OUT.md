# 고정 8행: whole-body 값→out과 공유 호출자

기준은 `83f86488083f0db96a5810af587fbd4797d694b4`의 v536 정보/C#·명시 호출
대응 UI와 기존 단일 whole-body 계약 검증기다. 정확한 code/return lift의
값→out을 여러 직접 소유 함수와 ordinary shared caller의 한 후보/CAS에 결합한다.
이름·위치·타입·핀 수·반환 및 C# 원문을 유지한다.

## 원래 조작과 종료 조건

기존 C# 매개변수 `long nativeTotal`에 out을 직접 명시한다. 공개 amount/count와
nativeAmount/nativeTotal은 구분한다. 호출 계약 갱신에서 제거되는 count 입력의
원래 바인딩을 명시 해제하고 남는 amount 입력과 원래 return 출력을 유지한다.
새 count out은 자동 연결하거나 공개하지 않는다. 기존 caller의 ref second 선언과
첫 return→둘째 amount 연결·최종 return 경로도 보존한다.

원래 native 코드는 nativeTotal에 먼저 대입하므로 양쪽 역할에 유효하며 그대로
검증한다. 변환 전 C# 원문 파일도 보존한다. out 대입 전 읽는 본문은 컴파일에서
거절한다. callee의 기존 implicit profile은 out 셀을 지원하는 기존 ref profile로
검증되며, 다른 graph 상태를 임의로 바꾸지 않는다.

기본/독립 460px의 편집 취소/재열기·명시 해제·Undo/Redo·미저장/저장 재시작·
실패/경합/응답 유실/취소·프로젝트 전환·Review 취소/Confirm과 정확한 64비트
값·설명·원문·부모/외부 보존이 이번 종료 조건이다. 순서나 다른 문맥을 새 조합으로
확장하지 않는다.

## 구현과 보호

Batch는 명시 body 계획의 원래 값/out 전환을 whole-role 경계로 분류한다.
함수마다 한 역할 방향과 원래 핀 식별자·타입·수·순서·반환 및 모든 body/caller
증거가 필요하다. 값→out은 원래 값 핀의 해제 목록이 정확히 일치해야 하며 남는
입력과 원래 출력은 identity 대응만 허용한다. 해제 값·원래 source/hash/typed
import와 컴파일은 기존 단일 closure가 재검사한다.

exact IsLift·whole/body 계획일 때만 implementationContext를 허용한다. 기존
WholeBody/RootContract/함수 계약 검증기와 MappingFor·ProjectOutputs·Merge 및
원래 hash/CAS는 바꾸지 않는다. 모든 원래 선택을 먼저 증명한 뒤 내부 overlay를
합치고 전체 후보만 저장한다. 사용자 동의를 실제 변경된 source에 재적용하지
않는다. 추가 노드/locals/alias·copy/private/wrapper/native guard와 Review/Confirm을
유지하며 새 UI/권한/계약 ID나 C# 자동 재작성을 만들지 않는다.

## 검증

변경 전 두 단일 값→out 후보가 유효하고 기존 그룹만 거절하는 실제 엔진 재현을
통과했다. 집중10흐름·25확인과 영향9흐름·26확인이 모두 통과했다.
기본/독립 화면의 취소/재열기·명시 해제·Undo/Redo·미저장/저장 재시작·Review
취소/Confirm, 저장 실패 후 전체 미적용/입력 보존·재시도, 저장/조회 응답 유실 뒤
cold 결과 조회/중복 방지, 실제 peer 경합·취소·프로젝트 분리/오래된 창 차단·
마지막 불완전 대응 거절/Undo 재시도를 확인했다.

정방향/역순 후보의 원래 hash·전체 graph/header/import·native/public out·
profile·원문·정확한 값과 경로를 대조했다. 타입/순서/수/반환/역할·해제/출력/
본문/whole receipt/컴파일·다른 문맥/copy·물리 caller 경합은 전부 미적용이었다.
원래 ref→out과 out→값은 실제 플래그의 후보/독립 UI로 각각 회귀했다.
out→ref·입출력 정의·오버라이드 보호·출력 없는 경로·단일 값→out도 통과했다.
새 ZIP20개의 파일 집합·권한·전체 바이트/SHA를 재검증했고 미해결 실패는 없다.
[집중·영향 근거](evidence/v536-information-shared-value-out/focused-verification.json)에
실제 실행·플래그·보존 근거를 기록한다. 독립 checkout·새 교차 패키지는 별도 기록한다.

## 고정 목록의 판정

| 구분 | 현재 경계 |
|---|---|
| 직접 소유 exact whole-body 값→out·명시 원래 입력 해제/반환 보존 | 이번 지원 단위 완료 |
| 오버라이드의 원래 매개변수/출력 구조 변경 | 정상 금지, 미구현으로 세지 않음 |
| 독립 계약 복제/새 계약 ID·정보 상세창에 없는 정렬 제어 | 필수 제외 또는 원본 밖 추가 UI |
| 원본에서 가능한 순서 편집의 그룹 결합·다른 역할/바인딩/출력/계약 결합 | 별도 실제 잔여 |

일반 retained 그래프·선택 callee 의존·native/mixed·중첩/private·whole/postCall·
같은 계약 copy/상속/등록·소유 정보 property·scalar 밖 타입의 여러 closure 문맥은
기존 별도 수용 경계다. 7행 원계약 copy 편집/배정, 9행 고급 함수 타입·표시명/
native 식별자 분리, I6/B2·A4~A6·M4/M11/M12는 후속으로 유지한다.
전체 v536 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 미완료다.
Helper 실제 작업은 UI 이후이며 이미지/협의/렌더 신규 backend는 범위 밖이다.
