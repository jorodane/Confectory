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
