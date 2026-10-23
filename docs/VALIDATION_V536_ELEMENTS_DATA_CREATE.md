# v536 요소 Browser — Data 읽기와 inline 바리에이션 생성

사용자가 지정한 `origin/main` 196c605의 보존된 v536 ZIP을 기준으로 한다. 전체 UI 복원·Windows 패키지·게시 완료가 아니다. 이번에는 원본 Data 객체 행과 inline 입력 행에 실제 소유 프로젝트 기능을 연결했다. 원본 CSS/화면 구조를 재사용했으며 비교 구성 폼이나 새 상시 패널을 추가하지 않았다.

## 이번 묶음의 안전한 완료 조건

1. 현재 프로젝트의 명시한 소유 객체 값만 읽고, 조회가 선택·소스·편집 입력을 바꾸지 않는다. 실제 상속/자체 값과 설명을 표시하고 실패를 0/빈 값의 성공으로 처리하지 않는다.
2. 객체 아래의 `개념 생성`은 해당 객체를 상속하는 기존 `createVariation` 계약에 한정한다. Category 포함 관계를 상속으로 대신 구현하지 않는다. 원본 inline 입력/Enter/blur/Escape를 재사용하며 실제 엔진 선언 이름 제한은 오류로 안내한다.
3. 생성 전 취소, 잘못된 이름/중복 수정, 거절된 transport admission의 제한 재시도 및 생성 후 부모·자손 편집을 실제 경로로 검증한다. 성공했는지 모르는 쓰기를 새 source 버전으로 덮어쓰지 않는다.
4. 생성은 새 객체와 등록 변경을 공유 작업 초안에만 남긴다. 실제 최종 소스/manifest 파일은 Save가 아니라 별도의 기존 명시적 Review/Confirm 경계를 유지한다. 이번 묶음에서 생성 그룹의 최종 Confirm까지 통과했다고 주장하지 않는다.
5. 미제출 이름, 기존 부모 입력, 생성 자손의 저장된 작업 초안과 Data 모드를 실제 재시작 후 복원한다. 기존 파일 바이트와 파일 집합을 보존한다.

## 구현과 경계

- `TableCommand.csbody`의 좁은 `browser-elements` 읽기는 기존 `EditWorkspace.DescribeSchema`를 재사용한다. 1~64개의 중복 없는 명시적 ID, 현재 프로젝트 context/namespace, 실제 소유 `object`를 검사한다. 계정 설정 workspace는 기존처럼 제외한다. 반환은 ID/버전 해시 및 공개 요소 필드 값이며 source 본문·경로·계정/자격증명을 반환하지 않는다. 숫자는 기존 정확한 JSON 문자열로 전달한다.
- `Command.csbody`는 이 읽기로 primary properties projection을 지우지 않는다. `WebInvoke` 입력은 `ids`만 받으며 내부에서 검증된 context를 붙인다. `WebBundle`에는 이 소비자 UI용 엔드포인트만 명시적으로 등록했다. Helper의 편집 도구/권한이나 실제 사용 동의를 추가하지 않았다.
- Data는 원본 `browser-data-list`, 객체 identity/fields/edit 버튼 구조를 사용한다. **현재 scalar 셀은 읽기 전용**이다. complex `편집` 및 원본 `⋯`는 기존 소유 요소 편집창을 연다. 셀 직접 쓰기와 원본 값 상세 팝오버의 완전한 대응은 미완료다. 기존 개발용 표 비교 UI를 대신 삽입하거나 writable처럼 보이게 하지 않았다.
- inline 생성은 현재 보이는 부모와 최초 표시 source revision/hash를 고정한다. 부모의 미적용 입력이나 다른 source의 미적용 입력은 생성 전에 막는다. 성공 후 부모 cursor를 복원하고 기존 입력/창을 보존한다. 실제 source CAS를 새 버전으로 자동 갱신하지 않는다.
- 입력은 기존 window metadata 안의 `variations.createDraft`에 보관한다. 같은 window의 진행 중 job으로 중복 Enter/blur 처리를 막고, 새 UI나 자동 재생성은 추가하지 않는다. 재시작은 입력만 복원한다. Enter 전 Escape는 source/등록 작업 없이 취소한다. 이미 생성된 객체를 취소처럼 삭제하지 않는다.

## 실제 검사 결과

`v536_elements_data_create_engine.py` 세 번째 실행은 다음 **5건 통과** 후 마지막 테스트의 창 겹침에서 중단했다. 실제 생성 엔진과 Chromium이며 provider/계정 호출은 없다.

- 원본 Data 행에 실제 Monster의 상속 HP100, 자체 Speed2, 설명을 읽었다. primary Unit 선택, 원래 source 바이트와 파일 집합은 유지됐다.
- 서버가 다른 namespace 소유자와 알 수 없는 입력 필드를 거절했다. source/선택이 유지됐다.
- 원본 inline 행에서 Escape 취소 전후 생성/manifest 요청이 없었다.
- 한글/공백 이름과 중복 이름은 입력을 보존하며 안내했다. 유효한 이름으로 고친 후, 최초 `createVariation` admission을 실제 서버에서 `stale_revision`으로 거절하도록 주입했다. 동일 ID/원래 부모 proof로 다시 admission된 한 건만 생성됐다. 새 항목/등록은 공유 초안이며 최종 파일은 생성되지 않았다.
- 자손 FreshVariant의 HP222 staged Save, 부모의 미적용 HP111, Data 모드, 미제출 `Draft_계속` 이름이 실제 엔진 프로세스 재시작 후 복원됐다. 이름 입력을 취소해도 이미 생성된 자손과 등록은 유지됐다.

마지막 테스트는 cold 후 원래 떠 있던 Project Browser가 부모 창의 Save 버튼을 가린 상태에서 클릭하려 해 timeout됐다. 보호 조건이나 assertion을 제거하지 않았다. 일반 사용 동작대로 부모 제목을 클릭해 앞에 두도록 fixture를 보완했다.

`v536_elements_data_create_focus.py`가 같은 소비 fixture에서 마지막 **집중 1건 전체 통과**했다: 부모 제목 focus → checked Unit staged Save → Data의 `⋯`로 기존 자손 View 재진입 → 333 임시 입력 취소 → 자손222/부모111 유지. 최종 source 파일 집합과 바이트가 전부 원래와 일치했다. 앞 5건을 불필요하게 재실행하지 않았다. 따라서 수정한 full script의 fresh 6건 전체 재실행과 6건 한 번에 통과는 구분한다.

증거: `/tmp/confectory-element-data-create-id7oxtwx`의 `progress.json`, `focus-evidence.json`, `actual-data.png`, `inline-and-parent-input.png`, `final-original-data-and-child.png`. 실제 PNG를 열어 확인했다. 현재 화면은 스크롤 위치/데이터/viewport가 다르므로 원본과 전체 픽셀 일치를 주장하지 않는다. 원본 Data/생성 PNG와 geometry는 `/workspace/scratch/v536-reference/elements-data-create-reference/`에 보존했다.

## 초기 실패와 수정

- 첫 실행은 `browserElements`의 소비자 endpoint 등록을 빠뜨려 거절됐다. 등록을 추가했다.
- 두 번째 실행은 서버 내부에서 `consumer_error`로 실패했다. 격리 C# probe가 동일 Model 호출의 `Error: browser-elements-fields`를 재현했다. 내부 호출이 붙이는 `context`를 새 필드 allowlist에서 누락한 것이 원인이었다. 현재 열린 context와 같을 때만 그 내부 필드를 받도록 수정했다. Web UI 입력은 여전히 `ids`만 허용한다.
- probe 최초 세 실행은 독립 검사 프로젝트의 transitive registry/provider 연결이 불완전해 빌드 실패했다. 원래 제품 실행 실패와 섞지 않았다. 원래 entry의 provider 구성을 격리 probe에서 재사용한 네 번째 실행은 build/run exit0으로 위 거절 조건을 확인했다.
- 첫 build 스크립트 실행은 존재하지 않는 임시 pack 복사 경로 때문에 컴파일 전에 중단했다. 실제 manifest가 저장소 pack을 직접 참조함을 확인하고 그 불필요한 복사를 제거했다. 이후 Linux 실제 엔진 build2/3/4/5가 exit0이었다.
- 마지막 리소스 62개/정규화 text 53개 크기·해시, 수정 JS/Python 구문 및 `git diff --check` 통과. 새 Linux 빌드가 실제 C# Model 수정도 포함한다.

## 미완료

Data scalar 직접 쓰기, 원본 complex/다중/참조 상세 팝오버의 정확한 대응, 빈 부모 footer 생성과 부모 변경 CAS 실패 UI의 신규 집중 검증, 생성 묶음의 명시적 최종 Confirm·응답 유실/프로젝트 전환 검사는 이번에 완주하지 않았다. 현재 기존 source/소유권/CAS 보호를 유지한다. Category 생성/포함 관계·이름 변경·삭제·다중 선택·드래그 및 정밀 화면 비교도 고정 잔여다.

모바일 Blueprint 공유/고정 반환 이름·잠정 빈 출력·영역/다중 선택·내부 흐름/async·특수 핀 제한은 그대로 남는다. Helper 이미지/폼 삭제, 전투 로그/신문고, 창별 실행과 전체 회귀/Windows 교차 패키지/checkout/정상 게시도 미완료다. 실제 Windows/Android/터치 기기 실행이나 실제 사용자 로그인·유료 추론은 하지 않았다. main/Android/원본 ZIP 및 사용자 데이터는 수정하지 않았다.
