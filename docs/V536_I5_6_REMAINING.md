# I5-6: 지원 경로와 남은 계약 편집

기준은 `196c605`의 v536 ZIP, `openOwnFunctionPopover`, `renderFunctionSignatureEditor`, `renderFeatureDefinition`과 기존 native 함수 계약이다. 원본 상세창은 입력/출력의 이름·타입·추가/삭제를 제공한다. 순서 조작은 `propertyStyle`인 Blueprint 정의에서 제공하며 정보 상세창에 새 드래그 제어를 만들지 않는다. 값/ref/out은 기존 native 계약과 구현 편집 경계를 유지한다. 기능 목록의 순서(I5-5)는 매개변수 순서와 별개다.

이번 수용 범위는 직접 소유한 **함수 하나**의 명시적 기존 핀 대응이다. 일반 Blueprint 루트와 실제 호출 입력 이름을 함께 바꾸고, 내부 code 노드의 매개변수·C# 내용은 유지한다. 동일 이름/타입/역할 집합의 순열은 C# 구현의 자체 매개변수 이름을 보존하고, 다중 target·소유 module require·안전한 후처리도 한 후보에 넣는다. 기본/독립 정보 창에서 입력 이름 편집과 저장/복원을 확인했다. 다중 target/순열/후처리 검사는 순수 후보와 실제 API/컴파일러 경로이며 원본 정보 상세창에 매개변수 정렬 UI를 추가했다는 뜻이 아니다.

| 화면과 사용자 조작 | 현재 결과 | 남은 연결/완료 기준 |
|---|---|---|
| 함수 상세창에서 연결된 입력을 다른 타입으로 바꾸거나 삭제한 뒤 저장 | 미사용 입력 삭제와 일반 code/call 값 인자의 직접 연결과 수식 전체, Set/export 값, root 별칭 저장소·exit의 삭제/타입 변경 대응을 명시 후보에 연결했다(VALIDATION_V536_INFORMATION_VALUE_USES.md). C# 매개변수/본문은 유지한다 | 1행의 기존 값 입력 문맥은 property 수신자/쓰기·branch/enum/After까지 연결했다(VALIDATION_V536_INFORMATION_PROPERTY_CALLS.md, V536_I5_6_ROW1_SCOPE.md). 별칭은 같은 타입의 현재 root 저장소만 명시 선택하며 값 복사로 바꾸지 않는다. callee/C# 형식 매개변수·nested/whole-body/ref 역할 변경은 4~7행의 별도 경계다. 함수 밖 계약이나 타입을 추측하지 않는다. 삭제/추가에서 기존 caller 저장소 재사용도 지원하며 모순된 동시 해제는 거절한다. 자동 연결 삭제는 없다. |
| 함수 상세창에서 입력을 추가하고, 사용 중인 호출에도 새 값을 전달 | 일반 scalar의 명시 값/기존 caller 바인딩 선택을 같은 후보/CAS에 연결했다(VALIDATION_V536_INFORMATION_INPUTS.md). 빠진 호출/값은 전체 거절 | 임의 기본값·새 저장소를 만들지 않는다. C#/중첩/복잡한 ref/out은 별도 경계다. |
| 함수 상세창에서 출력 이름·타입·추가/삭제 또는 반환 타입을 바꾸고 사용처 유지 | 일반 out 이름 변경은 기본/독립 상세창에서 내보내기·consumer·공개 metadata와 함께 검증했다(VALIDATION_V536_INFORMATION_OUT.md). 현재 native 식별자 문법 범위다. 기존 out/반환의 단일 숫자 출력 타입 변경을 exact-typed 현재 root 입력과 caller 출력의 명시 대응으로 연결했다(VALIDATION_V536_INFORMATION_OUTPUT_TYPES.md) | 출력 추가/전체 배치 삭제·양방향 void 반환 전환을 명시 값/삽입 위치·caller outputs와 같은 후보에 연결했다(VALIDATION_V536_INFORMATION_OUTPUT_DEFINITIONS.md). 다중 writer/여러 출력 동시·비숫자 출력의 타입 변경과 exact-typed root/노드 결과/지역값·명시 리터럴을 연결했다(VALIDATION_V536_INFORMATION_OUTPUT_REMAP.md). 출력 이름·타입·추가를 같은 후보에 묶고 모든 원래 writer/exit와 소비자 대응을 검증한다. 입력 계약 변경+출력 정의/타입 변경도 같은 원래 graph 증거·한 후보/CAS에 결합했다(VALIDATION_V536_INFORMATION_IO_CONTRACTS.md). 직접 소유 일반 Blueprint/현재 기본형·배열 선택기의 3행 지원 경로 완료. C#·중첩·전체 저장소·출처·여러 함수·고급 핀/표시명은 4~9행으로 구별한다. |
| 원본 구현/C# 편집창에서 새 본문을 명시하고 함수의 이름/타입/역할도 바꾸기 | 직접 소유 native C# target 및 C# 호출자/일반 Blueprint 호출자의 명시 본문·계약을 같은 후보/CAS에서 검증·저장한다(VALIDATION_V536_INFORMATION_CSHARP_CONTENT.md). 자동 재작성은 없다 | native-only 및 혼합 Blueprint/C# target을 각 원래 증거·명시 본문/핀 대응·한 후보/CAS에 결합했다(VALIDATION_V536_INFORMATION_MIXED_TARGETS.md). 현재 기본형/배열·직접 소유 native body/직접 C# 및 일반 Blueprint caller라는 고정 4행 지원 경계를 마감한다. 자동 C# 재작성은 하지 않는다. 등록/상속/copy·중첩·전체 저장소·고급 타입은 각 5~9행과 구분한다. 기존 source/서명/현재 계약의 명시 증거·컴파일·입력 보존 없이는 허용하지 않는다. |
| 내부 흐름에 들어가 중첩 그래프 안의 호출 계약을 바꾸기 | 직접 소유 qualified private 호출의 명시 입력·출력 대응과 일반 next C#·serial/enum 후처리를 같은 후보/CAS에 연결했다. 부모/형제와 동명 leaf를 구분한다(V536_I5_6_NESTED_SCOPE.md) | 부모 private 계약·저장소·계층별 명시 출력과 추가 계산/별칭을 한 후보에 연결했다. private branch/switch 수동 C#/helpers 및 별도 private enum 저장도 연결한다. frame마다 forwarded 자식 하나인 직접 소유 계층이 현재 지원 경계이며 같은 frame의 여러 forwarded 자식 계약 동시 변경은 남았다(V536_I5_6_NESTED_SCOPE.md). copy/등록 receipt는 7행이다. 기존 경계를 넘어 자동 추정하지 않는다. 5행 전체 완료와 이번 지원 단위를 구분한다. |
| 전체 본문 문맥/호출자 저장소를 쓰는 구현의 값/ref/out 변경 | 직접 소유·import 없는 원래 전체 본문 lift의 명시 C#·타입/핀 추가삭제·값/ref/out 역할·반환 타입/void 전환을 일반 caller의 저장소·출력 대응과 한 후보/CAS에 연결했다. V536_I5_6_WHOLE_CONTRACT_SCOPE.md, VALIDATION_V536_INFORMATION_WHOLE_CONTRACT.md에 검증 범위를 기록한다 | 프로젝트 소유 callee를 import하는 직접 소유 whole-body caller는 자신의 ABI·저장소를 유지한 수동 C#·import/context 갱신을 같은 후보에 연결했다(VALIDATION_V536_INFORMATION_CONTEXTS.md). 추가 일반 노드·locals/별칭의 callee, 별도 forwardCallerStorage code/call·serial/enum postCall의 명시 갱신을 같은 후보/CAS에 연결했다(V536_I5_6_RETAINED_SCOPE.md, VALIDATION_V536_INFORMATION_RETAINED.md). 원문·실제 셀/별칭·현재 import·호환 출력 대응을 검증한다. 등록/상속/copy caller는 7행 별도다. ref는 현재 기존 call 바인딩을 명시 선택해야 하며 임의 셀·별칭을 만들지 않는다. 고정 6행의 직접 소유 지원 경계는 위 수용 문서로 마감하며 nested/copy/등록·여러 함수·고급 타입은 5/7/8/9행이다. |
| 등록 팩 함수가 함께 호출되는 구현·출처가 있는 복사 구현의 전체 계약 변경 | 이번 검증은 프로젝트 소유 callable closure에 한정한다. 등록 계약이 제공되지 않으면 그래프 검증이 거절한다. 복사 provenance/등록 callable의 이 경로 수용은 미검증 | 기존 등록 callable의 읽기 전용 receipt와 `BlueprintCopyAbi`의 소유/출처 기준을 결합한다. donor·부모·외부 팩을 수정하지 않는다. |
| 정보 한 창에서 연결된 함수 둘 이상의 계약을 바꾸고 한 번에 저장 | 두 번째 연결 closure는 명시적으로 거절, 모든 입력 유지 | 모든 새 함수 계약을 먼저 확정한 검증 후보 위에서 공유 caller의 remap을 합성한 뒤 단일 CAS로 저장한다. 현재는 함수 하나씩 저장한다. |
| 상세창에서 정보/참조/외부 타입을 함수 핀 타입으로 선택 | 현재 상세 타입 선택기는 기본형/배열 범위다 | 기존 타입 catalogue·native 함수 타입 검증에 연결할 어댑터가 남았다. 일반 속성 타입 편집(I1~I3)의 완료와 혼동하지 않는다. |

이 표는 기존 I5-6 완료 조건의 세부 조작이다. 어려운 구현을 사용자 설계 결정으로 돌리거나 새 기능 요구로 분류하지 않는다. 서로 다른 새 조합을 추가해 완료 경계를 넓히지 않는다.

일반 out 이름 변경과 설명/입력 이름의 같은 후보 저장은 수용 검증을 마쳤다. 상세 표시명과 native 식별자의 분리(한글·공백 이름), 출력 타입/추가삭제·반환 변경은 전체 완료로 처리하지 않는다. 일반 입력 추가/미사용 입력 삭제와 caller의 명시 값·기존 바인딩/해제의 첫 단위를 연결했다. 정확한 수용/제한은 VALIDATION_V536_INFORMATION_INPUTS.md에 기록한다. 직접 code 값 인자의 사용 중인 입력 삭제·타입 변경 및 삭제/추가 혼합 대응도 명시 후보에 연결했다(VALIDATION_V536_INFORMATION_INPUT_REPLACEMENTS.md). 일반 call의 직접 root 값 인자는 기존 선택창과 후보/CAS에 연결했다. 수식/복합 바인딩 전체 값, root 별칭 저장소, Set/export·exit의 명시 대체도 연결했다(VALIDATION_V536_INFORMATION_VALUE_USES.md). 수식의 부분식 자동 재작성과 다른 저장소 역할의 추측은 하지 않는다. 기존 `BlueprintCallAbi.remap.inputs`의 선택을 사용하고, 새 값을 추정하거나 연결을 자동 삭제하지 않는다. 출력/반환 변경도 기존 내보내기·호출 매핑을 제출할 수 있을 때만 다음 후보로 다룬다. C#·중첩·전체 저장소 역할은 별도 명시 후보 없이 허용하지 않는다.

I5-1~5 지원 경로는 유지한다. I5-6 전체와 v536 전체 UI는 아직 완료가 아니다. I6/B2 및 A4~A6/M4/M11/M12, Helper 실제 작업은 기존 별도 후속이다.


## 고정 잔여의 우선순위와 종료 기준

위 9행의 범위를 유지한다. 아래 순서는 새 요구나 새로운 조합 목록이 아니라 그 9행을 마감할 순서다.

1. 입력 사용처: 일반 code/call의 직접 값·수식 전체, root alias 저장소·Set 값·exit/내보내기의 이번 단위를 마감했다. 표 1행의 property 수신자/쓰기 및 기존 branch/enum/After 값 인자도 고정 수용 범위로 마감했다. callee/C# 형식 매개변수·nested/whole-body/ref 역할 변경은 각 4~7행에 유지한다. 수식의 일부를 추측해 지우거나 별칭을 값 스냅샷으로 바꾸지 않는다. 출력 타입·추가삭제·반환 편집도 기존 output/remap 후보로 마감한다(표 1~3행).
2. 사용자가 명시 편집한 C# 원문과 전체 본문/저장소 역할(ref/out)을 기존 계약에 결합한다. 자동 소스 치환은 하지 않는다(4·6행).
3. 중첩 그래프 private path, 소유 복사본·등록 callable receipt, 함수 둘 이상의 공유 caller 후보를 순서대로 결합한다. 외부 원본은 변경하지 않는다(5·7·8행).
4. 상세창의 정보/참조/외부 타입 선택과 원래 표시명/native 식별자 경계를 마감한다(9행 및 기존 표시명 제한).

각 단위는 원본 UI에서 정상/취소/Undo·재시도/실패·충돌/응답 유실/재시작/명시적 Review·Confirm 및 해당 원문·입력·소유권 보존을 확인한 뒤 닫는다. 같은 기반에서 영향 없는 검사 조합을 계속 추가하지 않는다. **I5-6 전체 완료 기준은 위 표의 원본 사용자 조작이 모두 실제 경로로 연결·검증되는 것**이다. 안전한 거절만 구현한 항목은 완료가 아니다. 범위를 명시적으로 바꾸지 않는 한 이를 충족한 뒤 I6 아이콘/B2 배지, A4~A6/M4/M11/M12의 기존 후속으로 넘어간다. 실제 Windows·모바일 실행, 이미지 생성/협의/렌더 새 backend, Helper 작업 도구는 이 완료 판단과 분리한다.
