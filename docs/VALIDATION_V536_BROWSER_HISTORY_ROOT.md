# v536 이동 이력·Root와 삭제 전 검사

전체 v536/네이티브/게시 완료 보고가 아니다. work/current의 기존 미게시 변경을 보존했다. 실제 Linux 생성 엔진+Chromium+컴파일러와 격리 프로젝트만 사용했고 원본 레이아웃을 새로 설계하지 않았다.

## 일반 의미 편집 이력

`elements-browser-multi-history-1.log`에서 다중 이동 뒤 generic Undo가 본문만 복원하고 `hierarchyGroup`을 남기는 결함을 재현했다. 저장했던 설명 초안은 돌아왔지만 불필요한 공동 검토가 계속 요구됐다.

- Open의 기존 HistoryRecorder에 선택적인 `hierarchyVersion:1`, beforeGroup/afterGroup evidence를 추가했다. 기존 본문-only 이력은 계속 읽되 현재 활성 이동 그룹을 가진 오래된 무증거 이력은 자동 추정해 재생하지 않는다.
- MoveObjects와 EditBatch는 변경 전 본문/그룹을 기록한다. explicit Cancel은 기존 workspace lock 아래 한 번의 이력으로 기록하여 본문과 그룹 복원을 분리하지 않는다.
- History Preview/token은 현재 그룹도 비교한다. Undo/Redo는 변경 전·후 그룹을 본문과 함께 복원한다. saved History Restore는 version/필드 존재/멤버 중복/2~32 범위/소유 namespace/object kind를 검증한다. 그룹 정보는 새 접근 권한이 아니다.
- 실제 내용이나 그룹이 바뀐 이력을 무조건 최신 버전으로 맞추지 않는다. 최종 소스 파일은 이력 조작으로 쓰지 않는다.

**`elements-browser-multi-history-2.log` 전체 exit0, 실제3건**: 이전 설명 초안과 비그룹 경계까지 Undo, 동일 그룹 Redo, Save→실제 재시작→Undo 복원. case `/tmp/confectory-element-mutation-fqcfghh7`.

**`elements-browser-history-boundaries-1.log` 전체 exit0, 실제2건**: explicit Cancel을 한 이력으로 Undo/Redo, 새로운 scalar 변경 뒤 오래된 token 거절 및 새 scalar 이력 Undo 때 이동 그룹 보존. 같은 fixture를 이어 사용했으며 final source bytes는 원본 그대로다.

최종 Confirm이 이미 다른 실제 상태로 그룹을 정리한 뒤의 이동 이력 재생, 모든 과거 이력 조합까지 검증했다고 주장하지 않는다. 실제 binding 변경은 fail closed로 취급한다. 기존 일반 source 이력의 전체 통합 회귀는 마지막 전체 회귀 범위에 남긴다.

## Root 이동

원본 v536의 Project Browser Root 빈 영역을 실제 목적지로 연결했다. 현재 연결된 것은 **상속 부모를 명시적으로 null로 바꾸는 개념 이동**이다. category.Contains나 사적 폴더 배치로 재해석하지 않는다. 같은 project/window/group/namespace 목적지와 드래그 시작의 source proof를 확인하며 기존 단일/다중 CAS 경로를 사용한다. 새 영역이나 컨트롤을 추가하지 않았다.

**`elements-browser-root-move-1.log` 전체 exit0, 실제4건**, case `/tmp/confectory-element-mutation-exfh5voj`:

1. embedded Browser의 Bare를 원본 Project Browser Root로 drop→부모 제거 stage. Unit private111/다른 파일 유지.
2. 부모 해제로 inherited data 조건이 깨지는 Other는 기존 전체 그래프 검증에서 거절. folder-only 성공으로 표시하지 않음.
3. source Cancel은 원래 상속 복원. 다시 Root 이동→Save→실제 재시작에서 미확정 작업 사본/Unit111 유지.
4. Review 취소 뒤 새 Review/명시적 compiler Confirm은 Bare final source만 반영. 다른 소스와 private 입력 보존.

DataTransfer 합성 입력이다. 실제 Windows/OS drag/모바일 기기 검증이 아니다. `root-confirmed.png` 보존. 카테고리 목적지·다중 Root 전용 조합·standalone Browser의 일반 목적지 전체가 검증된 것은 아니다.

## 삭제 전 계약 — 실제 삭제는 미구현

신규 `EditWorkspace.PlanRemoval`과 일반 `planBrowserRemoval` endpoint는 명시적 소유 선언의 등록과 참조를 읽어 **private plan만** 만든다. 선택 1~32개/graph256개 제한, 중복·foreign·AISettings·미완성 생성/이동/계약 그룹은 거절한다. source text/revision/hash·정확한 manifest 등록을 관측하고, 변경된 관측을 다른 상태에 적용하지 않는다. 다른 소스가 선택 대상의 parent/target/function/scope를 참조하면 계획을 차단한다. 참조를 지우거나 자손을 Root로 옮기지 않는다.

반환값은 `declared-references-only`로 한계를 명시한다. 아직 후보 컴파일·실제 등록 해제·최종 쓰기·복구 영수증/재등록을 실행하지 않는다. 사용자 삭제 메뉴는 기존 미지원 상태로 유지하며 새 개발 패널이나 시험용 UI를 노출하지 않았다. 계정/AI 도구 권한은 추가하지 않았다.

첫 compile의 local `result` 변수 충돌은 이름을 분리해 수정했다. 그 실패 보고서로 시작한 첫 fixture는 엔진 실행 전에 종료했다. **`elements-browser-removal-plan-build-2.log` compile exit0** 이후 **`elements-browser-removal-plan-2.log` 전체 exit0, 실제4건**: 참조된 Unit 차단, Slime이 참조하는 Monster 차단, 비참조 leaf Other의 계획만 생성하면서 모든 소스·등록·선택·draft 그대로 유지, foreign/중복 선택 거절. case `/tmp/confectory-element-mutation-uw0vnq2k`.

## 남은 순서와 검증 한계

- 삭제 계획의 실제 적용·저장·취소·재시작·명시적 Review/Confirm·복구를 아직 연결하지 않았다. 원본 파일을 보관한 등록 해제와 검증된 복구 기록 방식으로 진행할 수 있으나, 완료된 기능으로 표시하지 않는다. 직접 File.Delete·빈 source·sentinel 우회는 없다.
- 카테고리 폴더 이동은 원본의 folder parent와 engine inheritance/typed Contains를 구분하는 어댑터가 미완료다. 상속을 조용히 삭제하거나 카테고리 참조를 무조건 폴더로 바꾸지 않는다.
- 이후 standalone Data/참조/context/표시 이름 표면과 정밀 화면 비교, Helper 이미지·이력·삭제, 전투로그/신문고/Yogi, 창별 Run 및 기존 모바일 Blueprint 제한을 고정 목록대로 진행한다.
- 최신 `elements-browser-root-build-1.log` compile exit0. JS/Python 구문·Review admission·projection 집중 검사·resource pins·diff 검사 수행. 전체 회귀·Windows 교차 패키지·실제 네이티브 실행·checkout·커밋/push는 미완료다.
