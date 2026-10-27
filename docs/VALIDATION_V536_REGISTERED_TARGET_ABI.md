# v536 등록 callee와 여러 Blueprint target의 원자 갱신

기준 게시 `605bcb25c0601c8beceba6935ff7e8bd3b19ad5e`, 저장소 원본 v536 및 기존 고정 7행·A4–A6의 target별 원본 계약 갱신을 대조했다. 이번 최소 단위는 **직접 소유한 일반 구현의 기존 여러 Blueprint target에서 하나의 direct-dependency 등록 callee를 각각 한 번 사용하는 경우**다. 저장 copy의 단일 target 완료 경로는 재구현하지 않는다.

## 연결과 보호

기존 all-target 명시 대응 UI와 `BlueprintCallAbiGroup` 후보를 재사용한다. 현재 target 목록·각 graph/record·선택된 call·wrapper·소비자 및 공유 typed import를 한 후보에서 검증하고 기존 authorBatch/checkpoint CAS로 저장한다. 마지막 target의 부적합한 출력도 앞선 target이나 import를 부분 적용하지 않는다. 입력과 출력의 의미를 추측하거나 사용자 C# 원문을 자동 재작성하지 않는다.

등록 함수 선언은 기존 `blueprintCallableContracts`의 직접 dependency/registry 읽기를 사용한다. provider 선택/본문 읽기는 하지 않는다. 외부 선언 ID를 owned unit이나 source 쓰기 목록에 넣지 않고, 소유 caller의 `rootAbiContracts`에 정확한 선언 원문·callee ID·owner/등록 manifest와 source의 SHA-256 receipt를 보관한다. 소유 project manifest는 관측·그룹 CAS에 포함한다. binding은 이 snapshot도 식별한다. 이 단위의 fixture에서 최종 변경 파일은 Caller 선언과 두 target graph뿐이다.

저장 직전 모든 관측 소스의 revision/hash 및 물리 baseline을 확인하고 현재 등록 receipt를 재조회한다. checkpoint 복원은 보관 snapshot의 ID·선언·typed import·manifest·소유 group만 검증하며 변경된 외부 파일로 snapshot을 덮거나 복원을 버리지 않는다. Review와 실제 Confirm이 공유하는 검증 경계에서 현재 프로젝트 경로를 사용해 등록 receipt를 다시 조회한다. 변경하지 않는 소유 manifest/본문 기록도 현재 물리 baseline을 검사하고, 마지막 파일 CommitPlan의 읽기 검사에 넣어 변경 파일과 하나의 CAS로 처리한다. 저장된 filesystem 요청 경로를 신뢰하여 다른 프로젝트에 연결하지 않는다. 외부 manifest 원문만 바뀌어도 재검토 없이 확정하지 않는다.

일반 multi-target owned callee, 저장 copy의 등록 단일 target, 기존 legacy 3/4-unit group 규칙을 보존한다. 공개 override는 원래 매개변수·출력 계약을 유지하고 구현만 변경한다. 별도 독립 계약 ID/기능을 생성하거나 부모/외부 원본을 변경하지 않는다. 모든 UI 리소스와 bundle 바이트는 기준 게시와 같다.

## 유한한 수용 범위

격리 `Owned.Multi`의 common/windows graph와 외부 `Lib::Native`를 사용한다. 기존 ref 입력/반환을 현재 step·renamed 입력 및 total 출력에 target별로 명시 대응한다. 두 원래 code 본문/graph 식별자·연결·공개 root 계약을 보존한다. 별도 정보 소유 어댑터나 새로운 UI를 만들지 않고, 기본 Blueprint와 다른 독립 raw 문서의 미저장 원문이 재시작/확정에도 유지되는지 확인한다.

검사 목록은 정상 저장/cold/Review 취소/compiler Confirm, 불완전 입력/미저장 갱신 계획 Undo, 마지막 target 비호환 대응, 실제 source/CP 경합, 쓰기 실패·재시도, 응답 유실 조회, 거절 후 미저장 계획 Undo/새 대응, 외부 manifest 변경 시 Save/Review/Confirm 차단이다. 순수 후보/복원 group 검사는 소유 경계·완전한 target/record·snapshot 누락/위조/잘못된 manifest/import를 검사한다. 통과 수와 명령/해시는 확정 후 evidence에 기록한다.

## 종료 경계와 다음 잔여

- 이번 단위는 등록 receipt가 있는 일반 직접 소유 all-Blueprint 구현의 기존 target별 후보 연결이다. 기존 기반의 2–8 target 한계를 유지하며 실제 화면 표본은 common/windows 두 target이다. 여러 call 사용처/모든 타입 조합의 전수 검증을 주장하지 않는다.
- same-contract copy의 다중 target 및 provenance/owner 그룹 결합, 새 immutable copy의 등록 복수 use, 별도 frame 계약/본문·opaque/whole-body closure는 기존 7/8행·A4–A6의 같은 잔여로 유지한다. copy의 모든 target을 자동 선택/복제하는 정책은 만들지 않는다.
- 고정 8행의 이 단위 밖 공유 caller 결합, 9행 고급 타입/표시명, I6 아이콘/B2 실제 배지와 M4/M11/M12는 별도 미완료다. 정상적인 override 계약 위반 차단을 미구현으로 세지 않는다.
- 전체 UI, 실제 Windows apphost/WebView2 실행, 실제 모바일 기기/터치 및 Library 전달은 미완료다. RAM Windows 교차 패키지는 별도 검사이며 전달용 보관 파일이 아니다. 이미지·협의·렌더 신규 backend는 이번 범위에 없다.

시작 디스크 여유 약782MiB, 순차 디스크200MiB/RAM768MiB 예산을 확인했다. 새 clone/환경 교체나 기존 자료 정리는 하지 않는다. 이번 검사 소유 fixture/package만 결과 증거를 먼저 보관한 뒤 승인된 수명관리로 정리한다. 기존 독립 checkout은 기존 설정을 유지한 FF로 재현 검사한다.

## 확정 집중 검사

선행 집중 검사 13흐름 65확인 후 readonly CAS 누락을 수정했다. 최종 코드의 영향 검사 7흐름 34확인과 순수 후보/group 5확인이 통과했다. 수정 영향이 없는 선행 Save 실패·응답 유실·계획 Undo/재시도 검사는 단계별 소스/엔진 증거와 함께 재사용했다. 정상·cold·Review 취소/Confirm과 독립 raw 문서의 별도 미저장 원문을 지켰다. 등록 manifest가 저장 전/Review 전/Confirm 전에 달라지는 경우, 마지막 target 오류·물리 source/CP 충돌·쓰기 실패·응답 유실·Undo 후 새 선택의 전체 미적용/입력 보존을 확인했다. owned multi-target과 저장 copy의 등록 단일-target은 영향 회귀로 지켰다. 초기 실패 로그/fixture 증거를 보관하고 최종 통과만 집계했다.
