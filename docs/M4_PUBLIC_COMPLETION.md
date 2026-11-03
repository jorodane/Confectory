# M4 공개 함수 완료의 일반 분기 전환

저장소 v666의 `blueprintSetAsync`는 동기 복귀 때 완료의 `completion` 표시를 해제하고 포트 자체를 보존한다. 기존 `blueprintExecutionBranches`와 별도 실행 결과 인터페이스를 재사용한다. 새로운 실행/권한 정책이나 C# 의미 추론을 추가하지 않는다.

직접 소유한 기존 ordinary Blueprint 함수와 기존 직접 Blueprint 호출자에서, 내부 async 동작을 먼저 명시적으로 전환한 뒤 기능 heading 메뉴로 동기 복귀한다. 완료 ID·양의 공개 Result 값·표시명을 `blueprintFunctionCompletion`에 보존한다. 원래 C#·IO·지역 Result·provider/target·실행선 목적지와 literal `completion` 키는 유지한다. 기존 공개 분기가 없던 함수는 원래 반환값/out 값을 그대로 게시하며 기존 종료점을 명시적 `none` 선택으로 표현한다. 원래 C#이 새 일반 완료를 자동 선택하지 않는다.

Save는 함수/모든 소유 Blueprint target와 해당 실제 호출자·C# 영수증·원래 관측을 한 후보에 묶는다. 새 호출 대상이나 runtime provider를 자동 선택하지 않는다. 기존 Root 반환 카드에서 일반 완료를 명시 선택하면 같은 호출자 완료 줄이 실행된다. 이 후속 공개 계약 편집은 기존 M12의 전체 호출자 대응을 요구한다. 일반 분기의 이름 편집도 ID/값을 유지한다. async 재활성화는 그 ID를 예약하고 다시 암묵적 완료로 표시한다. 일반 완료 반환이 아직 남으면 자동 None 치환 없이 거절한다.

재시작 때 무관한 지연 로딩 body를 읽도록 강제하지 않는다. 선언된 importing body와 실제 저장 호출자는 빠짐없이 관측하며 누락·변조·경합은 거절한다. 실제 권한·부모/참조 원본·override 입출력 계약·Review/Confirm·최종 CAS는 유지한다.

## 정확한 경계

이 경계는 기존 직접 소유 ordinary root/provider와 직접 Blueprint 호출자다. 명시 C# import 호출이나 native 호출자의 소스 계약을 자동 재작성하지 않는다. 그 문맥은 명시적인 기존 소스 계약 검토가 필요한 호환성 오류로 보존한다. 자동 소스/호출 어댑터를 새 필수 요구로 늘리지 않는다. 미등록 외부 소스 접근이나 비소유 원본 편집을 추가하지 않는다.

M4의 다음 유한한 흐름은 Result 없는 next/native/whole-body 본문의 출력 보존 어댑터, 새/내부 소유 본문의 명시 전환, property 보조 편집 연결이다. 공개 완료의 지원 완료 부분을 다시 조합별 잔여로 늘리지 않는다. ref 입력·실제 await·내부 async 호출의 동기 복귀 거절과 override 공개 계약 보호는 정상 동작이다. M11/M12는 이 M4 연결의 회귀를 제외하면 닫힌 상태를 유지한다.

새 `blueprintFunctionCompletion`과 호출자 literal 포트 대응을 이전 parser가 동일하게 해석한다고 보장하지 않는다. 소스 rollback과 프로젝트/초안 복구를 구분하고 원본·최신 보관본을 함께 보존한다. Linux 검증과 Windows 교차 패키지는 실제 Windows/모바일 기기 검증이나 전체 UI/Space 전달 완료가 아니다.

최종 검증은 `tools/verify_desktop.py --suite async-function`에서 독립 LF/CRLF·fresh package/전체 복원·실패 수명관리를 수행한다. 동결 source와 새/재사용 검사는 종료 기록에 구분한다.
