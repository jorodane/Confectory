# 등록 import·scope 관측과 M12의 유한한 마감

기준은 저장소 v666 `blueprint.js:135,248,969–976`과 [M12의 네 사용자 흐름](M12_CLOSURE.md)이다. 직접 소유한 공개 함수의 정의/반환과 명시한 모든 target·caller를 갱신하면서, 기존 등록 외부 import·scope가 포함된 native 소비자를 보존한다. 외부 원본 쓰기나 새로운 provider 선택·복제·권한 부여를 추가하지 않는다.

## 구현 경계

- `BlueprintRootExecutionImports`는 기존 ProjectPack registry/직접 dependency와 선언 locator로 import 함수·scope·부모/모듈/스키마·기존 배정 헤더 및 해당 manifest를 읽는다. 함수 계약은 compiler가 사용하는 원래 선언 text이며 실행 C# 본문은 읽지 않는다. 관측 budget과 링크 거절을 유지한다.
- 외부 선언은 writable unit/group member로 만들지 않는다. 각 소유 implementation의 `rootExecutionImports` sidecar에 헤더 text·정확한 locator·원시/디코드 SHA를 보관한다. 순수 후보/복원 검증은 저장된 구조와 완전한 헤더 closure를 확인하며, Save/Review/Confirm은 현재 등록에서 경로를 다시 도출해 관측을 대조한다. 저장된 임의 경로를 읽기 권한으로 사용하지 않는다.
- `rootExecutionDependencyHash`를 private 입력과 author-attempt journal에 결합한다. 입력 후 외부 관측이 바뀌면 묵시적으로 최신 기준으로 바꾸지 않고 입력을 유지한다. 등록 외부 함수/직접 scope에 필요한 receipt 누락은 순수 Root 후보/복원 검증에서 거절한다. 새 sidecar가 없는 일반 Root ABI 그룹은 기존 검증 계약을 유지하며 이 readonly 거래에 묵시적으로 편입하지 않는다.
- 기존 override 관측의 최종 raw-read CAS 경로를 재사용한다. owned checkpoint와 Review 후보의 읽기 증거를 같은 원자적 저장에 결합하고 완료한 sidecar는 기존 그룹과 함께 퇴역한다. 후속 독립 편집을 잠그지 않는다.
- 기존 C# bytes/source identity·ordinary IInvoke·ref/out·NoBranch와 공개/override 계약, 부모/외부 원본, UI 배치와 Review→Confirm을 보존한다. 비소유 target의 자동 materialization, 구형 profile migration과 새 타입/문맥 조합을 필수 잔여로 만들지 않는다.

## 검증 절차

생성한 readonly 외부 테스트 팩의 함수·scope·포함 모듈·provider 헤더만 관측한다. 실제 C# 호출과 out 값·legacy/public 분기·다음 실행을 확인한다. Save 전 누락/경합, receipt text/path/raw SHA/필수 scope 변조, cold 복원·중복 receipt 조회, 반복 편집과 Review 후 경합을 검사한다. UI의 Undo/Redo·취소·저장 실패·응답 유실·늦은 입력과 LF/CRLF·새 패키지/전체 복원은 전용 `root-execution-import-observations` suite로 최종 동결 commit에 실행한다.

초기 API와 UI 집중 검사를 통과했으며, 최종 동결 코드의 전체 결과/패키지 출처·보관 해시·공간 수치는 완료 후 아래에 기록한다. 초기 테스트 자산의 선언/인자/BOM 오류와 제품 결과는 구별하고 실패 로그도 보존한다. 실제 Windows apphost/WebView2·모바일 실행, 전체 UI와 Space 전달의 완료를 주장하지 않는다.

M12는 위 관측 거래가 최종 검증되면 네 원래 흐름으로 마감한다. 다음은 확정된 M4의 명시 async 전환·호출/출력/완료/결과 분기 순서다. 동기 caller는 명시적으로 async로 바뀌기 전까지 오류이며 자동 blocking/호출자 전환·C# 원문 치환은 하지 않는다. 다른 고정 v666 UI·종류 C# 표현/사용 중 삭제 대응·별도 팩/권한 backend·실기기 검증은 별도다.
