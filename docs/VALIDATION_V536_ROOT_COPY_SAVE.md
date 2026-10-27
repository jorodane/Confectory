# 저장 copy의 Root 복귀 Save 수용

기준은 게시 `0edf63d`와 저장소 `196c605`의 v536 ZIP이다. 새로운 조합을 추가하지 않고, 직전 private ordinary frame 편집의 기존 **내부 편집→Root 빵부스러기→저장**을 마감한다. 원본의 빵부스러기는 자식 definition/graph를 부모의 graphDraft에 넣어 보관하고, Root의 `saveDefinition`은 그 전체 graph를 저장한다. source/override의 공개 입출력은 원본에서 다시 가져와 유지한다. ZIP/Git blob·원본 JS SHA 및 함수 위치는 evidence JSON에 기록했다.

## 실제 누락과 연결

기존 `saveEntries`는 private 화면에서만 형제 frame 입력을 수집했다. Root 복귀 후에는 입력이 남아도 현재 frame 입력으로 분류하지 않아 요청 전에 거절했고, 서버도 기준 graph가 물리 Root이면 frame 후보를 거절했고, 독립 창 어댑터는 private frame payload를 일반 Root 계약 편집으로 오인했다. 실제 기본 UI와 cold에서 이 차단을 재현했다.

Root에서도 같은 author surface·owner·copy의 명시 private 입력만 모으고 각 edit에 원래 frame ID를 보낸다. 단일/복수 private frame 모두 기존 한 격리 후보에서 실제 node·소유/출처·원래 checkpoint·전체 source closure를 검증하고 `WriteChecked` CAS 한 번으로 저장한다. 각 step은 그 frame의 실제 basis로 처리한다. Root 자체를 private frame edit 대상으로 지정할 수 없으며 공개 override 계약은 변경하지 않는다. 독립 창은 기존 owner/hash/nonce/view 결박을 유지하며 Root 아래 private frame ID와 ordinary body action이 명시된 요청만 이 기존 후보로 전달한다. 기존 단일-frame 형식과 보관 ledger는 원래 graph에 결박해 복구하고, Root 응답 유실/재시작도 조회 후 결과를 확인한다. 현재 viewport가 달라도 ledger는 원래 graph의 edit 형식으로 비교한다.

원래 창·카드·버튼/단축키·빵부스러기 배치는 바꾸지 않는다. 기존 dirty 표시에 보관 private 입력도 반영하며 Root에 새 메뉴나 자동 대상 선택을 추가하지 않는다. 편집/Undo는 frame별로 유지하고 저장된 frame의 경계만 정리한다. Root의 다른 입력, 다른 창/owner/target·프로젝트 입력을 묵시적으로 합치지 않는다. 이번 frame 형식 밖의 계획이 함께 있으면 입력을 보존하고 거절한다. 미적용 조회와 원래 기준 불변이 확인돼야 교정 재시도가 가능하며, 실패 기록을 무조건 지우지 않는다.

Save는 초안 보관이다. 물리 원본 반영과 컴파일은 기존 명시 Review/Confirm이며 취소·오류·충돌은 원문/값/참조/부모/외부·출처를 보존한다. 공개 override는 원래 입출력 계약을 유지하고 구현만 바꾸며 독립 계약 복제는 필수 제외다.

## 실제 검사

집중8흐름51확인과 최소 영향 회귀27확인이 통과했다.

단일 frame은 기본 창, 복수 frame은 독립 창 및 실패 흐름에서 원래 Root 버튼으로 저장했다. 실제 blueprint 요청의 기준 id가 Root이고 모든 edit의 frame이 명시 private ID인지 확인했다. 기존850×600 창과 원래 코드/핀 조작, frame별 Undo/Redo·C# 편집 취소·cold·마지막 잘못된 핀의 전체 미적용/명시 보완·실제 쓰기 실패·응답 유실 조회·실제 peer checkpoint 충돌·다른 창 입력·프로젝트 전환을 실제 엔진/렌더러 fixture로 검증했다. 저장 graph 전체를 비교해 private frame 계약·원래 Root 입출력·정확한64비트 local·순서/실행선·helpers·copy 출처를 지킨다. 다른 창 입력은 보존하고 검토 전 fixture에서 명시 취소한 뒤 Confirm한다.

| Root 흐름 | 확인 수 |
|---|---:|
| normal | 6 |
| view | 6 |
| invalid | 7 |
| storage | 7 |
| loss | 7 |
| conflict | 4 |
| context | 7 |
| projects | 7 |

기존 private Save/핀 편집, saved-copy ABI의 소유·nonce·등록 원본·cold·명시 Confirm 및 제품의 Review/Confirm/CommitPlan의 성공·검토 후 late race·proof 누락·path escape를 최소 영향 회귀로 확인했다. 명령·종료 코드·환경/자원과 source SHA는 `evidence/v536-saved-copy-root-save/focused-verification.json`을 따른다. 로그/화면/fixture는 scratch 증거로 보관하며 사용자 자료를 사용하거나 영구 삭제하지 않는다.

## 원래 요구와 잔여 판정

| 기존 사용자 조작 | 원본 근거와 현재 결과 | 판정 |
|---|---|---|
| ordinary private 핀·수동 본문 편집 후 Root 복귀 Save | 원본 빵부스러기와 Root 전체 graph 저장. 이번에 단일/복수·기본/독립 경로 연결 | 이번 지원 경로 완료 |
| 원본 계약 갱신 wrapper와 다른 frame의 일반 입력이 같은 구현에 존재 | 원본 `data-wrapper-refresh`가 최신 callee 계약을 선택하며 내부 편집은 부모 graph에 보관된다. 현재 ordinary frame 형식은 wrapper 계획을 함께 수집하지 않는다 | 기존7행/A4–A6의 영향 후보 결합 잔여다. 별도 독립 기능이나 모든 C# 조합을 새 필수로 추가하지 않는다 |
| 기존 forwarded 연결을 유지하려면 private 부모 계약/본문도 영향받는 갱신 | 원본은 기존 내부 기능 정의를 부모 graph에 저장한다. 기존 일반 ABI/forwarded 검증 기반은 있으나 copy의 출처/소유 closure와 다른 frame 계획 결합은 이 단위 밖 | 실제 영향이 있을 때만 명시 대응·import/본문을 같은 후보로 검사하는 기존 잔여다. 공개 override 구조 변경을 허용하는 작업이 아니다 |
| opaque/whole-body C#·import 사용이 있는 copy의 계약 갱신 | 원본 수동 C#·원본 계약 갱신은 기존 조작. 엔진의 수동 본문·계약 검사 기반과 copy closure 어댑터 결합을 구분한다 | 기존 source closure 결합 잔여. 본문을 추측해 자동 재작성하거나 새 backend가 없다고 일괄 분류하지 않는다 |
| override 독립 계약/새 ID 복제·전체 target 자동 선택·alias/import 전용 새 UI | 사용자 확정 필수 제외이거나 원본에 없는 추가 제안 | 이번 미구현으로 확대하지 않음 |

위 영향 후보 결합은 같은 고정7행/A4–A6 항목으로 한 번만 관리한다. 이름/타입/핀 수/ref/out/순서의 가능한 순열을 별도 새 작업으로 늘리지 않는다. 후속8행의 남은 여러 함수 C#/중첩/copy 문맥과 9행 고급 핀 타입·표시명/생성 식별자, I6 로컬 아이콘·B2 실제 배지·M4 async/M11 C#→graph/M12 root 분기는 별도다. 이미지/협의/렌더 신규 backend는 이 복원 범위 밖이다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 미완료다.
