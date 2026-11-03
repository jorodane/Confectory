# M12 기존 private 실행 경계 안의 공개 호출 갱신

원본 v666 `dist/blueprint.js:135`는 call의 실행 포트를 참조 정의에서 가져오며 `:248`은 분기 반환과 부모의 연속 실행을 구별한다. 기존 M11은 소유 private graph의 `executionSource`·`executionEnum`·종료점 선택을 이미 저장한다. 이번 흐름은 그 프레임의 기존 실행 분기 안에서 호출한 함수의 공개 분기를 갱신하는 것이다. 새 계약 복제·profile 자동 migration·원문 변환을 추가하지 않는다.

후보는 기존 switch-profile frame과 분기 소유 관계를 보존한다. `executionExitMode` 또는 `branchOwner`가 있다는 이유만으로 호출 전체를 일괄 거절하지 않고, 기존 전체 `Definitions`/`SwitchFlow` 검증을 후보 전후에 적용한다. private source·서명·enum·분기 소유자·종료점 coverage가 맞지 않으면 계속 거절한다. 피호출자의 공개 분기를 바깥 selector의 enum으로 대체하지 않으며 부모/참조 원본·override 계약·권한은 변경하지 않는다. 모든 실제 호출은 계속 명시 대응하고 같은 checkpoint/Review→Confirm/최종 CAS를 사용한다.

집중 fixture의 기존 private selector는 `done=17`과 out 저장소를 갖는다. 그 분기 안에서 callee를 호출한 뒤 private 반환·부모 분기·부모 다음 줄을 실행한다. callee의 성공만 기존 private 반환 카드에 연결하면 그 프레임의 다음 줄만 건너뛰며 원래 `17`·출력 `10`·부모 실행을 유지해야 한다. 실패/None의 미연결 분기는 원래 다음 줄을 계속한다. 잘못된 source/enum/서명/owner/coverage·다른 frame 경로·낡은 증거와 Save/Review 뒤 원문 경합을 거절하고, 원문 C#·형제 frame·readonly mode·재시작/응답 유실·늦은 입력·Undo/취소/저장 실패를 확인한다. 실제 UI와 독립 LF/CRLF·새 패키지/전체 복원 결과는 최종 동결 뒤 아래에 기록한다.

원본 `blueprint.js:1504–1512`의 wrapper는 원본의 핀·분기·공개 출력이 바뀌면 계약 갱신을 요구한다. 이 정상 거절을 자동 wrapper 갱신의 미구현으로 세지 않는다. `:1514–1519`의 명시적 OriginalResult 매핑은 별도 기존 wrapper 흐름의 실제 잔여이며, 기존 ordinary IInvoke/NoBranch adapter를 실제 공개 결과라고 바꾸어 해석하지 않는다. copy/자식 전체 정의 갱신과 등록 import의 실제 잔여는 [유한한 M12 표](M12_CLOSURE.md)를 따른다. M11은 구체적 회귀 없이 유지하며 M4의 명시 async caller 규칙은 별개다.

레이아웃·CSS/HTML·원본 C#·공개 IO·권한을 보존한다. 검사는 승인된 실행별 임시물 수명관리와 최신/롤백 보관을 사용하며 과거 자료를 추가 삭제하지 않는다. 교차 패키지/복원 검사는 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달 완료가 아니다.

## 최종 동결 검증 결과 — 2026-11-03

제품·검사 동결 source는 `0f0ea8ca238e89d655065749d61eb4a36bddfd2c`다. 독립 LF 19단계·CRLF 16단계·새 Windows 내용 교차 패키지/전체 복원/실패 수명관리 6단계, 총 **41단계(신규 33·동등 근거 재사용 8)**가 통과했다. 실제 private-frame 후보/API·UI normal/cancel/storage/conflict/loss/late, 기존 native UI·별도 공개 계약 caller API·ordinary 비void API 및 최종 readonly CAS를 확인했다. 아래에 신규와 재사용 근거를 구분한다. 집중 단계의 독립 생성 엔진 API 6개·UI 8개 확인은 실패 없이 통과했다. 실제 캔버스의 원래 private selector·callee 성공/실패 포트·기존 반환 카드 연결을 픽셀로 확인했다.

변경하지 않은 Core runtime 17개·소유 경계 2개씩 두 checkout의 합계 38개 검사에 해당하는 4단계는 native 최종 실행의 근거를 재사용했다. 참조 source `e64dea66427b25d4413b5a52bb393a3977fc47f6`와 현재 `src`, `tests/Confectory.Tests`, `targets/dotnet` Git 객체 및 SDK/NuGet/configuration/RID가 같다. 직접 Core 검사는 수정한 element-authoring 후보/UI를 호출하지 않는다. 모든 독립 checkout·빌드·CRLF API/UI·새 패키지/전체 복원·실패 수명관리는 신규다. LF의 잘못된 경합 파일을 고친 conflict 검사도 신규다. informational-version 바이트 동일성을 주장하지 않으며 재사용 controller·소스/입력 proof·원본 로그 SHA와 참조 증거를 함께 보존했다. 기본 저장소 harness는 모든 단계도 새로 실행한다. Core-only controller에서 이어진 일반 설명의 ‘API/UI 신규’ 문구보다 각 결과의 `reusedFrom` 및 `resumption-equivalence.json`을 최종 실행 구분의 근거로 사용한다. 원래 ZIP은 변경하지 않고 설명 보충 `/workspace/artifacts/v536-verification-managed/runs/3b368f5b59264c0089bf5213c79e4ccf.evidence-clarification.json`(SHA-256 `9162b5fd46b0cafeab046cb33bb2a507ea2728c2fa40854622e304aafb87a20a`)에 신규33/재사용8과 정확한 단계 목록을 기록했다.

최초 최종 실행의 제품 실패는 없었으나 conflict fixture가 실제 `After.node.json` 대신 다른 fixture의 `NestedAfter.node.json`을 찾아 경합 주입 전에 KeyError로 중단됐다. 해당 실패와 통과 결과를 지속 보존하고 소유 RAM root를 정리했으며 패키지는 승격하지 않았다. 테스트의 경합 경로 선택을 명시한 후 새 source로 동결했다. 이 수리 전후의 제품/도구 Git 트리는 같고, AST 대조로 UI의 `mode==conflict` 경로 선택과 fixture의 새 상수 외 모든 문장이 동일함을 확인했다. 따라서 첫 최종 실행에서 통과한 LF API·normal/cancel/storage 4단계도 재사용했다(API 6개·normal 8개·cancel 9개·storage 9개 확인). 실패한 conflict는 재사용하지 않았다. 전체 재사용은 Core 4단계와 이 4단계를 합친 8단계다. SDK/NuGet 입력, old/new 소스와 SHA·AST controller·원본 로그·참조 증거는 새 증거의 `resumption-equivalence.json`과 `equivalence-sources`에 포함한다.

- 최초 최종 실행 source: `52f52535358df9443c4f67e0140f8bd5eef796f4`, 통과 15단계·fixture 실패 1단계. 증거 `/workspace/artifacts/v536-verification-managed/runs/7187da534e9a4024afb5192c6c3f2625.zip`, SHA-256 `5a4d901806d235d21632e6021afe66606dd17484860eb7dfb7d2caaa27b770f2`.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/3b368f5b59264c0089bf5213c79e4ccf.json`
- 최종 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/3b368f5b59264c0089bf5213c79e4ccf.zip`, SHA-256 `3d0d99ce8b3c882c0fcdf8aca0cd7e981529150a3846cfc37bc776126b4d30b5`
- 집중 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/ef9d20f7594d43599a53542548dcc25d.zip`, SHA-256 `35ff7b53aacb40f9ca21ce343af77e33082befdefb4aa826044746ae63773442`
- 최신 패키지 source `0f0ea8ca238e89d655065749d61eb4a36bddfd2c`, archive/SHA `1384cd7ceb013187e572dc45de358fd227d6f51a35747ebe087bb6f33c41b2db`, 2370파일·147디렉터리, 51,345,727 bytes, manifest SHA `9fe69780b223e71d3ba5fd133b4150ba4c5fcda5930b919d3516df55081578ed`.
- 정상 롤백 source `d0b954a3146cbec25c3c0e4697ba11e30cd8563e`, archive/SHA `4f8829bd87966c167ec941103768617571e5f9da7e2750bb088bb3032e39cfd4`, manifest SHA `a51d39234bb5948e10e45d30e3d2f3834b7b43c2823e8822296584ac7361f5fd`.

새 패키지와 전체 압축 복원본에서 같은 private 경계의 저장·실행·cold와 늦은 입력을 확인했다. 전체 파일·디렉터리 mode·크기·SHA를 검증한 뒤 승인된 두 세대 저장소에 승격했다. 교차 검사 환경은 Linux dotnet/Chromium이며 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달 검증은 아니다. 독립 편집 창과 프로젝트 왕복은 이번 단위에서 새로 실행하지 않았으며 기존의 다른 흐름 증거로 완료를 대신하지 않는다.

집중 및 최종 실행이 직접 만든 임시 작업공간은 자식 종료·지속 증거 검증 뒤 정리했다. 승인된 최신/롤백 승격 외의 기존 자료는 삭제하지 않았다. 최종 전 여유 1860.43MiB, 정리/승격 후 1856.32MiB, 신규 단계 표본 최소 1860.38MiB였다. 이 표본은 보관/승격의 모든 순간을 측정한 값이 아니며 해당 구간에는 별도 지속 공간 144MiB(안전 64MiB 포함)를 확보했다. RAM 작업공간 3GiB+512MiB·추가 메모리 7GiB+1GiB 예산은 낮추지 않았다. 신규 단계 cgroup 메모리 표본 최고 4278.68MiB, 집중 기록 순증가 0.71MiB·최종 기록 순증가 4.12MiB였다. 첫 최종 실행의 기록 순증가는 2.13MiB다. 이번 단위 시작부터 최종 검증 종료까지의 실제 디스크 순증가는 7.21MiB이며 집중/실패/최종 증거와 그 시점까지의 코드/Git·보관 기록을 포함한다. 이후 보고/게시의 쓰기는 별도로 확인한다.

후속 보고 문서 커밋은 동결 제품·검사 트리를 유지한다. work/current 게시 뒤 원격 SHA·clean을 확인하며 main은 변경하지 않는다.
