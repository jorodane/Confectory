# M4 명시적 비동기 전환과 저장

기준은 저장소 v666 ZIP의 `Confectory-v666/dist/blueprint.js`다. `blueprintSetAsync`와 개별 동작 heading 메뉴의 명시 전환, 완료 포트 및 실행 순서가 원본 근거다. 프로토타입의 본문 재작성은 채택하지 않는다. 동기 호출자는 사용자가 명시적으로 전환할 때까지 오류로 표시한다는 확정 결정을 유지한다.

## 연결한 사용자 흐름

직접 소유한 기존 ordinary method/switch Blueprint 함수의 이름/시작 heading과 C# 동작 heading 메뉴에서 비동기 플래그를 편집한다. 시계와 완료 포트를 표시하고 기존 연결 도구로 완료 영역을 연결한다. 전환은 private 입력이므로 Undo/Redo와 cold 재시작을 지원하며 원본 파일을 쓰지 않는다. 참조 호출 카드는 원본 설정을 변경하지 않는다. 호출자 함수는 별도의 명시 전환을 거친다.

Save는 원래 함수·소유 provider의 모든 Blueprint target·C# record와 호출자/선택 관련 원본 관측을 하나의 checkpoint 후보에 묶는다. 기존 C# source와 helpers, IO/공개 분기 ID·값·연결은 보존하며 필요한 async metadata·profile·정의 영수증만 갱신한다. 다른 진행 중 계약 변경은 묵시적으로 합치지 않는다. 같은 async 전환의 명시 호출자 후보끼리는 전체 그룹을 합쳐 Review한다. 부분 Review를 거절하며 Review 취소는 원본을 쓰지 않는다.

관측 헤더와 호출자 원문도 Save·복원·Review·최종 CommitPlan CAS에 남긴다. 물리 경합·변조·저장 권한 실패에서는 전체 입력을 보존한다. 이미 반영된 Save의 응답 유실은 같은 receipt로 조회하고, 실패가 확실한 시도만 원래 checkpoint·전체 source proof·물리 원본을 다시 확인하여 재시도한다. 저장 중 생긴 다른 입력은 이전 응답으로 삭제하지 않는다. 실제 실행은 기존 Task runtime의 await → 출력 게시 → 완료 → 결과 분기 → continuation을 따른다.

## 정확한 경계와 남은 원래 흐름

이번 경계는 직접 소유한 기존 ordinary root와 코드 동작 및 명시적 direct caller다. 원래 C#의 `await`가 남거나 내부 async 호출이 있는 동기 복귀는 compiler/계약 오류이며 자동 대기나 재작성으로 해결하지 않는다. ref 입력 거절과 비소유 원본·공개 override 계약 보호는 정상 동작이다.

M4 전체가 완료된 것은 아니다. 다음 원래 흐름은 계속 남는다.

1. 연결된 완료 포트를 동기 복귀 시 원본처럼 일반 분기로 보존하는 전환. 현재는 연결을 폐기하지 않고 명확히 거절한다. 이 임시 구현 경계를 영구 UX 정책으로 확정하지 않는다.
2. 원래 새/내부 소유 본문 전환의 실제 연결과 native/whole-body 문맥 보존. 기존 source/profile을 자동 마이그레이션하거나 부모·등록 외부 원본의 계약을 바꾸지 않는다. 실제 소유 편집과 정상 비소유 거절을 대조해 유한한 사용자 흐름으로 마감한다.

M11·M12는 구체적 회귀가 없으므로 닫힌 상태를 유지한다. V2–V9·별도 팩/backend·종류 표현/사용 중 항목 처리 및 실제 기기/전체 UI/Space 전달은 고정 수용 표의 별도 잔여다.

## 검증 방법

`tools/verify_desktop.py --suite async-transition`은 최종 commit의 독립 LF/CRLF checkout·독립 캐시로 API/영수증 거절, 실제 메뉴·Undo/Redo·Save·cold·Review/Confirm, 저장 실패·경합·응답 유실·늦은 입력을 실행한다. 기존 async/switch runtime과 M12 관련 회귀도 검사한다. 새 Windows 교차 패키지와 전체 SHA/manifest 압축 복원본에서 같은 UI·실제 Task runtime·저장 실패를 검사하고 증거를 지속 보관한 뒤 해당 실행 소유 임시물만 정리한다. Linux에서 수행하며 실제 Windows/모바일 실행을 뜻하지 않는다. 최종 수치와 보관 SHA는 검증 종료 기록에 남긴다.
