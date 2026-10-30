# v536 원래 잔여 대조와 다음 최소 단위

기준은 게시 `cc5e651`과 저장소 `196c605` v536 원본이다. 고정 9행·27개 UI 조작을
늘리지 않는다. 이전 감사표의 I5 설명에는 이미 완료한 독립 창·삭제/복구·순서가
남아 있으므로 최신 `V536_I5_6_REMAINING.md`와 각 검증 문서를 우선한다.

| 항목 | 원래 사용자 조작 | 현재 실제 차단/미연결 | 판정 |
|---|---|---|---|
| 7: same-contract copy | 기존 복사 구현을 편집·배정하고 원본 유지 | `BlueprintCopyAbi.Bind`의 같은 namespace 함수·단일 target 제한은 ABI receipt의 경계다. 모듈 화면의 외부 함수 copy 본문 재편집은 별도 owned slot 경로이며 정상 저장은 이미 동작했다. 쓰기 실패 시 입력 선삭제 결함을 기존 후보/CAS/receipt에 연결해 보완한다 | 단독 정보 소유 copy의 고정 계약 본문 저장은 [집중 수용](VALIDATION_V536_INFORMATION_EXTERNAL_COPY.md)으로 구분한다. 외부 함수를 구현하는 copy 내부 호출의 명시 ABI 갱신 receipt·import/alias 자체 변경·serial whitelist 밖 graph는 실제 잔여다. 기존 선택창은 target 하나를 복사하며 자동 전체 target 복제는 새 필수 요구로 늘리지 않는다 |
| 7: override | 원본 매개변수·출력 계약을 유지하고 구현 편집 | 부모/외부 쓰기와 타입·핀 수·역할·반환 구조 변경 거절 | 사용자 확정 정상 보호. 독립 계약 복제/새 ID는 필수 제외 |
| 8: 같은 창의 한 Save | 여러 함수에서 실제 편집한 내용을 함께 저장 | `InformationFunctionBatch.Begin`은 body 계획이 있으면 계약 편집으로 분류하고, native C# target 및 대부분 body 계획을 거절한다. 계약이 같은 C# 본문 2개도 거절됨 | 명확한 현재 UI 저장 연결 누락. 다음 최소 단위 |
| 8: 다른 계약/문맥 | 원본에서 제공하는 이름·타입·순서 편집과 명시 본문/연결을 보존 | batch의 direct leaf/call·code/return lift·native/private/copy/wrapper/서로 의존하는 callee guard | 각 실제 UI 흐름을 기준으로 축소 재현할 구현 경계. 가능한 C# 조합 전체를 새 수용 목록으로 만들지 않음 |
| 9: 함수 핀 타입 | 원본 타입 선택의 정보/참조/기능·외부 타입 선택 | `Parser.Types`/`Type`은 기본 CLR형과 배열만 받는다. 속성 schema의 typed datum 구현과 함수 계약은 별개 | 기존 명세의 문법/타입 및 UI 연결 미구현. 선택기를 켜는 것만으로 완료 아님 |
| 9: 표시명 | 한글·공백 표시명과 생성 코드의 식별자를 구별 | 현재 함수 pin name이 native parameter 식별자에 직접 사용됨 | 표시 metadata/기존 의미 대응 미구현. 별도 영구 pin ID 재설계는 승인되지 않았으며 추가하지 않음 |
| I6: 아이콘 | 원본 `editIconValue`의 기호/이모지/사용자 로컬 PNG/JPG/WebP 선택·적용 | 요소/속성/함수 icon callback이 unsupported, 모바일 pin icon은 disabled. 저장 metadata/후보 연결 부족 | 원본 UI 연결 잔여. AI 이미지 생성 provider와 분리 |
| B2: 실제 작업자 배지 | 선언별 실제 배정/변경 중 작업자 표시 | `WebState.csbody`에 이미 `assignedNode`, `supportingDraftIds`, `changedIds`, 상태·Helper가 있다. v666에서 실제 배정/관측 변경/지원 초안을 소유 선언·폴더·기본/독립 헤더로 연결함 | [B2 실제 지원/검증](VALIDATION_V666_WORKER_BADGES.md). 현재 로컬 소유 ProjectContext 범위이며 다른 사용자/그룹은 권한 backend 선행. 가짜 작업자 생성 금지 |
| A4–A6 | 등록/all-target, copy/상속, whole/forward/동일 callee 복수 사용의 명시 ABI 갱신 | 단일 receipt와 all-target 그룹 결합·모든 사용처/소유 source의 결합 검증이 부족 | 기존 요구의 결합 구현. 외부 권한 확대/자동 재작성과 구별 |
| M4 | 원본 async 전환 | 현재 sync 실행 profile와 await/저장 연결이 없음 | 실행 계약 구현 잔여. 버튼만 활성화하지 않음 |
| M11 | C# 동작→내부 graph | 전체 구현 C# lift 기반은 있으나 개별 node의 활성 구현/원문을 보존하는 전환 거래가 없음 | node 단위 변환 연결 잔여. 임의 C#→시각 로직 추론을 요구하지 않음 |
| M12 | 원본 root 실행 분기 | code/wrapper enum과 달리 root 분기의 실행/저장 계약 연결이 없음 | 원본 root 경계의 구현 잔여. 새 분기/루프 모델을 추가하지 않음 |

현재 순수 순열 adapter는 추측을 막기 위한 검증된 구현 경계다. 이름/타입/역할과
순서를 함께 편집하는 조작을 영구 UX 금지로 결정한 것이 아니다. 동일하게 현재
copy/group guard가 있다는 사실만으로 사용자 설계 결정이 필요하다고 분류하지 않는다.

다음 단위는 **직접 소유한 두 함수의 단일 native C# 본문만 편집하고, 계약·핀·
호출자·import는 그대로 한 Save**다. 원본의 기존 본문 편집창과 정보 저장 버튼을
사용한다. 기존 단일 본문 검증·compiler·원래 관측·후보/CAS·Review/Confirm을
재사용하고, 함수의 새로운 계약 대응·새 target·새 ID·레이아웃·권한을 추가하지 않는다.
실제 UI 거절 재현 → 정상·잘못된 마지막 본문·취소·Undo·실패·충돌·응답 유실·
재시작·명시 Confirm → 영향/clean checkout/교차 패키지 → 검증 코드·문서만 게시한다.

새 사용자 정책 결정은 이 단위에 없다. 실제 Windows/WebView2·모바일 기기와
Library 전달, 전체 UI 완료는 별개 미검증/미완료다. 기존 자료 정리는 하지 않으며
이번 검사 소유 임시 복사본의 승인된 종료 cleanup만 사용한다.

## 선정 단위의 후속 결과

직접 소유 단일 native C# 본문 두 개의 계약 불변 Save를 후보/CAS와 기존 화면에 연결했다. 집중12흐름31확인·영향8흐름25확인 및 실제 compiler Confirm이 통과했다([검증](VALIDATION_V536_INFORMATION_SHARED_BODIES.md)). 같은 graph의 재직렬화와 identity 출력 표현의 불필요한 정규화도 보완해 caller 원문을 보존한다. 원래 순열 adapter의 경계를 영구 정책으로 정하거나 새로운 핀 ID를 만들지 않았다. 7행 copy·8행 나머지 실제 문맥·9행 타입/표시명과 후속 UI는 위 표의 원래 범위로 남긴다.

로컬 same-contract copy가 이미 가진 native 별칭·읽기 전용 등록 import를 그대로 보존하는 본문 편집은 [별도 수용 기록](VALIDATION_V536_INFORMATION_COPY_IMPORTS.md)으로 구별한다. 변환된 Blueprint 부모의 import 일괄 거절만 관측된 source map과 고정 서명의 내부 연결로 보완한다. 외부 함수를 구현하는 copy/다중 target/별칭·import 자체 변경/다른 graph 문맥의 원래 잔여를 자동 완료로 세지 않는다.

등록 함수를 구현하는 정보 모듈 copy의 본문 재편집은 [현재 수용 기록](VALIDATION_V536_INFORMATION_EXTERNAL_COPY.md)에 별도로 정리한다. 외부 함수 ID라는 이유만으로 전체 본문 편집을 미구현으로 분류하지 않는다. Windows-only 선택본의 Linux compiler Confirm 거절은 target/common body 규칙의 정상 보호이며 독립 계약 복제 요구와 관계없다.
