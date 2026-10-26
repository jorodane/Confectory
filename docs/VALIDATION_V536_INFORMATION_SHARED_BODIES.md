# v536 같은 계약의 여러 C# 본문 저장

[원래 잔여 대조](V536_I5_6_RESIDUAL_RECONCILIATION.md)를 먼저 보고하고 선정한
고정 8행의 최소 단위다. 기존 정보 화면에서 두 자체 함수를 열어 각각 C# 본문을
직접 편집한 뒤 정보 창의 임시 저장을 한 번 누른다. 매개변수·반환·native 별칭·
핀·호출 서명·import를 바꾸지 않는다. 새 UI/레이아웃·핀 ID·실행 권한은 없다.

변경 전 두 단일 후보는 각각 유효하지만 그룹 후보와 실제 화면 Save는 거절됐다.
`InformationFunctionBatch`의 body 계획 분류/Blueprint whitelist가 원인이며 C#
언어의 제약이 아니다. `InformationFunctionBodyBatch`에서 public/native 서명과
명시 identity 대응·직접 소유 단일 C# target·보존할 ordinary caller를 확인한다.
원래 source에서 모든 단일 closure와 실제 compiler 검증을 먼저 마친 뒤 기존
Batch Merge/원래 hash/CAS를 사용한다. 중간 결과는 저장하지 않는다.

Batch의 별도 본문 경로 진입은 한 줄로 연결했다. 기존 ABI 그룹/MappingFor/Merge 및 단일 본문/copy/whole/root 검증기는 그대로다. ProjectOutputs와 단일 caller 대응은 같은 출력 identity일 때 원래 표현을 유지하는 조건을 각각 추가했다. 단일 계약의 저장 단계는 검증한 graph가 원래 graph와 완전히 같으면 원래 문자열을 유지하도록 보완했다. 기존 다중 출력 profile의 명시 return과 기본 profile의 암시 return 모두 보존한다. 기본 profile에서 허용되지 않는 명시 output 표기를 지원하는 것으로 확대하지 않는다. 바뀌지 않은 caller를 다시 직렬화하던 실제 불필요한 쓰기를 제거하며 원래 관측·hash·compiler 검사는 유지한다.
두 본문 중 마지막이 부적합하면 전체 후보가 실패하고 입력·기존 checkpoint와
물리 source는 유지된다. user text는 자동 재작성하지 않으며 별도 원문 파일,
정확한 64비트 값·주석/Unicode·입력 순서·공유 호출의 반환→입력·실행/최종 반환
경로·부모/외부 source와 권한을 보존한다. 같은 ABI의 본문 여러 개가 지원될 뿐,
새 계약 변경·copy/상속·private/whole/wrapper·다중 target 조합을 허용하지 않는다.
이는 현재 증명한 구현 경계이며 영구 UX 금지 정책이 아니다.

검토 그룹에는 읽기 의존성인 호출자도 포함될 수 있다. 순수 후보의 linked 변경은
선택한 두 native body이며, caller graph/header 전체 byte와 핀·import는 불변으로
대조한다. 검토 그룹에 caller가 있다는 이유로 caller 변경이라고 판단하지 않는다.
본문 편집이 없는 빈 계획은 정상 no-op일 수 있으므로 오류로 세지 않는다. 실제
누락된 원래 서명·해시·경로·불완전 C#과 compiler 오류를 거절 대상으로 검사한다.
화면의 고정 native return은 기존 표시명 `결과`와 구분하여 타입/입력 이름/순서를
비교한다. 초기 검사 기대값 3건은 실패 증거를 보존한 뒤 바로잡았다. 제품 검사를
완화하지 않았다.

실제 결과는 [집중 근거](evidence/v536-information-shared-bodies/focused-verification.json)에
기록한다. 제품 UI/manifest 75파일·74개 resource는 `cc5e651`과 byte 동일하다.
같은 계약 body 그룹은 기존 승인된 요구의 저장 연결이며 모든 C# 조합의 구현으로
범위를 늘린 것이 아니다. 순수 순열의 현재 guard를 영구 정책으로 만들지 않는다.

7행 same-contract copy의 미확정/외부/다중 target 편집·배정, 8행 이번 최소 단위 밖
실제 문맥/계약 결합, 9행 타입/표시명 및 I6/B2·A4~A6·M4/M11/M12는 고정 후속이다.
override는 원계약 유지·구현만 변경하며 독립 계약 복제/새 ID는 필수 제외한다.
B2는 실제 worker 데이터가 전부 없는 상태가 아니며 기존 WebState의 대상/변경 ID를
원본 배지와 연결하는 범위를 먼저 확인한다. 새 이미지/협의/렌더 backend는 범위 밖이다.
전체 UI 및 실제 Windows/WebView2·모바일 기기·Library 전달은 미완료/미검증이다.

집중 12흐름·31확인, 영향 8흐름·25확인이 통과했다. 기본/독립 창의 본문 편집·취소·Undo/Redo·미저장 cold·저장 cold·Review 취소/명시 Confirm, 실패 전체 미적용/재시도·응답 유실/결과 조회·중복 방지·실제 경합·프로젝트/오래된 창 차단·거절 후 Undo 재시도를 확인했다. 마지막 body/hash/path/원래 서명·구문/컴파일/경계 오류는 전부 미적용이며 원문을 보존한다. 암시 return과 기존 다중 출력 profile의 명시 return을 함께 포함한 실제 후보·독립 화면에서도 caller 원문 전체와 실행 경로를 유지했다. 초기 기대값/fixture 4건과 실제 재직렬화 결함의 실패 증거 및 통과한 재검증은 별도로 기록했으며 미해결 실패는 없다.
