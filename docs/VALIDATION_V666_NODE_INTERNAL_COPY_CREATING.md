# 새 copy의 첫 Save와 내부 흐름

기준은 고정 v666 ZIP의 `localImplementationDraft`와 선택 동작의 `openInternal(node,false)`다. 이미 저장된 copy의 M11을 새 기능으로 다시 구현하지 않는다. 기존 private copy 선택의 불변 snapshot 안에서 Root의 `next` C#을 같은 native `BlueprintNodeFlow`로 감싸고, 첫 Save에 copy·정보 배정·manifest·graph·새 내부 코드를 한 후보로 저장한다. 원래 팝오버·카드·버튼·레이아웃을 사용한다.

## 지원 경계

선택한 source/target 하나의 same-contract copy이며 기존 private graph 지원 profile을 사용한다. 아직 copy 파일이나 배정이 없는 때부터 내부 미리보기·본문 편집·Undo/Redo·Root 왕복·첫 Blueprint Save 및 부모 정보 Save를 연결한다. 새 공개 함수/계약을 만들거나 모든 target을 자동 선택하지 않는다. 최초 내부 미리보기에서는 원래 계약과 구조를 고정하고 선택한 본문만 편집한다. 기존 graph 안의 다른 private frame에서 첫 전환하는 경로와 실행 selector는 이번 Root `next` 단위에 합산하지 않는다.

새 `PrivateCopyNodeFlow`는 sealed seed·현재 guard·원래 node/definition/record hash·명시 nonce를 확인하고 기존 pure 래핑을 재사용한다. source path를 입력으로 받지 않는다. 원래 바깥 ID·signature·arguments·실행선·반환·표시 metadata와 copy 출처를 유지한다. 원문과 helpers를 내부 코드 한 개에 보존하며 본문을 사용자가 바꾼 경우에만 그 입력을 적용한다. this/재귀/import·whole-body/ref/out은 이미 확정된 native context/저장소 전달 규칙을 사용하며 자동 재작성·복사/초기화 추정을 추가하지 않는다.

기존 snapshot의 copy record는 아직 물리 파일로 만들어진 원본이 아니다. 선택한 가상 record를 새 내부 leaf로 옮기고 `retainedCode`에 원래 정의·ID·hash를 남긴다. donor의 실제 파일은 그대로 보존한다. 존재하던 C# 파일을 삭제하거나 덮어쓰는 처리가 아니며 `retainedCode`는 파일 접근 권한을 부여하지 않는다.

## 첫 저장과 기존 보호

첫 Save는 기존 `applySlots`의 격리 후보·전체 checkpoint CAS·영수증과 `settledSlots` 복구를 사용한다. 공개 계약/owner/원본 선택·binding이 바뀌면 전체를 거절한다. 부분 Review와 새 경로 충돌은 기존 보호를 따른다. 물리 파일 반영은 컴파일과 명시 Review→Confirm에서만 일어난다. 수락한 선택과 입력만 정리하고, 지연 응답 뒤 새로 들어온 본문은 같은 copy의 다음 Save용 입력으로 남긴다. copy 생성으로 소유 멤버십이 바뀐 뒤 이전 전환 Undo를 되살리지 않는다.

선택부터 첫 Save까지는 donor snapshot/관측 source 변경을 거절한다. 첫 Save 뒤 생성된 copy는 기존 copy 계약대로 독립된 저장 snapshot이다. 최종 파일 CAS는 owner·manifest·새 출력 등 실제 반영 대상을 보호한다. donor는 쓰기 대상이 아니며, 이미 복사한 뒤의 donor 본문을 새 copy가 묵시적으로 다시 읽거나 교체하지 않는다. 이 경계를 기존 source 편집의 원본 guard와 혼동하지 않는다.

## 구형 profile의 분류

`FeatureBlueprint.SupportsPrivateGraphs`와 기존 old-profile 회귀를 기준으로 한다. `sync-acyclic-ref-v1`, implicit/out/locals 계열 등 기존 형식의 읽기·실행 자체를 미구현으로 세지 않는다. 실제로 실행 가능한 구형 fixture를 만든 뒤 내부 전환을 요청하여, graph profile·코드·copy 선택·checkpoint가 바뀌지 않고 거절되는지 검증한다.

구형 profile의 암시 종료·출력/저장소 의미를 다른 profile로 자동 승격하지 않는 것은 **호환성 보호**다. v666 원본은 native 구형 저장 형식의 마이그레이션 정책을 정하지 않는다. 자동 또는 새 일괄 마이그레이션은 이번 고정 필수 잔여가 아니며 추가하지 않는다. 현대 profile의 M11 실제 미구현과 구분한다. 이 설명은 기존 함수 편집이나 명시적 기존 profile 도구 전체를 금지하는 정책이 아니다.

## 검증과 진단

`tools/verify_desktop.py --suite node-internal-copy-creating`는 독립 LF/CRLF·새 패키지·전체 SHA/CRC/모드 복원·복원본 실행·실패 수명관리를 순차 검증한다. 신규 first-save API/화면과 기존 private snapshot checkpoint, 저장 copy context/실행 분기, native 중첩/whole-body/ref-out·소유 보호 및 원문 편집을 다룬다. 최신/정상 롤백과 입력·로그·프로필·스크린샷·manifest를 지속 보관한 뒤 해당 실행 소유 임시물만 정리한다. 최종 신규/재사용 검사와 수치는 검증 뒤 아래에 기록한다.

집중 실행의 첫 두 실패는 fixture 모듈에 명시 default source가 없어 선택할 source가 없었던 문제였다. 이를 실제 기존 module 규칙에 맞게 고쳤다. 다음 미리보기의 JSON node 이중 parent 오류는 제품 후보를 `DeepClone`으로 분리해 수정했다. 첫 Save 뒤 donor 본문 경합을 최종 쓰기 CAS 대상으로 잘못 가정한 검사도 실패로 보존하고, 기존 독립 snapshot 의미와 대조해 owner 경합을 검사하도록 바로잡았다. 원본 선택 시 donor 경합 검사와 실제 쓰기 대상의 최종 CAS 검사를 모두 유지한다. 늦은 C# 입력은 저장됐지만 마지막 본문 receipt 뒤 accepted copy 선택이 남아 완료를 막는 제품 오류도 수정했다. 정확한 copy/출처와 수락된 receipt를 확인하고 같은 copy의 입력·미확정 시도가 모두 없을 때만 선택을 해제한다. 대기 조건이나 실제 기능 검사를 약화하지 않는다. 실패 로그·입력·수정 전 source를 보존하며 실패를 최종 통과 수에 합산하지 않는다.

## 고정 잔여

M11 전체 완료는 아니다. 생성 중 copy의 기존 중첩 문맥과 실행 selector, 직접 상속/참조 내부 진입은 실제 기존 원본 요구/소유 경계와 대조할 잔여다. 가능한 타입/target/프레임의 모든 조합을 새 필수 작업으로 만들지 않는다. 공개 override 입출력 구조 변경 거절은 정상 보호이며 독립 공개 계약 복제는 필수에서 제외한다. 부모·외부/참조 원본을 직접 쓰지 않는다.

B2 타 사용자/그룹 backend, 정보 종류 C# 표현/사용 중 삭제 대응, M4/M12 및 3D/권한 별도 팩과 고정 V2–V9는 기존 잔여다. 3D 이동은 표시 연출이며 실행 조건이 아니다. 실제 Windows apphost/WebView2·모바일·전체 UI·Library/Space 전달은 교차 패키지와 구분해 미완료로 유지한다.
