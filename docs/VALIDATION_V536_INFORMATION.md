# v536 기존 정보 선택과 새 중첩 속성 — 한정 단위

`cd35313c` 이후 원본 새 속성 타입 선택창에서 **기존 소유 정보(schema)**를 골라 새 compound 속성을 만들고 중첩 값을 편집하는 단위다. 원본 HTML/CSS·메뉴·크기·배치는 바꾸지 않았다. 정보 자체의 정의/기본값 편집, legacy inline 복합 및 raw source 결합 Save는 아직 미완료다.

## 원본과 연결

원본 `app.js`의 `choosePropertyType`은 정보를 검색/선택하고, `informationDefaults`/`propertyDefault`는 정보의 기본값 또는 primitive/중첩 fallback을 만든다. linked 정보의 자식 정의는 객체에서 직접 편집하지 않는다. 이 경계대로 기존 타입 팝오버의 정보 그룹과 linked 값 위젯을 연결했다. 별도 복합 타입·편집창을 발명하지 않았다.

- 현재 선택은 root 소유 schema의 primitive·중첩 compound·상속 필드와 그 내부 multiple을 지원한다. 기본값이 없는 native 정보는 원본 fallback의 숫자0/빈 글자/false와 multiple 첫 항목을 사용한다. 없는 custom 기본값 저장 문법을 추가하지 않았다.
- 참조/함수·imported 정의·custom 값 metadata가 필요한 기본값은 대상을 추측하지 않고 선택 불가로 표시한다. 새 속성 자체의 multiple 전환과 정보 원본 custom 기본값 저장은 이번 범위 밖이다.
- `information-definition`은 새 이름·정보 ID·상속/중첩 source hash proof·정확한 typed JSON을 기존 `MixedOwnerCopyEdits`→SlotBatch/ApplySlots 한 후보/CAS에 넣는다. 원본 정보·부모·외부 소유 요소를 쓰지 않으며 native schema/전체 graph/Review 그룹 검사를 유지한다.
- 중첩 값·불완전 입력·proof는 한 private cell에 보관한다. 기존 Undo·창별 presentation·journal/receipt 조회를 사용하고 최신 source proof로 자동 치환하거나 실패 기록을 삭제하지 않는다. primitive/기존 receipt 호환은 유지한다.

## 격리 검사

로그는 `/workspace/scratch/v536-information/`에 있다. 아래 숫자는 공통 준비를 포함한 PASS 묶음이며 독립 테스트 수로 합산하지 않는다. 사용자 자료/계정/인증파일·로그인·유료 추론·사용자 프로젝트 실행은 사용하지 않았다.

| 검사 | 실제 결과 |
| --- | --- |
| `v536_information_types.py` | `metadata4.log` 3 PASS. 상속·중첩/multiple fallback, exact long/한글의 결정적 compound 후보, stale/불완전 proof·잘못된 값/이름·외부/ref/중복 전체 거절. inherited/nested custom metadata도 추측하지 않고 unavailable, 표시명 metadata는 유지한다. 순수 metadata이며 엔진/renderer 검사 아님 |
| 기존 primitive metadata | `primitive-metadata-regression.log` 4 PASS. 부적합 원래 값 거절, 명시 schema/value/설명, 정확한 long 유지, hash/소유권/중복 보호 |
| 실제 엔진/Chromium 정상 | `ui-normal2.log` 4 PASS. 원본 추가/검색/선택→Ctrl+Z→재선택, 중첩 long/한글, 저장 전 재시작, 한 후보 Save/cold, Review 취소·명시 compiler Confirm·확정 후 cold |
| 취소 | `ui-cancel2.log` 3 PASS. 입력 흐름 후 명시 취소/cold, 정보 원본·checkpoint·owner 불변 |
| checkpoint 쓰기 실패 | `ui-storage1.log` 5 PASS. schema/등록/owner 전체 미적용·입력 보존→cold 명시 재시도→Review/Confirm/cold |
| 응답/조회 유실 | `ui-loss1.log` 5 PASS. 실제 적용/조회 응답 유실, cold receipt 조회로만 복구·새 applySlots 없음, 중복 생성 방지와 Review/Confirm/cold |
| 실제 정보 source 변경 | `ui-conflict1.log` 3 PASS. 격리 정보 파일에 동료 변경 후 Save 전체 거절·원문/proof/동료 source 보존, cold 재시도도 원래 proof로 거절 |
| 값 거절 후 재시도 | `ui-reject1.log` 5 PASS. 중첩 long 범위 오류는 설명/schema/등록 전체 미적용, 원문 cold 복원→명시 수정→Save/Review/Confirm/cold |
| 기존 혼합 UI 회귀 | `root-copy-regression.log` 4 PASS. 기존 타입 거절→Undo→copy 결합·응답/조회 유실→cold·Review 취소/compiler Confirm. 부모/원본/다른 target 보존 |
| 마지막 기본/독립 창 | `ui-normal-final.log` 4 PASS / `ui-view-final.log` 5 PASS. 최신 Workspace 키 라우팅으로 같은 Info 편집/저장/cold/Review/Confirm, 독립 창 local Undo가 Workspace 이력을 소비하지 않음 및 폼 밖 실제 Workspace Undo/Redo·source 불변 |

초기 `metadata1.log`는 fixture가 공통 `{ok,result}`를 array로 직접 읽은 오류다. `engine1`은 추가 변수와 기존 `identity`의 이름 충돌로 컴파일 실패해 기존 변수를 재사용했다. `ui-normal1.log`는 정보 선택 뒤 renderer의 `name` 지역 변수 TDZ를 재현했다. `nameInput`으로 수정한 뒤 새 엔진으로 검증했다. 입력과 실패 로그를 보존했고 CAS/보호 assertion은 완화하지 않았다. 최종 UI 생성 엔진은 `engine5.json`(경고0)이다. 마지막 helper 빌드는 `helper-build3.log` 경고0으로, 모든 관찰한 상속/중첩 source의 미연결 custom 기본값을 확인하는 한정 guard를 추가했고 metadata4에서 정상/비지원 모두 재검증했다.

독립 창 첫 Undo는 ready/focus 확인 후에도 실패했다(`ui-view1.log`, `ui-view2.log`). 격리 CDP 관찰에서 local handler의 Control 입력은 도달하고 Undo1개/원래 입력 참조도 동일했지만 z 입력은 도달하지 않았다(`ui-view3-debug.log`). `workspace-host.js`의 document capture가 private Workspace 이력이 있으면 Ctrl+Z를 먼저 소비했다. 객체 폼을 전역 Workspace Undo 대상에서 제외해 기존 local Undo가 처리하게 했다. 폼 밖 history 동작은 바꾸지 않았다. 최종 View5개 PASS는 local Undo 전후 Workspace 이력이 같음과 폼 밖 실제 Undo/Redo도 확인한다. CDP 관찰 코드는 최종 테스트에서 제거했고 소유권/CAS/입력 비교 가드는 완화하지 않았다.

`information-scrolled.png`를 실제 열어 기존 linked 카드의 `Nested`/`Stats`와 중첩 한글·정확한 long을 확인했다. 저장된 fixture를 다시 읽었고 source byte는 불변이었다. 1600×1100에서 해당 root 영역은394×256px다. 원본 class/controls 재사용과 해당 영역 확인이며 전체 pixel equality/native Windows 검사는 아니다. 정상 최종 캡처의 위쪽 스크롤과 새 카드의 별도 캡처를 구분한다.

## 정확한 잔여

1. 정보 자체의 정의/custom 기본값, legacy inline 복합의 중첩 정의 변경. native compound/reference 타입은 있으므로 전체 backend 부재로 세지 않는다. 원본 정보 기본값과 native typed data 저장 계약을 먼저 결부해야 한다.
2. dirty raw source와 owner/schema·독립 창의 결합 Save. source View의 properties owner-only endpoint 사용 및 primary dirty raw 입력의 View Review 자동 Apply 차단은 유지한다. 원래 source/path/hash·checkpoint를 같은 후보/CAS에 결부한 뒤에만 해제한다.
3. ABI 교차 문맥·다른 계획 혼합과 모바일 최종 조작은 `V536_REMAINING_ACCEPTANCE.md`의 고정 잔여다. 이미지·협의·내장 렌더 backend를 이번 복원에 추가하지 않는다. 실제 Windows/Android/touch·DPI/IME·Library 전달은 미검증이다.

독립 properties View 및 패키지/깨끗한 checkout 결과는 아래에 추가한다. 전체 UI 복원 완료가 아니다.
