# v536 넓은 혼합 Save의 고정 범위

`c03349b` 이후 작업. 원본 UI에 이미 있는 입력만 결합하며 아래 current-widget 조합을 한 후보/CAS로 연결했다. 실제 fixture 수용과 한계는 `VALIDATION_V536_WIDE_MIXED_SAVE.md`를 따른다.

| 현재 입력 | 이번 결합 대상 | 기존 의미/보호 |
| --- | --- | --- |
| 여러 새 private copy | 같은 owner의 서로 다른 요구 슬롯1~8개 | 원래 snapshot·source/target·import/wrapper/모든 record, provider 및 등록을 한 후보/CAS로 처리 |
| 설명·일반값 | 설명과 기존 scalar 값 | raw text/정확한 숫자 보존, 현재 owner hash/field contract 확인 |
| 복합·배열·참조 | 현재 typed widget의 전체 값/명시 override·순서·대상 선택·local reset | JsonDocument/typed JSON 사용, parent/다른 객체 쓰기 없음, 중첩 참조 owner 편집 불가 |
| 구조 | owned parent/Root·로컬 modules 선택 | 순환/상속/계약과 모든 기존 data의 최종 유효성 검사, 선택한 copy가 최종 요구 슬롯에 남아야 함 |
| 새 속성 | 원래 추가 행의 새 primitive 정의+기본값 | 기존 schema를 수정하지 않고 새 소유 schema/uses/등록을 같은 후보에 포함 |

기존 속성 타입/이름/아이콘/삭제, 새로운 compound schema 정의, 외부 schema·다른 소유자 수정은 현재 UI가 연결하지 않은 기능이라 추가하지 않는다. 일반 ABI remap·모바일 특수 문맥·Set/property 및 다른 소스 편집은 별도 고정 잔여다. 잘못된 마지막 copy/선언·CAS·저장 실패는 전체 미적용/입력 보존이어야 하며 Review/Confirm을 자동 실행하지 않는다. 실제 검사는 격리 fixture만 사용한다.

안전 예산은 owner 연산64개/새 primitive 정의32개/modules32개, copy1~8개 및 전체 receipt source64개다. 초과 시 쓰기 전에 전체 거절하며 일부 저장하지 않는다. 실제 수용 fixture는2copy이며 모든 최대치 조합을 전수 검증한 것은 아니다.
