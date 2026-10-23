# v536 선언 삭제·복구 — 서버 계약과 목록 연결

**서버의 실제 등록 해제/복구 경로와 목록 표시를 검증한 체크포인트다. 사용자 삭제·복구 메뉴의 전체 연결은 아직 완료하지 않았다.** 전체 v536, Windows/native 실행이나 게시 완료 보고가 아니다. 실제 사용자 자료를 변경하거나 영구 삭제하지 않았고 `/tmp` fixture만 사용했다.

## 삭제의 의미와 경계

삭제는 프로젝트 manifest의 선언 등록을 해제한다. 원본 `.celem` 파일은 그대로 두고, 당시 원본·작업 초안·소스 proof를 소유자별 draft checkpoint의 복구 기록에 보관한다. 다른 곳에서 참조하는 부모/자손/선언은 기존 PlanRemoval에서 차단하며, 참조를 자동 정리하거나 자손을 Root로 옮기지 않는다.

- `EditWorkspace.Retirement`의 apply는 현재 plan token과 관측한 전체 unit state가 정확히 맞을 때만 manifest 작업 사본을 바꾸고 선택한 선언을 활성 편집 목록에서 제외한다. 새 편집 뒤 오래된 plan은 거절한다.
- 미확정 삭제의 recover는 이전 등록과 당시 편집 초안을 복원한다. 확정된 삭제의 recover는 보관된 원본 파일 proof를 재확인하고 등록/초안 복구를 stage한다. 복구 stage 취소는 원본을 쓰지 않고 삭제 보관 상태로 돌아가며, 복구 과정에서 수정한 shared draft도 보관한다.
- 한 번에 하나의 pending/restoring 등록 transaction을 처리하며, 복구 기록은 최대32개/8MiB다. 한도를 넘는 새 삭제나 복구 취소는 실제 unit 변경 전에 거절한다. 복구 기록을 자동 삭제하지 않는다.
- Export/Restore가 복구 기록과 소유 namespace/path/kind/원본 hash·본문·stable ID를 검증한다. 복구된 등록과 source는 `retirementGroup`으로 함께 Review해야 한다. 새 source 권한이나 계정 승낙으로 취급하지 않는다.
- 등록 membership 변경은 기존 생성 workflow처럼 의미 편집 이력의 OWNERSHIP_CHANGED 경계를 사용한다. 일반 Undo로 삭제를 추정 복원하지 않으며 명시적 복구를 사용한다. 기존 이동 그룹 이력은 별도 검증 결과를 유지한다.

## 최종 확정과 원본 보존

`Changes`의 보관 원본 관측 행은 실제 declaration ID/path/hash/원본 text이며 빈 source나 sentinel이 아니다. `FileStream.CommitPlan`은 명시적 writes와 read-only checks를 같은 소유 root lease와 충돌 검사 안에서 처리한다. 보관 원본은 checks여서 재인코딩하거나 쓰지 않는다. manifest와 실행 활동 기록 등 실제 쓰기만 원자적으로 적용하고, 실패 시 쓰기 대상만 기존 rollback 경로로 복원한다.

기존 ChangeSet의 후보 준비·Validate/Check/Build·Review token 검증을 그대로 거친다. 일반 Confirm은 checks가 없으면 기존 Commit을 계속 사용한다. Accept/Acknowledge가 확정된 삭제/복구 상태와 checkpoint를 대응시키며 다른 source 초안을 승격하거나 삭제하지 않는다.

현재 actual 프로젝트 fixture는 진짜 compiler-backed Confirm이다. pack 자체 Confirm의 기존 owned-syntax-only 한계는 이번 작업에서 바꾸지 않았다.

## 실행 결과와 수정한 실패

- retirement-build1의 local 변수 충돌을 수정해 build2 compile exit0.
- retirement-contract1은 BOM을 가진 fixture의 inventory 조회에서 SYNTAX로 중단했다. 일반 File.ReadAllText 기반 조회와 Documents의 raw UTF-8 decoding이 달라 선두 BOM을 문자로 넘기던 결함이었다.
- `Documents.Decode`는 **첫 UTF-8 BOM만** 읽기 시 제외한다. 원본 bytes와 contentHash를 유지하고 strict UTF-8 및 비선두 BOM 문법 거절을 유지한다. 캐시 형식 version을 갱신했다. CLI/authoring/test build는 경고0/오류0. `CoreTests.test_documents_accept_initial_utf8_bom_without_changing_source_bytes` **1 passed/0 failed**: cached/snapshot reader, 원본 bytes 보존, invalid UTF-8 및 비선두 BOM 거절.
- retirement-contract2는 첫 stale plan 거절을 통과한 뒤 test의 transport token 변수와 archive token 변수가 충돌하여 HTTP403으로 apply 접수 전에 종료했다. 변수명을 분리했으며 인증 검사를 우회하지 않았다.
- **retirement-contract3 전체 exit0, 실제6건**: stale plan/새 초안 보존, 실제 unregistration와 취소 복구, Save/cold, 명시적 compiler Confirm 및 retained BOM 원본 byte-for-byte 보존, 확정 archive의 cold/복구 stage 취소, 복구 Save/cold/부분 Review 거절/그룹 compiler Confirm. case `/tmp/confectory-element-mutation-778jqgms`.
- 공개 복구 metadata·목록 filtering·Browser discard 라우팅을 추가한 build4는 변수 이름 충돌로 실패했고 build5에서 수정했다. **retirement-projection1 전체 exit0, 실제 렌더러2건**: confirmed inventory에 남은 삭제 항목도 숨김, Browser discard API가 비파괴 복구와 checkpoint 저장 후 실제 row 복원. Unit private111과 모든 final bytes 보존. 이 검사는 Delete 메뉴 클릭을 검증한 것이 아니다.
- 복구 기록 한도를 선검사하는 최종 build6 compile exit0. 이 변경으로 영향을 받는 **retirement-contract4 전체 exit0, 실제6건 재검증**. case `/tmp/confectory-element-mutation-4fwkc0u9`. 확정된 fixture를 초기화하거나 결과 불명확한 Confirm을 재시도하지 않았다.

실제 수정 대상 외 Monster 초안·Unit private111·Slime/다른 source를 보존했다. Confirm된 삭제에서는 보관 파일 BOM까지 그대로였고, 이후 복구의 별도 Review/Confirm에서 명시적으로 검토한 이전 편집 초안만 source에 반영했다. token/credential/OAuth/유료 추론·새 실계정 권한은 사용하지 않았다.

## 남은 일

1. 원본 삭제·복구 메뉴의 주요 연결과 UI 검증은 아래 후속 절에 기록했다. 다중 선택 메뉴 수정 재검증과 게시 전 전체 통합 검증을 남긴다. stale plan은 자동 재적용하지 않는다.
2. Browser 복구 선택과 header Save/취소/확정은 pending/restoring manifest 및 전체 support group에 연결했고 실제 cold/Review/Confirm을 확인했다. 세부 검증·남은 경계는 아래 후속 절을 따른다.
3. 삭제된 source의 열린 창 잠금/입력 보존·복구 후 proof 갱신·모달 inert/focus·Save 실패는 아래 실제 renderer 결과로 확인했다. saved receipt before/after registration 구조와 malformed import, 체크 경로/CAS의 추가 집중 검사는 게시 전에 남아 있다.
4. 카테고리 폴더 이동은 아직 미구현이다. folder 위치와 engine inheritance/typed Contains를 분리하는 원본 어댑터를 이어간다.
5. 전체 회귀·정밀 화면 비교·이미지/전투로그/실행창 등 고정 잔여, Windows 패키지·checkout·커밋/push는 미완료다. Linux/Chromium 결과를 실제 Windows/Android 실행 검증으로 해석하지 않는다.

## 원본 사용자 메뉴 연결 — 2026-10-23 후속

`v508-runtime.js`의 objectActions와 Delete 키, `elementEditorAPI.remove`를 같은 plan→원본 `의미 객체 삭제` 모달→명시적 apply 경로에 연결했다. 원본 `app.js:1874`의 모달 제목/삭제 버튼/배치를 재사용한다. 데모의 자손 자동 Root 이동은 복사하지 않으며, 실제 참조를 차단한다. 원본과 공유 초안은 archive에 보존하고 삭제는 manifest 등록 해제다. 화면 문구는 작업 사본 적용·보관 저장·최종 Confirm을 구별한다.

기존 Browser 메뉴에 조건부 복구 선택을 연결하고, 기존 Save/변경 취소/확정 바는 active pending/restoring manifest를 사용한다. 복구 Review는 변경 없는 support 원본까지 서버가 요구하는 전체 묶음을 선택한다. 다른 객체의 private 입력 때문에 이 묶음을 불필요하게 막거나 지우지 않는다. 삭제된 객체의 열린 창은 닫거나 입력을 지우지 않고 본문과 쓰기 버튼을 잠근다. 복구 후 다시 열 때 최신 schema/hash/revision을 확인한다. 별도 영구 관리 패널·새 레이아웃은 추가하지 않았다.

실제 UI 검사 `v536_elements_browser_retirement_ui.py`, `elements-browser-retirement-ui-1.log`: **전체 exit0, 6건 통과**, fixture `/tmp/confectory-element-mutation-5pezy2xf`.

1. 실제 삭제 메뉴로 참조된 Unit 삭제 차단, 자손/다른 입력 보존.
2. 원본 삭제 모달 닫기 시 적용 없음, app.inert 잔류 없음.
3. Other 삭제 클릭→apply/Save→목록 숨김, 최종 source bytes/Unit private111 보존.
4. 기존 header 변경 취소로 저장된 삭제 복구, unrelated private111 보존.
5. 실제 cold 재시작→Review 취소→새 Review/명시적 compiler Confirm. manifest에서만 등록 해제, 보관된 Other UTF-8 BOM 원본 완전 보존.
6. 확정된 삭제의 cold 재시작→원본 Browser 메뉴 복구→전체 group Review/명시적 compiler Confirm. 등록 복원, 다른 source/입력 보존.

실제 캡처 `retirement-pending.png`, `retirement-restoring.png`를 위 fixture에 보존했다. 복구 화면을 실제 열어 확인했다. 기존 header/검색/폴더 트리 배치를 유지하며 성공 상태 패널을 새로 추가하지 않았다.

추가 경계 검사 첫 실행 `elements-browser-retirement-ui-boundaries-1.log`는 처음 3건 통과 후 복구 요청 미시작으로 실패했다. fixture `/tmp/confectory-element-mutation-kka1hwgq`. 선택한 private 입력 차단, stale plan 거절, 반복 클릭 단일 apply·Save admission 실패 뒤 header Save·열린 삭제창 잠금을 확인했다. 그다음 배경 상태 조회와 복구 메뉴 클릭이 겹치면 `if(busy)return`으로 사용자 요청을 버리는 경로를 발견했다. 같은 프로젝트/창/receipt가 유지된 경우에만 조회 종료를 기다리도록 수정했다. 오래된 plan 자동 재적용이나 실패 결과 자동 승격은 하지 않는다. 수정 뒤 추가 검사 결과는 아래에 별도 기록한다.

`elements-browser-retirement-ui-boundaries-2.log`는 수정 후 **전체 exit0, 실제 렌더러4건 통과**했다. fixture `/tmp/confectory-element-mutation-j0xpeo25`.

- 일반 Delete 키로 선택된 private 입력이 있으면 삭제 전에 멈추고 입력 보존.
- 모달 표시 후 공유 draft가 바뀌면 이전 plan 거절 및 이전 버튼 재사용 차단.
- 이중 클릭 apply 1회. 실제 서버의 stale transport admission으로 Save 거절1회 주입, 적용됨/저장 미확인을 구별하는 안내 및 header Save 재시도 확인. Delete 재적용0회. 열린 삭제 대상은 입력을 보관하면서 본문과 쓰기를 잠금.
- 복구 메뉴와 최신 proof 재조회 후 다시 열기를 통해 기존 shared draft 보존. 원본 파일 변경 없음.

다중 선택 추가 검사 `elements-browser-retirement-ui-multi-1.log`는 메뉴 선택 전에 실패했다. fixture `/tmp/confectory-element-mutation-g3yjar_j`, 삭제 미실행. Workspace 우클릭 팬 처리가 embedded Browser의 선택 메뉴를 거치지 않고 단일 객체 메뉴를 열었다. `workspace-host.js`에서 대상 window를 전달하고 `elementBrowser.context`로 원래 선택 메뉴에 연결했다. 이동/캔버스 팬 규칙과 레이아웃은 바꾸지 않았다. 수정 뒤 결과를 아래에 따로 남긴다.

다중 선택 두 번째 실행 `elements-browser-retirement-ui-multi-2.log`는 실제 2개 대상 apply/Save 뒤, 열린 embedded Browser에 삭제된 행이 남는 결함을 재현했다. fixture `/tmp/confectory-element-mutation-q3mkoi9h`. 서버 active units와 관계 map에는 두 대상이 없으며 원본 파일은 그대로였다. `removalRefresh`가 기본/독립 요소 창의 기존 renderer를 재실행하도록 연결했고, 기존 header 변경 취소에도 같은 갱신을 사용한다. schema/입력 저장소를 교체하거나 초안을 삭제하지 않는다. inactive source의 상태 조회는 중단하고 기존 늦은 조회 결과는 세대 검사로 적용하지 않는다. 수정 뒤 build6 compile exit0이며, 다중 선택·열린 창 경계 재검증 결과는 다음에 기록한다.


`elements-browser-retirement-ui-multi-3.log`는 build6에서 **전체 exit0, 실제 렌더러2건 통과**했다. fixture `/tmp/confectory-element-mutation-csz5avpx`: embedded Browser의 두 항목 다중 선택→원본 선택 메뉴→단일 apply/Save→정확한 두 행 숨김, 기존 Project Browser 변경 취소→전체 복구. Unit private111·부모·다른 원본 bytes·모달 정리를 보존했다. `retirement-multi-recovered.png`를 실제 열어 확인했다.

다중 갱신 수정의 영향을 받는 열린 편집창 경계를 재검사한 `elements-browser-retirement-ui-boundaries-3.log`는 앞 3건 뒤 복구 후 다시 열기의 idle 대기에서 실패했다. fixture `/tmp/confectory-element-mutation-5sjtvcy4`. 복구 자체와 원본 보존은 성공했지만, 잠긴 창의 이전 schema revision으로 status를 반복 조회했다. 복구된 창을 다시 열어 최신 proof를 받기 전에는 그 조회를 중단하도록 수정했다. stale schema를 자동 승인하거나 새 revision으로 기존 입력을 덮지 않는다. build7 compile exit0. 후속 결과는 아래에 기록한다.


`elements-browser-retirement-ui-boundaries-4.log`는 build7에서 **전체 exit0, 실제 렌더러4건 통과**했다. fixture `/tmp/confectory-element-mutation-7db62zsg`. 위 3건과 복구→다시 열기→최신 proof/상태 조회 완료·원본 및 shared draft 보존까지 확인했다. 실행 중 검사는 남기지 않았다. 새 원자성/내구성 범위를 확장하지 않았다.

이번 사용자 메뉴 묶음의 증거는 주요 흐름6건, 경계4건, 다중 선택2건이다. 이는 다른 시점의 독립 테스트 묶음이며 Windows 네이티브 검증 건수가 아니다. 최종 compile build7 exit0, canonical resource62/text53 hash·size와 JS/Python 구문 검증, diff check 통과. Context menu lifecycle, private workspace links/deletion inverse, private layout history, 기존 projection/review admission 집중 회귀도 통과했다. 카테고리 이동과 전체 v536 UI 수용·Windows 패키지·checkout·commit/push는 여전히 미완료다.
