# v536 Browser 카테고리 분류 연결 검증

현재 work/current의 미게시 변경이다. main/Android/원본 ZIP/사용자 프로젝트를 변경하지 않았다. 실행은 복사한 `/tmp/confectory-element-mutation-*` 격리 프로젝트에서만 했으며, 실제 계정·토큰·OAuth·유료 추론을 사용하지 않았다. Windows/Android 네이티브 및 전체 UI 수용은 미완료다.

## 분류와 실제 언어 관계의 경계

원본 `app.js:3314..3330`의 `parent`(폴더)와 `inherits`(상속)는 별개다. 엔진의 `Element.Parent`는 실제 상속이며 `Category.Contains`는 typed semantic 관계다. 최신 요청의 참조·상속·자손·네임스페이스 보존에 맞춰 Browser 분류는 기존 `value editorFolder = "정규 카테고리 ID"` 메타데이터로 분리한다. 빈 문자열은 명시적 Root다. 새로운 언어 구문·실행 체계를 추가하지 않는다. 분류 이동은 ID/namespace/path/Parent/Contains/본문·반환 계약을 바꾸지 않는다. 원본 데모의 상속 제거·자동 이름 변경·샘플 자료 복사는 적용하지 않는다.

원본 UI 위치/크기/버튼은 유지한다. Browser의 폴더 계층과 요소 내부의 실제 상속/바리에이션 계층을 별도 projection으로 제공한다. 같은 분류에 있는 자손은 기존 부모 아래에 남으며, 별도 분류로 이동한 객체의 상속 자체도 남는다. category의 기존 Contains를 폴더로 추정하지 않는다. Category의 `editorBrowserGroup`이 명시되면 concept/info/feature/module의 해당 탭에 한정한다. Namespace 트리 선택은 실제 등록 namespace를 보여 주며 분류 드롭으로 source namespace를 다시 쓰지 않는다.

## 구현

- `BrowserFolderLayout` host 계약: explicit source/category revision+hash, 같은 소유 namespace/탭, 카테고리 및 상속이 섞인 표시 순환, 여러 대상 준비의 원자성 검증. 디스크 쓰기 없음.
- `EditWorkspace.MoveFolders`: immutable owned graph 관측 뒤 exact CAS로 metadata 변경을 한 번 stage. 분류 카테고리/조상은 기존 유한 hierarchy group의 관측 source로 함께 검토한다. 무관한 부모의 data 편집을 함께 확정하지 않도록 실제 폴더에 필요한 증거만 묶는다. 다른 pending group/관련 category의 실제 shared 변경은 자동 덮어쓰지 않는다.
- ordinary Web endpoint→EditorHomeModel→PackWorkspace 연결. connection settings/detached view 금지 유지. AI 도구나 권한/계정 grant를 추가하지 않는다.
- 기존 Save/변경 취소/Review/명시 compiler Confirm 재사용. unchanged support는 typed CommitPlan check로 CAS를 검사하고 쓰지 않는다. Source acceptance와 cold restore에서도 byte/hash/content가 동일한 관측 source만 불필요한 revision 상승을 피한다. 실제 변경·파일 충돌은 기존 fail-closed를 유지한다.
- header 클릭이 배경 조회와 겹쳐 버려지는 경합은 클릭 시점의 scope/CAS proof를 보관해 대기 후 처리한다. 늦은 클릭을 새 프로젝트에 재적용하거나 stale write를 재시도하지 않는다.

## 검사와 발견

1. Authoring build1/2/3/4 모두 성공(각 warning0/error0). 최초 engine build1은 Metadata 중복 import로 실패했고 중복만 제거한 build2부터 성공했다.
2. `browser_folder_layout.py` 처음 두 실행은 host의 `{ok,result}`/`{ok:false}` envelope를 exit-code로 잘못 가정한 fixture 실패였다. contract3 4묶음 통과 후, 최소 분류 dependency와 혼합 표시 순환 검사를 반영한 contract4 **5묶음 통과**. source/namespace/상속/Contains 보존, 다중 준비, source/category stale·외부 namespace·다른 탭 거절, category 순환과 category+실제 상속 표시 순환 거절을 확인했다.
3. `browser_folder_projection.mjs` **2묶음 통과**. 분류/실제 상속·자손·Root/feature 탭·Contains 구분과 프로젝트 격리를 검사했다. 기존 `browser_projection.mjs`도 분류 metadata가 없는 category/contain을 임의 폴더로 만들지 않는다는 검사를 통과했다.
4. 실제 UI1은 Other→GroupA stage/상속·원본·Unit private111 보존까지 통과 후 취소 확인에서 실패했다. fixture `/tmp/confectory-element-mutation-7z0talw2`. background status 응답을 discard 완료로 잘못 기다리는 fixture 경합과, 기존 header work가 busy 중 클릭을 버리는 경로를 함께 수정했다. 테스트는 action=discard/save의 해당 request 결과를 구별한다.
5. 실제 UI2는 이동/취소/cold/Review취소/명시 compiler Confirm 4건 통과 뒤 별도 Unit 입력 저장에서 실패했다. fixture `/tmp/confectory-element-mutation-ggth5goa`. 변경 없는 group support Unit이 cold restore에서 revision0→1로 바뀌어 private0 입력을 잠갔다. 원본 bytes/hash/text가 모두 같은 관측 source에만 현 revision을 유지하고 실제 변경은 거절/기존 version bump를 유지하도록 수정했다.
6. engine build4의 실제 UI3 **전체 exit0, 5건 통과**. fixture `/tmp/confectory-element-mutation-r3zglp9j`. Other 분류 이동→취소→Save/cold→Review취소→새 Review/명시 compiler Confirm→다른 Unit private111 별도 Save까지 확인했다. source ID/namespace/상속/typed Contains/원본 등록부와 다른 파일을 보존했다. readonly GroupA의 UTF-8 BOM도 byte 단위로 유지했다. 이 fixture는 의도한 Other 최종 Confirm을 이미 마쳤으므로 초기화나 중복 Confirm을 하지 않는다.
7. 이후 group을 실제 분류 dependency에 한정하고 no-op 결과/namespace·외부 category UI 차단 및 혼합 순환 검사를 보완했다. 최종 author4/engine5 결과와 UI4는 아래에 따로 기록한다.

## 원본 화면 대조

Repository v536 ZIP을 별도 localhost/새 browser storage에서 열었고 외부 요청을 막았다. 원본 캡처는 `/workspace/scratch/v536-reference/folder-reference/original-category-browser.png`, 측정은 같은 폴더 JSON에 보존했다. 실제 UI3의 `folder-browser-geometry.json`과 viewport1480×1050에서 비교한 Browser 창678×458 및 title/tabs/tools/pane/tree/items 6개 사각형의 위치·치수는 모두 같았다. 제목45, tabs55, tools62, pane294 높이와 tree160 너비가 일치한다. 원본과 실제 화면을 직접 열어 확인했다. 실제 프로젝트 데이터·이름·배치 위치가 다른 전체 page pixel equality나 모든 아이콘/자식 수 badge/drag preview를 검증했다는 뜻은 아니다.

## 남은 범위

카테고리 자체의 중첩 이동과 자손·다중 선택·Root/namespace 드롭의 실제 UI 완주, stale/실제 target 변경·취소/재시작 경계와 원본 표시의 나머지 정밀 대조를 이어간다. 요소 기본 Confirm 진입에서 분류 group을 부모 이동으로 부르는 기존 문구도 분리해야 한다. Browser 전체의 standalone Data·일부 context/reference hover/표시 이름·원본 badge/icon 경계, 앞 삭제 receipt import/check-path 집중 검사도 전체 수용 전에 남아 있다. 이미지/Helper 삭제·전투로그/신문고/Yogi·창별 Run 및 모바일 Blueprint/호출 ABI의 고정 제한은 기존 scope 문서에서 유지한다. 전체 UI 수용 전 새 Windows 패키지/checkout/commit/push 완료로 표현하지 않는다.


최종 engine build5 compile exit0 후 실제 UI4 **전체 exit0, 5건 통과**했다. fixture `/tmp/confectory-element-mutation-dptgq49r`. 분류 dependency를 Other+GroupA 두 source로 한정한 최신 계약에서 동일한 이동/취소/cold/Review취소/명시 compiler Confirm/다른 입력 별도 Save를 확인했다. 최종 author4는 warning0/error0, contract4 5묶음, projection2묶음 통과. UI4의 Browser 창/6개 내부 사각형도 원본 JSON과 정확히 일치했다. 이 fixture 역시 Other 최종 Confirm이 끝난 상태이므로 중복 실행하지 않는다.


## 마지막 카테고리 묶음 — 공개 projection와 Root 경계

일반 Browser의 과거 `setupBrowserRootDrop`(실제 parent=null) 경로를 제거하고 Root를 분류 드롭으로 연결했다. 실제 상속 Root 변경은 기존 요소의 부모 선택 흐름에 남으며 원래 schema 검증을 우회하지 않는다. 명시적 editorFolder는 부모와 같은 Root라도 Browser 표시에서 우선하고, 실제 parent/variation projection은 그대로다. 해당 의미를 host의 혼합 cycle 검사와 맞췄다. Snapshot reviewGroupKind와 기존 grouped Review 문구를 folder/분류 위치로 구분했다. semantic Review는 빈 folder 값을 '빈 내용' 대신 Root로 보여 준다. CSS·버튼 배치 변경 없음.

`browser-folder-nested-1.log`는 category GroupA→GroupB의 서버 stage는 성공했지만 실제 트리가 Root에 남는 결함을 재현했다. fixture `/tmp/confectory-element-mutation-10bbpgsk`. `WebState.ProjectRelationsMap`의 node allowlist가 folderDefined/folder/browserGroup을 누락했다. 메타데이터 host와 source 저장에는 값이 있었지만 공개 node에서 빠졌다. 세 가지 유한 metadata 필드만 전달하도록 수정하며 원본 text/path/비밀을 추가 노출하지 않는다.

이 발견으로 앞선 UI1~4의 Other 행 깊이 비교는 정확한 부모 연결을 입증하지 못했음을 정정한다. 기존 상속 부모 Unit과 카테고리 GroupA의 깊이가 같아 우연히 통과했다. 저장·취소·파일 보존·compiler Confirm 증거는 유효하지만, 표시 부모 연결은 새 검사로 다시 확인한다. 검사는 실제 treeitem의 직전 조상 key와 공개 folder 값을 확인하도록 보강했다.

수정 뒤 engine7 compile exit0, `browser-folder-nested-2.log` **전체 exit0 실제3건**(fixture `/tmp/confectory-element-mutation-5dq1nsch`)과 `browser-folder-ui-5.log` **전체 exit0 실제5건**(fixture `/tmp/confectory-element-mutation-pm4ugouf`) 통과. source 설정뿐 아니라 실제 부모 key를 확인했다. category 자체 이동/자손/순환 시 부분 적용 없음/취소/cold/Review취소/명시 compilerConfirm 및 기존 단일 source 분류 흐름을 확인했다. 두 fixture 모두 의도한 Confirm 완료 상태이며 초기화하거나 같은 Confirm을 반복하지 않는다.

원본 파일·typed Contains·실제 parent/namespace/자손 파일, private112 및 별도의 shared Monster draft를 유지했다. 다음 복수 항목/Root 검사는 성공한 중첩 fixture를 그대로 이어 사용하며 시작/진행 marker를 기록해 중복 Confirm을 막는다. Windows/native touch/OS drag 검증이 아니다.


## 마지막 묶음 완료 결과

`browser-folder-multi-root-1.log`는 재시작 직후 raw test view의 relationsMap 준비를 기다리지 않아 authoring 전에 실패했다. `multi-root-progress.json`은 started/검사0, 실패 traffic에는 이동·편집·Save·Confirm 호출이 0개임을 확인했다. 정확한 관계 읽기를 추가하고 같은 fixture에서 single-use setup retry marker를 남긴 뒤 이어갔다. 자료/진행 marker를 지우거나 Confirm을 다시 실행하지 않았다.

`browser-folder-multi-root-2.log` **전체 exit0, 실제 엔진/renderer 7건 통과**. fixture `/tmp/confectory-element-mutation-5dq1nsch`, 앞 중첩 Confirm 이후 상태를 이어 사용했다.

1. 두 번째 source가 실제 다른 편집으로 바뀐 뒤 오래된 두-source 요청을 거절하며 첫 source/새 두 번째 초안 보존, 부분 분류 적용 없음.
2. 실제 embedded Ctrl 다중 선택의 단일 batch 이동 및 header 취소, 저장돼 있던 분류/선행 초안과 private112 보존.
3. 다중 batch Save/실제 cold/Review취소/newReview/명시 full-group compiler Confirm. 두 source의 Parent와 무관한 source bytes, 별도 shared Monster draft 유지.
4. namespace Root와 빈 Root 드롭은 분류 전용. 명시적 Root를 실제 namespace 아래에 표시하고 취소로 기존 folder 복원. 분류가 이미 Root인 상속 객체는 no-op이며 parent-null API를 호출하지 않음.
5. 외부 namespace 드롭은 UI에서 차단. server 이동 호출/다른 프로젝트 이동/namespace 재지정 없음.
6. Root Save/cold/요소의 기존 Confirm 진입에서 '분류 위치 변경 검토'와 Root 표시. 모달 닫기/재열기·inert 정리와 명시적 compiler Confirm 뒤에도 Parent 유지.
7. 실제 부모 선택의 Root는 기존 전체 schema guard로 잘못된 상속 데이터 제거를 거절. 그 pending 입력 취소 및 별도 Unit private112 Save가 원본과 다른 작업을 보존함.

`multi-root-progress.json`은 complete다. GroupA 중첩 Confirm·Other/Third 다중 Confirm·Other Root Confirm은 모두 이미 성공했다. 이 fixture를 초기화하거나 같은 Confirm을 다시 보내지 않는다. `category-nested-confirmed.png`, `category-multi-confirmed.png`, `category-root-confirmed.png`를 보존했고 중첩/Root 화면을 실제 열어 확인했다.

기존 Root 드롭 검사를 실제 부모 변경 회귀로 갱신했다. 첫 adaptation 실행은 창이 Bare로 바뀐 뒤 Unit의 HP 입력을 그 창에서 찾는 fixture 기대 오류로 실패했다(최종 Confirm 전). 사용자가 보는 부모 선택의 private 취소/Save 경계로 검사를 다시 작성하여 assertion 의미를 맞췄다. `explicit-parent-root-regression-2.log` **전체 exit0, 기존 engine 4건**(fixture `/tmp/confectory-element-mutation-vcgceals`): private 부모 Root 취소, 유효 Root draft Save, invalid inherited-data 거절+취소, cold/Review취소/명시 Confirm 및 Unit private111 보존. 분류 Root와 실제 상속 Root를 별도 경로로 검증하며 보호를 제거하지 않았다.

최종 author6 warning0/error0, engine7 compile exit0. host contract5 5묶음, folder projection2/기존 projection2/review admission6경로/context action lifecycle 통과. canonical resource62/text53 및 JS/Python 구문·diff check 통과. 이 카테고리 기능 묶음의 고정된 owned concept/category 범위는 완료로 기록한다. 다른 source 종류는 동일한 bounded host 계약/탭 mapping을 사용하지만 모든 종류의 실제 UI/플랫폼 조합까지 검사한 것은 아니다. 전체 Browser 시각/부가 기능, 전체 v536, Windows package/checkout/게시 완료라는 뜻이 아니다.
