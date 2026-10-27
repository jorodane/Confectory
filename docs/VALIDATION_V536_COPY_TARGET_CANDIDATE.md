# v536 명시 배정 copy의 여러 target 후보

기준은 `0d0b382`와 저장소 v536 원본이다. 원본 `localImplementationDraft`는 선택한 구현 정의를 객체 소유 복사본으로 만들고, 현재 `copyPicker`/`ImplementationCopy.Query`는 사용자가 고른 **하나의 source ID와 target**을 복사한다. 이번 범위는 그 기존 선택을 두 번 사용한 뒤 실제로 생기는 소스 결합이다. 모든 target 자동 복사나 새 독립 계약/ID 정책을 추가하지 않는다.

## 이번 지원 단위

서로 다른 두 owner가 동일한 caller 함수의 common·windows 구현을 각각 명시적으로 복사·배정한 fixture에서, 한 직접 소유 정보 함수(callee)의 입력 이름을 바꾸고 영향을 받는 두 copy의 C# 호출 본문을 사용자가 편집한다. donor의 두 본문은 기존 선택창에서 원문 그대로 명시 검토한다. 기존 `InformationFunctionContracts` backend가 두 copy receipt·공유 import·본문·계약을 하나의 후보/CAS로 이미 처리하므로 새 화면 어댑터나 순차 저장 endpoint를 추가할 필요가 없었다.

각 copy의 공개 caller 계약과 소유 ID·target·출처는 유지한다. callee 선언 및 두 소유 본문은 한 번의 임시 저장과 명시적 Review/Confirm으로만 적용한다. CRLF인 미편집 donor와 사용자가 편집한 본문, 정확한 64비트 값·설명·기존 배정·다른 target을 구별하여 보존한다. fixture의 `windows` review target은 기존 `Confectory.Build.DotNet::Portable` compiler provider에 명시적으로 연결한다. 실제 Windows 실행이 아니다.

## 재현한 결함과 수정

검토가 ready인 뒤 두 번째 copy owner의 `provide`를 다른 구현으로 바꿨을 때, 기존 Confirm이 성공했다. 변경되는 callee/본문 파일의 CAS는 있었지만 **변경하지 않는 copy 배정**은 최종 검사 대상에서 빠졌다. 이 재현은 격리 fixture에서만 수행했다.

- `ApplySlots`: Native 검증을 통과한 선택 copy의 기존 구현·graph/본문, 배정 독점성을 판단했던 소유 object/schema, manifest와 해당 proof의 프로젝트 내부 의존 원본의 **원래 물리적 baseline**을 저장 receipt에 보관한다. 쓰기 대상이나 권한을 추가하지 않는다. 임의의 새 물리 기준으로 바꾸지 않는다.
- `ValidateReviewSelection`: 재시작 후에도 저장된 baseline을 그대로 검사한다. 배정·출처·본문 원본이 바뀌거나 링크/프로젝트 경계를 벗어나면 초안과 입력을 유지하고 전체 거절한다.
- `ConfirmReviewed`: 같은 읽기 전용 경로를 기존 `CommitPlan`의 checks에 넣어 컴파일/재검토 이후의 마지막 경합도 전체 write와 한 source lease/CAS에서 거절한다. 읽기 의존 원본을 다시 쓰지 않는다.

완전한 write+read proof가 240항목을 넘으면 일부 guard를 버리지 않고 저장 전 거절한다. 기존 receipt에 read proof가 없는 저장 초안은 자동 재기준화하지 않고 보존하며 새 명시 저장이 필요하다. 일반 저장/복구·외부 소유·공개 override 계약 제한은 완화하지 않는다.

## 실제 검사와 재현 명령

최종 결과와 각 소스 SHA·실패 원인·예산은 `evidence/v536-copy-target-candidate/`의 JSON을 따른다. 실행 중이거나 실패한 검사를 통과 수에 넣지 않는다.

```sh
python3 tests/web/v536_information_copy_targets_native.py "$REPO" "$ENGINE_REPORT" metadata
python3 tests/web/v536_information_copy_targets_ui.py "$REPO" "$ENGINE_REPORT" normal
python3 tests/web/v536_information_copy_targets_ui.py "$REPO" "$ENGINE_REPORT" normal view
python3 tests/web/v536_information_copy_targets_ui.py "$REPO" "$ENGINE_REPORT" ownership-cas
python3 tests/web/v536_information_copy_targets_ui.py "$REPO" "$ENGINE_REPORT" record-cas
python3 tests/web/v536_information_copy_targets_ui.py "$REPO" "$ENGINE_REPORT" cancel
python3 tests/web/v536_information_copy_targets_ui.py "$REPO" "$ENGINE_REPORT" conflict
python3 tests/web/v536_information_copy_targets_ui.py "$REPO" "$ENGINE_REPORT" last-invalid
python3 tests/web/v536_information_copy_targets_ui.py "$REPO" "$ENGINE_REPORT" storage-loss
python3 tests/web/v536_information_copy_targets_ui.py "$REPO" "$ENGINE_REPORT" projects
python3 tests/web/v536_copy_read_guards_core.py "$REPO"
```

UI 검사는 실제 engine/Chromium 기본·독립 정보 창의 원래 구현 선택/C# 편집·취소, 불완전 입력 cold 복원, Undo/Redo, 임시 저장, Review 취소/재검토, compiler Confirm을 사용한다. 마지막 copy 오류·실제 checkpoint 쓰기 실패·peer 충돌·응답/결과조회 유실 후 cold 조회·프로젝트 전환의 새 입력 보존을 검사한다. Native 순수 후보는 마지막 본문/target/소유 증거·receipt 누락을 전체 거절한다. 별도 core 검사는 실제 생산 Review/Confirm/CommitPlan 본문을 컴파일하고 compiler 의존성만 통제하여 **두 번째 최종 검토 이후**의 파일 변경, 정상 읽기 전용 CAS, 누락 proof·경로 이탈 거절을 결정적으로 검증한다. 이 core를 실제 compiler/UI나 native 기기 검사로 세지 않는다.

초기 실패 중 로컬 취소에 server discard를 기대한 검사, 잘못된 fixture target provider, unchanged graph가 write 집합에 반드시 들어간다고 기대한 검사 및 peer 변경 뒤 원래 guard hash와 현재 hash를 혼동한 검사는 제품 결함과 구별하여 기록한다. 제품 결함 재현은 위 배정 경합이다.

## 정확한 남은 범위

이번 수용은 **서로 다른 명시 단일-target copy 두 개와 소유 callee 한 개**다. 한 copy에 여러 body를 자동 생성하거나 모든 target을 선택하지 않는다. 현재 원본 UI가 그 묶음을 생성하지 못한다는 이유만으로 자동 전체 복제 기능을 필수 잔여로 추가하지 않는다.

기존 7행/A4–A6의 새 immutable copy에서 등록 callee 복수 use, 별도 frame 계약/본문 및 opaque/whole-body source closure는 이번 완료로 합산하지 않는다. 여러 함수 계약을 함께 바꾸는 고정8행 나머지 문맥과 고정9행 정보/참조/기능 핀 타입·표시명/생성 식별자 대응, I6 기호/이모지/사용자 로컬 이미지 아이콘·B2 실제 배정 배지, M4 async·M11 C# 동작의 graph 전환·M12 root 실행 분기는 별도다. 공개 override 계약 위반·외부/부모 쓰기·미대응 소비자 삭제·자동 C# 재작성 거절은 정상 보호다.

CSS/HTML/레이아웃·권한·main·보관 빌드·원본·사용자 자료는 변경하지 않는다. 이번 실행이 만든 임시 fixture/package만 기존 증거 보관 후 수명관리로 정리한다. 실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달과 전체 UI 완료는 미검증/미완료로 유지한다.

## 집중·영향 검사 확정 결과

최종 고정 소스에서 실제 UI 9흐름 29확인·순수 후보 2확인과 실제 생산 Review/Confirm/CommitPlan의 통제 의존성 검사4확인이 통과했다. 영향 회귀3흐름의 확인 수는 `{'reg-csharp': 4, 'reg-abi': 5, 'reg-private': 10}`이며, 기존 단독 copy 등록/private ABI·일반 등록 다중 target·소유 C# 전체 본문을 검사했다. 실패한 초기/중간 검사는 이 통과 수에 넣지 않았다. 변경 제품 소스3개와 검사4개의 SHA 및 원인 구분은 위 evidence에 있다.
