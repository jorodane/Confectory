# v536 표시 이름 저장·취소·재시작 — 검증 체크포인트

표시 이름의 임시 저장·취소·재시작·명시적 최종 확정 묶음을 검증했다. 전체 Browser/UI 복원 완료 보고가 아니다. work/current HEAD `cf2fcae`와 기존 WIP를 보존했고 게시·Windows 패키징은 하지 않았다. 실제 Linux 생성 엔진+Chromium, 격리 fixture만 사용했다. 사용자 계정·자격 증명·유료 추론·실제 사용자 자료 삭제는 없다.

## 확인한 결함과 수정

1. 상세 View에서 이름 변경을 임시 저장한 뒤, 다른 부모 Browser의 이름 복원 영수증은 source version이 그대로여서 갱신되지 않았다. Save 성공을 관련 Browser에 전달하고 기존 `checkpointSaved`/정확한 현재 값으로 닫힌 영수증만 정리한다. 편집 중 새 입력·다른 창 입력은 정리하지 않는다.
2. 저장본에 한글 이름이 있어도 재시작 때 UI에 기본 이름이 표시됐다. 디스크의 draft.json과 상세 View에는 올바른 editorName이 있었고, 관계 조회 직후 schema 조회가 public relationsMap을 없애기 전에 UI cache가 관측하지 못했다. 서버 상태에 relationsMap이 들어온 즉시 기존 projection에 관측시킨다. 저장값을 바꾸지 않는다.
3. 복원된 미저장 이름 입력창은 focus를 받았다가 bootstrap/re-render로 blur될 때 자동으로 이전 이름을 재적용할 수 있었다. 실제 cold 요청 기록에서 명시적 사용자 입력 전에 editDeclaration이 발생하고, 디스크 checkpoint A2와 메모리의 B가 달라진 것을 확인했다. recovered 입력의 blur는 그 DOM에서 사용자가 직접 편집한 경우만 적용하고, 그 외 재적용은 Enter가 필요하다. Escape는 복원 의도를 명시적으로 취소하며 source rollback write를 만들지 않는다.
4. 주 편집기에서 원래 이름을 취소할 때, 정확히 일치하는 닫힌 영수증만 capture해 실제 source discard 성공 뒤 정리한다. scope·record identity·snapshot string·source revision/hash가 다르면 삭제하지 않는다. 그래서 취소한 B가 재시작 때 다시 제안되지 않는다.
5. 마지막 실제 확정 진입의 `스키마 열기`가 background 조회와 transport admission 경합을 일으켰다. 첫 수정에서 openEditorView/closeEditorView 전용 helper를 select에 사용해 허용 목록에 걸렸고, 이 오류를 인정하고 바로잡았다. 최종 코드는 기존 읽기/사적 cursor 재조회에 select를 명시적으로 포함해 `stale_revision`일 때만 최대3회 재시도한다. editDeclaration/Save/Confirm의 재시도 범위를 넓히지 않는다. 같은 project와 선택 id를 매번 확인하고 표시한 schema 창을 foreground로 올린다. 이 경로는 최종 실제 렌더러 검사에서 통과했다.

## 실제 통과 범위

- `elements-browser-name-confirm-2.log`: 첫 **1 PASS**. 상세 Save가 한글 이름을 checkpoint하고 부모 private111 및 모든 final source 바이트가 보존됨. 뒤의 영수증 정리 실패를 재현했다.
- `elements-browser-name-confirm-4.log`: 첫 **1 PASS**. Save notification 후 원래 부모 Browser의 일치하는 영수증만 정리되는 것을 확인했다. 이후 UI fixture가 live nth View를 닫으면서 다음 nth를 잃어 중단했다. 기존 창을 닫지 않고 주 Browser를 focus하도록 fixture를 고쳤다.
- `elements-browser-name-confirm-7.log`: **첫 3 PASS**. (a) cold 미저장 B 원문이 자동 write 없이 복원되고 Esc로 거절하면 savedA2 표시, (b) 실제 source discard 요청이 정확한 id/revision/hash/checkpoint/owner proof로 실행되어 savedA2와 부모111/자손/다른 source 보존, 취소 영수증만 제거, (c) 실제 재시작 후 취소 이름이 재생되지 않고 savedA2가 복원됨. 이어 최종 Review 진입 전 schema/cursor 조회에서 중단했다. 전체 스크립트 통과라고 하지 않는다.
- `cancel-observation.json`에 source discard의 실제 status→discard 요청, 오류 없음과 당시 상태를 보존했다. 값은 격리 fixture source 정보다.
- 기존 `browser_projection.mjs` 2개 묶음 통과: 선언 ID/parent/schema edge, project 분리, cycle/depth/ancestor 경계와 observation cache 유지.
- 최신 `elements-browser-name-recovery-build-3.log` Linux compile exit0. 이 빌드는 마지막 schema/select helper 수정까지 포함한다. JS/Python 구문, resource62/text53 hash·size 및 diff check 확인.

중간에 기존 `정의 열기`가 이미 열린 독립 View를 재사용하는 것을 primary 전환으로 잘못 가정한 fixture가 있었다. 실제 제공되는 context 메뉴 `스키마 열기`로 primary 경로를 명확히 했다. 강제 클릭이나 source/동의 guard 삭제로 통과시키지 않았다.

## 2026-10-23 실제 최종 확정 결과

- `elements-browser-name-confirm-9.log`: schema 열기는 통과했으나 background browserDrafts status와 Review admission이 경합하여 `stale_revision`으로 Review가 실행 전에 거절됐다. Confirm은 실행되지 않았다.
- `reviewSelected`의 단일 소스 Review에만 최대3회 알려진 미실행 admission 재시도를 추가했다. 최초 project/선택 source id/revision/본문/검증 target을 바인딩하고 달라지면 중단한다. Browser raw 입력을 매번 재검사한다. 기존 Review 동의/Confirm을 재사용하거나 최종 쓰기를 자동 재시도하지 않는다.
- `review_admission.mjs`: 실제 함수 추출 검사 6경로 통과. 미실행 stale 한 번은 재시도하고 source revision/본문/선택/project/target 변화는 두 번째 Review 전 차단한다. 실제 서버 검사와 구분되는 통제 테스트다.
- `elements-browser-name-confirm-10.log`: 초기 presentation 복원이 끝나기 전 query를 조작한 fixture 실패. 화면 준비 조건을 추가했다.
- **`elements-browser-name-confirm-11.log` 전체 exit0, 실제 UI 2 PASS**: reviewDraft 첫 요청의 transport revision을 의도적으로 오래되게 보내 실제 서버 미실행 거절→안전한 재시도, Monster만 검토→검토 취소, 새 Review→명시적 compiler Confirm. 최종 Monster editorName을 JSON Unicode escape로 해석해 `몬스터 A2`임을 확인했다. 안정 ID·Slime 부모 참조·Other·Unit final 바이트와 Unit private111 보존을 확인했다. 외부 요청/JS 오류 없음.
- 실제 캡처 `/tmp/confectory-element-mutation-uj3cgnj5/name-explicitly-confirmed.png`를 열어 확인했다. 한 화면의 구조 확인이며 전체 v536 정밀 픽셀 비교 완료 근거는 아니다.
- 빌드 `elements-browser-name-review-build.log` Linux compile exit0. 이후 부모 드롭을 위한 별도 빌드/테스트는 다음 묶음에 기록한다.

## 현재 상태와 남은 검사

격리 case `/tmp/confectory-element-mutation-uj3cgnj5`: final Monster 표시 이름은 실제 Confirm으로 `몬스터 A2`가 됐다. 이 fixture를 재초기화하거나 이미 확인된 Confirm을 다시 실행하지 않는다. 부모 Unit private111, Monster/Other View와 Unit→Monster→Slime 참조를 보존했다. 이름 검사 런타임과 테스트는 종료했다.

삭제·복구는 아직 미구현이다. Browser 내부 부모 이동은 별도 첫 연결 묶음으로 구현·검증 중이며 이 문서의 이름 완료 결과에 포함하지 않는다. 삭제는 기존 write-only Changes/Restore/Confirm/Commit에 versioned 제거·복구와 registration group을 표현해야 하며, 직접 File.Delete·빈 문자열·sentinel로 우회하지 않는다. 참조·자손을 자동으로 Root로 이동시키거나 다른 객체를 편집하지 않는다. 부모 이동은 기존 private parent 입력과 EditObjectStructure/CAS를 재사용할 수 있으나, 사적 preview와 실제 backend 상태를 구분하고 재시작·취소·소유권·순환/타입·여러 입력 보존을 검증해야 한다. 아직 이는 구현 계획이다.

전체 원본 비교/나머지 Browser 동작, 모바일 Blueprint 제한, 이미지/삭제, 전투·신문고/Yogi, 창별 Run, 전체 회귀·Windows·checkout·게시가 미완료다. Helper 편집 기능 확장은 UI 완료 뒤 순서를 유지한다.
