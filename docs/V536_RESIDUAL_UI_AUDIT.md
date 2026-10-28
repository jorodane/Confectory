# v536 잔여 화면·조작의 명시적 경계

기준: `4102f2f`와 A7/M6 수용 수정. 기존 표는 실제 25행이었다. M3/M5에 섞였던 두 계약 제한을 M11/M12로 분리해 **27개 조작**으로 고정한다. 새 기능을 추가한 목록이 아니다.

원본 `196c605`의 v536 `app.js`/`blueprint.js`. `VALIDATION_V536_UI_ACCEPTANCE.md`의 포괄적인 잔여 표현을 아래 조작으로 분해한다. **미연결**, **미검증**, **지원 제한**, **백엔드 부재**를 서로 바꾸어 쓰지 않는다. 원본 프로토타입의 메모리상 데모 동작이 컴파일/저장 계약의 존재를 증명하지 않는다. 표의 현재 결과가 소스 판독이면 실제 기기 재현이라고 표시하지 않는다.

## ABI: 새로 확장할 조합과 현재 UI 수용의 구분

| ID·화면/조작 | 정상 기대 결과 | 현재 결과·분류·근거 |
| --- | --- | --- |
| A1. 직접 소유 호출/슬롯에서 변경된 호출의 `원본 계약 갱신` → 핀 대응 → 저장/확정 | 선택한 입력/출력/import/소비자만 함께 갱신. 취소·비호환 시 입력 보존 | **지원·수용 완료**. 일반 ABI 및 직전 copy/owned2target 실제 검사. 이름·순서·타입/out/반환 변경 전체를 미완료로 반복 표기하지 않는다. |
| A2. 직접 등록 callable을 쓰는 저장 copy에서 같은 갱신 | 외부 팩/부모/원본 불변, caller만 명시적으로 갱신 | **지원·수용 완료**. 직전 `abi-copy.log` 5 PASS. 새 private copy 단일 target도 기존 `VALIDATION_V536_GENERAL_ABI.md`의 owned/registered 각각 UI5 PASS 범위다. |
| A3. 소유 ordinary 구현의 common/windows 두 target에서 갱신 | 두 graph·공통 import·code record를 한 후보/CAS·Review 그룹으로 갱신 | **지원·수용 완료**. 직전 `abi-multiple.log` 5 PASS. 두 target 검사이며 모든 가능한 target 수를 전수 검사했다고 주장하지 않는다. |
| A4. **등록** callable + 여러 caller target에서 갱신 | 등록 receipt까지 포함한 모든 대상의 원자 후보가 필요 | **일반 직접 소유 target 연결·수용, 나머지 문맥은 구분**. 기존 all-Blueprint 구현의 common/windows 두 target에서 각각 한 등록 wrapped call을 명시 대응하고, 외부 선언/receipt는 caller의 읽기 전용 snapshot으로 보관한다. Save/Review/Confirm 재조회·소유 관측 파일의 최종 CAS와 전체 후보를 결합한다. 외부 ID는 owned write unit이 아니다. 2–8 target 기존 기반을 유지하되 실제 표본은 둘이며 copy/상속은 A5, 여러 use/opaque는 A6의 동일 잔여다. [검증·정확한 제한](VALIDATION_V536_REGISTERED_TARGET_ABI.md). |
| A5. copy의 여러 target 또는 상속된 구현 대상으로 일괄 갱신 | immutable seed/부모/각 target 출처를 보존한 전체 후보 | **명시 배정 두 copy의 결합 수용 / 나머지 제한 구분**. 서로 다른 owner가 common/windows를 각각 선택한 단일-target copy 두 개와 한 소유 callee의 계약/수동 본문을 기존 후보/CAS·Review/Confirm에 결합한다. 검토 뒤 read-only 배정 변경도 최종 CAS로 거절한다. [copy target 검증](VALIDATION_V536_COPY_TARGET_CANDIDATE.md)의 표본만 완료이며, 하나의 copy에 모든 target을 자동 복제하는 정책은 추가하지 않는다. 상속 group/새 copy 등록 복수 use·별도 frame/opaque closure는 해당 기존 잔여와 구분한다. |
| A6. whole-body/opaque 문맥·forwarded storage 또는 같은 callee의 복수 사용에서 갱신 | 모든 사용처와 본문 의미를 명시적으로 검증, 임의 재작성 금지 | **부분 지원·고정 잔여**. ordinary wrapped 복수 use의 owned-callee 및 저장 copy Root/private·등록 단일 target closure는 후속 연결이 완료됐다. 새 owned copy 초안의 복수 use도 별도 완료 증거가 있다. 별도 frame 계약/본문과 opaque/whole-body closure, 새 copy의 등록 복수 use는 단일 target·명시 대응/receipt 보관과 cold/Review/Confirm으로 연결했다([검증](VALIDATION_V536_PENDING_REGISTERED_CLOSURE.md)). 다중 target과 다른 frame 계약/본문·opaque 결합은 각 기존 완료 범위와 구별한다. 현재 ordinary all-target group은 target당 한 선택 call이다. 오래된 단일-call 거절 조건을 이미 완료한 경로의 미구현 근거로 재사용하지 않으며 [최신 경계](V536_ROW7_REMAINING_BOUNDARY.md)를 따른다. |
| A7. 모바일 카드에서 `그래프 ↗` → `보기/미니맵 펼치기` → 기존 갱신 → 카드/저장/재시작/Confirm | 동일 caller/선택/입력을 유지하며 기존 갱신을 사용할 수 있음 | **지원·수용 완료(등록 copy 모바일6)**. 실제 Files→슬롯 카드→Graph/View/minimap→기존 명시 갱신을 완주했다. 빈 지도 재그리기 누락을 수정했다. raw 선택의 cold/취소, 잘못된 대응 전체 미적용과 활성 창 Undo 재선택, Home 재진입·retired callback 차단, 한 후보 Save·Review 취소/compiler Confirm을 확인했다. 외부 팩/부모/원문은 불변이다. A4–A6까지 확대하지 않는다. |

## 모바일: 원본에 있는 정확한 조작

| ID·화면/조작 | 원본/정상 기대 결과 | 현재 결과·분류·근거 |
| --- | --- | --- |
| M1. 그래프 모드 `보기 → 영역 선택 모드` → 빈 배경 드래그 | 원본 `bp-selection-box`로 여러 노드 선택, 이후 선택 메뉴·이동 | **지원·수용 완료(선택 renderer6)**. 기존 보기 메뉴·`bp-selection-box`·modifier/배경 선택을 연결했다. 원본 CSS를 유지하며 입력/entry/종료 벽을 선택 대상으로 오인하지 않는다. 실제 backend 호출 없는 개인 선택 상태다. |
| M2. 여러 노드 선택 → 함께 이동/선택 삭제 | 원본 선택 집합에만 적용, 취소 시 복원; 삭제는 한 검증 후보 | **지원·수용 완료(범위 한정)**. 선택 집합 이동·좌표 Undo/Redo, 직접 소유 ordinary root의 연결 없는 다중 삭제를 한 authorBatch/CAS·receipt로 저장한다. 연결/값 참조가 남은 노드는 전체 거절한다. private/slot/copy의 다중 삭제는 순차 Save로 대체하지 않고 차단한다. 원본 파일은 명시적 Confirm 전 보존한다. |
| M3. 동작 카드 → `내부 흐름 편집` | 원본 `api.internal(node,false)`로 해당 노드의 내부 흐름 진입·복귀 | **기존 native 중첩 graph 수용 완료(실제 엔진4)**. `kind=graph`를 원본 동작 카드에 렌더하고 내부 흐름·breadcrumb·상위 복귀를 연결했다. root/private path별 입력과 위치·Undo 문맥을 분리하고 desktop/mobile 전환·cold·코드 취소/Save·compiler Confirm을 확인했다. C# code→graph 변환은 M11로 분리한다. 부모/자식 양쪽의 미저장 쓰기는 자동 병합하지 않고 기존 보호로 막는다. |
| M4. 동작 카드 → `비동기 함수로 전환` | 원본은 정의의 async 상태를 전환해 표시 | **대응 실행 계약 부재에 따른 제한**. 현재 버튼 disabled. 기존 지원 프로파일은 sync-acyclic 계열이며 이 원본 async 플래그와 await/실행·저장 계약의 매핑이 없다. 버튼만 켜거나 새 async 실행 모델을 이번 수용에 추가하지 않는다. |
| M5. 소유 code/wrapper 동작 상세의 분기 목록 | 원본 executionOutputs의 이름/순서/추가·삭제를 편집 | **소유 code/wrapper enum 패널 연결·수용 완료(wrapper5/code3)**. 원본 분기 행/이름 편집/추가/순서·삭제 UI를 기존 enum 후보에 연결했다. 숫자와 stable ID·연결·본문을 유지한다. 연결된 삭제는 거절, 잘못된 이름 원문은 cold까지 보관하며 Escape/Undo/Redo·Save/Review취소/Confirm을 확인했다. 별도 root 실행 출력은 M12다. |
| M6. 출력 정의 탭의 공유 이름 변경 / 한 배치 inspector의 별도 이름 | 원본의 공유 정의 rename과 배치별 선택을 구별 | **공유 정의 탭 수용 완료(실제 엔진4) / 배치 inspector 제한 유지**. 두 export가 공유하는 out 정의의 이름 변경·Undo/Redo·cold·저장/Review 취소/compiler Confirm을 확인했다. 정의 remap 후 배치 guard가 옛 ID와 비교하던 결함을 고쳤다. 두 64비트 값·실행 경로를 유지하고 거절된 배치 raw 이름 취소도 보존한다. 고정 native return rename은 M7이다. |
| M7. native `return`/종료 카드의 출력 이름 변경 | ABI identity와 표시 별칭을 구별해야 함 | **의도된 native 계약 보호**. 고정 return 이름/종료 선택은 readonly. 별도의 표시 별칭 편집 계약은 없다. ‘return을 자유롭게 rename하지 못함’을 기존 native Save 결함으로 표시하지 않는다. |
| M8. 새 출력 이름을 빈 값/불완전 이름으로 둔 뒤 Save | 개인 입력은 보관하고 안정된 출력 identity 없이 최종 적용하지 않음 | **명시적 Save 제한**. raw draft를 보관하며 이름을 정하기 전 저장을 차단한다. 기존 새 정의+배치+값의 완전한 이름은 Save/Confirm 가능하다. 개인 draft와 compiler가 받을 이름 없는 최종 출력을 구분한다. |
| M9. 입력/출력 카드의 ref/out·고정 native 이름·외부 readonly 값 편집 | 소유 범위와 현재 C# 계약을 보호하며 지원된 코드 편집으로 이동 | **기존 지원/보호이며 잔여에서 제외**. whole-body 모바일 C# ref/out·native 이름 대응·폭 전환/cold/Confirm6 PASS. 외부/readonly 값을 일반 타입 버튼으로 바꾸지 않는다. 모든 readonly 핀을 미연결이라고 쓰지 않는다. |
| M10. 새 출력 정의·타입·배치·기존 출력 선택·비호환 타입 거절을 한 흐름으로 수행 | 새 source를 자동 Confirm하지 않고 입력/연결을 보존 | **최신 전체 수용 완료**. 이번 `mobile-outputs.log` 4 PASS로 새 정의/타입/배치·불완전 이름 raw 보존/cold/Escape·Save/compiler Confirm·기존 출력 재선택/비호환 타입 거절까지 완주했다. 과거의 locator 오류와 집중 재개 결과를 최신 전체 결과와 섞지 않는다. 새로운 출력 의미를 구현하지 않았다. |

| M11. 기존 C# code 동작 카드 → 내부 흐름 전환 | C# 본문/graph의 소유 및 활성 구현을 명시하고 기존 본문을 보존 | **변환 계약 부재**. native node는 `code` 또는 `graph` 한 종류다. 원본 prototype은 한 definition에 body/blueprint를 함께 보관한다. 기존 소스를 조용히 지우거나 버튼을 C# 편집기로 치환하지 않는다. 기존 native graph 진입 M3와 다르다. |
| M12. root `분기` 탭 → `＋ 분기` | 함수 루트 실행 출력과 호출자의 반환 분기/연결을 함께 검증 | **root 실행 출력 계약 부재**. 현재 native 함수 루트는 data args/return이고 enum 실행 출력은 소유 code/wrapper 노드에 있다. root 데이터 출력을 실행 enum으로 임의 변환하지 않으며 버튼은 비활성이다. M5의 노드 분기 목록과 분리한다. |

## 요소/Browser: 포괄 표현을 대신하는 조작

| ID·화면/조작 | 기대 결과 | 현재 결과·분류·근거 |
| --- | --- | --- |
| I1. 요소/정보 속성 `자료형` → `여러 개 허용`으로 **정의 cardinality 변경** | 기존 정확한 값/참조를 검증하는 원자 정의 변경 | **지원·수용 완료**. 기존 picker에서 단일↔다중을 한 후보/CAS로 처리하고 정확한 값·참조를 보존한다. 다중→단일은 사용자가 먼저 하나로 정리해야 하며 자동 폐기하지 않는다. [I1–I3 검증](VALIDATION_V536_FIELD_DEFINITIONS.md). |
| I2. 이미 존재하는 compound/reference/다중 정의의 자료형 버튼으로 구조 자체 전환 | 모든 기존 값/참조·자손을 검증하거나 전체 거절 | **지원·수용 완료**. 직접 소유한 정보/직접 적용한 소유 schema의 compound/reference/다중 정의를 변경한다. 다른 객체/자손/기본값·참조·연결과 호환되지 않으면 전체 미적용하고 원문을 보존한다. 외부/상속 정의 자동 수정은 허용하지 않는다. |
| I3. 새 속성 타입에서 ref/function/imported 정의 선택 | 선택 종류의 source receipt·기본값·참조 검증이 필요 | **지원·수용 완료**. 현재 문법의 primitive/compound/schema 제약 reference/function 연관과 직접 dependency의 등록 schema/function을 선택하고 명시적 대상·기본값을 검증한다. 선택은 실행 허가가 아니다. 임의 CLR 타입이나 다른 원본 종류를 새 의미로 추가하지 않는다. |
| I4. 정보 카드 `부모 변경` → 같은 정보 그룹의 카테고리/Root | 원본의 분류 위치만 바꾸고 schema 상속·필드·기본값은 보존 | **지원·수용 완료(기본6/독립16)**. 원본 Category/Root 분류 의미를 유지하고 기본/독립 properties 창을 bound 단일 정보·완전한 group/CAS·저장/취소/cold·Review/Confirm에 연결했다. 같은 정보 peer 입력·stale proof·위조·부분 그룹 차단, 실제 Undo/Redo의 off-filter projection 표시와 응답 유실 후 중복 방지를 검증했다. native `extends`는 보존하며 임의의 다른 source/복수 이동을 detached UI에 열지 않는다. [검증 기록](VALIDATION_V536_INFORMATION_PARENT.md) 참고. |
| I5. 정보(schema) 카드의 원본 기능/모듈 영역 | 해당 정보 타입에 결부된 기능 의미·소유 편집을 보존 | **부분 지원·I5 전체 미완료**. 기본/독립 정보 창의 모듈 연결·계약 표시·저장/취소와 기본창의 명시적 가져오기·Blueprint private copy·단독 소유 본문 편집은 동일 owner 후보/CAS·원본 보존·Review/Confirm으로 연결했다. 자체 함수의 inline 생성·이름/설명·미연결 기본형 핀 편집·저장 전 삭제와 기본/독립창 Save/cold/Review/Confirm도 연결했다. 기본창 자체 함수의 직접 작성·C# 본문/설명 Save·cold·Review/Confirm와 저장 실패/응답 유실·프로젝트 문맥 보존도 연결했다. 기본창 저장/미확정 자체 함수의 비파괴 삭제·전체 archive 복구·Undo/명시 Redo·원자 변경취소·응답 유실/cold·Review/Confirm은 연결했다. 구현만 삭제·순서 변경, 독립창 구현 편집/함수 삭제와 연결된 서명 전체 변경은 여전히 미완료다. [삭제·복구 검증](VALIDATION_V536_INFORMATION_FUNCTION_RETIREMENT.md) 참고. [모듈 검증](VALIDATION_V536_INFORMATION_MODULES.md), [자체 함수 첫 단위 검증](VALIDATION_V536_INFORMATION_OWN_FUNCTIONS.md), [기본 창 본문 검증](VALIDATION_V536_INFORMATION_FUNCTION_BODIES.md) 참고. |
| I6. 요소 아이콘 `편집`·속성/핀 아이콘 클릭 | 원본 선택과 저장된 표시 metadata 연결 | **기존 glyph 지원과 직접 소유 정보 헤더 이미지 수용 / 잔여 미완료**. 요소 [팝오버](VALIDATION_V536_ELEMENT_GLYPH.md), 기존 직접 정보 속성 [해제·저장](VALIDATION_V536_INFORMATION_PROPERTY_GLYPH.md), 새 직접 정보 속성 [생성·값·glyph 결합](VALIDATION_V536_NEW_INFORMATION_PROPERTY_GLYPH.md)을 구별한다. 객체의 기존 직접 소유 속성 [소유 스키마 결합 저장](VALIDATION_V536_OBJECT_PROPERTY_GLYPH.md)을 구별한다. 새 객체 속성의 저장 전 [생성·glyph 결합](VALIDATION_V536_NEW_OBJECT_PROPERTY_GLYPH.md)도 구별한다. 정보의 저장된 직접 소유 함수 카드 [glyph](VALIDATION_V536_INFORMATION_FUNCTION_GLYPH.md)도 별도 수용 범위다. 새 정보 함수 카드의 저장 전 [glyph·생성/receipt 수명](VALIDATION_V536_NEW_FUNCTION_GLYPH.md)은 기존 연결의 별도 수용 검사로 마감한다. 부모 없는 직접 소유 독립 기능 요소의 헤더 [glyph·설명 원자 저장](VALIDATION_V536_FEATURE_HEADER_GLYPH.md)도 구별한다. 직접 소유 정보 헤더의 [로컬 PNG/JPG/WebP 선택·128px WebP 저장](VALIDATION_V536_LOCAL_HEADER_IMAGE.md)은 원래 inline metadata·한 후보/CAS·Review/Confirm 범위로 연결한다. 직접 소유 객체 헤더의 [로컬 이미지·부모/본문 보존](VALIDATION_V536_OBJECT_HEADER_IMAGE.md)도 같은 기존 저장 계약으로 연결한다. 자체 중첩 정의·원본에서 실제 편집 핸들러가 확인되는 별도 아이콘과 기능 헤더/속성/함수 카드의 로컬 이미지는 미완료다. 그래프 카드의 함수 카드 마크업 재사용만으로 독립 노드 glyph라는 새 필수 기능을 추가하지 않는다. 원본 CSS가 숨긴 Blueprint 루트·모바일 카드 입력 아이콘은 새 필수 누락으로 늘리지 않는다. 부모 있는 직접 소유 기능의 로컬 헤더 [glyph·설명](VALIDATION_V536_PARENT_FEATURE_GLYPH.md)도 원계약·부모 보존 범위로 수용한다. 부모 선택·계약 변경·독립 복제의 지원 확대는 아니다. linked 정보 하위 값의 정상 읽기 전용을 새 편집 요구로 확대하지 않는다. |
| B1. Browser에서 **외부 runtime 객체**의 Data 직접 쓰기 또는 임의 source 종류 이동/삭제 | 소유권/데이터 수명을 확인한 검증된 mutation만 허용 | **의도된 지원/권한 제한**. 현재 소유 object Data·검증된 선언만 편집한다. 타 소유/외부 runtime 쓰기를 ‘단순 누락 버튼’으로 열지 않는다. 지원 Browser Data/개념 이동/복구는 기존 검증 완료다. |
| B2. Browser 선언별 ‘작업자’ 배지 | 실제 진행 중 작업과 선언을 연결해 표시 | **실제 상태 어댑터 미연결**. `WebState.csbody`의 assignedNode/supportingDraftIds/changedIds·Helper 상태는 이미 존재한다([원래 잔여 대조](V536_I5_6_RESIDUAL_RECONCILIATION.md)). 이를 원본 배지·프로젝트 범위에 연결하는 잔여이며 데이터 전체 부재로 단정하지 않는다. 임의 작업자나 AI 결과를 만들지 않는다. |

`legacy inline`은 손실 우려가 있는 이전 기록을 총칭하던 표현이었다. 별도의 새 UI 조작을 가리키지 않으므로 독립적인 무한 잔여로 세지 않는다. 기존 입력을 보존하고 미지원 정의 전환은 I2로 한정한다. 원본의 모든 가능한 타입 조합을 새 수용 요구로 추가하지 않는다.

raw+저장 copy ABI/기존 body/다중 target/Set-property/다른 Blueprint 계획, 여러 raw/독립 properties+copy는 이번 지시에서 확장하지 않는 명시적 제한이다. 새 ABI 결합 계약·opaque 자동 재작성·새 async runtime·이미지/협의/렌더 backend는 이번 UI 수용 수정에 포함하지 않는다. 실제 Windows/WebView2/모바일 하드웨어·DPI/native IME와 Library 전달은 계속 미검증이다.

## 27개 조작 최종 판정

지원 경로 수용 **15개**: A1/A2/A3/A7, M1/M2/M3/M5/M6/M9/M10, I1/I2/I3/I4. 이 한정 범위에 남은 재현된 화면 미연결 또는 필수 미검증은 없다. 전체 타입·ABI 조합이나 원본의 모든 기능을 구현했다는 뜻은 아니다. M2의 다중 삭제는 직접 소유 ordinary root/연결 해제 후, M3은 기존 native graph 진입, M5는 지원 code/wrapper enum 범위다.

나머지 **12개**를 완료로 바꾸지 않는다. M7/M8/B1은 의도된 native identity·최종 이름·소유권 보호다. A4/A5/A6/M4/M11/M12/I5/I6/B2는 위에 적은 정확한 범위의 추가 계약/adapter/데이터 구현이 필요한 제한·미구현이다. I6 아이콘 편집처럼 원본 조작이 실제로 미구현인 것도 이 목록에 남으며 단순 미검증으로 숨기지 않는다. 실제 기기 및 이미지/협의/렌더 backend 부재도 해제하지 않는다. 상세 근거는 [A7/M6 수용](VALIDATION_V536_A7_M6.md)을 참조한다.
