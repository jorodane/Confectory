# 소유 자식 생성·등록과 명시 함수 계획의 공동 저장

고정 7/8행에서 원래 소유 정의 UI가 제공하는 두 생성 흐름을 다룬다.
첫째는 새 단일 소유 복합 속성에 중첩 자식을 만드는 흐름이고, 둘째는 기존 단일 소유
트리에 새 소유 자식을 추가하는 흐름이다. 같은 정보 창에서 두 함수의 명시 native
계약·직접 작성한 본문·공유 caller 대응·정보 설명/아이콘과 한 Save로 결합한다.
기존 [자식 구조 편집](V666_OWNED_STRUCTURE.md)의 원본 버전은 그대로 보존한다.

원래 OwnedInformationDefinitions의 ID·owner/path marker·타입/값·중복·사용처 검증과
새 schema 생성·등록을 재사용한다. 새 자식 ID는 원래 ChildId(owner, native key path)로
결정한다. 표시명이나 순서로 신원을 새로 추정하거나 ordinary/named 정의를 소유하지 않는다.
원래 source map에 없는, 명시 tree의 owned 노드만 새 source다. 생성 후보와 등록을 원래
검증기로 재생해 exact ID·경로·marker·text·등록 hash를 대조한다. membership 계산은 권한 부여가 아니다.

기존 자식은 캡처한 원래 hash, 새 자식은 missing baseline·빈 original·정확한 creationOwner를
유지한다. 두 종류를 기존 version3 nativeBodyOwnerEdits/nativeBodyOwnerReads/readGuards와
동일한 원자 그룹·Review/Confirm·최종 CAS로 처리한다. 새 receipt 필드나 문법·자동 migration은 없다.
본문/graph는 선언 registry에 넣지 않으며 원래 전체 compiler·Save 후보에는 그대로 전달한다.

생성 뒤 늦게 입력한 이름·정확한 값은 cold 후 명시 Save한다. 같은 필드 ID·계층·타입만
허용하며, 현재 draft와 sources를 검증해도 원래 null 생성 계약 또는 기존 계약/hash/source
map 및 missing leases를 바꾸지 않는다. 저장한 새 source가 unit에서 빠지거나 draft/proof·
owner/path/marker·등록·원래 읽기 집합이 바뀌면 전체 거절한다. 파일·디렉터리가 생성 목적지를
차지하면 Save/Confirm을 거절하며 peer와 원래 source·등록·checkpoint를 보존해야 한다.

검증 조작은 새 root+내부 두 schema 생성과 기존 tree+새 child 한 schema 추가다.
원래 정확64 기본값·필드/참조 ID·CRLF 주석·명명 정의·부모·외부 원본·선택 밖 C#을 보존하고
명시한 두 native 계획만 적용한다. 기존 내부 source의 bytes·inode·mode·mtime도 확인한다.
함수 계약은 자동 변환하지 않고 정보별 struct·종류 enum·모듈 interface 및 명시 async 전환
전 sync caller 오류·공개 override·권한·authored layout을 유지한다.

두 생성 흐름의 정상/거절·원래 UI·Undo/Redo·취소·실패/재시도·응답 유실·cold·경합·
늦은 입력/후속 Save·프로젝트 전환·원본/생성 목적지의 Review 이후 충돌, LF/CRLF 새
restore/build·새 package/전체 추출 복원이 통과하면 이 단위를 닫는다. 기존 구조·compound·
field/typed-value/scalar receipt·사용처 보호도 회귀 검증한다. root cardinality/type 전환이나
임의 leaf/type/context 조합을 새 의무로 확장하지 않는다.

고정 잔여는 opaque/private 명시 C# 계획과 소유 callee·기존 import/등록 외부 원본 관측의
결합, 별도 원래 계약/전환 경계다. M11/M12/M4는 회귀 없이 다시 열지 않는다. main은
사용자 검토/merge에 남긴다. 같은 게시 세대의 authoring/runtime을 사용하며 구 reader의
새 미확정 생성 초안 downgrade는 보장하지 않는다. 실제 Windows/WebView2·물리 기기·
OS IME·GPU/audio·전체 UI 전수는 자동화와 구분하며 초기 빈 화면 원인은 미확정이다.

이 소유 자식 생성·등록·native 계약 공동 저장 단위의 [최종 신규 41·재사용 14·합계 55 검증과 보관](VALIDATION_V666_OWNED_CREATION.md)을 마쳤다.
