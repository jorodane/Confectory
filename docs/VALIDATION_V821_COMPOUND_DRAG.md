# v821 같은 부모 흐름의 복합 호출 드래그

시작 게시본은 `c898340d2ff05a07aedb057fdde6769cc24480c4`, 제품·검사 고정 소스는 `5a6d2ba90af16966f0030bb25ad4fe3349d39820`다. 기존 일반 셀 드래그와 [복합 호출의 위·아래 순서 편집](VALIDATION_V821_COMPOUND_CELLS.md)이 모두 허용하는 교집합에 데스크톱 마우스 손잡이를 연결한다.

## 구현과 지원 경계

직접 소유 물리 root의 기존 `sync-acyclic-nested-v1` 복합 사슬에서만 `kind:graph`를 일반 셀과 함께 드래그 대상으로 인정한다. `compoundCellChain`의 엔진 관측과 같은 `cellOrderPlan`/`applyCellOrder`, 전체 entry/next 계획과 개인 Undo 기록을 그대로 사용한다. 배치 선·drop 토큰·현재 화면/관측/입력 바인딩·취소 처리와 기존 버튼/키보드는 앞선 드래그 구현을 그대로 재사용한다. 제품 변경은 `feature-authoring.js`의 대상 판정과 그 canonical 리소스 해시 한 곳이다. 엔진·팩·런타임·저장 형식·권한 API는 변경하지 않았다.

허용된 복합 호출 전체가 한 노드로 순서만 바뀌고, inline 자식 graph/노드 집합/전체 경로·식별자·signature/arguments·입출력/기존 종료점과 C# leaf 원문은 그대로 남는다. 소스 수명·소유권을 새로 만들거나 자식을 분해하지 않는다. 부모의 동일 frame 안에서만 이동하며 scope·source proof·checkpoint, Review/Confirm·최종 CAS와 기존 batch history를 유지한다.

**분기 포함 복합 호출은 이번 지원 범위에 없다.** 기존 `BlueprintCellRegion.CompoundOrder`는 모든 하위 graph까지 동일한 직렬 profile/next 사슬인지 재귀 검사하고 `branchOwner`, `executionEnum`, opaque/receiver/forwarded/async 문맥을 거절한다. 자식 트리는 부모를 따라 보존되지만, 이를 분기 실행 지원으로 해석해 기존 소유/실행 계약을 넓히지 않았다. 공유 분기로 들어가는 복합 호출의 실제 UI/backend 거절과 원래 실행도 따로 검사한다. 중첩 분기 전체의 실행/이동을 새로 시험하거나 구현한 것은 아니다.

일반 드래그와 같은 locals·개인 입력·다른 frame 입력 제한을 유지한다. 자식 frame의 순서를 부모 밖으로 옮기기, 교차 frame/분기, 모바일/롱프레스, 삭제, 생성/분해, 슬롯/다른 private ABI는 제외다. 기존에 별도 지원하던 일반 child/분기 편집의 권한도 이 변경으로 늘리지 않는다.

## 고정 실행 검증

독립 LF checkout에서 고정 소스 신규 **18단계·실패 0·재사용 0**이 실제 Linux 앱/엔진에서 통과했다. 빌드와 패키지 검사도 단계 수에 포함하며 개발 결과를 더하지 않는다.

| 단계 | 실제 통과 범위 |
| --- | --- |
| 1–6 | 독립 복제·고정 checkout, .NET 복원·Release·MCP·Linux 엔진 빌드 |
| 7–9 | 복합 호출의 실제 마우스 이동·취소·입력 보존·Save/history·Confirm/CAS·실행, 값 의존성 거절, 공유 분기 문맥 거절·원래 실행 |
| 10–12 | 기존 일반 셀 드래그 전체 정상 흐름·의존성 거절, 기존 읽기 전용 C# 생성 미리보기 |
| 13–15 | Windows x64 교차 패키지·구성 검사, 패키지 managed 앱의 Linux 복합 드래그 전체 정상 흐름 |
| 16–18 | 전체 복원 후 복합 의존성 거절·입력 보존, 기존 네이티브 직접 편집·실패·CAS·실행, 패키지 실패 수명 |

- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/a31cfea10a5e4f599bc636c2f1909570.zip`
- 증거 SHA-256: `824e32e7d5e685ea73531572757b361e7c0c81683814fddb291a35602ef3c015`
- latest: source `5a6d2ba90af16966f0030bb25ad4fe3349d39820`, 54,254,899bytes, SHA-256 `1e602fd145f17fc57deb5fb14277350dc58715187b1d2b55ea4c837ddba49d6c`
- rollback: source `542b600367e368fd222212030ac25ec113eef739`, 54,256,237bytes, SHA-256 `8f0ac2bc8dc8e56f6ac5c555ac8943d4a9a8c7868657cee3f093bbcb40c1924c`

전체 복원은 파일 2,761개와 디렉터리 158개, 합계 2,919개 항목의 바이트·종류·모드를 검증했다. `full-restore.json`의 `files`는 디렉터리도 포함한다. 증거 보관 뒤 새 패키지를 승격하고 소유 인증 임시 공간만 정리했다. latest와 rollback의 실제 크기와 SHA-256을 재확인했다.

격리 프로젝트에서 실제 Chromium mouse로 `body` 복합 호출을 `other` 아래로, `other`를 `body` 위로 이동했다. 배치 표시, 개인 Undo/Redo, Escape·외부·자기 위치 drop, 기존 버튼의 Enter와 손잡이 Alt+↑를 검사했다. 보기 전환과 자식 내부 탐색·상위 복귀·cold 이후 동일한 부모 순서와 원문을 유지한다. 부모 개인 순서가 있는 동안 child 내부 손잡이/구조 조작은 비활성이다.

checkpoint 쓰기 권한 실패/재시도, 공유 Undo/Redo와 저장 후 cold, Review 취소와 원본 동시 수정 CAS 거절 뒤 fresh Confirm을 확인한다. 실제 재빌드 출력은 `other → body → inside → after → 10`, 종료값 10이다. 물리 graph의 entry/edges 외에는 모든 node/자식 graph/계약/바인딩·종료점 객체가 원래와 같다. 같은 local `inner` ID를 갖는 두 자식의 파일·인접 일반 셀·권한 모드도 보존한다. Confirm 이후 별도 이름 입력이 있으면 복합 드래그가 비활성이고, 시도 후 정확한 입력이 cold 복원된다.

생산자보다 앞서는 복합 이동은 실제 마우스 배치 표시/변경 없이 거절된다. 공유 분기 복합 호출은 기존 조건 탭을 유지하며 손잡이와 순서 편집이 비활성이다. 위조한 명시 의도·frame·owner·종료점·불완전 노드 집합·source 혼합·source proof/checkpoint와 직접 serialRoutes 요청은 기존 engine candidate 검사로 거절하며 원본·공유 checkpoint·개인 입력을 보존한다. 성공 드래그는 synthetic drag/drop을 사용하지 않는다.

일반 셀의 실제 상하/끝 이동과 취소·의존성·보기/저장·Undo/Redo·Confirm·실행·입력 cold 회귀도 신규 실행했다. 기존 생성 C# 미리보기와 복원 후 네이티브 직접 편집·컴파일 실패·late 입력·CAS·실행은 별도 회귀다. Windows x64 교차 패키지를 구성 검사하고, 패키지와 전체 복원의 managed 앱은 Linux에서 실행한다.

## 남은 한계

개발 record `0cd97e70921d43e289514fb75f6fb213`는 6개 빌드 단계와 정상/의존성/공유 UI 검사 모두 통과했다. 개발 overlay의 결과이며 위 고정 소스 신규 실행과 합산하지 않는다. 원문 fixture·로그·브라우저 상태·WIP 백업을 보관했고 증거 SHA-256은 `f1b69beb203f64b82fe0591f20518c1fa40f47d63bb289d9dd02d55607dd8381`다. 제품에 진단 추적을 넣지 않았다.

실제 Windows/WebView2·물리 기기·모바일·전체 UI·신규 CRLF·v821 목업 직접 시각 대조는 미실행이다. Linux 앱의 실제 배치 화면은 확인하며 목업과 동일하다고 주장하지 않는다. 분기 포함 복합 호출의 이동은 기존 엔진 계약부터 별도 검토해야 한다. 이전 삭제 계약 제한, 구 Reference reader 제약과 과거 초기 빈 화면 원인 미확정도 유지한다. main과 Sites는 변경하지 않는다.
