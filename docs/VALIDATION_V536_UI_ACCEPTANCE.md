# v536 기존 UI 통합 수용과 명시적 제한

`8366739f` 이후 기존 지원 UI를 마감하는 유한 검사다. ABI·raw 조합을 추가하거나 원본 `196c605` v536 레이아웃/메뉴/실행 의미를 변경하지 않았다. **지원된 경로의 수용 통과와 전체 원본 UI 완료는 다르다.** 격리 fixture만 사용했으며 실제 사용자 프로젝트·계정·인증파일·OAuth·유료 AI 호출·프로젝트 실행을 사용하지 않았다. 아래 PASS는 공통 준비를 포함하므로 서로 독립인 총 검사 수로 합산하지 않는다.

## 이번 고정 수용 목록

| 실제 경로 | 결과와 증거 |
| --- | --- |
| 등록 callable → 저장 복사본의 명시적 일반 ABI | `abi-copy.log` 5 PASS. 기존 슬롯에서 핀 매핑 취소/불완전 값/cold, 실제 비호환 출력 거절→Undo→명시 재선택, copy 출처/import/소비자 한 후보/CAS, Review 취소·compiler Confirm. 등록 팩/부모/다른 실행 대상/원본 불변 |
| 소유 ordinary 호출의 두 target | `abi-multiple.log` 5 PASS. 두 target의 일반 매핑·소스 closure를 한 후보로 저장, 성공 응답 유실 후 전체 receipt로 확인하여 중복 적용 방지, cold/Review 취소/명시 Confirm. 등록 all-target으로 일반화하지 않음 |
| 독립 문서/Pack Manager/모바일 목록 전환 | `documents.log` 6 PASS. 실제 server View 둘의 다른 원문 입력·동일 DOM, 문서 탭 선택/플로팅/일괄 닫기/재열기/Pack Manager와 재시작 보존, 모바일 Browser 검색·프로젝트 identity 복원. 소스 무변경 |
| 같은 이름 프로젝트 A/B의 모바일 편집 | `mobile-projects-2.log` 4 PASS. 다른 listing/project scope의 값·한글 설명 입력 격리, 실제 Home A→B·재진입, 폐기된 A callback이 B에 쓰지 못함, 재시작 후 두 입력·원본 보존 |
| whole-body C# 특수 입력/출력·폭 전환 | `mobile-contracts.log` 6 PASS. 보호된 입력과 out/return·native 이름 구분, 비호환 타입 거절/취소, 값/ref·한글/emoji 코드 입력의 desktop/mobile/cold 보존, 한 원자 그룹 Save·Review 취소·390폭 compiler Confirm |
| 모바일 일반 카드의 편집 수명 | `mobile-lifecycle.log` 4 PASS. 카드·상세·코드 취소, 한글/emoji/줄바꿈과 desktop/mobile 전환, Save는 checkpoint만 변경, 재시작 미저장 설명/본문 검토·명시 Save와 Review 취소/Confirm |
| 터치·검색·뷰 좌표 | 최초 `mobile-touch.log`와 수정 후 새 엔진의 `mobile-touch-final.log` 각4 PASS. 원본 View/전체 보기/미니맵/설명, Chromium protocol pan/pinch/touchCancel·로컬 finder. 최종 경로는 합성 composition Enter/Escape가 한글 검색어·overlay를 보존하고 일반 Escape만 닫는지도 검사. 실제 기기 터치가 아니며 카메라 이동이 source/실행 계획을 쓰지 않음 |
| 공통 모바일 shell | `mobile-shell.log` 7 PASS. 760/761 및 coarse-pointer1000 breakpoint, 패널 상호 배제/Escape/모달 우선·동일 한글 입력 DOM, visual height composer와 새 프로젝트 lifecycle. controlled renderer와 모의 caption bridge이며 native 증거가 아님 |
| 요소 내부 원본 시각 대조 | v536 원본 렌더 함수와 **원본 CSS**로 그린 같은 데이터의 기본 속성10/비어 있지 않은 모듈·핀 포함19영역을 실제 adapter/engine CSS와 비교하여 정확한 rectangle 일치. `visual-*-reference-css.log`. 원본/adapter 캡처를 직접 열어 확인. 하위 목록은 빈 fixture이고 모든 데이터·전체 화면 pixel equality는 아님 |

## 발견한 결함과 최소 수정

찾기 패널이 `isComposing` Enter를 다음 결과 이동으로 처리했다. 두 한글 결과의 controlled renderer에서 `1 / 2`가 `2 / 2`로 바뀌는 실패를 `find-ime-red.log`에 보존했다. 패널은 키 전파를 계속 막되 조합 중/legacy keyCode229이면 Enter·Escape shortcut을 실행하지 않는다. 전역 Ctrl+F도 같은 조합 가드를 사용한다. 일반 Enter/Shift+Enter/Escape/Ctrl+F·폐기된 scope 정리는 그대로다. `find-ime-green.log` 2 PASS로 실제 결과·검색어·overlay·focus를 검증했다. 이는 실제 OS IME 검사가 아닌 합성 composition event의 renderer 검사다.

기존 모바일 테스트의 `정의 열기` 버튼은 현재 원본 Browser 행 구조에 없다. 첫 `mobile-projects.log` 실패는 해당 locator 대기이며 제품 실패나 통과로 처리하지 않았다. 같은 Browser의 실제 행 Enter 열기로 driver를 고쳤고, 새 fixture의 전체 프로젝트/카드/터치 흐름을 완주했다. 새 제품 버튼이나 우회 endpoint를 추가하지 않았다.

두 기존 visual oracle은 v508 기본값을 유지하면서 v536을 명시 선택할 수 있다. v536 선택 시 원본 CSS로 원본을 먼저 측정하고 이후 engine CSS/adapter를 측정한다. 같은 engine CSS를 양쪽에 쓰는 비교만으로 원본 일치를 주장하지 않는다. 원본 CSS와 engine CSS의 파일 전체가 동일하다는 주장도 하지 않는다.

## 영역별 수용 판정

- **연결된 지원 UI:** 기존 상단바·Workspace/Pack Manager·Helper 생성/배치/삭제·프로젝트 목록/생성·문서/독립 View·Browser의 지원 Data/참조/이름/카테고리/복구·요소 상속/자체속성/기능모듈/복사·지원 Blueprint와 실제 Run/저장 이력 읽기는 각 기존 검증 문서의 범위다. 이번에는 위 문맥 교차·모바일 수명을 추가 수용했다. 변경하지 않은 과거 전체 검사를 다시 실행했다고 표시하지 않는다.
- **실제 연결/계약 잔여:** 등록 callable all-target의 receipt closure, copy-alltarget/상속/opaque·whole-body·같은 callee 여러 사용의 provenance/remap, 공유/고정 반환 이름·잠정 빈 출력, 영역/다중 선택과 나머지 readonly/async/내부 흐름 문맥은 전체 연결 미완료다. primitive runtime이 일부 존재하는 것과 UI 계약 결합 완료를 구분한다. Info legacy inline/모든 compound·multiple 정의 전환·일부 ref/function/imported·부모/기능 및 일반 Browser 외부 runtime Data/범용 mutation·작업자 배지도 제한이다. 지원 경로에서 새로 재현된 미해결 오류와 이 지원 제한을 섞지 않는다.
- **그대로 차단한 조합:** raw+저장 복사본 ABI/기존 본문/다중 target ABI/Set-property/다른 Blueprint 계획, 여러 raw 또는 독립 properties+copy. 기존 한 raw+기본 요소 typed+새 private copy 범위만 지원한다. 이번 수용에서 순차 Save·자동 병합·자동 Confirm으로 확대하지 않았다.
- **backend 부재:** Helper 이미지 제공자/자산·이력, 실제 협의·승자·shared Confirm/신문고, 실행창 내장 renderer/FPS와 일부 수신자 전달. 데모/저장 이력/프로세스 상태로 가짜 성공을 표시하지 않는다. 새 provider나 사용자 권한을 만들지 않는다.
- **기기/전달 미검증:** Windows apphost/WebView2·drag/snap/DPI/native IME, 실제 Android/모바일 터치, Library 전달. 교차 빌드·Linux managed 웹 기동·합성 터치는 이 결과를 대신하지 않는다. Library의 기존 tools/list 네트워크 장애에 새 복구 근거가 없어 재호출/우회 업로드하지 않았다.

이 목록으로 이번 수용 범위를 고정한다. 지원 제한을 계속 새 조합 검사로 확장하지 않는다. 이후 전체 상태 판단과 Helper의 실제 에디터 도구 누락 감사는 구별하고, UI endpoint를 Helper에 자동 노출하거나 Confirm/프로젝트 실행/다른 프로젝트 권한을 추가하지 않는다.

## 재현·빌드 기록

로그는 `/workspace/scratch/v536-final-acceptance/`와 각 로그의 evidence 폴더에 보존했다. 일부 기존 실제 엔진 검사는 `/workspace/scratch/v508-elements/actual13-source-fixture`라는 격리 fixture를 전제로 하며 새 checkout만으로 자동 준비되는 일반 단위 테스트라고 주장하지 않는다. 새 찾기 검사는 자체 DOM fixture를 만든다. ABI/문서/카드 검사는 선행 `8366739f` 엔진에서 수행했고 유일한 제품 변경인 find 조합 가드 후에는 새 엔진의 실제 터치/finder 경로와 집중 renderer를 재검증했다. 관련 없는 전체 ABI 검사를 다시 실행한 것으로 표시하지 않는다.

최종 Linux 엔진 생성 exit0/warnings0,73리소스의 canonical/exact SHA·크기와 변경 Python 구문·diff 검사를 통과했다. 새 Windows x64 교차 패키지의 로컬 경로는 `/workspace/artifacts/Confectory-v536-ui-acceptance/Windows-x64/Confectory.exe`를 포함한 전체 폴더다. .NET Desktop Runtime10 x64 및 WebView2가 별도 필요하며 동반 파일을 유지한다. 패키지 구성/기동·checksum·깨끗한 checkout 결과는 후속 검증 기록에 추가한다. 실제 기기 실행/Library 전달 완료를 의미하지 않는다.

`package-probe.log`는 선언2321파일·리소스73개, PE/의존성/변조 거절, 별도 cwd와 설치 SDK 없는 runtime-only packaged managed 웹 기동·최소 로그인 렌더를 통과했다. Windows apphost/WebView2는 실행하지 않았다. marker 포함2322파일/131882098bytes의 manifest hash를 모두 확인했고 포함된 추적 소스2101파일은 이번 실행 코드와 바이트 단위로 같다. marker SHA-256은 `cff7c4f7dd383831122d45ccd4651312b91da71538c0f14a25887195f46b0e1d`, 정렬 checksum 목록의 SHA-256은 `6318d2e98aba7d52bd4c6a42c37a4c19c427b6b64facdc53c5735a8c58164c79`이다. 사전 검토11파일(구현2/테스트6/문서3)의 비밀 패턴 검출0, 생성물/로그/사용자 데이터는 Git 후보에 없다. 패턴 검사는 모든 비밀 부재의 증명이 아니며 실제 profile/인증파일은 읽지 않았다. 전체 파일 목록·checksums는 scratch의 `review/`에만 둔다.

구현 커밋 `5fd3967019927a2d56a67649ef53f034165ef765`을 별도 깨끗한 checkout에 ff-only로 적용했다. Release solution은 경고/오류0, Linux 엔진 생성 exit0/warnings0이고 retained-CRLF attribute pull·fresh-LF의73리소스 시작·변조/인코딩/BOM/binary/budget 거절이 통과했다. 원래 checkout 바이트는 유지됐고 두 checkout의 추적 구현/테스트3202파일은 줄끝 정규화 후 같다. 최종 문서 커밋은 실행 코드를 바꾸지 않는다. 수용한 지원 경로에서 이번 검사 후 남은 재현 오류는 없지만 위의 연결 제한·백엔드 부재·기기 미검증은 해제하지 않는다. 원격 게시 SHA와 clean 상태는 체크포인트에서 확인한다.
