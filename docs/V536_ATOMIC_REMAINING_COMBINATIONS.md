# v536 원자적 편집의 고정 잔여 조합

새 기능 범위를 추가하는 목록이 아니다. 현재 연결된 저장 경로와 명시적으로 차단한 조합을 구별한다. 같은 ProjectPack의 원래 source closure/소유권·한 후보/CAS·입력 보존·명시적 Review/Confirm 원칙을 유지한다.

| 조합 | 현재 상태 | 다음 최소 완결 단위 |
| --- | --- | --- |
| 새 copy 하나 + 동일 owner 설명/기존 단일 primitive 값 | `VALIDATION_V536_MIXED_COPY.md`의 지원/검증 범위 | 기존 상태 보존. 일반 구조 편집까지 완료로 확대하지 않는다. |
| 소유 ordinary root의 모든 Blueprint target + 공유 값/ref import/wrapper ABI | `VALIDATION_V536_MULTI_TARGET_ABI.md`의 한정 지원 | 현재 ordinary/context 없는 code/소유 callee 범위만. opaque/상속·copy·등록 callee/multiple uses·whole-body context는 미지원. |
| 새 비공개 copy의 오래된 ABI | `VALIDATION_V536_PRIVATE_COPY_ABI.md`의 한정 지원 | 원래 immutable seed와 현재 callee/직접 등록 receipt를 분리한다. 단일 선택 Blueprint target·context 없는 code·같은 이름/순서/타입/out/반환의 값↔ref만 명시 갱신한다. 기존 최소 one-copy+설명/단일 primitive 혼합은 같은 후보/CAS에 결부한다. donor/부모/등록 원본·다른 target을 변경하지 않는다. whole-body C#/일반 ABI·다중 target copy는 미지원. |
| 여러 새 copy + owner 설명/기본값 | 지원, 이번 실제2copy 검증 | `VALIDATION_V536_WIDE_MIXED_SAVE.md`: 1~8 explicit new copy를 한 후보/CAS로 처리한다. 전체 intent+선언+source proof receipt이고 일부 목록은 전체 저장으로 인정하지 않는다. |
| 새 copy + 현재 원본 UI의 새 primitive 정의·부모·모듈 | 지원, 기존 schema 편집은 제외 | 새 소유 schema/uses/manifest와 owner 및 모든 copy를 한 후보로 검증한다. 최종 parent/modules에서 선택 copy가 여전히 요구되는지 재검사한다. 기존 속성의 이름/타입/아이콘/삭제, 새 compound schema·외부 소유 변경은 미구현이며 이를 지원으로 세지 않는다. |
| 새 copy + 복합/배열/참조 값·override/unset | 현재 typed widget 범위 지원 | 전체 typed root 값·정확한 숫자·순서·참조 및 최종 schema를 함께 검사한다. 서버는 중첩 typed path를 검증하되 겹치는 root/child 계획과 참조를 따라 다른 owner 쓰기는 거절한다. raw owner text를 받지 않는다. |
| 저장 copy ABI + 동일 owner 값/구조 편집 | 미지원 | 기존 exclusive `rebindCopyAbi`의 출처/독점 owner와 선언 변경을 함께 검증해야 한다. 새 copy 생성의 receipt로 대신하지 않는다. |
| 다중 target ABI + 새 copy/slot/owner 구조·값 편집 | 미지원 | 모든 영향 target/공용 import 및 copy/owner 계획의 공통 원래 snapshot·하나의 Review 그룹이 필요하다. 현재 단일 경로를 순서대로 Save하지 않는다. |
| Set/property 계획 + copy/slot/다중 target/별도 선언 편집 | 미지원 | 명시적 runtime/타입 의미와 관련 source 계획을 하나의 후보에 표현하기 전에는 분리 차단을 유지한다. field 값 변경과 local Set을 혼동하지 않는다. |
| dirty raw source + 새 private copy/primary owner typed 편집 | 한정 지원 | `VALIDATION_V536_RAW_COPY_SAVE.md`: 직접 소유 object 한 raw 입력과 기본 요소 창 및 새 copy1~8개만 한 후보/CAS·전체 receipt/Review 그룹에 결부한다. 원문 먼저 선택·source Save도 지원하며 실제2copy·실패/충돌/응답 유실/Undo/cold/Confirm을 검증했다. 여러 raw/독립 properties+copy·saved-copy ABI/기존 body·multi-target ABI/Set/property/다른 Blueprint 계획은 차단한다. |

이 조합들은 구현/검증 후에만 지원으로 바뀐다. 준비 상태·과거 계정 동의·현재 대화는 프로젝트 실행이나 자동 Confirm 권한이 아니다. 원본 v536 레이아웃, main/Android/reference ZIP과 사용자 자료는 유지한다. 사용자 결정 없이 정할 수 있는 기존 기술 계약은 새 승인 대기를 만들지 않고 구현하되, 실제 편집 시 변경 대상·비호환 remap·최종 반영 선택은 원본의 명시적 동작을 사용한다.

현재 UI 인벤토리와 유한 완료 조건은 `V536_WIDE_MIXED_SAVE_SCOPE.md`다. 임시 Save의 성공은 전체 초안 접수이며 C# 컴파일 성공/최종 파일 반영은 명시적 Confirm 결과로만 판단한다. 일반 ABI·모바일/조작 잔여의 완료 조건은 `V536_REMAINING_ACCEPTANCE.md`로 고정한다.
