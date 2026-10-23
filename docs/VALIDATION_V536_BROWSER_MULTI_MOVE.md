# v536 Browser 다중 개념 이동 — 검증 묶음

원본 v536의 다중 선택 드롭을 기존 상속 계약과 실제 저장/검토 경로에 연결했다. work/current 미게시 WIP이며 전체 Browser/UI 복원·Windows 검증·배포 완료가 아니다. 사용자 프로젝트 대신 `/tmp` fixture만 사용했다.

## 구현

- `EditWorkspace.MoveObjects`는 2~32개 소유 object의 명시적 id/parent/revision/hash를 받는다. 기존 선언 변환기로 후보 본문들을 만든 뒤 전체 소유 그래프를 검증하고, 관측한 소스/의존 상태가 모두 일치할 때 한 lock에서 전부 반영한다. 두 번째 항목이 실패해도 첫 번째 변경을 남기지 않는다. 새로운 파일 쓰기나 Confirm은 수행하지 않는다.
- 이동의 `hierarchyGroup`은 기존 source group과 구분한다. Save export/cold Restore, Browser 변경 상태와 전체 취소, Review 선택 및 Confirm acknowledgement에 연결했다. 일부만 취소·검토하는 서버 요청은 거절한다. 기존의 root/C# 계약 그룹 검증은 그대로 유지한다.
- 원본 다중 선택에서 상위와 자손이 함께 선택되면 상위 항목만 직접 이동하고 자손의 원래 상속 소스는 변경하지 않는다. 같은 프로젝트 소유 개념과 기존 입력을 검사하며, 다른 프로젝트/미지원 카테고리·Root 폴더를 이동 대상으로 사용하지 않는다.
- 이동 그룹의 검토는 같은 기존 모달/Review 화면에서 이루어진다. 새로운 레이아웃이나 권한 승낙을 추가하지 않았다. 해당 그룹과 무관한 다른 객체 private 입력은 보존하고 검토 범위에 넣지 않는다.
- 취소는 본문뿐 아니라 checkpoint의 이동 그룹 정보도 같은 잠금 아래 복원한다. Save checkpoint가 바뀌면 중단한다. 전체 취소 뒤 이전 초안에 불필요한 이동 그룹이 남는 결함을 실제로 재현하고 수정했다.

## 실제 엔진 결과

1. `elements-browser-multi-build-1.log`는 생성 body의 LINQ 확장 import 누락 등으로 실패했다. fully qualified LINQ로 수정했으며 build2 이후 컴파일 통과. UI 배선까지 포함한 최종 빌드는 `elements-browser-multi-build-7.log` exit0이다.
2. `elements-browser-multi-parent-1.log`는 새 endpoint의 WebBundle 등록 누락으로 요청 접수 전에 중단됐다. 등록 및 EditorHomeModel의 plan 전달/connection settings 차단을 연결했다. 테스트 전용 우회 endpoint가 아니며 일반 편집 endpoint의 소유권/CAS 검사를 따른다. AI 도구 권한을 추가하지 않았다.
3. **`elements-browser-multi-parent-2.log` 첫5건 통과**: 두 번째 stale source로 전체 원자 거절, 실제 다중 드롭, 부분 Review/Cancel 거절, 전체 취소 및 clean group 정리, Save→실제 재시작 후 두 source/group 복원. 이후 다른 객체 Unit의 private111까지 막는 기존 UI 입력 검토 조건에서 중단됐다. 이 실패를 전체 스크립트 통과로 기록하지 않는다.
4. 이동 그룹의 private 입력 검사만 소유 source 범위로 좁히고, 기존 새 선언/등록 검토의 조건은 유지했다. **`elements-browser-multi-publish-1.log` 전체 exit0, 실제1건**: 같은 저장 fixture에서 검토 취소→새 검토→명시적 compiler Confirm. Monster/Other 부모를 Third로 함께 반영하고 Slime 참조·Third/Unit source·Unit private111·다른 final 바이트 보존. case `/tmp/confectory-element-mutation-96j5nu16`는 이미 확정됐으므로 초기화하거나 재확정하지 않는다. saved draft.json은 changes0/group0임을 추가로 읽기 확인했다. `multi-parent-confirmed.png`를 실제 열어 확인했다.
5. `elements-browser-multi-checkpoint-1.log`: 기존 저장 설명이 있는 Monster를 다중 이동하고 취소하면 본문은 돌아오지만 hierarchyGroup이 잔류하는 결함을 재현했다. `BrowserDrafts`가 checkpoint의 그룹 정보를 본문과 함께 복원하도록 수정했다.
6. **`elements-browser-multi-checkpoint-2.log` 실제2건 exit0**: 이전 설명 초안과 ungrouped Review 경계 복원, actual cold에서도 이전 초안/원본 바이트 유지. case `/tmp/confectory-element-mutation-5v0_vpaj`.

**`elements-browser-multi-checkpoint-3.log` 전체 exit0, 실제4건**: 순환 다중 그래프 전체 거절, 이동 취소 시 이전 본문/비그룹 검토 경계 복원, actual cold 유지, 이미 Save한 이동 그룹의 후속 설명 편집을 취소하면 저장된 본문과 그룹은 그대로 유지. case `/tmp/confectory-element-mutation-une3_0sx`. 마지막 코드 변경 뒤의 focused 검사이며 기존5건/최종Confirm을 다시 실행하지 않았다.

외부 요청·실제 계정·OAuth·토큰/자격 증명 접근·유료 추론은 없다. Chromium DataTransfer 합성 입력과 실제 Linux 생성 엔진/컴파일러를 사용했다. 실제 Windows/Android/OS 마우스 드래그·터치 검증은 아니다. Review admission/projection 집중 검사와 JS/Python 구문·resource pins·diff 검사를 별도로 수행했다.

## 고정 잔여와 다음 순서

- **후속 Undo/Redo 수정·실제5건 검증 완료** — VALIDATION_V536_BROWSER_HISTORY_ROOT.md 참조. 이 아래는 당시 체크포인트의 잔여 기록이다. 이번에 완주한 취소는 명시적 source Cancel이다. HistoryRecorder는 본문 위주이므로 이동 그룹 metadata와의 정합성을 게시 전 확인해야 한다. 새로운 내구성 범위가 아니라 새 그룹 편집의 기존 이력 경계다.
- **삭제·복구 미구현**. 기존 선언별 source file 직접 삭제/빈 source/sentinel 처리는 도입하지 않았다. 실제 `unregisterDeclarations`는 정확한 소유 manifest 항목 제거를 지원한다. 따라서 물리 파일 파괴를 먼저 추가하기보다 등록 해제와 검증된 복구 영수증으로 구성하는 경로도 조사할 수 있다. 이 경우 UI상 삭제와 디스크 원본 보존을 명확히 구별하고, 참조/자손이 남으면 후보 컴파일/검증이 거절해야 한다. 아직 이 방식을 구현했다고 주장하지 않는다.
- **카테고리/Root 폴더 이동·standalone Browser 이동 미구현**. 원본은 폴더 parent와 개념 inherits를 별도로 갖고 실제 엔진의 object.parent는 상속이다. 기존 category.Contains의 의미를 단순 폴더로 재해석하거나 상속을 조용히 지우지 않았다. containment와 inheritance를 나누는 어댑터를 먼저 완성할 필요가 있다.
- 이 변이 범위 후 standalone Data·참조/표시 이름 표면 및 정밀 화면 비교, Helper 이미지/이력/삭제, 전투로그/신문고/Yogi, 창별 Run 순서. 모바일 Blueprint 제한과 나머지 고정 목록은 V536_UI_RESTORATION_SCOPE.md에 유지한다.
- 전체 회귀·Windows 교차 패키지·checkout·work/current 정상 commit/push는 전체 UI 수용 뒤 진행한다. 실제 Windows 실행 검증과 교차 빌드는 구분한다.
