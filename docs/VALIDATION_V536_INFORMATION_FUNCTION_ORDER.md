# v536 I5-5: 정보 자체 함수 순서

원본 제목 드래그와 Alt+↑/↓를 기본·독립 정보 창의 기존 순서·임시 저장·Review/Confirm 흐름에 연결했다. 함수 식별자, 이름·핀, 함수/구현/본문·참조·상속 정의를 변경하지 않고 현재 정보의 로컬 `contain function` 순서만 바꾼다. I5-1~4 지원을 유지하며 I5-6 연결된 전체 계약 편집은 미완료다. 전체 v536 UI 복원이나 실제 Windows 실행 완료가 아니다.

## 원본과 저장 의미

기준은 `196c605:reference/site-ui/Confectory-Editor-Prototype-v536.zip`의 `Confectory-v536/dist/app.js`, `bindOwnFunctionReorder`다. 제목에서만 drag를 시작하고 입력·버튼을 제외한다. before/after drop 및 Alt+↑/↓는 기존 행을 splice하여 이동한다. 원본 CSS·카드·핀·버튼을 그대로 쓰며 새 메뉴나 폼을 만들지 않았다.

새 `function-order` 입력은 기존 owner/copy/raw 저장 후보와 같은 검증·checkpoint CAS를 거친다. 최대 64개의 중복 없는 정확한 로컬 함수 집합만 받고, 다른 정보·프로젝트·상속에서 온 항목이나 누락을 거절한다. 이동할 수 없는 로컬 참조의 상대 순서를 보존한다. 다른 종류의 contain 자리, 주석·정확한 64비트 값·원문은 유지한다. 저장되지 않은 새 함수도 동일 후보에 명시적으로 포함할 수 있다.

기존 declaration 병합은 문장 내용만 비교해 순서 변경을 놓쳤다. 명시적인 typed 순서 변경에 한해 정확한 원문 clause를 재배치하고 독립 raw 변경을 보존하도록 했다. 실제 raw 순서/구성 충돌은 거절한다. 일반 필드 편집이나 단순 추가만으로 raw 순서를 바꾸지 않는다. 쓰기 충돌을 무조건 최신 기준으로 재시도하지 않는다.

Undo/Redo는 창별 입력 Map의 이전/다음 순서를 복원한다. 저장 중 새 순서 조작은 막아 결과와 입력이 섞이지 않게 한다. 응답이 불명확하면 저장 receipt를 조회하고 apply를 반복하지 않는다. 프로젝트를 바꾸거나 닫힌 이전 heading 이벤트가 도착하면 새 대상에 적용하지 않는다.

`변경 취소`는 마지막 명시적 임시 저장 이후 입력을 취소한다. 이미 저장한 순서를 저장 전 원본으로 되돌리는 동작이 아니다. 첫 cancel fixture는 그 의미를 잘못 기대하여 비활성 버튼에서 실패했다. 보호를 바꾸지 않고, 저장/cold 뒤 새 순서 입력을 만든 다음 실제 취소로 저장본·checkpoint·다른 창 입력을 보존하는 검증으로 수정했다. Native 첫 fixture의 Unicode 원문 문자열 비교도 JSON escape를 해독한 실제 description 비교로 고쳤다. 두 실패를 제품 성공으로 간주하지 않았고 수정한 검사를 완주했다.

## 검증

격리 프로젝트·실제 엔진/컴파일러·Chromium을 사용했다. 사용자 자료·실제 계정·유료 추론은 사용하지 않았다. 원시 근거는 `/workspace/scratch/v536-information-function-order`에 보관한다. 아래 수는 시나리오 내부 check 수이며 기능 개수나 통과/실패 비율이 아니다.

| 검사 | 결과 |
|---|---|
| Native SDK / Linux engine | warnings/errors/stderr 0 |
| Native 후보/원문 병합 | 4 PASS: ID/핀/원문 보존, 새 함수 혼합 및 누락/중복/보호/외부 거절, 독립 raw/주석 보존, 충돌 거절 |
| 실제 API | normal 2, 쓰기 실패/재시도 3, live 충돌 1, 상속/외부/보호 membership 거절 1 PASS |
| 실제 화면 | 기본 3, 독립 3, 쓰기 실패/재시도 4, 다른 창 입력/취소 3, 응답/조회 유실 2, live 충돌 2, 동일 namespace 프로젝트 전환 2 PASS (7회 실행, 총 19 check) |
| 기존 순수 회귀 | raw owner 병합 5, 함수 전체 삭제 9, 구현만 삭제의 추가 7 PASS. 구현 검사 안의 기존 함수 9 재실행은 중복 합산하지 않음 |
| 원본 화면 대조 | 동일 함수 카드의 13영역 위치·크기·색 일치, title/drag 속성 일치. style/consumer/runtime CSS는 기준 d596c09와 byte 일치 |
| Windows 교차 패키지 | win-x64 PE 2329파일. SDK 없는 runtime-only에서 패키지 엔진 웹 기동, 74개 리소스, 최소 연결창 렌더, 변조/의존성 누락 거절 PASS |
| 깨끗한 checkout/리소스 재현 | 소스 커밋 후 수행하여 최종 문서에 별도 기록 |

원본 [카드](evidence/v536-information-function-order/original.png)와 [어댑터](evidence/v536-information-function-order/adapted.png), 실제 엔진 [기본 창](evidence/v536-information-function-order/primary.png)·[독립 창과 보존된 다른 입력](evidence/v536-information-function-order/detached.png)을 남겼다. 13영역 측정은 정적 동일 데이터 카드 범위다. 실제 화면의 전체 pixel 일치나 네이티브 조작 검증을 뜻하지 않는다.

## 패키지와 한계

로컬 Windows 패키지: `/workspace/artifacts/v536-information-function-order/Windows-x64`, 진입점 `Confectory.exe`. .NET Desktop Runtime 10.0 x64와 WebView2 Runtime이 필요하다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미검증이다. 로컬 경로는 첨부 전달 성공이 아니다. 생성 빌드·프로필·로그는 Git에 넣지 않는다.

## I5-6 다음 경계

현재 `InformationDefinitions.function-edit`는 source hash·소유 origin/writable을 확인하고, 서명이 바뀔 때 Function/Parent/Imports/Requires/Defaults/Provides 참조가 있으면 전체 거절한다. 이 보호는 유지한다. 순서 변경은 서명 변경이 아니다.

다음은 기존 `BlueprintRootContract`·`BlueprintCallAbi`·`BlueprintCallAbiGroup`와 원자 owner/copy 저장 기반을 사용해 직접 소유 함수·구현·호출 typed import/wrapper·graph/code의 영향 목록을 하나의 후보/CAS로 결합하는 경계다. 비호환 핀은 명시적으로 매핑하며 자동 추측·삭제하지 않는다. 외부/공유 원본은 임의 수정하지 않고, 기본/독립 창·입력 보존·Undo/취소·실패/충돌/응답 유실·cold·Review/Confirm으로 검증해야 한다. 이 계약 편집은 아직 구현하지 않았다. I6/B2, A4~A6/M4/M11/M12 및 Helper 실제 작업은 별도 기존 후속이다.
