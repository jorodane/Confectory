# v536 원자적 편집의 고정 잔여 조합

새 기능 범위를 추가하는 목록이 아니다. 현재 연결된 저장 경로와 명시적으로 차단한 조합을 구별한다. 같은 ProjectPack의 원래 source closure/소유권·한 후보/CAS·입력 보존·명시적 Review/Confirm 원칙을 유지한다.

| 조합 | 현재 상태 | 다음 최소 완결 단위 |
| --- | --- | --- |
| 새 copy 하나 + 동일 owner 설명/기존 단일 primitive 값 | `VALIDATION_V536_MIXED_COPY.md`의 지원/검증 범위 | 기존 상태 보존. 일반 구조 편집까지 완료로 확대하지 않는다. |
| 소유 ordinary root의 모든 Blueprint target + 공유 값/ref import/wrapper ABI | `VALIDATION_V536_MULTI_TARGET_ABI.md`의 한정 지원 | 현재 ordinary/context 없는 code/소유 callee 범위만. opaque/상속·copy·등록 callee/multiple uses·whole-body context는 미지원. |
| 새 비공개 copy의 오래된 ABI | `VALIDATION_V536_PRIVATE_COPY_ABI.md`의 한정 지원 | 원래 immutable seed와 현재 callee/직접 등록 receipt를 분리한다. 단일 선택 Blueprint target·context 없는 code·같은 이름/순서/타입/out/반환의 값↔ref만 명시 갱신한다. 기존 최소 one-copy+설명/단일 primitive 혼합은 같은 후보/CAS에 결부한다. donor/부모/등록 원본·다른 target을 변경하지 않는다. whole-body C#/일반 ABI·다중 target copy는 미지원. |
| 여러 새 copy + owner 설명/기본값 | 미지원 | 기존 다중 slot batch에 owner 변경을 한 번 적용하고 모든 copy/요구/제공/record를 최종 후보로 검사한다. 첫 slot만 저장하는 반복 호출을 금지한다. |
| 새 copy + 스키마/필드 정의·타입·추가/삭제·부모·모듈 | 미지원 | 구조 변경 후 상속/요구/제공/유효성의 전체 closure를 한 후보에 표현한다. 다른 객체의 정의나 외부 소유 원본을 쓰지 않는다. |
| 새 copy + 복합/배열/참조/중첩 값 또는 unset | 미지원 | 실제 typed value/참조 유효성·정확한 숫자·원래/이전 필드 보존을 같은 선언 후보에 결부한다. raw owner text를 받지 않는다. |
| 저장 copy ABI + 동일 owner 값/구조 편집 | 미지원 | 기존 exclusive `rebindCopyAbi`의 출처/독점 owner와 선언 변경을 함께 검증해야 한다. 새 copy 생성의 receipt로 대신하지 않는다. |
| 다중 target ABI + 새 copy/slot/owner 구조·값 편집 | 미지원 | 모든 영향 target/공용 import 및 copy/owner 계획의 공통 원래 snapshot·하나의 Review 그룹이 필요하다. 현재 단일 경로를 순서대로 Save하지 않는다. |
| Set/property 계획 + copy/slot/다중 target/별도 선언 편집 | 미지원 | 명시적 runtime/타입 의미와 관련 source 계획을 하나의 후보에 표현하기 전에는 분리 차단을 유지한다. field 값 변경과 local Set을 혼동하지 않는다. |
| dirty raw source + 위 결합 편집 | 미지원 | 사용자가 raw 편집 대상을 먼저 확인해야 한다. 서로 다른 편집기의 입력을 자동 합치거나 버리지 않는다. |

이 조합들은 구현/검증 후에만 지원으로 바뀐다. 준비 상태·과거 계정 동의·현재 대화는 프로젝트 실행이나 자동 Confirm 권한이 아니다. 원본 v536 레이아웃, main/Android/reference ZIP과 사용자 자료는 유지한다. 사용자 결정 없이 정할 수 있는 기존 기술 계약은 새 승인 대기를 만들지 않고 구현하되, 실제 편집 시 변경 대상·비호환 remap·최종 반영 선택은 원본의 명시적 동작을 사용한다.
