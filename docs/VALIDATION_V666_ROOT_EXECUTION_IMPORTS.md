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

초기 API와 UI 집중 검사를 통과했으며, 최종 동결 코드의 전체 결과/패키지 출처·보관 해시·공간 수치는 아래에 구분해 기록한다. 초기 테스트 자산의 선언/인자/BOM 오류와 제품 결과는 구별하고 실패 로그도 보존한다. 실제 Windows apphost/WebView2·모바일 실행, 전체 UI와 Space 전달의 완료를 주장하지 않는다.

M12는 위 관측 거래가 최종 검증되면 네 원래 흐름으로 마감한다. 다음은 확정된 M4의 명시 async 전환·호출/출력/완료/결과 분기 순서다. 동기 caller는 명시적으로 async로 바뀌기 전까지 오류이며 자동 blocking/호출자 전환·C# 원문 치환은 하지 않는다. 다른 고정 v666 UI·종류 C# 표현/사용 중 삭제 대응·별도 팩/권한 backend·실기기 검증은 별도다.

## 최종 동결 결과

동결 구현 `a6dd2876100f08197f9d34feb304a7e2ac1e6528`에 독립 LF/CRLF checkout과 새 Windows 교차 패키지/전체 압축 복원 검증 **44단계(신규 32·동등 근거 재사용 12)**를 실행했다. LF 20·CRLF 18와 패키지/복원/실패 수명관리 6단계를 구별한다. 동등 근거 12단계는 변경되지 않은 Core 직접 실행/소유권 4단계, Node 전용 UI 원문/문법 6단계, 실제 관측 helper를 호출하지 않는 격리 source-lease probe 2단계다. 각 입력 소스·SDK/의존성·인자와 참조 archive SHA를 대조했다. 관측 helper/API가 바뀌었으므로 해당 API/UI는 모두 다시 실행했고 독립 빌드·CRLF lease·패키지/복원도 신규다. informational-version을 포함한 바이너리 동일성은 주장하지 않는다. 초기 집중 검사나 진단 실패를 최종 통과 수에 넣지 않는다.

독립 CAS probe의 기존 비JSON 초안 때문에 중단된 첫 최종 실행은 `5921b9a58b7b4bf79e4df5786f644f4c.zip`/SHA `e418a66ca72b5ea24e18283a67685e452d9775bb9c5f97a626ebcdf869c4c061`에 보존했다. 제품 Confirm/CommitPlan은 변경하지 않았으며 `9e845be`는 그 probe의 입력 수정만 포함한다.

별도 재현에서 새 helper가 receipt 없는 일반 Root 헤더 초안을 거절한 결함을 확인해 `a6dd287`에서 적용 범위를 sidecar 보유 거래로 좁혔다. 관련 기존 검증을 약화하지 않고 새 API 회귀로 그 경계를 확인했다. 수정 전 실행은 `37015f8679d44580ba2841729446e171.zip`/SHA `20bb29c0e20cb7abd8b6f6b07b67b76bb648703d00e27409f4b085c21bf69c2a`에 완료 단계·중단 이유·증거를 보존했다. 관측은 헤더 64개·원시 관측 128개·파일당 1MiB/합계 2MiB·snapshot JSON 4MiB 안에서 수행하며 초과를 묵시적으로 잘라 저장하지 않는다. 이 구현 예산을 새로운 영구 UX 정책으로 확정하지 않는다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/bc23390f68094484aabb35a5b9ebec3d.json`
- 최종 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/bc23390f68094484aabb35a5b9ebec3d.zip` / SHA-256 `a0365715d839402d68b34a42b1377964db70b5d4dc37cf8c69ffa8fff1098cd7`
- 초기 집중 증거 ZIP: `3ba151b214b74d33bf3991f6d7ca7304.zip` / SHA-256 `10998cfc0b04b01514f0a45df32871f43149c5cd8e10de625896de760c6aeded`. 초기 API5/UI8 통과와 fixture 선언/인자/BOM 진단 실패를 보존하며 최종 코드 검증과 분리한다.
- 최신 패키지 출처: `a6dd2876100f08197f9d34feb304a7e2ac1e6528`, archive `f4b8ec56e3b19d643e4202083ea47894d75c02a085442da5939acd25ad0e97c7.zip`, SHA-256 `f4b8ec56e3b19d643e4202083ea47894d75c02a085442da5939acd25ad0e97c7`, 전체 manifest SHA-256 `916463f323425ca44a255846ab21c7a4361d4ca67e1585bb73a257dad3f22a3c`.
- 롤백 패키지 출처: `448f1605d48ccf1773527ffdbee6bdb2eaeb757a`, archive `b8eb752e9351ea14c3db22ba1f9ae8010cde885b1860d1c1e6da4a0d25286ac1.zip`, SHA-256 `b8eb752e9351ea14c3db22ba1f9ae8010cde885b1860d1c1e6da4a0d25286ac1`, 전체 manifest SHA-256 `ef604b1ef1f8aa43241333f0ea0f6f58deaf480b22196707d0a24043f4952632`.

패키지 전체 파일 SHA/모드·압축 무결성과 RAM 전체 복원을 확인하고, 생성본에서는 정상 UI 저장/Confirm을, 복원본에서는 늦은 응답·실패 수명관리를 확인했다. 최신/롤백과 증거는 지속 보관하고 자식 프로세스 종료 확인 후 이번 실행의 소유 RAM 임시물만 정리했다. 기존 승인된 최신/롤백 두 세대 교체 외의 과거 보관 자료는 추가 정리하지 않았다. 미확정 신규 외부 관측 초안의 구버전 에디터 호환성을 보장하지 않으며 최신 검증본과 원래 초안을 보존한다.

실측 디스크 여유는 시작 1839.56MiB에서 종료 1829.76MiB로, 순증가 9.80MiB다(초기/실패/중단 증거 포함). 마지막 최종 검증 실행만 기준으로는 4.19MiB 증가했다. 추가 144MiB(안전 64MiB 포함) 예산을 낮추지 않았다. 실행 단계 sampler의 최대 메모리는 4094.79MiB다. 메모리는 단계별 sampler 값이며 개별 프로세스 peak의 합계가 아니다.

이 네 원래 흐름의 마감으로 **M12를 완료**한다. M11은 구체적 회귀가 없어 닫혀 있다. 다음은 확정된 M4 async와 기존 고정 v666 UI/별도 팩 및 종류 표현/사용 중 삭제 대응이며, 실제 Windows·모바일/전체 UI·Space 전달은 별도 미완료다. 후속 기록 commit이 문서만 바꾸면 동결 구현과 `src/targets/packs/examples/tests/tools` tree 동일성을 확인해 패키지 출처를 명시한다.
