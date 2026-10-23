# v536 모바일 Blueprint 첫 연결 묶음

기준은 `origin/main`196c605의 원본 v536 ZIP이다. 원본 ZIP/main/Android/사용자 자료와 기존 Agent·승낙·Helper 채팅은 보존했다. 이 기록은 모바일 카드 기본 편집 묶음이며 전체 Blueprint/전체 v536 UI/Windows 배포 완료를 뜻하지 않는다.

## 원본 확인과 실제 연결

격리 loopback HTTP·새 Chromium touch context390×844에서 원본 기능 작성 화면을 열고, 원본 ＋→동작 만들기→전체 화면 편집→뒤로가기→입력 탭을 실제 조작했다. `inspect-mobile-blueprint-detail.py` 최종 session11240 exit0, `mobile-blueprint-detail-render.json` pageerror0. 초기에 존재하지 않는 `.bp-resource-panel`을 기다린 두 probe는 fixture selector 오류이며 `.bp-search-menu`로 고친 최종 결과만 사용한다. 원본의 Demo Project·임시 동작은 브라우저 메모리에서 확인한 참조이며 엔진 데이터로 복사하지 않았다. 원본/현재 PNG를 실제로 열었다.

새 `mobile-blueprint.js`는 원본의 카드 흐름 탭·노드 카드·전체 화면 inspector·뒤로/완료·그래프 복귀 구조와 CSS를 사용한다. 실제 `feature-authoring.js`의 소유 graph·node·entry·exit/기존 enum 실행 출력 데이터를 표현한다. 새 시각적 분기/반복 언어를 추가하지 않는다. 원본의 내부 흐름/비동기/터치 선택·보기 등 아직 연결하지 못한 동작은 비활성 상태로 남긴다.

노드 제목·설명은 기존 private author input과 source proof를 사용한다. C# 편집·값 메뉴·타입·핀 계약·삭제/검색도 기존 편집 핸들러에 위임하며, 실제 저장/Review/Confirm은 기존 서버 계약을 따른다. 읽기 전용 변환/참조의 제약을 모바일 overlay가 우회하지 않게 검사한다. 이 중 세부 값/핀/서명/삭제/검색의 모든 조합을 검증했다고 표시하지 않는다.

모바일 열기는 기존 문서 탭을 사용한다. 숨긴 문서를 프로젝트/대상이 바뀐 폐기된 View와 구분해, 전자는 메뉴/overlay만 일시 정리하고 이벤트와 입력을 보관한다. 프로젝트/소유 창/author generation 변경·DOM 제거 시에는 기존 전체 정리를 수행한다. 정리 중 DOM 변경이 다시 정리를 호출하는 observer 경합은 한 번만 suspend하도록 막았다. 숨긴 canvas는 좌표를 다시 계산하지 않는다. 새 권한이나 자동 source Confirm은 없다.

## 실제 검사 결과

`v536_mobile_blueprint_engine.py` / `mobile-blueprint-engine-1.log`, `/tmp/confectory-mobile-blueprint-73skvazi`: **3건 PASS 후** 마지막 Review 기대에서 중단됐다.

1. 실제 소유 Serial graph가 원본 탭/카드 문서로 열리고 desktop canvas는 inert. 데모 그래프·모델 호출 없음.
2. 전체 화면 한글/이모지/줄바꿈 설명 편집, Script 취소, 뒤로가기,1440↔390 폭 전환 시 입력 보존. 최종 원본 바이트 불변.
3. 실제 Save는 checkpoint만 변경. 프로세스를 종료/재시작한 뒤 미저장 입력과 원본 proof 복원, 명시적 재저장.

마지막 실패를 source 검사를 약화해 통과시키지 않았다. 실제 diagnostics는 `needs-implementation`, 변경된 intent의 기존 body가 `stale`였다. 설명이 바뀌면 기존 구현 본문을 명시적으로 확인해야 하는 기존 보호다. 같은 실패 profile을 초기화 없이 이어 쓴 `v536_mobile_blueprint_confirm.py`는 원본 Script 화면에서 기존 본문을 명시적으로 저장한다. 임의의 자연어 코드 생성이나 실제 AI 호출은 수행하지 않았다.

첫 후속 검사에서는 Script 확인은 통과했지만, Review 취소 후 Blueprint 탭에서 기존 hide-cleanup이 모바일 편집기를 파괴하는 결함을 확인했다. 임시 숨김과 실제 소유/세대 변경 정리를 분리했다. 다음 검사에서 observer 재진입과 카드 복귀의 CSS 순서 차이를 확인하고 한 번의 suspend 및 원본 CSS 순서로 수정했다. 기존 실패 로그는 유지한다.

최종 `mobile-blueprint-confirm-3.log` session68541 exit0, 같은 profile의 `confirm-mobile-evidence.json` **집중3건 PASS**:

- 변경된 설명의 Script를 명시적으로 확인한 뒤 저장. 그전에는 stale-body 보호가 정상 차단함.
- 그래프↗→원본 흐름 버튼 복귀, Review 취소→원래 Blueprint 탭 재진입에서 모바일 편집기와 입력 보존.
- 별도 선택·컴파일 Confirm 성공. 실제 변경 파일은 소유 graph JSON과 body node JSON 두 개이며, Unit/Monster/Slime/Main/project 등록부는 보존됨. 프로젝트 실행은 없음.

이는 최초 전체4건을 처음부터 다시 실행한 결과가 아니다. 첫3건과 같은 profile의 최종 집중3건을 구분한다. 첫3건은 build1, 최종 집중 검사는 build4의 UI/수명/CSS 수정 상태다. 이후 build5는 CSS EOF 여백 정리와 리소스 pin 갱신이며 기능 변경은 없다.

별도 기존 desktop controlled renderer `v508_feature_serial_canvas.py` / `mobile-blueprint-desktop-regression.log`, session58255 exit0, `/tmp/confectory-feature-serial-renderer-l384b25u/evidence.json` **15건 PASS**. 정확한 핀 payload·자료형 거부·값/별칭/표현식·노드/연결·CAS·입력 및 수명 보호 회귀다. 이 검사는 fixture provider이며 실제 backend/계정 성공으로 확대하지 않는다.

## 화면 근거와 환경 한계

원본과 실제 touch-emulated 엔진의390×844 기준 치수가 일치했다.

| 영역 | x,y | width×height |
| --- | --- | --- |
| 카드 host | 0,112 | 390×732 |
| 흐름/입력/출력/분기 탭 | 0,112 | 390×53 |
| 노드 inspector | 0,0 | 390×844 |
| inspector header | 0,0 | 390×58 |

`mobile-blueprint-detail-geometry.json`, fixture `touch-geometry.json` 및 `v536-mobile-blueprint-{flow,inspector,inputs}.png`/`initial-card-flow.png`/`node-inspector.png`/`touch-inspector.png` 참조. 원본 Attack와 실제 Serial의 설명·노드·핀 수가 달라지는 내용 차이를 layout 결함으로 단정하지 않는다. 세부 메뉴 전체의 픽셀 일치 검증은 아직 아니다. 첫 narrow viewport는 일반 Chromium, 최종 집중 검사는 has_touch/is_mobile emulation이다. 실제 Android/Windows·터치 하드웨어·가상 키보드/노치 QA가 아니다.

최종 Linux build5 및 리소스62/정규 텍스트53·구문/diff 결과는 checkpoint/evidence에 기록한다. 실제 계정 로그인·토큰·추론·새 권한 설정·플러그인 변경·Site 게시·새 Windows package·commit/push는 없다.

## 정확한 잔여

다음 묶음은 원본 모바일의 값 선택/취소·정확한64비트·표현식/별칭, 입력/출력 계약 편집·추가/삭제/순서, 노드 검색/배치/삭제와 연결 조작, 구현·프로젝트 전환 및 readonly/CAS 경계의 실제 검증이다. 위임한 코드가 있다는 사실만으로 이 동작들이 완성됐다고 하지 않는다. 내부 흐름·비동기·터치 선택/보기 메뉴 및 원본에서 요구하는 나머지 graph touch 조작도 미연결/부분 상태로 남긴다. 후속 묶음에서 기존 지원 범위와 새로 필요한 API를 구분한다.

그 뒤의 요소 Browser·이미지/삭제·전투 로그/신문고·창별 Run·기존 소유 호출 ABI/복사/혼합 저장 제한·전체 수용/Windows 패키징/checkout/work-current 게시도 그대로 남아 있다. Helper 에디터 기능 추가는 전체 UI 복원 이후의 별도 순서다. 새 내구성 범위나 새 시각적 언어를 만들지 않는다.


## 세부 값·핀·표현식·검색 두 번째 묶음 (2026-10-23)

기존 서버 계약을 그대로 사용하는 좁은 모바일 UI 연결이다. 값 메뉴는 별도 파서나 일반 JSON 숫자로 바꾸지 않고 기존 정확한 64비트 파서와 source receipt를 사용한다. 원본 `blueprint.js:1621`의 중첩 `bp-flow-expression`/`data-value-path` 구조를 모바일에 반영하여 연산자와 각 하위 피연산자를 실제 기존 편집 경로로 연다. 한글·이모지·따옴표·실제 줄바꿈 문자열은 JSON 인코딩을 거쳐 보존된다.

핀 추가/타입/이름 변경이 `refreshLocal`로 화면을 다시 만들면서 전체 화면 inspector를 닫는 결함을 실제 엔진에서 재현했다. 편집 중인 노드·스크롤은 프로젝트/기능/구현/graph에 묶인 일시적 창 상태로만 복구한다. 다른 소유 문맥에는 재사용하지 않으며 문서 숨김/뒤로/완료/모드 변경은 해당 편집 표시를 정리한다. 이 상태는 계정·권한·서버 원본 proof를 대체하지 않는다. 새 동작을 만든 뒤 원본처럼 inspector를 열며 C# 제목도 현재 private rename을 반영한다.

선택한 ＋ 위치를 전달해도 검색 결과가 별도 노드로만 생성되던 결함도 재현했다. 원본 `addNode`의 실행 줄 삽입 의미에 맞춰 선택 당시 source/port/successor를 보관하고, 같은 소유 화면과 현재 실행 줄인지 다시 확인한 뒤 새 동작의 앞뒤 연결을 함께 private 편집으로 만든다. 일반 직렬 호출도 같은 연결 어댑터를 사용하지만 이번 실제 통합 검증은 동작 생성 경로다. 루트 계약 미저장 상태, 아직 연결하지 못한 gap의 내보내기/특수 실행 출력 호출은 기존 데이터나 연결을 바꾸지 않고 실제 미지원 안내를 한다. 성공처럼 표시하지 않는다. 새 분기/반복 언어를 만들지 않았다.

실제 Linux 생성 엔진+격리 fixture+390×844 touch-emulated Chromium 결과:

- `mobile-values-engine-2.log` / `/tmp/confectory-mobile-values-cyxntc89/evidence.json`: **5 PASS**. 범위 밖 long 거부/값 메뉴 취소, 최대 long 정확한 checked Save, 한글·따옴표·boolean·long 배열, 폭 전환/cold pending 입력 복구, 명시적 compiler Confirm. 최초 run1은 fixture graph의 `/body:common` suffix를 빠뜨린 읽기 요청 오류이며 성공으로 취급하지 않는다.
- `mobile-contracts-engine-2.log` / `/tmp/confectory-mobile-contracts-kxapswpu/evidence.json`: **2 PASS**. 노드 입력 추가 뒤 inspector 유지, 이름/long 타입/반환 출력 추가·타입/루트 입력 연결·보호된 C# 본문 Save와 실제 graph 확인. 저장 전후 사용자 원본 파일 바이트 불변. run1의 inspector 닫힘 재현 로그 유지.
- `mobile-expressions-engine-1.log` / `/tmp/confectory-mobile-expressions-jyj6owi6/evidence.json`: **4 PASS**. 원본 중첩 연산자·하위 값 경로, 정확한 long, 0 나눗셈 Save 거부와 입력 보존, 오류 수정/하위 값 취소, 실제 줄바꿈 한글 문자열, 폭 전환/cold 복구/checked Save/명시적 compiler Confirm. 최종 변경은 소유 graph JSON 한 개.
- `mobile-search-engine-3.log` / `/tmp/confectory-mobile-search-cw3eoxlf/evidence.json`: **4 PASS**. 검색/취소 무변경, 기존 시작→body 줄에 새 동작 삽입과 successor 보존, 원본 새 inspector의 제목/설명/C# 편집과 Save, 실제 cold 뒤 같은 실행 순서/명시 compiler Confirm. 원본 파일은 Confirm 전 불변이고 Confirm 뒤 소유 Blueprint만 변경. 첫 run은 기존 연결 미반영 결함, run2는 C# 제목이 이전 표시 이름을 사용하던 결함으로 중단되었고 로그를 보존했다. 첫 test의 세 노드 기대는 기존 terminal 카드까지 포함해 초기 목록+1로 바로잡았으며 순서와 실제 graph도 별도로 검증했다.

`mobile-details-desktop-regression.log` / `/tmp/confectory-feature-serial-renderer-7ig4dki0/evidence.json`: **controlled renderer 15 PASS**, 실제 backend/계정 결과와 구분한다. 이 실행은 build3의 gap 연결까지 포함하고, 그 뒤 build4는 Script 제목의 private rename 반영과 초기 inspector 복원 RAF의 새 선택 보호만 바꿨다. build4의 생성/Script/cold/Confirm 실제 경로는 위 search run3에서 확인했다.

최종 `mobile-details-build-4.log` compile exit0. 리소스62/정규 텍스트53의 해시·크기, JS 모듈2개 및 모바일 Python 구문, diff 공백 검사가 통과했다. 스크린샷은 fixture의 `nested-expression.png`, `contract-cold-inspector.png`, `inserted-action-inspector.png`에 남긴다. 원본 중첩 값 마크업을 소스와 대조했고 실제 표현식 PNG를 열었다. 이 묶음에서 세부 화면 전체 픽셀 일치나 실제 터치 기기 검증을 완료했다고 하지 않는다.

노드 계약 후속 `mobile-contract-confirm-1.log`는 cold 뒤 실제 저장된 새 입력/출력 타입·본문·값 복원 **1 PASS** 후, Review 취소를 없는 `#cancel`로 눌러 실패했다. 원본 `[data-reject]`로 fixture를 고쳤지만 해당 실패 profile을 reset 없이 재사용한 run2는 cold 화면에서 Blueprint를 찾지 못했다. run3에서는 실제 기존 Blueprint 문서 탭을 명시적으로 눌렀으나 여전히 선언 화면/Workspace만 표시되고 카드 편집기가 생성되지 않았다. pageerror/backend error는 없고 해당 시작 traffic에 Blueprint read가 없다. 원본 저장본이나 계정 문제로 단정하지 않으며 복구 메타데이터/활성 문서 연결과 fixture 조건을 다음 묶음에서 조사한다. 최종 계약 Confirm/Review 취소 회귀는 미완료이며 실패를 숨기지 않는다. 모든 세션은 종료·회수했다.

실제 생성 inspector PNG에는 성공한 source 작업과 별도로 “기능 편집 대상이 바뀌었습니다. 입력은 유지됩니다.” 알림이 남아 있다. 폐기된 검색 메뉴의 비동기 catalog read와 일치하는 코드 경로가 있으나 현재 알림의 정확한 발생 콜백은 미확정이다. 활성 오류나 source CAS를 숨기지 않는 범위에서 다음 묶음에서 추적한다. 모바일 루트/핀 순서·삭제/출력 배치·검색의 나머지 종류, 별칭/readonly/다른 구현과 프로젝트 전환 경계, 터치 선택·보기/내부 흐름·async 등 고정 잔여는 아직 부분/미연결이다. 실제 Windows/Android 하드웨어/IME 가상 키보드·계정·모델 호출, 새 Windows 패키지·checkout·commit/push는 수행하지 않았다. 전체 UI 복원은 미완료다.


## 후속 해결 결과

위 두 번째 묶음의 미해결 cold/검토 복원 및 생성 뒤 알림은 다음 실제 재현·수정·검증 묶음에서 해결했다. 숨긴 탭의 source 복원/초기 클릭 차단과 폐기된 catalog 읽기, 실제 프로젝트 재진입의 retained author 재바인딩을 구분했다. 상세한 실패/최종 결과와 남은 모바일 범위는 [복원·수명·핀/출력 배치 검증](VALIDATION_V536_MOBILE_BLUEPRINT_RECOVERY.md)에 기록한다. 전체 UI/Windows/게시가 완료되었다는 의미는 아니다.
