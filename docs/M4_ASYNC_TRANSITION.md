# M4 명시적 비동기 전환과 저장

기준은 저장소 v666 ZIP의 `Confectory-v666/dist/blueprint.js`다. `blueprintSetAsync`와 개별 동작 heading 메뉴의 명시 전환, 완료 포트 및 실행 순서가 원본 근거다. 프로토타입의 본문 재작성은 채택하지 않는다. 동기 호출자는 사용자가 명시적으로 전환할 때까지 오류로 표시한다는 확정 결정을 유지한다.

## 연결한 사용자 흐름

직접 소유한 기존 ordinary method/switch Blueprint 함수의 이름/시작 heading과 C# 동작 heading 메뉴에서 비동기 활성화를 명시한다. Result 동작의 동기 복귀는 아래 후속 지원 경계를 따른다. 시계와 완료 포트를 표시하고 기존 연결 도구로 완료 영역을 연결한다. 전환은 private 입력이므로 Undo/Redo와 cold 재시작을 지원하며 원본 파일을 쓰지 않는다. 참조 호출 카드는 원본 설정을 변경하지 않는다. 호출자 함수는 별도의 명시 전환을 거친다.

Save는 원래 함수·소유 provider의 모든 Blueprint target·C# record와 호출자/선택 관련 원본 관측을 하나의 checkpoint 후보에 묶는다. 기존 C# source와 helpers, IO/공개 분기 ID·값·연결은 보존하며 필요한 async metadata·profile·정의 영수증만 갱신한다. 다른 진행 중 계약 변경은 묵시적으로 합치지 않는다. 같은 async 전환의 명시 호출자 후보끼리는 전체 그룹을 합쳐 Review한다. 부분 Review를 거절하며 Review 취소는 원본을 쓰지 않는다.

관측 헤더와 호출자 원문도 Save·복원·Review·최종 CommitPlan CAS에 남긴다. 물리 경합·변조·저장 권한 실패에서는 전체 입력을 보존한다. 이미 반영된 Save의 응답 유실은 같은 receipt로 조회하고, 실패가 확실한 시도만 원래 checkpoint·전체 source proof·물리 원본을 다시 확인하여 재시도한다. 저장 중 생긴 다른 입력은 이전 응답으로 삭제하지 않는다. 실제 실행은 기존 Task runtime의 await → 출력 게시 → 완료 → 결과 분기 → continuation을 따른다.

## 정확한 경계와 남은 원래 흐름

이번 경계는 직접 소유한 기존 ordinary root와 코드 동작 및 명시적 direct caller다. 원래 C#의 `await`가 남거나 내부 async 호출이 있는 동기 복귀는 compiler/계약 오류이며 자동 대기나 재작성으로 해결하지 않는다. ref 입력 거절과 비소유 원본·공개 override 계약 보호는 정상 동작이다.

M4 전체가 완료된 것은 아니다. 다음 원래 흐름은 계속 남는다.

1. 공개 함수 전체와 직접 Blueprint 호출자의 완료 보존은 [공개 완료 전환](M4_PUBLIC_COMPLETION.md)에 연결했다. 명시 C# import/native 호출자의 호환되지 않는 기존 소스 계약은 자동 재작성하지 않고 거절한다. 자동 호출 어댑터는 새 필수 요구가 아니다.
2. Result가 없는 next/native/whole-body 동작의 완료를 기존 IO·C# 원문 그대로 일반 분기로 보존하는 어댑터. 임의로 반환형을 바꾸거나 코드를 재작성하지 않는다.
3. 새/내부 직접 소유 본문의 명시 전환. 기존 async root의 속성 보조 편집은 [속성 편집 후속](M4_ASYNC_PROPERTIES.md)에 연결했다. 비소유 원본 쓰기/override IO 변경은 정상 거절이고 legacy 자동 마이그레이션은 필수 요구가 아니다.

직접 소유한 기존 root의 일반 C# Result 동작은 완료를 **일반 지역 Result 분기**로 전환한다. 기존 `completion` wire 키·목적지, Result ID/값/기본 분기와 C# 원문을 보존한다. `completionBranch`는 별도 ID·유효한 C# 이름·정수값·화면 표시명을 저장하고 async 재전환 때 같은 정체성을 예약한다. 동기에서는 원래 C#이 그 Result를 명시 반환할 때만 해당 줄을 실행한다. 자동 완료 실행이나 본문 재작성은 하지 않는다. 연결된 분기 삭제·변조·중복 별칭은 거절한다. 캔버스/요약/소형 화면은 같은 포트 의미를 사용한다.

ordinary async root의 Set 출력 이름·저장 대상·값/실행 연결은 기존 원자 Set 계획을 재사용한다. async profile을 기존 UI/저장 게이트에 포함하며 새로운 타입·소유권·실행 정책은 추가하지 않는다.
M11·M12는 구체적 회귀가 없으므로 닫힌 상태를 유지한다. V2–V9·별도 팩/backend·종류 표현/사용 중 항목 처리 및 실제 기기/전체 UI/Space 전달은 고정 수용 표의 별도 잔여다.

## 검증 방법

`tools/verify_desktop.py --suite async-transition`은 최종 commit의 독립 LF/CRLF checkout·독립 캐시로 API/영수증 거절, 실제 메뉴·Undo/Redo·Save·cold·Review/Confirm, 저장 실패·경합·응답 유실·늦은 입력을 실행한다. 기존 async/switch runtime과 M12 관련 회귀도 검사한다. 새 Windows 교차 패키지와 전체 SHA/manifest 압축 복원본에서 같은 UI·실제 Task runtime·저장 실패를 검사하고 증거를 지속 보관한 뒤 해당 실행 소유 임시물만 정리한다. Linux에서 수행하며 실제 Windows/모바일 실행을 뜻하지 않는다. 최종 신규 40단계·재사용 0 및 보관 SHA/공간은 [검증 종료 기록](VALIDATION_V666_ASYNC_TRANSITION.md)에 남겼다.


완료 일반 분기와 Set 보조 경로의 최종 검증은 `--suite async-completion`으로 수행한다. 기존 40단계는 앞선 checkpoint의 근거이고 이번 최종 코드의 재실행 여부/보관 SHA는 별도 종료 기록에 명시한다.

일반 완료 분기의 `completionBranch` metadata와 literal 포트 대응을 이전 빌드가 동일하게 해석한다고 보장하지 않는다. 최신 소스·프로젝트 원본·초안을 함께 보존하며 코드 rollback과 데이터/초안 복구를 구분한다.

이번 완료 일반 분기·Set 단위의 [최종 검증·보관 기록](VALIDATION_V666_ASYNC_COMPLETION.md)에 신규/재사용·호환성·공간을 기록한다.
