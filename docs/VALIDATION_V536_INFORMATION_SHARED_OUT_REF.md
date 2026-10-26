# 고정 8행: 전체 C# out→ref와 공유 호출자

기준은 `d9fc0234f056b3e1dd02f65966103549f725d9eb`의 기존 v536 정보/C#/
명시 호출 대응 UI 및 I5-6 고정 8행이다. 단일 whole-body 계약 검증기가 이미
지원하는 out→ref를 여러 직접 소유 함수와 공유 ordinary caller의 한 후보에
연결한다. 새 UI나 계약 ID, 오버라이드 계약 변경을 추가하지 않는다.

## 원래 조작과 이번 종료 기준

기존 정보 창에서 각 함수의 C# 매개변수 `out long nativeTotal`을
`ref long nativeTotal`로 직접 편집한다. 공개 amount/count와 nativeAmount/
nativeTotal은 구분한다. 이름·위치·타입·핀 수·반환과 C# 원문은 유지한다.

호출 계약 갱신에서는 새 count ref에 원래 amount 입력 바인딩의 저장소를 명시
선택한다. 같은 원래 바인딩은 한 번만 사용하므로 새 amount에는 사용자가 입력한
정확한 값 5를 선택한다. 기존 count out의 소비자는 호환되는 return에 명시
대응한다. 저장소·초기값·출력 대응이나 C# 본문을 자동 추정하지 않는다.

fixture의 첫 호출 amount는 caller의 원래 first 입력이다. 둘째 호출 amount는
첫 호출의 count out을 소비하며 caller의 return도 둘째 count out을 소비한다.
최종 후보는 두 out 소비를 각각 명시 return에 대응하고 그 저장소를 ref에
전달한다. caller의 기존 ref second 선언은 그대로 보존한다. 순서 반전에도
같은 결과여야 한다. 원래 native 코드는 out에 먼저 대입하므로 ref에도 유효하며
수정하지 않는다. 변환 전 C# 원문 파일도 보존한다.

기본/독립 460px 원본 화면의 취소·재열기·Undo/Redo·미저장/저장 재시작·실패/
경합/응답 유실·프로젝트 전환·Review 취소/Confirm과 정확한 64비트 값·설명·
원문·기존 연결·다른 입력 보존이 이번 종료 조건이다. 순서·타입·핀 수·반환
변경이나 다른 그래프 문맥을 새 조합으로 확장하지 않는다.

## 구현과 보호

`InformationFunctionBatch`는 기존 whole ref/out 분기에서 한 함수의 명시 방향과
원래 핀 식별자·타입·위치·수·반환 및 완전한 bodies/callers 선택을 검사한다.
out→ref의 새 ref는 같은 타입의 원래 입력 이름을 선택해야 한다. 원래 out
소비자는 호환 return에 대응하고 나머지 출력 식별자는 유지한다. 입력의 중복
선택·리터럴 ref·빠진 입력·잘못된 출력·임의 해제는 기존 단일 closure가 재검사한다.

선택된 callee의 implementationContext는 해당 명시 whole 계획과 정확한
`InformationFunctionRetained.IsLift`의 code/return 구조일 때만 허용한다.
원래 whole receipt·native/public/body/hash·컴파일과 입력 저장소 검사는 기존
`InformationFunctionWholeBody.Contract` 및 함수 계약 검증기를 재사용한다.
추가 노드·locals/alias·copy/private/wrapper/native target guard는 유지한다.

모든 원래 선택을 먼저 검증한 뒤 앞선 producer의 명시 출력 대응을 원래 graph
복제본에 투영하고 뒤 caller 선택을 합친다. `MappingFor`·`ProjectOutputs`·
`Merge`와 원래 hash/CAS 본문은 바꾸지 않는다. 내부 overlay hash를 실제 변경된
source에 대한 동의로 사용하지 않는다. 전체 후보만 저장하고 Review/Confirm을
유지한다. UI/bundle·권한·부모/외부 원본은 변경하지 않는다.

## 검증 기록

변경 전 두 단일 후보가 유효하고 기존 그룹만 거절하는 실제 엔진 재현을
확인했다. 최초 검사 파일의 문법 오류와 fixture typed import가 ref로 남아
원래 정보가 invalid였던 준비 오류를 구별하여 수정했다. 원래 실패 로그와
fixture ZIP은 보존하며 제품 결함이나 통과로 집계하지 않는다. 첫 빌드 명령의
읽기 전용 기본 CLI 홈 오류는 기존 승인된 임시 CLI 홈으로 수정했다.

집중 10흐름·25확인과 영향 9흐름·27확인이 통과했다. 정방향/역순 후보의
전체 업데이트·원래 hash와 최종 caller graph/header/import, callee native/public
ref·본문·원래 C# 파일·정확한 64비트 값·writer/실행 경로를 대조했다.

실제 기본/독립 화면의 C# 취소/재열기·명시 입력/출력 대응·Undo/Redo·미저장/
저장 재시작·Review 취소/Confirm을 통과했다. 저장 실패 후 재시도·저장/결과조회
응답 유실 뒤 cold receipt 조회/중복 적용 방지·실제 peer 경합·취소·프로젝트
분리와 오래된 창 제출 차단·마지막 함수의 불완전 대응 거절/Undo 재시도도 통과했다.

마지막 함수의 타입/역할/순서/핀 수/반환·매핑·중복/리터럴 저장소·해제/출력·
본문/whole receipt/컴파일·copy/다른 문맥 및 실제 caller source 경합은 전체
미적용이었다. 기존 ref→out 후보/독립 화면·값/ref·ref 이름·입출력 정의·
출력 없는 이전 경로·오버라이드 보호·이전 값/ref API·단일 out→ref를 회귀했다.

실행마다 실제 fixture 플래그를 기록했다. 준비 실패 증거 1개를 포함한 새 ZIP
21개의 파일 집합·권한·전체 바이트/SHA-256을 재검증했다. 원래 실패 로그/증거를
삭제하거나 통과로 집계하지 않았으며 미해결 제품 실패는 없다.
[집중·영향 근거](evidence/v536-information-shared-out-ref/focused-verification.json)에
각 실제 실행·초기 준비 오류·보존 근거를 구분한다. 독립 checkout과 새 교차
패키지의 최종 검증은 별도 기록한다.

## 정확한 잔여

이번 단위는 out→ref의 exact whole-body/명시 기존 입력 저장소·호환 return
소비 대응이다. 값/out 전환·다른 저장소/출력 대응·공개 순서 및 더 넓은 계약
결합과 일반 retained-storage·선택 callee 의존·native/mixed·중첩/private·
whole/postCall·같은 계약 copy/상속/등록·소유 정보 property·scalar 밖 타입의
그룹 문맥은 별도 수용 경계다. 정보 상세창에 없는 정렬 제어는 만들지 않는다.

7행의 원계약 copy 편집/배정 잔여와 9행 고급 함수 타입·표시명/native 식별자
분리, I6/B2·A4~A6·M4/M11/M12는 별도다. 오버라이드 원계약 구조 변경 거절은
정상 보호이며 독립 계약 복제는 필수 범위에서 제외한다. 전체 v536 UI·실제
Windows/WebView2·모바일 기기 및 Library 전달은 미완료다. Helper 실제 작업은
UI 이후이며 이미지/협의/렌더 신규 backend는 이 UI 복원 범위 밖이다.
