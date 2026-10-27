# 저장 copy의 분리 private frame 핀·본문 결합 수용

원래 v536 7행의 기존 내부 구현 편집을 잇는 최소 단위다. 같은 정보 창·owner·저장된 단독 소유 single-target same-contract copy에서 원래 내부 편집/빵부스러기로 `left`, `right/deep` frame을 오가며 동명 ordinary `code next` leaf의 핀 이름/정의·값과 직접 작성 C# 본문을 편집하고 Save한다. 새 copy의 owner 결합 저장은 이미 qualified 편집을 모았지만, 저장 copy는 sibling frame 입력 차단으로 서버 요청 전에 멈췄다.

## 저장 및 보호

렌더링/선택/Undo는 frame별로 유지한다. Save만 같은 author surface의 명시 입력을 모으고 각 편집에 정확한 frame ID를 붙인다. 다른 창·owner·target·루트 입력을 자동 채택하지 않는다. 기본 saved private copy에서 읽기 전용 소유권 증거의 무관한 peer 입력을 쓰기 충돌로 오인하던 범위도 기존 독립 창과 맞췄다. 전체 server source 증거·실제 source/CAS 보호와 동일 원본의 다른 편집 차단은 유지한다. 기존 단일 frame 요청과 저장 기록도 유지한다. 새 레이아웃/메뉴/핀 ID 체계·자동 C# 재작성은 없다.

기존 authorBatch의 한 격리 후보에서 원래 checkpoint·전체 source closure·소유 receipt와 각 frame의 실제 ordinary leaf를 먼저 확인한다. 모든 핀 대응/값/사용자 본문을 적용한 뒤 각 frame과 결합 그래프를 검증하고 기존 WriteChecked CAS 한 번으로 저장한다. 마지막 frame 오류와 쓰기 실패는 앞선 frame도 전부 미적용이다. 재시도는 이전 요청이 미적용이며 원래 checkpoint·source가 불변임을 조회한 경우에만 허용하고 실패 기록을 보존한다. 응답 유실은 receipt 조회로 중복 적용을 막는다. 성공 시 저장된 frame의 Undo 경계를 함께 정리한다.

Save는 초안 보관이고 컴파일 및 물리 원본 반영은 기존 명시 Review/Confirm이다. 공개 override의 매개변수/출력·private graph root signature·부모/외부 원본·출처·다른 target·helpers·정확한 64비트 local·설명·권한을 바꾸지 않는다. 호환 불가 연결을 폐기하거나 값을 추측하지 않는다.

## 실제 검사

기본/독립 창·마지막 미연결 핀 거절과 명시 보완·실제 checkpoint 쓰기 실패·저장/조회 응답 유실·실제 peer 저장 충돌·다른 창 입력·프로젝트 전환을 actual engine/renderer fixture로 검사했다. 각 흐름에 frame별 Undo/Redo·C# 편집 취소·cold 복원·원본 보존을 포함하고 정상 저장 흐름은 Review 거절/재검토/명시 Confirm까지 확인했다. 다른 창 미적용 입력이 남으면 기존 전역 검토 보호를 유지하며, fixture에서 그 입력을 명시 취소한 뒤 Confirm한다. 기존850×600 창·360px 카드 및 변경 없는 CSS/HTML을 유지한다. 정밀 pixel 전수 대조나 실제 기기 검증은 아니다.

| 검사 | 실제 확인 수 |
|---|---:|
| normal | 5 |
| view | 5 |
| invalid | 7 |
| storage | 7 |
| loss | 7 |
| conflict | 4 |
| context | 7 |
| projects | 7 |

영향 회귀는 기존 단일 private 핀 계획/본문 경로, 저장 copy ABI, 생산 Review/Confirm/CommitPlan의 최종 read CAS 성공·late conflict·누락 proof·path escape다. 정확한 명령/종료 코드/소스 SHA는 `evidence/v536-saved-copy-frames/focused-verification.json`에 기록한다. 실패 로그·fixture·화면 증거는 scratch에 보관하며 사용자 자료를 검사에 사용하지 않는다.

## 남은 경계

이번 완료는 현재 편집 중인 private frame의 Save에서 저장된 ordinary leaf 핀·수동 본문을 여러 frame에 걸쳐 결합하는 경로다. Root로 돌아온 뒤 Save하는 진입은 아직 원래 입력 guard에 막히며 이 단위의 완료로 세지 않는다. 원본 callee ABI 갱신으로 영향받는 forwarded frame 계약·wrapper와 다른 frame의 일반 입력을 결합하는 경로, opaque/whole-body source closure는 이 단위에서 지원하지 않는다. 공개 override 구조 변경은 정상 금지이고 독립 계약 복제는 요구에서 제외한다. 가능한 변환/target 조합을 새 필수 요구로 늘리지 않는다.

고정8행의 여러 함수 C#/중첩/copy 문맥, 9행 고급 정보/참조/기능 핀 타입 및 표시명/생성 식별자, I6 기호·이모지·사용자 로컬 이미지 아이콘, B2 실제 배정 배지, M4 async/M11 C# 동작→graph/M12 root 실행 분기는 별도 잔여다. 이미지·협의·렌더 신규 backend는 이 복원 범위 밖이다. 전체 UI·실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달은 미완료다.

## 독립 checkout·새 교차 패키지 확정 결과

실행 소스 커밋 `335c80d041b2562b7437b01c562608f5fa30a515`의 변경 Git blob·기존 autocrlf·clean을 확인했다. 기존 독립 checkout에서 Native/CLI Release·새 Linux 엔진, 두 private frame의 독립 정보 창 6확인 및 생산 final CAS 4확인이 통과했다. 새 RAM Windows x64 교차 패키지는 restore·Release·MCP·생성·probe·패키지 자체 두 frame UI 6확인까지 6단계를 통과했다. 전체 2349개/manifest 2348개 목록·SHA·Core/Native DLL과 변경 제품 소스 바이트를 확인했다.

manifest SHA `0de3f84f50b027febeb609b1f40f09e31b824e3091d11dc0f11e79196693b6c6`. 전체 manifest와 fixture/로그/프로필 증거 보관 뒤 이번 실행의 임시 패키지만 정리했고 기존 보관 패키지/SDK/원본/사용자 자료는 삭제하지 않았다. 최종 후속 커밋은 문서/evidence만 달라 실행 코드는 위 소스 커밋과 같다. 실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달 및 전체 UI는 계속 미완료다.

## 후속 Root 진입

이 문서의 당시 Root guard 잔여는 [Root 복귀 Save 수용](VALIDATION_V536_ROOT_COPY_SAVE.md)에서 ordinary private 핀·값·수동 본문에 한해 마감했다. 당시 검증 결과와 실행 소스 커밋은 그대로 유지한다. forwarded/wrapper·다른 frame 영향 후보 및 opaque/whole-body closure와 별도8/9행·UI·실제 기기/Library는 해당 후속 기록의 잔여 판정을 따른다.
