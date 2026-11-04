# v666 구현 기준과 고정 수용 목록

사용자가 2026-10-29에 승인한 저장소의 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`을 현재 UI 구현 기준으로 삼는다. ZIP SHA-256은 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`, 내부 버전은 666, Site 소스 commit은 `d6d8a63575a3d1addafc9ab0b558aa3fec600a46`이다. 최신 라이브 Site나 다른 버전을 자동 채택하지 않는다. 첨부 이름·크기는 일치하지만 Library 바이트 전송 실패로 첨부와 ZIP의 바이트 동일성은 미확정이다. 사용자가 main에도 있다고 지정한 이 저장소 ZIP을 사용한다.

v536 기록은 과거 검증 증거이며 기존 기능을 미구현으로 되돌리지 않는다. 속성·정보 함수 카드 이미지, 저장/실패/응답 유실·Undo·취소·cold·CAS·Review/Confirm의 기존 지원을 보존한다. 프로토타입의 브라우저 저장소·모의 Confirm·멤버 정책·Worker 연출은 실제 실행 권한이나 서버 보안의 증거가 아니다. 실제 계정·자격증명·접근권한 변경과 배포는 이번 구현 승인에 포함되지 않는다. 공개 override는 원본 입출력 계약을 유지하고 구현만 바꾸며, 독립 새 계약 복제는 필수 범위가 아니다.

## 현재 M11·M12·M4 경계

아래 긴 표의 누적 문장은 각 당시 검증의 기록이다. 현재 잔여 판단은 [유한한 M12 마감표](M12_CLOSURE.md)를 우선한다. M11의 원래 소유 구현 편집은 마감했으며 구체적 회귀 없이 다시 열지 않는다. M12는 데이터 반환·소유 provider/target·일반 및 native 진입·공개/private 실행 계약 caller의 보존을 연결했고, 현재 실제 흐름의 마감 경계는 다음과 같다.

- ordinary IInvoke/native import·기존 NoBranch의 관측은 [검증 기록](VALIDATION_V666_ROOT_EXECUTION_OBSERVERS.md)을 따른다. 실제 공개 OriginalResult를 명시 wrapper로 연결하고 원본 계약의 전체 갱신 후보를 [wrapper 검증 기록](VALIDATION_V666_ROOT_EXECUTION_WRAPPERS.md)에 연결한다. 네 원래 흐름의 지원과 마감 근거는 다음과 같다.
- 같은 계약 copy·자식 소유 target의 전체 명시 갱신과 inherited-only 관측은 최종 검증까지 마감했다. [전체 갱신 기록](VALIDATION_V666_ROOT_EXECUTION_OWNED_UPDATES.md)에 신규/재사용과 환경 중단 복구 근거를 유지한다.
- 등록 외부 import·manifest·scope/포함 모듈의 읽기 전용 receipt도 저장·복원·Review·최종 CAS·실제 실행까지 마감했다. [최종 44단계와 패키지/복원 증거](VALIDATION_V666_ROOT_EXECUTION_IMPORTS.md)를 따른다. 네 원래 흐름으로 M12를 완료하며 조합별 새 잔여를 추가하지 않는다.

wrapper의 정상 stale 거절을 자동 변환 요구로, 비소유 부모/참조 쓰기나 override IO 변경을 미구현으로 늘리지 않는다. 새 타입·문맥 조합을 이 목록에 추가하지 않는다. M4의 직접 소유 ordinary 함수·동작/호출자의 명시적 Task 실행 기반은 [현재 지원 경계](M4_ASYNC.md)에 연결했다. 최종 신규 LF22·CRLF20·패키지/전체 복원/실패 수명관리8, 총50단계를 통과했다([검증·보관 기록](VALIDATION_V666_ASYNC_RUNTIME.md)). 직접 소유 ordinary Root의 원본 전환 메뉴·초안/원자 저장 연결은 [이번 지원 경계](M4_ASYNC_TRANSITION.md)를 따른다. 이 UI 단위의 [최종 신규 40단계·재사용 0](VALIDATION_V666_ASYNC_TRANSITION.md)을 마감했다. 지역 C# Result 완료 분기의 동기 복귀와 ordinary async Set 연동은 아래 후속에 연결했고, ordinary 공개 완료는 후속에 연결했고, async root 속성 편집은 [현재 단위](M4_ASYNC_PROPERTIES.md)로 연결했다. 명시 native/Result 없는 본문·새/내부 소유 전환은 남는다. 동기 caller는 명시적으로 async로 바뀌기 전에는 오류로 거절한다. V2–V9와 기존 별도 UI/권한 backend·종류 C# 표현/사용 중 삭제 대응·실기기 검증의 남은 범위는 해당 고정 행을 따른다.

## 기존 미완료 사용자 흐름

아래는 기존 27행/ABI 9행의 같은 흐름을 묶은 목록이다. ref/out·target·프레임의 가능한 조합마다 새 필수 행을 추가하지 않는다. 원본 ZIP의 `app.js`/`blueprint.js`에 대응하며 완료 조건은 해당 원본 조작의 정상 저장·원자 실패·명시 대응·입력 보존 및 영향 검증이다.

| 고정 흐름 | 실제 잔여와 종료 조건 |
|---|---|
| 자체 중첩 정의 | `renderObjectSchema`의 자체 compound 자식 추가/이름/타입/기본값/아이콘/삭제. named 정보의 값 편집은 이미 지원한다. 기존 qualified schema/소유 키 경로로 **새 자체 복합과 저장된 소유 복합의 하위 정의 편집 지원 단위를 마감**했다. 기본/독립 정보 창·객체에서 추가·이름·타입·기호/이미지·기본값·삭제, private Undo/Redo·Save/cold/Review/Confirm을 검증했다. 실패·충돌·응답 유실·저장 중 입력·별도 실제 프로젝트 cold 왕복을 집중 확인했고 최초 LF/CRLF·새 패키지/압축 복원 회귀 36단계가 통과했다. named 정보·부모·외부 정의는 복제하지 않는다. 기존 일반/named·참조 속성의 소유 복합 전환도 원본의 빈 복합 초기화 의미와 기존 팝오버의 명시 적용으로 연결했다. 정보/객체 private source·저장된 내부 자식, 배열 유지/축소와 오류/복구 집중 검증 및 **이번 전환의 최종 LF/CRLF·새 패키지·압축 복원 40단계**를 마감했다. [전환 지원/신규·재사용·미실행 검증](VALIDATION_V666_OWNED_CONVERSION.md). 연결된 public 정보의 정의는 원본 창에서 편집하고, 비호환 기존 소비자는 전체 미적용한다. 공개 override 계약 금지·독립 계약 복제 제외는 그대로다. 모든 참조/배열 타입 조합의 UI 검증 완료로 표시하지 않는다. [최초 저장/보호 검증 경계](VALIDATION_V666_OWNED_INFORMATION.md). |
| 나머지 실제 노출 아이콘 | 소유 graph 동작 카드의 기호·로컬 이미지를 기존 팝오버·private 입력·소유 후보/CAS로 연결했다. 일반/직접 private graph 및 same-contract copy의 root/private frame을 다루며, call/wrapper는 원본과 같이 readonly다. 공개 함수 정의·ABI·본문·외부 원본을 바꾸지 않는다. 집중 native/UI와 최종 LF/CRLF·새 패키지·압축 복원의 **49단계**가 통과했다. [아이콘 지원/검증·보관 경계](VALIDATION_V666_ACTION_ICONS.md). 분류·개념·모듈 헤더도 기존 팝오버·로컬 이미지와 metadata 전용 owner 거래에 연결했고 집중 UI/보호·프로젝트 왕복과 최종 LF/CRLF·새 교차 패키지·압축 복원 **57단계**를 마감했다. [헤더 범위/검증 기록](VALIDATION_V666_DECLARATION_ICONS.md). 모듈의 직접 요구 입력/out/반환과 기존 Set 편집이 지원하는 자체 출력에는 공통 팝오버·로컬 이미지·해제를 연결했다. 아이콘은 실행 ID/타입/순서/연결과 분리한다. 집중 보호 검사와 최종 **LF30·CRLF26·새 패키지/압축 복원/실패 수명관리14, 총70단계**가 통과했다. Set의 copy 초안·slot·private·conversion·결합 copy/호출 문맥은 기존 Set UI 미지원 경계로 유지하며 정상 금지로 확정하지 않는다. [지원/검증 경계](VALIDATION_V666_PIN_ICONS.md). 종류는 별도 nominal `enum` 정의와 미참조 항목의 생성·이름·순서·문자/이미지·해제·삭제를 연결했고 집중 기본/독립 창·cold·원자 실패·Review/Confirm을 확인했다. 최종 **LF34·CRLF29·새 교차 패키지/압축 복원/실패 수명관리16, 총79단계**가 통과했고 증거와 최신/롤백 두 패키지를 지속 보관했다. 이는 종류 정의·미참조 항목 편집의 완료이며 전체 종류 소비 흐름 완료는 아니다. [종류 정의 지원과 호환성](VALIDATION_V666_INFORMATION_ENUM.md). 속성의 종류 값/기본값은 owner+항목 ID 기반의 단일/배열 typed-data와 원본 드롭다운으로 연결했다. 정보/객체의 새 속성·기존 값·기본/독립 창·입력/Undo/취소/실패/충돌/응답 유실/프로젝트 왕복/cold/ReviewConfirm의 집중 검사와 최종 **LF37·CRLF31·새 패키지/전체 압축 복원/실패 수명관리18, 총86단계**가 통과했다. 기존 79단계도 다시 실행했으며 최신/롤백 두 패키지와 증거를 지속 보관했다. C# 표현은 결정하지 않으며 runtime property descriptor는 비지원/CLR 미지정을 유지한다. [종류 속성 값 지원·검증 경계](VALIDATION_V666_INFORMATION_ENUM_VALUES.md). 사용 중 ID 삭제는 현재 값/기본값이 무효가 되면 전체 거절한다. 소비자 삭제 대응 UI는 별도 잔여다. 종류 정의 전체 보관/복구는 기존 Browser 삭제·등록 보관 계약과 동일 ID 복구에 연결했다. 참조 중 정의는 값을 바꾸지 않고 보관을 차단하며 원문·초안·현재 입력을 보존한다. 집중 12개와 최종 **LF39·CRLF32·새 패키지/전체 복원/실패 수명 관리20, 총91단계**가 통과했고 증거·최신/롤백 두 패키지를 지속 보관했다. [보관/복구 지원·검증 경계](VALIDATION_V666_INFORMATION_ENUM_RETIREMENT.md). 원본 핸들러가 없는 함수 상세 핀이나 CSS가 숨긴 루트/모바일 핀은 추가하지 않는다. 종류의 숫자/C# 변환은 결정하지 않고 실행 분기 enum과 구분한다. 완료된 속성·정보 함수 카드 이미지는 제외한다. |
| copy의 영향 소스 결합 | 원본 계약 갱신이 실제 forwarded 부모/opaque·whole-body/import에 영향을 주는 경우 명시 본문·저장소·연결을 한 후보/CAS로 저장. ordinary Root/private·복수 호출·명시 target 지원을 중복 구현하지 않는다. 기존 A4–A6/7행에 한 번만 집계한다. |
| 여러 함수의 공유 호출자 결합 | 현재 지원한 직접 scalar·정의·ref/out·순열·계약 불변 본문 그룹 밖의 실제 private/wrapper/copy/상속/등록 소스 closure를 한 Save에 결합. 현재 순수 순열 보호는 구현 경계이며 영구 UX 금지가 아니다. |
| 함수 고급 타입 | 원본 타입 선택기의 정보·객체·기능 등 제공 타입을 native 함수 계약/호출자 검증에 연결. 속성의 typed datum 지원과 구별한다. |
| 핀 표시명 | 한글·공백 표시명과 생성 코드 식별자의 대응·저장·복원. 별도 영구 핀 ID 재설계를 이미 결정된 것으로 취급하지 않는다. |
| 실제 작업자 배지 B2 | 기존 `assignedNode`/지원 초안/변경 source와 실제 Helper/Worker 상태를 선언·폴더·헤더 범위에 표시. 3D 연출과 동일한 실제 상태를 사용하며 가짜 작업을 생성하지 않는다. **로컬 소유 활성 ProjectContext의 실제 배정·관측 변경/지원 초안, 고유 Helper 집계·팝오버·cold 읽기 연결 구현.** 실행 owner 부재는 확인 필요이며 다른 사용자/그룹의 권한 backend는 별도 팩 선행. [범위와 검증](VALIDATION_V666_WORKER_BADGES.md). |
| 비동기 M4 | 원본 async 전환/완료 분기를 실제 저장·호출·실행 계약에 연결. ref 입력 등 원본의 정상 거절을 유지한다. |
| 개별 C# 동작의 내부 흐름 M11 | 원본 내부 편집 진입에 대응하는 노드 단위 활성 구현·원문 보존·복구 거래. 임의의 C# 로직 추론은 요구하지 않는다. 저장된 직접 소유 Root 및 중첩 graph의 일반 next C#를 원문 보존 단일 내부 코드로 감싸는 미리보기/편집/Save를 연결했다. 중첩은 전체 frame/source binding·조상 왕복·혼합 profile을 보존하며 기존 엔진 예산을 적용한다. 이번 중첩 단위의 집중 보호 검사와 최종 **LF22·CRLF18·새 패키지/전체 복원/실패 수명관리8, 총48단계**가 통과했고 최신/롤백·증거를 지속 보관했다. 일반 ref/out은 바깥 저장소 배정·역할을 보존하는 native 전달로 연결했고, 집중 API/화면과 최종 **LF18·CRLF17·새 패키지/전체 복원/실패 수명관리8, 총43단계**가 통과했다. native 저장소·whole-body 문맥 11개도 양쪽에서 통과했으며 whole-body 노드의 private 전환 완료를 뜻하지 않는다. [저장소 지원/whole-body 경계](VALIDATION_V666_NODE_INTERNAL_STORAGE.md). 직접 소유 whole-body의 원래 Invoke/this·재귀·scoped import/source identity를 private 경로로 전달하는 연결도 추가했다. 원문 자동 재작성 없이 외부 계약·ref/out 저장소·원래 target을 유지한다. [whole-body 지원/검증](VALIDATION_V666_NODE_INTERNAL_CONTEXT.md). 이 단위의 최종 **LF23·CRLF20·새 패키지/전체 복원/실패 수명관리8, 총51단계**가 통과했고 최신/롤백과 증거를 지속 보관했다. 전체 M11 완료 아님. 직접 소유 실행 enum 선택기의 원문 보존 래핑·본문/helpers 편집·실행 결과 전달도 연결했다. [실행 분기 지원/검증](VALIDATION_V666_NODE_INTERNAL_BRANCHES.md). 이 단위는 최종 **LF27·CRLF22·새 패키지/전체 복원/실패 수명관리8, 총57단계**가 통과했으며 최신/롤백과 증거를 지속 보관했다. 내부 종료점의 기존 분기 ID 선택·연결·첫 미리보기/저장된 흐름의 원자 Save도 연결했다. [종료점 지원/검증](VALIDATION_V666_NODE_BRANCH_EXITS.md). 이 단위는 독립 **LF22·CRLF18** 통과 후 검사 helper 경로만 수정하여 동등 코드의 40단계를 재사용했고, 최종 source의 **새 준비6·패키지/전체 복원/실패 수명관리8**을 통과했다. 최신/롤백과 실패를 포함한 증거를 지속 보관했다. 저장된 same-contract copy의 단독 정보 배정·Root 일반 C# 내부 진입도 기존 소유 receipt와 원자 후보로 연결한다. [copy 지원/검증 경계](VALIDATION_V666_NODE_INTERNAL_COPY.md). 최종 소스의 **새 LF18·CRLF14·패키지/전체 복원/실패 수명관리8, 총40단계**를 통과하고 최신/롤백과 증거를 지속 보관했다. 저장된 단독 same-contract copy의 소유 중첩 graph 안 일반 C# 내부 진입도 정확한 frame/source binding과 기존 소유 receipt로 연결한다. [중첩 copy 지원/검증 경계](VALIDATION_V666_NODE_INTERNAL_COPY_NESTED.md). 최종 소스의 **새 LF21·CRLF17·패키지/전체 복원/실패 수명관리10, 총48단계**를 통과하고 집중 증거·최신/롤백을 지속 보관했다. 저장 copy의 일반 ref/out 내부 진입도 기존 caller/local 저장소와 out 역할을 보존하며 연결한다. [copy 저장소 지원/검증](VALIDATION_V666_NODE_INTERNAL_COPY_STORAGE.md). 최종 소스의 **새 LF18·CRLF16·패키지/전체 복원/실패 수명관리8, 총42단계**를 통과하고 집중 증거·최신/롤백을 지속 보관했다. 저장된 단독 배정 copy의 실행 enum 선택기 내부 진입·본문/helpers 편집도 기존 분기 전달과 소유 receipt에 연결한다. [copy 실행 분기 지원/검증](VALIDATION_V666_NODE_INTERNAL_COPY_BRANCHES.md). 최종 수정 코드의 **새 LF19·CRLF18·패키지/전체 복원/실패 수명관리8, 총45단계**를 통과하고 최신/롤백·증거를 지속 보관했다. 저장된 단독 배정 whole-body copy의 원문 보존 내부 진입도 기존 native context 전달에 연결한다. [whole-body copy 지원/검증](VALIDATION_V666_NODE_INTERNAL_COPY_CONTEXT.md). 최종 코드의 **새 LF19·CRLF19·패키지/전체 복원/실패 수명관리8, 총46단계**를 통과하고 최신/롤백·증거를 지속 보관했다. 새 copy의 Root next C# 내부 진입과 첫 Save/정보 배정도 기존 snapshot·receipt·원자 후보로 연결한다. [첫 Save 지원/검증](VALIDATION_V666_NODE_INTERNAL_COPY_CREATING.md). 최종 코드의 **새 LF19·CRLF19·패키지/전체 복원/실패 수명관리8, 총46단계**를 통과하고 최신/롤백·증거를 지속 보관했다. 새 copy의 기존 소유 중첩 frame 및 실행 selector 최초 전환도 같은 전체 경로/source binding과 원자 첫 Save/배정에 연결한다. [중첩/분기 최초 전환 지원·검증](VALIDATION_V666_NODE_INTERNAL_COPY_FRAMES.md). 최종 **LF20·CRLF19·새 교차 패키지/전체 복원/실패 수명관리8, 총47단계(새23·동등재사용24)**를 통과하고 증거·최신/롤백을 지속 보관했다. 지연 응답을 기다리던 검사 도우미의 추가 flush는 수정하고 새로 검증했으며 실패/중단도 따로 보존한다. call/wrapper·상속받기만 한 부모 본문은 원래 readonly/소유 보호이며 새 미구현으로 세지 않는다. 자식이 직접 선언한 own Blueprint target은 같은 공개 계약을 유지하며 M11 진입/편집/원자 저장을 지원한다. [override 소유 경계·검증](VALIDATION_V666_NODE_INTERNAL_OVERRIDE.md). 최종 동결 코드의 **신규 LF19·CRLF18·새 교차 패키지/전체 복원/실패 수명관리8, 총45단계**가 통과했고 집중 증거·최신/롤백 두 패키지를 지속 보관했다. 등록 외부 부모도 기존 등록 의존성의 헤더 관측·영수증·Save/Review/Confirm 재검증 및 최종 읽기 전용 CAS에 연결했다. [등록 부모·최종 CAS 지원/검증](VALIDATION_V666_NODE_INTERNAL_EXTERNAL_OVERRIDE.md). 최종 동결 코드의 **신규 LF22·CRLF21·새 교차 패키지/전체 복원/실패 수명관리8, 총51단계**를 통과하고 집중 실패 증거·최신/롤백 두 패키지를 지속 보관했다. 이로써 원래 고정 M11의 소유 구현 편집 범위를 마감하며 부모/참조 원본 직접 쓰기와 공개 override 계약 변경은 정상 거절이다. 실제 기기/전체 UI 검증과 다른 고정 행의 잔여는 별도로 유지한다. private graph 미지원 구형 profile의 자동 승격 거절은 호환성 보호이며 새 마이그레이션을 필수 잔여로 추가하지 않는다. [지원 경계](BLUEPRINT_NODE_INTERNAL_FLOW.md), [Root 최초 검증](VALIDATION_V666_NODE_INTERNAL_FLOW.md), [중첩 검증](VALIDATION_V666_NODE_INTERNAL_NESTED.md). |
| 루트 실행 분기 M12 | 루트 분기 추가·반환 배치와 호출자 분기를 원자 검증. 이미 지원된 노드 enum과 구별한다. **직접 소유한 동기 void 함수의 Blueprint target 전부·명시한 일반 직접 호출자들**를 공개 실행 metadata/별도 결과 인터페이스·반환 카드·호출자 분기 포트와 하나의 후보에 연결한다. 원래 C#·ordinary Invoke·ID/값·override 계약은 유지한다. 보존 원문/헤더와 관측 closure도 Save/Confirm의 읽기 CAS에 포함한다. 값 입력에 정수 out 하나가 있는 동기 void 계약도 기존 출력 카드/데이터 연결과 IInvoke를 보존하며 결과 enum과 함께 전달한다. 출력 발행 뒤 호출자 분기/다음 줄을 실행한다. 같은 그래프의 반복 호출·여러 호출자/target의 계약과 반환을 하나의 후보/CAS/Review 그룹으로 결합하며, 영향받는 모든 호출 위치와 다른 target 반환을 직접 지정한다. Blueprint 호출자가 없는 정의와 기존 C# IInvoke 소비자도 보존한다. Confirm 후 작은 그룹의 기준본 정착도 공통 검증으로 처리한다. 직접 소유 함수 계약의 정보(schema)에 단독 배정된 저장 same-contract copy에는 기존 공개 분기/None의 반환 선택·배치·연결을 readonly 정의와 분리해 연결했다. 관측 소스 전체의 원자 그룹과 읽기 receipt를 checkpoint/복원/Review/최종 CAS에 결합하며, 완료된 공개 루트 거래의 live metadata 수명도 같은 세션의 copy 생성/후속 편집과 구분한다. 이 후속 단위의 최종 **신규 LF23·CRLF19·새 교차 패키지/전체 복원/실패 수명관리6, 총48단계**가 통과했다. 최신/롤백과 증거를 지속 보관했다. [copy 반환 지원/검증](VALIDATION_V666_ROOT_EXECUTION_COPY.md). 새 정보(schema) copy의 미리보기에서도 같은 공개 분기/None 반환을 편집하고 생성·등록·배정과 첫 Save에 결합하도록 연결했다. 최초 관측 원문을 보존하며 미확정 copy의 후속 본문 영수증과 구분한다. 독립 창은 같은 소유자의 정확한 반환 계획만 전달한다. 이 첫 저장 단위의 최종 **신규 LF24·CRLF20·새 교차 패키지/전체 복원/실패 수명관리6, 총50단계**를 통과하고 증거·최신/정상 롤백을 지속 보관했다. [첫 저장 지원·검증 경계](VALIDATION_V666_ROOT_EXECUTION_COPY_CREATING.md). 자식이 직접 선언한 ordinary Blueprint target의 기존 공개 분기/None 반환을 동일 계약·원자 그룹에 연결했다. 상속된 Blueprint 실행은 선언 소유자의 원문을 사용하고 부모 본문 직접 편집은 거절한다. 이미 등록된 외부 부모는 readonly ancestry receipt와 최초 화면 dependency hash를 Save/복구/Review/최종 CAS에 결합한다. [자식 소유 반환 지원·검증](VALIDATION_V666_ROOT_EXECUTION_OVERRIDE.md). 이 단위의 최종 **신규 LF23·CRLF20·새 교차 패키지/전체 복원/실패 수명관리6, 총49단계**가 통과했고 최신/롤백과 증거를 지속 보관했다. 기존 직접 등록 외부 함수의 공개 분기/None도 정보(schema)에 명시 배정된 로컬 소유 ordinary provider에서 readonly 계약·헤더 관측과 원자 Save/최종 CAS로 연결한다. [등록 함수 반환 지원·검증](VALIDATION_V666_ROOT_EXECUTION_REGISTERED.md). 최종 **신규 LF16·CRLF14·패키지/전체 복원/실패 수명관리6, 총36단계**와 명시한 집중/변경 없는 native 재사용 근거를 보존했고 최신/롤백 보관을 마쳤다. 등록 외부 함수의 **저장된** public same-contract copy도 기존 분기/None 반환·명시 배정·readonly 헤더 receipt·원자 저장/최종 CAS에 연결했다. [저장 외부 copy 검증](VALIDATION_V666_ROOT_EXECUTION_REGISTERED_COPY.md). 최종 **신규 LF17·CRLF14·패키지/전체 복원/실패 수명관리6, 총37단계**와 명시한 집중 재사용 및 추가 native80개 신규 근거를 보존했고 최신/롤백 보관을 마쳤다. 새 외부 함수 copy의 미리보기/첫 Save도 기존 선택 origin·첫 관측 해시·생성/등록/배정·반환의 원자 거래로 연결했다. [외부 새 copy 검증](VALIDATION_V666_ROOT_EXECUTION_REGISTERED_CREATING.md). 최종 **LF19·CRLF16·패키지/전체 복원/실패 수명관리6, 총41단계(신규33·동등재사용8, native/소유 경계80개 포함)**와 집중 보호·원본 증거를 보존했고 최신/롤백 보관을 마쳤다. 나머지 원래 데이터/호출 문맥은 [유한한 M12 대조표](BLUEPRINT_ROOT_EXECUTION.md)에 남기며 공개 외부 계약 변경은 정상 readonly 보호다. 다른 직접 소유 함수 import가 있는 ordinary 본문·caller도 추가 계약을 변경 없는 관측 멤버로 결합한다. [본문 import 검증](VALIDATION_V666_ROOT_EXECUTION_PROVIDER_IMPORT.md). 최종 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계(native/소유 경계82개 포함)**와 집중 증거·최신/롤백을 지속 보관했다. [소유 복합 호출 검증](VALIDATION_V666_ROOT_EXECUTION_COMPOUND_OWNED.md). 최종 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계(native/소유 경계82개 포함)**와 집중 실패 증거·최신/롤백을 지속 보관했다. 중첩/private·등록 외부 import receipt·복수 provider 계약 변경은 현재 구현 경계이지 새 정상 금지 정책이 아니다. 이 확장 단위의 최종 **신규 LF21·CRLF18·새 교차 패키지/전체 복원/실패 수명관리6, 총45단계**를 마감하고 최신/롤백과 증거를 지속 보관했다. [복수 호출자/target 검증](VALIDATION_V666_ROOT_EXECUTION_CLOSURE.md). 후속 단위에서 동기 void의 typed out·복수 out·ref를 기존 전달 계약으로 연결한다. ordinary 비void 반환은 별도 경계다. [동기 데이터 전달 검증](VALIDATION_V666_ROOT_EXECUTION_DATA_VOID.md). 최종 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계(native/소유 경계82개 포함)**와 실패를 포함한 집중 증거·최신/롤백을 지속 보관했다. 정수 out 단위의 **신규 LF19·CRLF17·새 교차 패키지/전체 복원/실패 수명관리6, 총42단계**가 통과했고 증거·최신/정상 롤백을 지속 보관했다. [out 동시 반환 검증](VALIDATION_V666_ROOT_EXECUTION_OUT.md). [이번 지원 경계](BLUEPRINT_ROOT_EXECUTION.md). 최종 동결 코드의 **신규 LF18·CRLF16·새 교차 패키지/전체 복원/실패 수명관리6, 총40단계**가 통과했고 최신/정상 롤백·집중 및 최종 증거를 지속 보관했다. [최종 검증·보관 결과](VALIDATION_V666_ROOT_EXECUTION.md). 다른 원래 함수/호출 문맥 및 M4는 별도 잔여이며 전체 M12/UI 완료로 표시하지 않는다. |

## v666의 누적 변경

다음은 이번에 제외하지 않고 반영한 유한한 추가 수용 단위다. 각 단위는 기본/독립 창·프로젝트 경계·입력/취소·저장/재시작과 실제 관련 권한 검증으로 닫는다. 동일 화면의 모든 타입/target 순열을 별도 항목으로 늘리지 않는다.

| 단위·원본 근거 | 구현 범위·의존성·현재 상태 |
|---|---|
| V1 화면 확대: `clampCanvasZoom`, `createSteppedZoomWheel`, 두 zoom menu | Workspace/Blueprint 3.125–500%, 400/500 프리셋, 직접 입력/슬라이더/휠/터치, 중심/포인터 기준과 개인 화면 복원. source·실행 권한과 분리한다. **기본 화면 지원 구현·집중 검증 완료**. LF/CRLF·새 교차 패키지·압축 복원본에서 확대 8개 확인씩 통과했다. 새 배율의 독립 정보 창/프로젝트 전환 조작은 이번 집중 검사에서 별도 실행하지 않았으며 모든 문맥 완료로 표시하지 않는다. [검증 범위와 출처](VALIDATION_V666_CANVAS_ZOOM.md). |
| V2 안내 문체 | 원본의 바뀐 안내·오류·확인 문구를 실제 대응 화면에 적용. 오류 의미·거절·번역되지 않은 backend 진단을 전역 문자열 치환으로 바꾸지 않는다. 후속 미구현. |
| V3 3D 작업실: `office.js`, `office-world.js`, `office-actors.js`, `voxel-character.js` | 기존 패널과 아이소메트릭 보기 전환, 프로젝트별 방·보관 설비·배치·카메라/추적, Helper/Worker 표시와 보관함→기존 Browser 진입. 실제 Worker 이벤트의 read/write/완료/중단을 즉시 표시한다. 사용자가 2026-10-29에 명시한 대로 캐릭터 이동은 시각적 연출뿐이다. 실제 작업 시작/실행은 도착·이동 애니메이션 완료를 기다리지 않으며 시각적 위치를 선행 조건·실행 잠금·스케줄로 사용하지 않는다. 실제 권한·검증·실행 조건은 그대로이고 6개 단말은 표시 자리다. 실제 상태 adapter·로컬 3D 자원/라이선스와 저장 수명이 선행한다. 미구현. |
| V4 프로젝트 멤버/조직: `members.js` 및 동봉 조직/권한/소유권 검사 | 원본 멤버·그룹·미배정 영역·계층/복수 소속, 공개 범위, 경로별 권한 트리, staged 변경/Undo/취소/소유권 제안 UI. native의 실제 신원/권한 source와 연결해야 하며 로컬 demo ACL을 서버 권한으로 채택하지 않는다. 현재 멤버/조직 backend 연결 미구현. 실제 계정/접근권한 변경은 이번 승인 밖이다. |
| V5 Agent 공유·대화 경계: `agents.js`, 관련 `app.js` 함수 | 실제 사용/관리 가능 상태와 Helper·사용자별 세션·철회·개인 이력 분리의 표시/기존 동작 연결. 새 자격증명 복제·실제 grant 확대는 하지 않는다. 기존 권한 source adapter가 선행하며 미구현이다. |
| V6 리소스 탐색: `resourceDatabase`, `renderResourceBrowser`, `setupResourceTree` | 프로젝트 자산의 폴더/검색/밀도·선택·이름·이동·삭제와 복구, 원래 drag/drop 진입. 실제 소유 자산·경로/권한·원자 변경/이력 저장이 선행한다. 사용자 개인 폴더를 임의 탐색/업로드하지 않는다. 현재 자산 backend/adapter 미구현. |
| V7 리소스 미리보기·편집: `resource-preview.js`, `resource-edit.js` | 원본이 제공한 텍스트·이미지·PDF 등 미리보기와 지원하는 내용 편집/취소/저장. PDF/3D 등은 원본에서 제공한 보기 범위만 다루며 임의 편집 기능을 늘리지 않는다. 로컬 vendor·라이선스·읽기 권한·자산 수명·최종 CAS가 선행한다. 미구현. |
| V8 실행창 제어: `openRunViewport`, `setupRunDeveloperMenu` | 원본의 해상도/전체화면·소리·개발 표시 제어를 실제 Run 수명에 연결. 모의 scene/FPS를 native renderer 성공으로 쓰지 않는다. 기존 Run backend로 가능한 제어와 내장 renderer/오디오 backend 부재를 구별한다. 기존 지원 외 추가 제어 미구현. |
| V9 찾기·참여자 탐색: `openWorkspaceFinder`, 참여자/연락처 관련 함수 | 현재 프로젝트의 원본 찾기/관련 요소 이동과 멤버·Helper 프로필/연락처/대화 진입. 실제 보이는 범위와 신원·대화 권한을 사용한다. V4/V5와 기존 탐색 adapter가 선행하며 새 외부 메시지 전송 권한을 만들지 않는다. 추가 UI 연결 미구현. |

raw+저장 copy ABI/다중 target/Set-property/독립 properties+copy의 넓은 혼합 저장은 기존 명시적 지원 제한이다. 정상 보호와 혼합 미구현을 구별하며 이번 목록의 자동 조합 확장으로 만들지 않는다. Helper의 실제 ‘설명으로 작성’과 AI 이미지·협의/shared Confirm·내장 renderer backend는 별도 기존 후속이다. 실제 Windows/WebView2·모바일 기기·DPI/IME·Space/Library 전달은 교차 패키징과 별개로 미검증이다.

## 사용자 확정 팩 경계

2026-10-29 사용자 지시에 따라 **3D Workspace와 권한 부여·관리는 서로 다른 팩**으로 구현한다. 에디터 본체에 두 구현을 직접 결합하지 않는다. 기존 namespace-qualified 계약 ID·명시 provider/팩 연결과 소유 검증을 사용하며, 아직 없는 로더/모드 정책 전체를 새로 만드는 범위로 확대하지 않는다. 팩을 문서에 나눴다는 이유로 실제 구현·권한 검증 완료로 표시하지 않는다.

- 3D Workspace 팩은 실제 프로젝트/Helper/Worker 상태를 읽고 위치·카메라·선택·연출을 표시한다. 이동 완료는 작업 시작/실행 조건·잠금·스케줄이 아니다. 표시 팩이 비활성화되어도 실제 작업과 권한 검사는 유지한다. 실제 작업 제어가 필요하면 기존 에디터/실행 계약을 통해 다시 검증하며 3D 위치가 권한이나 작업 완료의 근거가 되지 않는다.
- 권한 팩은 권한 관리 UI와 실제 작업 허용 판단을 연결한다. 판정은 현재 프로젝트·실제 신원/소유/권한 source를 사용하고 기존 실행 경계·CAS/Review/Confirm 검증을 우회하지 않는다. 권한 팩이 없거나 판정을 확인할 수 없다고 무조건 허용하지 않는다. 기존 검증된 권한 경계는 계속 유지하며 새 허용 판정이 필요한 작업은 명확히 거절한다. 실제 계정 설정·외부 접근권한 변경은 이번 요청 밖이다.
- 에디터는 두 팩의 명시된 계약을 연결하는 어댑터를 제공한다. 3D 팩에 권한 판정/작업 스케줄러를 소유시키거나 권한 팩에 3D renderer를 필수 의존성으로 두지 않는다. 현재 확대 단위는 두 팩의 구현/권한과 독립적이다.


## M12 데이터 반환 후속 경계

직접 소유 ordinary Root의 비void 반환값과 공개 분기는 원래 Invoke·C#·데이터 연결을 유지하는 별도 생성 캡처로 함께 전달한다. [이번 지원·검증과 유한한 잔여](VALIDATION_V666_ROOT_EXECUTION_NONVOID.md)를 기준으로 copy/자식·등록외부 데이터 흐름, 중첩/private·외부 import 관측, 여러 직접 소유 provider의 원자 계약 갱신을 구별한다. 임의 타입/문맥 곱을 새 필수 목록으로 만들지 않는다. M4 호환 정책은 사용자 결정으로 확정됐다: 호출자가 명시적으로 async로 바뀌기 전에는 호환되지 않는 호출을 오류로 거절하고 자동 대기/자동 변환을 하지 않는다. 실제 async 저장·호출·완료 구현은 남아 있다.

비void 동결 코드의 최종 **신규 LF21·CRLF18·패키지/전체 복원/실패 수명관리6, 총45단계(Core/runtime·소유 경계86개 포함)**가 통과했고 집중 실패·최종 증거 및 최신/정상 롤백을 지속 보관했다. [최종 결과](VALIDATION_V666_ROOT_EXECUTION_NONVOID.md).


M12 ordinary 비void 데이터 반환의 기존 소유 흐름(저장/새 copy·자식 직접 본문·등록 외부 함수의 local provider와 저장/새 copy)을 같은 실행 선택·데이터 보존 검증에 연결한다. [지원과 검증 범위](VALIDATION_V666_PUBLIC_RETURN_DATA.md). 남은 M12는 중첩/private/native·외부 import의 실제 호출 계약 결합과 여러 직접 소유 provider의 완전한 명시 대응이다. 정상 예약 이름/소유권 거절이나 구형 자동 migration은 새 필수 항목이 아니다.

ordinary 소유/등록 데이터 반환의 최종 **신규 LF20·CRLF19·패키지/전체 복원/실패 수명관리6, 총45단계(반환 계약/runtime·소유 경계36개 포함)**가 통과했고 최신/롤백·집중/최종 증거를 지속 보존했다. [결과와 경계](VALIDATION_V666_PUBLIC_RETURN_DATA.md).

같은 함수의 여러 직접 소유 ordinary provider·각 target·실제 직접 caller를 전체 명시 대응에 연결한다. 실행 provider의 기존 scoped 배정은 변경하지 않고 다른 provider의 import도 readonly 최종 CAS 관측에 포함한다. [이번 범위와 검증](VALIDATION_V666_ROOT_EXECUTION_PROVIDERS.md). 남은 공개 계약 결합은 중첩/private/native와 등록 외부 import의 실제 caller/provider closure다. 기존 copy provenance가 포함되는 공개 계약 갱신도 같은 경계 대조에 묶고, 완료한 본문 반환 편집이나 독립 새 계약 복제와 구별한다.

여러 직접 소유 provider의 최종 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계(반환/runtime·소유 경계36개 포함)**가 통과했고 증거·최신/롤백을 지속 보관했다. [결과와 경계](VALIDATION_V666_ROOT_EXECUTION_PROVIDERS.md).

소유 ordinary switch-profile private caller도 물리 Root+전체 node 경로로 명시 대응하고 local frame의 반환/실행선만 갱신한다. 재귀적인 leaf 원문 관측과 body target을 같은 후보/CAS/Review 그룹에 유지한다. [중첩 호출 경계와 검증](VALIDATION_V666_ROOT_EXECUTION_NESTED.md).

소유 private caller 결합의 최종 **총45단계(신규39·동등재사용6; LF21·CRLF18·패키지/복원6, 계약/runtime·소유 경계36개 중 신규18·재사용18 포함)**가 통과했고 증거·최신/롤백을 지속 보관했다. [결과와 실제 경계](VALIDATION_V666_ROOT_EXECUTION_NESTED.md).


기존 branch-capable native whole-body의 공개 실행 진입을 원래 instance Invoke/this·재귀/scoped import/소스 위치와 분리해 연결하고 scope object·import 함수의 읽기 관측을 같은 CAS/Review 그룹에 보존했다. 최종 동결 코드의 **신규 LF19·CRLF16·새 패키지/전체 복원/실패 수명관리6, 총41단계**가 모두 통과했다(계약/runtime·소유 경계 38개 포함, 재사용 0). [지원·증거](VALIDATION_V666_ROOT_EXECUTION_NATIVE.md)와 [M12의 유한한 실제 흐름·종료 조건](M12_CLOSURE.md)을 기준으로 남은 caller 계약·copy/자식·등록 import를 구분한다. M4의 확정된 동기 caller 오류 정책과 실제 async 구현, 원래 V2–V9/UI 후속 및 기기 검증은 이 단위로 완료되지 않는다.


피호출자의 공개 분기 갱신 중 호출자 자신이 가진 공개 Root 분기·반환 데이터·readonly 선언을 보존하고, 원래 반환 카드에 연결하는 흐름을 마감했다. 최종 LF19·CRLF16·새 패키지/전체 복원/실패 수명관리6, **총41단계(신규37·동등 근거 재사용4)**가 통과했다. 재사용은 소스/SDK 입력이 동일한 Core 직접 검사 38개에만 해당하며 변경된 후보/API/UI·빌드·패키지는 신규다. [지원·검증·재사용 근거](VALIDATION_V666_ROOT_EXECUTION_CALLER.md). 남은 M12는 [유한한 종료 표](M12_CLOSURE.md)의 private forwarding/postCall 실제 영향, 같은 계약 copy·자식 전체 갱신과 등록 import 경계이며 임의 조합을 새 필수 행으로 늘리지 않는다.


기존 private 실행 frame·그 분기 영역 안의 callee 공개 계약 갱신을 연결했다. caller의 source/enum/서명/owner/종료점과 원래 `17`·out `10`·부모 분기/연속 실행을 보존한다. 최종 LF19·CRLF16·새 패키지/전체 복원/실패 수명관리6, **총41단계(신규33·동등 근거 재사용8)**가 통과했다. 재사용 Core 직접 검사38개 및 경합 경로 수리에 영향 없는 기존 LF 4단계와, 신규 충돌·CRLF API/UI·빌드·패키지 검사를 구분하고 [지원·증거·실제 경계](VALIDATION_V666_ROOT_EXECUTION_FORWARDING.md)에 기록했다. 이후 [유한한 M12 표](M12_CLOSURE.md)의 실제 소비자 관측/명시 wrapper 계약, 같은 계약 copy·자식 전체 갱신과 등록 import를 마감하며 조합별 필수 항목을 새로 만들지 않는다.


ordinary IInvoke/native import와 legacy NoBranch wrapper를 공개 계약 갱신의 읽기 관측·생성 receipt 갱신에 연결했다. 원래 profile·C#·IO·source identity·scope/자체 분기를 보존하고 실제 public caller만 명시 대응한다. 최종 **LF20·CRLF16·새 패키지/전체 복원/실패 수명관리6, 총42단계(신규38·동등 재사용4)**가 통과했다. [정확한 지원·신규/재사용 근거·증거와 잔여](VALIDATION_V666_ROOT_EXECUTION_OBSERVERS.md)를 따른다. wrapper의 실제 공개 OriginalResult 명시 연결과 copy/자식·등록 외부의 전체 갱신은 유한한 M12 표에 유지한다.


직접 소유 Root caller의 공개 OriginalResult wrapper·기존 데이터 ABI와 원본 계약의 전체 명시 wrapper 선택을 연결했다. legacy NoBranch adapter·원문·ID·자체 enum/연결은 보존한다. 최종 **LF20·CRLF16·새 패키지/전체 복원/실패 수명관리6, 총42단계(신규42·재사용0)**가 통과했다. [정확한 지원/검증/호환/증거](VALIDATION_V666_ROOT_EXECUTION_WRAPPERS.md)를 따른다. 남은 M12는 같은 계약 copy·자식 본문이 포함된 정의 전체 갱신과 등록 외부 readonly import 관측 두 흐름이다.


같은 공개 계약 copy·직접 자식 target과 inherited-only 관측을 전체 명시 반환/호출자 갱신·checkpoint/Review/최종 CAS에 연결했다. 원문/IO·donor provenance·부모 소유권·기존 화면을 보존한다. 최종 **LF19·CRLF16·패키지/전체 복원/실패 수명관리6, 총41단계(신규28·동등 재사용13)**가 통과했다. [범위·중단 복구·신규/재사용 증거와 잔여](VALIDATION_V666_ROOT_EXECUTION_OWNED_UPDATES.md)를 따른다. 유한한 남은 M12는 등록 외부 import/manifest/scope의 readonly 관측 결합이다. M4 및 고정 UI/실기기 검증은 별도다.


## M4 완료의 일반 분기 복귀 후속

직접 소유 ordinary root 안의 기존 C# Result 동작은 완료의 literal 포트/연결과 원문을 보존하는 일반 지역 분기로 전환하고 같은 ID로 async 재활성화한다. UI 표시명과 C# 식별자를 분리한다. async ordinary root의 Set 계획도 기존 소유/타입/원자 검증을 재사용한다. [정확한 경계](M4_ASYNC_TRANSITION.md).

유한한 M4 후속은 **공개 함수·호출자의 완료 일반분기 어댑터**, **Result 없는 next/native/whole-body 원문 보존 어댑터**, **새/내부 소유 본문과 실제 보조 편집 통합**이다. 앞선 지역 Result 지원과 Set 지원을 다시 잔여로 세지 않는다. 정상 비소유/override/ref/실제 await 거절 및 선택적 legacy 자동 변환은 새 필수 조합이 아니다. M11/M12는 닫힌 상태를 유지한다. V2–V9와 별도 팩·backend/종류 호환성 결정, 실제 기기·전체 UI·Space 전달은 기존 별도 잔여다.

완료 일반 분기·ordinary async Set의 동결 코드 `a24e3e2`를 신규 47단계(재사용 0)로 검증하고 최신/롤백 및 전체 증거를 보관했다. [최종 검증 기록](VALIDATION_V666_ASYNC_COMPLETION.md).


## M4 공개 함수 완료 후속

직접 소유한 기존 ordinary 함수/Blueprint target·직접 Blueprint 호출자의 완료를 같은 ID·값·literal 연결의 일반 공개 Result로 전환한다. C#·IO·지역 Result를 보존하며 기존 반환 카드의 명시 선택/이름 편집과 async 재활성화에 연결한다. [정확한 경계와 호환성](M4_PUBLIC_COMPLETION.md). Root 전환·실제 호출자 전체 관측과 final CAS를 유지하고, 재시작의 무관한 lazy body와 필수 importing body 누락을 구분한다.

다음 M4 흐름은 Result 없는 소유 next/native/whole-body 본문의 원문/출력 보존 어댑터, 새/내부 소유 본문의 명시 전환, property 보조 편집이다. 완료한 ordinary 공개 완료/지역 Result/Set을 다시 조합별 잔여로 추가하지 않는다. M11/M12는 관련 회귀를 제외하면 닫힌 상태를 유지하며 V2–V9·팩/backend·종류 호환성 및 실제 기기/전체 UI/Space 전달은 기존 별도 잔여다.

공개 완료의 최종 동결 `262f1a5`를 신규 52단계(재사용 0)로 검증하고 최신/롤백·전체 증거를 보관했다. [최종 검증 기록](VALIDATION_V666_PUBLIC_COMPLETION.md).

## M4 속성 편집 후속

기존 직접 소유 async root의 속성 검색·receiver/소비 연결·필드 쓰기를 원래 속성 UI와 propertyPlan 후보에 연결한다. 전환 가능 여부와 현재 async 시계 표시를 분리하며 프로젝트 관측을 최종 CAS까지 유지한다. 물리 원본 관측과 저장 응답 후보 해시를 분리해 후속 C# 편집·재시작을 허용하고, 전체 Confirm 뒤 관측을 종료해 반복 저장을 유지한다. [정확한 경계와 검증 계획](M4_ASYNC_PROPERTIES.md). 기존 Result 없는 본문 어댑터와 새/내부 소유 본문 전환은 남고, 기존 copy/slot/private 보호를 새 조합 요구로 확대하지 않는다. 최종 검증 수치는 종료 기록에서 확정한다.

속성 편집·관측/CAS의 최종 동결 `e4c0646`를 신규 48단계(재사용 0)로 검증하고 최신/롤백·전체 증거를 보관했다. [최종 검증 기록](VALIDATION_V666_ASYNC_PROPERTIES.md).
