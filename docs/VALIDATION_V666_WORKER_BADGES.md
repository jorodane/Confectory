# v666 실제 작업자 배지 B2

## 원본과 구현 경계

기준은 저장소 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`이며 SHA-256은 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다. `dist/app.js`의 `browserWorker`(3965행), `browserFolderWorkers`(3975행), `updateBrowserHeaderWorkers`(2035행), `bindWorkerCount`(3905행), `data-object-workers`(2319~2331행)를 따른다. 폴더 숫자는 자식/작업 개수가 아니라 **고유 Helper 수**다. 원본 portrait/count/popover CSS와 기존 도우미 프로필 진입을 재사용한다. Preview/Compact/Data 선언 카드, 폴더/namespace/root 계층, 현재 Browser 범위 헤더와 기본/독립 선언 헤더에 표시한다. 새 배정 UI·자동 배정 정책·도착 대기·권한 부여는 만들지 않는다.

`assignmentWorkers`는 활성 ProjectContext의 표시 전용 요약이다. 기존 작업 조작에 쓰이는 `workers`와 분리한다. 현재 소유자 `local-user`에게 보이는 전역/해당 프로젝트 Helper와 기존 등록 Agent 연결만 사용한다. 도우미별 기존 Task 저장 경로, 정확한 project/owner/chief, Task owner Helper 및 상태를 검증한다. 다른 사용자/그룹/비공개 프로젝트의 조회나 권한팩 정책을 추가하지 않는다. 부모·외부 선언의 배지를 소유 선언으로 잘못 옮기지 않으며 외부 원본을 읽거나 수정하는 새 권한을 만들지 않는다.

직접 배정된 노드의 등록 `/body:` 소유 선언과 일반 Task의 기존 `semanticTargets` ID를 사용한다. 함수의 명시 `provide` 관계로 구현 노드와 함수 정의를 연결한다. 이름/별칭/문자열/C# 본문으로 사용처를 추정하지 않는다. 관측된 관계는 기존 프로젝트별 Browser projection을 사용하므로 다른 편집 대상을 선택한 뒤에도 연결을 유지하고 프로젝트 간에는 공유하지 않는다.

배정은 ready/dispatching/running/awaiting-verification 상태에서 표시한다. 실제 현재 owner가 관측한 `draftContributions`와 dirty source만 **미반영 변경**으로 표시한다. 사용자가 편집한 `supportingSources`는 **지원 초안**으로 구별하며 Worker가 작성했다고 표시하지 않는다. 취소/완료 자체를 작업 진행으로 표시하지 않는다. 현재 실행 owner가 없는 저장 running/dispatching 기록은 **배정 확인 필요**로 표시하고 실행 중이라고 주장하지 않는다.

## 조회·보호

배지 조회는 기존 FileSnapshot과 Helper 소유 범위를 사용하며 Task 실행/복구 세션을 열지 않는다. 저널 schema/project/owner/chief/Helper, 파일당 4MiB·총 8MiB/32파일·각 1024 Task를 검사한다. 프로젝트 내부 링크 경로는 거절한다. 손상/권한 불일치한 기록은 제외하고 읽을 수 있는 독립 기록은 유지한다. 공개 표시 요약에 원문 요청·목표·진행 내용·자격증명·파일 경로를 추가하지 않는다. `assignmentWorkersStatus`로 no-project/available/partial을 구분한다.

기존 UI 갱신 주기 안에서 최대 초당 한 번 조회하고 이전 source 오류/작업 결과/보관 안내를 지우지 않는다. 소스·체크포인트·원자 후보·최종 CAS·권한 승인·Task 상태를 쓰지 않는다. badge/profile 선택은 기존 보이는 Helper 범위와 현재 프로젝트를 다시 확인하며 자동 배치·전송·Review·Confirm·Task 재생을 하지 않는다. 캐릭터 이동 및 3D 팩과 독립이며 권한 팩이 없어도 기존 실행 검사는 유지한다.

저장된 배정은 cold 조회가 가능하다. cold에서 현재 실행 owner의 dirty/provenance 증거가 없으면 변경 작성자를 추정하지 않는다. 기존 Task의 출처와 원본은 보존하며 이 배지가 실행 복구·작업 성공·도메인 검증을 대신하지 않는다. 다른 사용자/그룹의 가시성은 실제 신원/권한 backend와 별도 권한팩 연결이 선행한다.

## 검증

집중 검사와 최종 독립 checkout/새 Windows 교차 패키지/압축 복원의 확정 결과를 아래에 추가한다. 새 B2 검사는 실제 로컬 Task 배정·명시 취소·일반 semantic target, 도우미별 저널, 고유 Helper 집계/원본 팝오버·세 밀도·기본/독립 헤더·입력 보존, cold·잘못된 소유/프로젝트/Helper/저널/링크, 프로젝트 없음/동일 이름 프로젝트 왕복을 검사한다. 실제 생산 provider/tools를 사용하는 소유 loopback fixture로 미반영 변경/지원 초안을 검증한다. 개인 파일·외부 계정·유료 추론·실제 프로젝트 실행은 사용하지 않는다.

기존 enum 보관·값/정의, 핀·헤더·카드 이미지, 소유 복합/중첩 편집과 입력/Undo/취소/실패/충돌/응답 유실/Review/Confirm 회귀를 유지한다. 진단 중 발견한 실제 연결 결함은 함수 `provide`의 생략 가능한 function 필드를 필수로 보던 검사와, 관계가 없는 현재 선택 응답 대신 프로젝트별 관측 관계를 사용해야 했던 점이다. 독립 일반 선언 제목도 기존 헤더에 연결한다. fixture의 범위 변경 후 갱신/원래 함수 창의 다른 keep 조작/최대 1초 표시 주기 대기 문제는 제품 기능을 완화하거나 레이아웃을 바꿔 통과시키지 않고 실제 계약에 맞게 검사한다.

실제 Windows apphost/WebView2·물리 모바일·전체 UI 및 Library/Space 전달은 미검증이다. C# 종류 표현과 사용 중 종류 항목의 명시적 소비자 대응은 별도 잔여이며 이번 단위에서 결정하지 않는다.

## 집중 검증 기록

실행 기록은 `/workspace/artifacts/v536-verification-managed/runs/54d2e3765bc449d39c91ad51bd0a002a.json`이다. `ui-cancel-refresh`의 전체 배정/취소/cold/프로젝트/가시성 검사, `contributions-confirm`의 실제 생산 provider/tool 출처와 명시 compiler Confirm 후 제거 검사, `projection-final`이 통과했다. 진단 실패의 원문·소유 fixture·스크린샷·후속 수정 근거를 동일 실행 증거 ZIP에 보존했다. 증거 SHA/현재 소스 overlay와 재생성 가능한 출력 manifest를 남긴 뒤 이 실행이 만든 RAM workspace만 정리했으며 과거 자료는 삭제하지 않았다. 최종 패키지 검증에는 기존 Worker 조작 요약을 그대로 보존한 소스가 사용된다.
