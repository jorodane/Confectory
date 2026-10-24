# v536 정보 부모 선택: 기존 분류 계약 연결

이번 완료 단위는 **기본 정보 편집창**의 부모 선택과 새 타입 편집 중 실제 프로젝트 전환 회귀다. I4 전체/독립 편집창이나 I5/I6/B2를 완료로 세지 않는다.

## 원본 의미와 변경

원본 기준은 사용자가 지정한 main 레퍼런스 `196c605`의 `reference/site-ui/Confectory-Editor-Prototype-v536.zip`이다. `app.js`의 `openObjectParentPicker`는 `canMoveBrowserObject`를 사용한다. info 그룹은 같은 그룹의 **Category 또는 Root**만 부모로 선택할 수 있다. `browserHierarchyParent`와 `moveBrowserObject`에서 이 부모는 분류 위치다. native schema `extends`와 정보→정보 상속으로 해석했던 기존 I4 감사는 잘못되어 바로잡았다.

기본 정보 창의 기존 부모 행/선택창을 유지하며 현재 소유 info 카테고리와 Root를 기존 `moveBrowserFolders`에 연결했다. 표시에는 Browser 분류를 사용하고 schema `extends`·상속 속성·기본값을 그대로 둔다. 선택은 작업 사본의 분류 그룹에 적용하고, 기존 임시 저장/변경 취소/Review/명시적 compiler Confirm 경계를 사용한다. 선택 목록을 그린 뒤 위치를 계산해 원본 위치 계산 순서도 맞췄다. 적용 뒤 schema를 다시 읽어 편집창이 적용 전 버전으로 취소/상태 검사를 수행하지 않게 한다. 부모 아이콘은 현재 실제 Browser 아이콘을 사용한다. 소유권·분류/상속 순환·source/category proof·CAS 검사는 변경하지 않았다.

같은 정보에 미저장 값/타입/다른 창 입력이 있으면 분류를 임의 병합/폐기하지 않고 기존 보호로 거절한다. 독립 properties 창은 별도의 로컬 문서 저장 경로이므로 이번 분류 선택을 활성화하지 않았다. 그 창의 분류 이동·취소/저장 그룹 연결은 **I4 잔여**다.

## 실행 결과

| 검사 | 실제 확인 범위 |
| --- | --- |
| `v536_field_projects.py` | root 및 별도 깨끗한 checkout 각각 4 PASS. 같은 namespace/같은 정보 ID를 가진 실제 두 프로젝트 사이 새 cardinality·exact64·reference 후보, retired Save 차단, A만 저장/B 입력 및 checkpoint 보존, 프로세스 cold·양방향 재진입 분리 복원 |
| `v536_information_parent_ui.py` | 실제 격리 엔진/Chromium 6 PASS. 같은 info 카테고리/Root만 선택, native extends/상속 Count 보존, Escape 미적용, 미저장 입력의 분류 거절·보존, 실제 그룹 적용, 변경 취소, 임시 저장/cold, Review 취소·새 명시적 compiler Confirm, 확정 후 Root 재편집/취소 |
| 원본 정밀 비교 | 위 실제 UI 검사에서 추적 ZIP의 원본 함수/CSS를 별도 렌더. 같은 `lang=ko`·doctype·글꼴 조건의 선택창/검색/목록/세 버튼 **6개 영역** 좌표·치수·색·font/padding 완전 일치. 팝오버 280×165px. 원본/실제 PNG와 비교 JSON 보존 |
| `browser_folder_layout.py` | 5 PASS. 상속/ID/contain 보존, 한 후보 다중 분류, source/category stale proof·외부/다른 탭 차단, category 및 상속/분류 합성 순환 차단 |
| `browser_folder_projection.mjs` | 2 PASS. 분류/상속/명시 Root·후손·다른 탭 의미와 프로젝트별 projection 분리 |
| Linux 엔진 | 변경된 두 JS의 검증된 canonical pin으로 재빌드, 경고 0. JavaScript syntax·Python compile·diff whitespace 검사 통과 |

검사 fixture는 자체 생성한 프로젝트·프로필뿐이다. 실제 계정/로그인/동의·모델 호출/사용자 프로젝트를 사용하지 않았다. native schema 부모·카테고리·등록 팩·다른 원본 파일은 변경하지 않았다. 다른 객체의 미저장 `9223372036854775802`와 타입 기본값의 64비트 원문도 보존했다.

증거는 작업 환경의 `/workspace/scratch/v536-schema-parents`에 있다. 최종 실제 UI `information-parent-8.log`, fixture `confectory-wide-mixed-*`의 `information-parent-geometry.json`, `information-parent-original.png`, `information-parent-picker.png`, `information-parent-final.png`. 초기 실패는 잘못된 빌드 manifest 경로, 갱신 전 리소스 pin, fixture의 중복 Count/중복 Browser/아이콘 포함 text assertion, 비교 페이지의 언어·doctype 불일치였다. 통과로 계산하지 않았다. 분류 적용 직후 draft revision은 바뀌고 schema snapshot은 비워지는 실제 상태를 확인해 위 재읽기 adapter를 추가했다.

## 한계와 다음 묶음

I4 독립 정보 창 분류/취소 그룹 연결과 실제 UI의 오류·응답 유실·Undo 조합은 추가 검증/연결이 남는다. 기존 분류 CAS/순환/소유권 보호는 통과했지만 이를 새 헤더의 모든 실패 조합 검사라고 확대하지 않는다. I5 정보 기능/모듈, I6 glyph/emoji/로컬 이미지 아이콘, B2 실제 선언별 작업자 배지는 아직 구현하지 않았다. A4–A6 및 M4/M11/M12도 별도 고정 잔여다.

Windows 패키지는 교차 생성·구성 및 Linux에서 패키지의 관리형 웹 엔진 기동을 검사한다. 실제 Windows apphost/WebView2/DPI/IME·모바일 하드웨어 통과가 아니다. Library 업로드/사용자 전달은 완료하지 않았다. 최종 패키지/checkout 검사 결과와 SHA는 후속 기록을 따른다.

## 최종 checkout·패키지 검증

실행 변경 커밋 `258c8992d23bc0122711be2e808cb0c709e864f6`을 기존 별도 checkout에 ff-only 적용하고 깨끗한 상태에서 새 정보 부모 UI **6 PASS**를 재현했다. root/checkout의 추적 실행 소스·검사 3214개는 줄끝 정규화 후 일치한다. 실제 Git CRLF attribute pull·fresh LF와 내용/인코딩/BOM/바이너리/budget 거절을 포함한 **73리소스** 검사도 통과했다. 원본 파일 바이트는 불변이다. 새 네이티브 C# 소스 변경은 없으며, 이번 엔진의 pinned pack 본문은 Linux/Windows 교차 빌드로 컴파일했다.

최종 로컬 전체 패키지: `/workspace/artifacts/Confectory-v536-information-parent-final/Windows-x64`의 `Confectory.exe`와 모든 동반 파일. 선언 2322개/marker 포함 2323개, 131924302바이트다. marker SHA-256은 `a0fa423c0c6944db2745d1098cf33c1665e89fbb7bc902b652e1fddec28cb25b`, 정렬 체크섬 목록 SHA-256은 `d8c5a435e2b62b5219bd1325cc7fc63afe3e99ba9f4d4ed7e7eb5c11fe2a2e0a`다. 패키지의 추적 실행 소스 2102개가 이 커밋과 바이트 일치한다. PE/의존성/리소스/검증값 손상 거절과, 다른 cwd·SDK 없는 격리 runtime으로 패키지의 관리형 웹 엔진 및 최소 로그인 화면 기동을 검사했다. 실제 로그인/추론/Windows apphost/WebView2 실행은 하지 않았다. 필요한 Windows 선행 설치는 .NET Desktop Runtime 10 x64와 WebView2이며 전체 폴더를 함께 사용해야 한다. 파일은 로컬 보관 상태이며 사용자에게 전달/업로드됐다고 표시하지 않는다.

분류 adapter가 포함된 최종 엔진에서도 `v536_field_projects.py`를 다시 실행해 **4 PASS**했다(`projects-current.log`). 저장 뒤 분류 projection 재조회가 추가된 경로에서도 A/B 전환·오래된 콜백 차단·정확한 typed 입력·cold 복원은 유지된다. 비교 페이지의 원본/실제 PNG와 최종 정보 창 PNG도 직접 열어 확인했다.

## I4 독립 properties 창과 오류 경계 후속

독립 창도 동일 프로젝트의 EditWorkspace를 공유한다. 별도의 View handle은 선택 대상과 private 입력을 나누므로, 기존 전역 분류 호출을 무조건 전달하지 않고 `view + id`에 묶었다. 서버는 실제로 열린 properties 창이 소유한 **schema 하나**만 분류하며, 취소는 그 정보 하나만 이동한 **완전한 분류 그룹**에만 허용한다. 다른 창/미개방 slot/복수 source/부분 그룹/다른 owner는 거절한다. 원래 source·metadata·category proof와 BrowserDrafts CAS를 유지한다. detached source/declaration 창에 새 분류 권한을 열지 않는다. View에서의 최종 확정은 기존 primary Review/Confirm 경로를 사용한다.

같은 정보의 다른 창에 private 입력이 있으면 분류 취소를 거절한다. 자기 창의 private 입력과 다른 창의 private 입력을 구별하며 저장 시도·copy/Blueprint 계획도 기존 pending 검사에 포함한다. 분류 후 갱신과 독립 정보 창 재그리기에는 분류 projection 버전을 사용한다. 또 Browser 목록이 다른 종류/검색 결과로 필터된 경우에도 **bound editorViews의 draft revision**을 관찰한다. 이 둘이 빠졌을 때 실제 Undo는 Root로 돌아왔지만 독립 정보 창이 옛 카테고리를 계속 표시하던 결함을 실제 화면에서 재현·수정했다. 해당 순서의 UI Undo/Redo가 최종 검사에서 통과했다.

`v536_information_parent_views.py`의 실제 엔진/Chromium 검사는 다음과 같다. 모든 fixture는 독립 임시 디렉터리이며 사용자 프로젝트·계정·동의·AI 호출을 사용하지 않는다.

| 묶음 | 실제 결과 |
| --- | --- |
| normal | **5 PASS**. View1 분류/그룹 취소, 다른 primary 선택·view2 exact64 입력 보존, 실제 편집 이력 UI Undo/Redo와 늦은 분류 표시 갱신, 원본 창 닫기/새 창으로 열기를 통한 같은 slot 재진입, Save/cold, Review 취소 및 명시적 compiler Confirm. 원본/부모/등록 팩/다른 파일은 불변 |
| boundaries | **3 PASS**. 잘못된 bound id/미개방 view/복수 source 위조 거절, 실제 newer shared source에 대한 오래된 proof 거절·peer 원문/checkpoint 보존, 부분 그룹/다른 owner 취소 거절과 정확한 group/CAS 취소 |
| loss | **2 PASS**. 서버가 실제 적용한 응답만 격리 fixture에서 실패 응답으로 대체. 자동 move 재요청은 0회, 실제 창 재진입으로 결과 조회·명시 Save/cold 후 이미 적용된 그룹과 입력을 복원 |
| peers | **2 PASS**. 같은 정보의 view3에 새 64비트 입력이 있으면 view1의 분류 취소는 native 쓰기 없이 거절. 사용자가 view3 값을 명시적으로 원래 값으로 정리하면 기존 group 취소가 두 정보 창을 갱신. 별도 객체 view2 입력은 그대로 |
| 기존 기본 정보 창 | **6 PASS** 재검증. 원본 선택창 6영역 비교, 미저장 값 보호, 저장/취소/cold/Review/Confirm 및 다른 객체 입력 보존 유지 |
| projection | **3 PASS**. 기존 분류/상속/프로젝트 분리와 새 off-filter bound view 변경 감지·읽기 실패 억제 key 갱신·옛 category 제거 |

최종 실행 로그는 `/workspace/scratch/v536-information-views`의 `normal-final-4.log`, `boundaries-final-3.log`, `loss-final-4.log`, `peers-final-3.log`, `primary-regression.log`다. 초기 red 로그도 보존했다. Fixture의 dependency history가 category를 포함한다는 점, JSON 인코딩된 description의 재조회, 이미 숨긴 독립 창을 primary 선택으로만 열던 잘못된 재진입 경로, 소비된 bootstrap URL 직접 새로고침 문제를 바로잡았고, 검사/인증/CAS를 약화하지 않았다. 원본 UI의 기존 `새 창으로 열기`는 숨긴 동일 slot을 재사용하며 이를 실제 검사했다. 이후 순수 읽기 projection과 재그리기 버전의 실제 결함 두 곳을 함께 수정했다.

이 단계는 I4의 기본/독립 properties 정보 분류 지원 경로 수용이다. 모든 raw/copy/ABI 조합이나 파일 시스템 장애 주입·실제 기기를 전수 검사한 것은 아니다. native `extends`를 바꾸는 UI로 확장하지 않으며 I5/I6/B2와 A4–A6/M4/M11/M12는 여전히 별도 미완료다. 현재 원본은 저장소 v536 레퍼런스이며 새 사이트 변경은 섞지 않았다.

같은 정보의 미확정 분류를 다시 선택하는 경계도 확인했다. 기존 MoveFolders의 전역 미확정 hierarchy 차단은 같은 정보의 카테고리 재선택까지 막았다. schema 하나와 변경되지 않은 category 의존성으로만 이루어진 이전 그룹에 한해 이전/새 category를 하나의 후보에 합치고 동일 shared-state CAS로 처리한다. 새 그룹의 모든 멤버/이전 그룹 metadata를 함께 보관하므로 취소는 원래 저장한 그룹으로 돌아가고 새로운 category에 부분 그룹이 남지 않는다. 다른 moving source/복수 source 그룹/변경된 category/외부 소유/다른 root·retirement·atomic 그룹은 자동 결합하지 않는다.

`projects` 실제 검사 **3 PASS**(`projects-final-5.log`): A의 저장된 InfoA→InfoB 재선택이 Info/InfoA/InfoB 한 그룹이며 취소 후 저장된 Info/InfoA 그룹·checkpoint로 복원된다. 그 그룹을 두고 다른 정보 Leaf를 분류하려는 native 요청은 전체 거절된다. 같은 namespace·ID의 실제 A/B 프로젝트는 다른 분류/peer 64비트 입력을 각각 보관한다. Home A→B 후 은퇴한 A callback은 B에서 move 요청조차 보내지 않으며 두 checkpoint와 private 입력이 불변이다. A에서 Root 재편집/취소와 프로세스 cold·양방향 재진입 후 A/B 분류·입력·양쪽 원본이 분리 보존된다.

native 재선택 변경을 포함한 `normal-final-5.log`도 **5 PASS**로 다시 완주했다. I4 독립 창 검증은 현재 normal5 + boundaries3 + loss2 + peers2 + projects3이며, 기존 기본 정보 창6·순수 projection3은 별도 검사다. 모든 조합을 한 개의 성공률 분모로 혼합하지 않는다.

`atomic` 격리 실제 검사 **1 PASS**(`atomic-final-2.log`): 기존 정보 설명을 실제 UI에서 원자 저장하면 정보+ProjectManifest의 기존 `atomicEditGroup`이 생긴다. 이 상태에서 분류 그룹으로 바꾸려는 요청은 전체 거절되고 기존 그룹/checkpoint/원문/다른 창의 private 입력이 불변이다. 그룹을 자동 분해하거나 확정하지 않는다. 이 단계의 독립 창 검사는 **16개(5+3+2+2+3+1)**이며 기본 창6·projection3은 별도다. 원본의 카테고리 재선택은 지원하되 아직 확정하지 않은 다른 종류의 원자적 편집 그룹과의 혼합 저장으로 확대하지 않는다.

현재 로컬 최종 패키지는 `/workspace/artifacts/Confectory-v536-information-views-final/Windows-x64`의 전체 폴더다. 선언2322/marker 포함2323파일,131932651바이트. marker SHA-256 `061ae0a6a0cd02f26d0642f77e5384f73617a951be573afb09801dfe63fcd6ab`, 정렬 체크섬 목록 SHA-256 `10a16f5435076371bda30d2113e78b47ebd7428695e8d66b0c61d0634766436c`. Windows 교차 생성, PE/의존성/리소스/손상 거절 및 SDK 없는 격리 runtime·다른 cwd에서 패키지 관리형 웹 엔진/최소 로그인 화면 기동 검사가 통과했다. Windows apphost/WebView2 실행·실제 로그인·모델 호출·Library 전달 통과로 해석하지 않는다. 이전 `information-views` 폴더는 마지막 재선택/atomic guard 변경 전 중간 결과이므로 이번에는 `-final` 폴더를 사용한다.

## 독립 창 후속의 깨끗한 checkout 재현

실행 변경 `b55d52c6af76fb48d7327636d6b8e6e9253d1930`을 별도 깨끗한 checkout에 ff-only 적용했다. 그 checkout에서 새 Linux 엔진을 빌드해 warnings0을 확인하고 독립 창 normal **5 PASS**(분류/취소/실제 UI UndoRedo/창 재진입/Save/cold/Review/Confirm)를 재현했다. 순수 projection **3 PASS**, 실제 CRLF attribute pull·fresh LF 및 내용/encoding/BOM/binary/budget 거절을 포함한 **73리소스** 검사도 통과했다. source/test3215파일은 root/checkout에서 줄끝 정규화 후 같고, 최종 패키지의 추적 실행 소스2102파일은 이 실행 커밋과 바이트 일치한다. 실제 Windows 실행·모바일 기기·Library 전달은 여전히 미검증이다. 이 검증 기록 후속은 실행 코드나 패키지를 변경하지 않는다.
