# v821 연결된 일반 셀 삭제: 현행 계약 조사와 구현 보류

2026-11-20. 시작 게시본은 `105923e951f8b8ff3019124b3163c20eb117fa95`다. 이번은 삭제 기능 완료 기록이 아니다. 요청한 stale·동시 수정·파일 수명/복구 조건을 현행 API 조합으로 보장하지 못하는 사례를 실제 Linux 앱/엔진에서 재현했다. 새 삭제 UI·제품 코드·저장 형식·권한은 추가하지 않았다. 실제 프로젝트 데이터는 건드리지 않고 격리 fixture만 변경했다.

## 조사한 기존 계약

- [EditWorkspace.BlueprintNode](../packs/edit-workspace/BlueprintNode.csbody)는 실행선·entry와 값 소비가 없는 노드만 제거한다. 기존 clean C# 파일은 남기며, 이미 생성 중인 미게시 노드의 본문 초안 제거와 물리 파일 삭제는 구별한다. 제거 시 소스 소유 단위를 내리고 history recorder에 `OWNERSHIP_CHANGED`를 기록한다.
- [PackWorkspace 문서](../packs/pack-workspace/README.md)는 기존 파일 보존과 disconnected/unreferenced 조건, 물리 파일 삭제를 별도 범위로 명시한다. 이름이 비슷한 v666 PRIVATE_NODE_REMOVE 문서는 인자 삭제이며 이 셀 삭제의 구현 근거가 아니다.
- [공유 history](../packs/edit-workspace/History.csbody)는 그 소유권 경계에서 Undo/Redo를 제공하지 않는다. 이를 단순 텍스트 Undo로 우회해 파일 소유권을 되살리지 않았다.
- [기존 물리 관측 가드](../targets/element-authoring/BlueprintPropertyObservations.cs)는 알려진 owned unit의 정확한 path/kind/baseline을 요구한다. membership 제거로 사라진 소스를 현재 source 관측에 그대로 붙이거나 임의의 path에서 복원할 권한을 만드는 것은 기존 가드를 그대로 재사용하는 방법이 아니다.

## 실제 재현 결과

두 기존 code 셀 `body → after → exit:return`를 가진 직접 소유 root fixture를 사용했다. `after`는 인수·반환이 없는 일반 void 동작이며 원래 C#은 `after`를 출력한다. 기존 입력·반환·종료점과 body 원문은 유지했다.

| 검사 | 관측한 실제 결과 |
| --- | --- |
| 원래 실행 | 출력 `body → after → 10`, 종료값 10 |
| 연결된 `after`의 직접 `removeNode` | 거절, 원본·체크포인트·셀 보존 |
| 실제 UI | 문서형 연결 셀 삭제 버튼 없음. 기존 개요로 노드에 이동한 뒤 legacy Delete도 연결된 셀·입력을 보존 |
| 오래된 checkpoint | 후보 저장 전에 거절 |
| 기존 API 조합 | `body.next → exit:return`, `after.next → 빈 연결`, `removeNode after`의 3편집 raw authorBatch는 체크포인트 저장을 수용 |
| 선택 셀 revision만 stale | 정확한 `.../node:after`의 revision 0 대신 1을 sourceProof에 넣어도 위 조합이 `checkpointSaved:true`로 저장됨. 다른 project source의 관측만 변조한 사례와 별도로 재확인 |
| 저장 뒤 파일 수명 | graph에서만 after 제거. C# 원본 파일은 그대로 남고, 해당 sourceId는 현재 sources에서 빠짐 |
| 공유 Undo/Redo | `OWNERSHIP_CHANGED`, 두 방향 모두 unavailable. stale inverse 호출도 accepted/changed false |
| 저장 후 새 프로세스 | graph의 제거 상태를 cold 복원하고 물리 원본 파일은 보존. 이것은 제거된 셀의 정확한 역복구가 제공된다는 뜻이 아님 |
| Review 취소 | 원본 보존 |
| Review 뒤 남겨진 after C# 파일 변경 | 원문 JSON 끝에 공백을 추가해 물리 hash를 바꿨으나 Confirm은 통과. peer 파일의 수정 바이트 자체는 보존됨 |
| 위 진단 Confirm 뒤 실제 실행 | graph에서 after가 빠진 상태로 `body → 10`, 종료값 10. 다른 셀·계약·원문은 유지 |

따라서 기존 raw 연결/제거 조합을 새 사용자 조작으로 그대로 노출하면 요청한 정확한 source 관측 및 제거 원본의 최종 변경 거절을 만족하지 못한다. 이는 기존 API의 모든 동작이나 전체 권한 체계에 대한 일반 결론이 아니라, 이번 새 삭제 흐름에 필요한 계약과의 차이다. 물리 파일 보존과 peer 수정 바이트 보존을 stale 거절 또는 정확한 삭제/복구 완료로 표현하지 않는다.

## 이번에 게시하는 범위와 선행 작업

게시 범위는 이 조사·증거·미지원 경계 기록뿐이다. 일반 셀 삭제 버튼이나 근사 삭제 동작, 직접 graph 텍스트 수정으로 membership 가드를 우회하는 구현은 넣지 않는다. 기존 v821 자식 미리보기와 나머지 편집 기능은 그대로다.

삭제할 소스의 원래 관측을 membership 제거 뒤에도 권한 확장 없이 유지하고, Save/cold·Review/최종 CAS와 파일 보존/복구·history 경계를 함께 증명하는 선행 작업이 필요하다. 기존 receipt를 확장할 수 있는지부터 별도로 검토해야 하며, 새 저장 형식이 반드시 필요하다고 단정하지 않는다. 이번에 미결정 파일 수명 정책이나 새 저장 형식을 자동 도입하지 않았다.

분기·분기 탭·복합 전체 삭제, 마지막 필수 셀, 값 출력 소비·타 소유자·read-only·슬롯 삭제, 생성/분해 및 다른 frame의 삭제를 구현하거나 그 신규 삭제 보호가 통과했다고 주장하지 않는다. 새로운 삭제 조작이 없으므로 저장 전 개인 Undo/Redo를 구현·검증했다고도 하지 않는다. 현재 공유 경계와 cold 상태는 위 표의 실제 결과만 기록한다.

## 실행·보관과 한계

- 소스 checkout: `105923e951f8b8ff3019124b3163c20eb117fa95`
- 실제 사용한 기존 runtime source: `42d28235fa2508ae3f1c48c2b7eba4a0f14bdfad`
- 기존 패키지: 54,253,202bytes, SHA-256 `67ec94edf78087f2d073e2299410a9eee78a2336308face59947ad19758e8e7a`
- 두 소스의 src/packs/targets/examples/tools/tests가 동일함을 확인하고 온전한 기존 패키지 2,919항목을 검증·복원했다. **새 runtime 빌드나 새 패키지 승격은 없다.** 과거 23단계를 이번 신규 통과 수로 재사용하지 않는다.
- 조사 record: `/workspace/artifacts/v536-verification-managed/runs/0b9923a782be440a94659ffa31223e34.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/0b9923a782be440a94659ffa31223e34.zip`
- 증거 SHA-256: `74e506a1dfebb452091103db8d7d3c6ee59269373e818e85d096a3de21a16fd9`
- ZIP의 `audit-summary.json`, `fixtures/.../removal-contract-result.json`, `selected-stale-result.json`, 원본/체크포인트·트래픽·캡처 및 실행 로그와 probe-v1/v2/v3·선택 stale probe를 보존했다. 이 조사에서 생성한 소유 인증 임시 공간만 정리했다.

준비 clone/checkout 2단계가 통과했다. 첫 UI 진단은 화면 밖 헤더 클릭을 출력 패널이 가려 중단됐고 기존 개요 탐색으로 수정했다. 두 번째는 stale sourceProof를 거절할 것으로 기대한 assertion에서 실제 저장 수용을 발견해 중단됐으며, 이는 이번 계약 차이의 증거다. 세 번째 전체 진단과 선택 셀 자체의 별도 stale 진단은 위 관측을 기록하고 정상 종료했다. 이를 기능 구현 성공 또는 전체 보호 검사 통과로 합산하지 않는다. 제품에 진단 출력을 넣지 않았다.

실제 Linux Chromium/엔진을 사용했다. 실제 Windows/WebView2·물리 기기·전체 UI·목업 직접 시각 대조·신규 LF/CRLF 전체 빌드 및 기존 모든 편집 흐름 재검증은 미실행이다. 제품 변경이 없음을 확인했으며 이전 검증 기록과 분리한다. 과거 초기 빈 화면 원인은 이번 결과로 확정하지 않는다. main과 Sites는 변경하지 않으며 기존 원본 checkout과 latest/rollback 패키지를 보존한다.
