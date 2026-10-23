# v536 문서 분리·탭 일괄 닫기·플로팅 첫 묶음

사용자가 지정한 main 196c605의 v536 ZIP을 읽었다. 원본 `app.js`의 `detachDocumentTab`, `documentTabContext`, `closeRelatedWorkspaceTabs`, `activateWorkspaceTab`, `placeWindow`, `clampFloatingPosition`을 기준으로 한다. 원본은 브라우저 내부 플로팅 창이며 새 OS 창이 아니다. Windows 창 제어·다중 네이티브 창 구현으로 설명하지 않는다.

## 연결 범위

- Workspace가 배경일 때 문서 탭을 끌면 캔버스 좌표에 배치한다. 문서/Pack Manager가 배경이면 화면 좌표의 플로팅으로 분리하며 배경을 유지한다. 기존 domain 창과 입력 DOM을 그대로 옮기고, 편집 View·초안·권한을 새로 만들지 않는다.
- 원본의 워크스페이스로 이동/탭 닫기/다른·오른쪽·왼쪽·모든 탭 닫기를 기존 이동/닫기 경로에 연결한다. 고정 Workspace/Pack Manager는 대상에서 제외한다. 메모와 하위 Workspace를 닫아도 원본 데이터·하위 공간을 삭제하지 않는다. 원본에서 닫을 대상이 없는 메뉴는 비활성이다.
- 기존 source/editor의 닫기는 숨겨 보존하는 계약을 유지한다. 실제 View 해제·소스 Save/Confirm이나 프로젝트 실행으로 바꾸지 않는다. 서버의 프로젝트·View 소유권과 CAS/명시적 확정은 그대로다.
- 문서 외곽은 원본처럼 탭 아래38px, 모바일32px부터 Workspace 폭을 사용한다. 문서 위에 따로 넣었던 Workspace 복귀 버튼과 창 접기/닫기를 제거하고 원본 탭 메뉴를 사용한다. 이동 뒤에는 기존 창 제어가 다시 나타난다. Browser/Blueprint 내부의 미완료까지 완성했다고 주장하지 않는다.
- 플로팅은 Workspace 카메라 배율을 적용하지 않는다. 화면/레이어와 메타데이터의 표시 소유자를 분리한다. `floatingTabId`는 해당 프로젝트의 표시 참조일 뿐 도구/계정/다른 프로젝트 권한이 아니다. 원본처럼 배경 문서를 닫으면 참조가 비어도 다른 탭 위에서 플로팅 표시를 유지할 수 있다. 이전 저장본의 필드 부재와 호환한다.
- 배치 전용 Undo/Redo 기록은 기존9필드 형식을 유지하며, 현재 플로팅 참조와 실제 편집 메타데이터를 덮어쓰지 않는다. 오래된 프로젝트 메뉴/드래그와 잘못된 복수 창 요청은 현재 소유자 검사로 중단한다.

## 검증 기록과 확인한 결함

최종 production `runtime.css`를 사용하는 통제 렌더러 **8건 PASS**: `documents-renderer-8.log`, `/tmp/confectory-document-renderer-svqq26el/evidence.json`. 실제 Workspace/document/note 모듈을 실행하되 domain 서버·네이티브 창은 fixture이다. 정확한 DOM/독립 입력, 원본 문서 외곽, Pack Manager/다른 문서 위 분리와 포커스, Workspace 배치, Escape 취소, 좌/우/다른/전체 닫기·재열기, 고정 탭 보존, 메모/하위 공간 원본 보존, A→B→A 및 오래된 A 메뉴가 B에 작용하지 않음을 확인했다.

이전 renderer의 `$`가 root 인수를 무시해 다른 창 본문을 덮은 실패와, 닫을 다른 탭이 없는 비활성 메뉴를 누른 실패는 fixture 오류로 보존했다. 해당 메뉴를 활성화하거나 보호를 제거해 통과시키지 않았다.

실제 생성된 Linux 엔진 검사는 정상 서버 계약으로 격리된 Unit/Monster 편집 View 두 개를 준비한 뒤 실제 UI로 탭/분리/닫기를 조작한다. 실제 사용자 계정·토큰·유료 추론 없이 원본 소스 바이트를 대조한다. 테스트 API 우회나 배포된 엔진의 새 fixture endpoint는 추가하지 않았다.

실제 엔진에서 다음 결함을 확인·수정했다.

1. 첫 플로팅은 실제 로드된 `runtime.css`에 레이어 규칙이 없어 Pack Manager 뒤에 가렸다. `consumer.css`만 읽는 기존 renderer 환경과 실제 배포 진입점 차이를 확인하고, production 스타일에 연결했다. 최종 renderer도 같은 스타일로 검사한다.
2. 초기 분리 메타데이터가 메모리에는 있으나 저장 layout에 연결되지 않았다. 실제 Save 요청/표시 자료로 확인해 직렬화에 연결했다. 배경 문서를 닫아 참조가 비는 정상 동작은 필드가 잘못 지워진 것으로 처리하지 않는다.
3. cold 복구에서는 원본 텍스트가 presentation에 남았지만 편집 View가 없었다. 저장된 Pack Manager를 먼저 표시하면서 capture가 아직 없는 View 목록으로 `editorBindings`를 덮었다. 복구 계획을 먼저 고정하고 기존 `recoveryFailed` 보호를 복구 완료까지 유지하도록 순서를 수정했다. 실패 시 계획/입력을 보존하고 서버의 View 재개 계약을 그대로 사용한다.

최종 실제 엔진 **6건 PASS**, `documents-engine-4.log`/session86996 exit0, `/tmp/confectory-document-engine-pzj4ltxx/evidence.json`. 마지막 cold 수정 후 전체 묶음을 재실행해 독립 View2개·입력 DOM·Pack Manager 위 표시·실제 layout 저장·문서 배경·일괄 닫기/Browser 재열기·실제 프로세스 cold 복원·모바일 재열기를 통과했다. 모든 원본 소스 바이트가 그대로이고 Save/Confirm/실행/AI 호출은 없었다. 이전 재시작 실패를 assertion 완화로 숨기지 않았다. 원본에서 배경 탭 닫기 후 표시 참조가 비는 경우는 마지막 저장본과 동일한 참조인지 비교하며, 실제 프로젝트/소스 View 소유자는 별도로 검증한다.

## 원본 비교와 한계

원본을 1440×1000에서 실제 렌더한 `original-v536-document.png`, `original-v536-floating-pack.png`, `original-v536-documents.json`을 열어 확인했다. 문서 외곽은 canvas x/폭과 같고 y는 canvas+38이다. 원본과 엔진의 프로젝트·데모 데이터/열린 문서형은 다르므로 전체 화면 픽셀 동일성을 주장하지 않는다. 최초 oracle 탭 이름 locator 오류는 실제 `data-tab-id`로 고쳤다.

실제 Windows/Android·네이티브 snap/DPI/터치·새 OS 창·실제 계정 QA는 하지 않았다. 전체 UI는 미완료이며, 동일 객체의 새 독립 인스턴스 생성 경로·원본의 문서 내부 새 창 기본 동작/여러 실행 대상까지 이 묶음으로 완료했다고 하지 않는다. 실제 엔진의 서로 다른 프로젝트 간 live 전환은 후속 통합 검증으로 남긴다. 통제 renderer의 A/B 검사를 실제 domain 서버 A/B 검사로 계산하지 않는다. 창 닫기는 현재 입력을 보존하지만 모든 독립 View의 사용자 재진입 UI가 완성된 뜻은 아니다.

모바일 Blueprint·이미지/삭제·요소/하위 Browser·전투 로그/신문고/창별 Run와 전체 회귀/Windows 패키지/checkout/게시도 고정 잔여 목록대로 남는다. main/Android/원본 ZIP/사용자 프로젝트는 보존하며 아직 commit/push하지 않았다.


## 최종 체크포인트 (2026-10-22 23:02 UTC)

- production 스타일의 최종 document renderer8/session92784, 실제 엔진6/session86996 통과. 기존 모바일 공통 renderer7(`documents-mobile-regression.log`, `/tmp/confectory-mobile-renderer-y9ub2tq6`)과 private layout history suite(`documents-history-regression.log`) 통과. history에는 현재 floating 참조 보존과9필드 placement 기록 검사를 추가했다.
- 생성 Linux 빌드 `documents-build-5.log`/51622 exit0, 리소스60/canonical text51 해시·크기, JS/Python 구문·diff 검사 통과. 실제 엔진 문서 외곽 geometry는 원본 oracle와 x180/y102/1260×718, canvas180/64/1260×756으로 동일했다. 원본/renderer/실제 엔진의 PNG를 열어 확인했다. 실제 스크린샷 중 Pack Manager 목록이 아직 읽히는 중인 프레임도 있으며, 해당 PNG만으로 팩 기능 완료나 실제 계정 준비 성공을 주장하지 않는다.
- `work/current` HEAD `cf2fcaef2788eab256e65f171b42e0579d7b1fbd`, 기존 작업 포함 WIP209 보존. commit/push/새 Windows 패키지·checkout 미실행. 환경 정상, 모든 실행 세션 종료, 불확실한 게시 없음.
- 현재 문서 단계의 잔여는 실제 서버 live 프로젝트 A/B 및 같은 namespace/path가 다른 저장소 전환, 닫은 독립 View 사용자 재진입과 같은 객체의 추가 인스턴스/문서 내부 기본 열기 경로의 원본 대조다. 기존3개 View 계약을 무제한 인스턴스로 표시하지 않는다. 다음 묶음에서 경계를 확정·검증한 뒤 모바일 Blueprint 및 고정 잔여 목록으로 이어간다.
