# 정보 헤더와 명시 native 계약·본문의 한 저장

고정7/8행의 한 정보 창·한 Save에서 소유 정보의 설명·아이콘을 이미 지원하는 직접 소유
native 함수 계약·본문·공유 caller 변경과 함께 저장한다. 원래 `captureMixedCell`과
460px 상세창을 유지하고 새 UI나 계약 변환을 만들지 않는다.

기존 native 입력/역할/out/반환/지원 복합 타입 그룹의 명시 검증을 그대로 호출한다.
그룹은 함수2..8개, 설명과 아이콘 각각 최대 하나, 전체 최대10행이다. 표시 행은 기존
exact-key·중복·설명 길이·기호/로컬 이미지 검증을 받으며 새 source closure나 권한을 만들지 않는다.
지원 밖의 구조/정렬/생성·부모/외부 쓰기·opaque/private 계획을 표시 행으로 숨겨 허용하지 않는다.

설명·아이콘을 분류할 때만 분리하고 완전한 원래 선언은 기존 검증·Save receipt와 한 checkpoint CAS에 남긴다.
각 함수의 원래 signature·native 선언·본문·caller 대응을 독립 검증한 뒤 한 후보로 결합한다.
원래 hash·소유권·권한·Review/Confirm·최종 source lease를 유지하고 C#을 자동 재작성하지 않는다.
동일한 분류를 cold 헤더 읽기·guard 준비/검증·후속 설명 Save에도 사용한다.
원래 readGuards나 원본 기준을 새로 추정해 재기준화하지 않는다.

검사는 이전에 구현한 scalar out·반환의 명시 변경과 기존 호환 출력 대응에 owner 설명·아이콘을 함께 넣는다.
기존 body/ABI-only 후보와 단독 표시/각 함수는 게시본에서 이미 유효하지만 결합 Save는 거절됨을 재현한다.
수정 후 후보의 순서를 바꿔도 같은 결과이며 body/ABI-only와 비소유자 변경 footprint가 같아야 한다.
원본38→편집40 실행과 입력 ABI 타입 교체 그룹의 같은 owner 결합을 별도로 검증한다.
미완성/틀린 계약·본문/caller·중복/틀린 표시·구조/외부/알 수 없는 행은 전체 거절한다.
UI 취소·Undo/Redo·저장 실패/재시도·응답 유실·cold·owner 경합·늦은 설명과 후속 Save를 검사한다.

기존 계약·본문과 header-only 후속 Save, 원래 C# bytes와 import/override·공개 계약 및 authored layout을 유지한다.
새 종류/모듈/정보 ABI 정책은 없으며 정보별 struct·종류 enum·모듈 interface를 그대로 따른다.
같은 게시 세대의 저장/재편집 기준이다. 구 Reference reader와 이전 authoring으로의 migration/downgrade는 바꾸지 않는다.
남은 고정7/8행은 원래 UI의 다른 복합 계약/본문·속성 구조 편집, opaque/private 호출자의 명시 C# 계획,
선택 native callee 의존성과 기존 import/등록 외부 관측의 결합으로 대조한다.
원래 조작의 재현·지원/정상 거절 경계와 회귀 증거를 종료 기준으로 삼고 타입/문맥의 모든 조합을 필수로 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 초기 빈 화면 원인은 미확정이며 실제 Windows/WebView2·물리 기기·전체 UI 검증은 자동화와 구분한다.
