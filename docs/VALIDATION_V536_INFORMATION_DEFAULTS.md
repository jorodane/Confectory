# v536 정보 자체 정의와 기본값 — 한정 완료 단위

`09dd004f` 이후 기존 정보(schema)를 원본 요소 카드에 연결한 단위다. 정보 탭의 상세 편집 및 원본에 있는 새 창 열기, 기존 속성의 표시 이름/기본값, 한글 표시 이름의 새 primitive·linked 정보 속성을 연결했다. raw source와 typed/View의 결합 Save는 아직 차단하며 다음 별도 단위다. 전체 UI 복원 완료가 아니다.

## 저장 계약과 호환성

- `informationDefinitions`는 같은 root 소유 schema만 변경하는 순수 후보다. 설명, 기존 primitive/복합 기본값, 직접 소유 primitive 타입/표시 이름/삭제, 새 single primitive/기존 named 정보 정의를 지원한다. 기존 데이터·자손·참조·Blueprint 계약이 맞지 않으면 후보 전체를 거절한다. 다른 정보 원본/객체/부모/등록 팩을 변경하거나 schema owner에 slot/copy 권한을 주지 않는다.
- native `value` 문법의 명시적인 `editorInformationDefaults = "typed-json-v1"` 표식과 `editorFieldDefault_<stable key>` JSON-string metadata를 사용한다. 별도 언어나 runtime cache를 추가하지 않는다. 새 필드의 native key와 한글 표시 이름을 분리하며 typed JSON의 64비트 숫자·중첩 값·참조를 보존한다.
- 이 기본값은 새 값을 만들 때의 스냅샷이다. 이미 존재하는 객체의 명시 값이나 실행 시점 속성 읽기를 덮지 않는다. 기본값이 없는 primitive/중첩 정보는 원본의 fallback을 사용한다. 해석 불가능한 이전 prefix·알 수 없는 profile·고아/잘못된 값은 editor에서 unavailable로 유지하며 자동 이전/삭제하지 않는다.
- 명시 profile의 타입·참조·JSON은 `SchemaContracts`에서 최종 compiler 검증에도 포함한다. 기본값 metadata가 대상을 실행 의존성으로 활성화하지 않는다. 표식 없는 과거 metadata는 compiler에서 임의로 기본값으로 해석하지 않는다.
- 기존 SlotBatch/ApplySlots의 하나의 후보·전체 source 관찰·checkpoint CAS·전체 Blueprint 검사·persist-before-live·receipt를 재사용한다. 실패/충돌은 전체 미적용이며, 응답 유실은 원래 시도 조회 후 복구한다. 새 basis로 무조건 덮어쓰거나 기존 실패 기록을 지우지 않는다. 기본 창과 독립 properties View의 입력/receipt 및 명시 Review/Confirm을 구분한다.

## 실제 검사

로그와 화면 근거는 `/workspace/scratch/v536-info-definitions/`에 있다. 아래 PASS 수는 공통 준비를 포함한 시나리오 묶음으로, 서로 합산한 독립 테스트 수가 아니다. 모두 격리 fixture이며 실제 사용자 자료/계정/인증파일·로그인·유료 모델 호출·사용자 프로젝트 실행을 사용하지 않았다.

| 검사 | 결과와 범위 |
| --- | --- |
| Release solution | `build3.log` 경고0/오류0. compiler/core+helper+host 빌드 |
| 순수 후보와 실제 compiler | `metadata4.log` 5 PASS. 명시 profile/정확한 long/한글/중첩·multiple 기본값/기존 객체 값 불변, 타입·삭제 영향·stale proof·불명확 기록 전체 거절. compiler의 참조 대상 변경·잘못된 타입/JSON 차단과 unmarked legacy 해석 안 함 |
| 실제 엔진 API | `api4.log` 4 PASS. 마지막 값 오류의 전체 미적용·원문/checkpoint 보존, schema owner-only Save/receipt, peer stale/copy 요청 차단, 프로세스 재시작 복구 |
| 실제 Chromium 기본 창 | `ui-normal-final.log` 4 PASS. 정보 탭→기존 상세 편집→새 필드/중첩 정확 값·표시 이름/설명→저장 전 cold→한 후보 Save/cold→Review 취소/명시 compiler Confirm/확정 후 cold. 정보 파일만 반영 |
| 취소·실제 충돌 | `ui-cancel1.log` 3 / `ui-conflict1.log` 3 PASS. 명시 취소는 기존 checkpoint/객체/부모 불변. 실제 source 변경은 cold 재시도에도 전체 미적용·원래 입력/proof와 peer 파일 보존 |
| 값 거절·수정 재시도 | `ui-reject1.log` 5 PASS. 중첩 long 범위 오류는 전체 미적용, 불완전 원문 cold 복원 후 명시 수정하여 Save/Review/Confirm |
| checkpoint 쓰기 실패 | `ui-storage3.log` 5 PASS. 정보 기본값/새 정의/설명 전체 미적용·입력 보존→cold 명시 재시도→Review/Confirm |
| 응답/조회 유실 | `ui-loss2.log` 5 PASS. 원래 journal 보관→cold receipt 조회만으로 복구, applySlots 중복 없음→Review/Confirm |
| 독립 정보 창 | `ui-view-final.log` 4 PASS. 원본 새 창 메뉴→창별 정보 편집→저장 전/후 cold→명시 Review/Confirm. 최종 원본 높이 계산 수정 후 재검증 |
| 이전 독립 Undo 회귀 | `undo-regression.log` 5 PASS. 기존 linked 정보 선택/저장/cold/Confirm, 폼 local Undo가 Workspace history를 소비하지 않음, 폼 밖 실제 Workspace Undo/Redo와 원본 불변 |
| 공통 core/schema/view 회귀 | `core-regressions.log` 52 PASS/1 FAIL. 실패는 게시 기준 `09dd004f`의 깨끗한 checkout에서도 재현(`baseline-core-failure.log`): 기존 지원 object ABI를 TYPE 오류로 기대한 오래된 assertion. object 허용과 미지원 decimal 거절로 테스트를 수정했고 해당 테스트 `core-targeted-final.log` 1 PASS. 나머지52건을 불필요하게 반복하지 않았으며 parser 보호/지원 타입은 바꾸지 않음 |

초기 API fixture의 save 후 projection 재조회 및 다른 owner select 누락, 이전 리소스 pin을 쓴 엔진 시작 실패를 바로잡았다. `metadata3.log`의 새 compiler fixture는 target 등록 누락으로 실패했고 target을 명시한 metadata4에서 통과했다. `ui-storage1/loss1/storage2`는 빠른 Enter가 목록의 상태 조회/DOM 갱신과 경합해 열기까지 도달하지 않았다. 제품 저장 결함이라고 단정하거나 assertion을 제거하지 않고 기존 상세 편집 메뉴와 사용 가능 상태를 사용하는 실제 경로로 storage3/loss2를 완주했다. Browser 키보드 재렌더 안정성은 최종 조작 수용의 잔여다.

## 원본 화면 대조

원본 저장소 v536(`196c605`) `app.js`의 `objectEditorInitialSize`, `fitNewObjectEditor`, `renderObjectSchema`, `informationDefaults`/`propertyDefault`를 대조했다. 첨부 ZIP 동일성은 이전과 같이 미확인이다. `original-info.png`, `engine-info.png`와 `visual.json`은 1280×900, 같은 두 속성의 Details 정보 화면이다. 두 이미지를 실제 열어 확인했다.

창 초기384px에 고정되어 기능 영역이 잘리던 차이를 원본의 내용 높이 계산으로 수정했다. 최종 창은 양쪽 **460×529px**이며, 창·기능 영역·기능 본문·제목바·이름·설명·속성 영역·자체 heading·첫 속성 행·값 상자의 가시10영역 상대 위치와 크기가 일치한다. hidden zero-size 요소 좌표와 창 배치/프로젝트 데이터 차이는 일치 주장에 넣지 않는다. 수동/복원 크기를 내용 최대 범위에서 보존한다. HTML/CSS/버튼 배치를 새로 설계하지 않았으며 전체 pixel equality/모든 데이터 조합/native 기기 검사는 아니다.

## 패키지와 남은 범위

최종 Windows 교차 패키지는 `/workspace/artifacts/Confectory-v536-information-definitions-final/Windows-x64/Confectory.exe`이며 **폴더 전체**가 필요하다. 앞 information-definitions 폴더는 최종 높이 수정 전 중간본이다. `package-final.log` 2318개 선언 파일, `package-probe.log` PASS는 SDK 없는 별도 cwd/profile에서 실제 packaged managed 웹 시작/72 리소스·fixture profile 보존 및 변조/누락 거절을 확인한다. Windows apphost/WebView2 실행 검사가 아니다. 실제 Windows/Android/touch·DPI/IME는 미검증이며 Library 기존 네트워크 장애에 새 복구 근거가 없어 재호출·업로드 우회하지 않았다. 로컬 패키지가 전달됐다는 뜻이 아니다.

남은 정보 경계는 legacy inline compound 정의 변경, 기존 compound/multiple 정의의 모든 전환·순서·아이콘, 새 ref/function/imported 정보 선택, Info 부모/기능 편집이다. 현재 지원 위젯과 native 계약을 넘어 자동 변환하거나 성공 표시하지 않는다. 기존 참조 필드의 명시 기본값 검증과 새 참조 정의 생성 UI를 혼동하지 않는다.

다음은 **raw source와 owner/schema·독립 View 결합 Save**다. 원래 source/id/path/hash·checkpoint·창별 입력과 원문/주석을 같은 후보/CAS에 결부하기 전까지 현재 dirty source 차단은 유지한다. 그 뒤 ABI 교차 문맥(opaque/상속/whole-body/copy 다중 target·등록 callable 여러 target·동일 호출 복수 사용·다른 계획 혼합)과 모바일 최종 조작의 고정 목록을 `V536_REMAINING_ACCEPTANCE.md` 기준으로 마감한다. 이미지 자산/제공자·협의·내장 렌더/FPS backend는 이 UI 복원에 추가하지 않는다.
