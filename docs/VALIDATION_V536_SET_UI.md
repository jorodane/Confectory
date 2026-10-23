# v536 Set와 속성 읽기 UI 연결 검증

기준 게시본 `66b825f`의 Set backend에 원본 v536 카드·모바일 화면과 속성 읽기를 연결했다. 원본 ZIP/CSS 배치와 기존 AI 연결·동의·프로젝트 권한은 변경하지 않았다. **전체 v536 UI 완료 보고가 아니다.**

## 동작과 저장 경계

Set은 원본 260px 카드, 저장 대상, 타입, 값과 저장한 값 출력을 재사용한다. 원본 CSS는 카드 내부 이름 필드를 숨기므로 데스크톱 이름은 기존 출력 핀의 inline 편집에서 변경한다. 모바일은 원본 저장 대상·출력 필드를 사용한다. 새 저장소/Set/출력/직렬 삽입/값 연결은 기존 `authorBatch` 안의 단일 `setPlan`과 checkpoint CAS로 저장한다. 출력 연결은 `{node:setId,output:"stored"}`이며 현재 대상 local의 실시간 읽기로 바꾸지 않는다. `long` 원문은 typed JSON 경로로 보존한다. 이전 void Set은 단순 열기로 이행하지 않으며 명시적 편집 시 새 출력 셀을 함께 준비한다.

속성 카드는 원본처럼 **실행 핀이 없다**. 새 읽기의 출력을 사용할 작업에 명시적으로 연결하면 그 작업의 현재 단일 main-line 입력 바로 전에 기존 node-time 읽기를 연결한다. 화면 좌표나 전체 실행의 첫 필드값으로 시점을 추측하지 않는다. 원본 카드/데이터 선과 별개로 실제 graph에는 읽기 실행 지점이 유지된다. 이미 만들어진 출력은 그 읽기의 값/참조를 보존하고, 별도의 읽기는 해당 실행 시점의 현재 값을 읽는다. 다음 기능 호출에서도 다시 읽는다. 배열/객체를 임의 deep-copy하거나 getter/ref로 바꾸지 않는다. 기존 property-set의 대상·값은 원본 함수 카드/모바일 값 편집에 연결하며 C# 작성 기능으로 위장하지 않는다.

`propertyPlan`은 `authorBatch`에서만 사용하는 단일 후보다. 선택한 descriptor와 receiver를 재검사하고 읽기 노드/필요한 typed import/소비 binding/실행 연결 및 Set 변경을 함께 검증·저장한다. 직접 호출, stale descriptor, 자료형/가용성 오류, 지원 밖 action, slot/private/copy provenance는 거절한다. 최종 원본 반영은 별도 compiler Review/명시적 Confirm이다. 이미 일치하는 accessor import가 있으면 metadata가 구현 원문을 불필요하게 재포맷하지 않도록 수정했다.

저장 성공 응답 유실 뒤 늦은 입력이 기존 source proof 때문에 영구 차단되는 결함을 재현·수정했다. 동일 시도의 receipt와 두 번 확인한 정확한 저장 closure가 일치한 경우에만 그 직전 proof에서 파생된 늦은 입력의 기준을 갱신한다. 동료 변경을 새 버전으로 자동 승격하지 않는다. 다음 저장도 현재 closure/checkpoint CAS를 통과해야 한다. 성공한 요청의 captured 입력만 지우며 새 텍스트/다른 초안은 유지한다. 다음 저장에서 필요한 Set 계획을 현재 metadata로 다시 준비한다.

## 실제 실행한 검사

모든 프로젝트/프로필은 `/tmp` 격리 fixture다. 계정·인증파일·유료 AI 호출·실제 사용자 프로젝트 Run은 사용하지 않았다. 아래 UI 검사는 생성 Linux 엔진과 실제 Chromium이며 Windows/WebView2 또는 실제 모바일 기기 검사가 아니다.

| 검사 | 결과와 증거 |
| --- | --- |
| Set 기본 화면/값/모바일/cold/원자 Save/Review 취소/명시 Confirm | 6개 통과. `/tmp/confectory-set-plan-tiykdpgx`, `ui-test7.log`. graph만 원본 반영. |
| 새 Set 검색·삽입/타입·기존 대상/이름·값/기존 successor/cold 저장 | 공통 열기 1 + 신규 2개 통과. `/tmp/confectory-set-plan-89i_3m2i`, `ui-create1.log`. |
| peer/checkpoint 충돌과 재시작 후 입력 보존 | 공통 1 + 신규 2개 통과. receipt 수정 뒤 재검증 `/tmp/confectory-set-plan-qx_lno18`, `ui-conflict2.log`. |
| legacy void Set 열기 무변경/명시적 편집 원자 이행 | 공통 1 + 신규 2개 통과. `/tmp/confectory-set-plan-q1o1p59j`, `ui-legacy3.log`. |
| 새 노드 구조 Undo/불완전 이름 재진입·재시작·저장 거절 | 공통 1 + 신규 2개 통과. 최종 source `/tmp/confectory-set-plan-51r09c9n`, `ui-final-cancel-raw.log`. 저장 전 입력은 live graph에 반영되지 않는다. |
| 복사 provenance의 읽기 전용 표시/위조 Set 저장 거절 | 공통 1 + 신규 2개 통과. `/tmp/confectory-set-plan-joas3v3x`, `ui-readonly1.log`. 서버가 `requiresCoupledCopy`를 투영하며 UI 숨김에만 의존하지 않는다. |
| 실제 성공 응답 유실 + 저장 중 새 입력 + receipt 복구/cold/명시 재시도 | 공통 1 + 신규 2개 통과. `/tmp/confectory-set-plan-mv6zd82u`, `ui-loss4.log`. 엔진에는 먼저24만 저장, UI의 늦은27은 유지, 재시작 후 명시 저장으로27 적용. 네트워크 응답만 fixture에서 변조했다. |
| 속성 기존 읽기/새 검색 선택/모바일 receiver·소비 연결/cold 단일 후보/Confirm/실제 값 | 6개 통과. 최종 source `/tmp/confectory-set-plan-f44941pk`, `property-final-ui.log`. 격리 CLR 실행 `1020`, `2030`: 10 읽기→20 쓰기→별도20 읽기, 다음 호출20→30. 같은 counter에 후속 Set을 해도 앞 보관 출력10/20은 유지. engine `projectRun`은 호출하지 않았다. |
| Property 후보 부정·원자성·descriptor/receiver·실행 시점·receipt | 기존 import 문맥8개 통과 `/tmp/confectory-set-plan-bj4nj8vx`, `property-plan1.log`; 누락 import 문맥8개 집중 재검증 `/tmp/confectory-set-plan-qn40rgyu`, `property-new-import.log`. 두 문맥의 반복 검사를16개의 서로 다른 기능으로 합산하지 않는다. |

Set 기본/6개 별도 모드의 공통 열기 검사는 중복이다. 위 Set UI는 합계24개 실행 label 중 **고유 시나리오18개**이며 다른 검사와 무분별하게 합산하지 않는다. copy property 후보, 패키지/checkout 최종 결과는 아래 마무리 기록을 따른다.

정밀 대조는 `v536_set_visual.py`가 원본 v536의 HTML 표현식/실행 rail/출력 signature renderer를 직접 읽어 수행한다. Set shell/type의13개와 property shell의8개 사각형이 일치했다. live plug/rail skin/backend/전체 앱 시각 일치 주장은 아니다. `/tmp/confectory-set-visual-nvf54dg4` 및 최종 `ui-final-visual.log`에 원본/수정 PNG와 측정 JSON이 있다. 실제 runtime PNG는 기본 및 속성 UI fixture의 `set-desktop.png`, `set-mobile.png`, `property-mobile.png`다. 외부 Library 첨부로 전달하지 않았다.

기존 enum 불완전 입력 재진입 renderer5개가 통과했다 (`/tmp/confectory-enum-reentry-81034acm`, `ui-enum-regression.log`). 이는 controlled renderer다. 추가 실행한 과거 v508 root/action geometry probe는 오래된 mock이 `featureBodies`에 `rows` 없이 응답하여 실패했다. mock을 현행 catalog 계약으로 고쳤으며 assertion을 제거하지 않았다. 재검증22영역 통과: `/tmp/confectory-feature-author-visual-qs1uj_bm`, `ui-action-visual-fixed.log`. 전체 v536 비교로 합산하지 않는다.

## 지원 제한과 다음 묶음

- 원자 후보는 동일 소유 ordinary root/main-line 읽기다. 새 읽기의 첫 소비 연결에는 명확한 단일 실행 입력이 필요하다. branch/private/slot/copy의 자동 시점 추측이나 계약 변경은 지원하지 않는다. 기존 읽기 실행 지점과 연결을 임의 재정렬하지 않는다.
- 저장된 Set 출력 셀의 타입/초기값은 유지한다. 새 Set의 타입을 선택할 수 있다. 기존 저장 타입을 바꾸는 UI는 비활성이다. scalar long/receiver object의 실제 UI·실행을 검증했으며 모든 배열/참조 UI 조합을 검사했다고 주장하지 않는다.
- 명시적 mutable property-ref/자기 receiver/등록 타입 전체 선택/기존 읽기 삭제와 모든 graph 재구성은 이번 어댑터의 완료 범위가 아니다. owner 검색은 현재 API의 첫 페이지32개/지원 필드에 한정한다. 일반 읽기를 mutable ref로 치환하지 않는다.
- 복사본 ABI·다중 target·선언/속성+copy 혼합 Save는 다음 별도 원자 결합 저장 묶음이다. 현재 차단을 유지한다. 새 Agent 동의·Confirm·프로젝트 실행·다른 프로젝트 접근을 추가하지 않는다.

## 빌드와 배포 검증

solution Release 컴파일0경고/0오류 (`property-solution.log`), 최종 Linux 생성 빌드 (`final-build.json`), JS 문법 및 diff 검사 통과. Windows 교차 패키지는 `/workspace/artifacts/Confectory-v536-set-property/Windows-x64/Confectory.exe`이며 폴더 전체가 필요하다. .NET Desktop Runtime10.0 x64와 Edge WebView2 Runtime이 필요하고 자동 설치하지 않았다. 실제 Windows 더블클릭/드래그/네이티브 창 동작이나 실제 기기 터치 검사는 수행하지 않았다. 로컬 경로는 사용자 첨부/다운로드 전달 성공을 뜻하지 않는다.

패키지 checksum/SDK-less managed web 시작/리소스/clean checkout 및 게시 결과는 최종 마무리 기록에 추가한다. 전체 UI나 실제 Windows 실행 완료로 표현하지 않는다.

마무리 전 로컬 수용: Property copy provenance 후보1개 거절 통과 (`/tmp/confectory-set-plan-ypqmadn_`, `property-copy-boundary.log`). 최종 Set13/property8 치수 일치 증거는 `/tmp/confectory-set-visual-5rmkyzin`이다. Windows 패키지는 선언 파일2307개(검증 marker 포함2308개)이며 checksum 목록 전체를 검사했다. SDK 없는 managed packaged web 시작, checkout profile 재사용/명시 override, 누락/변조 거절, 최소 로그인 렌더와 리소스68개를 확인했다 (`/tmp/confectory-desktop-package-mk8w02pm`, `windows-package-probe.log`). apphost/WebView2 실행은 하지 않았다.

패키지 marker SHA-256: `5540d3aa0a75a8a9bfb04b23982a716f62f156028841bd64e76eb8b260193a9b`. 전체 checksum 목록 SHA-256: `fa3ff226ac9cb988d626c486392863ad83559a037790f3b4b5159e03535d3c0e`. 구현7/테스트5/문서5 파일을 검토했고 생성 빌드·인증정보·로그·사용자 데이터는 Git 게시 대상에 없다. 패턴 검토에서 발견0건이며 모든 가능한 비밀 부재의 증명이라고 표현하지 않는다.

깨끗한 checkout 수용 완료: 구현 커밋 `81205e2152be9d23aa0a2fa3c78079227a096489`를 별도 clean checkout으로 fast-forward한 뒤 solution Release0경고/0오류와 생성 Linux 엔진 빌드가 통과했다 (`checkout-solution.log`, `checkout-engine.json`). 실제 legacy CRLF checkout→일반 attributes pull과 fresh LF checkout에서 원본68개 canonical/exact 리소스를 확인했고 content/encoding/BOM/binary/budget 변조를 거절하며 원본 바이트를 보존했다 (`checkout-resources.log`). 검사 후 양쪽 tracked 작업 트리는 깨끗했다. 최종 enum controlled renderer5건도 통과했다 (`/tmp/confectory-enum-reentry-zcoe2km4`, `ui-final-enum.log`). 이 검증 기록 뒤의 변경은 문서뿐이며 구현·리소스·패키지 bytes는 같다.
